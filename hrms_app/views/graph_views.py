from datetime import datetime
from django.db import connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from decimal import Decimal


class HRDashboardGraphs(APIView):
    """
    API to fetch data for HR Dashboard graphs and charts:
    - Ticket Distribution (critical, high, medium, low) - Pie Chart
    - Payroll Monthly (April to March) - Bar Graph
    - Attrition Rate Monthly (April to March) - Line/Bar Graph
    - Employee Level Distribution (L1, L2, L3, L4) - Pie Chart
    - Recruitment Tracker (total, open, in-process) - Pie/Bar Chart
    - Employee Separation Monthly (April to March) - Bar Graph
    
    Data Sources:
    - ci_support_tickets_employee: ticket priority distribution
    - ci_payroll_report: monthly payroll data
    - ci_revenue: attrition rate, recruitment tracker
    - ci_erp_users_details + ci_grade: employee level distribution
    - ci_resignations + ci_terminations: employee separation
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Get year from query params (default to current financial year)
            year = request.query_params.get('year')
            today = datetime.now()
            if not year:
                if today.month >= 4:
                    year = today.year
                else:
                    year = today.year - 1
            else:
                year = int(year)

            months_order = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
            month_names = ['April', 'May', 'June', 'July', 'August', 'September',
                          'October', 'November', 'December', 'January', 'February', 'March']

            with connection.cursor() as cursor:
                # 1. Ticket (Stacked Bar: Raised/Closed by priority)
                ticket_priorities = ['critical', 'high', 'medial', 'low']
                ticket_statuses = ['Raised', 'Closed']
                # Map ticket_status: treat 'Closed' as closed, everything else as raised
                ticket_counts = {status: {priority: 0 for priority in ticket_priorities} for status in ticket_statuses}
                cursor.execute("""
                    SELECT LOWER(priority), LOWER(ticket_status), COUNT(*)
                    FROM ci_support_tickets_employee
                    GROUP BY LOWER(priority), LOWER(ticket_status)
                """)
                for row in cursor.fetchall():
                    priority = row[0] if row[0] in ticket_priorities else 'low'
                    status = row[1]
                    count = row[2]
                    if status == 'closed':
                        ticket_counts['Closed'][priority] += count
                    else:
                        ticket_counts['Raised'][priority] += count
                ticket_bar_data = {
                    'labels': [p.upper() for p in ticket_priorities],
                    'datasets': [
                        {'label': 'Raised', 'data': [ticket_counts['Raised'][p] for p in ticket_priorities]},
                        {'label': 'Closed', 'data': [ticket_counts['Closed'][p] for p in ticket_priorities]},
                    ]
                }

                # 2. Payroll (Line: Total Employee Cost by month)
                payroll_line_data = []
                for i, month in enumerate(months_order):
                    query_year = year if month >= 4 else year + 1
                    cursor.execute("""
                        SELECT COALESCE(SUM(net_pay), 0) as total_payroll
                        FROM ci_payroll_report
                        WHERE month = %s AND year = %s
                    """, [month, query_year])
                    result = cursor.fetchone()
                    payroll_line_data.append({
                        'month': month_names[i],
                        'total_employee_cost': float(result[0]) if result and result[0] else 0
                    })

                # 3. Attrition Rate (Line: % by month) - overall, not department/division
                attrition_line_data = []
                for i, month in enumerate(months_order):
                    query_year = year if month >= 4 else year + 1
                    # Employees who left (resignations + terminations)
                    cursor.execute("""
                        SELECT COUNT(*) FROM ci_resignations
                        WHERE MONTH(resignation_date) = %s AND YEAR(resignation_date) = %s
                    """, [month, query_year])
                    resigned = cursor.fetchone()[0]
                    cursor.execute("""
                        SELECT COUNT(*) FROM ci_terminations
                        WHERE MONTH(date_of_termination) = %s AND YEAR(date_of_termination) = %s
                    """, [month, query_year])
                    terminated = cursor.fetchone()[0]
                    left_count = resigned + terminated
                    # Average employee count for the month (start + end) / 2
                    # Start: employees active at start of month
                    cursor.execute("""
                        SELECT COUNT(*) FROM ci_erp_users
                        WHERE is_active = 1 AND (created_at < DATE(%s))
                    """, [f"{query_year}-{month:02d}-01"])
                    start_count = cursor.fetchone()[0]
                    # End: employees active at end of month
                    # Get last day of month
                    import calendar
                    last_day = calendar.monthrange(query_year, month)[1]
                    cursor.execute("""
                        SELECT COUNT(*) FROM ci_erp_users
                        WHERE is_active = 1 AND (created_at <= DATE(%s))
                    """, [f"{query_year}-{month:02d}-{last_day:02d}"])
                    end_count = cursor.fetchone()[0]
                    avg_count = (start_count + end_count) / 2 if (start_count + end_count) > 0 else 0
                    attrition_rate = (left_count / avg_count * 100) if avg_count > 0 else 0
                    attrition_line_data.append({
                        'month': month_names[i],
                        'attrition_rate': round(attrition_rate, 2)
                    })

                # 4. Employee Level (Stacked Bar: 0-3yr, 3-5yr, 5+yr by L1-L4)
                # Get all active employees with grade and date_of_joining
                cursor.execute("""
                    SELECT g.grade_name, ud.date_of_joining
                    FROM ci_erp_users_details ud
                    INNER JOIN ci_erp_users u ON ud.user_id = u.id
                    LEFT JOIN ci_grade g ON ud.grade_id = g.grade_id
                    WHERE u.is_active = 1 AND ud.date_of_joining IS NOT NULL
                """)
                # Prepare buckets
                level_labels = ['L1', 'L2', 'L3', 'L4']
                exp_buckets = ['0 to 3 yr', '3 to 5 yr', '5+ yr']
                level_exp_counts = {exp: {lvl: 0 for lvl in level_labels} for exp in exp_buckets}
                for row in cursor.fetchall():
                    grade = row[0] or ''
                    doj = row[1]
                    # Map grade to L1-L4
                    grade_upper = grade.upper()
                    if 'L1' in grade_upper or grade_upper == 'LEVEL 1' or grade_upper == 'LEVEL1':
                        lvl = 'L1'
                    elif 'L2' in grade_upper or grade_upper == 'LEVEL 2' or grade_upper == 'LEVEL2':
                        lvl = 'L2'
                    elif 'L3' in grade_upper or grade_upper == 'LEVEL 3' or grade_upper == 'LEVEL3':
                        lvl = 'L3'
                    elif 'L4' in grade_upper or grade_upper == 'LEVEL 4' or grade_upper == 'LEVEL4':
                        lvl = 'L4'
                    else:
                        continue
                    # Calculate experience
                    try:
                        doj_date = datetime.strptime(str(doj), '%Y-%m-%d')
                    except Exception:
                        continue
                    years = (today - doj_date).days / 365.25
                    if years < 3:
                        exp = '0 to 3 yr'
                    elif years < 5:
                        exp = '3 to 5 yr'
                    else:
                        exp = '5+ yr'
                    level_exp_counts[exp][lvl] += 1
                employee_level_bar_data = {
                    'labels': level_labels,
                    'datasets': [
                        {'label': exp, 'data': [level_exp_counts[exp][lvl] for lvl in level_labels]} for exp in exp_buckets
                    ]
                }

                # 5. Recruitment Tracker (Pie: Total, Open, In process)
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(opened_recruitment_tracker), 0) as open_positions,
                        COALESCE(SUM(filed_recruitment_tracker), 0) as filled_positions,
                        COALESCE(SUM(in_process_recruitment_tracker), 0) as in_process
                    FROM ci_revenue
                    WHERE year = %s OR year = %s
                """, [year, year + 1])
                recruitment_result = cursor.fetchone()
                open_positions = int(recruitment_result[0]) if recruitment_result and recruitment_result[0] else 0
                filled_positions = int(recruitment_result[1]) if recruitment_result and recruitment_result[1] else 0
                in_process = int(recruitment_result[2]) if recruitment_result and recruitment_result[2] else 0
                recruitment_pie_data = {
                    'labels': ['Total', 'Open', 'In process'],
                    'data': [open_positions + filled_positions + in_process, open_positions, in_process]
                }

                # 6. Employee Separation (Stacked Bar: Total Resigned, Accepted, F&F Proceed by month)
                total_resigned = []
                accepted = []
                fnf_proceed = []
                for i, month in enumerate(months_order):
                    query_year = year if month >= 4 else year + 1
                    # Total resigned
                    cursor.execute("""
                        SELECT COUNT(*) FROM ci_resignations
                        WHERE MONTH(resignation_date) = %s AND YEAR(resignation_date) = %s
                    """, [month, query_year])
                    total_resigned.append(cursor.fetchone()[0])
                    # Accepted (status = 'Accepted')
                    cursor.execute("""
                        SELECT COUNT(*) FROM ci_resignations
                        WHERE MONTH(resignation_date) = %s AND YEAR(resignation_date) = %s AND LOWER(status) = 'accepted'
                    """, [month, query_year])
                    accepted.append(cursor.fetchone()[0])
                    # F & F Proceed (exists in ci_employee_exit_final for employee_id in ci_resignations)
                    cursor.execute("""
                        SELECT COUNT(*) FROM ci_resignations r
                        WHERE MONTH(r.resignation_date) = %s AND YEAR(r.resignation_date) = %s
                        AND EXISTS (SELECT 1 FROM ci_employee_exit_final f WHERE f.employee_id = r.employee_id AND f.`f&f` IS NOT NULL)
                    """, [month, query_year])
                    fnf_proceed.append(cursor.fetchone()[0])
                separation_bar_data = {
                    'labels': month_names,
                    'datasets': [
                        {'label': 'Total Resigned', 'data': total_resigned},
                        {'label': 'Accepted', 'data': accepted},
                        {'label': 'F & F Proceed', 'data': fnf_proceed},
                    ]
                }

                # 7. Performance Management Matrix (Stacked Bar: Exceed, Exceptional, Meet, Below, Unsatisfactory by quarter)
                # Sum each metric by quarter from ci_revenue
                quarter_map = {1:0, 2:0, 3:0, 4:0, 5:1, 6:1, 7:1, 8:2, 9:2, 10:2, 11:3, 12:3}
                perf_labels = ['Q I', 'Q II', 'Q III', 'Q IV']
                perf_keys = ['exceeds_expectations', 'exceptional', 'meet_expectations', 'below_expectations', 'unsatisfactory']
                perf_names = ['Exceed Expectation', 'Exceptional', 'Meet Exp.', 'Below Exp.', 'Unsatisfactory']
                perf_quarters = [{k:0 for k in perf_keys} for _ in range(4)]
                cursor.execute("""
                    SELECT month, year, exceptional, exceeds_expectations, meet_expectations, below_expectations, unsatisfactory
                    FROM ci_revenue
                    WHERE (year = %s OR year = %s)
                """, [year, year+1])
                for row in cursor.fetchall():
                    m = row[0]
                    q = quarter_map.get(m, 0)
                    for idx, k in enumerate(perf_keys):
                        val = row[idx+2] if row[idx+2] is not None else 0
                        perf_quarters[q][k] += int(val)
                performance_matrix_bar_data = {
                    'labels': perf_labels,
                    'datasets': [
                        {'label': perf_names[i], 'data': [perf_quarters[q][perf_keys[i]] for q in range(4)]} for i in range(5)
                    ]
                }

            response_data = {
                "status": True,
                "message": "HR Dashboard graph data fetched successfully",
                "financial_year": f"FY {year}-{str(year + 1)[-2:]}",
                "data": {
                    "ticket": ticket_bar_data,
                    "payroll": payroll_line_data,
                    "attrition_rate": attrition_line_data,
                    "employee_level": employee_level_bar_data,
                    "recruitment_tracker": recruitment_pie_data,
                    "employee_separation": separation_bar_data,
                    "performance_management_matrix": performance_matrix_bar_data
                }
            }

            from rest_framework import status as drf_status
            return Response(response_data, status=drf_status.HTTP_200_OK)

        except Exception as e:
            from rest_framework import status as drf_status
            return Response(
                {"status": False, "message": f"Error fetching HR Dashboard graph data: {str(e)}"},
                status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR
            )

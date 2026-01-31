from datetime import date, timedelta
from collections import defaultdict
from calendar import monthrange
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection

# class EmployeeLeavePattern(APIView):
#     LEAVE_TYPE_MAP = {
#         184: "CL",    # Casual Leave
#         185: "ML",    # Medical Leave
#         289: "PL",    # Paid Leave
#         187: "MTL",   # Maternity Leave
#         1098: "PTL",  # Paternity Leave
#         1749: "LWP",  # Leave Without Pay
#     }

#     MONTH_NAMES = [
#         "January", "February", "March", "April", "May", "June",
#         "July", "August", "September", "October", "November", "December"
#     ]

#     def post(self, request):
#         try:
#             year = int(request.data.get("year"))
#             if not year:
#                 return Response({"status": "error", "message": "Year is required"}, status=400)

#             # Fetch leave records for active employees overlapping the year
#             with connection.cursor() as c:
#                 c.execute("""
#                     SELECT la.leave_type_id, la.from_date, la.to_date
#                     FROM ci_leave_applications la
#                     INNER JOIN ci_erp_users_details ud ON la.employee_id = ud.employee_id
#                     INNER JOIN ci_erp_users u ON ud.user_id = u.id
#                     WHERE u.is_active = 1
#                     AND (
#                         YEAR(la.from_date) = %s OR
#                         YEAR(la.to_date) = %s OR
#                         (la.from_date <= %s AND la.to_date >= %s)
#                     )
#                 """, [year, year, f"{year}-01-01", f"{year}-12-31"])

#                 leave_records = c.fetchall()

#             # Initialize results
#             month_data = [
#                 {"month": m, "CL": 0, "ML": 0, "PL": 0, "MTL": 0, "PTL": 0, "LWP": 0, "Total": 0}
#                 for m in self.MONTH_NAMES
#             ]

#             # Process each leave
#             for leave_type_id, from_date, to_date in leave_records:
#                 leave_code = self.LEAVE_TYPE_MAP.get(leave_type_id)
#                 if not leave_code:
#                     continue  # Ignore unknown leave types

#                 # Adjust range to fit within the requested year
#                 start_date = max(from_date, date(year, 1, 1))
#                 end_date = min(to_date, date(year, 12, 31))

#                 current_date = start_date
#                 while current_date <= end_date:
#                     month_idx = current_date.month - 1
#                     month_data[month_idx][leave_code] += 1
#                     month_data[month_idx]["Total"] += 1
#                     current_date += timedelta(days=1)

#             return Response({"status": "success", "year": year, "data": month_data}, status=200)

#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=500)




class EmployeeLeavePattern(APIView):
    MONTH_NAMES = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    def post(self, request):
        try:
            year = int(request.data.get("year"))
            if not year:
                return Response({"status": "error", "message": "Year is required"}, status=400)

            # 🔹 Step 1: Fetch leave setup mapping for the given year
            with connection.cursor() as c:
                c.execute("""
                    SELECT constants_id, current_leave_name
                    FROM ci_leave_setup
                    WHERE year = %s
                """, [year])
                leave_setup = dict(c.fetchall())  # {constants_id: leave_name}

            if not leave_setup:
                return Response({"status": "error", "message": f"No leave setup found for year {year}"}, status=404)

            # 🔹 Step 2: Fetch leave applications for active employees in that year
            with connection.cursor() as c:
                c.execute("""
                    SELECT la.leave_type_id, la.from_date, la.to_date
                    FROM ci_leave_applications la
                    INNER JOIN ci_erp_users_details ud ON la.employee_id = ud.employee_id
                    INNER JOIN ci_erp_users u ON ud.user_id = u.id
                    WHERE u.is_active = 1
                    AND (
                        YEAR(la.from_date) = %s OR
                        YEAR(la.to_date) = %s OR
                        (la.from_date <= %s AND la.to_date >= %s)
                    )
                """, [year, year, f"{year}-01-01", f"{year}-12-31"])

                leave_records = c.fetchall()

            # 🔹 Step 3: Initialize results dynamically with leave names
            month_data = []
            for m in self.MONTH_NAMES:
                month_row = {"month": m, "Total": 0}
                for leave_name in leave_setup.values():
                    month_row[leave_name] = 0
                month_data.append(month_row)

            # 🔹 Step 4: Process each leave record
            for leave_type_id, from_date, to_date in leave_records:
                leave_name = leave_setup.get(leave_type_id)
                if not leave_name:
                    continue  # Ignore unknown leave types

                # Bound the leave within requested year
                start_date = max(from_date, date(year, 1, 1))
                end_date = min(to_date, date(year, 12, 31))

                current_date = start_date
                while current_date <= end_date:
                    month_idx = current_date.month - 1
                    month_data[month_idx][leave_name] += 1
                    month_data[month_idx]["Total"] += 1
                    current_date += timedelta(days=1)

            return Response({"status": "success", "year": year, "data": month_data}, status=200)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)
 

        
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta


class MonthlyLeaveReport(APIView):
    def post(self, request):
        try:
            query_year = request.data.get("year")
            if not query_year:
                return Response(
                    {"error": "Year is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            query_year = int(query_year)

            # Fetch employee details with manager info
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, ud.employee_id, u.first_name, u.last_name,
                           d.department_name, dg.designation_name, divn.division_name,
                           CONCAT(m.first_name, ' ', m.last_name) AS manager_name,
                           ud.date_of_joining
                    FROM ci_erp_users u
                    JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                    LEFT JOIN ci_designations dg ON ud.designation_id = dg.designation_id
                    LEFT JOIN ci_division divn ON ud.division_id = divn.division_id
                    LEFT JOIN ci_erp_users m ON ud.manager = m.id
                    WHERE u.is_active = 1
                """)
                employees = cursor.fetchall()

            # Fetch leave applications for given year (and spillover into next year for Jan–Mar)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT employee_id, from_date, to_date, no_of_days, is_half_day
                    FROM ci_leave_applications
                    WHERE line_manager_status = 1
                      AND (
                          YEAR(from_date) = %s OR YEAR(to_date) = %s
                      )
                """, [query_year, query_year + 1])
                leaves = cursor.fetchall()

            # Organize leaves by employee
            leave_map = {}
            for emp_id, from_date, to_date, no_of_days, is_half_day in leaves:
                if not emp_id:
                    continue
                leave_map.setdefault(emp_id, []).append({
                    "from": from_date,
                    "to": to_date,
                    "days": float(no_of_days or 0),
                    "half": bool(is_half_day),
                })

            months = ["Apr", "May", "June", "July", "Aug", "Sept",
                      "Oct", "Nov", "Dec", "Jan", "Feb", "March"]

            report = []

            # Build report rows
            for emp in employees:
                user_id, employee_id, fname, lname, dept, desg, divn, manager_name, doj = emp
                manager_name = manager_name if manager_name else "NA"

                row = {
                    "Employee ID": employee_id,
                    "Name": f"{fname} {lname}",
                    "Department": dept,
                    "Designation": desg,
                    "Division": divn,
                    "Sub-Division": "NA",
                    "Level": "NA",
                    "Headquarter": "NA",
                    "Line Manager": manager_name,
                    "D.O.J": str(doj) if doj else None,
                }

                total_leaves = 0.0

                for idx, month in enumerate(months, start=4):  
                    # Fiscal year Apr–Mar mapping
                    actual_month = idx if idx <= 12 else idx - 12
                    actual_year = query_year if idx <= 12 else query_year + 1

                    month_days = 0.0

                    # Check employee's leaves
                    for leave in leave_map.get(employee_id, []):
                        start = leave["from"]
                        end = leave["to"]
                        no_of_days = leave["days"]

                        if not start or not end:
                            continue

                        # Clip leave within this month
                        month_start = datetime(actual_year, actual_month, 1).date()
                        if actual_month == 12:
                            month_end = datetime(actual_year, 12, 31).date()
                        else:
                            month_end = (datetime(actual_year, actual_month + 1, 1) - timedelta(days=1)).date()

                        overlap_start = max(start, month_start)
                        overlap_end = min(end, month_end)

                        if overlap_start <= overlap_end:
                            # Count overlapping days
                            overlap_days = (overlap_end - overlap_start).days + 1
                            # Handle half-day
                            if leave["half"] and overlap_days == 1:
                                month_days += 0.5
                            else:
                                month_days += overlap_days

                    row[month] = float(month_days)
                    total_leaves += month_days

                row["Total"] = float(total_leaves)
                report.append(row)

            return Response(report, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class LeaveBalanceReport(APIView):
    def post(self, request):
        try:
            query_year = request.data.get("year")
            if not query_year:
                return Response(
                    {"error": "Year is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            query_year = int(query_year)

            # === 1. Define leave type mapping ===
            target_leaves = {
                "Casual Leave (CL)": "CASUAL LEAVE",
                "Medical Leave (ML)": "MEDICAL",
                "Maternity Leave": "MATERNITY LEAVE",
                "Paid Leave": "PAID LEAVE",
                "Paternity Leave": "PATERNITY LEAVE"
            }

            # === 2. Fetch Employee Data ===
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, ud.employee_id, u.first_name, u.last_name,
                           d.department_name, dg.designation_name, divn.division_name,
                           CONCAT(m.first_name, ' ', m.last_name) AS manager_name,
                           ud.date_of_joining
                    FROM ci_erp_users u
                    JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                    LEFT JOIN ci_designations dg ON ud.designation_id = dg.designation_id
                    LEFT JOIN ci_division divn ON ud.division_id = divn.division_id
                    LEFT JOIN ci_erp_users m ON ud.manager = m.id
                    WHERE u.is_active = 1
                """)
                employees = cursor.fetchall()

            # === 3. Fetch Leave Balances ===
            leave_balances = {}
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT lb.employee_id, lb.leave_type, lb.balance_leave
                    FROM ci_leave_balance lb
                    WHERE lb.year = %s AND lb.status = 'Y'
                      AND lb.leave_type IN %s
                """, [query_year, tuple(target_leaves.keys())])
                for emp_id, leave_name, balance in cursor.fetchall():
                    if emp_id not in leave_balances:
                        leave_balances[emp_id] = {}
                    leave_balances[emp_id][target_leaves[leave_name]] = float(balance)

            # === 4. Fetch Used Leaves (join with leave_balance to get leave_type) ===
            used_leaves = {}
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT la.employee_id, lb.leave_type, SUM(la.no_of_days)
                    FROM ci_leave_applications la
                    JOIN ci_leave_balance lb
                      ON la.employee_id = lb.employee_id AND la.leave_type_id = lb.leave_type_id
                    WHERE la.status = 1
                      AND (YEAR(la.from_date) = %s OR YEAR(la.to_date) = %s)
                      AND lb.leave_type IN %s
                    GROUP BY la.employee_id, lb.leave_type
                """, [query_year, query_year, tuple(target_leaves.keys())])

                for emp_id, leave_name, days_used in cursor.fetchall():
                    if emp_id not in used_leaves:
                        used_leaves[emp_id] = {}
                    used_leaves[emp_id][target_leaves[leave_name]] = float(days_used or 0)

            # === 5. Build Report ===
            report = []
            for emp in employees:
                user_id, emp_id, fname, lname, dept, desg, divn, manager, doj = emp
                row = {
                    "Employee ID": emp_id,
                    "Name": f"{fname} {lname}",
                    "Department": dept,
                    "Designation": desg,
                    "Division": divn,
                    "Sub-Division": "NA",
                    "Level": "NA",
                    "Headquarter": "NA",
                    "Line Manager": manager if manager else "NA",
                    "D.O.J": str(doj) if doj else None,
                }

                # Initialize all leave types with default values
                for leave_key in target_leaves.values():
                    if leave_key == "PAID LEAVE":
                        row[leave_key] = {
                            "OPENING BALANCE": 0,
                            "EARN": 0,
                            "USED": 0,
                            "BALANCE": 0
                        }
                    else:
                        row[leave_key] = {
                            "ALLOCATED": 0,
                            "USED": 0,
                            "BALANCE": 0
                        }

                # Populate leave data if exists
                if emp_id in leave_balances:
                    for leave_key, balance in leave_balances[emp_id].items():
                        used = used_leaves.get(emp_id, {}).get(leave_key, 0)

                        if leave_key == "PAID LEAVE":
                            row[leave_key] = {
                                "OPENING BALANCE": balance,
                                "EARN": 0,  # can calculate if needed
                                "USED": used,
                                "BALANCE": balance - used
                            }
                        else:
                            row[leave_key] = {
                                "ALLOCATED": balance + used,
                                "USED": used,
                                "BALANCE": balance
                            }

                report.append(row)

            return Response(report, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
 
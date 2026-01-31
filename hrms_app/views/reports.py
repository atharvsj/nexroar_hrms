from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from datetime import datetime

class NewJoinerReport(APIView):
    def post(self, request):
        try:
            from_date = request.data.get("from")
            to_date = request.data.get("to")

            if not from_date or not to_date:
                return Response(
                    {"error": "'from' and 'to' dates are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate and convert date strings to Python date objects
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()

            # Fetch employees who joined between the given dates
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, ud.employee_id, 
                           CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
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
                      AND ud.date_of_joining BETWEEN %s AND %s
                    ORDER BY ud.date_of_joining
                """, [from_date_obj, to_date_obj])

                employees = cursor.fetchall()

            # Build the report
            report = []
            for emp in employees:
                user_id, emp_id, employee_name, dept, desg, divn, manager, doj = emp
                row = {
                    "Employee ID": emp_id,
                    "Name": employee_name,  # concatenated first + last name
                    "Department": dept,
                    "Designation": desg,
                    "Division": divn,
                    "Sub-Division": "NA",
                    "Level": "NA",
                    "Headquarter": "NA",
                    "Line Manager": manager if manager else "NA",
                    "D.O.J": str(doj) if doj else None,
                }
                report.append(row)

            return Response(report, status=status.HTTP_200_OK)

        except ValueError as ve:
            return Response(
                {"error": f"Invalid date format: {ve}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from calendar import monthrange
from datetime import datetime, date


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection
from datetime import date
from calendar import monthrange


class EmployeeAttritionRateReportAPIView(APIView):

    def get(self, request):
        year = request.GET.get("year")
        department_id = request.GET.get("department_id")
        division_id = request.GET.get("division_id")

        if not year:
            return Response({"error": "Year is required"}, status=400)

        try:
            year = int(year)
        except:
            return Response({"error": "Invalid year"}, status=400)

        # Financial Year: Apr (year) → Mar (year+1)
        months = [
            ("April", year, 4), ("May", year, 5), ("June", year, 6),
            ("July", year, 7), ("August", year, 8), ("September", year, 9),
            ("October", year, 10), ("November", year, 11), ("December", year, 12),
            ("January", year + 1, 1), ("February", year + 1, 2), ("March", year + 1, 3),
        ]

        # Query employees with department/division/designation joins
        query = """
            SELECT e.employee_id, e.date_of_joining, e.date_of_leaving,
                   d.department_name, v.division_name, des.designation_name
            FROM ci_erp_users_details e
            LEFT JOIN ci_departments d ON e.department_id = d.department_id
            LEFT JOIN ci_division v ON e.division_id = v.division_id
            LEFT JOIN ci_designations des ON e.designation_id = des.designation_id
          
        """
        params = []

        if department_id and division_id:
            query += " AND (e.department_id = %s OR e.division_id = %s)"
            params.extend([department_id, division_id])
        elif department_id:
            query += " AND e.department_id = %s"
            params.append(department_id)
        elif division_id:
            query += " AND e.division_id = %s"
            params.append(division_id)

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        employees = []
        for r in rows:
            employees.append({
                "id": r[0],
                "joining": r[1],
                "leaving": r[2],
                "department": r[3],
                "division": r[4],
                "designation": r[5]
            })

        results = []
        sr_no = 1
        quarter_totals = {"Q I": [], "Q II": [], "Q III": [], "Q IV": []}
        grand_total = {"start": 0, "join": 0, "exit": 0, "end": 0}

        for idx, (month, yr, mon_num) in enumerate(months, start=1):
            start_date = date(yr, mon_num, 1)
            end_date = date(yr, mon_num, monthrange(yr, mon_num)[1])

        

            # Employees at start (carry forward until leaving date)
            start_count = sum(
                1 for emp in employees
                if emp["joining"] and emp["joining"] <= start_date
                and (not emp["leaving"] or emp["leaving"] >= start_date)
            )

            # New Joinees → count employees who joined in this month
            new_joinees = sum(
                1 for emp in employees
                if emp["joining"] and start_date <= emp["joining"] <= end_date
            )

            # Exits → count employees who left in this month
            exits = sum(
                1 for emp in employees
                if emp["leaving"] and start_date <= emp["leaving"] <= end_date
            )

            # Employees at end → start_count + previous joinees - previous exits
            end_count = start_count + new_joinees - exits


            # Attrition Rate % (Exits / Average Headcount)
            attrition_rate = round(
                (exits / ((start_count + end_count) / 2) * 100), 2
            ) if (start_count + end_count) > 0 else 0

            row = {
                "Sr No": sr_no,
                "Month": month,
                "Start": start_count,
                "New Joinees": new_joinees,
                "Exit": exits,
                "End": end_count,
                "Attrition Rate (%)": attrition_rate
            }
            results.append(row)

            # Quarter mapping
            if idx in [1, 2, 3]:   # Apr–Jun
                quarter_totals["Q I"].append(row)
            elif idx in [4, 5, 6]: # Jul–Sep
                quarter_totals["Q II"].append(row)
            elif idx in [7, 8, 9]: # Oct–Dec
                quarter_totals["Q III"].append(row)
            elif idx in [10, 11, 12]: # Jan–Mar
                quarter_totals["Q IV"].append(row)

            # Grand total
            if idx == 1:  # April Start
                grand_total["start"] = start_count
            grand_total["join"] += new_joinees
            grand_total["exit"] += exits
            if idx == 12:  # March End
                grand_total["end"] = end_count

            sr_no += 1

        # Add Quarter Totals
        for quarter, rows in quarter_totals.items():
            if rows:
                start_avg = sum(r["Start"] for r in rows) // len(rows)
                end_avg = sum(r["End"] for r in rows) // len(rows)
                exits = sum(r["Exit"] for r in rows)
                joins = sum(r["New Joinees"] for r in rows)
                attrition_rate = round((exits / ((start_avg + end_avg) / 2) * 100), 2) if (start_avg + end_avg) > 0 else 0

                results.append({
                    "Month": quarter,
                    "Start": start_avg,
                    "New Joinees": joins,
                    "Exit": exits,
                    "End": end_avg,
                    "Attrition Rate (%)": attrition_rate
                })

        # Add Grand Total
        results.append({
            "Grand Total": True,
            "Start": grand_total["start"],
            "New Joinees": grand_total["join"],
            "Exit": grand_total["exit"],
            "End": grand_total["end"],
            "Attrition Rate (%)": round((grand_total["exit"] / ((grand_total["start"] + grand_total["end"]) / 2) * 100), 2)
            if (grand_total["start"] + grand_total["end"]) > 0 else 0
        })

        return Response(results)


 
 


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection


class  AnnualManpowerReportAPIView(APIView):
    def get(self, request):
        try:
            year = int(request.GET.get("year"))  # year from query param, e.g. 2023

            # Financial year runs from Apr of given year -> Mar of next year
            financial_year = f"{year}-{year+1}"
            months = [
                f"Apr-{year}", f"May-{year}", f"Jun-{year}", f"Jul-{year}",
                f"Aug-{year}", f"Sep-{year}", f"Oct-{year}", f"Nov-{year}", f"Dec-{year}",
                f"Jan-{year+1}", f"Feb-{year+1}", f"Mar-{year+1}"
            ]

            # Prepare month-year combinations for SQL
            month_years = [
                (f"Apr-{year}", year, 4),
                (f"May-{year}", year, 5),
                (f"Jun-{year}", year, 6),
                (f"Jul-{year}", year, 7),
                (f"Aug-{year}", year, 8),
                (f"Sep-{year}", year, 9),
                (f"Oct-{year}", year, 10),
                (f"Nov-{year}", year, 11),
                (f"Dec-{year}", year, 12),
                (f"Jan-{year+1}", year + 1, 1),
                (f"Feb-{year+1}", year + 1, 2),
                (f"Mar-{year+1}", year + 1, 3),
            ]

            # Get all departments
            with connection.cursor() as cursor:
                cursor.execute("SELECT department_id, department_name FROM ci_departments ORDER BY department_name ASC")
                departments = cursor.fetchall()

            response_data = []
            total_monthly_counts = [0] * 12
            grand_total = 0
            sr_no = 1

            # Department-wise manpower counts
            for dept_id, dept_name in departments:
                manpower_counts = [0] * 12
                dept_total = 0

                for idx, (mon_name, yr, mon) in enumerate(month_years):
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM ci_erp_users_details 
                            WHERE department_id = %s
                              AND YEAR(date_of_joining) <= %s
                              AND MONTH(date_of_joining) <= %s
                        """, [dept_id, yr, mon])
                        count = cursor.fetchone()[0]

                    manpower_counts[idx] = count
                    dept_total += count
                    total_monthly_counts[idx] += count

                grand_total += dept_total

                response_data.append({
                    "sr_no": sr_no,
                    "department_id": dept_id,
                    "department_name": dept_name,
                    "manpower_counts": manpower_counts,
                    "total_for_department": dept_total
                })
                sr_no += 1

            # Add TOTAL row (no Sr.No)
            response_data.append({
                "sr_no": None,
                "department_id": "TOTAL",
                "department_name": "All Departments",
                "manpower_counts": total_monthly_counts,
                "total_for_department": grand_total
            })

            response = {
                "financial_year": financial_year,
                "months": months,
                "data": response_data
            }

            return Response(response)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
 

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class EmployeeMasterReportAPIView(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        u.id as user_id,
                        d.employee_id,
                        CONCAT(u.first_name, ' ', COALESCE(u.middle_name,''), ' ', u.last_name) as full_name,
                        u.contact_number,
                        u.email,
                        u.gender,
                        d.date_of_birth,
                        d.marital_status,
                        d.blood_group,
                        d.aadhar_no,
                        d.pan_number,
                        d.uan_number,
                        d.date_of_joining,
                        d.date_of_leaving,
                        u.is_active,

                        dept.department_name as department,
                        desg.designation_name as designation,
                        divi.division_name as division,

                        u.address_1, u.address_2, u.city,
                        st.category_name as state,
                        ctry.category_name as country,
                        u.zipcode,

                        d.account_title, d.account_number, d.bank_name, d.ifsc_code, d.swift_code, d.bank_branch,

                        d.contact_full_name, d.contact_phone_no
                    FROM ci_erp_users u
                    JOIN ci_erp_users_details d ON u.id = d.user_id
                    LEFT JOIN ci_departments dept ON d.department_id = dept.department_id
                    LEFT JOIN ci_designations desg ON d.designation_id = desg.designation_id
                    LEFT JOIN ci_division divi ON d.division_id = divi.division_id
                    LEFT JOIN ci_erp_constants st ON u.state = st.constants_id
                    LEFT JOIN ci_erp_constants ctry ON u.country = ctry.constants_id
                """)
                users = dictfetchall(cursor)  # fetch all employees

            response_data = []
            sr_no = 1

            for user in users:
                # fetch assets for each employee
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            a.assets_name,
                            cat.category_name as category,
                            br.category_name as brand,
                            a.manufacturer,
                            a.serial_number
                        FROM ci_assets a
                        LEFT JOIN ci_erp_constants cat ON a.assets_category_id = cat.constants_id
                        LEFT JOIN ci_erp_constants br ON a.brand_id = br.constants_id
                        WHERE a.employee_id = %s
                    """, [user["user_id"]])
                    assets = dictfetchall(cursor)

                response_data.append({
                    "Sr No.": sr_no,
                    "Employee ID": user.get("employee_id"),
                    "Name": user.get("full_name"),
                    "Contact Number (Personal)": user.get("contact_number"),
                    "Email Id (Personal)": user.get("email"),
                    "Gender": user.get("gender"),
                    "Date of Birth": user.get("date_of_birth"),
                    "Age": None,
                    "Marital Status": (
                        "Unmarried" if user.get("marital_status") == 0 else
                        "Married" if user.get("marital_status") == 1 else "Unknown"
                    ),
                    "Blood Group": user.get("blood_group"),
                    "Education": None,
                    "Degree": None,

                    # Permanent Address
                    "Address": user.get("address_1"),
                    "Country": user.get("country"),
                    "State": user.get("state"),
                    "District": None,
                    "Tehsil": None,
                    "Village": None,
                    "Pin code": user.get("zipcode"),

                    # Work Details
                    "Department": user.get("department"),
                    "Designation": user.get("designation"),
                    "Division": user.get("division"),
                    "D.O.J.": user.get("date_of_joining"),
                    "Status": "Active" if user.get("is_active") == 1 else "Inactive",

                    # Bank account details
                    "Account Holder Name": user.get("account_title"),
                    "Account Number": user.get("account_number"),
                    "Bank Name": user.get("bank_name"),
                    "IFSC": user.get("ifsc_code"),
                    "Swift Code": user.get("swift_code"),
                    "Bank Branch": user.get("bank_branch"),

                    # Emergency contact
                    "Emergency Contact Name": user.get("contact_full_name"),
                    "Emergency Contact Number": user.get("contact_phone_no"),

                    # Exit info
                    "Exit Date": user.get("date_of_leaving"),

                    # Assets
                    "No. of Asset Allocated": len(assets),
                    "Assets": assets
                })

                sr_no += 1

            return Response(response_data)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from datetime import date, datetime


def calculate_work_duration(doj):
    """Helper function to calculate work duration from DOJ to today."""
    if not doj:
        return "NA"
    try:
        doj_date = doj if isinstance(doj, date) else datetime.strptime(str(doj), "%Y-%m-%d").date()
        today = date.today()
        years = today.year - doj_date.year
        months = today.month - doj_date.month
        days = today.day - doj_date.day

        if days < 0:
            months -= 1
            prev_month = (today.month - 1) if today.month > 1 else 12
            prev_year = today.year if today.month > 1 else today.year - 1
            days += (date(prev_year, prev_month % 12 + 1, 1) - date(prev_year, prev_month, 1)).days

        if months < 0:
            years -= 1
            months += 12

        return f"{years} Years {months} Months {days} Days"
    except Exception:
        return "NA"
 
class HRMasterDataAPIView(APIView):
    """
    API to return HR Master Data.
    Filters: status = Active / Inactive / All
    """

    def post(self, request):
        status_filter = request.data.get("status", "All")  # Active / Inactive / All

        query = """
            SELECT 
                u.id as user_id,
                d.employee_id,
                CONCAT(u.first_name, ' ', u.last_name) as name,
                u.gender,
                d.date_of_birth,
                d.marital_status,
                d.blood_group,
                dep.department_name,
                des.designation_name,
                divi.division_name,
                d.date_of_joining,
                hub.employee_hub_name,
                d.aadhar_no,
                d.pan_number,
                d.uan_number,
                d.manager,
                CONCAT(m.first_name, ' ', m.last_name) as manager_name,
                d.ctc_yearly,
                d.gross_salary,
                d.basic_salary,
                d.confirmation_date,
                u.is_active
            FROM ci_erp_users u
            JOIN ci_erp_users_details d ON u.id = d.user_id
            LEFT JOIN ci_departments dep ON d.department_id = dep.department_id
            LEFT JOIN ci_designations des ON d.designation_id = des.designation_id
            LEFT JOIN ci_division divi ON d.division_id = divi.division_id
            LEFT JOIN ci_employee_hub hub ON u.employee_hub_id = hub.employee_hub_id
            LEFT JOIN ci_erp_users m on d.manager=m.id
        """

        if status_filter == "Active":
            query += " WHERE u.is_active = 1"
        elif status_filter == "Inactive":
            query += " WHERE u.is_active = 0"

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        employees = []
        for row in rows:
            record = dict(zip(columns, row))
            employees.append({
                "Employee ID": record["employee_id"],
                "Name": record["name"],
                "Gender": record["gender"],
                "Date of Birth": record["date_of_birth"],
                "Age": self.get_age(record["date_of_birth"]),
                "Marital Status": (
                "Married" if str(record["marital_status"]) == "1"
                else "Single" if str(record["marital_status"]) == "0"
                else "NA"),
                "Blood Group": record["blood_group"] if record["blood_group"] else "NA",
                "Education": "NA",
                "Degree": "NA",
                "Department": record["department_name"] if record["department_name"] else "NA",
                "Designation": record["designation_name"] if record["designation_name"] else "NA",
                "Division": record["division_name"] if record["division_name"] else "NA",
                "Sub-Division": "NA",
                "Level": "NA",
                "D.O.J.": record["date_of_joining"],
                "Work Duration": calculate_work_duration(record["date_of_joining"]),
                "Head Quarter": "NA",
                "Holiday Hub": record["employee_hub_name"] if record["employee_hub_name"] else "NA",
                "Adhar No.": record["aadhar_no"] if record["aadhar_no"] else "NA",
                "PAN No.": record["pan_number"] if record["pan_number"] else "NA",
                "UAN No.": record["uan_number"] if record["uan_number"] else "NA",
                "Line Manager": record["manager"] if record["manager"] else "NA",
                "Manager Name": record["manager_name"] if record["manager_name"] else "NA",
                "CTC": record["ctc_yearly"] if record["ctc_yearly"] else "NA",
                "Gross Salary": record["gross_salary"] if record["gross_salary"] else "NA",
                "Basic + DA": record["basic_salary"] if record["basic_salary"] else "NA",
                "Gratuity": "NA",
                "Notice Period": "NA",
                "Date of Confirmation": record["confirmation_date"] if record["confirmation_date"] else "NA",
                "Exit Type": "NA",
                "Resignation Date": "NA",
                "Date of Exit": "NA",
                "F & F Status": "NA",
                "Status": "Active" if record["is_active"] == 1 else "Inactive"
            })

        return Response({"status": "success", "data": employees}, status=status.HTTP_200_OK)

    def get_age(self, dob):
        if not dob:
            return "NA"
        try:
            dob_date = dob if isinstance(dob, date) else datetime.strptime(str(dob), "%Y-%m-%d").date()
            today = date.today()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            return age
        except Exception:
            return "NA"



class EmployeeExitReportAPIView(APIView):
    """
    API to return Employee Exit Report.
    Filters: from, to (on date_of_leaving)
    """

    def post(self, request):
        from_date = request.data.get("from")
        to_date = request.data.get("to")

        if not from_date or not to_date:
            return Response({"status": "error", "message": "Both 'from' and 'to' dates are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        query = """
            SELECT 
                u.id as user_id,
                d.employee_id,
                CONCAT(u.first_name, ' ', u.last_name) as name,
                dep.department_name,
                des.designation_name,
                divi.division_name,
                d.date_of_joining,
                d.date_of_leaving,
                d.manager,
                CONCAT(
                    m.first_name, ' ', m.last_name
                ) as manager_name
            FROM ci_erp_users u
            JOIN ci_erp_users_details d ON u.id = d.user_id
            LEFT JOIN ci_departments dep ON d.department_id = dep.department_id
            LEFT JOIN ci_designations des ON d.designation_id = des.designation_id
            LEFT JOIN ci_division divi ON d.division_id = divi.division_id
            LEFT JOIN ci_erp_users m ON d.manager = m.id
            WHERE d.date_of_leaving BETWEEN %s AND %s
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [from_date, to_date])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        employees = []
        for row in rows:
            record = dict(zip(columns, row))
            return_asset = self.check_return_asset(record["employee_id"])

            employees.append({
                "Employee ID": record["employee_id"],
                "Name": record["name"],
                "Department": record["department_name"] if record["department_name"] else "NA",
                "Designation": record["designation_name"] if record["designation_name"] else "NA",
                "Division": record["division_name"] if record["division_name"] else "NA",
                "Sub-Division": "NA",
                "Level": "NA",
                "Headquarter": "NA",
                "Line Manager": record["manager_name"] if record["manager_name"] else "NA",
                "D.O.J": record["date_of_joining"].strftime("%Y-%m-%d") if record["date_of_joining"] else "NA",
                "Exit Type": "NA",
                "Last Working Date": record["date_of_leaving"].strftime("%Y-%m-%d") if record["date_of_leaving"] else "NA",
                "Return Asset": return_asset,
                "Exit Interview Questionnaire": "NA",
                "Employee Clearance Form": "NA",
                "Full & Final settlement": "NA",
                "Relieving letter": "NA",
                "Experience Letter": "NA"
            })

        return Response({"status": "success", "data": employees}, status=status.HTTP_200_OK)

    def check_return_asset(self, employee_id):
        query = """
            SELECT 
                SUM(CASE WHEN employee_confirmation='accepted' THEN 1 ELSE 0 END) as assigned_count,
                SUM(CASE WHEN employee_confirmation='accepted' AND return_request_status='2' THEN 1 ELSE 0 END) as returned_count
            FROM ci_assets
            WHERE employee_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [employee_id])
            row = cursor.fetchone()

        # Ensure None values are treated as 0
        assigned_count = row[0] if row[0] is not None else 0
        returned_count = row[1] if row[1] is not None else 0

        # If no assets are assigned → consider as "Yes"
        if assigned_count == 0:
            return "Yes"

        return "Yes" if returned_count >= assigned_count else "No"
    
# class PerformanceManagementReportAPIView(APIView):

#     def post(self, request):
#         employee_id = request.data.get("employee_id")

#         if employee_id is None:
#             return Response(
#                 {"status": "error", "message": "'employee_id' is required"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Base query (only active employees)
#         query = """
#             SELECT 
#                 u.id as user_id,
#                 d.employee_id,
#                 CONCAT(u.first_name, ' ', u.last_name) as name,
#                 dep.department_name,
#                 des.designation_name,
#                 divi.division_name,
#                 d.date_of_joining,
#                 CONCAT(m.first_name, ' ', m.last_name) as manager_name
#             FROM ci_erp_users u
#             JOIN ci_erp_users_details d ON u.id = d.user_id
#             LEFT JOIN ci_departments dep ON d.department_id = dep.department_id
#             LEFT JOIN ci_designations des ON d.designation_id = des.designation_id
#             LEFT JOIN ci_division divi ON d.division_id = divi.division_id
#             LEFT JOIN ci_erp_users m ON d.manager = m.id
#             WHERE u.is_active = 1
#         """

#         params = []
#         if employee_id != 0:  # Specific employee
#             query += " AND d.employee_id = %s"
#             params.append(employee_id)

#         with connection.cursor() as cursor:
#             cursor.execute(query, params)
#             rows = cursor.fetchall()
#             columns = [col[0] for col in cursor.description]

#         # Dynamic financial year calculation
#         today = date.today()
#         if today.month >= 4:  # April onwards → current FY
#             financial_year = f"{today.year}-{today.year + 1}"
#         else:  # Jan-Mar → previous FY
#             financial_year = f"{today.year - 1}-{today.year}"

#         employees = []
#         for row in rows:
#             record = dict(zip(columns, row))

#             employees.append({
#                 "Employee ID": record["employee_id"],
#                 "Name": record["name"],
#                 "Department": record["department_name"] if record["department_name"] else "NA",
#                 "Designation": record["designation_name"] if record["designation_name"] else "NA",
#                 "Division": record["division_name"] if record["division_name"] else "NA",
#                 "Sub-Division": "NA",
#                 "Level": "NA",
#                 "Headquarter": "NA",
#                 "Line Manager": record["manager_name"] if record["manager_name"] else "NA",
#                 "D.O.J": record["date_of_joining"].strftime("%Y-%m-%d") if record["date_of_joining"] else "NA",
#                 "Financial Year": financial_year,
#                 "PDR": "NA"
#             })

#         return Response({"status": "success", "data": employees}, status=status.HTTP_200_OK)


from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class PerformanceManagementReportAPIView(APIView):

    def post(self, request):
        employee_id = request.data.get("employee_id")

        if employee_id is None:
            return Response(
                {"status": "error", "message": "'employee_id' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Base query (only active employees)
        query = """
            SELECT 
                u.id as user_id,
                d.employee_id,
                CONCAT(u.first_name, ' ', u.last_name) as name,
                dep.department_name,
                des.designation_name,
                divi.division_name,
                d.date_of_joining,
                CONCAT(m.first_name, ' ', m.last_name) as manager_name
            FROM ci_erp_users u
            JOIN ci_erp_users_details d ON u.id = d.user_id
            LEFT JOIN ci_departments dep ON d.department_id = dep.department_id
            LEFT JOIN ci_designations des ON d.designation_id = des.designation_id
            LEFT JOIN ci_division divi ON d.division_id = divi.division_id
            LEFT JOIN ci_erp_users m ON d.manager = m.id
            WHERE u.is_active = 1
        """

        params = []
        if employee_id != 0:  # Specific employee
            query += " AND d.employee_id = %s"
            params.append(employee_id)

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Dynamic financial year calculation
        today = date.today()
        if today.month >= 4:  # April onwards → current FY
            financial_year = f"{today.year}-{today.year + 1}"
        else:  # Jan-Mar → previous FY
            financial_year = f"{today.year - 1}-{today.year}"

        employees = []
        for row in rows:
            record = dict(zip(columns, row))

            # Since date_of_joining may already be a string, avoid .strftime()
            doj_value = record["date_of_joining"]
            doj_str = doj_value if doj_value else "NA"

            employees.append({
                "Employee ID": record["employee_id"],
                "Name": record["name"],
                "Department": record["department_name"] or "NA",
                "Designation": record["designation_name"] or "NA",
                "Division": record["division_name"] or "NA",
                "Sub-Division": "NA",
                "Level": "NA",
                "Headquarter": "NA",
                "Line Manager": record["manager_name"] or "NA",
                "D.O.J": doj_str,
                "Financial Year": financial_year,
                "PDR": "NA"
            })

        return Response(
            {"status": "success", "data": employees},
            status=status.HTTP_200_OK
        )



class AnnualAppraisalReportAPIView(APIView):
    """
    GET API for Annual Appraisal Report.
    No filters → returns all active employees with hardcoded appraisal fields.
    """

    def get(self, request):
        query = """
            SELECT 
                u.id as user_id,
                d.employee_id,
                CONCAT(u.first_name, ' ', u.last_name) as name,
                dep.department_name,
                des.designation_name,
                divi.division_name,
                d.date_of_joining,
                CONCAT(m.first_name, ' ', m.last_name) as manager_name
            FROM ci_erp_users u
            JOIN ci_erp_users_details d ON u.id = d.user_id
            LEFT JOIN ci_departments dep ON d.department_id = dep.department_id
            LEFT JOIN ci_designations des ON d.designation_id = des.designation_id
            LEFT JOIN ci_division divi ON d.division_id = divi.division_id
            LEFT JOIN ci_erp_users m ON d.manager = m.id
            WHERE u.is_active = 1
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        employees = []
        for row in rows:
            record = dict(zip(columns, row))

            employees.append({
                "Employee ID": record["employee_id"],
                "Name": record["name"],
                "Department": record["department_name"] if record["department_name"] else "NA",
                "Designation": record["designation_name"] if record["designation_name"] else "NA",
                "Division": record["division_name"] if record["division_name"] else "NA",
                "Sub-Division": "NA",
                "Level": "NA",
                "Headquarter": "NA",
                "Line Manager": record["manager_name"] if record["manager_name"] else "NA",
                "D.O.J": record["date_of_joining"].strftime("%Y-%m-%d") if record["date_of_joining"] else "NA",
                "KIP Ach %": "NA",
                "KRA Ach %": "NA",
                "Total Ach %": "NA",
                "Final Rating": "NA",
                "LM Feedback": "NA",
                "HOD Feedback": "NA",
                "HR Feedback": "NA",
                "Employee Comment": "NA",
                "Reccommended Action": "NA",
                "% of Increment": "NA",
                "Status": "NA"
            })

        return Response({"status": "success", "data": employees}, status=status.HTTP_200_OK)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class SalaryReportAPIView(APIView):

    def get(self, request):
        try:
            # Filters from query params
            month = request.GET.get("month")
            year = request.GET.get("year")
            

            if not (month and year):
                return Response({"error": "month and year are required"}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        -- Basic Employee Info
                        pr.payroll_report_id AS sr_no,
                        ud.employee_id,
                        pr.employee_name,
                        d.department_name AS department,
                        dg.designation_name AS designation,

                        -- Days Section
                        pr.gender AS gender,
                        pr.gross_salary AS gross_salary,
                        pr.payable_days AS days,

                        -- ESIC + Gross Earning
                        pr.esic_applicable AS esic_applicable,
                        pr.gross_earning AS gross_earning,

                        -- Earnings Section
                        pr.basic_plus_da AS basic_da,
                        pr.hra AS hra,
                        pr.conveyance_allowance AS conveyance_allowance,
                        pr.medical_allowance AS medical_allowance,
                        pr.arrears AS arrears,

                        -- Deduction Section
                        pr.pf AS pf,
                        pr.esic AS esic,
                        pr.pt AS pt,
                        pr.tds AS tds,
                        pr.total_deduction AS total_deduction,

                        -- Net Pay + Remark
                        pr.net_pay AS net_pay,
                        pr.status AS remark,

                        -- Bank Payment Details
                        ud.bank_name AS bank_name,
                        ud.ifsc_code AS ifsc_code,
                        ud.account_number AS account_number,
                        ud.account_title AS account_holder_name,
                        pr.net_pay AS net_payment_amount,
                        pr.status AS bank_remark

                    FROM ci_payroll_report pr
                    LEFT JOIN ci_erp_users_details ud ON pr.employee_id = ud.employee_id
                    LEFT JOIN ci_designations dg ON ud.designation_id = dg.designation_id
                    LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                    WHERE pr.month = %s AND pr.year = %s
                """, [month, year])

                rows = dictfetchall(cursor)

            return Response(rows)

        except Exception as e:
            return Response({"error": str(e)}, status=500)




from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class PTReportAPIView(APIView):
    def get(self, request):
        try:
            # Filters from query params
            month = request.GET.get("month")
            year = request.GET.get("year")

            if not (month and year):
                return Response({"error": "month and year are required"}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        pr.payroll_report_id AS sr_no,
                        ud.employee_id,
                        pr.employee_name, 
                        pr.payable_days AS days,
                        ud.ctc_monthly AS salary_per_month,
                        pr.total_earnings,
                        pr.pt
                    FROM ci_payroll_report pr
                    LEFT JOIN ci_erp_users_details ud ON pr.employee_id = ud.employee_id
                    WHERE pr.month = %s AND pr.year = %s
                """, [month, year])

                rows = dictfetchall(cursor)

            return Response(rows)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection

class AnnualManpowerReportAPIView(APIView):
    def get(self, request):
        try:
            year = int(request.GET.get("year"))  # year from query param, e.g. 2023

            # Financial year runs from Apr of given year -> Mar of next year
            financial_year = f"{year}-{year+1}"
            months = [
                f"Apr-{year}", f"May-{year}", f"Jun-{year}", f"Jul-{year}",
                f"Aug-{year}", f"Sep-{year}", f"Oct-{year}", f"Nov-{year}", f"Dec-{year}",
                f"Jan-{year+1}", f"Feb-{year+1}", f"Mar-{year+1}"
            ]

            # Prepare month-year combinations for SQL
            month_years = [
                (f"Apr-{year}", year, 4),
                (f"May-{year}", year, 5),
                (f"Jun-{year}", year, 6),
                (f"Jul-{year}", year, 7),
                (f"Aug-{year}", year, 8),
                (f"Sep-{year}", year, 9),
                (f"Oct-{year}", year, 10),
                (f"Nov-{year}", year, 11),
                (f"Dec-{year}", year, 12),
                (f"Jan-{year+1}", year + 1, 1),
                (f"Feb-{year+1}", year + 1, 2),
                (f"Mar-{year+1}", year + 1, 3),
            ]

            # Get all departments
            with connection.cursor() as cursor:
                cursor.execute("SELECT department_id, department_name FROM ci_departments ORDER BY department_name ASC")
                departments = cursor.fetchall()

            response_data = []
            total_monthly_counts = [0] * 12
            grand_total = 0
            sr_no = 1

            # Department-wise manpower counts
            for dept_id, dept_name in departments:
                manpower_counts = []
                dept_total = 0

                for idx, (mon_name, yr, mon) in enumerate(month_years):
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM ci_erp_users_details 
                            WHERE department_id = %s  
                              AND (
                                  YEAR(date_of_joining) < %s
                                  OR (YEAR(date_of_joining) = %s AND MONTH(date_of_joining) <= %s)
                              )
                        """, [dept_id, yr, yr, mon])
                        count = cursor.fetchone()[0]

                    manpower_counts.append({
                        "month": mon_name,
                        "count": count
                    })
                    dept_total += count
                    total_monthly_counts[idx] += count

                grand_total += dept_total

                response_data.append({
                    "sr_no": sr_no,
                    "department_id": dept_id,
                    "department_name": dept_name,
                    "manpower_counts": manpower_counts,
                    "total_for_department": dept_total
                })
                sr_no += 1

            # Add TOTAL row (no Sr.No) with same structure
            total_manpower_counts = []
            for idx, (mon_name, _, _) in enumerate(month_years):
                total_manpower_counts.append({
                    "month": mon_name,
                    "count": total_monthly_counts[idx]
                })

            response_data.append({
                "sr_no": None,
                "department_id": "TOTAL",
                "department_name": "All Departments",
                "manpower_counts": total_manpower_counts,
                "total_for_department": grand_total
            })

            response = {
                "financial_year": financial_year,
                "months": months,
                "data": response_data
            }

            return Response(response)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


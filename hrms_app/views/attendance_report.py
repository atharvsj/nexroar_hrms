from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# class MonthlyAttendanceReport(APIView):
#     def post(self, request):
#         try:
#             query_year = request.data.get("year")
#             if not query_year:
#                 return Response(
#                     {"error": "Year is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             try:
#                 query_year = int(query_year)
#             except ValueError:
#                 return Response(
#                     {"error": "Year must be an integer"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # 1️⃣ fetch employee info
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT u.id, ud.employee_id, u.first_name, u.last_name,
#                            d.department_name, dg.designation_name, divn.division_name,
#                            CONCAT(m.first_name, ' ', m.last_name) AS manager_name,
#                            ud.date_of_joining
#                     FROM ci_erp_users u
#                     JOIN ci_erp_users_details ud ON u.id = ud.user_id
#                     LEFT JOIN ci_departments d ON ud.department_id = d.department_id
#                     LEFT JOIN ci_designations dg ON ud.designation_id = dg.designation_id
#                     LEFT JOIN ci_division divn ON ud.division_id = divn.division_id
#                     LEFT JOIN ci_erp_users m ON ud.manager = m.id
                    
#                 """)
#                 employees = cursor.fetchall()

#             emp_map = {}
#             for emp in employees:
#                 user_id, employee_id, fname, lname, dept, desg, divn, manager_name, doj = emp
#                 emp_map[employee_id] = {
#                     "Employee ID": employee_id,
#                     "Name": f"{fname} {lname}",
#                     "Department": dept,
#                     "Designation": desg,
#                     "Division": divn,
#                     "Sub-Division": "NA",
#                     "Level": "NA",
#                     "Headquarter": "NA",
#                     "Line Manager": manager_name,
#                     "D.O.J": str(doj) if doj else None,
#                     "Apr": 0.0, "May": 0.0, "June": 0.0, "July": 0.0,
#                     "Aug": 0.0, "Sept": 0.0, "Oct": 0.0, "Nov": 0.0,
#                     "Dec": 0.0, "Jan": 0.0, "Feb": 0.0, "March": 0.0,
#                     "Total": 0.0,
#                 }

#             if not emp_map:
#                 return Response([], status=status.HTTP_200_OK)

#             # 2️⃣ fetch attendance for all employees in one query
#             fy_start = f"{query_year}-04-01"
#             fy_end = f"{query_year+1}-03-31"

#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT emp_id,
#                            YEAR(attendance_date) as y,
#                            MONTH(attendance_date) as m,
#                            COUNT(*) as full_days,
#                            SUM(CASE WHEN is_half_day='Y' THEN 1 ELSE 0 END) as half_days
#                     FROM ci_biomatric_data
#                     WHERE attendance_date BETWEEN %s AND %s
#                       AND (status='P' OR attendance_status='Present')
#                     GROUP BY emp_id, YEAR(attendance_date), MONTH(attendance_date)
#                 """, [fy_start, fy_end])
#                 attendance = cursor.fetchall()

#             # 3️⃣ map DB month → report month
#             month_map = {
#                 4: "Apr", 5: "May", 6: "June", 7: "July",
#                 8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov",
#                 12: "Dec", 1: "Jan", 2: "Feb", 3: "March"
#             }

#             # 4️⃣ aggregate into emp_map
#             for emp_id, y, m, full_days, half_days in attendance:
#                 if emp_id not in emp_map:
#                     continue
#                 month_name = month_map.get(m)
#                 present_days = float(full_days or 0) + float(half_days or 0) * 0.5
#                 emp_map[emp_id][month_name] += present_days
#                 emp_map[emp_id]["Total"] += present_days

#             return Response(list(emp_map.values()), status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
 
class MonthlyAttendanceReport(APIView):
    def post(self, request):
        try:
            query_year = request.data.get("year")
            if not query_year:
                return Response(
                    {"error": "Year is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                query_year = int(query_year)
            except ValueError:
                return Response(
                    {"error": "Year must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 1️⃣ fetch employee info
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

            emp_map = {}
            for emp in employees:
                user_id, employee_id, fname, lname, dept, desg, divn, manager_name, doj = emp
                emp_map[employee_id] = {
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
                    "Apr": 0.0, "May": 0.0, "June": 0.0, "July": 0.0,
                    "Aug": 0.0, "Sept": 0.0, "Oct": 0.0, "Nov": 0.0,
                    "Dec": 0.0, "Jan": 0.0, "Feb": 0.0, "March": 0.0,
                    "Total": 0.0,
                }

            if not emp_map:
                return Response([], status=status.HTTP_200_OK)

            # 2️⃣ fetch attendance for all employees in one query
            fy_start = f"{query_year}-04-01"
            fy_end = f"{query_year+1}-03-31"

            with connection.cursor() as cursor:
                cursor.execute("""
                   SELECT emp_id,
       YEAR(attendance_date) as y,
       MONTH(attendance_date) as m,
       COUNT(DISTINCT attendance_date) as present_days
FROM ci_biomatric_data
WHERE attendance_date BETWEEN %s AND %s
  AND (status='P' OR attendance_status='Present')
GROUP BY emp_id, YEAR(attendance_date), MONTH(attendance_date);

                """, [fy_start, fy_end])
                attendance = cursor.fetchall()

            # 3️⃣ map DB month → report month
            month_map = {
                4: "Apr", 5: "May", 6: "June", 7: "July",
                8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov",
                12: "Dec", 1: "Jan", 2: "Feb", 3: "March"
            }

            # 4️⃣ aggregate into emp_map
            for emp_id, y, m, present_days in attendance:
                if emp_id not in emp_map:
                    continue
                month_name = month_map.get(m)
                emp_map[emp_id][month_name] += float(present_days or 0)
                emp_map[emp_id]["Total"] += float(present_days or 0)


            return Response(list(emp_map.values()), status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
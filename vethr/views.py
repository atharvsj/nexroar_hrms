from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

# class EmployeeLeaveBalanceAPIView(APIView):
#     def get(self, request):
#         employee_id = request.GET.get('employee_id')
#         if not employee_id:
#             return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)

#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT leave_type_id ,leave_type ,balance_leave ,year FROM ci_leave_balance WHERE employee_id = %s;

#             """, [employee_id])
#             columns = [col[0] for col in cursor.description]
#             rows = cursor.fetchall()

#         result = [dict(zip(columns, row)) for row in rows]
#         return Response(result, status=status.HTTP_200_OK)


# class EmployeeLeaveBalanceAPIView(APIView):
#     def get(self, request):
#         employee_id = request.GET.get('employee_id')
#         if not employee_id:
#             return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
 
#         try:
#             with connection.cursor() as cursor:
#                 # Fetch gender of employee
#                 cursor.execute("""
#                     SELECT gender
#                     FROM ci_erp_users
#                     WHERE username = %s
#                 """, [employee_id])
#                 gender_row = cursor.fetchone()
#                 if not gender_row:
#                     return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
               
#                 gender = gender_row[0]  # '1' for male, '2' for female
 
#                 # Fetch leave balances
#                 cursor.execute("""
#                         SELECT
#                             lb.leave_type_id,
#                             ec.type,
#                             ec.category_name,
#                             ec.field_one AS days_per_year,
#                             lb.balance_leave,
#                             lb.year
#                         FROM ci_leave_balance lb
#                         INNER JOIN ci_erp_constants ec
#                             ON lb.leave_type_id = ec.constants_id
#                         WHERE lb.employee_id = %s
#                     """, [employee_id])
 
#                 columns = [col[0] for col in cursor.description]
#                 rows = cursor.fetchall()
 
 
#             result = []
#             for row in rows:
#                 row_dict = dict(zip(columns, row))
 
#                 leave_type = row_dict.get('leave_type', '').strip()
 
#                 # Filter based on gender
#                 if gender == '1' and leave_type == 'Maternity Leave':
#                     continue  # Skip Maternity Leave for male
#                 elif gender == '2' and leave_type == 'Paternity Leave':
#                     continue  # Skip Paternity Leave for female
 
#                 result.append(row_dict)
 
#             return Response(result, status=status.HTTP_200_OK)
 
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

# class EmployeeLeaveBalanceAPIView(APIView):
#     def get(self, request):
#         employee_id = request.GET.get('employee_id')
#         if not employee_id:
#             return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
            
#             with connection.cursor() as cursor:
#                 #print(f"🔍 Input Employee ID: {employee_id}")  # Console print

#                 # Get user_id from employee_id
#                 cursor.execute("""
#                     SELECT user_id
#                     FROM ci_erp_users_details
#                     WHERE employee_id = %s
#                 """, [employee_id])
#                 user_row = cursor.fetchone()

#                 if not user_row:
#                     return Response({'error': 'User ID not found for this employee_id'}, status=status.HTTP_404_NOT_FOUND)

#                 user_id = user_row[0]
#                 #print(f"✅ Mapped User ID: {user_id}")  # Console print

#                 # Get gender from user_id and ensure it's clean
#                 cursor.execute("""
#                     SELECT TRIM(gender)
#                     FROM ci_erp_users
#                     WHERE id = %s
#                 """, [user_id])
#                 gender_row = cursor.fetchone()

#                 if not gender_row or not gender_row[0]:
#                     return Response({'error': 'Gender not found for this user_id'}, status=status.HTTP_404_NOT_FOUND)

#                 gender = gender_row[0].strip()
#                 #print(f"🧬 User Gender (raw): {gender}")  # Console print

#                 is_male = gender == '1'
#                 is_female = gender == '2'

#                 # Get all leave types from constants
#                 cursor.execute("""
#                     SELECT 
#                         ec.constants_id AS leave_type_id,
#                         ec.type,
#                         ec.category_name,
#                         ec.field_one AS days_per_year,
#                         IFNULL(lb.balance_leave, 0) AS balance_leave,
#                         IFNULL(lb.year, '') AS year
#                     FROM ci_erp_constants ec
#                     LEFT JOIN ci_leave_balance lb
#                         ON lb.leave_type_id = ec.constants_id AND lb.employee_id = %s
#                     WHERE ec.type = 'leave_type' and ec.constants_id != 1749
#                 """, [employee_id])

#                 columns = [col[0] for col in cursor.description]
#                 rows = cursor.fetchall()

#                 result = []
#                 for row in rows:
#                     leave_data = dict(zip(columns, row))
#                     leave_type_id = leave_data["leave_type_id"]

#                     # Gender-specific leave filtering
#                     if leave_type_id == 1098 and not is_male:
#                         continue  # Paternity Leave – skip if not male
#                     if leave_type_id == 187 and not is_female:
#                         continue  # Maternity Leave – skip if not female

#                     result.append(leave_data)

#                 return Response(result, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EmployeeLeaveBalanceAPIView(APIView):
    def get(self, request):
        employee_id = request.GET.get('employee_id')
        if not employee_id:
            return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:

            current_year = datetime.now().year  # Get current year dynamically

            with connection.cursor() as cursor:
                #print(f"🔍 Input Employee ID: {employee_id}")  # Console print

                # Get user_id from employee_id
                cursor.execute("""
                    SELECT user_id
                    FROM ci_erp_users_details
                    WHERE employee_id = %s
                """, [employee_id])
                user_row = cursor.fetchone()

                if not user_row:
                    return Response({'error': 'User ID not found for this employee_id'}, status=status.HTTP_404_NOT_FOUND)

                user_id = user_row[0]
                #print(f"✅ Mapped User ID: {user_id}")  # Console print

                # Get gender from user_id and ensure it's clean
                cursor.execute("""
                    SELECT TRIM(gender)
                    FROM ci_erp_users
                    WHERE id = %s
                """, [user_id])
                gender_row = cursor.fetchone()

                if not gender_row or not gender_row[0]:
                    return Response({'error': 'Gender not found for this user_id'}, status=status.HTTP_404_NOT_FOUND)

                gender = gender_row[0].strip()
                #print(f"🧬 User Gender (raw): {gender}")  # Console print

                is_male = gender == '1'
                is_female = gender == '2'

                # Get all leave types from constants
                cursor.execute("""
                    SELECT 
                        ec.constants_id AS leave_type_id,
                        ec.type,
                        ec.category_name,
                        ec.field_one AS days_per_year,
                        IFNULL(lb.balance_leave, 0) AS balance_leave,
                        IFNULL(lb.year, '') AS year
                    FROM ci_erp_constants ec
                    LEFT JOIN ci_leave_balance lb
                        ON lb.leave_type_id = ec.constants_id AND lb.employee_id = %s AND lb.year = %s
                    WHERE ec.type = 'leave_type' and ec.constants_id != 1749
                """, [employee_id, current_year])

                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

                result = []
                for row in rows:
                    leave_data = dict(zip(columns, row))
                    leave_type_id = leave_data["leave_type_id"]

                    # Gender-specific leave filtering
                    if leave_type_id == 1098 and not is_male:
                        continue  # Paternity Leave – skip if not male
                    if leave_type_id == 187 and not is_female:
                        continue  # Maternity Leave – skip if not female

                    result.append(leave_data)

                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

#########################################################################################################################################

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db import connection

# class EmployeeLeavehistoryAPIView(APIView):
#     def get(self, request):
#         employee_id = request.GET.get('employee_id')
#         if not employee_id:
#             return Response({'error': 'employee_id is required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             with connection.cursor() as cursor:
#                 # Fetch leave balances
#                 cursor.execute("""
#                     SELECT leave_type_id, leave_type, balance_leave, year 
#                     FROM ci_leave_balance 
#                     WHERE employee_id = %s
#                 """, [employee_id])
#                 balance_rows = cursor.fetchall()
#                 balance_columns = [col[0] for col in cursor.description]

#                 # Fetch field_one mapping from ci_erp_constants
#                 cursor.execute("""
#                     SELECT category_name, field_one 
#                     FROM ci_erp_constants 
#                     WHERE type = 'leave_type'
#                 """)
#                 field_map = {row[0]: row[1] for row in cursor.fetchall()}

#                 # Fetch leave_taken as a map: leave_type_id -> total leaves taken
#                 cursor.execute("""
#                     SELECT leave_type_id, SUM(number_of_leave) 
#                     FROM ci_leave_count 
#                     WHERE employee_id = %s 
#                     GROUP BY leave_type_id
#                 """, [employee_id])
#                 leave_taken_map = {str(row[0]): float(row[1]) for row in cursor.fetchall()}

#             # Build final response
#             result = []
#             for row in balance_rows:
#                 row_dict = dict(zip(balance_columns, row))
#                 leave_type = row_dict.get('leave_type')
#                 leave_type_id = str(row_dict.get('leave_type_id'))

#                 row_dict['field_one'] = field_map.get(leave_type, None)
#                 row_dict['leave_taken'] = leave_taken_map.get(leave_type_id, 0)

#                 result.append(row_dict)

#             return Response(result, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EmployeeLeavehistoryAPIView(APIView):
    def get(self, request):
        employee_id = request.GET.get("employee_id")
        if not employee_id:
            return Response(
                {"error": "employee_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as cursor:

                # 1️⃣ Fetch total approved leave days per leave_type_id
                cursor.execute("""
                    SELECT leave_type_id, COALESCE(SUM(no_of_days), 0) AS approved_days
                    FROM ci_leave_applications
                    WHERE employee_id = %s AND line_manager_status = 1
                    GROUP BY leave_type_id
                """, [employee_id])
                approved_days_map = {str(row[0]): float(row[1]) for row in cursor.fetchall()}

                # 2️⃣ Fetch leave balances from ci_leave_balance
                cursor.execute("""
                    SELECT leave_type_id, leave_type, balance_leave, year
                    FROM ci_leave_balance
                    WHERE employee_id = %s
                """, [employee_id])
                balance_rows = cursor.fetchall()
                balance_columns = [col[0] for col in cursor.description]

                # 3️⃣ Fetch days_per_year mapping
                cursor.execute("""
                    SELECT category_name, field_one
                    FROM ci_erp_constants
                    WHERE type = 'leave_type'
                """)
                field_map = {row[0]: row[1] for row in cursor.fetchall()}

            # 4️⃣ Build final response
            result = []
            for row in balance_rows:
                row_dict = dict(zip(balance_columns, row))
                leave_type = row_dict.get("leave_type")
                leave_type_id = str(row_dict.get("leave_type_id"))

                # Days per year
                raw_days = field_map.get(leave_type)
                days_per_year = (
                    int(raw_days) if raw_days not in (None, "", "0") else "N/A"
                )

                # Calculate dynamic balance (based on approved leave days)
                approved_days = approved_days_map.get(leave_type_id, 0)
                dynamic_balance = max(row_dict.get("balance_leave", 0) - approved_days, 0)

                result.append({
                    "leave_type": leave_type,
                    "days_per_year": days_per_year,
                    "approved_leave_days": approved_days,
                    "balance": dynamic_balance
                })

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#############################################################################################################

#Working API

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db import connection
# from datetime import datetime, timedelta

# class ApplyLeaveAPIView(APIView):
#     def post(self, request):
#         try:
#             data = request.data

#             employee_id = data.get('employee_id')
#             company_id = data.get('company_id')
#             leave_type_id = data.get('leave_type_id')
#             from_date = data.get('from_date')
#             to_date = data.get('to_date')
#             reason = data.get('reason')
#             remarks = data.get('remarks', '')
#             is_half_day = data.get('is_half_day', False)
#             leave_attachment = data.get('leave_attachment', None)

#             # Validate and parse input dates
#             if not from_date or not to_date:
#                 return Response({'error': 'Both from_date and to_date are required'}, status=400)
#             try:
#                 from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
#                 to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
#             except ValueError:
#                 return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

#             apply_date = datetime.today().date()
#             no_of_days = (to_dt - from_dt).days + 1
#             status_app = "1"
#             status_lc = "N"
#             line_manager_status = "1"

#             # Check for overlapping leaves
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM ci_leave_applications
#                     WHERE employee_id = %s
#                     AND (
#                         (from_date BETWEEN %s AND %s)
#                         OR (to_date BETWEEN %s AND %s)
#                         OR (%s BETWEEN from_date AND to_date)
#                         OR (%s BETWEEN from_date AND to_date)
#                     )
#                 """, [
#                     employee_id, from_dt, to_dt,
#                     from_dt, to_dt,
#                     from_dt, to_dt
#                 ])
#                 overlap_count = cursor.fetchone()[0]
#                 if overlap_count > 0:
#                     return Response({'error': 'Leave already applied for these dates.'}, status=400)

#             # Check leave balance
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT leave_type, balance_leave, carry_forward FROM ci_leave_balance
#                     WHERE employee_id = %s AND leave_type_id = %s LIMIT 1
#                 """, [employee_id, leave_type_id])
#                 result = cursor.fetchone()
#                 if not result:
#                     return Response({'error': 'Leave type not assigned to employee'}, status=400)

#                 leave_type, balance_leave, carry_forward = result
#                 leave_type_lower = leave_type.lower()

#                 # Business rule checks
#                 if 'casual' in leave_type_lower:
#                     if no_of_days > 2:
#                         return Response({'error': 'Only 2 casual leave days can be availed at once'}, status=400)

#                     cursor.execute("""
#                         SELECT clc.leave_type, cla.to_date FROM ci_leave_count clc
#                         JOIN ci_leave_applications cla ON cla.leave_id = clc.leave_id
#                         WHERE clc.employee_id = %s AND clc.leave_type LIKE '%%Medical%%'
#                     """, [employee_id])
#                     medical_leaves = cursor.fetchall()
#                     for leave_type_val, prev_to_date in medical_leaves:
#                         if prev_to_date:
#                             prev_to_date = prev_to_date.date() if isinstance(prev_to_date, datetime) else prev_to_date
#                             if from_dt and (from_dt - prev_to_date).days == 1:
#                                 return Response({'error': 'Casual leave cannot immediately follow a Medical Leave'}, status=400)

#                 if 'medical' in leave_type_lower:
#                     cursor.execute("""
#                         SELECT clc.leave_type, cla.from_date FROM ci_leave_count clc
#                         JOIN ci_leave_applications cla ON cla.leave_id = clc.leave_id
#                         WHERE clc.employee_id = %s AND clc.leave_type LIKE '%%Casual%%'
#                     """, [employee_id])
#                     casual_leaves = cursor.fetchall()
#                     for leave_type_val, next_from_date in casual_leaves:
#                         if next_from_date:
#                             next_from_date = next_from_date.date() if isinstance(next_from_date, datetime) else next_from_date
#                             if to_dt and (next_from_date - to_dt).days == 1:
#                                 return Response({'error': 'Medical leave cannot be followed by Casual Leave'}, status=400)

#                 if 'paid' in leave_type_lower:
#                     if (from_dt - apply_date).days < 8:
#                         return Response({'error': 'Paid leave must be applied at least 8 days in advance'}, status=400)
#                     if no_of_days > 6:
#                         return Response({'error': 'Max 6 paid leaves can be availed at once'}, status=400)

#                     cursor.execute("""
#                         SELECT COUNT(*) FROM ci_leave_applications
#                         WHERE employee_id = %s AND leave_type_id = %s AND YEAR(from_date) = YEAR(CURDATE())
#                     """, [employee_id, leave_type_id])
#                     applied_times = cursor.fetchone()[0]
#                     if applied_times >= 7:
#                         return Response({'error': 'Only 7 paid leave applications are allowed per year'}, status=400)

#                 # Sandwich rule
#                 sandwich_days = 0
#                 cursor.execute("SELECT start_date, end_date FROM ci_holidays")
#                 holidays = []
#                 for row in cursor.fetchall():
#                     if row[0] and row[1]:
#                         holiday_start = row[0].date() if isinstance(row[0], datetime) else row[0]
#                         holiday_end = row[1].date() if isinstance(row[1], datetime) else row[1]
#                         delta = (holiday_end - holiday_start).days
#                         for i in range(delta + 1):
#                             holidays.append(holiday_start + timedelta(days=i))

#                 for day in range(1, (to_dt - from_dt).days):
#                     temp_day = from_dt + timedelta(days=day)
#                     if temp_day.weekday() in [5, 6] or temp_day in holidays:
#                         sandwich_days += 1

#                 no_of_days += sandwich_days
#                 sandwich_note = f"{sandwich_days} sandwich day(s) added due to weekends or holidays." if sandwich_days else "No sandwich days applied."

#                 if balance_leave < no_of_days:
#                     return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)

#             # Insert leave application
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_applications (
#                         company_id, employee_id, leave_type_id, from_date, to_date,
#                         no_of_days, reason, remarks, status, line_manager_status,
#                         is_half_day, leave_attachment, created_at
#                     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
#                 """, [
#                     company_id, employee_id, leave_type_id, from_dt, to_dt,
#                     no_of_days, reason, remarks, status_app, line_manager_status,
#                     is_half_day, leave_attachment
#                 ])
#                 leave_id = cursor.lastrowid

#             # Insert into leave count
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_count (
#                         employee_id, leave_id, leave_type, leave_type_id,
#                         number_of_leave, status_lc
#                     ) VALUES (%s, %s, %s, %s, %s, %s)
#                 """, [
#                     employee_id, leave_id, leave_type, leave_type_id,
#                     no_of_days, status_lc
#                 ])

#             # Update leave balance
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE ci_leave_balance SET balance_leave = balance_leave - %s
#                     WHERE employee_id = %s AND leave_type_id = %s
#                 """, [no_of_days, employee_id, leave_type_id])

#             return Response({
#                 'message': 'Leave applied successfully',
#                 'leave_id': leave_id,
#                 'no_of_days': no_of_days,
#                 'leave_type': leave_type,
#                 'note': sandwich_note
#             }, status=201)

#         except Exception as e:
#             return Response({'error': str(e)}, status=500)

#########################################################################################################

#Working code Date05-08-2025

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db import connection
# from datetime import datetime, timedelta

# class ApplyLeaveAPIView(APIView):
#     def post(self, request):
#         try:
#             data = request.data

#             employee_id = data.get('employee_id')
#             company_id = data.get('company_id')
#             leave_type_id = data.get('leave_type_id')
#             from_date = data.get('from_date')
#             to_date = data.get('to_date')
#             reason = data.get('reason')
#             remarks = data.get('remarks', '')
#             is_half_day = data.get('is_half_day', False)
#             leave_attachment = data.get('leave_attachment', None)

#             # Validate and parse input dates
#             if not from_date:
#                 return Response({'error': 'from_date is required'}, status=400)
#             try:
#                 from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
#             except ValueError:
#                 return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

#             apply_date = datetime.today().date()
#             status_app = "1"
#             status_lc = "N"
#             line_manager_status = "1"

#             # Get leave type and balance
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT leave_type, balance_leave, carry_forward FROM ci_leave_balance
#                     WHERE employee_id = %s AND leave_type_id = %s LIMIT 1
#                 """, [employee_id, leave_type_id])
#                 result = cursor.fetchone()
#                 if not result:
#                     return Response({'error': 'Leave type not assigned to employee'}, status=400)

#                 leave_type, balance_leave, carry_forward = result
#                 leave_type_lower = leave_type.lower()

#             # Maternity leave logic
#             if 'maternity' in leave_type_lower:
#                 to_dt = from_dt + timedelta(days=181)
#                 no_of_days = 182
#                 sandwich_note = "Maternity Leave: 182 days auto-applied (including weekends and holidays)."
#                 if balance_leave < no_of_days:
#                     return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)
#                 skip_other_checks = True


#             elif 'paternity' in leave_type_lower:
#                 to_dt = from_dt + timedelta(days=2)
#                 no_of_days = 3
#                 sandwich_note = "Paternity Leave: 3 days auto-applied (including weekends and holidays)."
#                 if balance_leave < no_of_days:
#                     return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)
#                 skip_other_checks = True    

#             else:
#                 # Validate and parse to_date for other leave types
#                 if not to_date:
#                     return Response({'error': 'to_date is required'}, status=400)
#                 try:
#                     to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
#                 except ValueError:
#                     return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

#                 no_of_days = (to_dt - from_dt).days + 1
#                 skip_other_checks = False

#             # Check for overlapping leaves
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM ci_leave_applications
#                     WHERE employee_id = %s
#                     AND (
#                         (from_date BETWEEN %s AND %s)
#                         OR (to_date BETWEEN %s AND %s)
#                         OR (%s BETWEEN from_date AND to_date)
#                         OR (%s BETWEEN from_date AND to_date)
#                     )
#                 """, [
#                     employee_id, from_dt, to_dt,
#                     from_dt, to_dt,
#                     from_dt, to_dt
#                 ])
#                 overlap_count = cursor.fetchone()[0]
#                 if overlap_count > 0:
#                     return Response({'error': 'Leave already applied for these dates.'}, status=400)

#             if not skip_other_checks:
#                 # Business rule checks
#                 with connection.cursor() as cursor:
#                     if 'casual' in leave_type_lower:
#                         if no_of_days > 2:
#                             return Response({'error': 'Only 2 casual leave days can be availed at once'}, status=400)
#                         cursor.execute("""
#                             SELECT clc.leave_type, cla.to_date FROM ci_leave_count clc
#                             JOIN ci_leave_applications cla ON cla.leave_id = clc.leave_id
#                             WHERE clc.employee_id = %s AND clc.leave_type LIKE '%%Medical%%'
#                         """, [employee_id])
#                         medical_leaves = cursor.fetchall()
#                         for _, prev_to_date in medical_leaves:
#                             if prev_to_date:
#                                 prev_to_date = prev_to_date.date() if isinstance(prev_to_date, datetime) else prev_to_date
#                                 if from_dt and (from_dt - prev_to_date).days == 1:
#                                     return Response({'error': 'Casual leave cannot immediately follow a Medical Leave'}, status=400)

#                     if 'medical' in leave_type_lower:
#                         cursor.execute("""
#                             SELECT clc.leave_type, cla.from_date FROM ci_leave_count clc
#                             JOIN ci_leave_applications cla ON cla.leave_id = clc.leave_id
#                             WHERE clc.employee_id = %s AND clc.leave_type LIKE '%%Casual%%'
#                         """, [employee_id])
#                         casual_leaves = cursor.fetchall()
#                         for _, next_from_date in casual_leaves:
#                             if next_from_date:
#                                 next_from_date = next_from_date.date() if isinstance(next_from_date, datetime) else next_from_date
#                                 if to_dt and (next_from_date - to_dt).days == 1:
#                                     return Response({'error': 'Medical leave cannot be followed by Casual Leave'}, status=400)

#                     if 'paid' in leave_type_lower:
#                         if (from_dt - apply_date).days < 8:
#                             return Response({'error': 'Paid leave must be applied at least 8 days in advance'}, status=400)
#                         if no_of_days > 6:
#                             return Response({'error': 'Max 6 paid leaves can be availed at once'}, status=400)

#                         cursor.execute("""
#                             SELECT COUNT(*) FROM ci_leave_applications
#                             WHERE employee_id = %s AND leave_type_id = %s AND YEAR(from_date) = YEAR(CURDATE())
#                         """, [employee_id, leave_type_id])
#                         applied_times = cursor.fetchone()[0]
#                         if applied_times >= 7:
#                             return Response({'error': 'Only 7 paid leave applications are allowed per year'}, status=400)

#                 # Sandwich rule
#                 sandwich_days = 0
#                 holidays = []
#                 with connection.cursor() as cursor:
#                     cursor.execute("SELECT start_date, end_date FROM ci_holidays")
#                     for row in cursor.fetchall():
#                         if row[0] and row[1]:
#                             holiday_start = row[0].date() if isinstance(row[0], datetime) else row[0]
#                             holiday_end = row[1].date() if isinstance(row[1], datetime) else row[1]
#                             delta = (holiday_end - holiday_start).days
#                             for i in range(delta + 1):
#                                 holidays.append(holiday_start + timedelta(days=i))

#                 for day in range(1, (to_dt - from_dt).days):
#                     temp_day = from_dt + timedelta(days=day)
#                     if temp_day.weekday() in [5, 6] or temp_day in holidays:
#                         sandwich_days += 1

#                 no_of_days += sandwich_days
#                 sandwich_note = f"{sandwich_days} sandwich day(s) added due to weekends or holidays." if sandwich_days else "No sandwich days applied."

#                 if balance_leave < no_of_days:
#                     return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)
#             else:
#                 # Maternity case: no sandwich counted, note already set
#                 pass

#             # Insert leave application
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_applications (
#                         company_id, employee_id, leave_type_id, from_date, to_date,
#                         no_of_days, reason, remarks, status, line_manager_status,
#                         is_half_day, leave_attachment, created_at
#                     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
#                 """, [
#                     company_id, employee_id, leave_type_id, from_dt, to_dt,
#                     no_of_days, reason, remarks, status_app, line_manager_status,
#                     is_half_day, leave_attachment
#                 ])
#                 leave_id = cursor.lastrowid

#             # Insert into leave count
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_count (
#                         employee_id, leave_id, leave_type, leave_type_id,
#                         number_of_leave, status_lc
#                     ) VALUES (%s, %s, %s, %s, %s, %s)
#                 """, [
#                     employee_id, leave_id, leave_type, leave_type_id,
#                     no_of_days, status_lc
#                 ])

#             # Update leave balance
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE ci_leave_balance SET balance_leave = balance_leave - %s
#                     WHERE employee_id = %s AND leave_type_id = %s
#                 """, [no_of_days, employee_id, leave_type_id])

#             return Response({
#                 'message': 'Leave applied successfully',
#                 'leave_id': leave_id,
#                 'no_of_days': no_of_days,
#                 'leave_type': leave_type,
#                 'note': sandwich_note if not skip_other_checks else sandwich_note
#             }, status=201)

#         except Exception as e:
#             return Response({'error': str(e)}, status=500)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from datetime import datetime, timedelta

class ApplyLeaveAPIView(APIView):
    status_mapping = {
            0: "Pending",
            1: "Approved",
            2: "Rejected"
        }


    def get(self, request):
        status_mapping = {
            0: "Pending",
            1: "Approved",
            2: "Rejected"
        }

        employee_id = request.GET.get("employee_id")
        if not employee_id:
            return Response({"error": "employee_id is required"}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    la.leave_id,
                    la.employee_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    c.category_name AS leave_type,
                    la.from_date,
                    la.to_date,
                    la.no_of_days,
                    la.reason,
                    la.line_manager_status
                FROM ci_leave_applications la
                LEFT JOIN ci_erp_users_details ud ON la.employee_id = ud.employee_id
                LEFT JOIN ci_erp_users u ON ud.user_id = u.id
                LEFT JOIN ci_erp_constants c ON la.leave_type_id = c.constants_id
                WHERE la.employee_id = %s
                ORDER BY la.leave_id DESC
            """, [employee_id])

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        result = []
        for row in rows:
            record = dict(zip(columns, row))
            #  Safe assignment with default Pending (0)
            status_value = record.get("line_manager_status", 0) 
            if status_value is None:
                status_value = 0

            record["line_manager_status"] = self.status_mapping.get(status_value, "Pending")
            result.append(record)

        return Response(result)


    def post(self, request):
        try:
            data = request.data

            employee_id = data.get('employee_id')
            user_id = data.get('user_id')

            company_id = data.get('company_id')
            leave_type_id = data.get('leave_type_id')
            from_date = data.get('from_date')
            to_date = data.get('to_date')
            reason = data.get('reason')
            remarks = data.get('remarks', '')
            is_half_day = data.get('is_half_day', False)
            leave_attachment = data.get('leave_attachment', None)

            # Validate and parse input dates
            if not from_date:
                return Response({'error': 'from_date is required'}, status=400)
            try:
                from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

            apply_date = datetime.today().date()
            status_app = "1"
            status_lc = "N"
            line_manager_status = "0"

            # Get leave type and balance
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT leave_type, balance_leave, carry_forward FROM ci_leave_balance
                    WHERE employee_id = %s AND leave_type_id = %s LIMIT 1
                """, [employee_id, leave_type_id])
                result = cursor.fetchone()
                if not result:
                    return Response({'error': 'Leave type not assigned to employee'}, status=400)

                leave_type, balance_leave, carry_forward = result
                leave_type_lower = leave_type.lower()

            # Handle special leave types
            if 'maternity' in leave_type_lower:
                to_dt = from_dt + timedelta(days=181)
                no_of_days = 182
                sandwich_note = "Maternity Leave: 182 days auto-applied (including weekends and holidays)."
                if balance_leave < no_of_days:
                    return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)
                skip_other_checks = True

            elif 'paternity' in leave_type_lower:
                to_dt = from_dt + timedelta(days=2)
                no_of_days = 3
                sandwich_note = "Paternity Leave: 3 days auto-applied (including weekends and holidays)."
                if balance_leave < no_of_days:
                    return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)
                skip_other_checks = True

            else:
                # Validate and parse to_date
                if not to_date:
                    return Response({'error': 'to_date is required'}, status=400)
                try:
                    to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
                except ValueError:
                    return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

                if from_dt > to_dt:
                    return Response({'error': 'from_date cannot be after to_date'}, status=400)

                # Calculate base leave days
                # total_days = (to_dt - from_dt).days + 1
                # if is_half_day:
                #     if from_dt == to_dt:
                #         no_of_days = 0.5
                #     else:
                #         no_of_days = total_days - 1 + 0.5
                # else:
                #     no_of_days = total_days

                total_days = (to_dt - from_dt).days + 1  # Always include both dates

                # Case 1: Half-day leave for the same day
                if is_half_day and from_dt == to_dt:
                    no_of_days = 0.5

                # Case 2: Full-day leave for the same day
                elif not is_half_day and from_dt == to_dt:
                    no_of_days = 1.0

                # Case 3: Leave spanning multiple days (half-day ignored)
                else:
                    no_of_days = total_days


                skip_other_checks = False

            # Check for overlapping leaves
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM ci_leave_applications
                    WHERE employee_id = %s
                    AND (
                        (from_date BETWEEN %s AND %s)
                        OR (to_date BETWEEN %s AND %s)
                        OR (%s BETWEEN from_date AND to_date)
                        OR (%s BETWEEN from_date AND to_date)
                    )
                """, [
                    employee_id, from_dt, to_dt,
                    from_dt, to_dt,
                    from_dt, to_dt
                ])
                overlap_count = cursor.fetchone()[0]
                if overlap_count > 0:
                    return Response({'error': 'Leave already applied for these dates.'}, status=400)

            if not skip_other_checks:
                # Business rule checks
                with connection.cursor() as cursor:
                    if 'casual' in leave_type_lower:
                        if no_of_days > 2:
                            return Response({'error': 'Only 2 casual leave days can be availed at once'}, status=400)
                        cursor.execute("""
                            SELECT clc.leave_type, cla.to_date FROM ci_leave_count clc
                            JOIN ci_leave_applications cla ON cla.leave_id = clc.leave_id
                            WHERE clc.employee_id = %s AND clc.leave_type LIKE '%%Medical%%'
                        """, [employee_id])
                        medical_leaves = cursor.fetchall()
                        for _, prev_to_date in medical_leaves:
                            if prev_to_date:
                                prev_to_date = prev_to_date.date() if isinstance(prev_to_date, datetime) else prev_to_date
                                if from_dt and (from_dt - prev_to_date).days == 1:
                                    return Response({'error': 'Casual leave cannot immediately follow a Medical Leave'}, status=400)

                    if 'medical' in leave_type_lower:
                        cursor.execute("""
                            SELECT clc.leave_type, cla.from_date FROM ci_leave_count clc
                            JOIN ci_leave_applications cla ON cla.leave_id = clc.leave_id
                            WHERE clc.employee_id = %s AND clc.leave_type LIKE '%%Casual%%'
                        """, [employee_id])
                        casual_leaves = cursor.fetchall()
                        for _, next_from_date in casual_leaves:
                            if next_from_date:
                                next_from_date = next_from_date.date() if isinstance(next_from_date, datetime) else next_from_date
                                if to_dt and (next_from_date - to_dt).days == 1:
                                    return Response({'error': 'Medical leave cannot be followed by Casual Leave'}, status=400)

                    if 'paid' in leave_type_lower:
                        if (from_dt - apply_date).days < 8:
                            return Response({'error': 'Paid leave must be applied at least 8 days in advance'}, status=400)
                        if no_of_days > 6:
                            return Response({'error': 'Max 6 paid leaves can be availed at once'}, status=400)

                        cursor.execute("""
                            SELECT COUNT(*) FROM ci_leave_applications
                            WHERE employee_id = %s AND leave_type_id = %s AND YEAR(from_date) = YEAR(CURDATE())
                        """, [employee_id, leave_type_id])
                        applied_times = cursor.fetchone()[0]
                        if applied_times >= 7:
                            return Response({'error': 'Only 7 paid leave applications are allowed per year'}, status=400)

                # Sandwich rule
                sandwich_days = 0
                holidays = []
                with connection.cursor() as cursor:
                    cursor.execute("SELECT start_date, end_date FROM ci_holidays")
                    for row in cursor.fetchall():
                        if row[0] and row[1]:
                            holiday_start = row[0].date() if isinstance(row[0], datetime) else row[0]
                            holiday_end = row[1].date() if isinstance(row[1], datetime) else row[1]
                            delta = (holiday_end - holiday_start).days
                            for i in range(delta + 1):
                                holidays.append(holiday_start + timedelta(days=i))

                for day in range(1, (to_dt - from_dt).days):
                    temp_day = from_dt + timedelta(days=day)
                    if temp_day.weekday() in [5, 6] or temp_day in holidays:
                        sandwich_days += 1

                no_of_days += sandwich_days
                sandwich_note = f"{sandwich_days} sandwich day(s) added due to weekends or holidays." if sandwich_days else "No sandwich days applied."

            # Final balance check
            if balance_leave < no_of_days:
                return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)

            # Insert leave application
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_leave_applications (
                        company_id, employee_id, leave_type_id, from_date, to_date,
                        no_of_days, reason, remarks, status, line_manager_status,
                        is_half_day, leave_attachment, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, [
                    company_id, employee_id, leave_type_id, from_dt, to_dt,
                    no_of_days, reason, remarks, status_app, line_manager_status,
                    is_half_day, leave_attachment
                ])
                leave_id = cursor.lastrowid

            # Insert into leave count
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_leave_count (
                        employee_id, leave_id, leave_type, leave_type_id,
                        number_of_leave, status_lc
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    employee_id, leave_id, leave_type, leave_type_id,
                    no_of_days, status_lc
                ])

            # Update leave balance
            # with connection.cursor() as cursor:
            #     cursor.execute("""
            #         UPDATE ci_leave_balance SET balance_leave = balance_leave - %s
            #         WHERE employee_id = %s AND leave_type_id = %s
            #     """, [no_of_days, employee_id, leave_type_id])

            return Response({
                'message': "Leave applied successfully. Waiting for Line Manager approval.",
               
                'leave_id': leave_id,
                'no_of_days': no_of_days,
                'leave_type': leave_type,
                'note': sandwich_note if not skip_other_checks else sandwich_note
            }, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
        


    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class LineManagerApprovalAPIView(APIView):
    status_mapping = {
        0: "Pending",
        1: "Approved",
        2: "Rejected"
    }

    status_text_mapping = {
        "pending": 0,
        "approved": 1,
        "rejected": 2
    }

    def get(self, request):
        """
        Fetch all leave requests for employees under the logged-in line manager.
        """
        line_manager_id = request.user.id  #  logged-in manager

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    la.leave_id,
                    la.employee_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    c.category_name AS leave_type,
                    la.from_date,
                    la.to_date,
                    la.no_of_days,
                    la.reason,
                    la.line_manager_status
                FROM ci_leave_applications la
                LEFT JOIN ci_erp_users_details ud ON la.employee_id = ud.employee_id
                LEFT JOIN ci_erp_users u ON ud.user_id = u.id
                LEFT JOIN ci_erp_constants c ON la.leave_type_id = c.constants_id
                WHERE ud.manager = %s   --  manager column holds user_id of manager
                ORDER BY la.leave_id DESC
            """, [line_manager_id])

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        result = []
        for row in rows:
            record = dict(zip(columns, row))
            record["line_manager_status"] = self.status_mapping.get(record["line_manager_status"], "Unknown")
            result.append(record)

        return Response(result)


    def patch(self, request, leave_id):
        """
        Update line_manager_status (Approve/Reject/Pending) for a leave request.
        Leave ID is passed in the URL.
        Manager can only update if request is still Pending (0).
        """
        line_manager_id = request.user.id
        new_status_text = request.data.get("line_manager_status")

        if not new_status_text:
            return Response({"error": "line_manager_status is required"}, status=400)

         # Normalize input (case-insensitive)
        new_status_text = str(new_status_text).lower().strip().strip("'").strip('"')

        if new_status_text not in self.status_text_mapping:
            return Response({
                "error": "Invalid status. Use 'approved', 'rejected', or 'pending'"
            }, status=400)

        new_status = self.status_text_mapping[new_status_text]

        with connection.cursor() as cursor:
            #  Check if leave belongs to an employee under this manager and is still Pending (0)
            cursor.execute("""
                SELECT la.line_manager_status
                FROM ci_leave_applications la
                LEFT JOIN ci_erp_users_details ud ON la.employee_id = ud.employee_id
                WHERE la.leave_id = %s AND ud.manager = %s
            """, [leave_id, line_manager_id])
            leave = cursor.fetchone()

            if not leave:
                return Response({"error": "Leave request not found or not under this manager"}, status=403)

            current_status = leave[0]
            if current_status != 0:  # 0 = Pending
                return Response({"error": "This leave request has already been processed"}, status=400)

            # Update status
            cursor.execute("""
                UPDATE ci_leave_applications
                SET line_manager_status = %s
                WHERE leave_id = %s
            """, [new_status, leave_id])

        return Response({
            "message": f"Leave request {leave_id} updated successfully",
            "new_status": new_status_text
        }, status=200)


    # def patch(self, request, leave_id):
        


    #     """
    #     Update line_manager_status (Approve/Reject/Pending) for a leave request.
    #     Leave ID is passed in the URL.
    #     Manager can only update if request is still Pending.
    #     """
    #     line_manager_id = request.user.id
    #     new_status_text = request.data.get("line_manager_status")

    #     if not new_status_text:
    #         return Response({"error": "line_manager_status is required"}, status=400)

    #     new_status_text = new_status_text.lower()
    #     if new_status_text not in self.status_text_mapping:
    #         return Response({
    #             "error": "Invalid status. Use 'approved', 'rejected', or 'pending'"
    #         }, status=400)

    #     new_status = self.status_text_mapping[new_status_text]
        
    #     with connection.cursor() as cursor:
    #         #  Check if leave belongs to an employee under this manager and is still Pending
    #         cursor.execute("""
    #             SELECT la.line_manager_status
    #             FROM ci_leave_applications la
    #             LEFT JOIN ci_erp_users_details ud ON la.employee_id = ud.employee_id
    #             WHERE la.leave_id = %s AND ud.manager = %s
    #         """, [leave_id, line_manager_id])
    #         leave = cursor.fetchone()

    #         if not leave:
    #             return Response({"error": "Leave request not found or not under this manager"}, status=403)

    #         current_status = leave[0]
    #         if current_status != 0:  # 0 = Pending
    #             return Response({"error": "This leave request has already been processed"}, status=400)

    #         # Update status
    #         cursor.execute("""
    #             UPDATE ci_leave_applications
    #             SET line_manager_status = %s
    #             WHERE leave_id = %s
    #         """, [new_status, leave_id])

    #     return Response({
    #         "message": f"Leave request {leave_id} updated successfully",
    #         "new_status": new_status_text
    #     }, status=200)








# class ApplyLeaveAPIView(APIView):
#     def post(self, request):
#         try:
#             data = request.data

#             employee_id = data.get('employee_id')
#             user_id = data.get('user_id')

#             company_id = data.get('company_id')
#             leave_type_id = data.get('leave_type_id')
#             from_date = data.get('from_date')
#             to_date = data.get('to_date')
#             reason = data.get('reason')
#             remarks = data.get('remarks', '')
#             is_half_day = data.get('is_half_day', False)
#             leave_attachment = data.get('leave_attachment', None)

#             # Validate and parse input dates
#             if not from_date:
#                 return Response({'error': 'from_date is required'}, status=400)
#             try:
#                 from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
#             except ValueError:
#                 return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

#             apply_date = datetime.today().date()
#             # status_app = "1"
#             # status_lc = "N"
#             # line_manager_status = "1"

#             line_manager_status = 2  # Pending until Line Manager updates

#             status_mapping = {
#                 0: "Rejected",
#                 1: "Approved",
#                 2: "Pending"
#             }

#             # Get leave type and balance
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT leave_type, balance_leave, carry_forward FROM ci_leave_balance
#                     WHERE employee_id = %s AND leave_type_id = %s LIMIT 1
#                 """, [employee_id, leave_type_id])
#                 result = cursor.fetchone()
#                 if not result:
#                     return Response({'error': 'Leave type not assigned to employee'}, status=400)

#                 leave_type, balance_leave, carry_forward = result
#                 leave_type_lower = leave_type.lower()

#             # Handle special leave types
#             if 'maternity' in leave_type_lower:
#                 to_dt = from_dt + timedelta(days=181)
#                 no_of_days = 182
#                 sandwich_note = "Maternity Leave: 182 days auto-applied (including weekends and holidays)."
#                 if balance_leave < no_of_days:
#                     return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)
#                 skip_other_checks = True

#             elif 'paternity' in leave_type_lower:
#                 to_dt = from_dt + timedelta(days=2)
#                 no_of_days = 3
#                 sandwich_note = "Paternity Leave: 3 days auto-applied (including weekends and holidays)."
#                 if balance_leave < no_of_days:
#                     return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)
#                 skip_other_checks = True

#             else:
#                 # Validate and parse to_date
#                 if not to_date:
#                     return Response({'error': 'to_date is required'}, status=400)
#                 try:
#                     to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
#                 except ValueError:
#                     return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

#                 if from_dt > to_dt:
#                     return Response({'error': 'from_date cannot be after to_date'}, status=400)

#                 # Calculate base leave days
#                 # total_days = (to_dt - from_dt).days + 1
#                 # if is_half_day:
#                 #     if from_dt == to_dt:
#                 #         no_of_days = 0.5
#                 #     else:
#                 #         no_of_days = total_days - 1 + 0.5
#                 # else:
#                 #     no_of_days = total_days

#                 total_days = (to_dt - from_dt).days + 1  # Always include both dates

#                 # Case 1: Half-day leave for the same day
#                 if is_half_day and from_dt == to_dt:
#                     no_of_days = 0.5

#                 # Case 2: Full-day leave for the same day
#                 elif not is_half_day and from_dt == to_dt:
#                     no_of_days = 1.0

#                 # Case 3: Leave spanning multiple days (half-day ignored)
#                 else:
#                     no_of_days = total_days


#                 skip_other_checks = False

#             # Check for overlapping leaves
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM ci_leave_applications
#                     WHERE employee_id = %s
#                     AND (
#                         (from_date BETWEEN %s AND %s)
#                         OR (to_date BETWEEN %s AND %s)
#                         OR (%s BETWEEN from_date AND to_date)
#                         OR (%s BETWEEN from_date AND to_date)
#                     )
#                 """, [
#                     employee_id, from_dt, to_dt,
#                     from_dt, to_dt,
#                     from_dt, to_dt
#                 ])
#                 overlap_count = cursor.fetchone()[0]
#                 if overlap_count > 0:
#                     return Response({'error': 'Leave already applied for these dates.'}, status=400)

#             if not skip_other_checks:
#                 # Business rule checks
#                 with connection.cursor() as cursor:
#                     if 'casual' in leave_type_lower:
#                         if no_of_days > 2:
#                             return Response({'error': 'Only 2 casual leave days can be availed at once'}, status=400)
#                         cursor.execute("""
#                             SELECT clc.leave_type, cla.to_date FROM ci_leave_count clc
#                             JOIN ci_leave_applications cla ON cla.leave_id = clc.leave_id
#                             WHERE clc.employee_id = %s AND clc.leave_type LIKE '%%Medical%%'
#                         """, [employee_id])
#                         medical_leaves = cursor.fetchall()
#                         for _, prev_to_date in medical_leaves:
#                             if prev_to_date:
#                                 prev_to_date = prev_to_date.date() if isinstance(prev_to_date, datetime) else prev_to_date
#                                 if from_dt and (from_dt - prev_to_date).days == 1:
#                                     return Response({'error': 'Casual leave cannot immediately follow a Medical Leave'}, status=400)

#                     if 'medical' in leave_type_lower:
#                         cursor.execute("""
#                             SELECT clc.leave_type, cla.from_date FROM ci_leave_count clc
#                             JOIN ci_leave_applications cla ON cla.leave_id = clc.leave_id
#                             WHERE clc.employee_id = %s AND clc.leave_type LIKE '%%Casual%%'
#                         """, [employee_id])
#                         casual_leaves = cursor.fetchall()
#                         for _, next_from_date in casual_leaves:
#                             if next_from_date:
#                                 next_from_date = next_from_date.date() if isinstance(next_from_date, datetime) else next_from_date
#                                 if to_dt and (next_from_date - to_dt).days == 1:
#                                     return Response({'error': 'Medical leave cannot be followed by Casual Leave'}, status=400)

#                     if 'paid' in leave_type_lower:
#                         if (from_dt - apply_date).days < 8:
#                             return Response({'error': 'Paid leave must be applied at least 8 days in advance'}, status=400)
#                         if no_of_days > 6:
#                             return Response({'error': 'Max 6 paid leaves can be availed at once'}, status=400)

#                         cursor.execute("""
#                             SELECT COUNT(*) FROM ci_leave_applications
#                             WHERE employee_id = %s AND leave_type_id = %s AND YEAR(from_date) = YEAR(CURDATE())
#                         """, [employee_id, leave_type_id])
#                         applied_times = cursor.fetchone()[0]
#                         if applied_times >= 7:
#                             return Response({'error': 'Only 7 paid leave applications are allowed per year'}, status=400)

#                 # Sandwich rule
#                 sandwich_days = 0
#                 holidays = []
#                 with connection.cursor() as cursor:
#                     cursor.execute("SELECT start_date, end_date FROM ci_holidays")
#                     for row in cursor.fetchall():
#                         if row[0] and row[1]:
#                             holiday_start = row[0].date() if isinstance(row[0], datetime) else row[0]
#                             holiday_end = row[1].date() if isinstance(row[1], datetime) else row[1]
#                             delta = (holiday_end - holiday_start).days
#                             for i in range(delta + 1):
#                                 holidays.append(holiday_start + timedelta(days=i))

#                 for day in range(1, (to_dt - from_dt).days):
#                     temp_day = from_dt + timedelta(days=day)
#                     if temp_day.weekday() in [5, 6] or temp_day in holidays:
#                         sandwich_days += 1

#                 no_of_days += sandwich_days
#                 sandwich_note = f"{sandwich_days} sandwich day(s) added due to weekends or holidays." if sandwich_days else "No sandwich days applied."

#             # Final balance check
#             if balance_leave < no_of_days:
#                 return Response({'error': f'Insufficient balance: Only {balance_leave} {leave_type} available'}, status=400)

#             # Insert leave application
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_applications (
#                         company_id, employee_id, leave_type_id, from_date, to_date,
#                         no_of_days, reason, remarks, line_manager_status,
#                         is_half_day, leave_attachment, created_at
#                     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
#                 """, [
#                     company_id, employee_id, leave_type_id, from_dt, to_dt,
#                     no_of_days, reason, remarks, line_manager_status,
#                     is_half_day, leave_attachment
#                 ])
#                 leave_id = cursor.lastrowid

#             # Insert into leave count
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_count (
#                         employee_id, leave_id, leave_type, leave_type_id,
#                         number_of_leave, line_manager_status
#                     ) VALUES (%s, %s, %s, %s, %s, %s)
#                 """, [
#                     employee_id, leave_id, leave_type, leave_type_id,
#                     no_of_days, line_manager_status
#                 ])

#             # Update leave balance
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     UPDATE ci_leave_balance SET balance_leave = balance_leave - %s
#                     WHERE employee_id = %s AND leave_type_id = %s
#                 """, [no_of_days, employee_id, leave_type_id])

#             return Response({
#                 'message': 'Leave applied successfully',
#                 'leave_id': leave_id,
#                 'no_of_days': no_of_days,
#                 'leave_type': leave_type,
#                 'line_manager_status': status_mapping[line_manager_status],     # Always in words
#                 'note': sandwich_note if not skip_other_checks else sandwich_note
#             }, status=201)

#         except Exception as e:
#             return Response({'error': str(e)}, status=500)



    # def get(self, request):

    #     status_mapping = {
    #                     0: "Rejected",
    #                     1: "Approved",
    #                     2: "Pending"
    #                 }
        
    #     """
    #     Fetch leave applications with leave_type name and readable line_manager_status.
    #     """
    #     employee_id = request.GET.get("employee_id")
    #     if not employee_id:
    #         return Response({"error": "employee_id is required"}, status=400)

    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT 
    #                 la.leave_id,
    #                 la.employee_id,
    #                 CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    #                 c.category_name AS leave_type,
    #                 la.from_date,
    #                 la.to_date,
    #                 la.reason,
    #                 la.line_manager_status
    #             FROM ci_leave_applications la
    #             LEFT JOIN ci_erp_users u ON la.employee_id = u.id
    #             LEFT JOIN ci_erp_constants c ON la.leave_type_id = c.constants_id
    #             WHERE la.employee_id = %s
    #             ORDER BY la.leave_id DESC
    #         """, [employee_id])

    #         columns = [col[0] for col in cursor.description]
    #         rows = cursor.fetchall()

    #     # Convert to readable format
    #     result = []
    #     for row in rows:
    #         record = dict(zip(columns, row))
    #         record["line_manager_status"] = self.status_mapping.get(record["line_manager_status"], "Unknown")
    #         result.append(record)

    #     return Response(result)






###################################################################################################################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class LeaveListByEmployeeAPIView(APIView):
    def get(self, request):
        employee_id = request.query_params.get('employee_id')

        if not employee_id:
            return Response({'error': 'employee_id is required as query param'}, status=400)

        try:
            with connection.cursor() as cursor:
                # Get user_id from employee_id
                cursor.execute("""
                    SELECT user_id FROM ci_erp_users_details WHERE employee_id = %s LIMIT 1
                """, [employee_id])
                user_row = cursor.fetchone()

                if not user_row:
                    return Response({'error': 'No user found for the given employee_id'}, status=404)

                user_id = user_row[0]

                # Get user details
                cursor.execute("""
                    SELECT first_name, middle_name, last_name, email FROM ci_erp_users
                    WHERE id = %s LIMIT 1
                """, [user_id])
                user_details = cursor.fetchone()

                if not user_details:
                    return Response({'error': 'User details not found'}, status=404)

                first_name, middle_name, last_name, email = user_details
                full_name = " ".join(filter(None, [first_name, middle_name, last_name]))

                # Get all leave applications
                cursor.execute("""
                    SELECT leave_type_id, from_date, to_date, no_of_days, status
                    FROM ci_leave_applications
                    WHERE employee_id = %s
                    ORDER BY from_date DESC
                """, [employee_id])
                leaves = cursor.fetchall()

                if not leaves:
                    return Response({'message': 'No leave applications found.'}, status=200)

                results = []
                for row in leaves:
                    leave_type_id, from_date, to_date, no_of_days, status_val = row

                    # Get leave type from ci_leave_count
                    cursor.execute("""
                        SELECT leave_type FROM ci_leave_count
                        WHERE employee_id = %s AND leave_type_id = %s
                        ORDER BY leave_count_id DESC LIMIT 1
                    """, [employee_id, leave_type_id])
                    lt = cursor.fetchone()
                    leave_type = lt[0] if lt else 'Unknown'

                    # Format date safely
                    from_date_str = from_date if isinstance(from_date, str) else from_date.strftime("%Y-%m-%d")
                    to_date_str = to_date if isinstance(to_date, str) else to_date.strftime("%Y-%m-%d")

                    # Optional: convert status code to text
                    status_map = {
                        "0": "Pending",
                        "1": "Approved",
                        "2": "Rejected",
                        "3": "Cancelled"
                    }
                    status_text = status_map.get(str(status_val), str(status_val))

                    results.append({
                        'employee_name': full_name,
                        'email': email,
                        'leave_type': leave_type,
                        'from_date': from_date_str,
                        'to_date': to_date_str,
                        'days_applied': no_of_days,
                        'status': status_text
                    })

                return Response({'leave_applications': results}, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=500)


#########





class SandwichRuleCheckAPIView(APIView):
    """
    Utility API to check if sandwich rule applies (1 = applied, 0 = not applied)
    """

    def post(self, request):
        data = request.data
        employee_id = data.get("employee_id")
        from_date = data.get("from_date")
        to_date = data.get("to_date")

        if not employee_id:
            return Response({"error": "employee_id is required"}, status=400)

        if not from_date or not to_date:
            return Response({"error": "from_date and to_date are required"}, status=400)

        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        if from_dt > to_dt:
            return Response({"error": "from_date cannot be after to_date"}, status=400)

        # Fetch holidays from DB
        holidays = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT start_date, end_date FROM ci_holidays")
            for row in cursor.fetchall():
                if row[0] and row[1]:
                    holiday_start = row[0].date() if isinstance(row[0], datetime) else row[0]
                    holiday_end = row[1].date() if isinstance(row[1], datetime) else row[1]
                    delta = (holiday_end - holiday_start).days
                    for i in range(delta + 1):
                        holidays.append(holiday_start + timedelta(days=i))

        # Check if any sandwich days exist
        sandwich_applied = 0
        for day in range(1, (to_dt - from_dt).days):  # exclude start & end
            temp_day = from_dt + timedelta(days=day)
            if temp_day.weekday() in [5, 6] or temp_day in holidays:
                sandwich_applied = 1
                break  # stop once we know sandwich applies

        response = {
            "from_date": str(from_dt),
            "to_date": str(to_dt),
            "sandwich_applied": sandwich_applied
        }

        return Response(response, status=200)
 
from datetime import date, datetime, time, timedelta

# from django.shortcuts import get_object_or_404
from django.db import connection, transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated

# from app.models import *
# from .serializers import *
from hrms_app.permissions import IsAdmin, IsEmployee, IsReportingManager

# from drf_yasg.utils import swagger_auto_schema
# from django.db.models import Count
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated

import os
from urllib.parse import quote
from django.conf import settings
from django.core.files.storage import FileSystemStorage

import logging
logger = logging.getLogger(__name__)

import pytz
from django.utils import timezone


class EmployeeOnlyView(APIView):
    permission_classes = [AllowAny]


class EmployeeAttendance(APIView):

    # def post(self, request):

    #     emp_id = request.data.get("emp_id")
    #     punch_time_str = request.data.get("punch_time")  # "YYYY-MM-DD HH:MM:SS"
    #     punch_type = request.data.get("punch_type")  # "IN" or "OUT"
    #     location = request.data.get("location", "")

    #     punch_time_strr = datetime.strptime(punch_time_str, "%Y-%m-%d %H:%M:%S")
    #     attendance_date = punch_time_strr.date()
    #     punch_time = punch_time_strr.time()

    #     try:
    #         # Get department of employee
    #         with connection.cursor() as cursor:
    #             cursor.execute(
    #                 "SELECT user_id, department_id, designation_id FROM ci_erp_users_details WHERE employee_id = %s",
    #                 [emp_id],
    #             )
    #             row = cursor.fetchone()
    #             user_id = row[0] if row and row[0] is not None else 0
    #             department = row[1] if row and row[1] is not None else 0
    #             designation_id = row[2] if row and row[2] is not None else 0

    #         with connection.cursor() as cursor:
    #             cursor.execute(
    #                 "SELECT employee_hub_id, employee_hub_name FROM ci_employee_hub WHERE designation_id = %s",
    #                 [designation_id],
    #             )
    #             # row = cursor.fetchone()
    #             # employee_hub_id = row[0]
    #             # employee_hub_name = row[1]

    #             hub_row = cursor.fetchone()

    #         if hub_row:
    #             # If a hub is found, use its values
    #             employee_hub_id, employee_hub_name = hub_row
    #         else:
    #             # If no hub is found, assign default values instead of returning an error
    #             employee_hub_id = 0
    #             employee_hub_name = ""

    #         if punch_type == "IN":

    #             late_mark = "N"
    #             is_half_day = "N"
    #             half_day_reason = None

    #             if employee_hub_name.lower() == "office":
    #                 in_time = datetime.strptime("10:00", "%H:%M").time()
    #             else:
    #                 in_time = datetime.strptime("09:30", "%H:%M").time()

    #             late_mark = "Y" if punch_time > in_time else "N"

    #             # Count previous late marks in this month
    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     """
    #                     SELECT COUNT(*) FROM ci_biomatric_data
    #                     WHERE emp_id = %s AND MONTH(attendance_date) = MONTH(CURDATE()) AND late_mark = 'Y'
    #                 """,
    #                     [emp_id],
    #                 )
    #                 late_mark_count = cursor.fetchone()[0]

    #             # 4. Half Day if this is 2nd late mark
    #             if late_mark == "Y" and late_mark_count == 2:
    #                 is_half_day = "Y"
    #                 half_day_reason = "Exceeded Late Mark Limit"
    #                 late_mark_count = 0  # reset count after marking half day
    #             elif late_mark == "Y":
    #                 late_mark_count += 1  # increment for tracking

    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     """
    #                     INSERT INTO ci_biomatric_data 
    #                     (emp_id, userid, employee_hub_id, login_date, clock_in, clock_in_location, state_in_out, late_mark, is_half_day, half_day_reason, late_mark_count, attendance_date, attendance_status, status, from_od, reason)
    #                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #                 """,
    #                     [
    #                         emp_id,
    #                         user_id,
    #                         employee_hub_id,
    #                         attendance_date,
    #                         punch_time,
    #                         location,
    #                         "in",
    #                         late_mark,
    #                         is_half_day,
    #                         half_day_reason,
    #                         late_mark_count,
    #                         attendance_date,
    #                         "Present",
    #                         "P",
    #                         "N",
    #                         "Check IN",
    #                     ],
    #                 )

    #             return Response({"status": "Clock-In recorded"})

    #         # elif punch_type == "OUT":
    #         #     # Fetch today's IN entry
    #         #     with connection.cursor() as cursor:
    #         #         cursor.execute(
    #         #             """
    #         #             SELECT ci_biomatric_id, clock_in 
    #         #             FROM ci_biomatric_data 
    #         #             WHERE emp_id = %s AND attendance_date = %s AND status = 'P'
    #         #             ORDER BY ci_biomatric_id DESC LIMIT 1
    #         #         """,
    #         #             [emp_id, attendance_date],
    #         #         )
    #         #         row = cursor.fetchone()

    #         #     if not row:
    #         #         return Response({"error": "No clock-in found"}, status=404)

    #         #     biomatric_id, clock_in_str = row  # clock_in_str = "10:01:00"

    #         #     # clock_in_time = datetime.combine(attendance_date, datetime.strptime(clock_in_str, "%H:%M:%S").time())
    #         #     # clock_out_time = datetime.combine(attendance_date, punch_time)

    #         #     # total_work = clock_out_time - clock_in_time

    #         #     clock_in = datetime.combine(attendance_date, datetime.strptime(clock_in_str, "%H:%M:%S").time())
    #         #     # clock_out = datetime.combine(attendance_date, datetime.strptime(punch_time, "%H:%M:%S").time())
    #         #     clock_out = datetime.combine(attendance_date, punch_time)


    #         #     if clock_out < clock_in:
    #         #         return Response({"error": "Clock-out time cannot be before clock-in"}, status=400)

    #         #     total_work = clock_out - clock_in
    #         #     # Convert to HH:MM
    #         #     total_seconds = int(total_work.total_seconds())
    #         #     hours, remainder = divmod(total_seconds, 3600)
    #         #     minutes, _ = divmod(remainder, 60)

    #         #     total_work_str = f"{hours:02}:{minutes:02}"

    #         #     def time_str_to_decimal(time_str):
    #         #         hours, minutes = map(int, time_str.split(":"))
    #         #         return hours + minutes / 60

    #         #     formatted_total_work = time_str_to_decimal(total_work_str)


    #         #     # formatted_total_work = float(formatted_total_work)

    #         #     # print("total_work: ", total_work)
    #         #     print("formatted_total_work: ", formatted_total_work)

    #         #     # Late mark and half day logic
    #         #     late_mark = "N"
    #         #     is_half_day = "N"
    #         #     half_day_reason = []

    #         #     # Timings
    #         #     if employee_hub_name.lower() == "office":
    #         #         end_time = datetime.strptime("18:00", "%H:%M").time()
    #         #     else:
    #         #         end_time = datetime.strptime("17:30", "%H:%M").time()

    #         #     print("end_time: ", end_time)

    #         #     early_mark = "Y" if punch_time < end_time else "N"

    #         #     # 1. Half Day by Early Punch-Out
    #         #     if punch_time < end_time:
    #         #         is_half_day = "Y"
    #         #         half_day_reason = "Early Punch-Out"

    #         #     # 2. Half Day by Working Hours
    #         #     if formatted_total_work < 8.25:
    #         #         is_half_day = "Y"
    #         #         half_day_reason = "Insufficient Working Hours"

    #         #     # 3. Late Mark if between 8.15 and 8.5 hours
    #         #     if 8.25 <= formatted_total_work < 8.50:
    #         #         late_mark = "Y"

    #         #     # Count previous late marks in this month
    #         #     with connection.cursor() as cursor:
    #         #         cursor.execute(
    #         #             """
    #         #             SELECT COUNT(*) FROM ci_biomatric_data
    #         #             WHERE emp_id = %s AND MONTH(attendance_date) = MONTH(%s) AND YEAR(attendance_date) = YEAR(%s) AND late_mark = 'Y'
    #         #         """,
    #         #             [emp_id, attendance_date, attendance_date],
    #         #         )
    #         #         late_mark_count = cursor.fetchone()[0]

    #         #     # 4. Half Day if this is 2nd late mark
    #         #     if late_mark == "Y" and late_mark_count == 2:
    #         #         is_half_day = "Y"
    #         #         half_day_reason = "Exceeded Late Mark Limit"
    #         #         late_mark_count = 0  # reset count after marking half day
    #         #     elif late_mark == "Y":
    #         #         late_mark_count += 1  # increment for tracking

    #         #     # Update biomatric record
    #         #     with connection.cursor() as cursor:
    #         #         cursor.execute(
    #         #             """
    #         #             UPDATE ci_biomatric_data
    #         #             SET clock_out = %s,
    #         #                 clock_out_location = %s,
    #         #                 state_in_out = %s,
    #         #                 total_work = %s,
    #         #                 late_mark = %s,
    #         #                 early_mark = %s,
    #         #                 is_half_day = %s,
    #         #                 half_day_reason = %s,
    #         #                 late_mark_count = %s
    #         #             WHERE ci_biomatric_id = %s
    #         #         """,
    #         #             [
    #         #                 punch_time,
    #         #                 location,
    #         #                 "out",
    #         #                 total_work_str,
    #         #                 late_mark,
    #         #                 early_mark,
    #         #                 is_half_day,
    #         #                 half_day_reason,
    #         #                 late_mark_count,
    #         #                 biomatric_id
    #         #             ],
    #         #         )

    #         #     return Response(
    #         #         {
    #         #             "status": "Clock-Out recorded",
    #         #             "total_work_hours": round(formatted_total_work, 2),
    #         #             "late_mark": late_mark,
    #         #             "is_half_day": is_half_day,
    #         #             "half_day_reason": half_day_reason,
    #         #         }
    #         #     )

    #         elif punch_type == "OUT":
    #             # Fetch today's IN entry
    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     """
    #                     SELECT ci_biomatric_id, clock_in 
    #                     FROM ci_biomatric_data 
    #                     WHERE emp_id = %s AND attendance_date = %s AND status = 'P'
    #                     ORDER BY ci_biomatric_id DESC LIMIT 1
    #                 """,
    #                     [emp_id, attendance_date],
    #                 )
    #                 row = cursor.fetchone()

    #             if not row:
    #                 return Response({"error": "No clock-in found for today"}, status=404)

    #             biomatric_id, clock_in_str = row  # Renamed to make it clear it's a string

    #             # --- THIS IS THE FIX ---
    #             # The database returns a string 'HH:MM:SS' or a timedelta object.
    #             # We need to parse it into a proper datetime.time object.
    #             # First, handle the case where it might be a timedelta object (from a TIME column)
    #             if isinstance(clock_in_str, timedelta):
    #                 total_seconds = int(clock_in_str.total_seconds())
    #                 hours, remainder = divmod(total_seconds, 3600)
    #                 minutes, seconds = divmod(remainder, 60)
    #                 clock_in_time_obj = time(hours, minutes, seconds)
    #             else:
    #                 # If it's a string (from a VARCHAR column), parse it.
    #                 clock_in_time_obj = datetime.strptime(str(clock_in_str), "%H:%M:%S").time()
    #             # --- END OF FIX ---

    #             # Now combine() will work correctly for both clock-in and clock-out
    #             clock_in_datetime = datetime.combine(attendance_date, clock_in_time_obj)
    #             clock_out_datetime = datetime.combine(attendance_date, punch_time)

    #             if clock_out_datetime < clock_in_datetime:
    #                 return Response({"error": "Clock-out time cannot be before clock-in"}, status=400)

    #             total_work = clock_out_datetime - clock_in_datetime
    #             total_seconds = int(total_work.total_seconds())
    #             hours, remainder = divmod(total_seconds, 3600)
    #             minutes, _ = divmod(remainder, 60)
    #             total_work_str = f"{hours:02}:{minutes:02}"

    #             # The rest of your logic remains the same...
    #             total_work_decimal = hours + (minutes / 60)

    #             # ... [your existing logic for late marks, half-days, etc.] ...
                
    #             # (The rest of the code from the previous correct answer follows)
    #             # ...
    #             late_mark = "N"
    #             early_mark = "N"
    #             reasons_list = []

    #             if employee_hub_name.lower() == "office":
    #                 end_time = datetime.strptime("18:00", "%H:%M").time()
    #             else:
    #                 end_time = datetime.strptime("17:30", "%H:%M").time()

    #             if punch_time < end_time:
    #                 early_mark = "Y"
    #                 reasons_list.append("Early Punch-Out")

    #             if total_work_decimal < 8.25:
    #                 reasons_list.append("Insufficient Working Hours")
                
    #             if 8.25 <= total_work_decimal < 8.50:
    #                 late_mark = "Y"

    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     """
    #                     SELECT late_mark_count FROM ci_biomatric_data
    #                     WHERE emp_id = %s AND MONTH(attendance_date) = MONTH(%s) AND YEAR(attendance_date) = YEAR(%s)
    #                     ORDER BY ci_biomatric_id DESC LIMIT 1
    #                     """,
    #                     [emp_id, attendance_date, attendance_date],
    #                 )
    #                 result = cursor.fetchone()
    #                 late_mark_count = result[0] if result else 0

    #             if late_mark == "Y":
    #                 if late_mark_count >= 2:
    #                     reasons_list.append("Exceeded Late Mark Limit")
    #                     late_mark_count = 0
    #                 else:
    #                     late_mark_count += 1

    #             is_half_day = "Y" if reasons_list else "N"
    #             half_day_reason = ", ".join(reasons_list) if reasons_list else None

    #             with connection.cursor() as cursor:
    #                 cursor.execute(
    #                     """
    #                     UPDATE ci_biomatric_data
    #                     SET clock_out = %s, clock_out_location = %s, state_in_out = %s, total_work = %s,
    #                         late_mark = %s, early_mark = %s, is_half_day = %s, half_day_reason = %s,
    #                         late_mark_count = %s
    #                     WHERE ci_biomatric_id = %s
    #                 """,
    #                     [
    #                         punch_time, location, "out", total_work_str, late_mark, early_mark,
    #                         is_half_day, half_day_reason, late_mark_count, biomatric_id
    #                     ],
    #                 )

    #             return Response({
    #                     "status": "Clock-Out recorded",
    #                     "total_work_hours": round(total_work_decimal, 2),
    #                     "late_mark": late_mark, "is_half_day": is_half_day,
    #                     "half_day_reason": half_day_reason if half_day_reason else "N/A",
    #                 })

    #         return Response({"error": "Invalid punch type"}, status=400)

    #     except Exception as e:

    #         return Response(
    #             {"status": "error", "message": f"An error occured: {str(e)}"},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         )

    # def post(self, request):
    #     try:
    #         # Input validation
    #         emp_id = request.data.get("emp_id")
    #         punch_time_str = request.data.get("punch_time")
    #         punch_type = request.data.get("punch_type")
    #         location = request.data.get("location", "")
            
    #         # Validate required fields
    #         if not emp_id or not punch_time_str or not punch_type:
    #             return Response(
    #                 {"error": "Missing required fields: emp_id, punch_time, punch_type"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
            
    #         # Validate punch_type
    #         if punch_type not in ["IN", "OUT"]:
    #             return Response(
    #                 {"error": "Invalid punch_type. Must be 'IN' or 'OUT'"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
            
    #         # Parse punch time
    #         try:
    #             punch_datetime = datetime.strptime(punch_time_str, "%Y-%m-%d %H:%M:%S")
    #             attendance_date = punch_datetime.date()
    #             punch_time = punch_datetime.time()
    #         except ValueError:
    #             return Response(
    #                 {"error": "Invalid punch_time format. Expected: YYYY-MM-DD HH:MM:SS"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
            
    #         # Get employee details
    #         employee_details = self._get_employee_details(emp_id)
    #         if not employee_details:
    #             return Response(
    #                 {"error": "Employee not found"}, 
    #                 status=status.HTTP_404_NOT_FOUND
    #             )
            
    #         user_id, department_id, designation_id = employee_details
            
    #         # Get hub details
    #         hub_details = self._get_hub_details(user_id)
    #         employee_hub_id, employee_hub_name = hub_details
            
    #         # Use transaction for data consistency
    #         with transaction.atomic():
    #             if punch_type == "IN":
    #                 return self._handle_clock_in(
    #                     emp_id, user_id, employee_hub_id, employee_hub_name,
    #                     attendance_date, punch_time, location
    #                 )
    #             else:  # punch_type == "OUT"
    #                 return self._handle_clock_out(
    #                     emp_id, employee_hub_name, attendance_date, punch_time, location
    #                 )
                    
    #     except Exception as e:
    #         logger.error(f"Error in EmployeeAttendance: {str(e)}")
    #         return Response(
    #             {"status": "error", "message": "An internal error occurred"},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         )
    
    # def _get_employee_details(self, emp_id):
    #     """Get employee details from database"""
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             "SELECT user_id, department_id, designation_id FROM ci_erp_users_details WHERE employee_id = %s",
    #             [emp_id],
    #         )
    #         row = cursor.fetchone()
    #         if not row:
    #             return None
    #         return (
    #             row[0] if row[0] is not None else 0,
    #             row[1] if row[1] is not None else 0,
    #             row[2] if row[2] is not None else 0
    #         )
    
    # def _get_hub_details(self, user_id):
    #     """Get hub details from database"""
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             "SELECT u.employee_hub_id, eh.employee_hub_name FROM ci_erp_users u inner join ci_employee_hub eh on u.employee_hub_id = eh.employee_hub_id WHERE u.id = %s",
    #             [user_id],
    #         )
    #         hub_row = cursor.fetchone()
            
    #         if hub_row:
    #             return hub_row[0], hub_row[1]
    #         else:
    #             return 0, ""
    
    # def _get_work_timings(self, employee_hub_name):
    #     """Get work timings based on hub"""
    #     if employee_hub_name.lower() == "office":
    #         return time(10, 0), time(18, 0)  # 10:00 AM to 6:00 PM
    #     else:
    #         return time(9, 30), time(17, 30)  # 9:30 AM to 5:30 PM
    
    # def _get_current_month_late_marks(self, emp_id, attendance_date):
    #     """Get current month's late mark count"""
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             SELECT COUNT(*) FROM ci_biomatric_data
    #             WHERE emp_id = %s 
    #             AND MONTH(attendance_date) = MONTH(%s) 
    #             AND YEAR(attendance_date) = YEAR(%s) 
    #             AND late_mark = 'Y'
    #             """,
    #             [emp_id, attendance_date, attendance_date],
    #         )
    #         return cursor.fetchone()[0]
    
    # def _handle_clock_in(self, emp_id, user_id, employee_hub_id, employee_hub_name, 
    #                     attendance_date, punch_time, location):
    #     """Handle clock-in logic"""
        
    #     # Check if already clocked in today
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             SELECT COUNT(*) FROM ci_biomatric_data 
    #             WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
    #             """,
    #             [emp_id, attendance_date]
    #         )
    #         if cursor.fetchone()[0] > 0:
    #             return Response(
    #                 {"error": "Already clocked in today"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
        
    #     in_time, _ = self._get_work_timings(employee_hub_name)
    #     late_mark = "Y" if punch_time > in_time else "N"
        
    #     # Get current month's late mark count
    #     late_mark_count = self._get_current_month_late_marks(emp_id, attendance_date)
        
    #     # Check if this late mark exceeds the limit
    #     is_half_day = "N"
    #     half_day_reason = None
        
    #     if late_mark == "Y":
    #         if late_mark_count >= 2:  # This would be the 3rd late mark
    #             is_half_day = "Y"
    #             half_day_reason = "Exceeded Late Mark Limit"
    #             # Don't increment late_mark_count as it will be reset after half day
    #         else:
    #             late_mark_count += 1
        
    #     # Insert clock-in record
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             INSERT INTO ci_biomatric_data 
    #             (emp_id, userid, employee_hub_id, login_date, clock_in, clock_in_location, 
    #              state_in_out, late_mark, is_half_day, half_day_reason, late_mark_count, 
    #              attendance_date, attendance_status, status, from_od, reason)
    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #             """,
    #             [
    #                 emp_id, user_id, employee_hub_id, attendance_date, punch_time, location,
    #                 "in", late_mark, is_half_day, half_day_reason, late_mark_count,
    #                 attendance_date, "Present", "P", "N", "Check IN"
    #             ],
    #         )
        
    #     return Response({
    #         "status": "Clock-In recorded",
    #         "late_mark": late_mark,
    #         "is_half_day": is_half_day,
    #         "half_day_reason": half_day_reason if half_day_reason else "N/A"
    #     })
    
    # def _handle_clock_out(self, emp_id, employee_hub_name, attendance_date, punch_time, location):
    #     """Handle clock-out logic"""
        
    #     # Fetch today's IN entry
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             SELECT ci_biomatric_id, clock_in, late_mark_count
    #             FROM ci_biomatric_data 
    #             WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
    #             ORDER BY ci_biomatric_id DESC LIMIT 1
    #             """,
    #             [emp_id, attendance_date],
    #         )
    #         row = cursor.fetchone()
        
    #     if not row:
    #         return Response(
    #             {"error": "No clock-in found for today"}, 
    #             status=status.HTTP_404_NOT_FOUND
    #         )
        
    #     biomatric_id, clock_in_data, current_late_mark_count = row
        
    #     # Parse clock_in time properly
    #     clock_in_time_obj = self._parse_time_data(clock_in_data)
        
    #     # Calculate work hours
    #     clock_in_datetime = datetime.combine(attendance_date, clock_in_time_obj)
    #     clock_out_datetime = datetime.combine(attendance_date, punch_time)
        
    #     if clock_out_datetime <= clock_in_datetime:
    #         return Response(
    #             {"error": "Clock-out time must be after clock-in time"}, 
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     total_work = clock_out_datetime - clock_in_datetime
    #     total_work_decimal = total_work.total_seconds() / 3600  # Convert to hours
        
    #     # Format total work as HH:MM
    #     hours = int(total_work_decimal)
    #     minutes = int((total_work_decimal - hours) * 60)
    #     total_work_str = f"{hours:02}:{minutes:02}"
        
    #     # Determine work timings
    #     _, end_time = self._get_work_timings(employee_hub_name)
        
    #     # Initialize flags and reasons
    #     late_mark = "N"
    #     early_mark = "N"
    #     reasons_list = []
    #     late_mark_count = current_late_mark_count or 0
        
    #     # Check for early punch-out
    #     if punch_time < end_time:
    #         early_mark = "Y"
    #         reasons_list.append("Early Punch-Out")
        
    #     # Check for insufficient working hours (less than 8.25 hours)
    #     if total_work_decimal < 8.25:
    #         reasons_list.append("Insufficient Working Hours")
        
    #     # Check for late mark (between 8.25 and 8.5 hours)
    #     if 8.25 <= total_work_decimal < 8.50:
    #         late_mark = "Y"
    #         # Check if this exceeds late mark limit
    #         if late_mark_count >= 2:  # This would be the 3rd late mark
    #             reasons_list.append("Exceeded Late Mark Limit")
    #             late_mark_count = 0  # Reset after half day
    #         else:
    #             late_mark_count += 1
        
    #     # Determine half day status
    #     is_half_day = "Y" if reasons_list else "N"
    #     half_day_reason = ", ".join(reasons_list) if reasons_list else None
        
    #     # Update biometric record
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             UPDATE ci_biomatric_data
    #             SET clock_out = %s, clock_out_location = %s, state_in_out = %s, 
    #                 total_work = %s, late_mark = %s, early_mark = %s, 
    #                 is_half_day = %s, half_day_reason = %s, late_mark_count = %s
    #             WHERE ci_biomatric_id = %s
    #             """,
    #             [
    #                 punch_time, location, "out", total_work_str, late_mark, early_mark,
    #                 is_half_day, half_day_reason, late_mark_count, biomatric_id
    #             ],
    #         )
        
    #     return Response({
    #         "status": "Clock-Out recorded",
    #         "total_work_hours": round(total_work_decimal, 2),
    #         "late_mark": late_mark,
    #         "early_mark": early_mark,
    #         "is_half_day": is_half_day,
    #         "half_day_reason": half_day_reason if half_day_reason else "N/A",
    #     })
    
    # def _parse_time_data(self, time_data):
    #     """Parse time data from database (handles both string and timedelta)"""
    #     if isinstance(time_data, timedelta):
    #         total_seconds = int(time_data.total_seconds())
    #         hours, remainder = divmod(total_seconds, 3600)
    #         minutes, seconds = divmod(remainder, 60)
    #         return time(hours, minutes, seconds)
    #     else:
    #         # Handle string format
    #         return datetime.strptime(str(time_data), "%H:%M:%S").time()

    def post(self, request):
        try:
            emp_id = request.data.get("emp_id")
            punch_time_str = request.data.get("punch_time")
            punch_type = request.data.get("punch_type")
            location = request.data.get("location", "")
            
            if not emp_id or not punch_time_str or not punch_type:
                return Response(
                    {"error": "Missing required fields: emp_id, punch_time, punch_type"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if punch_type not in ["IN", "OUT"]:
                return Response(
                    {"error": "Invalid punch_type. Must be 'IN' or 'OUT'"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                punch_datetime = datetime.strptime(punch_time_str, "%Y-%m-%d %H:%M:%S")
                attendance_date = punch_datetime.date()
                punch_time = punch_datetime.time()

            except ValueError:
                return Response(
                    {"error": "Invalid punch_time format. Expected: YYYY-MM-DD HH:MM:SS"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            employee_details = self._get_employee_details(emp_id)
            if not employee_details:
                return Response(
                    {"error": "Employee not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            user_id, department_id, designation_id = employee_details
            hub_details = self._get_hub_details(user_id)
            employee_hub_id, employee_hub_name = hub_details
            
            with transaction.atomic():
                if punch_type == "IN":
                    return self._handle_clock_in(
                        emp_id, user_id, employee_hub_id, employee_hub_name,
                        attendance_date, punch_time, punch_datetime, location
                    )
                else:
                    return self._handle_clock_out(
                        emp_id, employee_hub_name, attendance_date, punch_time, punch_datetime, location
                    )
                    
        except Exception as e:
            logger.error(f"Error in EmployeeAttendance: {str(e)}")
            return Response(
                {"status": "error", "message": "An internal error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_employee_details(self, emp_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, department_id, designation_id FROM ci_erp_users_details WHERE employee_id = %s",
                [emp_id],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return (
                row[0] if row[0] is not None else 0,
                row[1] if row[1] is not None else 0,
                row[2] if row[2] is not None else 0
            )
    
    # def _get_hub_details(self, user_id):
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             "SELECT u.employee_hub_id, eh.employee_hub_name FROM ci_erp_users u inner join ci_employee_hub eh on u.employee_hub_id = eh.employee_hub_id WHERE u.id = %s",
    #             [user_id],
    #         )
    #         hub_row = cursor.fetchone()
            
    #         if hub_row:
    #             return hub_row[0], hub_row[1]
    #         else:
    #             return 0, ""
    
    def _get_hub_details(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cos.office_shift_id , cos.shift_name FROM ci_erp_users_details u inner join ci_office_shifts cos on u.office_shift_id = cos.office_shift_id WHERE u.user_id = %s",
                [user_id],
            )
            hub_row = cursor.fetchone()
           
            if hub_row:
                return hub_row[0], hub_row[1]
            else:
                return 0, ""
    
    # def _get_work_timings(self, employee_hub_name):
    def _get_work_timings(self, office_shift_id, shift_name, attendance_date):

        # if employee_hub_name.lower() == "office":
        #     return time(9, 30), time(18, 0)
        # elif employee_hub_name.lower() == "factory":
        #     return time(9, 0), time(17, 30)
        # else:
        #     return time(9, 30), time(18, 0)

        # New logic

        # if employee_hub_name.lower() != "office":
        #     # Keep original logic for non-office hubs
        #     if employee_hub_name.lower() == "factory":
        #         return time(9, 0), time(17, 30)
        #     else:
        #         return time(9, 30), time(18, 0)
            
        day_name = attendance_date.strftime('%A').lower()  # Get day name (monday, tuesday, etc.)
        
        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         f"""
        #         SELECT {day_name}_in_time, {day_name}_out_time
        #         FROM ci_office_shifts 
        #         WHERE employee_hub_id = %s
        #         ORDER BY office_shift_id DESC
        #         LIMIT 1
        #         """,
        #         [employee_hub_id]
        #     )
        
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {day_name}_in_time, {day_name}_out_time
                FROM ci_office_shifts
                WHERE office_shift_id = %s
                ORDER BY office_shift_id DESC
                LIMIT 1
                """,
                [office_shift_id]
            )
            
            shift_row = cursor.fetchone()
            
            if shift_row and shift_row[0] and shift_row[1]:
                try:
                    # Parse the time strings to time objects
                    in_time_str = shift_row[0]
                    out_time_str = shift_row[1]
                    
                    # Handle different time formats that might be in the database
                    if isinstance(in_time_str, str):
                        # Try parsing HH:MM:SS format first, then HH:MM
                        try:
                            in_time = datetime.strptime(in_time_str, "%H:%M:%S").time()
                        except ValueError:
                            in_time = datetime.strptime(in_time_str, "%H:%M").time()
                    else:
                        in_time = in_time_str
                    
                    if isinstance(out_time_str, str):
                        try:
                            out_time = datetime.strptime(out_time_str, "%H:%M:%S").time()
                        except ValueError:
                            out_time = datetime.strptime(out_time_str, "%H:%M").time()
                    else:
                        out_time = out_time_str
                    
                    return in_time, out_time
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing shift times for employee_hub {employee_hub_id}: {e}")
                    # Fall back to default office timings
                    return time(9, 30), time(18, 0)
            else:
                # No shift found or empty times, use default office timings
                return time(9, 30), time(18, 0)
    
    def _get_current_month_late_marks(self, emp_id, attendance_date):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT SUM(late_mark_count) FROM ci_biomatric_data
                WHERE emp_id = %s 
                AND MONTH(attendance_date) = MONTH(%s) 
                AND YEAR(attendance_date) = YEAR(%s) 
                
                """,
                [emp_id, attendance_date, attendance_date],
            )
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0

    def _handle_clock_in(self, emp_id, user_id, employee_hub_id, employee_hub_name, 
                         attendance_date, punch_time, punch_datetime, location):
        
        # print(f"DEBUG - Raw punch_time: {punch_time}")
        # print(f"DEBUG - punch_time type: {type(punch_time)}")
        # print(f"DEBUG - punch_time hour: {punch_time.hour}")
        # print(f"DEBUG - Comparison time (1 PM): {time(13, 0)}")
        # print(f"DEBUG - Is punch_time > 1 PM? {punch_time > time(13, 0)}")

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM ci_biomatric_data 
                WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
                """,
                [emp_id, attendance_date]
            )
            if cursor.fetchone()[0] > 0:
                # return Response(
                #     {"status": "Clock-in ignored", "message": "First clock-in already recorded for the day."}, 
                #     status=status.HTTP_200_OK
                # )

                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT ci_biomatric_id FROM ci_biomatric_data
                        WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
                        ORDER BY ci_biomatric_id DESC LIMIT 1
                    """, [emp_id, attendance_date])

                    row = cursor.fetchone()
                    if row:
                        biometric_id = row[0]
                        cursor.execute("""
                            INSERT INTO ci_biomatric_data_2 (ci_biomatric_id, emp_id, login_date, clock_in)
                            VALUES (%s, %s, %s, %s)
                        """, [biometric_id, emp_id, punch_datetime, punch_time])

                return Response({"status": "Clock-in recorded in secondary log table"}, status=status.HTTP_200_OK)

        # in_time, _ = self._get_work_timings(employee_hub_name)
        # in_time, _ = self._get_work_timings(employee_hub_name, employee_hub_id, attendance_date)
        in_time, _ = self._get_work_timings(employee_hub_id, employee_hub_name, attendance_date)
 

        today = datetime.combine(attendance_date, in_time)
        punch_datetime = datetime.combine(attendance_date, punch_time)

        grace_period = timedelta(minutes=15)
        in_time_with_grace = today + grace_period

        late_mark = "Y" if punch_datetime > in_time_with_grace else "N"

        # print(f"DEBUG - Expected in_time: {in_time}")
        # print(f"DEBUG - in_time_with_grace: {in_time_with_grace}")
        # print(f"DEBUG - punch_datetime_full: {punch_datetime}")
        # print(f"DEBUG - Late mark: {late_mark}")

        if late_mark == "Y":
            late_mark_count = self._get_current_month_late_marks(emp_id, attendance_date)
        else:
            late_mark_count = 0


        # print(f"DEBUG - Current late_mark_count: {late_mark_count}")
        # print(f"DEBUG - Attendance Date: {attendance_date}")

        is_half_day = "N"
        reasons_list = []

        # print(f"DEBUG - About to check if punch_time > time(13, 0)")
        # print(f"DEBUG - punch_time = {punch_time}, time(13, 0) = {time(13, 0)}")

        if punch_time > time(13, 0):  # 1:00 PM
            reasons_list.append("Punched After 1 PM")

        # print(f"DEBUG - reasons_list after 1 PM check: {reasons_list}")

        if late_mark == "Y":
            if late_mark_count >= 2:
                is_half_day = "Y"
                reasons_list.append("Exceeded Late Mark Limit")

                # Reset all late marks and counts for the month before inserting
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE ci_biomatric_data
                        SET late_mark_count = 0
                        WHERE emp_id = %s
                        AND MONTH(attendance_date) = MONTH(%s)
                        AND YEAR(attendance_date) = YEAR(%s)
                        """,
                        [emp_id, attendance_date, attendance_date]
                    )

                late_mark_count = 0
            else:
                late_mark_count += 1
        

        is_half_day = "Y" if reasons_list else "N"
        half_day_reason = ", ".join(reasons_list) if reasons_list else None

        attendance_status = 'P'

        if is_half_day == 'Y':
            attendance_status = self._deduct_half_day_leave(emp_id)
            

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ci_biomatric_data 
                (emp_id, userid, employee_hub_id, login_date, clock_in, clock_in_location, 
                 state_in_out, late_mark, is_half_day, half_day_reason, late_mark_count, 
                 attendance_date, attendance_status, status, from_od, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    emp_id, user_id, employee_hub_id, punch_datetime, punch_time, location,
                    "in", late_mark, is_half_day, half_day_reason, late_mark_count,
                    attendance_date, "Present", attendance_status, "N", "Check IN"
                ],
            )

            cursor.execute(
                """
                    SELECT ci_biomatric_id
                    FROM ci_biomatric_data
                    WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
                    ORDER BY ci_biomatric_id DESC LIMIT 1
                """, [emp_id, attendance_date])

            biometric_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO ci_biomatric_data_2 (ci_biomatric_id, emp_id, login_date, clock_in)
                VALUES (%s, %s, %s, %s)

            """, [biometric_id, emp_id, punch_datetime, punch_time])

        return Response({
            "status": "Clock-In recorded",
            "punch_time": punch_datetime,
            "late_mark": late_mark,
            "is_half_day": is_half_day,
            "half_day_reason": half_day_reason if half_day_reason else "N/A"
        })

    def _handle_clock_out(self, emp_id, employee_hub_name, attendance_date, punch_time, punch_datetime, location):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ci_biomatric_id, clock_in, is_half_day, late_mark, status, half_day_reason
                FROM ci_biomatric_data 
                WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
                ORDER BY ci_biomatric_id DESC LIMIT 1
                """,
                [emp_id, attendance_date],
            )
            row1 = cursor.fetchone()

            cursor.execute(
                """
                SELECT id
                FROM ci_biomatric_data_2
                WHERE emp_id = %s AND login_date = %s
                ORDER BY ci_biomatric_id DESC LIMIT 1
                """,
                [emp_id, attendance_date],
            )

            row2 = cursor.fetchone()

        if not row1:
            return Response(
                {"error": "No clock-in found for today"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # biomatric_id, clock_in_data, current_half_day, late_mark, attendance_status, current_half_day_reason = row
        biomatric_id1 = row1[0]
        biomatric_id2 = row2[0]



        # clock_in_time_obj = self._parse_time_data(clock_in_data)
        # clock_in_datetime = datetime.combine(attendance_date, clock_in_time_obj)
        # clock_out_datetime = datetime.combine(attendance_date, punch_time)

        # if clock_out_datetime <= clock_in_datetime:
        #     return Response(
        #         {"error": "Clock-out time must be after clock-in time"}, 
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # total_work = clock_out_datetime - clock_in_datetime
        # total_work_decimal = total_work.total_seconds() / 3600

        # hours = int(total_work_decimal)
        # minutes = int((total_work_decimal - hours) * 60)
        # total_work_str = f"{hours:02}:{minutes:02}"

        # _, end_time = self._get_work_timings(employee_hub_name)

        # end_datetime = datetime.combine(attendance_date, end_time)

        # # late_mark = "N"
        # early_mark = "N"
        # reasons_list = [current_half_day_reason] if current_half_day_reason else []

        # late_mark_count = self._get_current_month_late_marks(emp_id, attendance_date)

        # # if punch_time < end_time:
        # if punch_datetime < end_datetime:
        #     early_mark = "Y"
        #     reasons_list.append("Early Punch-Out")

        # if total_work_decimal < 8.25:
        #     reasons_list.append("Insufficient Working Hours")

        # if 8.25 <= total_work_decimal < 8.50:
        #     late_mark = "Y"

        # # if late_mark == 'Y':
        # if late_mark_count >= 2:
        #     is_half_day = "Y"
        #     reasons_list.append("Exceeded Late Mark Limit")

        #     # Reset all late marks and counts for the month before inserting
        #     with connection.cursor() as cursor:
        #         cursor.execute(
        #             """
        #             UPDATE ci_biomatric_data
        #             SET late_mark_count = 0
        #             WHERE emp_id = %s
        #             AND MONTH(attendance_date) = MONTH(%s)
        #             AND YEAR(attendance_date) = YEAR(%s)
        #             """,
        #             [emp_id, attendance_date, attendance_date]
        #         )

        #     late_mark_count = 0
        # else:
        #     late_mark_count += 1


        # is_half_day = "Y" if reasons_list else "N"
        # half_day_reason = ", ".join(reasons_list) if reasons_list else None

        # if is_half_day == 'Y' and current_half_day == 'N':
        #     attendance_status = self._deduct_half_day_leave(emp_id)

        # if current_half_day == 'N':
        #     mark_half_day = is_half_day
        # else:
        #     mark_half_day = current_half_day
                            

        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         """
        #         UPDATE ci_biomatric_data
        #         SET clock_out = %s, clock_out_location = %s, state_in_out = %s, 
        #             total_work = %s, late_mark = %s, early_mark = %s, 
        #             is_half_day = %s, half_day_reason = %s, late_mark_count = %s, status = %s, reason = %s
        #         WHERE ci_biomatric_id = %s  
        #         """,
        #         [
        #             punch_time, location, "out", total_work_str, late_mark, early_mark,
        #             mark_half_day, half_day_reason, late_mark_count, attendance_status, "CHECK OUT", biomatric_id
        #         ],
        #     )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE ci_biomatric_data
                SET clock_out = %s, clock_out_location = %s
                WHERE ci_biomatric_id = %s  
                """,
                [punch_time, location, biomatric_id1],
            )

            cursor.execute("""
                UPDATE ci_biomatric_data_2
                SET clock_out = %s
                WHERE id = %s
                ORDER BY id DESC LIMIT 1
            """, [punch_time, biomatric_id2])


        return Response({
            "status": "Clock-Out recorded",
            "punch_time": punch_datetime
            # "total_work_hours": round(total_work_decimal, 2),
            # "late_mark": late_mark,
            # "early_mark": early_mark,
            # "is_half_day": is_half_day,
            # "half_day_reason": half_day_reason if half_day_reason else "N/A",
        })
    
    def _deduct_half_day_leave(self, emp_id):
        
        now = datetime.now()
        year = now.year
        
        with connection.cursor() as cursor:
            
            cursor.execute(
                """
                UPDATE ci_leave_balance
                SET balance_leave = balance_leave - 0.5
                WHERE employee_id = %s AND year = %s AND status = 'Y' 
                AND leave_type_id = 184 AND balance_leave >= 0.5
                """,
                [emp_id, year]
            )
            
            if cursor.rowcount == 0:
                
                cursor.execute(
                    """
                    SELECT balance_leave
                    FROM ci_leave_balance
                    WHERE employee_id = %s AND year = %s AND status = 'Y' AND leave_type_id = 184
                    """,
                    [emp_id, year]
                )
                result = cursor.fetchone()
                
                if result and result[0] < 0.5:
                    return 'H' 
        
        return 'P'

    def _parse_time_data(self, time_data):
        if isinstance(time_data, timedelta):
            total_seconds = int(time_data.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return time(hours, minutes, seconds)
        else:
            return datetime.strptime(str(time_data), "%H:%M:%S").time()

    # def post(self, request):
    #     try:
    #         emp_id = request.data.get("emp_id")
    #         punch_time_str = request.data.get("punch_time")
    #         punch_type = request.data.get("punch_type")
    #         location = request.data.get("location", "")
            
    #         if not emp_id or not punch_time_str or not punch_type:
    #             return Response(
    #                 {"error": "Missing required fields: emp_id, punch_time, punch_type"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
            
    #         if punch_type not in ["IN", "OUT"]:
    #             return Response(
    #                 {"error": "Invalid punch_type. Must be 'IN' or 'OUT'"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
            
    #         try:
    #             # Parse ISO format datetime
    #             punch_datetime_iso = datetime.fromisoformat(punch_time_str.replace('Z', '+00:00'))
    #             punch_time_iso = punch_datetime_iso.time().isoformat()
                
    #             # Convert to local timezone for calculations
    #             local_tz = pytz.timezone('Asia/Kolkata')  # Adjust timezone as needed
    #             punch_datetime_local = punch_datetime_iso.astimezone(local_tz)
                
    #             attendance_date = punch_datetime_local.date()
    #             punch_time_local = punch_datetime_local.time()
                
    #         except ValueError:
    #             return Response(
    #                 {"error": "Invalid punch_time format. Expected ISO format (e.g., '2024-01-01T10:30:00Z')"}, 
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
            
    #         employee_details = self._get_employee_details(emp_id)
    #         if not employee_details:
    #             return Response(
    #                 {"error": "Employee not found"}, 
    #                 status=status.HTTP_404_NOT_FOUND
    #             )
            
    #         user_id, department_id, designation_id = employee_details
    #         hub_details = self._get_hub_details(user_id)
    #         employee_hub_id, employee_hub_name = hub_details
            
    #         with transaction.atomic():
    #             if punch_type == "IN":
    #                 return self._handle_clock_in(
    #                     emp_id, user_id, employee_hub_id, employee_hub_name,
    #                     attendance_date, punch_time_local, punch_time_iso, punch_datetime_iso, 
    #                     punch_datetime_local, location
    #                 )
    #             else:
    #                 return self._handle_clock_out(
    #                     emp_id, employee_hub_name, attendance_date, punch_time_local, punch_time_iso,
    #                     punch_datetime_iso, punch_datetime_local, location
    #                 )
                    
    #     except Exception as e:
    #         logger.error(f"Error in EmployeeAttendance: {str(e)}")
    #         return Response(
    #             {"status": "error", "message": f"An internal error occurred: {str(e)}"},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         )

    # def _get_employee_details(self, emp_id):
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             "SELECT user_id, department_id, designation_id FROM ci_erp_users_details WHERE employee_id = %s",
    #             [emp_id],
    #         )
    #         row = cursor.fetchone()
    #         if not row:
    #             return None
    #         return (
    #             row[0] if row[0] is not None else 0,
    #             row[1] if row[1] is not None else 0,
    #             row[2] if row[2] is not None else 0
    #         )
    
    # def _get_hub_details(self, user_id):
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             "SELECT u.employee_hub_id, eh.employee_hub_name FROM ci_erp_users u inner join ci_employee_hub eh on u.employee_hub_id = eh.employee_hub_id WHERE u.id = %s",
    #             [user_id],
    #         )
    #         hub_row = cursor.fetchone()
            
    #         if hub_row:
    #             return hub_row[0], hub_row[1]
    #         else:
    #             return 0, ""
    
    # def _get_work_timings(self, employee_hub_name, employee_hub_id, attendance_date):
    #     day_name = attendance_date.strftime('%A').lower()
        
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             f"""
    #             SELECT {day_name}_in_time, {day_name}_out_time
    #             FROM ci_office_shifts 
    #             WHERE employee_hub_id = %s
    #             ORDER BY office_shift_id DESC
    #             LIMIT 1
    #             """,
    #             [employee_hub_id]
    #         )
            
    #         shift_row = cursor.fetchone()
            
    #         if shift_row and shift_row[0] and shift_row[1]:
    #             try:
    #                 in_time_str = shift_row[0]
    #                 out_time_str = shift_row[1]
                    
    #                 if isinstance(in_time_str, str):
    #                     try:
    #                         in_time = datetime.strptime(in_time_str, "%H:%M:%S").time()
    #                     except ValueError:
    #                         in_time = datetime.strptime(in_time_str, "%H:%M").time()
    #                 else:
    #                     in_time = in_time_str
                    
    #                 if isinstance(out_time_str, str):
    #                     try:
    #                         out_time = datetime.strptime(out_time_str, "%H:%M:%S").time()
    #                     except ValueError:
    #                         out_time = datetime.strptime(out_time_str, "%H:%M").time()
    #                 else:
    #                     out_time = out_time_str
                    
    #                 return in_time, out_time
                    
    #             except (ValueError, TypeError) as e:
    #                 logger.warning(f"Error parsing shift times for employee_hub {employee_hub_id}: {e}")
    #                 return time(9, 30), time(18, 0)
    #         else:
    #             return time(9, 30), time(18, 0)
    
    # def _get_current_month_late_marks(self, emp_id, attendance_date):
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             SELECT SUM(late_mark_count) FROM ci_biomatric_data
    #             WHERE emp_id = %s 
    #             AND MONTH(attendance_date) = MONTH(%s) 
    #             AND YEAR(attendance_date) = YEAR(%s) 
    #             """,
    #             [emp_id, attendance_date, attendance_date],
    #         )
    #         result = cursor.fetchone()
    #         return result[0] if result and result[0] is not None else 0

    # def _handle_clock_in(self, emp_id, user_id, employee_hub_id, employee_hub_name, 
    #                      attendance_date, punch_time_local, punch_time_iso, punch_datetime_iso, 
    #                      punch_datetime_local, location):
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             SELECT COUNT(*) FROM ci_biomatric_data 
    #             WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
    #             """,
    #             [emp_id, attendance_date]
    #         )
    #         if cursor.fetchone()[0] > 0:
    #             # return Response(
    #             #     {"status": "Clock-in ignored", "message": "First clock-in already recorded for the day."}, 
    #             #     status=status.HTTP_200_OK
    #             # )

    #             with connection.cursor() as cursor:
    #                 cursor.execute("""
    #                     SELECT ci_biomatric_id FROM ci_biomatric_data 
    #                     WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
    #                     ORDER BY ci_biomatric_id DESC LIMIT 1
    #                 """, [emp_id, attendance_date])
    #                 row = cursor.fetchone()
    #                 if row:
    #                     biometric_id = row[0]
    #                     cursor.execute("""
    #                         INSERT INTO ci_biomatric_data_2 (ci_biomatric_id, emp_id, login_date, clock_in)
    #                         VALUES (%s, %s, %s, %s)
    #                     """, [biometric_id, emp_id, punch_datetime_iso, punch_time_iso])
    #             return Response({"status": "Clock-in recorded in secondary log table"}, status=status.HTTP_200_OK)

    #     # Use local time for calculations
    #     in_time, _ = self._get_work_timings(employee_hub_name, employee_hub_id, attendance_date)

    #     today = datetime.combine(attendance_date, in_time)
    #     punch_datetime_for_calc = datetime.combine(attendance_date, punch_time_local)

    #     grace_period = timedelta(minutes=30)
    #     in_time_with_grace = today + grace_period

    #     late_mark = "Y" if punch_datetime_for_calc > in_time_with_grace else "N"

    #     if late_mark == "Y":
    #         late_mark_count = self._get_current_month_late_marks(emp_id, attendance_date)
    #     else:
    #         late_mark_count = 0

    #     is_half_day = "N"
    #     reasons_list = []

    #     # Use local time for comparison
    #     if punch_time_local > time(13, 0):  # 1:00 PM
    #         reasons_list.append("Punched After 1 PM")

    #     if late_mark_count >= 2:
    #         is_half_day = "Y"
    #         reasons_list.append("Exceeded Late Mark Limit")

    #         with connection.cursor() as cursor:
    #             cursor.execute(
    #                 """
    #                 UPDATE ci_biomatric_data
    #                 SET late_mark_count = 0
    #                 WHERE emp_id = %s
    #                 AND MONTH(attendance_date) = MONTH(%s)
    #                 AND YEAR(attendance_date) = YEAR(%s)
    #                 """,
    #                 [emp_id, attendance_date, attendance_date]
    #             )

    #         late_mark_count = 0
    #     else:
    #         late_mark_count += 1

    #     is_half_day = "Y" if reasons_list else "N"
    #     half_day_reason = ", ".join(reasons_list) if reasons_list else None

    #     attendance_status = 'P'

    #     if is_half_day == 'Y':
    #         attendance_status = self._deduct_half_day_leave(emp_id)

    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             INSERT INTO ci_biomatric_data 
    #             (emp_id, userid, employee_hub_id, login_date, clock_in, clock_in_location, 
    #              state_in_out, late_mark, is_half_day, half_day_reason, late_mark_count, 
    #              attendance_date, attendance_status, status, from_od, reason)
    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #             """,
    #             [
    #                 emp_id, user_id, employee_hub_id, punch_datetime_iso, punch_time_iso, location,
    #                 "in", late_mark, is_half_day, half_day_reason, late_mark_count,
    #                 attendance_date, "Present", attendance_status, "N", "Check IN"
    #             ],
    #         )

    #         # cursor.execute("SELECT LAST_INSERT_ID()")
    #         cursor.execute(
    #             """
    #                 SELECT ci_biomatric_id
    #                 FROM ci_biomatric_data 
    #                 WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
    #                 ORDER BY ci_biomatric_id DESC LIMIT 1
    #             """, [emp_id, attendance_date])
    #         biometric_id = cursor.fetchone()[0]

    #         cursor.execute("""
    #             INSERT INTO ci_biomatric_data_2 (ci_biomatric_id, emp_id, login_date, clock_in)
    #             VALUES (%s, %s, %s, %s)
    #         """, [biometric_id, emp_id, punch_datetime_iso, punch_time_iso])


    #     return Response({
    #         "status": "Clock-In recorded",
    #         "punch_time": punch_datetime_iso,
    #         "late_mark": late_mark,
    #         "is_half_day": is_half_day,
    #         "half_day_reason": half_day_reason if half_day_reason else "N/A"
    #     })

    # def _handle_clock_out(self, emp_id, employee_hub_name, attendance_date, punch_time_local, punch_time_iso,
    #                       punch_datetime_iso, punch_datetime_local, location):
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             SELECT ci_biomatric_id, clock_in, is_half_day, late_mark, status, half_day_reason
    #             FROM ci_biomatric_data 
    #             WHERE emp_id = %s AND attendance_date = %s AND state_in_out = 'in'
    #             ORDER BY ci_biomatric_id DESC LIMIT 1
    #             """,
    #             [emp_id, attendance_date],
    #         )
    #         row1 = cursor.fetchone()

    #         cursor.execute(
    #             """
    #             SELECT id
    #             FROM ci_biomatric_data_2
    #             WHERE emp_id = %s AND login_date = %s 
    #             ORDER BY ci_biomatric_id DESC LIMIT 1
    #             """,
    #             [emp_id, attendance_date],
    #         )
    #         row2 = cursor.fetchone()

    #     if not row1:
    #         return Response(
    #             {"error": "No clock-in found for today"}, 
    #             status=status.HTTP_404_NOT_FOUND
    #         )

    #     # biomatric_id, clock_in_data, current_half_day, late_mark, attendance_status, current_half_day_reason = row1
    #     biomatric_id1 = row1[0]
    #     biomatric_id2 = row2[0]


    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             UPDATE ci_biomatric_data
    #             SET clock_out = %s, clock_out_location = %s
    #             WHERE ci_biomatric_id = %s  
    #             """,
    #             [punch_time_iso, location, biomatric_id1],
    #         )

    #         cursor.execute("""
    #             UPDATE ci_biomatric_data_2
    #             SET clock_out = %s
    #             WHERE ci_biomatric_id = %s
    #             ORDER BY id DESC LIMIT 1
    #         """, [punch_time_iso, biomatric_id2])

    #     return Response({
    #         "status": "Clock-Out recorded",
    #         "punch_time": punch_datetime_iso
    #     })
    
    # def _deduct_half_day_leave(self, emp_id):
    #     now = datetime.now()
    #     year = now.year
        
    #     with connection.cursor() as cursor:
    #         cursor.execute(
    #             """
    #             UPDATE ci_leave_balance
    #             SET balance_leave = balance_leave - 0.5
    #             WHERE employee_id = %s AND year = %s AND status = 'Y' 
    #             AND leave_type_id = 184 AND balance_leave >= 0.5
    #             """,
    #             [emp_id, year]
    #         )
            
    #         if cursor.rowcount == 0:
    #             cursor.execute(
    #                 """
    #                 SELECT balance_leave
    #                 FROM ci_leave_balance
    #                 WHERE employee_id = %s AND year = %s AND status = 'Y' AND leave_type_id = 184
    #                 """,
    #                 [emp_id, year]
    #             )
    #             result = cursor.fetchone()
                
    #             if result and result[0] < 0.5:
    #                 return 'H' 
        
    #     return 'P'

    # def _parse_time_data(self, time_data):
    #     if isinstance(time_data, timedelta):
    #         total_seconds = int(time_data.total_seconds())
    #         hours, remainder = divmod(total_seconds, 3600)
    #         minutes, seconds = divmod(remainder, 60)
    #         return time(hours, minutes, seconds)
    #     else:
    #         return datetime.strptime(str(time_data), "%H:%M:%S").time()


class BasicInformation(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                query = """SELECT 
    id,
    first_name,
    middle_name,
    last_name,
    contact_number,
    gender,
    employee_id,
    date_of_birth,
    marital_status,
    ec.category_name as state,
    eh.employee_hub_name,
    city,
    zipcode,
    religion_id,
    blood_group,
    country,
    citizenship_id,
    address_1,
    address_2
FROM
    ci_erp_users ceu
        LEFT JOIN
    ci_erp_users_details ceud ON ceu.id = ceud.user_id
        LEFT JOIN
    ci_erp_constants ec ON ceu.state = ec.constants_id
        LEFT JOIN
    ci_employee_hub eh ON ceu.employee_hub_id = eh.employee_hub_id
WHERE
    id = %s;"""

                c.execute(query, [user_id])
                columns = [col[0] for col in c.description]
                data = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": data}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class HolidayList(EmployeeOnlyView):

    def get(self, request):
        from_date = "2024-01-01"
        to_date = "2024-12-31"

        try:
            with connection.cursor() as c:
                c.execute(
                    """select event_name as event_title, start_date, end_date, is_publish as status from ci_holidays where start_date  >= %s and end_date <= %s""",
                    [from_date, to_date],
                )
                rows = c.fetchall()

                response = [
                    {
                        "event_title": row[0],
                        "start_date": row[1],
                        "end_date": row[2],
                    }
                    for row in rows
                ]

                return Response(
                    {"status": "success", "data": response}, status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProjectList(EmployeeOnlyView):

    def get(self, request, user_id, type):

        if not user_id or not type:
            return Response(
                {"status": "error", "message": "user id or type is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                if type == 1:
                    query = """SELECT 
                                    CASE
                                        WHEN status = 0 THEN 'not_started'
                                        WHEN status = 1 THEN 'total_completed'
                                        WHEN status = 2 THEN 'total_in_progress'
                                        WHEN status = 3 THEN 'total_on_hold'
                                    END AS project_status,
                                    COUNT(*) AS total
                                FROM
                                    ci_projects
                                WHERE
                                    FIND_IN_SET(%s, REPLACE(REPLACE(REPLACE(assigned_to, '[', ''), ']', ''), ' ', '')) > 0
                                GROUP BY project_status;"""

                    c.execute(query, [user_id])
                    rows = c.fetchall()

                    response = {
                        "total_completed": 0,
                        "total_in_progress": 0,
                        "not_started": 0,
                        "total_on_hold": 0,
                    }

                    for row in rows:
                        status_label = row[0]
                        count = row[1]
                        response[status_label] = count

                elif type == 2:
                    query = """SELECT 
                            	p.project_id,
                                p.title,
                                CONCAT(c.first_name, ' ', c.last_name) AS client_name,
                                DATE_FORMAT(p.start_date, "%%d-%%m-%%Y"),
                                DATE_FORMAT(p.end_date, "%%d-%%m-%%Y"),
                                GROUP_CONCAT(CONCAT(u.first_name, ' ', u.last_name)) AS team_name,
                                GROUP_CONCAT(u.profile_photo) AS team_profile_photo,
                                priority,
                                project_progress
                            FROM
                                ci_projects p
                                    LEFT JOIN
                                ci_erp_users u ON FIND_IN_SET(u.id,
                                        REPLACE(REPLACE(REPLACE(p.assigned_to, '[', ''),
                                                ']',
                                                ''),
                                            ' ',
                                            ''))
                                    LEFT JOIN
                                ci_erp_users c ON c.id = p.client_id
                            WHERE
                                FIND_IN_SET(%s, REPLACE(REPLACE(REPLACE(p.assigned_to, '[', ''), ']', ''), ' ', '')) > 0
                            GROUP BY p.project_id;"""

                    c.execute(query, [user_id])
                    rows = c.fetchall()

                    response = [
                        {
                            "project": row[1],
                            "client": row[2],
                            "start_date": row[3],
                            "end_date": row[4],
                            "team": row[5],
                            "team_profile_photo": row[6],
                            "priority": row[7],
                            "progress": row[8],
                        }
                        for row in rows
                    ]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProjectDetails(EmployeeOnlyView):

    def get(self, request, user_id):

        if not user_id:
            return Response(
                {"status": "error", "message": "user id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                query = """SELECT 
                        	p.project_id,
                            p.title,
                            CONCAT(c.first_name, ' ', c.last_name) AS client_name,
                            budget_hours as estimated_hour,
                            priority,
                            DATE_FORMAT(p.start_date, "%%d-%%m-%%Y"),
                            DATE_FORMAT(p.end_date, "%%d-%%m-%%Y"),
                            GROUP_CONCAT(CONCAT(u.first_name, ' ', u.last_name)) AS team_name,
                            GROUP_CONCAT(u.profile_photo) AS team_profile_photo,
                            summary,
                            description,
                            project_progress,
                            p.company_id
                        FROM
                            ci_projects p
                                LEFT JOIN
                            ci_erp_users u ON FIND_IN_SET(u.id,
                                    REPLACE(REPLACE(REPLACE(p.assigned_to, '[', ''),
                                            ']',
                                            ''),
                                        ' ',
                                        ''))
                                LEFT JOIN
                            ci_erp_users c ON c.id = p.client_id
                        WHERE
                            FIND_IN_SET(%s, REPLACE(REPLACE(REPLACE(p.assigned_to, '[', ''), ']', ''), ' ', '')) > 0
                        GROUP BY p.project_id;"""
                c.execute(query, [user_id])
                rows = c.fetchall()
                response = [
                    {
                        "title": row[1],
                        "client": row[2],
                        "estimated_hour": row[3],
                        "priority": row[4],
                        "start_date": row[5],
                        "end_date": row[6],
                        "team_name": row[7],
                        "team_profile_photo": row[8],
                        "total_hours": "00:00",
                        "summary": row[9],
                        "description": row[10],
                        "company_id": row[11],
                    }
                    for row in rows
                ]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProjectDiscussion(EmployeeOnlyView):

    def post(self, request):

        user_id = request.data.get("user_id")
        desc = request.data.get("desc")
        company_id = request.data.get("company_id")
        project_id = request.data.get("project_id")

        if not user_id or not desc or not company_id or not project_id:
            return Response(
                {"status": "error", "message": "some required fields are missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:
                    query = """select discussion_text from ci_projects_discussion where employee_id = %s and company_id = %s"""

                    c.execute(query, [user_id, company_id])
                    row = c.fetchone()

                    if row:
                        # Update if exists
                        update_query = """
                            UPDATE ci_projects_discussion 
                            SET discussion_text = %s 
                            WHERE employee_id = %s AND company_id = %s
                        """
                        c.execute(update_query, [desc, user_id, company_id])
                        message = "Project discussion updated successfully"
                    else:
                        # Insert if not exists
                        insert_query = """
                            INSERT INTO ci_projects_discussion (company_id, project_id, employee_id, discussion_text) 
                            VALUES (%s, %s, %s, %s)
                        """
                        c.execute(insert_query, [company_id, project_id, user_id, desc])
                        message = "Project discussion added successfully"

            return Response(
                {"status": "success", "message": message},
                status=status.HTTP_202_ACCEPTED,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProjectAttachFile(EmployeeOnlyView):

    def post(self, request):
        user_id = request.data.get("user_id")
        file_title = request.data.get("file_title")
        doc = request.FILES.get("attachment_file")  # Expecting only one file
        company_id = request.data.get("company_id")
        project_id = request.data.get("project_id")

        if not user_id or not file_title or not doc:
            return Response(
                {"status": "error", "message": "Some fields are missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                # Fetch username
                find_username = """SELECT CONCAT(first_name, last_name) FROM ci_erp_users WHERE id = %s"""
                c.execute(find_username, [user_id])
                row = c.fetchone()
                username = row[0] if row else "unknown"

                # Ensure media/documents folder exists
                upload_folder = os.path.join(settings.MEDIA_ROOT, "documents")
                os.makedirs(upload_folder, exist_ok=True)

                # Save file
                fs = FileSystemStorage(location=upload_folder)
                original_filename = doc.name
                file_ext = os.path.splitext(original_filename)[1]
                new_filename = f"{user_id}_{file_title.replace(' ', '_')}{file_ext}"
                saved_filename = fs.save(new_filename, doc)

                # Optional: full file path or URL
                file_url = f"/hrms-backend/media/documents/{quote(saved_filename)}"

                # Insert into DB
                c.execute(
                    """INSERT INTO ci_projects_files (company_id, project_id, employee_id, file_title, attachment_file) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    [company_id, project_id, user_id, file_title, saved_filename],
                )

            return Response(
                {
                    "status": "success",
                    "message": "File uploaded successfully",
                    "file": saved_filename,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Payroll(EmployeeOnlyView):

    def get(self, request, user_id, type):

        if not user_id or not type:
            return Response(
                {"status": "error", "message": "user id or type is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                if type == 1:
                    query = """select employee_id, designation_name, CONCAT(first_name, last_name) as emp_name
                                from ci_erp_users u left join ci_erp_users_details ud on u.id = ud.user_id join ci_designations d on ud.designation_id = d.designation_id
                                where u.id = %s;"""

                    c.execute(query, [user_id])

                    rows = c.fetchall()
                    response = [
                        {
                            "emp_id": row[0],
                            "designation_name": row[1],
                            "emp_name": row[2],
                            "uan_no": 0,
                        }
                        for row in rows
                    ]

                elif type == 2:
                    query = """select salary_month, net_salary
                                from ci_payslips
                                where staff_id = %s;"""

                    c.execute(query, [user_id])
                    rows = c.fetchall()

                    response = [
                        {
                            "salary_month": row[0],
                            "net_salary": row[1],
                            "pay_date": None,
                        }
                        for row in rows
                    ]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Policies(EmployeeOnlyView):

    def get(self, request):

        try:
            with connection.cursor() as c:

                query = """select title, p.created_at, CONCAT(first_name,' ', last_name) as added_by from ci_policies p join ci_erp_users u on p.added_by = u.id group by title ORDER by p.created_at desc;"""
                c.execute(query)
                rows = c.fetchall()

                return Response(
                    {"status": "success", "data": rows}, status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

     
class DashboardAttendance(APIView):

    def get(self, request, employee_id):

        current_date = date.today().strftime("%Y-%m-%d")
        # current_date = '2025-10-01'

        if not employee_id:
            return Response({"status":"error","message": "employee_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with connection.cursor() as c:
                c.execute("""select clock_in, clock_out from ci_biomatric_data_2 where login_date = %s and emp_id = %s order by id desc limit 1""", [current_date, employee_id])

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response({"status":"success","data": response}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status":"error","message": f"An error occured: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class MyAttendanceAPIView(APIView):
#     def get(self, request, empid):
#         try:
#             with connection.cursor() as cursor:
#                 # Get user_id of the requested empid
#                 cursor.execute("""
#                     SELECT user_id FROM ci_erp_users_details
#                     WHERE employee_id = %s
#                     LIMIT 1
#                 """, [empid])
#                 user_row = cursor.fetchone()

#                 if not user_row:
#                     return Response({'error': 'Employee not found'}, status=404)

#                 user_id = user_row[0]

#                 # Get all employees under this manager or self
#                 cursor.execute("""
#                     SELECT ced.employee_id, ceu.first_name, ceu.last_name, ceu.email
#                     FROM ci_erp_users_details ced
#                     JOIN ci_erp_users ceu ON ceu.id = ced.user_id
#                     WHERE ced.manager = %s OR ced.employee_id = %s
#                 """, [user_id, empid])
#                 employees = cursor.fetchall()

#                 if not employees:
#                     return Response({'message': 'No subordinates found'}, status=200)

#                 emp_data_map = {} 
#                 emp_ids = []

#                 for employee_id, first_name, last_name, email in employees:
#                     full_name = f"{first_name} {last_name}".strip()
#                     emp_data_map[employee_id] = {
#                         'employee_name': full_name,
#                         'email': email
#                     }
#                     emp_ids.append(employee_id)

#                 # Get attendance records for October 2024 only
#                 # For current date only
#                 today_str = date.today().strftime('%Y-%m-%d')

#                 cursor.execute("""
#                     SELECT emp_id, attendance_date, attendance_status, clock_in,
#                            clock_out, late_mark, early_mark, total_work
#                     FROM ci_biomatric_data
#                     WHERE emp_id IN %s
#                     AND attendance_date = %s
#                 """, [tuple(emp_ids), today_str])
#                 records = cursor.fetchall()

#                 results = []
#                 for row in records:
#                     emp_id, attendance_date, status, clock_in, clock_out, late_mark, early_mark, total_work = row

#                     emp_info = emp_data_map.get(emp_id, {})
#                     results.append({
#                         'employee_name': emp_info.get('employee_name', ''),
#                         'email': emp_info.get('email', ''),
#                         'attendance_date': attendance_date,
#                         'status': status,
#                         'clock_in': clock_in or '00:00',
#                         'clock_out': clock_out or '00:00',
#                         'late_mark': late_mark or '00:00',
#                         'early_mark': early_mark or '00:00',
#                         'total_work': total_work or '00:00'
#                     })

#                 # Sort so that requested empid shows first
#                 results.sort(key=lambda x: x['email'] != emp_data_map[empid]['email'])

#                 return Response({'attendance': results}, status=200)

#         except Exception as e:
#             return Response({'error': str(e)}, status=500)

# class MonthlyReportView(APIView):
#     def post(self, request):
#         try:
#             employee_id = request.data.get('employee_id')
#             month_str = request.data.get('month')  # Format: YYYY-MM

#             if not employee_id or not month_str:
#                 return Response({'error': 'employee_id and month are required'}, status=400)
            
#             if month_str:
#                 year, month = map(int, month_str.split('-'))
#             else:
#                 now = datetime.now()
#                 year = now.year
#                 month = now.month

#             # try:
#             #     month_date = datetime.strptime(month, '%Y-%m')
#             # except ValueError:
#             #     return Response({'error': 'Invalid month format. Use YYYY-MM'}, status=400)

#             # today = datetime.today()
#             # is_current_month = today.year == month_date.year and today.month == month_date.month
#             # day_limit = today.day if is_current_month else 31

#             # start_date = f"{month}-01"
#             # end_date = f"{month}-{day_limit:02d}"

#             # with connection.cursor() as cursor:
#         #         cursor.execute("""
#         #             SELECT attendance_date, clock_in, clock_out, total_work, attendance_status
#         #             FROM ci_biomatric_data
#         #             WHERE emp_id = %s
#         #             AND attendance_date BETWEEN %s AND %s
#         #             ORDER BY attendance_date ASC
#         #         """, [employee_id, start_date, end_date])

#         #         rows = cursor.fetchall()

#         #     result = []
#         #     for row in rows:
#         #         attendance_date, clock_in, clock_out, total_work, attendance_status = row

#         #         # Convert string to datetime.date if necessary
#         #         if isinstance(attendance_date, str):
#         #             attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()

#         #         day_name = attendance_date.strftime('%A')
#         #         date_str = attendance_date.strftime('%Y-%m-%d')

#         #         # Format clock in/out if available
#         #         def fmt_time(val):
#         #             try:
#         #                 return datetime.strptime(val, '%H:%M:%S').strftime('%I:%M %p').lstrip("0").lower() if val else ""
#         #             except Exception:
#         #                 return val  # return as-is if not in expected format

#         #         result.append({
#         #             "day": day_name,
#         #             "date": date_str,
#         #             "status": attendance_status or "Absent",
#         #             "clock_in": fmt_time(clock_in),
#         #             "clock_out": fmt_time(clock_out),
#         #             "total_work": total_work or ""
#         #         })

#         #     return Response(result, status=200)

#         # except Exception as e:
#         #     return Response({'error': str(e)}, status=500)

#             with connection.cursor() as c:
#                 c.execute(
#                     """
#                     SELECT 
#                         DATE_FORMAT(STR_TO_DATE(login_date, '%%Y-%%m-%%d'), '%%W') AS day,
#                         DATE_FORMAT(STR_TO_DATE(login_date, '%%Y-%%m-%%d'), '%%d-%%m-%%Y') AS date,
#                         CASE 
#                             WHEN MAX(attendance_status) = 'Present' THEN 'Present'
#                             ELSE 'Absent'
#                         END AS status,
#                         DATE_FORMAT(MIN(TIME(clock_in)), '%%H:%%i') AS clock_in,
#                         DATE_FORMAT(MAX(TIME(clock_out)), '%%H:%%i') AS clock_out
#                     FROM ci_biomatric_data
#                     WHERE 
#                         emp_id = %s
#                         AND YEAR(STR_TO_DATE(login_date, '%%Y-%%m-%%d')) = %s
#                         AND MONTH(STR_TO_DATE(login_date, '%%Y-%%m-%%d')) = %s
#                     GROUP BY STR_TO_DATE(login_date, '%%Y-%%m-%%d')
#                     ORDER BY STR_TO_DATE(login_date, '%%Y-%%m-%%d');
#                     """,
#                     [employee_id, year, month],
#                 )

#                 columns = [col[0] for col in c.description]
#                 response = [dict(zip(columns, row)) for row in c.fetchall()]

#             return Response(
#                 {"status": "success", "data": response}, status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

class AssetsInventory(APIView):
 
    def get(self, request):
 
        with connection.cursor() as c:
 
            # 1. Get total purchased
            c.execute("""
                SELECT category_id, brand_id, product_id, SUM(quantity) AS total_purchased
                FROM ci_assets_instock
                GROUP BY category_id, brand_id, product_id
            """)
            purchased_rows = c.fetchall()
 
            # Convert to dict for easy lookup
            purchased_map = {}
            for row in purchased_rows:
                category_id, brand_id, product_id, total_purchased = row
                purchased_map[(category_id, brand_id, product_id)] = {
                    "Category": category_id,
                    "Brand": brand_id,
                    "Product": product_id,
                    "TotalPurchased": total_purchased,
                    "Assigned": 0,
                    "Returned": 0
                }
 
            # 2. Get assigned and returned
            c.execute("""
                SELECT assets_category_id AS category_id, brand_id, product_id,
                       SUM(CASE WHEN returned = 'N' THEN quantity ELSE 0 END) AS assigned,
                       SUM(CASE WHEN returned = 'Y' THEN quantity ELSE 0 END) AS returned
                FROM ci_assets
                GROUP BY assets_category_id, brand_id, product_id
            """)
            assets_rows = c.fetchall()
 
            for row in assets_rows:
                category_id, brand_id, product_id, assigned, returned = row
                key = (category_id, brand_id, product_id)
 
                # if key not in purchased_map:
                #     purchased_map[key] = {
                #         "Category": category_id,
                #         "Brand": brand_id,
                #         "Product": product_id,
                #         "TotalPurchased": 0,
                #         "Assigned": 0,
                #         "Returned": 0
                #     }
 
                if key in purchased_map:
 
                    purchased_map[key]["Assigned"] = assigned or 0
                    purchased_map[key]["Returned"] = returned or 0
 
        # 3. Calculate in stock
        result = []
        for key, val in purchased_map.items():
            total = val["TotalPurchased"]
            assigned = val["Assigned"]
            returned = val["Returned"]
 
            # in_stock = total - assigned + returned
            in_stock = total - assigned
            in_stock = max(0, in_stock)
 
            result.append({
                "Category": val["Category"],
                "Brand": val["Brand"],
                "Product": val["Product"],
                "TotalPurchased": total,
                "Assigned": assigned,
                "Returned": returned,
                "InStock": in_stock
            })
 
        return Response(result, status=status.HTTP_200_OK)
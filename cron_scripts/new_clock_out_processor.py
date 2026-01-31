

# WORKING COMMENTED SCRIPT

# import os
# os.environ['TZ'] = 'Asia/Kolkata'
# import time
# time.tzset()

# import sys
# import django
# from datetime import datetime, timedelta, time as datetime_time
# from django.db import connection, transaction
# import logging
# import pytz
# from django.utils import timezone

# def setup_django():
#     """Setup Django environment for standalone script"""
#     project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     if project_root not in sys.path:
#         sys.path.append(project_root)
    
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
#     django.setup()

# setup_django()

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[logging.StreamHandler()]
# )
# logger = logging.getLogger(__name__)

# class AttendanceCronProcessor:
    
#     def __init__(self):
#         self.processed_count = 0
#         self.error_count = 0
#         self.holiday_count = 0
        
#     def execute_query(self, query, params=None, fetch=True):
#         """Execute query using Django's connection"""
#         with connection.cursor() as cursor:
#             cursor.execute(query, params or [])
#             if fetch:
#                 return cursor.fetchall()
#             else:
#                 return cursor.rowcount
                
#     def get_work_timings(self, employee_hub_name, employee_hub_id, attendance_date):
#         day_name = attendance_date.strftime('%A').lower()
        
#         query = f"""
#             SELECT {day_name}_in_time, {day_name}_out_time
#             FROM ci_office_shifts 
#             WHERE employee_hub_id = %s
#             ORDER BY office_shift_id DESC
#             LIMIT 1
#         """
        
#         result = self.execute_query(query, [employee_hub_id])
        
#         if result and result[0][0] and result[0][1]:
#             try:
#                 in_time_str = result[0][0]
#                 out_time_str = result[0][1]
                
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

#                 if in_time == 'Holiday' or out_time == 'Holiday':
#                     raise ValueError("Shift is marked as holiday")
                
#                 return in_time, out_time
                
#             except (ValueError, TypeError) as e:
#                 if "holiday" in str(e).lower():
#                     raise ValueError("Shift is marked as holiday")
#                 else:
#                     logger.warning(f"Error parsing shift times for employee_hub {employee_hub_id}: {e}")
#                     return datetime_time(9, 30), datetime_time(18, 0)
#         else:
#             return datetime_time(9, 30), datetime_time(18, 0)
    
#     def get_current_month_late_marks(self, emp_id, attendance_date):
#         query = """
#             SELECT SUM(late_mark_count) FROM ci_biomatric_data
#             WHERE emp_id = %s 
#             AND MONTH(attendance_date) = MONTH(%s) 
#             AND YEAR(attendance_date) = YEAR(%s)
#         """
        
#         result = self.execute_query(query, [emp_id, attendance_date, attendance_date])
#         return result[0][0] if result and result[0][0] is not None else 0
    
#     def parse_time_data(self, time_data):
#         """Parse time data from various formats"""
#         if isinstance(time_data, timedelta):
#             total_seconds = int(time_data.total_seconds())
#             hours, remainder = divmod(total_seconds, 3600)
#             minutes, seconds = divmod(remainder, 60)
#             return datetime_time(hours, minutes, seconds)
#         else:
#             return datetime.strptime(str(time_data), "%H:%M:%S").time()
        
#     def deduct_half_day_leave(self, emp_id):
#         """Deduct half day leave and return attendance status"""
#         now = datetime.now()
#         year = now.year
        
#         update_query = """
#             UPDATE ci_leave_balance
#             SET balance_leave = balance_leave - 0.5
#             WHERE employee_id = %s AND year = %s AND status = 'Y' 
#             AND leave_type_id = 184 AND balance_leave >= 0.5
#         """
        
#         rowcount = self.execute_query(update_query, [emp_id, year], fetch=False)
        
#         if rowcount == 0:
#             check_query = """
#                 SELECT balance_leave
#                 FROM ci_leave_balance
#                 WHERE employee_id = %s AND year = %s AND status = 'Y' AND leave_type_id = 184
#             """
#             result = self.execute_query(check_query, [emp_id, year])
            
#             if result and result[0][0] < 0.5:
#                 return 'H'
        
#         return 'P'
    
#     def get_employees_to_process(self, target_date):
#         """Get all employees with clock-in but need processing"""
#         query = """
#             SELECT 
#                 bd.ci_biomatric_id,
#                 bd.emp_id,
#                 bd.clock_in,
#                 bd.clock_out,
#                 bd.is_half_day as current_half_day,
#                 bd.half_day_reason as current_half_day_reason,
#                 bd.status as attendance_status,
#                 COALESCE(eh.employee_hub_name, '') AS employee_hub_name,
#                 bd.attendance_date,
#                 bd.late_mark,
#                 bd.late_mark_count,
#                 COALESCE(eh.employee_hub_id, '0') AS employee_hub_id
#             FROM ci_biomatric_data bd
#             INNER JOIN ci_erp_users u ON bd.userid = u.id
#             LEFT JOIN ci_employee_hub eh ON u.employee_hub_id = eh.employee_hub_id
#             WHERE bd.attendance_date = %s 
#             AND bd.state_in_out = 'in'
#             AND bd.clock_out IS NOT NULL
#             ORDER BY bd.emp_id, bd.ci_biomatric_id DESC
#         """
        
#         rows = self.execute_query(query, [target_date])
        
#         employees_data = {}
#         for row in rows:
#             emp_id = row[1]
#             if emp_id not in employees_data:
#                 employees_data[emp_id] = {
#                     'biomatric_id': row[0],
#                     'emp_id': row[1],
#                     'clock_in': row[2],
#                     'clock_out': row[3],
#                     'current_half_day': row[4],
#                     'current_half_day_reason': row[5],
#                     'attendance_status': row[6],
#                     'employee_hub_name': row[7],
#                     'attendance_date': row[8],
#                     'late_mark': row[9],
#                     'late_mark_count': row[10],
#                     'employee_hub_id': row[11],
#                 }
        
#         return list(employees_data.values())
        
#     def process_employee_attendance(self, employee_data):
#         """Process individual employee attendance calculations"""
#         try:
#             emp_id = employee_data['emp_id']
#             biomatric_id = employee_data['biomatric_id']
#             clock_in_data = employee_data['clock_in']
#             clock_out_time = employee_data['clock_out']
#             current_half_day = employee_data['current_half_day']
#             current_half_day_reason = employee_data['current_half_day_reason']
#             attendance_status = employee_data['attendance_status']
#             employee_hub_name = employee_data['employee_hub_name']
#             attendance_date = employee_data['attendance_date']
#             current_late_mark = employee_data['late_mark']
#             current_late_mark_count = employee_data['late_mark_count']
#             employee_hub_id = employee_data['employee_hub_id']
            
#             clock_in_time_obj = self.parse_time_data(clock_in_data)
#             clock_in_datetime = datetime.combine(attendance_date, clock_in_time_obj)
            
#             if isinstance(clock_out_time, str):
#                 clock_out_time_obj = datetime.strptime(clock_out_time, "%H:%M:%S").time()
#             else:
#                 clock_out_time_obj = clock_out_time
            
#             clock_out_datetime = datetime.combine(attendance_date, clock_out_time_obj)
            
#             if clock_out_datetime <= clock_in_datetime:
#                 logger.warning(f"Invalid clock times for emp_id {emp_id}: clock_out <= clock_in")
#                 return False
            
#             total_work = clock_out_datetime - clock_in_datetime
#             total_work_decimal = total_work.total_seconds() / 3600
            
#             hours = int(total_work_decimal)
#             minutes = int((total_work_decimal - hours) * 60)
#             total_work_str = f"{hours:02}:{minutes:02}"
            
#             try:
#                 _, end_time = self.get_work_timings(employee_hub_name, employee_hub_id, attendance_date)
#             except ValueError as e:
#                 if "holiday" in str(e).lower():
#                     logger.info(f"Skipping emp_id {emp_id}: Shift is marked as holiday")
#                     return "HOLIDAY"
#                 else:
#                     logger.error(f"Error getting work timings for emp_id {emp_id}: {str(e)}")
#                     return False
            
#             end_datetime = datetime.combine(attendance_date, end_time)
#             clock_out_punch_datetime = datetime.combine(attendance_date, clock_out_time_obj)
            
#             late_mark = "N"
#             early_mark = "N"
#             reasons_list = [current_half_day_reason] if current_half_day_reason else []
            
#             if 8.25 <= total_work_decimal < 8.50:
#                 late_mark = "Y"

#             if late_mark == "Y":
#                 late_mark_count = self.get_current_month_late_marks(emp_id, attendance_date)
#             else:
#                 late_mark_count = 0
            
#             if clock_out_punch_datetime < end_datetime:
#                 early_mark = "Y"
#                 reasons_list.append("Early Punch-Out")
            
#             if total_work_decimal < 8.25:
#                 reasons_list.append("Insufficient Working Hours")
            
#             if clock_out_time_obj < datetime_time(13, 0):
#                 reasons_list.append("Punched Before 1 PM")

#             if late_mark == 'Y':
#                 if late_mark_count >= 2:
#                     is_half_day = "Y"
#                     reasons_list.append("Exceeded Late Mark Limit")
                    
#                     reset_query = """
#                         UPDATE ci_biomatric_data
#                         SET late_mark_count = 0
#                         WHERE emp_id = %s
#                         AND MONTH(attendance_date) = MONTH(%s)
#                         AND YEAR(attendance_date) = YEAR(%s)
#                     """
#                     self.execute_query(reset_query, [emp_id, attendance_date, attendance_date], fetch=False)
#                     late_mark_count = 0
#                 else:
#                     late_mark_count += 1
            
#             is_half_day = "Y" if reasons_list else "N"
#             half_day_reason = ", ".join(reasons_list) if reasons_list else None
            
#             if is_half_day == 'Y' and current_half_day == 'N':
#                 attendance_status = self.deduct_half_day_leave(emp_id)
            
#             mark_half_day = is_half_day if current_half_day == 'N' else current_half_day
#             mark_late_mark = late_mark if current_late_mark == 'N' else current_late_mark
#             mark_late_count = late_mark_count if late_mark == 'Y' else current_late_mark_count
            
#             update_query = """
#                 UPDATE ci_biomatric_data
#                 SET state_in_out = %s, total_work = %s, late_mark = %s, early_mark = %s, 
#                     is_half_day = %s, half_day_reason = %s, late_mark_count = %s, 
#                     status = %s, reason = %s
#                 WHERE ci_biomatric_id = %s
#             """
            
#             rowcount = self.execute_query(
#                 update_query,
#                 [
#                     "out", total_work_str, mark_late_mark, early_mark,
#                     mark_half_day, half_day_reason, mark_late_count, 
#                     attendance_status, "Check OUT", biomatric_id
#                 ],
#                 fetch=False
#             )
            
#             if rowcount > 0:
#                 logger.info(f"✅ Updated biomatric_id={biomatric_id} for emp_id={emp_id}")
#             else:
#                 logger.info(f"⚠️ No rows updated for biomatric_id={biomatric_id}")
            
#             logger.info(f"Processed emp_id {emp_id}: total_work={total_work_decimal:.2f}h, half_day={is_half_day}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error processing emp_id {emp_id}: {str(e)}")
#             return False
        
#     def run_daily_processing_detailed(self, target_date=None):
#         """Enhanced version with detailed tracking"""
#         if target_date is None:
#             target_date = datetime.now().date()
        
#         logger.info(f"Starting attendance processing for date: {target_date}")
        
#         results = {
#             'processed': [],
#             'failed': [],
#             'holidays': [],
#             'skipped': []
#         }
        
#         try:
#             employees_to_process = self.get_employees_to_process(target_date)
#             total_employees = len(employees_to_process)
            
#             logger.info(f"Found {total_employees} employees to process")
            
#             batch_size = 100
            
#             with transaction.atomic():
#                 for i in range(0, total_employees, batch_size):
#                     batch = employees_to_process[i:i + batch_size]
                    
#                     for employee_data in batch:
#                         emp_id = employee_data.get('emp_id', 'Unknown')
                        
#                         try:
#                             result = self.process_employee_attendance(employee_data)
                            
#                             if result == "HOLIDAY":
#                                 results['holidays'].append({
#                                     'emp_id': emp_id,
#                                     'reason': 'Shift marked as holiday',
#                                     'hub_name': employee_data.get('employee_hub_name', 'Unknown')
#                                 })
#                             elif result is True:
#                                 results['processed'].append({'emp_id': emp_id, 'status': 'success'})
#                             else:
#                                 results['failed'].append({'emp_id': emp_id, 'reason': 'Processing returned False'})
                                
#                         except Exception as e:
#                             results['failed'].append({'emp_id': emp_id, 'reason': f'Exception: {str(e)}'})
                    
#                     processed_so_far = min(i + batch_size, total_employees)
#                     logger.info(f"Processed batch: {processed_so_far}/{total_employees} employees")
            
#             self.processed_count = len(results['processed'])
#             self.error_count = len(results['failed'])
#             self.holiday_count = len(results['holidays'])
            
#             logger.info(f"Processing completed. Success: {self.processed_count}, "
#                     f"Errors: {self.error_count}, Holidays: {self.holiday_count}")
            
#             if results['failed']:
#                 logger.warning("Failed employees:")
#                 for failed in results['failed'][:10]:
#                     logger.warning(f"  - {failed['emp_id']}: {failed['reason']}")
#                 if len(results['failed']) > 10:
#                     logger.warning(f"  ... and {len(results['failed']) - 10} more failures")
            
#             results.update({
#                 'total_employees': total_employees,
#                 'errors': self.error_count,
#                 'success_rate': (self.processed_count / total_employees * 100) if total_employees > 0 else 0
#             })
            
#             return results
            
#         except Exception as e:
#             logger.error(f"Critical error in daily processing: {str(e)}")
#             raise


# def main():
#     """Main entry point for the cron script"""
#     try:
#         processor = AttendanceCronProcessor()
#         result = processor.run_daily_processing_detailed()

#         logger.info(f"Final Summary - Total: {result['total_employees']}, "
#                    f"Processed: {len(result['processed'])}, "
#                    f"Errors: {result['errors']}, "
#                    f"Holidays: {len(result['holidays'])}, "
#                    f"Success Rate: {result['success_rate']:.2f}%")
        
#         if result['errors'] > 0:
#             error_rate = (result['errors'] / result['total_employees'] * 100) if result['total_employees'] > 0 else 0
            
#             if error_rate > 10:
#                 logger.error(f"High error rate: {error_rate:.2f}% - Critical failure")
#                 sys.exit(2)
#             else:
#                 logger.warning(f"Completed with {result['errors']} errors ({error_rate:.2f}%)")
#                 sys.exit(1)
#         else:
#             logger.info("Processing completed successfully")
#             sys.exit(0)
            
#     except Exception as e:
#         logger.error(f"Script failed: {str(e)}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()


import os
os.environ['TZ'] = 'Asia/Kolkata'
import time
time.tzset()

import sys
import django
from datetime import datetime, timedelta, time as datetime_time
from django.db import connection, transaction
import logging
import pytz
from django.utils import timezone

def setup_django():
    """Setup Django environment for standalone script"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()

setup_django()

# Custom formatter to use IST timezone
class ISTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Convert the record time to IST
        dt = datetime.fromtimestamp(record.created, tz=pytz.timezone('Asia/Kolkata'))
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime('%Y-%m-%d %H:%M:%S')
        return s

    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStackInfo(record.stack_info)
        return s

# Configure logging with IST timezone
handler = logging.StreamHandler()
formatter = ISTFormatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class AttendanceCronProcessor:
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.holiday_count = 0
        
    def execute_query(self, query, params=None, fetch=True, commit=False):
        """Execute query using Django's connection with explicit commit option"""
        with connection.cursor() as cursor:
            cursor.execute(query, params or [])
            
            # Commit if this is an UPDATE/INSERT/DELETE query
            if commit:
                transaction.commit()
            
            if fetch:
                return cursor.fetchall()
            else:
                return cursor.rowcount
                
    def get_work_timings(self, employee_hub_name, employee_hub_id, attendance_date):
        day_name = attendance_date.strftime('%A').lower()
        
        query = f"""
            SELECT {day_name}_in_time, {day_name}_out_time
            FROM ci_office_shifts 
            WHERE employee_hub_id = %s
            ORDER BY office_shift_id DESC
            LIMIT 1
        """
        
        result = self.execute_query(query, [employee_hub_id])
        
        if result and result[0][0] and result[0][1]:
            try:
                in_time_str = result[0][0]
                out_time_str = result[0][1]
                
                if isinstance(in_time_str, str):
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

                if in_time == 'Holiday' or out_time == 'Holiday':
                    raise ValueError("Shift is marked as holiday")
                
                return in_time, out_time
                
            except (ValueError, TypeError) as e:
                if "holiday" in str(e).lower():
                    raise ValueError("Shift is marked as holiday")
                else:
                    logger.warning(f"Error parsing shift times for employee_hub {employee_hub_id}: {e}")
                    return datetime_time(9, 30), datetime_time(18, 0)
        else:
            return datetime_time(9, 30), datetime_time(18, 0)
    
    def get_current_month_late_marks(self, emp_id, attendance_date):
        query = """
            SELECT SUM(late_mark_count) FROM ci_biomatric_data
            WHERE emp_id = %s 
            AND MONTH(attendance_date) = MONTH(%s) 
            AND YEAR(attendance_date) = YEAR(%s)
        """
        
        result = self.execute_query(query, [emp_id, attendance_date, attendance_date])
        return result[0][0] if result and result[0][0] is not None else 0
    
    def parse_time_data(self, time_data):
        """Parse time data from various formats"""
        if isinstance(time_data, timedelta):
            total_seconds = int(time_data.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return datetime_time(hours, minutes, seconds)
        else:
            return datetime.strptime(str(time_data), "%H:%M:%S").time()
        
    def deduct_half_day_leave(self, emp_id):
        """Deduct half day leave and return attendance status"""
        now = datetime.now()
        year = now.year
        
        update_query = """
            UPDATE ci_leave_balance
            SET balance_leave = balance_leave - 0.5
            WHERE employee_id = %s AND year = %s AND status = 'Y' 
            AND leave_type_id = 184 AND balance_leave >= 0.5
        """
        
        rowcount = self.execute_query(update_query, [emp_id, year], fetch=False, commit=True)
        
        if rowcount == 0:
            check_query = """
                SELECT balance_leave
                FROM ci_leave_balance
                WHERE employee_id = %s AND year = %s AND status = 'Y' AND leave_type_id = 184
            """
            result = self.execute_query(check_query, [emp_id, year])
            
            if result and result[0][0] < 0.5:
                return 'H'
        
        return 'P'
    
    def get_employees_to_process(self, target_date):
        """Get all employees with clock-in but need processing"""
        query = """
            SELECT 
                bd.ci_biomatric_id,
                bd.emp_id,
                bd.clock_in,
                bd.clock_out,
                bd.is_half_day as current_half_day,
                bd.half_day_reason as current_half_day_reason,
                bd.status as attendance_status,
                COALESCE(eh.employee_hub_name, '') AS employee_hub_name,
                bd.attendance_date,
                bd.late_mark,
                bd.late_mark_count,
                COALESCE(eh.employee_hub_id, '0') AS employee_hub_id
            FROM ci_biomatric_data bd
            INNER JOIN ci_erp_users u ON bd.userid = u.id
            LEFT JOIN ci_employee_hub eh ON u.employee_hub_id = eh.employee_hub_id
            WHERE bd.attendance_date = %s 
            AND bd.state_in_out = 'in'
            AND bd.clock_out IS NOT NULL
            ORDER BY bd.emp_id, bd.ci_biomatric_id DESC
        """
        
        rows = self.execute_query(query, [target_date])
        
        employees_data = {}
        for row in rows:
            emp_id = row[1]
            if emp_id not in employees_data:
                employees_data[emp_id] = {
                    'biomatric_id': row[0],
                    'emp_id': row[1],
                    'clock_in': row[2],
                    'clock_out': row[3],
                    'current_half_day': row[4],
                    'current_half_day_reason': row[5],
                    'attendance_status': row[6],
                    'employee_hub_name': row[7],
                    'attendance_date': row[8],
                    'late_mark': row[9],
                    'late_mark_count': row[10],
                    'employee_hub_id': row[11],
                }
        
        return list(employees_data.values())
        
    def process_employee_attendance(self, employee_data):
        """Process individual employee attendance calculations"""
        try:
            emp_id = employee_data['emp_id']
            biomatric_id = employee_data['biomatric_id']
            clock_in_data = employee_data['clock_in']
            clock_out_time = employee_data['clock_out']
            current_half_day = employee_data['current_half_day']
            current_half_day_reason = employee_data['current_half_day_reason']
            attendance_status = employee_data['attendance_status']
            employee_hub_name = employee_data['employee_hub_name']
            attendance_date = employee_data['attendance_date']
            current_late_mark = employee_data['late_mark']
            current_late_mark_count = employee_data['late_mark_count']
            employee_hub_id = employee_data['employee_hub_id']
            
            clock_in_time_obj = self.parse_time_data(clock_in_data)
            clock_in_datetime = datetime.combine(attendance_date, clock_in_time_obj)
            
            if isinstance(clock_out_time, str):
                clock_out_time_obj = datetime.strptime(clock_out_time, "%H:%M:%S").time()
            else:
                clock_out_time_obj = clock_out_time
            
            clock_out_datetime = datetime.combine(attendance_date, clock_out_time_obj)
            
            if clock_out_datetime <= clock_in_datetime:
                logger.warning(f"Invalid clock times for emp_id {emp_id}: clock_out <= clock_in")
                return False
            
            total_work = clock_out_datetime - clock_in_datetime
            total_work_decimal = total_work.total_seconds() / 3600
            
            hours = int(total_work_decimal)
            minutes = int((total_work_decimal - hours) * 60)
            total_work_str = f"{hours:02}:{minutes:02}"
            
            try:
                _, end_time = self.get_work_timings(employee_hub_name, employee_hub_id, attendance_date)
            except ValueError as e:
                if "holiday" in str(e).lower():
                    logger.info(f"Skipping emp_id {emp_id}: Shift is marked as holiday")
                    return "HOLIDAY"
                else:
                    logger.error(f"Error getting work timings for emp_id {emp_id}: {str(e)}")
                    return False
            
            end_datetime = datetime.combine(attendance_date, end_time)
            clock_out_punch_datetime = datetime.combine(attendance_date, clock_out_time_obj)
            
            late_mark = "N"
            early_mark = "N"
            reasons_list = [current_half_day_reason] if current_half_day_reason else []
            
            if 8.25 <= total_work_decimal < 8.50:
                late_mark = "Y"

            if late_mark == "Y":
                late_mark_count = self.get_current_month_late_marks(emp_id, attendance_date)
            else:
                late_mark_count = 0
            
            if clock_out_punch_datetime < end_datetime:
                early_mark = "Y"
                reasons_list.append("Early Punch-Out")
            
            if total_work_decimal < 8.25:
                reasons_list.append("Insufficient Working Hours")
            
            if clock_out_time_obj < datetime_time(13, 0):
                reasons_list.append("Punched Before 1 PM")

            if late_mark == 'Y':
                if late_mark_count >= 2:
                    is_half_day = "Y"
                    reasons_list.append("Exceeded Late Mark Limit")
                    
                    reset_query = """
                        UPDATE ci_biomatric_data
                        SET late_mark_count = 0
                        WHERE emp_id = %s
                        AND MONTH(attendance_date) = MONTH(%s)
                        AND YEAR(attendance_date) = YEAR(%s)
                    """
                    self.execute_query(reset_query, [emp_id, attendance_date, attendance_date], fetch=False, commit=True)
                    late_mark_count = 0
                else:
                    late_mark_count += 1
            
            is_half_day = "Y" if reasons_list else "N"
            half_day_reason = ", ".join(reasons_list) if reasons_list else None
            
            if is_half_day == 'Y' and current_half_day == 'N':
                attendance_status = self.deduct_half_day_leave(emp_id)
            
            mark_half_day = is_half_day if current_half_day == 'N' else current_half_day
            mark_late_mark = late_mark if current_late_mark == 'N' else current_late_mark
            mark_late_count = late_mark_count if late_mark == 'Y' else current_late_mark_count
            
            update_query = """
                UPDATE ci_biomatric_data
                SET state_in_out = %s, total_work = %s, late_mark = %s, early_mark = %s, 
                    is_half_day = %s, half_day_reason = %s, late_mark_count = %s, 
                    status = %s, reason = %s
                WHERE ci_biomatric_id = %s
            """
            
            rowcount = self.execute_query(
                update_query,
                [
                    "out", total_work_str, mark_late_mark, early_mark,
                    mark_half_day, half_day_reason, mark_late_count, 
                    attendance_status, "Check OUT", biomatric_id
                ],
                fetch=False,
                commit=True  # CRITICAL: Commit the main update
            )
            
            if rowcount > 0:
                logger.info(f"✅ Updated biomatric_id={biomatric_id} for emp_id={emp_id}")
            else:
                logger.info(f"⚠️ No rows updated for biomatric_id={biomatric_id}")
            
            logger.info(f"Processed emp_id {emp_id}: total_work={total_work_decimal:.2f}h, half_day={is_half_day}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing emp_id {emp_id}: {str(e)}")
            # Rollback on error
            transaction.rollback()
            return False
        
    def run_daily_processing_detailed(self, target_date=None):
        """Enhanced version with detailed tracking"""
        if target_date is None:
            target_date = datetime.now().date()
        
        logger.info(f"Starting attendance processing for date: {target_date}")
        
        results = {
            'processed': [],
            'failed': [],
            'holidays': [],
            'skipped': []
        }
        
        try:
            employees_to_process = self.get_employees_to_process(target_date)
            total_employees = len(employees_to_process)
            
            logger.info(f"Found {total_employees} employees to process")
            
            batch_size = 100
            
            # Process each employee individually with its own transaction
            for i in range(0, total_employees, batch_size):
                batch = employees_to_process[i:i + batch_size]
                
                for employee_data in batch:
                    emp_id = employee_data.get('emp_id', 'Unknown')
                    
                    try:
                        result = self.process_employee_attendance(employee_data)
                        
                        if result == "HOLIDAY":
                            results['holidays'].append({
                                'emp_id': emp_id,
                                'reason': 'Shift marked as holiday',
                                'hub_name': employee_data.get('employee_hub_name', 'Unknown')
                            })
                        elif result is True:
                            results['processed'].append({'emp_id': emp_id, 'status': 'success'})
                        else:
                            results['failed'].append({'emp_id': emp_id, 'reason': 'Processing returned False'})
                            
                    except Exception as e:
                        results['failed'].append({'emp_id': emp_id, 'reason': f'Exception: {str(e)}'})
                        # Ensure rollback on exception
                        transaction.rollback()
                
                processed_so_far = min(i + batch_size, total_employees)
                logger.info(f"Processed batch: {processed_so_far}/{total_employees} employees")
            
            self.processed_count = len(results['processed'])
            self.error_count = len(results['failed'])
            self.holiday_count = len(results['holidays'])
            
            logger.info(f"Processing completed. Success: {self.processed_count}, "
                    f"Errors: {self.error_count}, Holidays: {self.holiday_count}")
            
            if results['failed']:
                logger.warning("Failed employees:")
                for failed in results['failed'][:10]:
                    logger.warning(f"  - {failed['emp_id']}: {failed['reason']}")
                if len(results['failed']) > 10:
                    logger.warning(f"  ... and {len(results['failed']) - 10} more failures")
            
            results.update({
                'total_employees': total_employees,
                'errors': self.error_count,
                'success_rate': (self.processed_count / total_employees * 100) if total_employees > 0 else 0
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Critical error in daily processing: {str(e)}")
            transaction.rollback()
            raise


def main():
    """Main entry point for the cron script"""
    try:
        # Ensure Django is in autocommit mode for standalone scripts
        connection.set_autocommit(True)
        
        processor = AttendanceCronProcessor()
        result = processor.run_daily_processing_detailed()

        logger.info(f"Final Summary - Total: {result['total_employees']}, "
                   f"Processed: {len(result['processed'])}, "
                   f"Errors: {result['errors']}, "
                   f"Holidays: {len(result['holidays'])}, "
                   f"Success Rate: {result['success_rate']:.2f}%")
        
        if result['errors'] > 0:
            error_rate = (result['errors'] / result['total_employees'] * 100) if result['total_employees'] > 0 else 0
            
            if error_rate > 10:
                logger.error(f"High error rate: {error_rate:.2f}% - Critical failure")
                sys.exit(2)
            else:
                logger.warning(f"Completed with {result['errors']} errors ({error_rate:.2f}%)")
                sys.exit(1)
        else:
            logger.info("Processing completed successfully")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        transaction.rollback()
        sys.exit(1)

if __name__ == "__main__":
    main()
from django.db import connection, transaction
from datetime import date
import os
import sys
import django
import mysql.connector

def setup_django():
    """Setup Django environment for standalone script"""
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up two levels from cron scripts folder
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    # Set the Django settings module - REPLACE 'project_name' with your actual project folder name
    # Check your D:\hrmaas\HRMAAS(16-4)\ folder for the folder containing settings.py
    # Common names: 'hrmaas', 'HRMAAS', 'project', 'config', etc.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')  # CHANGE THIS LINE
    
    # Setup Django
    django.setup()

# Call Django setup before importing models or using Django features
setup_django()

# def assign_paid_leaves_after_60_days():
#     current_year = date.today().year

#     with transaction.atomic():

#         with connection.cursor() as cursor:

#             # Get employees who already have PL row for current year
#             cursor.execute("""
#                 SELECT employee_id, balance_leave, carry_forward, last_paid_leave_given_at
#                 FROM ci_leave_balance
#                 WHERE leave_type = 'Paid Leave' AND year = %s
#             """, (current_year,))
#             all_rows = cursor.fetchall()

#             for row in all_rows:
#                 emp_id, balance, carry_forward, last_milestone = row
#                 last_milestone = last_milestone or 0  # None → 0

#                 # Get Present days (status = 'P')
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM ci_biomatric_data
#                     WHERE emp_id = %s AND status = 'P' AND YEAR(attendance_date) = %s
#                 """, (emp_id, current_year))
#                 present_days = cursor.fetchone()[0]

#                 # Max milestones = 60, 120, 180 (max 18 PLs)
#                 milestones = [60, 120, 180]
#                 for m in milestones:
#                     if present_days >= m and last_milestone < m:
#                         new_balance = min(balance + 5, 18)
#                         cursor.execute("""
#                             UPDATE ci_leave_balance
#                             SET balance_leave = %s, last_paid_leave_given_at = %s
#                             WHERE employee_id = %s AND leave_type = 'Paid Leave' AND year = %s
#                         """, (new_balance, m, emp_id, current_year))
#                         break  # Only assign once per run

DB_CONFIG = {
    "host": "192.168.0.253",
    "user": "vetrina_hrms_user",
    "password": "v^$XcpD!p7Qi",
    "database": "vetrina_hrms",
}

def connect_db():
    """Connect to MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database Connection Error: {err}")
        return

def assign_paid_leaves_after_60_days():

    conn = connect_db()
    if not conn:
        return

    current_year = date.today().year

    with transaction.atomic():
        with conn.cursor() as cursor:
            # Step 1: Get all confirmed employees with their confirmation date
            cursor.execute("""
                SELECT 
                    ud.employee_id,
                    ud.confirmation_date,
                    ud.employee_confirm
                FROM 
                    ci_erp_users_details ud
                INNER JOIN 
                    ci_erp_users u ON ud.user_id = u.id
                WHERE 
                    LOWER(ud.employee_confirm) = 'y'
            """)
            confirmed_employees = cursor.fetchall()

            for emp_id, confirmation_date, _ in confirmed_employees:
                if not confirmation_date:
                    continue  # Skip if no confirmation date

                # Step 2: Count 'Present' punch-ins from confirmation date to today
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM ci_biomatric_data 
                    WHERE emp_id = %s 
                      AND status = 'P' 
                      AND attendance_date >= %s 
                      AND attendance_date <= CURDATE()
                """, (emp_id, confirmation_date))
                present_days = cursor.fetchone()[0]

                # Step 3: Check if current present_days exactly hits a milestone (60, 120, 180)
                milestones = [60, 120, 180]

                for milestone in milestones:
                    if present_days == milestone:
                        # Step 4: Check if milestone already rewarded
                        cursor.execute("""
                            SELECT balance_leave, last_paid_leave_given_at 
                            FROM ci_leave_balance 
                            WHERE employee_id = %s 
                              AND leave_type = 'Paid Leave' 
                              AND year = %s
                        """, (emp_id, current_year))
                        leave_data = cursor.fetchone()

                        if leave_data:
                            current_balance, last_milestone = leave_data
                            last_milestone = last_milestone or 0

                            if last_milestone < milestone:
                                # Award +5 PL (max 18)
                                new_balance = min(current_balance + 5, 18)
                                cursor.execute("""
                                    UPDATE ci_leave_balance
                                    SET balance_leave = %s,
                                        last_paid_leave_given_at = %s
                                    WHERE employee_id = %s 
                                      AND leave_type = 'Paid Leave' 
                                      AND year = %s
                                """, (new_balance, milestone, emp_id, current_year))
                        break  # Only award one milestone per run

if __name__ == "__main__":
    assign_paid_leaves_after_60_days()

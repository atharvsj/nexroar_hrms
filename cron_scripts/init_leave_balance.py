# from datetime import date
# from django.db import connection, transaction
# import datetime
# import os
# import django
# import sys

# sys.path.append("/mnt/d/hrmaas/HRMAAS(16-4)")

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
# django.setup()


# def init_leave_balance():
#     current_year = date.today().year

#     with transaction.atomic():
#         with connection.cursor() as c:

#             c.execute(
#                 """
#                 SELECT DISTINCT ud.employee_id, CONCAT(u.first_name, ' ', u.last_name) AS employee_name
#                 FROM ci_erp_users_details ud
#                 JOIN ci_erp_users u ON u.id = ud.user_id
#             """
#             )

#             columns = [col[0] for col in c.description]
#             employees = [dict(zip(columns, rows)) for rows in c.fetchall()]

#             c.execute(
#                 """
#                 SELECT constants_id AS leave_type_id, category_name AS leave_type, field_one
#                 FROM ci_erp_constants
#                 WHERE type = 'leave_type'
#             """
#             )
#             columns = [col[0] for col in c.description]
#             leave_types = [dict(zip(columns, rows)) for rows in c.fetchall()]

#             for emp in employees:
#                 for leave in leave_types:
#                     emp_id = emp["employee_id"]
#                     emp_name = emp["employee_name"]
#                     leave_id = leave["leave_type_id"]
#                     leave_name = leave["leave_type"]
#                     field_one = leave["field_one"]

#                     if leave_name == "Paid Leave":

#                         c.execute(
#                             """
#                             SELECT balance_leave FROM ci_leave_balance
#                             WHERE employee_id = %s AND leave_type = 'Paid Leave' AND year = %s
#                         """,
#                             (emp_id, current_year - 1),
#                         )
#                         columns = [col[0] for col in c.description]
#                         row = c.fetchone()
#                         prev = dict(zip(columns, row)) if row else None
                        
#                         carry_forward = prev["balance_leave"] if prev else 0
#                         balance_leave = 0  # start from 0
#                     else:
#                         carry_forward = 0
#                         balance_leave = field_one

#                     c.execute(
#                         """
#                         INSERT INTO ci_leave_balance (
#                             employee_id, employee_name, leave_type_id, leave_type,
#                             balance_leave, year, carry_forward, last_paid_leave_given_at
#                         ) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
#                     """,
#                         (
#                             emp_id,
#                             emp_name,
#                             leave_id,
#                             leave_name,
#                             balance_leave,
#                             current_year,
#                             carry_forward,
#                         ),
#                     )

#     # print(f"Leave balances initialized for year {current_year}.")

# log_path = "/mnt/d/hrmaas/HRMAAS(16-4)/cron scripts/cron_test.log"

# with open(log_path, "a") as f:
#     f.write(f"[{datetime.datetime.now()}] Script ran successfully.\n")

# if __name__ == "__main__":
#     init_leave_balance()



from datetime import date
from django.db import connection, transaction
import datetime
import os
import django
import sys
import mysql.connector

sys.path.append("/mnt/d/hrmaas/HRMAAS(16-4)")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

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


def init_leave_balance():

    conn = connect_db()
    if not conn:
        return

    current_year = date.today().year
    
    with transaction.atomic():
        with conn.cursor() as c:
            # Get all employees
            c.execute(
                """
                SELECT DISTINCT ud.employee_id, CONCAT(u.first_name, ' ', u.last_name) AS employee_name
                FROM ci_erp_users_details ud
                JOIN ci_erp_users u ON u.id = ud.user_id
                """
            )
            employees = c.fetchall()
            
            # Get all leave types
            c.execute(
                """
                SELECT constants_id AS leave_type_id, category_name AS leave_type, field_one
                FROM ci_erp_constants
                WHERE type = 'leave_type'
                """
            )
            leave_types = c.fetchall()
            
            # Get previous year's paid leave balances in one query
            employee_ids = [emp[0] for emp in employees]
            if employee_ids:
                placeholders = ','.join(['%s'] * len(employee_ids))
                c.execute(
                    f"""
                    SELECT employee_id, balance_leave
                    FROM ci_leave_balance
                    WHERE employee_id IN ({placeholders}) 
                    AND leave_type = 'Paid Leave' 
                    AND year = %s
                    """,
                    employee_ids + [current_year - 1]
                )
                prev_balances = dict(c.fetchall())
            else:
                prev_balances = {}
            
            # Prepare bulk insert data
            insert_data = []
            for emp_id, emp_name in employees:
                for leave_type_id, leave_type, field_one in leave_types:
                    if leave_type == "Paid Leave":
                        carry_forward = prev_balances.get(emp_id, 0)
                        balance_leave = 0  # start from 0
                    else:
                        carry_forward = 0
                        balance_leave = field_one
                    
                    insert_data.append((
                        emp_id,
                        emp_name,
                        leave_type_id,
                        leave_type,
                        balance_leave,
                        current_year,
                        carry_forward
                    ))
            
            # Bulk insert all records
            if insert_data:
                c.executemany(
                    """
                    INSERT INTO ci_leave_balance (
                        employee_id, employee_name, leave_type_id, leave_type,
                        balance_leave, year, carry_forward, last_paid_leave_given_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
                    """,
                    insert_data
                )

# Log execution
# end_time = datetime.datetime.now()
# duration = end_time - start_time

# log_path = "/mnt/d/hrmaas/HRMAAS(16-4)/cron scripts/cron_test.log"
# with open(log_path, "a") as f:
#     f.write(f"[{start_time}] Script started.\n")
#     f.write(f"[{end_time}] Script completed. Duration: {duration}\n")

if __name__ == "__main__":
    start_time = datetime.datetime.now()

    try:
        init_leave_balance()
        status = "Script completed successfully."
    except Exception as e:
        status = f"Script failed with error: {str(e)}"

    end_time = datetime.datetime.now()
    duration = end_time - start_time

    log_path = "/mnt/d/hrmaas/HRMAAS(16-4)/cron scripts/cron_test.log"
    with open(log_path, "a") as f:
        f.write(f"[{start_time}] Script started.\n")
        f.write(f"[{end_time}] {status} Duration: {duration}\n")

    
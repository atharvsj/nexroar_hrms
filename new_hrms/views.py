from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.utils import timezone

class ConfirmationParameter(APIView):

    def post(self, request):
        para_name = request.data.get("para_name")

        if not para_name:
            return Response({"error": "para_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ci_confirmation_parameters (para_name) VALUES (%s)",
                    [para_name]
                )
            return Response({"message": "Parameter added successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT parameter_id, para_name FROM ci_confirmation_parameters")
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        parameter_id = request.data.get("parameter_id")
        para_name = request.data.get("para_name")

        if not parameter_id or not para_name:
            return Response({"error": "parameter_id and para_name are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE ci_confirmation_parameters SET para_name = %s WHERE parameter_id = %s",
                    [para_name, parameter_id]
                )
            return Response({"message": "Parameter updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        parameter_id = request.data.get("parameter_id")

        if not parameter_id:
            return Response({"error": "parameter_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM ci_confirmation_parameters WHERE parameter_id = %s",
                    [parameter_id]
                )
            return Response({"message": "Parameter deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# Phase one employee confirnmation 



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection, IntegrityError


# class SavePhase1APIView(APIView):
#     def post(self, request):
#         entries = request.data.get("entries", [])

#         if not entries:
#             return Response({"error": "No entries provided"}, status=status.HTTP_400_BAD_REQUEST)

#         valid_rows = []
#         invalid_entries = []
#         phase_value = None  # To store phase from valid entry

#         for index, entry in enumerate(entries):
#             emp_id = entry.get("emp_id")
#             parameter_id = entry.get("parameter_id")
#             phase = entry.get("phase", 1)

#             if emp_id is None or parameter_id is None:
#                 invalid_entries.append({
#                     "index": index,
#                     "error": "emp_id or parameter_id is missing"
#                 })
#                 continue

#             if phase_value is None:
#                 phase_value = phase  # store phase from the first valid entry

#             valid_rows.append([
#                 emp_id,
#                 parameter_id,
#                 phase,
#                 entry.get("points_by_lm"),
#                 entry.get("comment_by_lm"),
#                 entry.get("points_by_head"),
#                 entry.get("comment_by_head"),
#                 entry.get("points_by_hr"),
#                 entry.get("comment_by_hr"),
#             ])

#         if not valid_rows:
#             return Response({
#                 "error": "All entries are invalid",
#                 "details": invalid_entries
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             with connection.cursor() as cursor:
#                 cursor.executemany("""
#                     INSERT INTO ci_employee_progress_tracking (
#                         emp_id, parameter_id, phase,
#                         points_by_lm, comment_by_lm,
#                         points_by_head, comment_by_head,
#                         points_by_hr, comment_by_hr
#                     ) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s)
#                 """, valid_rows)

#             return Response({
#                 "message": f"Phase {phase_value} entries saved successfully.",
#                 "skipped_entries": invalid_entries
#             }, status=status.HTTP_201_CREATED)

#         except IntegrityError as e:
#             return Response({
#                 "error": "Integrity error",
#                 "details": str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({
#                 "error": "Server error",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SavePhasewiseAPIView(APIView):
    def post(self, request):
        entries = request.data.get("entries", [])
        user_role = request.data.get("role_id")  # Expected: 'line_manager', 'head_manager', 'hr'
       
        if not entries:
            return Response({"error": "No entries provided"}, status=status.HTTP_400_BAD_REQUEST)
       
        if not user_role or user_role not in [13, 14, 5, 7]:
            return Response({"error": "Valid role is required (line_manager, head_manager, hr)"}, status=status.HTTP_400_BAD_REQUEST)
       
        valid_entries = []
        invalid_entries = []
        phase_value = None
       
        # Validate entries
        for index, entry in enumerate(entries):
            emp_id = entry.get("emp_id")
            parameter_id = entry.get("parameter_id")
            phase = entry.get("phase", 1)
           
            if emp_id is None or parameter_id is None:
                invalid_entries.append({
                    "index": index,
                    "error": "emp_id or parameter_id is missing"
                })
                continue
           
            if phase_value is None:
                phase_value = phase
           
            valid_entries.append(entry)
       
        if not valid_entries:
            return Response({
                "error": "All entries are invalid",
                "details": invalid_entries
            }, status=status.HTTP_400_BAD_REQUEST)
       
        try:
            with connection.cursor() as cursor:
                for entry in valid_entries:
                    emp_id = entry.get("emp_id")
                    parameter_id = entry.get("parameter_id")
                    phase = entry.get("phase", 1)
                   
                    # Check if record already exists
                    cursor.execute("""
                        SELECT progress_id FROM ci_employee_progress_tracking
                        WHERE emp_id = %s AND parameter_id = %s AND phase = %s
                    """, [emp_id, parameter_id, phase])
                   
                    existing_record = cursor.fetchone()
                   
                    if user_role == 13:       # line_manager
                        if existing_record:
                            # Update existing record (line manager can modify their own entries)
                            cursor.execute("""
                                UPDATE ci_employee_progress_tracking
                                SET points_by_lm = %s, comment_by_lm = %s
                                WHERE emp_id = %s AND parameter_id = %s AND phase = %s
                            """, [
                                entry.get("points_by_lm"),
                                entry.get("comment_by_lm"),
                                emp_id, parameter_id, phase
                            ])
                        else:
                            # Insert new record
                            cursor.execute("""
                                INSERT INTO ci_employee_progress_tracking (
                                    emp_id, parameter_id, phase,
                                    points_by_lm, comment_by_lm,
                                    points_by_head, comment_by_head,
                                    points_by_hr, comment_by_hr
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, [
                                emp_id, parameter_id, phase,
                                entry.get("points_by_lm"),
                                entry.get("comment_by_lm"),
                                None, None, None, None
                            ])
                   
                    elif user_role == 14:           # head_manager
                        if existing_record:
                            # Update head manager fields
                            cursor.execute("""
                                UPDATE ci_employee_progress_tracking
                                SET points_by_head = %s, comment_by_head = %s
                                WHERE emp_id = %s AND parameter_id = %s AND phase = %s
                            """, [
                                entry.get("points_by_head"),
                                entry.get("comment_by_head"),
                                emp_id, parameter_id, phase
                            ])
                        else:
                            # Insert new record
                            cursor.execute("""
                                INSERT INTO ci_employee_progress_tracking (
                                    emp_id, parameter_id, phase,
                                    points_by_lm, comment_by_lm,
                                    points_by_head, comment_by_head,
                                    points_by_hr, comment_by_hr
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, [
                                emp_id, parameter_id, phase,
                                None, None,
                                entry.get("points_by_head"),
                                entry.get("comment_by_head"),
                                None, None
                            ])
                   
                    elif user_role in [5, 7]:       # hr or admin
                        if existing_record:
                            # Update HR fields
                            cursor.execute("""
                                UPDATE ci_employee_progress_tracking
                                SET points_by_hr = %s, comment_by_hr = %s
                                WHERE emp_id = %s AND parameter_id = %s AND phase = %s
                            """, [
                                entry.get("points_by_hr"),
                                entry.get("comment_by_hr"),
                                emp_id, parameter_id, phase
                            ])
                        else:
                            # Insert new record
                            cursor.execute("""
                                INSERT INTO ci_employee_progress_tracking (
                                    emp_id, parameter_id, phase,
                                    points_by_lm, comment_by_lm,
                                    points_by_head, comment_by_head,
                                    points_by_hr, comment_by_hr
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, [
                                emp_id, parameter_id, phase,
                                None, None, None, None,
                                entry.get("points_by_hr"),
                                entry.get("comment_by_hr")
                            ])
           
            return Response({
                "message": f"Phase {phase_value} entries saved successfully by {user_role}.",
                "skipped_entries": invalid_entries
            }, status=status.HTTP_200_OK)
           
        except IntegrityError as e:
            return Response({
                "error": "Integrity error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "Server error",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection





 
class EmployeeDailyAttendanceGetReport(APIView):
    def get(self, request):
        attendance_date = request.query_params.get("date", None)
 
        if not attendance_date:
            return Response(
                {"detail": "Missing required parameter: date"},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        eud.user_id,
                        eud.employee_id,
                        CONCAT(
                            COALESCE(eu.first_name, ''), ' ',
                            COALESCE(eu.middle_name, ''), ' ',
                            COALESCE(eu.last_name, '')
                        ) AS employee_name,
                        d.department_name,
                        deg.designation_name,
                        dv.division_name,
                        'null' AS sub_division,
                        'null' AS headquarter,
                        'null' AS level,
                        eud.manager AS manager_id,
                        CONCAT(
                            COALESCE(mgr.first_name, ''), ' ',
                            COALESCE(mgr.middle_name, ''), ' ',
                            COALESCE(mgr.last_name, '')
                        ) AS manager_name,
                        eud.date_of_joining,
                        cbd.clock_in  AS check_in_time,
                        cbd.clock_out AS check_out_time,
                        cbd.late_mark,
                        cbd.early_mark,
                        SEC_TO_TIME(
                            TIME_TO_SEC(cbd.clock_out) - TIME_TO_SEC(cbd.clock_in)
                        ) AS total_working_hours
                    FROM ci_erp_users AS eu
                    INNER JOIN ci_erp_users_details AS eud
                        ON eu.id = eud.user_id
                    LEFT JOIN ci_division AS dv
                        ON eud.division_id = dv.division_id
                    LEFT JOIN ci_designations AS deg
                        ON eud.designation_id = deg.designation_id
                    LEFT JOIN ci_departments AS d
                        ON d.department_id = eud.department_id
                    LEFT JOIN ci_erp_users AS mgr
                        ON eud.manager = mgr.id
                    LEFT JOIN ci_biomatric_data AS cbd
                        ON eud.user_id = cbd.userid
                    WHERE cbd.attendance_date = %s
                """
                cursor.execute(query, [attendance_date])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
 
            result = [dict(zip(columns, row)) for row in rows]
 
            return Response(result, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

# class EmployeeConfirmationUpdate(APIView):
#     def put(self, request):
#         user_id = request.data.get("user_id")
#         action = request.data.get("action")
#         comment_by_lm = request.data.get("comment_by_lm")
#         comment_by_head = request.data.get("comment_by_head")
#         comment_by_hr = request.data.get("comment_by_hr")

#         if not user_id or not action:
#             return Response({"error": "user_id and action are required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             with connection.cursor() as cursor:
#                 if action == "confirm":
#                     cursor.execute("""
#                         UPDATE ci_erp_users_details
#                         SET employee_confirm = 'Y',
#                             is_terminated = 'N',
#                             is_probation_extend = 'N',
#                             confirmation_date = NOW(),
#                             terminated_date = NULL,
#                             probation_extended_date = NULL,
#                             comment_by_lm = %s,
#                             comment_by_head = %s,
#                             comment_by_hr = %s
#                         WHERE user_id = %s
#                     """, [comment_by_lm, comment_by_head, comment_by_hr, user_id])

#                 elif action == "terminate":
#                     cursor.execute("""
#                         UPDATE ci_erp_users_details
#                         SET is_terminated = 'Y',
#                             employee_confirm = 'N',
#                             is_probation_extend = 'N',
#                             terminated_date = NOW(),
#                             confirmation_date = NULL,
#                             probation_extended_date = NULL,
#                             comment_by_lm = %s,
#                             comment_by_head = %s,
#                             comment_by_hr = %s
#                         WHERE user_id = %s
#                     """, [comment_by_lm, comment_by_head, comment_by_hr, user_id])

#                 elif action == "extend":
#                     cursor.execute("""
#                         UPDATE ci_erp_users_details
#                         SET is_probation_extend = 'Y',
#                             employee_confirm = 'N',
#                             is_terminated = 'N',
#                             probation_extended_date = NOW(),
#                             confirmation_date = NULL,
#                             terminated_date = NULL,
#                             comment_by_lm = %s,
#                             comment_by_head = %s,
#                             comment_by_hr = %s
#                         WHERE user_id = %s
#                     """, [comment_by_lm, comment_by_head, comment_by_hr, user_id])

#                 else:
#                     return Response({"error": "Invalid action. Use 'confirm', 'terminate', or 'extend'."},
#                                     status=status.HTTP_400_BAD_REQUEST)

#             return Response({"message": f"Employee status updated successfully for action '{action}'."}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from django.db import connection, transaction

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import os


class EmployeeConfirmationUpdate(APIView):
    def patch(self, request):
        user_id = request.data.get("user_id")
        action = request.data.get("action")
        # Set default "No comment" if values are not provided
        comment_by_lm = request.data.get("comment_by_lm", "No comment")
        comment_by_head = request.data.get("comment_by_head", "No comment")
        comment_by_hr = request.data.get("comment_by_hr", "No comment")

        if not user_id or not action:
            return Response({"error": "user_id and action are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                with connection.cursor() as cursor:

                    cursor.execute("""
                        SELECT id FROM ci_erp_users u
                        INNER JOIN ci_staff_roles sr ON u.user_role_id = sr.role_id
                        WHERE sr.role_name = 'HR'
                        ORDER BY u.id DESC LIMIT 1
                    """)

                    admin_result = cursor.fetchone()

                    if not admin_result:
                        raise ValueError("No HR user found in the system")
                    
                    admin_id = admin_result[0]

                    if action == "confirm":
                        # First update employee confirmation status
                        cursor.execute("""
                            UPDATE ci_erp_users_details
                            SET employee_confirm = 'Y',
                                is_terminated = 'N',
                                probation="N",
                                is_probation_extend = 'N',
                                confirmation_date = NOW(),
                                terminated_date = NULL,
                                probation_extended_date = NULL,
                                comment_by_lm = %s,
                                comment_by_head = %s,
                                comment_by_hr = %s
                            WHERE user_id = %s
                        """, [comment_by_lm, comment_by_head, comment_by_hr, user_id])

                        # Get employee details
                        cursor.execute("""
                            SELECT u.first_name, u.last_name, ud.employee_id
                            FROM ci_erp_users u
                            JOIN ci_erp_users_details ud ON u.id = ud.user_id
                            WHERE u.id = %s
                        """, [user_id])
                        employee = cursor.fetchone()
                        
                        if not employee:
                            raise Exception("Employee not found")
                            
                        first_name, last_name, employee_id = employee
                        employee_name = f"{first_name} {last_name}"
                        # current_year = datetime.now().year
                        current_year = timezone.now().year

                        # Define leave types and their balances
                        leave_assignments = {
                            "Casual Leave (CL)": 6,
                            "Medical Leave (ML)": 7,
                            "Maternity Leave": 182,
                            "Paid Leave": 5,  # Changed from 0 to 5 as per your sample data
                            "Paternity Leave": 3
                        }

                        # Get leave type IDs from constants table
                        cursor.execute("""
                            SELECT constants_id, category_name 
                            FROM ci_erp_constants 
                            WHERE type = 'leave_type' 
                            AND category_name IN %s
                        """, [tuple(leave_assignments.keys())])
                        
                        leave_types = cursor.fetchall()
                        
                        if len(leave_types) != len(leave_assignments):
                            missing = set(leave_assignments.keys()) - {lt[1] for lt in leave_types}
                            raise Exception(f"Missing leave type definitions: {missing}")

                        # Insert leave balance records
                        for constants_id, category_name in leave_types:
                            cursor.execute("""
                                INSERT INTO ci_leave_balance (
                                    employee_id,
                                    employee_name,
                                    leave_type_id,
                                    leave_type,
                                    balance_leave,
                                    carry_forward,
                                    last_paid_leave_given_at,
                                    year,
                                    status
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Y')
                            """, [
                                employee_id,
                                employee_name,
                                constants_id,
                                category_name,
                                leave_assignments[category_name],
                                0,  # carry_forward
                                60 if category_name == "Paid Leave" else None,  # last_paid_leave_given_at
                                current_year
                            ])


                        # Now generate confirmation letter PDF and send email
                        cursor.execute("""
                            SELECT u.email, d.designation_name, u.first_name, u.last_name
                            FROM ci_erp_users u 
                            INNER JOIN ci_erp_users_details ud ON u.id = ud.user_id 
                            INNER JOIN ci_designations d ON ud.designation_id = d.designation_id 
                            WHERE ud.employee_id = %s
                        """, [employee_id])

                        row = cursor.fetchone()
                        if not row:
                            raise Exception("Employee details not found")

                        email_id = row[0]
                        designation_name = row[1]
                        first_name = row[2]
                        last_name = row[3]

                        if email_id is None or email_id == '':
                            raise Exception("Employee email ID not found")

                        confirmation_date = datetime.now().strftime("%d/%m/%Y")
                        confirmation_date_text = datetime.now().strftime("1st %B %Y")  # e.g., "1st June 2025"

                        # Fetch HR details for signature
                        cursor.execute("""select concat(u.first_name,' ', u.last_name) as hr_name, sr.role_name from ci_erp_users u inner join ci_staff_roles sr on u.user_role_id = sr.role_id where sr.role_name = 'HR' and u.is_active = 1 order by id desc limit 1""")

                        hr_row = cursor.fetchone()

                        hr_name = hr_row[0]
                        hr_designation = hr_row[1] if hr_row else "HR"


                        html_content = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <style>
                                @page {{
                                    size: A4;
                                    margin: 0.75in;
                                }}
                                body {{
                                    font-family: Arial, sans-serif;
                                    font-size: 11pt;
                                    line-height: 1.6;
                                    color: #000;
                                }}
                                .header {{
                                    text-align: center;
                                    font-weight: bold;
                                    font-size: 14pt;
                                    margin-bottom: 30px;
                                }}
                                .date {{
                                    margin-bottom: 20px;
                                }}
                                .to-section {{
                                    margin-bottom: 20px;
                                }}
                                .subject {{
                                    font-weight: bold;
                                    margin-bottom: 20px;
                                }}
                                .body-text {{
                                    margin-bottom: 15px;
                                    text-align: justify;
                                }}
                                .signature {{
                                    margin-top: 40px;
                                }}
                                .signature-line {{
                                    margin-bottom: 8px;
                                }}
                                .company-name {{
                                    font-weight: bold;
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="header">LETTER OF CONFIRMATION</div>
                            
                            <div class="date">Date: {confirmation_date}</div>
                            
                            <div class="to-section">
                                To,<br>
                                Mr./Ms. {first_name} {last_name}
                            </div>
                            
                            <div class="subject">Subject: Confirmation of Employment</div>
                            
                            <div class="body-text">Dear Mr./Ms. {last_name},</div>
                            
                            <div class="body-text">
                                We are pleased to inform you that following a review of your performance during the probation 
                                period, your services have been confirmed for the position "{designation_name}", with 
                                effective from {confirmation_date_text}.
                            </div>
                            
                            <div class="body-text">
                                All other terms and conditions of your employment will remain same as stated in your 
                                appointment letter and company policy.
                            </div>
                            
                            <div class="body-text">
                                We look forward to your continued contribution and wish you a successful and rewarding 
                                career with Vetrina Healthcare Pvt. Ltd.
                            </div>
                            
                            <div class="signature">
                                <div class="signature-line">(DIGITAL SIGN) & stamp</div>
                                <div class="signature-line"><strong>Best regards,</strong></div>
                                <div class="signature-line">{hr_name}</div>
                                <div class="signature-line">{hr_designation}</div>
                                <div class="signature-line company-name">Vetrina Healthcare Pvt. Ltd</div>
                                <div class="signature-line">7447467450</div>
                                <div class="signature-line">www.vetrinahealthcare.com</div>
                            </div>
                        </body>
                        </html>
                        """

                        # Generate PDF
                        pdf_filename = f"Confirmation_Letter_{employee_id}_{employee_name.replace(' ', '_')}.pdf"
                        pdf_directory = os.path.join(settings.MEDIA_ROOT, 'confirmation_letters')
                        os.makedirs(pdf_directory, exist_ok=True)
                        pdf_path = os.path.join(pdf_directory, pdf_filename)

                        # Create PDF from HTML
                        with open(pdf_path, "wb") as pdf_file:
                            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

                        if pisa_status.err:
                            raise Exception("Error generating PDF")

                        # Email message
                        subject = "Congratulations! Your Employment has been Confirmed"
                        message = f"""Dear {first_name} {last_name},

                        Congratulations! We are delighted to inform you that your employment with Vetrina Healthcare Pvt. Ltd has been confirmed.

                        After carefully reviewing your performance, dedication, and contributions during your probation period, we are pleased to confirm you in the position of {designation_name}, effective from {confirmation_date}.

                        Your hard work, professionalism, and commitment to excellence have been truly impressive, and we are confident that you will continue to be a valuable asset to our team.

                        Please find attached your official Letter of Confirmation for your records.

                        We look forward to your continued success and contribution to Vetrina Healthcare Pvt. Ltd.

                        Once again, congratulations on this achievement!

                        Best regards,
                        {hr_name} ({hr_designation})
                        Vetrina Healthcare Pvt. Ltd
                        Email: support@thedatatechlabs.com
                        Phone: 7447467450
                        Website: www.vetrinahealthcare.com
                        """

                        # Create and send email
                        email = EmailMessage(
                            subject=subject,
                            body=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email_id],
                        )

                        # Attach PDF
                        with open(pdf_path, 'rb') as pdf_file:
                            email.attach(pdf_filename, pdf_file.read(), 'application/pdf')

                        # Send email
                        email.send(fail_silently=False)
                        

                        # Send Notification

                        notification_text = f"Employee {employee_name} ({employee_id}) has been confirmed."
                        cursor.execute("""
                            INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
                            VALUES (%s, %s, %s, NOW())
                        """, [admin_id, user_id, notification_text])
                        

                    elif action == "terminate":
                        cursor.execute("""
                            UPDATE ci_erp_users_details
                            SET is_terminated = 'Y',
                                employee_confirm = 'N',
                                is_probation_extend = 'N',
                                terminated_date = NOW(),
                                confirmation_date = NULL,
                                probation_extended_date = NULL,
                                comment_by_lm = %s,
                                comment_by_head = %s,
                                comment_by_hr = %s
                            WHERE user_id = %s
                        """, [comment_by_lm, comment_by_head, comment_by_hr, user_id])

                        # Send Notification
                        # Get employee details
                        cursor.execute("""
                            SELECT CONCAT(u.first_name,' ',u.last_name) as employee_name, ud.employee_id
                            FROM ci_erp_users u
                            JOIN ci_erp_users_details ud ON u.id = ud.user_id
                            WHERE u.id = %s
                        """, [user_id])
                        employee = cursor.fetchone()
                        
                        if not employee:
                            raise Exception("Employee not found")
                            
                        employee_name, employee_id = employee

                        notification_text = f"Employee {employee_name} ({employee_id}) has been terminated."
                        cursor.execute("""
                            INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
                            VALUES (%s, %s, %s, NOW())
                        """, [admin_id, user_id, notification_text])

                    elif action == "extend":
                        cursor.execute("""
                            UPDATE ci_erp_users_details
                            SET is_probation_extend = 'Y',
                                employee_confirm = 'N',
                                is_terminated = 'N',
                                probation_extended_date = NOW(),
                                confirmation_date = NULL,
                                terminated_date = NULL,
                                comment_by_lm = %s,
                                comment_by_head = %s,
                                comment_by_hr = %s
                            WHERE user_id = %s
                        """, [comment_by_lm, comment_by_head, comment_by_hr, user_id])

                        # Send Notification
                        # Get employee details
                        cursor.execute("""
                            SELECT CONCAT(u.first_name,' ',u.last_name) as employee_name, ud.employee_id
                            FROM ci_erp_users u
                            JOIN ci_erp_users_details ud ON u.id = ud.user_id
                            WHERE u.id = %s
                        """, [user_id])
                        employee = cursor.fetchone()
                        
                        if not employee:
                            raise Exception("Employee not found")
                            
                        employee_name, employee_id = employee

                        notification_text = f"Probation period has been extended for Employee {employee_name} ({employee_id})."
                        cursor.execute("""
                            INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
                            VALUES (%s, %s, %s, NOW())
                        """, [admin_id, user_id, notification_text])

                    else:
                        return Response({"error": "Invalid action. Use 'confirm', 'terminate', or 'extend'."},
                                      status=status.HTTP_400_BAD_REQUEST)

                return Response({
                    "message": f"Employee status updated successfully for action '{action}'.",
                    "employee_id": employee_id if action == "confirm" else None
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class GetEmployeeConfimationDash(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT 
                        CONCAT(
                            COALESCE(ceu.first_name, ''), ' ',
                            COALESCE(ceu.middle_name, ''), ' ',
                            COALESCE(ceu.last_name, '')
                        ) AS full_name,
                        cd.designation_name,
                        cdp.department_name,
                        ceud.is_probation_extend,
                        ceud.is_terminated,
                        ceud.employee_confirm,
                        ceu.created_at AS probation_start_date,
                        ceud.probation_extended_date,
                        ceud.terminated_date,
                        ceud.confirmation_date
                    FROM 
                        ci_erp_users AS ceu
                    INNER JOIN 
                        ci_erp_users_details AS ceud ON ceu.id = ceud.user_id
                    INNER JOIN 
                        ci_designations AS cd ON ceud.designation_id = cd.designation_id
                    INNER JOIN 
                        ci_departments AS cdp ON ceud.department_id = cdp.department_id;
                """
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]

            return Response({"data": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#10-07-2025


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class SavedesignationwiseParameters(APIView):
    def post(self, request):
        try:
            parameter_id = request.data.get('parameter_id')
            designation_id = request.data.get('designation_id')
            phase = request.data.get('phase')
            created_by = request.data.get('created_by')

            if not all([parameter_id, designation_id, phase]):
                return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

            with connection.cursor() as cursor:
                query = """
                    INSERT INTO ci_designationwise_parameters (parameter_id, designation_id, phase, created_by)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, [parameter_id, designation_id, phase, created_by])
                return Response({"message": "Designation Wise Parameters saved successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class GetDesignationwiseTableData(APIView):
    def get(self, request):
        phase = request.GET.get('phase')
        designation_id = request.GET.get('designation_id')

        if not phase or not designation_id:
            return Response(
                {"error": "Missing 'phase' or 'designation_id' parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT cdp.dp_id,cdp.parameter_id,cp.para_name,cdp.designation_id , cd.designation_name, cdp.phase 

                    FROM ci_designations AS cd
                    INNER JOIN ci_designationwise_parameters AS cdp 
                        ON cdp.designation_id = cd.designation_id
                    INNER JOIN ci_confirmation_parameters AS cp 
                        ON cp.parameter_id = cdp.parameter_id
                    WHERE cdp.phase = %s AND cdp.designation_id = %s
                """
                cursor.execute(query, [phase, designation_id])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({"data": results}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class DeleteDesigwiseParameter(APIView):
    def delete(self, request, pk):
        try:
            with connection.cursor() as cursor:
                query = "DELETE FROM ci_designationwise_parameters WHERE dp_id = %s"
                cursor.execute(query, [pk])

                if cursor.rowcount == 0:
                    return Response({"message": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Record deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class GetEmployeePerformanceTable(APIView):
    def get(self, request, role_id, user_id):
 
        try:
            if not role_id or not user_id:
                return Response({"status":"error","message":"role_id or user_id is missing"}, status=status.HTTP_400_BAD_REQUEST)
           
            with connection.cursor() as cursor:
           
                if role_id == 13:   # line manager
 
                    query = """
                        SELECT
                            ceu.id as user_id, ceu.username as emp_id,
                            CONCAT(
                                COALESCE(ceu.first_name, ''), ' ',
                                COALESCE(ceu.middle_name, ''), ' ',
                                COALESCE(ceu.last_name, '')
                            ) AS full_name,
                            cd.designation_id,
                            cd.designation_name,
                            ceud.date_of_joining,
                            CASE
                                WHEN is_probation_extend = 'Y' THEN 'Probation Extend'
                                WHEN is_terminated = 'Y' THEN 'Terminated'
                                WHEN employee_confirm = 'Y' THEN 'Confirmed'
                                ELSE 'Pending'
                            END AS employee_status,
                            CONCAT(
                                COALESCE(mgr.first_name, ''), ' ',
                                COALESCE(mgr.middle_name, ''), ' ',
                                COALESCE(mgr.last_name, '')
                            ) AS manager_name,
                            SUM(CASE WHEN cept.phase = 1 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_one_points,
                            SUM(CASE WHEN cept.phase = 2 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_two_points,
                            SUM(CASE WHEN cept.phase = 3 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_three_points,
                            SUM(CASE WHEN cept.phase = 4 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_four_points,
                            SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) AS total_score,
                            COUNT(cept.progress_id) * 10 AS max_possible_score,
                            CASE 
                                WHEN COUNT(cept.progress_id) > 0 
                                THEN ROUND((SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) / (COUNT(cept.progress_id) * 10.0)) * 100, 2)
                                ELSE 0 
                            END AS performance_analysis,
                            CASE 
                                WHEN COUNT(cept.progress_id) > 0 
                                THEN ROUND(SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) / 4.0, 2)
                                ELSE 0 
                            END AS avg_score
                        FROM
                            ci_erp_users ceu
                        INNER JOIN
                            ci_erp_users_details ceud ON ceu.id = ceud.user_id
                        LEFT JOIN
                            ci_designations AS cd ON ceud.designation_id = cd.designation_id
                        LEFT JOIN
                            ci_erp_users mgr ON ceud.manager = mgr.id
                        LEFT JOIN
                            ci_employee_progress_tracking AS cept ON ceu.id = cept.emp_id      
                        WHERE
                            ceud.manager = %s
                        GROUP BY
                            ceu.id, cd.designation_name, ceud.date_of_joining, mgr.id
                        ORDER BY
                            ceu.id DESC;
                    """
                    cursor.execute(query, [user_id])
                    columns = [col[0] for col in cursor.description]
                    data = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
           
                elif role_id == 14:     # head
 
                    # first find all line managers under Head
 
                    cursor.execute("""select ceud.user_id as line_mgrs from ci_erp_users_details ceud where ceud.manager = %s""", [user_id])
 
                    rows = cursor.fetchall()
                    line_mgrs = [row[0] for row in rows]  # [12, 13, 14]

                    if not line_mgrs:
                        raise ValueError({"status": "error", "message": "No line managers found"})
                    
                    placeholders = ','.join(['%s'] * len(line_mgrs))

                    # print("line_mgrs: ", line_mgrs)
 
                    query = f"""
                        SELECT
                            ceu.id as user_id, ceu.username as emp_id,
                            CONCAT(
                                COALESCE(ceu.first_name, ''), ' ',
                                COALESCE(ceu.middle_name, ''), ' ',
                                COALESCE(ceu.last_name, '')
                            ) AS full_name,
                            cd.designation_id,
                            cd.designation_name,
                            ceud.date_of_joining,
                            CASE
                                WHEN is_probation_extend = 'Y' THEN 'Extended'
                                WHEN is_terminated = 'Y' THEN 'Terminated'
                                WHEN employee_confirm = 'Y' THEN 'Confirmed'
                                ELSE 'Pending'
                            END AS employee_status,
                            CONCAT(
                                COALESCE(mgr.first_name, ''), ' ',
                                COALESCE(mgr.middle_name, ''), ' ',
                                COALESCE(mgr.last_name, '')
                            ) AS manager_name,
                            SUM(CASE WHEN cept.phase = 1 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_one_points,
                            SUM(CASE WHEN cept.phase = 2 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_two_points,
                            SUM(CASE WHEN cept.phase = 3 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_three_points,
                            SUM(CASE WHEN cept.phase = 4 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_four_points,
                            SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) AS total_score,
                            COUNT(cept.progress_id) * 10 AS max_possible_score,
                            CASE 
                                WHEN COUNT(cept.progress_id) > 0 
                                THEN ROUND((SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) / (COUNT(cept.progress_id) * 10.0)) * 100, 2)
                                ELSE 0 
                            END AS performance_analysis,
                            CASE 
                                WHEN COUNT(cept.progress_id) > 0 
                                THEN ROUND(SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) / 4.0, 2)
                                ELSE 0 
                            END AS avg_score
                        FROM
                            ci_erp_users ceu
                        INNER JOIN
                            ci_erp_users_details ceud ON ceu.id = ceud.user_id
                        LEFT JOIN
                            ci_designations AS cd ON ceud.designation_id = cd.designation_id
                        LEFT JOIN
                            ci_erp_users mgr ON ceud.manager = mgr.id
                        LEFT JOIN
                            ci_employee_progress_tracking AS cept ON ceu.id = cept.emp_id      
                        WHERE
                            ceud.manager IN ({placeholders})
                        GROUP BY
                            ceu.id, cd.designation_name, ceud.date_of_joining, mgr.id
                        ORDER BY
                            ceu.id DESC;
                    """
                    cursor.execute(query, line_mgrs)
                    columns = [col[0] for col in cursor.description]
                    data = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
 
                elif role_id in [5, 7]:             #hr, admin
 
                    query = """
                        SELECT
                            ceu.id as user_id, ceu.username as emp_id,
                            CONCAT(
                                COALESCE(ceu.first_name, ''), ' ',
                                COALESCE(ceu.middle_name, ''), ' ',
                                COALESCE(ceu.last_name, '')
                            ) AS full_name,
                            cd.designation_id,
                            cd.designation_name,
                            ceud.date_of_joining,
                            CASE
                                WHEN is_probation_extend = 'Y' THEN 'Probation Extend'
                                WHEN is_terminated = 'Y' THEN 'Terminated'
                                WHEN employee_confirm = 'Y' THEN 'Confirmed'
                                ELSE 'Pending'
                            END AS employee_status,
                            CONCAT(
                                COALESCE(mgr.first_name, ''), ' ',
                                COALESCE(mgr.middle_name, ''), ' ',
                                COALESCE(mgr.last_name, '')
                            ) AS manager_name,
                            SUM(CASE WHEN cept.phase = 1 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_one_points,
                            SUM(CASE WHEN cept.phase = 2 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_two_points,
                            SUM(CASE WHEN cept.phase = 3 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_three_points,
                            SUM(CASE WHEN cept.phase = 4 THEN COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0) ELSE 0 END) AS phase_four_points,
                            SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) AS total_score,
                            COUNT(cept.progress_id) * 10 AS max_possible_score,
                            CASE 
                                WHEN COUNT(cept.progress_id) > 0 
                                THEN ROUND((SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) / (COUNT(cept.progress_id) * 10.0)) * 100, 2)
                                ELSE 0 
                            END AS performance_analysis,
                            CASE 
                                WHEN COUNT(cept.progress_id) > 0 
                                THEN ROUND(SUM(COALESCE(points_by_hr, 0) + COALESCE(points_by_lm, 0) + COALESCE(points_by_head, 0)) / 4.0, 2)
                                ELSE 0
                            END AS avg_score
                        FROM
                            ci_erp_users ceu
                        INNER JOIN
                            ci_erp_users_details ceud ON ceu.id = ceud.user_id
                        LEFT JOIN
                            ci_designations AS cd ON ceud.designation_id = cd.designation_id
                        LEFT JOIN
                            ci_erp_users mgr ON ceud.manager = mgr.id
                        LEFT JOIN
                            ci_employee_progress_tracking AS cept ON ceu.id = cept.emp_id
                        GROUP BY
                            ceu.id, cd.designation_name, ceud.date_of_joining, mgr.id
                        ORDER BY
                            ceu.id DESC;
                    """
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    data = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
 
            return Response(data, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Live Done 

        
        
        
        # Save Overall Analysis - Employee Confirmation 

# GEt Phase Wise Marks 

from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status

from django.db import connection
 
# class GetEmployeeOverAllPhaseWiseMarks(APIView):

#     def get(self, request):

#         user_id = request.GET.get("user_id")

#         if not user_id:

#             return Response({

#                 "status": "error",

#                 "message": "Missing 'user_id' parameter"

#             }, status=status.HTTP_400_BAD_REQUEST)
 
#         try:

#             with connection.cursor() as cursor:

#                 query = """

#                     SELECT 

#                         CONCAT(

#                             COALESCE(ceu.first_name, ''), ' ',

#                             COALESCE(ceu.middle_name, ''), ' ',

#                             COALESCE(ceu.last_name, '')

#                         ) AS full_name,
 
#                         cd.designation_name,

#                         ceud.date_of_joining,
 
#                         CASE 

#                             WHEN is_probation_extend = 'Y' THEN 'Probation Extend'

#                             WHEN is_terminated = 'Y' THEN 'Terminated'

#                             WHEN employee_confirm = 'Y' THEN 'Confirmed'

#                             ELSE 'Pending' 

#                         END AS employee_status,
 
#                         CONCAT(

#                             COALESCE(mgr.first_name, ''), ' ',

#                             COALESCE(mgr.middle_name, ''), ' ',

#                             COALESCE(mgr.last_name, '')

#                         ) AS manager_name,
 
#                         SUM(CASE WHEN cept.phase = 1 THEN points_by_lm ELSE 0 END) AS phase1_lm,

#                         SUM(CASE WHEN cept.phase = 2 THEN points_by_lm ELSE 0 END) AS phase2_lm,

#                         SUM(CASE WHEN cept.phase = 3 THEN points_by_lm ELSE 0 END) AS phase3_lm,

#                         SUM(CASE WHEN cept.phase = 4 THEN points_by_lm ELSE 0 END) AS phase4_lm,
 
#                         SUM(CASE WHEN cept.phase = 1 THEN points_by_head ELSE 0 END) AS phase1_head,

#                         SUM(CASE WHEN cept.phase = 2 THEN points_by_head ELSE 0 END) AS phase2_head,

#                         SUM(CASE WHEN cept.phase = 3 THEN points_by_head ELSE 0 END) AS phase3_head,

#                         SUM(CASE WHEN cept.phase = 4 THEN points_by_head ELSE 0 END) AS phase4_head,
 
#                         SUM(CASE WHEN cept.phase = 1 THEN points_by_hr ELSE 0 END) AS phase1_hr,

#                         SUM(CASE WHEN cept.phase = 2 THEN points_by_hr ELSE 0 END) AS phase2_hr,

#                         SUM(CASE WHEN cept.phase = 3 THEN points_by_hr ELSE 0 END) AS phase3_hr,

#                         SUM(CASE WHEN cept.phase = 4 THEN points_by_hr ELSE 0 END) AS phase4_hr
 
#                     FROM 

#                         ci_erp_users AS ceu

#                     INNER JOIN 

#                         ci_erp_users_details AS ceud ON ceu.id = ceud.user_id

#                     INNER JOIN 

#                         ci_designations AS cd ON ceud.designation_id = cd.designation_id

#                     INNER JOIN 

#                         ci_employee_progress_tracking AS cept ON ceu.id = cept.emp_id

#                     LEFT JOIN 

#                         ci_erp_users AS mgr ON ceud.manager = mgr.id 

#                     WHERE 

#                         ceud.user_id = %s

#                     GROUP BY 

#                         ceu.id, cd.designation_name, ceud.date_of_joining, mgr.id

#                 """

#                 cursor.execute(query, [user_id])

#                 columns = [col[0] for col in cursor.description]

#                 row = cursor.fetchone()
 
#                 if row:

#                     data = dict(zip(columns, row))

#                 else:

#                     return Response({

#                         "status": "error",

#                         "message": f"No data found for user_id = {user_id}"

#                     }, status=status.HTTP_404_NOT_FOUND)
 
#             return Response({

#                 "status": "success",

#                 "data": data

#             }, status=status.HTTP_200_OK)
 
#         except Exception as e:

#             return Response({

#                 "status": "error",

#                 "message": str(e)

#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetEmployeeOverAllPhaseWiseMarks(APIView):
 
    def get(self, request):
        user_id = request.GET.get("user_id")
 
        if not user_id:
            return Response({
                "status": "error",
                "message": "Missing 'user_id' parameter"
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            with connection.cursor() as cursor:
                # query = """
                #     SELECT 
                #         CONCAT(
                #             COALESCE(ceu.first_name, ''), ' ',
                #             COALESCE(ceu.middle_name, ''), ' ',
                #             COALESCE(ceu.last_name, '')
                #         ) AS full_name,
                #         cd.designation_name,
                #         ceud.date_of_joining,
                #         CASE 
                #             WHEN is_probation_extend = 'Y' THEN 'Probation Extend'
                #             WHEN is_terminated = 'Y' THEN 'Terminated'
                #             WHEN employee_confirm = 'Y' THEN 'Confirmed'
                #             ELSE 'Pending' 
                #         END AS employee_status,
                #         CONCAT(
                #             COALESCE(mgr.first_name, ''), ' ',
                #             COALESCE(mgr.middle_name, ''), ' ',
                #             COALESCE(mgr.last_name, '')
                #         ) AS manager_name,
                #         SUM(CASE WHEN cept.phase = 1 THEN points_by_lm ELSE 0 END) AS phase1_lm,
                #         SUM(CASE WHEN cept.phase = 2 THEN points_by_lm ELSE 0 END) AS phase2_lm,
                #         SUM(CASE WHEN cept.phase = 3 THEN points_by_lm ELSE 0 END) AS phase3_lm,
                #         SUM(CASE WHEN cept.phase = 4 THEN points_by_lm ELSE 0 END) AS phase4_lm,
                #         SUM(CASE WHEN cept.phase = 1 THEN points_by_head ELSE 0 END) AS phase1_head,
                #         SUM(CASE WHEN cept.phase = 2 THEN points_by_head ELSE 0 END) AS phase2_head,
                #         SUM(CASE WHEN cept.phase = 3 THEN points_by_head ELSE 0 END) AS phase3_head,
                #         SUM(CASE WHEN cept.phase = 4 THEN points_by_head ELSE 0 END) AS phase4_head,
                #         SUM(CASE WHEN cept.phase = 1 THEN points_by_hr ELSE 0 END) AS phase1_hr,
                #         SUM(CASE WHEN cept.phase = 2 THEN points_by_hr ELSE 0 END) AS phase2_hr,
                #         SUM(CASE WHEN cept.phase = 3 THEN points_by_hr ELSE 0 END) AS phase3_hr,
                #         SUM(CASE WHEN cept.phase = 4 THEN points_by_hr ELSE 0 END) AS phase4_hr,
                #         ceoa.performance_analysis as final_hr_comment
                #     FROM 
                #         ci_erp_users AS ceu
                #     INNER JOIN 
                #         ci_erp_users_details AS ceud ON ceu.id = ceud.user_id
                #     INNER JOIN 
                #         ci_designations AS cd ON ceud.designation_id = cd.designation_id
                #     INNER JOIN 
                #         ci_employee_progress_tracking AS cept ON ceu.id = cept.emp_id
                #     INNER JOIN
                #         ci_employee_overall_analysis AS ceoa ON ceu.id = ceoa.user_id
                #     LEFT JOIN 
                #         ci_erp_users AS mgr ON ceud.manager = mgr.id 
                #     WHERE 
                #         ceud.user_id = %s
                #     GROUP BY 
                #         ceu.id, cd.designation_name, ceud.date_of_joining, mgr.id
 
                # """
 
                query = """
                        SELECT 
                        CONCAT(
                            COALESCE(ceu.first_name, ''), ' ',
                            COALESCE(ceu.middle_name, ''), ' ',
                            COALESCE(ceu.last_name, '')
                        ) AS full_name,
                        cd.designation_name,
                        ceud.date_of_joining,
                        CASE 
                            WHEN is_probation_extend = 'Y' THEN 'Extended'
                            WHEN is_terminated = 'Y' THEN 'Terminated'
                            WHEN employee_confirm = 'Y' THEN 'Confirmed'
                            ELSE 'Pending' 
                        END AS employee_status,
                        CONCAT(
                            COALESCE(mgr.first_name, ''), ' ',
                            COALESCE(mgr.middle_name, ''), ' ',
                            COALESCE(mgr.last_name, '')
                        ) AS manager_name,
                        SUM(CASE WHEN cept.phase = 1 THEN points_by_lm ELSE 0 END) AS phase1_lm,
                        SUM(CASE WHEN cept.phase = 2 THEN points_by_lm ELSE 0 END) AS phase2_lm,
                        SUM(CASE WHEN cept.phase = 3 THEN points_by_lm ELSE 0 END) AS phase3_lm,
                        SUM(CASE WHEN cept.phase = 4 THEN points_by_lm ELSE 0 END) AS phase4_lm,
                        SUM(CASE WHEN cept.phase = 1 THEN points_by_head ELSE 0 END) AS phase1_head,
                        SUM(CASE WHEN cept.phase = 2 THEN points_by_head ELSE 0 END) AS phase2_head,
                        SUM(CASE WHEN cept.phase = 3 THEN points_by_head ELSE 0 END) AS phase3_head,
                        SUM(CASE WHEN cept.phase = 4 THEN points_by_head ELSE 0 END) AS phase4_head,
                        SUM(CASE WHEN cept.phase = 1 THEN points_by_hr ELSE 0 END) AS phase1_hr,
                        SUM(CASE WHEN cept.phase = 2 THEN points_by_hr ELSE 0 END) AS phase2_hr,
                        SUM(CASE WHEN cept.phase = 3 THEN points_by_hr ELSE 0 END) AS phase3_hr,
                        SUM(CASE WHEN cept.phase = 4 THEN points_by_hr ELSE 0 END) AS phase4_hr,
                        ceoa.performance_analysis as final_hr_comment
                    FROM 
                        ci_erp_users AS ceu
                    INNER JOIN 
                        ci_erp_users_details AS ceud ON ceu.id = ceud.user_id
                    INNER JOIN 
                        ci_designations AS cd ON ceud.designation_id = cd.designation_id
                    LEFT JOIN 
                        ci_employee_progress_tracking AS cept ON ceu.id = cept.emp_id
					LEFT JOIN (
						SELECT user_id, performance_analysis
						FROM ci_employee_overall_analysis a
						WHERE a.created_at = (
							SELECT MAX(b.created_at) 
							FROM ci_employee_overall_analysis b 
							WHERE b.user_id = a.user_id
						)
					) ceoa ON ceu.id = ceoa.user_id
                    LEFT JOIN 
                        ci_erp_users AS mgr ON ceud.manager = mgr.id 
                    WHERE 
                        ceud.user_id = %s
                    GROUP BY 
                        ceu.id, cd.designation_name, ceud.date_of_joining, mgr.id;
                """
 
                cursor.execute(query, [user_id])
                columns = [col[0] for col in cursor.description]
                row = cursor.fetchone()
                if row:
                    data = dict(zip(columns, row))
                else:
                    return Response({
                        "status": "error",
                        "message": f"No data found for user_id = {user_id}"
                    }, status=status.HTTP_404_NOT_FOUND)
 
            return Response({
                "status": "success",
                "data": data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status

from django.db import connection
 
class SaveEmployeeOverallAnalysis(APIView):

    def post(self, request):

        try:

            data = request.data
 
            user_id = data.get('user_id')

            emp_id = data.get('emp_id')

            performance_analysis = data.get('performance_analysis')

            kra_kpi_total = data.get('kra_kpi_total')

            average = data.get('average')

            percent_achievement = data.get('percent_achievement')

            comment_by_lm = data.get('comment_by_lm')

            comment_by_hr = data.get('comment_by_hr')

            comment_by_head = data.get('comment_by_head')
 
            with connection.cursor() as cursor:

                insert_query = """

                    INSERT INTO ci_employee_overall_analysis (

                        user_id, emp_id, performance_analysis, 

                        kra_kpi_total, average, percent_achievement,

                        comment_by_lm, comment_by_hr, comment_by_head

                    )

                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)

                """

                cursor.execute(insert_query, [

                    user_id, emp_id, performance_analysis,

                    kra_kpi_total, average, percent_achievement,

                    comment_by_lm, comment_by_hr, comment_by_head

                ])
 
            return Response({"status": "success", "message": "Data inserted successfully."}, status=status.HTTP_201_CREATED)
 
        except Exception as e:

            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
 
# class EmployeeLeaveRequestGetReport(APIView):
#     def get(self, request):
#         try:
#             # Get parameters from query string
#             year = request.query_params.get('year')
#             month = request.query_params.get('month')
 
#             # Validate inputs
#             if not year or not month:
#                 return Response(
#                     {"detail": "Year and month are required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
 
#             query = """
#                 SELECT
#                     eud.user_id,
#                     eud.employee_id,
#                     d.department_name,
#                     deg.designation_name,
#                     dv.division_name,
#                     'null' AS sub_division,
#                         'null' AS headquarter,
#                         'null' AS level,
#                     eud.manager as manager,
#                     CONCAT(
#                         COALESCE(mgr.first_name, ''), ' ',
#                         COALESCE(mgr.middle_name, ''), ' ',
#                         COALESCE(mgr.last_name, '')
#                     ) AS manager_name,
#                     eud.date_of_joining,
#                     cla.created_at,
#                     ec.category_name AS leave_type,
#                     cla.from_date AS start_date,
#                     cla.to_date AS end_date,
#                     cla.no_of_days,
#                     cla.reason,
#                     cla.remarks
#                 FROM ci_erp_users AS eu
#                 INNER JOIN ci_erp_users_details AS eud
#                     ON eu.id = eud.user_id
#                 LEFT JOIN ci_division AS dv
#                     ON eud.division_id = dv.division_id
#                 LEFT JOIN ci_designations AS deg
#                     ON eud.designation_id = deg.designation_id
#                 LEFT JOIN ci_departments AS d
#                     ON d.department_id = eud.department_id
#                 LEFT JOIN ci_leave_applications AS cla
#                     ON eud.employee_id = cla.employee_id
#                 LEFT JOIN ci_erp_constants AS ec
#                     ON cla.leave_type_id = ec.constants_id
#                 LEFT JOIN ci_erp_users AS mgr
#                     ON eud.manager = mgr.id
#                 WHERE YEAR(cla.created_at) = %s
#                   AND MONTH(cla.created_at) = %s
#             """
 
#             with connection.cursor() as cursor:
#                 cursor.execute(query, [year, month])
#                 columns = [col[0] for col in cursor.description]
#                 results = [dict(zip(columns, row)) for row in cursor.fetchall()]
 
#             return Response(results, status=status.HTTP_200_OK)
 
#         except Exception as e:
#             return Response(
#                 {"detail": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class EmployeeLeaveRequestGetReport(APIView):
    def get(self, request):
        try:
            # Get parameters from query string
            year = request.query_params.get("year")
            month = request.query_params.get("month")

            # Validate inputs
            if not year or not month:
                return Response(
                    {"detail": "Year and month are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            query = """
                SELECT 
    eud.user_id,
    eud.employee_id,
    d.department_name,
    deg.designation_name,
    dv.division_name,
    eud.manager as manager_id,
    CONCAT(
        COALESCE(mgr.first_name, ''), ' ',
        COALESCE(mgr.middle_name, ''), ' ',
        COALESCE(mgr.last_name, '')
    ) AS manager_name,
    eud.date_of_joining,
    cla.created_at,
    ec.category_name AS leave_type,
    cla.from_date AS start_date,
    cla.to_date AS end_date,
    cla.no_of_days,
    cla.reason,
    cla.remarks,
    'null' AS sub_division_name,
    'null' AS headquarter,
    'null' AS level
FROM ci_erp_users AS eu
INNER JOIN ci_erp_users_details AS eud 
    ON eu.id = eud.user_id
LEFT JOIN ci_division AS dv 
    ON eud.division_id = dv.division_id
LEFT JOIN ci_designations AS deg 
    ON eud.designation_id = deg.designation_id
LEFT JOIN ci_departments AS d 
    ON d.department_id = eud.department_id
LEFT JOIN ci_leave_applications AS cla 
    ON eud.employee_id = cla.employee_id
LEFT JOIN ci_erp_constants AS ec 
    ON cla.leave_type_id = ec.constants_id
LEFT JOIN ci_erp_users AS mgr 
    ON eud.manager = mgr.id 
WHERE (
        (YEAR(cla.from_date) = %s AND MONTH(cla.from_date) = %s)
     OR (YEAR(cla.to_date) = %s AND MONTH(cla.to_date) = %s)
     OR (cla.from_date <= LAST_DAY(CONCAT(%s, '-', %s, '-01'))
         AND cla.to_date >= CONCAT(%s, '-', %s, '-01'))
      );

            """
            params = [year, month, year, month, year, month, year, month]
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

 
class GetEmployeeTypeFiveDetails(APIView):
    def post(self, request):
        # Get payload data
        req_type = request.data.get('type')
        user_id = request.data.get('user_id')
 
        # Validate request payload
        if req_type is None or user_id is None:
            return Response({"error": "Missing type or user_id"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Check if type is 5
        if str(req_type) == "5":
            query = """
                SELECT  pan_number, esic_number, pf_number ,aadhar_no
                FROM ci_erp_users_details
                WHERE user_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(query, [user_id])
                row = cursor.fetchone()
 
            if not row:
                return Response({"message": "No data found"}, status=status.HTTP_404_NOT_FOUND)
 
            columns = [
                "pan_number", "esic_number", "pf_number" ,"aadhar_no"
 
            ]
            result = dict(zip(columns, row))
 
            return Response(result, status=status.HTTP_200_OK)
 
        return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
import calendar
import datetime
 
class EmployeeMonthlycheckINCheckOUTGetReport(APIView):
    def get(self, request):
        month = request.query_params.get("month")  # e.g. 8
        year = request.query_params.get("year")    # e.g. 2025
 
        if not (month and year):
            return Response(
                {"detail": "Missing required parameters: month, year"},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        CONCAT(
                            COALESCE(eu.first_name, ''), ' ',
                            COALESCE(eu.middle_name, ''), ' ',
                            COALESCE(eu.last_name, '')
                        ) AS employee_name,
                        cbd.attendance_date,
                        cbd.clock_in,
                        cbd.clock_out
                    FROM ci_erp_users AS eu
                    INNER JOIN ci_erp_users_details AS eud
                        ON eu.id = eud.user_id
                    LEFT JOIN ci_biomatric_data AS cbd
                        ON eud.user_id = cbd.userid
                    WHERE MONTH(cbd.attendance_date) = %s
                      AND YEAR(cbd.attendance_date) = %s
                    ORDER BY eu.id, cbd.attendance_date
                """
                cursor.execute(query, [month, year])
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
 
            data = [dict(zip(columns, row)) for row in rows]
 
            # Month/day scaffolding
            year_i, month_i = int(year), int(month)
            days_in_month = calendar.monthrange(year_i, month_i)[1]
            day_name_map = {
                d: datetime.date(year_i, month_i, d).strftime('%A')  # Monday, Tuesday, ...
                for d in range(1, days_in_month + 1)
            }
 
            # Build per-employee objects
            employees = {}
 
            def init_employee(name: str):
                # Pre-fill all days with day names and blank times
                emp = {"name": name}
                for d in range(1, days_in_month + 1):
                    emp[str(d)] = {"day": day_name_map[d], "in": "", "out": ""}
                return emp
 
            for row in data:
                name = row["employee_name"]
                att_date = row["attendance_date"]
                if not att_date:
                    continue  # safety
 
                day_num = att_date.day
 
                # Safe string conversion for times
                def fmt_time(value):
                    if not value:
                        return ""
                    return value.strftime("%H:%M") if hasattr(value, "strftime") else str(value)[:5]
 
                in_time = fmt_time(row["clock_in"])
                out_time = fmt_time(row["clock_out"])
 
                if name not in employees:
                    employees[name] = init_employee(name)
 
                employees[name][str(day_num)]["in"] = in_time
                employees[name][str(day_num)]["out"] = out_time
 
            # In case some employees in the month have zero records (rare with the WHERE), you could add them here.
 
            result = list(employees.values())
            return Response(result, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
       
       
       
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
 
class AllEmployeeLeaveSummaryReportGetReport(APIView):
    def get(self, request):
        try:
            year = request.GET.get("year")
 
            with connection.cursor() as cursor:
                query = """
                SELECT eud.user_id, eud.employee_id, CONCAT( COALESCE(eu.first_name, ''), ' ', COALESCE(eu.middle_name, ''), ' ', COALESCE(eu.last_name, '') ) AS employee_name, d.department_name, deg.designation_name, dv.division_name,
                'null' AS sub_division,
                        'null' AS headquarter,
                        'null' AS level,           
                
                eud.manager AS manager_id, CONCAT( COALESCE(mgr.first_name, ''), ' ', COALESCE(mgr.middle_name, ''), ' ', COALESCE(mgr.last_name, '') ) AS manager_name, eud.date_of_joining, /* ===================== JANUARY ===================== */ SUM(CASE WHEN MONTH(cla.created_at) = 1 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Jan_CL, SUM(CASE WHEN MONTH(cla.created_at) = 1 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Jan_ML, SUM(CASE WHEN MONTH(cla.created_at) = 1 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Jan_PL, SUM(CASE WHEN MONTH(cla.created_at) = 1 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Jan_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 1 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Jan_LWP, /* ===================== FEBRUARY ==================== */ SUM(CASE WHEN MONTH(cla.created_at) = 2 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Feb_CL, SUM(CASE WHEN MONTH(cla.created_at) = 2 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Feb_ML, SUM(CASE WHEN MONTH(cla.created_at) = 2 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Feb_PL, SUM(CASE WHEN MONTH(cla.created_at) = 2 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Feb_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 2 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Feb_LWP, /* ===================== MARCH ======================= */ SUM(CASE WHEN MONTH(cla.created_at) = 3 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Mar_CL, SUM(CASE WHEN MONTH(cla.created_at) = 3 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Mar_ML, SUM(CASE WHEN MONTH(cla.created_at) = 3 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Mar_PL, SUM(CASE WHEN MONTH(cla.created_at) = 3 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Mar_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 3 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Mar_LWP, /* ===================== APRIL ======================= */ SUM(CASE WHEN MONTH(cla.created_at) = 4 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Apr_CL, SUM(CASE WHEN MONTH(cla.created_at) = 4 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Apr_ML, SUM(CASE WHEN MONTH(cla.created_at) = 4 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Apr_PL, SUM(CASE WHEN MONTH(cla.created_at) = 4 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Apr_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 4 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Apr_LWP, /* ===================== MAY ========================= */ SUM(CASE WHEN MONTH(cla.created_at) = 5 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS May_CL, SUM(CASE WHEN MONTH(cla.created_at) = 5 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS May_ML, SUM(CASE WHEN MONTH(cla.created_at) = 5 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS May_PL, SUM(CASE WHEN MONTH(cla.created_at) = 5 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS May_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 5 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS May_LWP, /* ===================== JUNE ======================== */ SUM(CASE WHEN MONTH(cla.created_at) = 6 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Jun_CL, SUM(CASE WHEN MONTH(cla.created_at) = 6 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Jun_ML, SUM(CASE WHEN MONTH(cla.created_at) = 6 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Jun_PL, SUM(CASE WHEN MONTH(cla.created_at) = 6 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Jun_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 6 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Jun_LWP, /* ===================== JULY ======================== */ SUM(CASE WHEN MONTH(cla.created_at) = 7 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Jul_CL, SUM(CASE WHEN MONTH(cla.created_at) = 7 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Jul_ML, SUM(CASE WHEN MONTH(cla.created_at) = 7 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Jul_PL, SUM(CASE WHEN MONTH(cla.created_at) = 7 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Jul_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 7 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Jul_LWP, /* ===================== AUGUST ====================== */ SUM(CASE WHEN MONTH(cla.created_at) = 8 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Aug_CL, SUM(CASE WHEN MONTH(cla.created_at) = 8 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Aug_ML, SUM(CASE WHEN MONTH(cla.created_at) = 8 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Aug_PL, SUM(CASE WHEN MONTH(cla.created_at) = 8 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Aug_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 8 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Aug_LWP, /* ===================== SEPTEMBER =================== */ SUM(CASE WHEN MONTH(cla.created_at) = 9 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Sep_CL, SUM(CASE WHEN MONTH(cla.created_at) = 9 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Sep_ML, SUM(CASE WHEN MONTH(cla.created_at) = 9 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Sep_PL, SUM(CASE WHEN MONTH(cla.created_at) = 9 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Sep_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 9 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Sep_LWP, /* ===================== OCTOBER ===================== */ SUM(CASE WHEN MONTH(cla.created_at) = 10 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Oct_CL, SUM(CASE WHEN MONTH(cla.created_at) = 10 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Oct_ML, SUM(CASE WHEN MONTH(cla.created_at) = 10 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Oct_PL, SUM(CASE WHEN MONTH(cla.created_at) = 10 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Oct_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 10 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Oct_LWP, /* ===================== NOVEMBER ==================== */ SUM(CASE WHEN MONTH(cla.created_at) = 11 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Nov_CL, SUM(CASE WHEN MONTH(cla.created_at) = 11 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Nov_ML, SUM(CASE WHEN MONTH(cla.created_at) = 11 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Nov_PL, SUM(CASE WHEN MONTH(cla.created_at) = 11 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Nov_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 11 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Nov_LWP, /* ===================== DECEMBER ==================== */ SUM(CASE WHEN MONTH(cla.created_at) = 12 AND cla.leave_type_id = 184 THEN 1 ELSE 0 END) AS Dec_CL, SUM(CASE WHEN MONTH(cla.created_at) = 12 AND cla.leave_type_id = 185 THEN 1 ELSE 0 END) AS Dec_ML, SUM(CASE WHEN MONTH(cla.created_at) = 12 AND cla.leave_type_id = 289 THEN 1 ELSE 0 END) AS Dec_PL, SUM(CASE WHEN MONTH(cla.created_at) = 12 AND cla.leave_type_id = 187 THEN 1 ELSE 0 END) AS Dec_MTL, SUM(CASE WHEN MONTH(cla.created_at) = 12 AND cla.leave_type_id = 1749 THEN 1 ELSE 0 END) AS Dec_LWP
 
                FROM ci_erp_users AS eu
                INNER JOIN ci_erp_users_details AS eud
                    ON eu.id = eud.user_id
                LEFT JOIN ci_division AS dv
                    ON eud.division_id = dv.division_id
                LEFT JOIN ci_designations AS deg
                    ON eud.designation_id = deg.designation_id
                LEFT JOIN ci_departments AS d
                    ON d.department_id = eud.department_id
                LEFT JOIN ci_leave_applications AS cla
                    ON eud.employee_id = cla.employee_id
                LEFT JOIN ci_erp_users AS mgr
                    ON eud.manager = mgr.id
                WHERE YEAR(cla.created_at) = %s
                GROUP BY
                    eud.user_id, eud.employee_id, eu.first_name, eu.middle_name, eu.last_name,
                    d.department_name, deg.designation_name, dv.division_name,
                    eud.manager, mgr.first_name, mgr.middle_name, mgr.last_name,
                    eud.date_of_joining
                ORDER BY eud.employee_id;
                """
 
                cursor.execute(query, [year])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
 
                data = [dict(zip(columns, row)) for row in rows]
 
            return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
 
 
class EmployeeConfirmationReportGetReport(APIView):
    """
    API to fetch employee performance analysis
    """
 
    def get(self, request):
        try:
            # Get year from frontend request body
            # year = request.data.get("year")
            year = request.query_params.get("year")
 
            if not year:
                return Response(
                    {"error": "Year is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
 
            query = """
                SELECT
                    eud.user_id,
                    eud.employee_id,
                    CONCAT(
                        COALESCE(eu.first_name, ''), ' ',
                        COALESCE(eu.middle_name, ''), ' ',
                        COALESCE(eu.last_name, '')
                    ) AS employee_name,
                    d.department_name,
                    deg.designation_name,
                    dv.division_name,
                    eud.manager AS manager_id,
                    CONCAT(
                        COALESCE(mgr.first_name, ''), ' ',
                        COALESCE(mgr.middle_name, ''), ' ',
                        COALESCE(mgr.last_name, '')
                    ) AS manager_name,
                    eud.date_of_joining,
 
                    -- Phase totals
                    (SUM(CASE WHEN cpt.phase = 1 THEN cpt.points_by_lm ELSE 0 END) +
                     SUM(CASE WHEN cpt.phase = 1 THEN cpt.points_by_hr ELSE 0 END) +
                     SUM(CASE WHEN cpt.phase = 1 THEN cpt.points_by_head ELSE 0 END)) AS phase1_total,
 
                    (SUM(CASE WHEN cpt.phase = 2 THEN cpt.points_by_lm ELSE 0 END) +
                     SUM(CASE WHEN cpt.phase = 2 THEN cpt.points_by_hr ELSE 0 END) +
                     SUM(CASE WHEN cpt.phase = 2 THEN cpt.points_by_head ELSE 0 END)) AS phase2_total,
 
                    (SUM(CASE WHEN cpt.phase = 3 THEN cpt.points_by_lm ELSE 0 END) +
                     SUM(CASE WHEN cpt.phase = 3 THEN cpt.points_by_hr ELSE 0 END) +
                     SUM(CASE WHEN cpt.phase = 3 THEN cpt.points_by_head ELSE 0 END)) AS phase3_total,
 
                    (SUM(CASE WHEN cpt.phase = 4 THEN cpt.points_by_lm ELSE 0 END) +
                     SUM(CASE WHEN cpt.phase = 4 THEN cpt.points_by_hr ELSE 0 END) +
                     SUM(CASE WHEN cpt.phase = 4 THEN cpt.points_by_head ELSE 0 END)) AS phase4_total,
 
                    (
                        (
                            SUM(CASE WHEN cpt.phase = 1 THEN cpt.points_by_lm ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 1 THEN cpt.points_by_hr ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 1 THEN cpt.points_by_head ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 2 THEN cpt.points_by_lm ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 2 THEN cpt.points_by_hr ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 2 THEN cpt.points_by_head ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 3 THEN cpt.points_by_lm ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 3 THEN cpt.points_by_hr ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 3 THEN cpt.points_by_head ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 4 THEN cpt.points_by_lm ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 4 THEN cpt.points_by_hr ELSE 0 END) +
                            SUM(CASE WHEN cpt.phase = 4 THEN cpt.points_by_head ELSE 0 END)
                        ) / 4.0
                    ) AS average_score,
 
                    eoa.kra_kpi_total,
                    eu.is_active AS employee_status,
                    eud.confirmation_date,
                    NULL AS `sub_division`,
                        NULL AS `level`,
                        NULL AS `headquarter`
 
                FROM ci_erp_users AS eu
                INNER JOIN ci_erp_users_details AS eud ON eu.id = eud.user_id
                LEFT JOIN ci_division AS dv ON eud.division_id = dv.division_id
                LEFT JOIN ci_designations AS deg ON eud.designation_id = deg.designation_id
                LEFT JOIN ci_departments AS d ON d.department_id = eud.department_id
                LEFT JOIN ci_erp_users AS mgr ON eud.manager = mgr.id
                LEFT JOIN ci_employee_progress_tracking AS cpt ON eu.id = cpt.emp_id
                LEFT JOIN ci_employee_overall_analysis AS eoa ON eu.id = eoa.user_id
                WHERE YEAR(eud.confirmation_date) = %s
                GROUP BY
                    eud.user_id,
                    eud.employee_id,
                    eu.first_name, eu.middle_name, eu.last_name,
                    d.department_name, deg.designation_name, dv.division_name,
                    eud.manager, mgr.first_name, mgr.middle_name, mgr.last_name,
                    eud.date_of_joining
                ORDER BY eud.employee_id;
            """
 
            with connection.cursor() as cursor:
                cursor.execute(query, [year])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
 
            return Response({"year": year, "data": results}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
# views.py
from django.db import connection, DatabaseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
 
class EmployeePIPReportGetReport(APIView):
    """
    GET: Returns employee data with hardcoded NULL PIP/TMS fields.
    Accepts optional ?year=YYYY&division_id=14 parameters.
    """
 
    def get(self, request):
        year = request.query_params.get("year")        # from ?year=2025
        division_id = request.query_params.get("division_id")  # from ?division_id=14
 
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        eud.user_id,
                        eud.employee_id,
                        CONCAT(
                            COALESCE(eu.first_name, ''), ' ',
                            COALESCE(eu.middle_name, ''), ' ',
                            COALESCE(eu.last_name, '')
                        ) AS employee_name,
                        d.department_name,
                        deg.designation_name,
                        dv.division_name,
                        NULL AS `sub_division`,
                        NULL AS `level`,
                        NULL AS `headquarter`,
                        eud.manager AS manager_id,
                        CONCAT(
                            COALESCE(mgr.first_name, ''), ' ',
                            COALESCE(mgr.middle_name, ''), ' ',
                            COALESCE(mgr.last_name, '')
                        ) AS manager_name,
                        eud.date_of_joining,
 
                        -- Hardcoded NULL fields
                        NULL AS `PIP Start Date`,
                        NULL AS `PIP End Date`,
                        NULL AS `TMS Score`,
                        NULL AS `LM Score`,
                        NULL AS `HOD Score`,
                        NULL AS `HR Score`,
                        NULL AS `Date`
 
                    FROM ci_erp_users AS eu
                    INNER JOIN ci_erp_users_details AS eud
                        ON eu.id = eud.user_id
                    LEFT JOIN ci_division AS dv
                        ON eud.division_id = dv.division_id
                    LEFT JOIN ci_designations AS deg
                        ON eud.designation_id = deg.designation_id
                    LEFT JOIN ci_departments AS d
                        ON d.department_id = eud.department_id
                    LEFT JOIN ci_erp_users AS mgr
                        ON eud.manager = mgr.id
                    WHERE (%(division_id)s IS NULL OR dv.division_id = %(division_id)s)
                    GROUP BY
                        eud.user_id, eud.employee_id, eu.first_name, eu.middle_name, eu.last_name,
                        d.department_name, deg.designation_name, dv.division_name,
                        eud.manager, mgr.first_name, mgr.middle_name, mgr.last_name,
                        eud.date_of_joining
                    ORDER BY eud.employee_id;
                """
                cursor.execute(query, {"division_id": division_id})
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
 
                results = [dict(zip(columns, row)) for row in rows]
 
            return Response(
                {
                    "year": year,
                    "division_id": division_id,
                    "count": len(results),
                    "results": results,
                },
                status=status.HTTP_200_OK,
            )
 
        except DatabaseError as e:
            return Response(
                {"detail": "Database error while fetching report.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": "Unexpected error.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
 
 
 
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
 
class EmployeePromotionGetReport(APIView):
    """
    API to fetch employee details by employee_id
    """
 
    def get(self, request):
        try:
            # Get employee_id from query params
            employee_id = request.query_params.get("employee_id")
 
            if not employee_id:
                return Response(
                    {"detail": "Employee ID is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
 
            query = """
                SELECT
                    eud.user_id,
                    eud.employee_id,
                    CONCAT(
                        COALESCE(eu.first_name, ''), ' ',
                        COALESCE(eu.middle_name, ''), ' ',
                        COALESCE(eu.last_name, '')
                    ) AS employee_name,
                    d.department_name,
                    deg.designation_name,
                    dv.division_name,
                    NULL AS sub_division,
                    NULL AS level,
                    NULL AS headquarter,
                    eud.manager AS manager_id,
                    CONCAT(
                        COALESCE(mgr.first_name, ''), ' ',
                        COALESCE(mgr.middle_name, ''), ' ',
                        COALESCE(mgr.last_name, '')
                    ) AS manager_name,
                    eud.date_of_joining,
                    NULL AS promotion_one,
                    NULL AS promotion_one_date,
                    NULL AS promotion_second,
                    NULL AS promotion_second_date
                FROM ci_erp_users AS eu
                INNER JOIN ci_erp_users_details AS eud
                    ON eu.id = eud.user_id
                LEFT JOIN ci_division AS dv
                    ON eud.division_id = dv.division_id
                LEFT JOIN ci_designations AS deg
                    ON eud.designation_id = deg.designation_id
                LEFT JOIN ci_departments AS d
                    ON d.department_id = eud.department_id
                LEFT JOIN ci_erp_users AS mgr
                    ON eud.manager = mgr.id
                WHERE eud.employee_id = %s
                GROUP BY
                    eud.user_id,
                    eud.employee_id,
                    eu.first_name,
                    eu.middle_name,
                    eu.last_name,
                    d.department_name,
                    deg.designation_name,
                    dv.division_name,
                    eud.manager,
                    mgr.first_name,
                    mgr.middle_name,
                    mgr.last_name,
                    eud.date_of_joining
                ORDER BY eud.employee_id
            """
 
            with connection.cursor() as cursor:
                cursor.execute(query, [employee_id])
                columns = [col[0] for col in cursor.description]
                result = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
 
            return Response(result, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
 
class GratuityEligibilityGetReport(APIView):
    """
    API to fetch Gratuity Eligibility Report
    """
 
    def get(self, request):
        try:
            query = """
                SELECT
                    eud.user_id,
                    eud.employee_id,
                    CONCAT(
                        COALESCE(eu.first_name, ''), ' ',
                        COALESCE(eu.middle_name, ''), ' ',
                        COALESCE(eu.last_name, '')
                    ) AS employee_name,
                    d.department_name,
                    deg.designation_name,
                    dv.division_name,
                    NULL AS sub_division,
                    NULL AS level,
                    NULL AS headquarter,
                    eud.manager AS manager_id,
                    CONCAT(
                        COALESCE(mgr.first_name, ''), ' ',
                        COALESCE(mgr.middle_name, ''), ' ',
                        COALESCE(mgr.last_name, '')
                    ) AS manager_name,
                    eud.date_of_joining ,
                    eud.date_of_leaving,
                   
                    TIMESTAMPDIFF(
                        YEAR,
                        eud.date_of_joining,
                        COALESCE(eud.date_of_leaving, CURDATE())
                    ) AS total_service_years,
 
                    CASE
                        WHEN TIMESTAMPDIFF(YEAR, eud.date_of_joining, COALESCE(eud.date_of_leaving, CURDATE())) >= 5
                            THEN 'Eligible'
                        ELSE 'Not Eligible'
                    END AS gratuity_eligibility,
 
                    eud.basic_yearly,
 
                    CASE
                        WHEN TIMESTAMPDIFF(YEAR, eud.date_of_joining, COALESCE(eud.date_of_leaving, CURDATE())) >= 5
                        THEN ROUND(
                            (eud.basic_monthly * 15 * TIMESTAMPDIFF(
                                YEAR, eud.date_of_joining, COALESCE(eud.date_of_leaving, CURDATE())
                            )) / 26, 2
                        )
                        ELSE 0
                    END AS gratuity_amount,
 
                    CASE
                        WHEN eu.is_active = 1 THEN 'Active'
                        WHEN eu.is_active = 0 THEN 'Resigned'
                        ELSE 'Unknown'
                    END AS employee_status
 
                FROM ci_erp_users AS eu
                INNER JOIN ci_erp_users_details AS eud
                    ON eu.id = eud.user_id
                LEFT JOIN ci_division AS dv
                    ON eud.division_id = dv.division_id
                LEFT JOIN ci_designations AS deg
                    ON eud.designation_id = deg.designation_id
                LEFT JOIN ci_departments AS d
                    ON d.department_id = eud.department_id
                LEFT JOIN ci_leave_applications AS cla
                    ON eud.employee_id = cla.employee_id
                LEFT JOIN ci_erp_users AS mgr
                    ON eud.manager = mgr.id
                GROUP BY
                    eud.user_id, eud.employee_id, eu.first_name, eu.middle_name, eu.last_name,
                    d.department_name, deg.designation_name, dv.division_name,
                    eud.manager, mgr.first_name, mgr.middle_name, mgr.last_name,
                    eud.date_of_joining, eud.date_of_leaving, eu.is_active, eud.basic_yearly, eud.basic_monthly
                ORDER BY eud.employee_id;
            """
 
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
 
            return Response(results, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
 
class PFReportEmployeeGetReport(APIView):
    """
    API to fetch payroll PF contribution report
    """
 
    def post(self, request):
        try:
            from_date = request.data.get("from_date")
            to_date = request.data.get("to_date")
 
            if not from_date or not to_date:
                return Response(
                    {"detail": "from_date and to_date are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
 
            query = """
                SELECT
                    cpr.employee_id,
                    cpr.employee_name,
                    NULL AS pf_number,
                    cpr.payable_days AS no_of_days,
                    cpr.basic_plus_da,
                    cpr.gross_salary,
                    eud.basic_salary,
                    eud.ctc_monthly AS salary_per_month,
 
                    -- Employee PF Contribution (12%%)
                    ROUND(cpr.basic_plus_da * 0.12, 2) AS employee_contribution,
 
                    -- Employer PF 3.67%%
                    ROUND(cpr.basic_plus_da * 0.0367, 2) AS employer_pf,
 
                    -- Employer Pension (EPS) 8.33%% (capped at 1250 if basic > 15000)
                    ROUND(
                        CASE
                            WHEN cpr.basic_plus_da > 15000
                                THEN 15000 * 0.0833
                            ELSE cpr.basic_plus_da * 0.0833
                        END, 2
                    ) AS employer_pension,
 
                    -- Employer EDLI 0.50%% (capped at 75 if basic > 15000)
                    ROUND(
                        CASE
                            WHEN cpr.basic_plus_da > 15000
                                THEN 15000 * 0.005
                            ELSE cpr.basic_plus_da * 0.005
                        END, 2
                    ) AS employer_edli,
 
                    -- Employer Admin Charges 0.50%% (capped at 75 if basic > 15000)
                    ROUND(
                        CASE
                            WHEN cpr.basic_plus_da > 15000
                                THEN 15000 * 0.005
                            ELSE cpr.basic_plus_da * 0.005
                        END, 2
                    ) AS employer_admin,
 
                    -- Total Employer Contribution
                    (
                        ROUND(cpr.basic_plus_da * 0.0367, 2) +
                        ROUND(
                            CASE
                                WHEN cpr.basic_plus_da > 15000
                                    THEN 15000 * 0.0833
                                ELSE cpr.basic_plus_da * 0.0833
                            END, 2
                        ) +
                        ROUND(
                            CASE
                                WHEN cpr.basic_plus_da > 15000
                                    THEN 15000 * 0.005
                                ELSE cpr.basic_plus_da * 0.005
                            END, 2
                        ) +
                        ROUND(
                            CASE
                                WHEN cpr.basic_plus_da > 15000
                                    THEN 15000 * 0.005
                                ELSE cpr.basic_plus_da * 0.005
                            END, 2
                        )
                    ) AS total
 
                FROM ci_payroll_report AS cpr
                INNER JOIN ci_erp_users_details AS eud
                    ON cpr.employee_id = eud.employee_id
                WHERE STR_TO_DATE(CONCAT(cpr.year, '-', cpr.month, '-01'), '%%Y-%%m-%%d')
                      BETWEEN %s AND %s;
            """
 
            with connection.cursor() as cursor:
                cursor.execute(query, [from_date, to_date])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
 
            return Response(results, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
 
class EmployeePayrollSalaryGetReport(APIView):
    """
    API to fetch payroll report based on month and year
    """
 
    def post(self, request):
        try:
            # Get params from request body
            month = request.data.get("month")
            year = request.data.get("year")
 
            if not month or not year:
                return Response(
                    {"detail": "Month and Year are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
 
            # SQL query
            query = """
                SELECT
                    cpr.employee_id,
                    cpr.employee_name,
                    0 AS net_salary,
                    cpr.pf AS pf_employee,
                    0 AS pf_employer,
                    cpr.esic AS esic_employee,
                    0 AS esic_employer,
                    cpr.pt,
                    cpr.tds,
                    cpr.mlwf,
                    cpr.arrears,
                    cpr.other_deduction,
                    0 AS gratuity,
                    cpr.ctc
                FROM ci_payroll_report AS cpr
                INNER JOIN ci_erp_users_details AS eud
                    ON cpr.employee_id = eud.employee_id
                WHERE cpr.month = %s AND cpr.year = %s
                GROUP BY cpr.employee_id, cpr.employee_name;
            """
 
            with connection.cursor() as cursor:
                cursor.execute(query, [month, year])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
 
            # Format data into JSON
            data = [dict(zip(columns, row)) for row in rows]
 
            return Response(data, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db import connection
 
class GetEmployeesByDeptAndDesigPromotionReport(APIView):
    def get(self, request):
        try:
            # get params from frontend
            dept_id = request.GET.get("dept")
            desig_id = request.GET.get("desig")
 
            if not dept_id or not desig_id:
                return JsonResponse({
                    "status": "error",
                    "message": "Both 'department' and 'designation' parameters are required"
                }, status=400)
 
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        eud.user_id,
                        eud.employee_id,
                        CONCAT(
                            COALESCE(eu.first_name, ''), ' ',
                            COALESCE(eu.middle_name, ''), ' ',
                            COALESCE(eu.last_name, '')
                        ) AS employee_name
                    FROM ci_erp_users AS eu
                    INNER JOIN ci_erp_users_details AS eud
                        ON eu.id = eud.user_id
                    WHERE eud.department_id = %s
                      AND eud.designation_id = %s;
                """
                cursor.execute(query, [dept_id, desig_id])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
 
                employees = [
                    dict(zip(columns, row))
                    for row in rows
                ]
 
            return JsonResponse({"status": "success", "data": employees}, safe=False)
 
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500) 
        
class SaveFreezeLeaveSetupYearWise(APIView):
    def post(self, request):
        try:
            leave_data = request.data  # direct list
            if not isinstance(leave_data, list) or not leave_data:
                return Response(
                    {"error": "Invalid payload format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
 
            with connection.cursor() as cursor:
                for row in leave_data:
                    constants_id = row.get("constants_id")
                    leave_type = row.get("leave_type")
                    days_per_year = row.get("days_per_year")
                    current_leave_name = row.get("current_leave_name")
                    current_leave_days = row.get("current_leave_days")
                    year = row.get("year")
 
                    # 🔎 Check if already exists
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM ci_leave_setup
                        WHERE constants_id = %s AND year = %s
                        """,
                        [constants_id, year]
                    )
                    exists = cursor.fetchone()[0]
 
                    if exists > 0:
                        return Response(
                            {"error": f"Leave setup already exists for constants_id {constants_id} in year {year}"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
 
                    # 1️⃣ Insert into ci_leave_setup
                    cursor.execute(
                        """
                        INSERT INTO ci_leave_setup
                        (constants_id, previous_leave_name, previous_leave_days, current_leave_name, current_leave_days, year, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
                        """,
                        [
                            constants_id,
                            leave_type,
                            days_per_year,
                            current_leave_name,
                            current_leave_days,
                            year
                        ]
                    )
 
                    # 2️⃣ Update ci_erp_constants
                    cursor.execute(
                        """
                        UPDATE ci_erp_constants
                        SET category_name = %s, field_one = %s
                        WHERE constants_id = %s AND type = 'leave_type' AND company_id = 2
                        """,
                        [current_leave_name, current_leave_days, constants_id]
                    )
 
            transaction.commit()
 
            return Response(
                {"message": "Leave setup saved and constants updated successfully"},
                status=status.HTTP_200_OK,
            )
 
        except Exception as e:
            transaction.rollback()
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AddNewAssetsToStock(APIView):
    def post(self, request):
        try:
            brand_id = request.data.get("brand_id")
            category_id = request.data.get("category_id")
            product_id = request.data.get("product_id")
            quantity = request.data.get("quantity")
            price = request.data.get("price")
            invoice_number = request.data.get("invoice_number")
            purchase_date = request.data.get("purchase_date")
            warranty_end_date = request.data.get("warranty_end_date")
 
            # Basic validation
            if not (brand_id and category_id and quantity and price and invoice_number and purchase_date):
                return Response(
                    {"message": "Missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST
                )
 
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_assets_instock
                    (brand_id, category_id,product_id, quantity, price, invoice_number, purchase_date, warranty_end_date, created_date)
                    VALUES (%s, %s, %s, %s, %s,%s, %s, %s, NOW())
                """, [brand_id, category_id, product_id , quantity, price, invoice_number, purchase_date, warranty_end_date])
 
 
                cursor.execute("""
                    UPDATE ci_erp_constants
                    SET field_one = COALESCE(field_one, 0) + %s
                    WHERE constants_id = %s
                """, [quantity, brand_id])
 
            return Response(
                {"message": "Asset stock added and updated successfully"},
                status=status.HTTP_201_CREATED
            )
 
        except Exception as e:
            return Response(
                {"message": "Error occurred", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
           
           
           
class UpdateDeleteCategoryAPIView(APIView):
 
    # Update category_name
    def put(self, request):
        constants_id = request.query_params.get("constants_id")
        category_name = request.data.get("category_name")
 
        if not constants_id:
            return Response({"error": "constants_id is required in query params"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not category_name:
            return Response({"error": "category_name is required in body"},
                            status=status.HTTP_400_BAD_REQUEST)
 
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_erp_constants
                    SET category_name = %s
                    WHERE constants_id = %s
                """, [category_name, constants_id])
 
            return Response({"message": f"Constant {constants_id} updated successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
    # Delete record
    def delete(self, request):
        constants_id = request.query_params.get("constants_id")
 
        if not constants_id:
            return Response({"error": "constants_id is required in query params"},
                            status=status.HTTP_400_BAD_REQUEST)
 
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM ci_erp_constants
                    WHERE constants_id = %s
                """, [constants_id])
 
            return Response({"message": f"Constant {constants_id} deleted successfully"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# create product 

from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CreateProductAPI(APIView):
    """
    CRUD API for products stored in ci_erp_constants
    """

    def get(self, request):
        """Fetch all products with full info"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM ci_erp_constants
                    WHERE type = 'assets_product'
                """)
                columns = [col[0] for col in cursor.description]  # get column names
                rows = cursor.fetchall()

                products = [dict(zip(columns, row)) for row in rows]

            return Response(products, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Add a new product"""
        try:
            product_name = request.data.get("product_name")
            if not product_name:
                return Response({"error": "Product name is required"}, status=status.HTTP_400_BAD_REQUEST)

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_erp_constants (company_id, category_name, type, field_one, field_two, parent_value)
                    VALUES (2, %s, 'assets_product', NULL, NULL, NULL)
                """, [product_name])
            
            return Response({"message": "Product added successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """Update an existing product"""
        try:
            product_id = request.query_params.get("product_id")
            product_name = request.data.get("product_name")

            if not product_id:
                return Response({"error": "product_id is required in query params"}, status=status.HTTP_400_BAD_REQUEST)
            if not product_name:
                return Response({"error": "Product name is required"}, status=status.HTTP_400_BAD_REQUEST)

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_erp_constants
                    SET category_name = %s
                    WHERE constants_id = %s
                      AND company_id = 2
                      AND type = 'assets_product'
                """, [product_name, product_id])
                if cursor.rowcount == 0:
                    return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Product updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """Delete a product"""
        try:
            product_id = request.query_params.get("product_id")
            if not product_id:
                return Response({"error": "product_id is required in query params"}, status=status.HTTP_400_BAD_REQUEST)

            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM ci_erp_constants
                    WHERE constants_id = %s
                      AND company_id = 2
                      AND type = 'assets_product'
                """, [product_id])
                if cursor.rowcount == 0:
                    return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Product deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPhasewiseData(APIView):

    def get(self, request, user_id):
 
        if not user_id:
            return Response({"status":"error","message": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
       
        try:
            with connection.cursor() as c:
 
                c.execute("""select ept.*,cp.para_name from ci_employee_progress_tracking ept left join ci_confirmation_parameters cp on ept.parameter_id = cp.parameter_id where emp_id = %s;""", [user_id])
 
                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]
 
                return Response({"status":"success","data": response}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"status":"error","message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
 
class GetMetricsFormData(APIView):
    def get(self, request):
        try:
            month = request.GET.get('month')
            year = request.GET.get('year')

            # Validate inputs
            if not month or not year:
                return Response({"error": "Month and Year are required parameters."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Execute query
            with connection.cursor() as cursor:
                query = "SELECT * FROM ci_revenue WHERE month = %s AND year = %s"
                cursor.execute(query, [month, year])
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response({"data": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
        


# class GetAvailableProQty(APIView):
#     def get(self, request):
#         try:
#             category_id = request.GET.get('category_id')
#             brand_id = request.GET.get('brand_id')

#             if not category_id or not brand_id:
#                 return Response(
#                     {"error": "Both category_id and brand_id are required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT 
#                         asi.product_id,
#                         prd.category_name AS product_name,
#                         COALESCE(SUM(asi.quantity), 0)
#                         - COALESCE(SUM(CASE WHEN a.returned = 'N' THEN a.quantity ELSE 0 END), 0)
#                         AS in_stock
#                     FROM ci_assets_instock asi
#                     LEFT JOIN ci_erp_constants cat 
#                         ON asi.category_id = cat.constants_id
#                     LEFT JOIN ci_erp_constants brd 
#                         ON asi.brand_id = brd.constants_id
#                     LEFT JOIN ci_erp_constants prd 
#                         ON asi.product_id = prd.constants_id
#                     LEFT JOIN ci_assets a 
#                         ON a.assets_category_id = asi.category_id
#                         AND a.brand_id = asi.brand_id
#                         AND a.product_id = asi.product_id
#                     WHERE asi.category_id = %s
#                       AND asi.brand_id = %s
#                     GROUP BY 
#                         asi.category_id, 
#                         cat.category_name, 
#                         asi.brand_id, 
#                         brd.category_name, 
#                         asi.product_id, 
#                         prd.category_name;
#                 """, [category_id, brand_id])

#                 columns = [col[0] for col in cursor.description]
#                 data = [dict(zip(columns, row)) for row in cursor.fetchall()]

#             return Response(data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


class GetAvailableProQty(APIView):
    def get(self, request):
        try:
            category_id = request.GET.get('category_id')
            brand_id = request.GET.get('brand_id')

            if not category_id or not brand_id:
                return Response(
                    {"error": "Both category_id and brand_id are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        i.product_id,
                        prd.category_name AS product_name,
                        COALESCE(i.total_purchased, 0) AS total_purchased,
                        COALESCE(a.assigned, 0) AS assigned,
                        COALESCE(a.returned, 0) AS returned,
                        GREATEST(
                            COALESCE(i.total_purchased, 0)
                            - (COALESCE(a.assigned, 0) - COALESCE(a.returned, 0)),
                            0
                        ) AS in_stock
                    FROM (
                        -- ✅ Total purchased items
                        SELECT 
                            category_id,
                            brand_id,
                            product_id,
                            SUM(quantity) AS total_purchased
                        FROM ci_assets_instock
                        WHERE category_id = %s
                          AND brand_id = %s
                        GROUP BY category_id, brand_id, product_id
                    ) AS i
                    LEFT JOIN (
                        -- ✅ Assigned and Returned items
                        SELECT 
                            assets_category_id AS category_id,
                            brand_id,
                            product_id,
                            SUM(CASE WHEN returned = 'N' THEN quantity ELSE 0 END) AS assigned,
                            SUM(CASE WHEN returned = 'Y' THEN quantity ELSE 0 END) AS returned
                        FROM ci_assets
                        where employee_confirmation = 'accepted'
                        GROUP BY assets_category_id, brand_id, product_id
                    ) AS a
                      ON a.category_id = i.category_id
                     AND a.brand_id = i.brand_id
                     AND a.product_id = i.product_id
                    LEFT JOIN ci_erp_constants prd 
                      ON prd.constants_id = i.product_id;
                """, [category_id, brand_id])

                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class GetAssetsInstockTableAPI(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT 
                        ai.*, 
                        eca.category_name AS brand, 
                        ecb.category_name AS category, 
                        ecc.category_name AS product
                    FROM ci_assets_instock AS ai
                    INNER JOIN ci_erp_constants AS eca ON eca.constants_id = ai.brand_id
                    INNER JOIN ci_erp_constants AS ecb ON ecb.constants_id = ai.category_id
                    INNER JOIN ci_erp_constants AS ecc ON ecc.constants_id = ai.product_id
                    ORDER BY ai.instock_id DESC
                """
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert query result into a list of dicts
            data = [dict(zip(columns, row)) for row in rows]

            return JsonResponse({"status": "success", "data": data}, status=200, safe=False)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

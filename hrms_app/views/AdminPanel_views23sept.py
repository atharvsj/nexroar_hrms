from datetime import date, datetime, time
from django.db import connection, transaction, connections
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from hrms_app.permissions import *
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
import os
from urllib.parse import quote
from django.conf import settings
from django.core.files.storage import default_storage
import os
from django.contrib.auth.hashers import make_password
import json

from django.core.mail import EmailMultiAlternatives
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import calendar
from decimal import Decimal, InvalidOperation

from urllib.parse import quote
import bcrypt


# class EmployeeDetails(APIView):
#     # permission_classes = [AllowAny]

#     def get(self, request):

#         try:
#             with connection.cursor() as c:

#                 query = """SELECT 
#     u.id,
#     ud.employee_id,
#     CONCAT(u.first_name, ' ', u.last_name) AS emp_name,
#     dpt.department_id,
#     dpt.department_name,
#     d.designation_id,
#     d.designation_name,
#     ud.date_of_joining AS join_date,
#     u.is_active AS status,
#     CONCAT(um.first_name, ' ', um.last_name) AS manager,
#     u.profile_photo,
#     ud.probation
# FROM ci_erp_users u
# LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
# LEFT JOIN ci_departments dpt ON ud.department_id = dpt.department_id
# LEFT JOIN ci_designations d ON ud.designation_id = d.designation_id
# LEFT JOIN ci_erp_users um ON ud.manager = um.id
# GROUP BY u.id, emp_name, dpt.department_name, d.designation_name, join_date, status, manager"""

#                 c.execute(query)

#                 rows = c.fetchall()

#                 response = [
#                     {
#                         "index": idx,
#                         "user_id": row[0],
#                         "employee_id": row[1],
#                         "employee_name": row[2],
#                         "department_id": row[3],
#                         "department_name": row[4],
#                         "designation_id": row[5],
#                         "designation_name": row[6],
#                         "join_date": row[7],
#                         "status": row[8],
#                         "manager": row[9],
#                         # "profile_photo": request.build_absolute_uri(
#                         #     f"/hrms-backend/media/documents/{quote(row[9])}"
#                         # ),
#                         # "profile_photo": request.build_absolute_uri(
#                         #     f"/hrms-backend/media/documents/{quote(str(row[10], 'utf-8'))}"
#                         #     if isinstance(row[10], bytes)
#                         #     else (
#                         #         f"/hrms-backend/media/documents/{quote(str(row[10]))}"
#                         #         if row[10]
#                         #         else None
#                         #     )
#                         # ),
#                         "profile_photo": (
#                             request.build_absolute_uri(
#                                 f"/hrms-backend/media/documents/{quote(row[10].decode('utf-8') if isinstance(row[10],                       bytes) else str(row[10]))}"
#                             )
#                             if row[10] else None
#                         ),

#                     }
#                     for idx, row in enumerate(rows, start=1)
#                 ]

#             return Response(
#                 {"status": "success", "data": response}, status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occured: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

from urllib.parse import quote
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class EmployeeDetails(APIView):
    # permission_classes = [AllowAny]

    def get(self, request):
        try:
            with connection.cursor() as c:
                query = """
                    SELECT 
                        u.id,
                        ud.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS emp_name,
                        dpt.department_id,
                        dpt.department_name,
                        d.designation_id,
                        d.designation_name,
                        ud.date_of_joining AS join_date,
                        u.is_active AS status,
                        CONCAT(um.first_name, ' ', um.last_name) AS manager,
                        u.profile_photo,
                        ud.probation
                    FROM ci_erp_users u
                    LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    LEFT JOIN ci_departments dpt ON ud.department_id = dpt.department_id
                    LEFT JOIN ci_designations d ON ud.designation_id = d.designation_id
                    LEFT JOIN ci_erp_users um ON ud.manager = um.id
                    GROUP BY u.id, emp_name, dpt.department_name, d.designation_name, join_date, status, manager
                """

                c.execute(query)
                rows = c.fetchall()

                response = []
                for idx, row in enumerate(rows, start=1):
                    profile_photo = None
                    if row[10]:
                        # Handle bytes -> string
                        photo_val = row[10].decode("utf-8") if isinstance(row[10], bytes) else str(row[10])

                        if photo_val.startswith("http://") or photo_val.startswith("https://"):
                            # Already a full URL in DB
                            profile_photo = photo_val
                        else:
                            # Just a filename, build the full media path
                            profile_photo = request.build_absolute_uri(
                                f"/hrms-backend/media/documents/{quote(photo_val)}"
                            )

                    response.append({
                        "index": idx,
                        "user_id": row[0],
                        "employee_id": row[1],
                        "employee_name": row[2],
                        "department_id": row[3],
                        "department_name": row[4],
                        "designation_id": row[5],
                        "designation_name": row[6],
                        "join_date": row[7],
                        "status": row[8],
                        "manager": row[9],
                        "profile_photo": profile_photo,
                    })

            return Response({"status": "success", "data": response}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class EditEmployee(APIView):
    # permission_classes = [IsAdmin]

#     def get(self, request, user_id):

#         if not user_id:
#             return Response(
#                 {"status": "error", "message": "user_id is required"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             with connection.cursor() as c:

#                 query = """SELECT 
#     CONCAT(u.first_name, ' ',u.middle_name, ' ', u.last_name) AS emp_name,
#     u.email,
#     u.contact_number,
#     CONCAT(um.first_name, ' ', um.last_name) AS manager,
#     d.designation_name,
#     dpt.department_name,
#     u.is_active AS status,
#     DATE(u.created_at) AS join_date,
#     um.id as manager_id,
#     ud.designation_id,
#     ud.department_id,
#     u.profile_photo,
#     ud.probation,
#     ud.division_id,
#     u.employee_hub_id,
#     u.state,
#     ofs.shift_name , 
#     ec.category_name as country_name
    
# FROM ci_erp_users u
# LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
# LEFT JOIN ci_designations d ON ud.designation_id = d.designation_id
# LEFT JOIN ci_departments dpt ON ud.department_id = dpt.department_id
# LEFT JOIN ci_office_shifts ofs ON ud.office_shift_id = ofs.office_shift_id
# LEFT JOIN ci_erp_users um ON ud.manager = um.id
# LEFT JOIN ci_erp_constants ec ON ec.constants_id = u.country
# WHERE u.id = %s
# GROUP BY u.id, emp_name, d.designation_name, join_date, status, manager;"""

#                 c.execute(query, [user_id])

#                 row = c.fetchone()

#                 response = [
#                     {
#                         "emp_name": row[0],
#                         "email": row[1],
#                         "phone": row[2],
#                         "manager": row[3],
#                         "designation": row[4],
#                         "department": row[5],
#                         "status": row[6],
#                         "join_date": row[7],
#                         "manager_id": row[8],
#                         "designation_id": row[9],
#                         "department_id": row[10],
#                         "profile_photo": (
#                             request.build_absolute_uri(
#                                 f"{quote(row[11])}"
#                             )
#                             if row[11]
#                             else None
#                         ),
#                         "probation": row[12],
#                         "division_id": row[13],
#                         "employee_hub_id": row[14],
#                         "state": row[15],
#                         "office_shift": row[16],
#                         "country_name": row[17],

#                     }
#                 ]

#             return Response(
#                 {"status": "success", "data": response}, status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occured: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


    def get(self, request, user_id):

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:
                query = """SELECT 
                    CONCAT(u.first_name, ' ',u.middle_name, ' ', u.last_name) AS emp_name,
                    u.email,
                    u.contact_number,
                    CONCAT(um.first_name, ' ', um.last_name) AS manager,
                    d.designation_name,
                    dpt.department_name,
                    u.is_active AS status,
                    DATE(u.created_at) AS join_date,
                    um.id as manager_id,
                    ud.designation_id,
                    ud.department_id,
                    u.profile_photo,
                    ud.probation,
                    ud.division_id,
                    u.employee_hub_id,
                    u.state,
                    ofs.shift_name , 
                    ec.category_name as country_name
                FROM ci_erp_users u
                LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
                LEFT JOIN ci_designations d ON ud.designation_id = d.designation_id
                LEFT JOIN ci_departments dpt ON ud.department_id = dpt.department_id
                LEFT JOIN ci_office_shifts ofs ON ud.office_shift_id = ofs.office_shift_id
                LEFT JOIN ci_erp_users um ON ud.manager = um.id
                LEFT JOIN ci_erp_constants ec ON ec.constants_id = u.country
                WHERE u.id = %s
                GROUP BY u.id, emp_name, d.designation_name, join_date, status, manager;"""

                c.execute(query, [user_id])
                row = c.fetchone()

                if not row:
                    return Response(
                        {"status": "error", "message": "Employee not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Fix profile photo handling
                profile_photo = None
                if row[11]:
                    if str(row[11]).startswith("http"):
                        profile_photo = row[11]
                    else:
                        profile_photo = request.build_absolute_uri(row[11])

                response = [
                    {
                        "emp_name": row[0],
                        "email": row[1],
                        "phone": row[2],
                        "manager": row[3],
                        "designation": row[4],
                        "department": row[5],
                        "status": row[6],
                        "join_date": row[7],
                        "manager_id": row[8],
                        "designation_id": row[9],
                        "department_id": row[10],
                        "profile_photo": profile_photo,
                        "probation": row[12],
                        "division_id": row[13],
                        "employee_hub_id": row[14],
                        "state": row[15],
                        "office_shift": row[16],
                        "country_name": row[17],
                    }
                ]

            return Response(
                {"status": "success", "data": response},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
    def put(self, request):

        try:
            file = request.FILES.get("file")
            user_id = request.data.get("user_id")

            if not user_id:
                return Response(
                    {"status": "error", "message": "user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            emp_name = request.data.get("emp_name")
            email = request.data.get("email")
            phone = request.data.get("phone")
            manager = request.data.get("manager_id")
            designation = request.data.get("designation_id")
            department = request.data.get("department_id")
            office_shift = request.data.get("office_shift")
            user_status = request.data.get("status")
            join_date = request.data.get("join_date")
            is_probation = request.data.get("is_probation")
            country_id = request.data.get("country_id")   # <-- NEW FIELD


            first_name, last_name = None, None
            if emp_name:
                name_parts = emp_name.strip().split()
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            new_file_name = None
            if file:
                file_name = file.name
                file_extension = file_name.split(".")[-1].lower()

                if file_extension not in ["jpg", "jpeg", "png"]:
                    return Response(
                        {
                            "status": "error",
                            "message": "Invalid file format. Please upload JPG, JPEG, or PNG.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
                os.makedirs(upload_dir, exist_ok=True)
                new_file_name = f"{user_id}_{first_name or 'user'}_{last_name or 'profile'}.{file_extension}"
                destination_path = os.path.join(upload_dir, new_file_name)

                with default_storage.open(destination_path, "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            with transaction.atomic():
                with connection.cursor() as c:
                    # Dynamic update for ci_erp_users
                    user_fields = []
                    user_values = []

                    if first_name is not None:
                        user_fields.append("first_name = %s")
                        user_values.append(first_name)
                    if last_name is not None:
                        user_fields.append("last_name = %s")
                        user_values.append(last_name)
                    if email:
                        user_fields.append("email = %s")
                        user_values.append(email)
                    if phone:
                        user_fields.append("contact_number = %s")
                        user_values.append(phone)
                    if user_status:
                        user_fields.append("is_active = %s")
                        user_values.append(user_status)
                    if join_date:
                        user_fields.append("created_at = %s")
                        user_values.append(join_date)
                    if new_file_name:
                        user_fields.append("profile_photo = %s")
                        user_values.append(new_file_name)
                    if country_id:   # ✅ update only in ci_erp_users
                        user_fields.append("country = %s")
                        user_values.append(country_id)

                    if user_fields:
                        user_values.append(user_id)
                        user_query = f"UPDATE ci_erp_users SET {', '.join(user_fields)} WHERE id = %s"
                        c.execute(user_query, user_values)

                    # Dynamic update for ci_erp_users_details
                    detail_fields = []
                    detail_values = []

                    if designation:
                        detail_fields.append("designation_id = %s")
                        detail_values.append(designation)
                    if department:
                        detail_fields.append("department_id = %s")
                        detail_values.append(department)
                    if office_shift:
                        detail_fields.append("office_shift_id = %s")
                        detail_values.append(office_shift)
                    if manager:
                        detail_fields.append("manager = %s")
                        detail_values.append(manager)
                    if join_date:
                        detail_fields.append("created_at = %s")
                        detail_values.append(join_date)
                    if is_probation:
                        detail_fields.append("probation = %s")
                        detail_values.append(is_probation)
                        
                    


                    if detail_fields:
                        detail_values.append(user_id)
                        detail_query = f"UPDATE ci_erp_users_details SET {', '.join(detail_fields)} WHERE user_id = %s"
                        c.execute(detail_query, detail_values)

            return Response(
                {"status": "success", "message": "Employee updated successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request):

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    c.execute(
                        "DELETE FROM ci_erp_users_details WHERE user_id = %s", [user_id]
                    )
                    c.execute("DELETE FROM ci_erp_users WHERE id = %s", [user_id])

            return Response(
                {
                    "status": "success",
                    "message": "employee deleted successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChangeManager(APIView):
    # permission_classes = [IsAdmin]

    def put(self, request):

        user_id = request.data.get("user_id")
        manager_id = request.data.get("manager_id")

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    c.execute(
                        """update ci_erp_users_details set manager = %s where user_id = %s""",
                        [manager_id, user_id],
                    )

            return Response(
                {
                    "status": "success",
                    "message": "manager updated successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetMaxEmployeeId(APIView):

    def get(self, request):

        with connection.cursor() as c:

            c.execute(
                """select employee_id from ci_erp_users_details order by staff_details_id desc"""
            )
            row = c.fetchone()

            return Response(
                {"status": "success", "employee_id": row}, status=status.HTTP_200_OK
            )

class FetchDocuments(APIView): 
 
    def post(self, request):  
        email_id = request.data.get("email_id") 
 
        if not email_id: 
            return Response({
                "status": "error", 
                "message": "Email ID is required."
            }, status=status.HTTP_400_BAD_REQUEST) 
 
        try:     
            with connections["raas"].cursor() as c: 
                # query = """ 
                #     SELECT  
                #         aadhar, pan, hsc, ssc, degree, other, passport_photo,  
                #         driving_licence, cheque_photo, experience_letter 
                #     FROM backendapp_document  
                #     WHERE email = %s 
                # """ 
                
                query="""SELECT  bd.aadhar, bd.pan, bd.hsc, bd.ssc, bd.degree, bd.other, bd.passport_photo,  
                        bd.driving_licence, bd.cheque_photo, bd.experience_letter, ba.letter as appointment_letter, bl.pdf_path as Offer_letter, baa.resume
                    FROM backendapp_document  bd  LEFT JOIN backendapp_appointmentletter ba on bd.user_id= ba.user_id
                    LEFT JOIN backendapp_letters bl on bd.user_id= bl.user_id
                    LEFT JOIN backendapp_applicant baa on bd.user_id=baa.id
                    WHERE bd.email = %s order by bd.user_id desc limit 1"""
                    
                c.execute(query, [email_id]) 
                row = c.fetchone() 
 
                if not row: 
                    return Response({
                        "status": "error", 
                        "message": "No documents found for the provided email."
                    }, status=status.HTTP_404_NOT_FOUND) 
 
                # columns = [ 
                #     "aadhar", "pan", "hsc", "ssc", "degree", "other",  
                #     "passport_photo", "driving_licence", "cheque_photo", "experience_letter" 
                # ] 
                
                columns = [
                    "aadhar", "pan", "hsc", "ssc", "degree", "other",  
                    "passport_photo", "driving_licence", "cheque_photo", "experience_letter" , "appointment_letter", "Offer_letter", "resume"
                ]
                
                documents = dict(zip(columns, row)) 
 
                # Construct URLs and verify file existence
                for key, value in documents.items(): 
                    if value: 
                        # Check if file exists
                        file_path = os.path.join(settings.MEDIA_ROOT, value)
                        if os.path.exists(file_path):
                            documents[key] = request.build_absolute_uri(f"{settings.MEDIA_URL}{quote(value)}")
                        else:
                            documents[key] = None  # File doesn't exist
                            # # print(f"Warning: File not found: {file_path}")
                    else: 
                        documents[key] = None 
 
                return Response({ 
                    "status": "success", 
                    "documents": documents 
                }, status=status.HTTP_200_OK) 
 
        except Exception as e: 
            # # print(f"Database error: {str(e)}")  # Log the error
            return Response({
                "status": "error", 
                "message": "An error occurred while fetching documents."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckExistingEmail(APIView):

    def get(self, request):

        try:
            with connection.cursor() as c:
                c.execute("""select email from ci_erp_users where email is not null and email != ''""")
                column = [col[0] for col in c.description]
                response = [dict(zip(column, rows)) for rows in c.fetchall()]

            return Response({"status":"success","data": response}, status=status.HTTP_200_OK)
        
        except Exception as e: 
            return Response({
                "status": "error", 
                "message": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class AddEmployee(APIView):
#     # permission_classes = [IsAdmin]

#     def post(self, request):

#         file = request.FILES.get("file")
#         first_name = request.data.get("first_name")
#         middle_name = request.data.get("middle_name")
#         last_name = request.data.get("last_name")
#         emp_id = request.data.get("emp_id")
#         phone = request.data.get("phone")
#         gender = request.data.get("gender")
#         email = request.data.get("email")
#         username = request.data.get("username")
#         password = request.data.get("password")
#         # hashed_password = make_password(password)

#         hashed_password = bcrypt.hashpw(
#             password.encode('utf-8'), 
#             bcrypt.gensalt(rounds=12)
#         ).decode('utf-8')

#         office_shift = request.data.get("office_shift")
#         user_type = request.data.get("role")
#         department = request.data.get("department_id")
#         designation = request.data.get("designation_id")
#         division_id = request.data.get("division_id")
#         gross_salary = request.data.get("gross_salary")
#         manager = request.data.get("manager_id")
#         user_status = request.data.get("status")
#         company_id = request.data.get("company_id")
#         is_probation = request.data.get("is_probation")
#         state_id = request.data.get("state_id")
#         employee_hub_id = request.data.get("employee_hub_id")

#         if not first_name or not last_name or not email or not phone:
#             return Response(
#                 {"status": "error", "message": "Required fields are missing."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # name_parts = emp_name.strip().split()
#         # first_name = name_parts[0] if len(name_parts) >= 1 else ""
#         # middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
#         # last_name = name_parts[-1] if len(name_parts) >= 2 else ""

#         try:
#             with transaction.atomic():
#                 with connection.cursor() as c:

#                     c.execute(
#                         """
#                         INSERT INTO ci_erp_users (first_name, middle_name, last_name, email, contact_number, is_active, gender, username, password, user_role_id, user_type, company_id, state, employee_hub_id, created_at)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
#                     """,
#                         [
#                             first_name,
#                             middle_name,
#                             last_name,
#                             email,
#                             phone,
#                             user_status,
#                             gender,
#                             username,
#                             hashed_password,
#                             user_type,
#                             user_type,
#                             company_id,
#                             state_id,
#                             employee_hub_id,
#                         ],
#                     )

#                     user_id = c.lastrowid

#                     new_file_name = None
#                     if file:
#                         file_name = file.name
#                         file_extension = file_name.split(".")[-1].lower()

#                         if file_extension not in ["jpg", "jpeg", "png"]:
#                             return Response(
#                                 {
#                                     "status": "error",
#                                     "message": "Invalid file format. Please upload JPG, JPEG, or PNG.",
#                                 },
#                                 status=status.HTTP_400_BAD_REQUEST,
#                             )

#                         new_file_name = (
#                             f"{user_id}_{first_name}_{last_name}.{file_extension}"
#                         )
#                         upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
#                         os.makedirs(upload_dir, exist_ok=True)
#                         destination_path = os.path.join(upload_dir, new_file_name)

#                         with default_storage.open(
#                             destination_path, "wb+"
#                         ) as destination:
#                             for chunk in file.chunks():
#                                 destination.write(chunk)

#                         c.execute(
#                             "UPDATE ci_erp_users SET profile_photo = %s WHERE id = %s",
#                             [new_file_name, user_id],
#                         )

#                     c.execute(
#                         """
#                         INSERT INTO ci_erp_users_details (user_id, employee_id, designation_id, department_id, division_id, office_shift_id, manager, basic_salary, gross_salary, salay_type, probation, created_at, date_of_joining)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
#                     """,
#                         [
#                             user_id,
#                             emp_id,
#                             designation,
#                             department,
#                             division_id,
#                             office_shift,
#                             manager,
#                             gross_salary,
#                             gross_salary,
#                             1,
#                             is_probation
#                         ],
#                     )

#             return Response(
#                 {"status": "success", "message": "Employee added successfully."},
#                 status=status.HTTP_201_CREATED,
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

from django.db import connection, transaction
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import os
import bcrypt


import requests 
# class AddEmployee(APIView):
#     # permission_classes = [IsAdmin]

#     def post(self, request):
#         file = request.FILES.get("file")
#         first_name = request.data.get("first_name")
#         middle_name = request.data.get("middle_name")
#         last_name = request.data.get("last_name")
#         emp_id = request.data.get("emp_id")   # <-- employee_id
#         phone = request.data.get("phone")
#         # gender = request.data.get("gender")
#         gender_str = request.data.get("gender")
 
#         # Map gender string to integer code
#         gender_mapping = {
#             'Male': 1,
#             'Female': 2,
#             'Other': 3,
#             'M': 1,
#             'F': 2,
#             'O': 3
#         }
        
#         # Convert gender string to integer code, default to 3 (Other) if not found
#         gender = gender_mapping.get(gender_str, 3) if gender_str else None
#         email = request.data.get("email")
#         username = request.data.get("username")
#         password = request.data.get("password")
#         office_shift = request.data.get("office_shift")
#         user_type = request.data.get("role")
#         department = request.data.get("department_id")
#         designation = request.data.get("designation_id")
#         division_id = request.data.get("division_id")
#         gross_salary = request.data.get("gross_salary")
#         manager = request.data.get("manager_id")
#         user_status = request.data.get("status")
#         company_id = request.data.get("company_id")
#         is_probation = request.data.get("is_probation")
#         state_id = request.data.get("state_id")
#         country_id = request.data.get("country_id")
#         employee_hub_id = request.data.get("employee_hub_id")

#         if not first_name or not last_name or not email or not phone:
#             return Response(
#                 {"status": "error", "message": "Required fields are missing."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             with transaction.atomic():
#                 with connection.cursor() as c:
#                     # Hash password
#                     hashed_password = bcrypt.hashpw(
#                         password.encode("utf-8"),
#                         bcrypt.gensalt(rounds=12)
#                     ).decode("utf-8")

#                     # Insert into users
#                     c.execute(
#                         """
#                         INSERT INTO ci_erp_users 
#                         (first_name, middle_name, last_name, email, contact_number, is_active, gender, username, password, 
#                          user_role_id, user_type, company_id, state,country, employee_hub_id, created_at)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
#                         """,
#                         [
#                             first_name, middle_name, last_name, email, phone,
#                             user_status, gender, username, hashed_password,
#                             user_type, user_type, company_id, state_id,country_id,  employee_hub_id,
#                         ],
#                     )
#                     user_id = c.lastrowid

#                     # ✅ Upload profile photo
#                     if file:
#                         file_name = file.name
#                         ext = file_name.split(".")[-1].lower()
#                         if ext not in ["jpg", "jpeg", "png"]:
#                             return Response(
#                                 {"status": "error", "message": "Invalid file format."},
#                                 status=status.HTTP_400_BAD_REQUEST,
#                             )

#                         new_file_name = f"{user_id}_{first_name}_{last_name}.{ext}"
#                         upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
#                         os.makedirs(upload_dir, exist_ok=True)
#                         destination_path = os.path.join(upload_dir, new_file_name)

#                         with default_storage.open(destination_path, "wb+") as dest:
#                             for chunk in file.chunks():
#                                 dest.write(chunk)

#                         # ✅ Store full live URL
#                         profile_url = f"{settings.SITE_URL}{settings.MEDIA_URL}documents/{new_file_name}"

#                         c.execute(
#                             "UPDATE ci_erp_users SET profile_photo = %s WHERE id = %s",
#                             [profile_url, user_id],
#                         )

#                     # Insert into user details
#                     c.execute(
#                         """
#                         INSERT INTO ci_erp_users_details 
#                         (user_id, employee_id, designation_id, department_id, division_id, office_shift_id, manager, 
#                          basic_salary, gross_salary, salay_type, probation, created_at, date_of_joining)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
#                         """,
#                         [
#                             user_id, emp_id, designation, department, division_id,
#                             office_shift, manager, gross_salary, gross_salary, 1, is_probation
#                         ],
#                     )

#                     # ✅ Initialize leave balances
#                     if is_probation in ["N", "n"]:
#                         self._init_leave_balances(
#                             cursor=c,
#                             employee_id=emp_id,
#                             employee_name=f"{first_name} {last_name}"
#                         )

#                     # ✅ Allocate all policies automatically
#                     self._allocate_policies(cursor=c, emp_id=emp_id)

#                     # ✅ Fetch & store employee documents from RAAS
#                     self._fetch_and_store_documents_from_raas(
#                         cursor=c,
#                         email=email,
#                         user_id=user_id,
#                         emp_id=emp_id
#                     )

#             return Response(
#                 {"status": "success", "message": "Employee added successfully with policies & documents stored."},
#                 status=status.HTTP_201_CREATED,
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#     def _init_leave_balances(self, cursor, employee_id, employee_name):
#         """Initialize leave balances"""
#         current_year = datetime.now().year
#         leave_assignments = {
#             "Casual Leave (CL)": 6,
#             "Medical Leave (ML)": 7,
#             "Maternity Leave": 182,
#             "Paid Leave": 5,
#             "Paternity Leave": 3,
#         }

#         cursor.execute(
#             "SELECT constants_id, category_name FROM ci_erp_constants WHERE type = 'leave_type' AND category_name IN %s",
#             [tuple(leave_assignments.keys())],
#         )
#         leave_types = cursor.fetchall()

#         for constants_id, category_name in leave_types:
#             cursor.execute(
#                 """
#                 INSERT INTO ci_leave_balance 
#                 (employee_id, employee_name, leave_type_id, leave_type, balance_leave, carry_forward, last_paid_leave_given_at, year, status)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Y')
#                 """,
#                 [employee_id, employee_name, constants_id, category_name,
#                  leave_assignments[category_name], 0, None, current_year],
#             )

#     def _allocate_policies(self, cursor, emp_id):
#         """Allocate all policies to a newly created employee"""
#         now = datetime.now()

#         cursor.execute("SELECT policy_id FROM ci_policies")
#         policies = cursor.fetchall()
#         if not policies:
#             return

#         policy_ids = [str(row[0]) for row in policies]
#         policy_ids_str = ",".join(policy_ids)

#         cursor.execute("SELECT 1 FROM ci_policy_allocations WHERE emp_id = %s", [emp_id])
#         if cursor.fetchone():
#             return  

#         cursor.execute(
#             """
#             INSERT INTO ci_policy_allocations (emp_id, policy_id, allocation_date)
#             VALUES (%s, %s, %s)
#             """,
#             [emp_id, policy_ids_str, now],
#         )

#     # -------------------------------
#     # ✅ NEW METHODS for Documents
#     # -------------------------------
#     def _fetch_and_store_documents_from_raas(self, cursor, email, user_id, emp_id):
#         """Fetch employee documents from RAAS and store them in HRMS"""
#         try:
#             raas_response = requests.post(
#                 "https://raasbackend.vetrinahealthcare.com/fetch_documents/",
#                 json={"email_id": email}
#             ).json()

#             if raas_response.get("status") != "success":
#                 return

#             documents = raas_response.get("documents", {})

#             for doc_type, raas_url in documents.items():
#                 if not raas_url:
#                     continue

#                 hrms_url = self._save_document_from_raas(raas_url, emp_id, doc_type)

#                 if hrms_url:
#                     cursor.execute("""
#                         INSERT INTO ci_employee_documents (user_id, employee_id, document_type, document_url)
#                         VALUES (%s, %s, %s, %s)
#                     """, [user_id, emp_id, doc_type, hrms_url])

#         except Exception as e:
#             # print(f"Failed fetching documents from RAAS: {e}")

#     def _save_document_from_raas(self, raas_url, emp_id, doc_type):
#         """Download from RAAS and save in HRMS"""
#         try:
#             response = requests.get(raas_url, stream=True)
#             response.raise_for_status()

#             ext = raas_url.split(".")[-1]
#             new_file_name = f"{emp_id}_{doc_type}.{ext}"
#             upload_dir = os.path.join(settings.MEDIA_ROOT, "employee_documents")
#             os.makedirs(upload_dir, exist_ok=True)

#             destination_path = os.path.join(upload_dir, new_file_name)
#             with open(destination_path, "wb") as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)

#             # ✅ Always build full URL using SITE_URL
#             return f"{settings.SITE_URL}/hrms-backend{settings.MEDIA_URL}employee_documents/{new_file_name}"

#         except Exception as e:
#             # print(f"Error saving document {doc_type}: {e}")
#             return None




# class AddEmployee(APIView):
#     # permission_classes = [IsAdmin]
 
#     def post(self, request):
#         file = request.FILES.get("file")
#         first_name = request.data.get("first_name")
#         middle_name = request.data.get("middle_name")
#         last_name = request.data.get("last_name")
#         emp_id = request.data.get("emp_id")   # <-- employee_id
#         phone = request.data.get("phone")
#         # gender = request.data.get("gender")
#         gender_str = request.data.get("gender")
 
#         # Map gender string to integer code
#         gender_mapping = {
#             'Male': 1,
#             'Female': 2,
#             'Other': 3,
#             'M': 1,
#             'F': 2,
#             'O': 3
#         }
       
#         # Convert gender string to integer code, default to 3 (Other) if not found
#         gender = gender_mapping.get(gender_str, 3) if gender_str else None
#         email = request.data.get("email")
#         username = request.data.get("username")
#         password = request.data.get("password")
#         office_shift = request.data.get("office_shift")
#         user_type = request.data.get("role")
#         department = request.data.get("department_id")
#         designation = request.data.get("designation_id")
#         division_id = request.data.get("division_id")
#         gross_salary = request.data.get("gross_salary")
#         manager = request.data.get("manager_id")
#         user_status = request.data.get("status")
#         company_id = request.data.get("company_id")
#         is_probation = request.data.get("is_probation")
#         state_id = request.data.get("state_id")
#         country_id = request.data.get("country_id")
#         employee_hub_id = request.data.get("employee_hub_id")
#         headquarter = request.data.get("headquarter")
#         sub_division = request.data.get("sub_division")
 
 
#         if not first_name or not last_name or not email or not phone:
#             return Response(
#                 {"status": "error", "message": "Required fields are missing."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
 
#         try:
#             with transaction.atomic():
#                 with connection.cursor() as c:
#                     # Hash password
#                     hashed_password = bcrypt.hashpw(
#                         password.encode("utf-8"),
#                         bcrypt.gensalt(rounds=12)
#                     ).decode("utf-8")
 
#                     # Insert into users
#                     c.execute(
#                         """
#                         INSERT INTO ci_erp_users
#                         (first_name, middle_name, last_name, email, contact_number, is_active, gender, username, password,
#                          user_role_id, user_type, company_id, state,country, employee_hub_id, created_at)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
#                         """,
#                         [
#                             first_name, middle_name, last_name, email, phone,
#                             user_status, gender, username, hashed_password,
#                             user_type, user_type, company_id, state_id,country_id,  employee_hub_id,
#                         ],
#                     )
#                     user_id = c.lastrowid
 
#                     # ✅ Upload profile photo
#                     if file:
#                         file_name = file.name
#                         ext = file_name.split(".")[-1].lower()
#                         if ext not in ["jpg", "jpeg", "png"]:
#                             return Response(
#                                 {"status": "error", "message": "Invalid file format."},
#                                 status=status.HTTP_400_BAD_REQUEST,
#                             )
 
#                         new_file_name = f"{user_id}_{first_name}_{last_name}.{ext}"
#                         upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
#                         os.makedirs(upload_dir, exist_ok=True)
#                         destination_path = os.path.join(upload_dir, new_file_name)
 
#                         with default_storage.open(destination_path, "wb+") as dest:
#                             for chunk in file.chunks():
#                                 dest.write(chunk)
 
#                         # ✅ Store full live URL
#                         profile_url = f"{settings.SITE_URL}{settings.MEDIA_URL}documents/{new_file_name}"
 
#                         c.execute(
#                             "UPDATE ci_erp_users SET profile_photo = %s WHERE id = %s",
#                             [profile_url, user_id],
#                         )
 
#                     # Insert into user details
#                     c.execute(
#                         """
#                         INSERT INTO ci_erp_users_details
#                         (user_id, employee_id, designation_id, department_id,headquarter, division_id,sub_division, office_shift_id, manager,
#                          basic_salary, gross_salary, salay_type, probation, created_at, date_of_joining)
#                         VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
#                         """,
#                         [
#                             user_id, emp_id, designation, department,headquarter , division_id,sub_division,
#                             office_shift, manager, gross_salary, gross_salary, 1, is_probation
#                         ],
#                     )
 
#                     # ✅ Initialize leave balances
#                     if is_probation in ["N", "n"]:
#                         self._init_leave_balances(
#                             cursor=c,
#                             employee_id=emp_id,
#                             employee_name=f"{first_name} {last_name}"
#                         )
 
#                     # ✅ Allocate all policies automatically
#                     self._allocate_policies(cursor=c, emp_id=emp_id)
 
#                     # ✅ Fetch & store employee documents from RAAS
#                     self._fetch_and_store_documents_from_raas(
#                         cursor=c,
#                         email=email,
#                         user_id=user_id,
#                         emp_id=emp_id
#                     )
 
#             return Response(
#                 {"status": "success", "message": "Employee added successfully with policies & documents stored."},
#                 status=status.HTTP_201_CREATED,
#             )
 
#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )



class AddEmployee(APIView):
    # permission_classes = [IsAdmin]
 
    def post(self, request):
        file = request.FILES.get("file")
        first_name = request.data.get("first_name")
        middle_name = request.data.get("middle_name")
        last_name = request.data.get("last_name")
        emp_id = request.data.get("emp_id")   # <-- employee_id
        phone = request.data.get("phone")
        # gender = request.data.get("gender")
        gender_str = request.data.get("gender")
 
        # Map gender string to integer code
        gender_mapping = {
            'Male': 1,
            'Female': 2,
            'Other': 3,
            'M': 1,
            'F': 2,
            'O': 3
        }
       
        # Convert gender string to integer code, default to 3 (Other) if not found
        gender = gender_mapping.get(gender_str, 3) if gender_str else None
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        office_shift = request.data.get("office_shift")
        user_type = request.data.get("role")
        department = request.data.get("department_id")
        designation = request.data.get("designation_id")
        division_id = request.data.get("division_id")
        gross_salary = request.data.get("gross_salary")
        manager = request.data.get("manager_id")
        user_status = request.data.get("status")
        company_id = request.data.get("company_id")
        is_probation = request.data.get("is_probation")
        state_id = request.data.get("state_id")
        country_id = request.data.get("country_id")
        employee_hub_id = request.data.get("employee_hub_id")
        headquarter = request.data.get("headquarter")
        sub_division = request.data.get("sub_division")
 
 
        if not first_name or not last_name or not email or not phone:
            return Response(
                {"status": "error", "message": "Required fields are missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        try:
            with transaction.atomic():
                with connection.cursor() as c:
                    # Hash password
                    hashed_password = bcrypt.hashpw(
                        password.encode("utf-8"),
                        bcrypt.gensalt(rounds=12)
                    ).decode("utf-8")
 
                    # Insert into users
                    c.execute(
                        """
                        INSERT INTO ci_erp_users
                        (first_name, middle_name, last_name, email, contact_number, is_active, gender, username, password,
                         user_role_id, user_type, company_id, state,country, employee_hub_id, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """,
                        [
                            first_name, middle_name, last_name, email, phone,
                            user_status, gender, username, hashed_password,
                            user_type, user_type, company_id, state_id,country_id,  employee_hub_id,
                        ],
                    )
                    user_id = c.lastrowid
 
                    # ✅ Upload profile photo
                    if file:
                        file_name = file.name
                        ext = file_name.split(".")[-1].lower()
                        if ext not in ["jpg", "jpeg", "png"]:
                            return Response(
                                {"status": "error", "message": "Invalid file format."},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
 
                        new_file_name = f"{user_id}_{first_name}_{last_name}.{ext}"
                        upload_dir = os.path.join(settings.MEDIA_ROOT, "documents")
                        os.makedirs(upload_dir, exist_ok=True)
                        destination_path = os.path.join(upload_dir, new_file_name)
 
                        with default_storage.open(destination_path, "wb+") as dest:
                            for chunk in file.chunks():
                                dest.write(chunk)
 
                        # ✅ Store full live URL
                        profile_url = f"{settings.SITE_URL}{settings.MEDIA_URL}documents/{new_file_name}"
 
                        c.execute(
                            "UPDATE ci_erp_users SET profile_photo = %s WHERE id = %s",
                            [profile_url, user_id],
                        )
 
                    # Insert into user details
                    c.execute(
                        """
                        INSERT INTO ci_erp_users_details
                        (user_id, employee_id, designation_id, department_id,headquarter, division_id,sub_division, office_shift_id, manager,
                         basic_salary, gross_salary, salay_type, probation, created_at, date_of_joining)
                        VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        """,
                        [
                            user_id, emp_id, designation, department,headquarter , division_id,sub_division,
                            office_shift, manager, gross_salary, gross_salary, 1, is_probation
                        ],
                    )
 
                    # ✅ Initialize leave balances
                    if is_probation in ["N", "n"]:
                        self._init_leave_balances(
                            cursor=c,
                            employee_id=emp_id,
                            employee_name=f"{first_name} {last_name}"
                        )
 
                    # ✅ Allocate all policies automatically
                    self._allocate_policies(cursor=c, emp_id=emp_id)
 
                    # ✅ Fetch & store employee documents from RAAS
                    self._fetch_and_store_documents_from_raas(
                        cursor=c,
                        email=email,
                        user_id=user_id,
                        emp_id=emp_id
                    )
 
            return Response(
                {"status": "success", "message": "Employee added successfully with policies & documents stored."},
                status=status.HTTP_201_CREATED,
            )
 
        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
 
    def _init_leave_balances(self, cursor, employee_id, employee_name):
        """Initialize leave balances"""
        current_year = datetime.now().year
        leave_assignments = {
            "Casual Leave (CL)": 6,
            "Medical Leave (ML)": 7,
            "Maternity Leave": 182,
            "Paid Leave": 5,
            "Paternity Leave": 3,
        }
 
        cursor.execute(
            "SELECT constants_id, category_name FROM ci_erp_constants WHERE type = 'leave_type' AND category_name IN %s",
            [tuple(leave_assignments.keys())],
        )
        leave_types = cursor.fetchall()
 
        for constants_id, category_name in leave_types:
            cursor.execute(
                """
                INSERT INTO ci_leave_balance
                (employee_id, employee_name, leave_type_id, leave_type, balance_leave, carry_forward, last_paid_leave_given_at, year, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Y')
                """,
                [employee_id, employee_name, constants_id, category_name,
                 leave_assignments[category_name], 0, None, current_year],
            )
 
    def _allocate_policies(self, cursor, emp_id):
        """Allocate all policies to a newly created employee"""
        now = datetime.now()
 
        cursor.execute("SELECT policy_id FROM ci_policies")
        policies = cursor.fetchall()
        if not policies:
            return
 
        policy_ids = [str(row[0]) for row in policies]
        policy_ids_str = ",".join(policy_ids)
 
        cursor.execute("SELECT 1 FROM ci_policy_allocations WHERE emp_id = %s", [emp_id])
        if cursor.fetchone():
            return  
 
        cursor.execute(
            """
            INSERT INTO ci_policy_allocations (emp_id, policy_id, allocation_date)
            VALUES (%s, %s, %s)
            """,
            [emp_id, policy_ids_str, now],
        )
 
    # -------------------------------
    # ✅ NEW METHODS for Documents
    # -------------------------------
    def _fetch_and_store_documents_from_raas(self, cursor, email, user_id, emp_id):
        """Fetch employee documents from RAAS and store them in HRMS"""
        try:
            raas_response = requests.post(
                "https://raasbackend.vetrinahealthcare.com/fetch_documents/",
                json={"email_id": email}
            ).json()
 
            if raas_response.get("status") != "success":
                return
 
            documents = raas_response.get("documents", {})
 
            for doc_type, raas_url in documents.items():
                if not raas_url:
                    continue
 
                hrms_url = self._save_document_from_raas(raas_url, emp_id, doc_type)
 
                if hrms_url:
                    cursor.execute("""
                        INSERT INTO ci_employee_documents (user_id, employee_id, document_type, document_url)
                        VALUES (%s, %s, %s, %s)
                    """, [user_id, emp_id, doc_type, hrms_url])
 
        except Exception as e:
            print(f"Failed fetching documents from RAAS: {e}")
 
    def _save_document_from_raas(self, raas_url, emp_id, doc_type):
        """Download from RAAS and save in HRMS"""
        try:
            response = requests.get(raas_url, stream=True)
            response.raise_for_status()
 
            ext = raas_url.split(".")[-1]
            new_file_name = f"{emp_id}_{doc_type}.{ext}"
            upload_dir = os.path.join(settings.MEDIA_ROOT, "employee_documents")
            os.makedirs(upload_dir, exist_ok=True)
 
            destination_path = os.path.join(upload_dir, new_file_name)
            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
 
            # ✅ Always build full URL using SITE_URL
            return f"{settings.SITE_URL}/hrms-backend{settings.MEDIA_URL}employee_documents/{new_file_name}"
 
        except Exception as e:
            # print(f"Error saving document {doc_type}: {e}")
            return None
 
 



class RoleList(APIView):
    # permission_classes = [IsAdmin]

    def get(self, request, role_id=None):

        try:
            with connection.cursor() as c:

                c.execute(
                    """select role_id,role_name,role_access,created_at from ci_staff_roles group by role_id"""
                )

                rows = c.fetchall()
                response = [
                    {
                        "index": row[0],
                        "role_name": row[1],
                        "menu_permission": row[2],
                        "added_date": row[3],
                    }
                    for idx, row in enumerate(rows, start=1)
                ]

                return Response(
                    {"status": "success", "data": response}, status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):

        role_id = request.data.get("role_id")
        if not role_id:
            return Response(
                {"status": "error", "message": "role_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build the update fields dynamically
        update_fields = []
        update_values = []

        if "role_name" in request.data:
            update_fields.append("role_name = %s")
            update_values.append(request.data["role_name"])

        if "role_access" in request.data:
            update_fields.append("role_access = %s")
            update_values.append(request.data["role_access"])

        if "role_resources" in request.data:
            role_resources = request.data["role_resources"]
            if not isinstance(role_resources, list):
                return Response(
                    {"status": "error", "message": "role_resources must be a list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            update_fields.append("role_resources = %s")
            update_values.append(json.dumps(role_resources))

        if not update_fields:
            return Response(
                {"status": "error", "message": "No valid fields to update"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Add role_id at the end for WHERE clause
        update_values.append(role_id)

        try:
            with transaction.atomic():
                with connection.cursor() as c:
                    query = f"""
                        UPDATE ci_staff_roles
                        SET {", ".join(update_fields)}
                        WHERE role_id = %s
                    """
                    c.execute(query, update_values)

            return Response(
                {"status": "success", "message": "role updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, role_id):

        role_id = request.data.get("role_id")

        if not role_id:
            return Response(
                {"status": "error", "message": "role_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    c.execute(
                        """delete from ci_staff_roles where role_id = %s""", [role_id]
                    )

            return Response(
                {"status": "error", "message": "role deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AddRole(APIView):

    # permission_classes = [IsAdmin]

    def post(self, request):

        role_name = request.data.get("role_name")
        role_access = request.data.get("role_access")
        role_resources = request.data.get("role_resources")

        if not isinstance(role_resources, list):
            return Response(
                {"status": "error", "message": "role_resources must be a list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role_resources_json = json.dumps(role_resources)

        if not request:
            return Response(
                {"status": "error", "message": "some fields are missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    query = """insert into ci_staff_roles(company_id,role_name,role_access,role_resources,created_at) values(%s,%s,%s,%s, NOW())"""

                    c.execute(query, [2, role_name, role_access, role_resources_json])

            return Response(
                {"status": "success", "message": "role added successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeShiftList(APIView):

    def get(self, request, shift_id=None):

        try:
            with connection.cursor() as c:

                c.execute("""select * from ci_office_shifts""")
                columns = [col[0] for col in c.description]
                rows = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": rows}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        required_fields = [
            "shift_id",
            "employee_hub_id",
            "shift_name",
            "monday_in_time",
            "monday_out_time",
            "tuesday_in_time",
            "tuesday_out_time",
            "wednesday_in_time",
            "wednesday_out_time",
            "thursday_in_time",
            "thursday_out_time",
            "friday_in_time",
            "friday_out_time",
            "saturday_in_time",
            "saturday_out_time",
            "sunday_in_time",
            "sunday_out_time",
        ]

        missing_fields = [
            field for field in required_fields if field not in request.data
        ]

        if missing_fields:
            return Response(
                {
                    "status": "error",
                    "message": f"Missing fields: {', '.join(missing_fields)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:
                    query = """
                    UPDATE ci_office_shifts
                    SET 
                        employee_hub_id = %s,
                        shift_name = %s,
                        monday_in_time = %s, monday_out_time = %s,
                        tuesday_in_time = %s, tuesday_out_time = %s,
                        wednesday_in_time = %s, wednesday_out_time = %s,
                        thursday_in_time = %s, thursday_out_time = %s,
                        friday_in_time = %s, friday_out_time = %s,
                        saturday_in_time = %s, saturday_out_time = %s,
                        sunday_in_time = %s, sunday_out_time = %s
                    WHERE office_shift_id = %s
                """
                    values = (
                        request.data["employee_hub_id"],
                        request.data["shift_name"],
                        request.data["monday_in_time"],
                        request.data["monday_out_time"],
                        request.data["tuesday_in_time"],
                        request.data["tuesday_out_time"],
                        request.data["wednesday_in_time"],
                        request.data["wednesday_out_time"],
                        request.data["thursday_in_time"],
                        request.data["thursday_out_time"],
                        request.data["friday_in_time"],
                        request.data["friday_out_time"],
                        request.data["saturday_in_time"],
                        request.data["saturday_out_time"],
                        request.data["sunday_in_time"],
                        request.data["sunday_out_time"],
                        request.data["shift_id"],
                    )
                    c.execute(query, values)

            return Response(
                {"status": "success", "message": "shift updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, shift_id):

        if not shift_id:
            return Response(
                {"status": "error", "message": "shift_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    c.execute(
                        """delete from ci_office_shifts where office_shift_id = %s""",
                        [shift_id],
                    )

            return Response(
                {"status": "error", "message": "office shift deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):

        # # # print(f"Request data: {request.data}")

        required_fields = [
            "employee_hub_id",
            "shift_name",
            "monday_in_time",
            "monday_out_time",
            "tuesday_in_time",
            "tuesday_out_time",
            "wednesday_in_time",
            "wednesday_out_time",
            "thursday_in_time",
            "thursday_out_time",
            "friday_in_time",
            "friday_out_time",
            "saturday_in_time",
            "saturday_out_time",
            "sunday_in_time",
            "sunday_out_time",
        ]

        missing_fields = [
            field for field in required_fields if field not in request.data
        ]

        if missing_fields:
            return Response(
                {
                    "status": "error",
                    "message": f"Missing fields: {', '.join(missing_fields)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:
                    query = """
                        INSERT INTO ci_office_shifts (
                            employee_hub_id,
                            shift_name,
                            company_id,
                            monday_in_time, monday_out_time,
                            tuesday_in_time, tuesday_out_time,
                            wednesday_in_time, wednesday_out_time,
                            thursday_in_time, thursday_out_time,
                            friday_in_time, friday_out_time,
                            saturday_in_time, saturday_out_time,
                            sunday_in_time, sunday_out_time,
                            created_at
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                        )
                    """
                    values = (
                        int(request.data["employee_hub_id"]),
                        request.data["shift_name"],
                        2,
                        request.data["monday_in_time"],
                        request.data["monday_out_time"],
                        request.data["tuesday_in_time"],
                        request.data["tuesday_out_time"],
                        request.data["wednesday_in_time"],
                        request.data["wednesday_out_time"],
                        request.data["thursday_in_time"],
                        request.data["thursday_out_time"],
                        request.data["friday_in_time"],
                        request.data["friday_out_time"],
                        request.data["saturday_in_time"],
                        request.data["saturday_out_time"],
                        request.data["sunday_in_time"],
                        request.data["sunday_out_time"],
                    )
                    c.execute(query, values)

                    c.execute(
                        "SELECT first_name, email FROM ci_erp_users WHERE id = %s",
                        [request.data["user_id"]],
                    )

                    user_email_row = c.fetchone()

            if user_email_row:
                user_name = user_email_row[0]
                user_email = user_email_row[1]

                smtp_server = "smtp.hostinger.com"
                smtp_port = 465
                sender_email = "hrms@thedatatechlabs.com"
                sender_password = "Tdtl@2025#"
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)

                # to_email = user_email
                to_email = "atharva.jadhav@tdtl.world"

                subject = "Office-Shift Details"

                # Constructing HTML message
                html_content = f"""
                <html>
                    <body>
                        <strong><p>Dear {user_name},</p></strong>
                        <br><p>Your office shift has been successfully assigned. Below are your shift timings:</p>

                        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
                            <tr><th>Day</th><th>In Time</th><th>Out Time</th></tr>
                            <tr><td>Monday</td><td>{request.data['monday_in_time']}</td><td>{request.data['monday_out_time']}</td></tr>
                            <tr><td>Tuesday</td><td>{request.data['tuesday_in_time']}</td><td>{request.data['tuesday_out_time']}</td></tr>
                            <tr><td>Wednesday</td><td>{request.data['wednesday_in_time']}</td><td>{request.data['wednesday_out_time']}</td></tr>
                            <tr><td>Thursday</td><td>{request.data['thursday_in_time']}</td><td>{request.data['thursday_out_time']}</td></tr>
                            <tr><td>Friday</td><td>{request.data['friday_in_time']}</td><td>{request.data['friday_out_time']}</td></tr>
                            <tr><td>Saturday</td><td>{request.data['saturday_in_time']}</td><td>{request.data['saturday_out_time']}</td></tr>
                            <tr><td>Sunday</td><td>{request.data['sunday_in_time']}</td><td>{request.data['sunday_out_time']}</td></tr>
                        </table>

                        <strong><p>Regards,<br>TDTL HRMS</p></strong>
                    </body>
                </html>
                """

                try:
                    # Construct the MIME message
                    message = MIMEMultipart("alternative")
                    message["Subject"] = subject
                    message["From"] = sender_email
                    message["To"] = to_email

                    mime_text = MIMEText(html_content, "html")
                    message.attach(mime_text)

                    # Connect and send the email
                    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, to_email, message.as_string())

                except Exception as mail_error:
                    return Response(
                        f"Email failed to send: {str(mail_error)}",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {
                    "status": "success",
                    "message": "office shift created and mail sent successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# class EmployeeExitList(APIView):

#     def get(self, request):

#         try:
#             with connection.cursor() as c:

#                 c.execute("""""")

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


# class AttendanceOverview(APIView):

#     def get(self, request):

#         today = date.today()
#         state_id = request.data.get("state_id")
#         employee_hub_id = request.data.get("employee_hub_id")
#         # # # print("today: ", today)

#         try:
#             with connection.cursor() as c:

#                 if state_id and employee_hub_id:

#                     query = """
#                         SELECT 
#                             CONCAT(u.first_name, ' ', u.last_name) AS full_name,
#                             u.email,
#                             DATE_FORMAT(bd.login_date, '%%d-%%m-%%Y') AS login_date,

#                             DATE_FORMAT(MIN(TIME(bd.clock_in)), '%%H:%%i') AS clock_in,
#                             DATE_FORMAT(MAX(TIME(bd.clock_out)), '%%H:%%i') AS clock_out,

#                             -- Late mark (after 9:30 AM)
#                             DATE_FORMAT(
#                                 SEC_TO_TIME(
#                                     GREATEST(
#                                         TIME_TO_SEC(TIMEDIFF(MIN(TIME(bd.clock_in)), '09:30:00')),
#                                         0
#                                     )
#                                 ), '%%H:%%i'
#                             ) AS late,

#                             -- Early leaving (before 7:00 PM)
#                             DATE_FORMAT(
#                                 SEC_TO_TIME(
#                                     GREATEST(
#                                         TIME_TO_SEC(TIMEDIFF('19:00:00', MAX(TIME(bd.clock_out)))),
#                                         0
#                                     )
#                                 ), '%%H:%%i'
#                             ) AS early_leaving,

#                             -- Total work time (first in to last out)
#                             DATE_FORMAT(
#                                 SEC_TO_TIME(
#                                     GREATEST(
#                                         TIME_TO_SEC(TIMEDIFF(MAX(TIME(bd.clock_out)), MIN(TIME(bd.clock_in)))),
#                                         0
#                                     )
#                                 ), '%%H:%%i'
#                             ) AS total_work

#                         FROM ci_biomatric_data bd
#                         LEFT JOIN ci_erp_users u ON bd.userid = u.id and u.state = %s and u.employee_hub_id = %s
#                         WHERE 
#                             CONCAT(u.first_name, ' ', u.last_name) IS NOT NULL
#                             -- AND DATE(bd.login_date) = '2024-07-12'
#                             AND DATE(bd.login_date) = %s
#                         GROUP BY bd.userid, DATE(bd.login_date)
#                         ORDER BY full_name ASC;
#                     """

#                     c.execute(query, [state_id, employee_hub_id, today])

#                 else:
#                     query = """
#                     SELECT 
#                         CONCAT(u.first_name, ' ', u.last_name) AS full_name,
#                         u.email,
#                         DATE_FORMAT(bd.login_date, '%%d-%%m-%%Y') AS login_date,

#                         DATE_FORMAT(MIN(TIME(bd.clock_in)), '%%H:%%i') AS clock_in,
#                         DATE_FORMAT(MAX(TIME(bd.clock_out)), '%%H:%%i') AS clock_out,

#                         -- Late mark (after 9:30 AM)
#                         DATE_FORMAT(
#                             SEC_TO_TIME(
#                                 GREATEST(
#                                     TIME_TO_SEC(TIMEDIFF(MIN(TIME(bd.clock_in)), '09:30:00')),
#                                     0
#                                 )
#                             ), '%%H:%%i'
#                         ) AS late,

#                         -- Early leaving (before 7:00 PM)
#                         DATE_FORMAT(
#                             SEC_TO_TIME(
#                                 GREATEST(
#                                     TIME_TO_SEC(TIMEDIFF('19:00:00', MAX(TIME(bd.clock_out)))),
#                                     0
#                                 )
#                             ), '%%H:%%i'
#                         ) AS early_leaving,

#                         -- Total work time (first in to last out)
#                         DATE_FORMAT(
#                             SEC_TO_TIME(
#                                 GREATEST(
#                                     TIME_TO_SEC(TIMEDIFF(MAX(TIME(bd.clock_out)), MIN(TIME(bd.clock_in)))),
#                                     0
#                                 )
#                             ), '%%H:%%i'
#                         ) AS total_work

#                     FROM ci_biomatric_data bd
#                     LEFT JOIN ci_erp_users u ON bd.userid = u.id
#                     WHERE 
#                         CONCAT(u.first_name, ' ', u.last_name) IS NOT NULL
#                         -- AND DATE(bd.login_date) = '2024-07-12'
#                         AND DATE(bd.login_date) = %s
#                     GROUP BY bd.userid, DATE(bd.login_date)
#                     ORDER BY full_name ASC;
#                 """
#                     c.execute(query, [today])

#                 columns = [col[0] for col in c.description]
#                 response = [dict(zip(columns, row)) for row in c.fetchall()]

#             return Response(
#                 {"status": "success", "data": response}, status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occured: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

# class AttendanceOverview(APIView):

#     def post(self, request):

#         today = date.today()
#         state_id = request.data.get("state_id")
#         employee_hub_id = request.data.get("employee_hub_id")
#         # # # print("today: ", today)

#         try:
#             with connection.cursor() as c:

#                 if state_id and employee_hub_id:

#                     # if employee_hub_id == '2':

#                     query = """
#                         SELECT 
#                             CONCAT(u.first_name, ' ', u.last_name) AS full_name,
#                             u.email,
#                             DATE_FORMAT(bd.login_date, '%%d-%%m-%%Y') AS login_date,

#                             DATE_FORMAT(TIME(bd2.clock_in), '%%H:%%i') AS clock_in,
#                             DATE_FORMAT(TIME(bd2.clock_out), '%%H:%%i') AS clock_out,

#                             -- Shift times based on the day of the week
#                             CASE DAYOFWEEK(bd.login_date)
#                                 WHEN 1 THEN os.sunday_in_time      -- Sunday
#                                 WHEN 2 THEN os.monday_in_time      -- Monday
#                                 WHEN 3 THEN os.tuesday_in_time     -- Tuesday
#                                 WHEN 4 THEN os.wednesday_in_time   -- Wednesday
#                                 WHEN 5 THEN os.thursday_in_time    -- Thursday
#                                 WHEN 6 THEN os.friday_in_time      -- Friday
#                                 WHEN 7 THEN os.saturday_in_time    -- Saturday
#                             END AS shift_in_time,
                            
#                             CASE DAYOFWEEK(bd.login_date)
#                                 WHEN 1 THEN os.sunday_out_time     -- Sunday
#                                 WHEN 2 THEN os.monday_out_time     -- Monday
#                                 WHEN 3 THEN os.tuesday_out_time    -- Tuesday
#                                 WHEN 4 THEN os.wednesday_out_time  -- Wednesday
#                                 WHEN 5 THEN os.thursday_out_time   -- Thursday
#                                 WHEN 6 THEN os.friday_out_time     -- Friday
#                                 WHEN 7 THEN os.saturday_out_time   -- Saturday
#                             END AS shift_out_time,

#                             -- Late mark calculation using dynamic shift time
#                             DATE_FORMAT(
#                                 SEC_TO_TIME(
#                                     GREATEST(
#                                         TIME_TO_SEC(TIMEDIFF(
#                                             MIN(TIME(bd.clock_in)), 
#                                             CASE DAYOFWEEK(bd.login_date)
#                                                 WHEN 1 THEN os.sunday_in_time
#                                                 WHEN 2 THEN os.monday_in_time
#                                                 WHEN 3 THEN os.tuesday_in_time
#                                                 WHEN 4 THEN os.wednesday_in_time
#                                                 WHEN 5 THEN os.thursday_in_time
#                                                 WHEN 6 THEN os.friday_in_time
#                                                 WHEN 7 THEN os.saturday_in_time
#                                             END
#                                         )),
#                                         0
#                                     )
#                                 ), '%%H:%%i'
#                             ) AS late,

#                             -- Early leaving calculation using dynamic shift time
#                             DATE_FORMAT(
#                                 SEC_TO_TIME(
#                                     GREATEST(
#                                         TIME_TO_SEC(TIMEDIFF(
#                                             CASE DAYOFWEEK(bd.login_date)
#                                                 WHEN 1 THEN os.sunday_out_time
#                                                 WHEN 2 THEN os.monday_out_time
#                                                 WHEN 3 THEN os.tuesday_out_time
#                                                 WHEN 4 THEN os.wednesday_out_time
#                                                 WHEN 5 THEN os.thursday_out_time
#                                                 WHEN 6 THEN os.friday_out_time
#                                                 WHEN 7 THEN os.saturday_out_time
#                                             END,
#                                             MAX(TIME(bd.clock_out))
#                                         )),
#                                         0
#                                     )
#                                 ), '%%H:%%i'
#                             ) AS early_leaving,

#                             -- Total work time (first in to last out)
#                             DATE_FORMAT(TIME(bd.total_work), '%%H:%%i') AS total_work,
#                             bd.is_half_day,
#                             os.shift_name

#                         FROM ci_biomatric_data bd
#                         INNER JOIN (
#                             SELECT 
#                                 bd2_sub.ci_biomatric_id,
#                                 bd2_sub.clock_in,
#                                 bd2_sub.clock_out
#                             FROM ci_biomatric_data_2 bd2_sub
#                             INNER JOIN (
#                                 SELECT ci_biomatric_id, MAX(id) AS max_id
#                                 FROM ci_biomatric_data_2
#                                 GROUP BY ci_biomatric_id
#                             ) latest_bd2 ON bd2_sub.id = latest_bd2.max_id
#                         ) bd2 ON bd.ci_biomatric_id = bd2.ci_biomatric_id
#                         LEFT JOIN ci_erp_users u ON bd.userid = u.id AND u.state = %s AND u.employee_hub_id = %s
#                         LEFT JOIN ci_office_shifts os ON u.employee_hub_id = os.employee_hub_id
#                         WHERE 
#                             CONCAT(u.first_name, ' ', u.last_name) IS NOT NULL
#                             AND DATE(bd.login_date) = %s
#                         GROUP BY bd.userid, DATE(bd.login_date), os.office_shift_id
#                         ORDER BY full_name ASC;
#                     """

#                     c.execute(query, [state_id, employee_hub_id, today])

#                 #     elif employee_hub_id == '3':

#                 #         query = """
#                 #         SELECT 
#                 #             CONCAT(u.first_name, ' ', u.last_name) AS full_name,
#                 #             u.email,
#                 #             DATE_FORMAT(bd.login_date, '%%d-%%m-%%Y') AS login_date,

#                 #             DATE_FORMAT(MIN(TIME(bd.clock_in)), '%%H:%%i') AS clock_in,
#                 #             DATE_FORMAT(MAX(TIME(bd.clock_out)), '%%H:%%i') AS clock_out,

#                 #             -- Late mark (after 9:30 AM)
#                 #             DATE_FORMAT(
#                 #                 SEC_TO_TIME(
#                 #                     GREATEST(
#                 #                         TIME_TO_SEC(TIMEDIFF(MIN(TIME(bd.clock_in)), '09:00:00')),
#                 #                         0
#                 #                     )
#                 #                 ), '%%H:%%i'
#                 #             ) AS late,

#                 #             -- Early leaving (before 7:00 PM)
#                 #             DATE_FORMAT(
#                 #                 SEC_TO_TIME(
#                 #                     GREATEST(
#                 #                         TIME_TO_SEC(TIMEDIFF('17:30:00', MAX(TIME(bd.clock_out)))),
#                 #                         0
#                 #                     )
#                 #                 ), '%%H:%%i'
#                 #             ) AS early_leaving,

#                 #             -- Total work time (first in to last out)
#                 #             DATE_FORMAT(TIME(bd.total_work), '%%H:%%i') AS total_work,
#                 #             bd.is_half_day

#                 #         FROM ci_biomatric_data bd
#                 #         LEFT JOIN ci_erp_users u ON bd.userid = u.id and u.state = %s and u.employee_hub_id = %s
#                 #         WHERE 
#                 #             CONCAT(u.first_name, ' ', u.last_name) IS NOT NULL
#                 #             -- AND DATE(bd.login_date) = '2024-07-12'
#                 #             AND DATE(bd.login_date) = %s
#                 #         GROUP BY bd.userid, DATE(bd.login_date)
#                 #         ORDER BY full_name ASC;
#                 #     """

#                 #         c.execute(query, [state_id, employee_hub_id, today])

#                 # else:
#                 #     query = """
#                 #         SELECT 
#                 #             CONCAT(u.first_name, ' ', u.last_name) AS full_name,
#                 #             u.email,
#                 #             DATE_FORMAT(bd.login_date, '%%d-%%m-%%Y') AS login_date,

#                 #             DATE_FORMAT(MIN(TIME(bd.clock_in)), '%%H:%%i') AS clock_in,
#                 #             DATE_FORMAT(MAX(TIME(bd.clock_out)), '%%H:%%i') AS clock_out,

#                 #             -- Late mark (after 9:30 AM)
#                 #             DATE_FORMAT(
#                 #                 SEC_TO_TIME(
#                 #                     GREATEST(
#                 #                         TIME_TO_SEC(TIMEDIFF(MIN(TIME(bd.clock_in)), '09:00:00')),
#                 #                         0
#                 #                     )
#                 #                 ), '%%H:%%i'
#                 #             ) AS late,

#                 #             -- Early leaving (before 7:00 PM)
#                 #             DATE_FORMAT(
#                 #                 SEC_TO_TIME(
#                 #                     GREATEST(
#                 #                         TIME_TO_SEC(TIMEDIFF('17:30:00', MAX(TIME(bd.clock_out)))),
#                 #                         0
#                 #                     )
#                 #                 ), '%%H:%%i'
#                 #             ) AS early_leaving,

#                 #             -- Total work time (first in to last out)
#                 #             DATE_FORMAT(TIME(bd.total_work), '%%H:%%i') AS total_work,
#                 #             bd.is_half_day

#                 #         FROM ci_biomatric_data bd
#                 #         LEFT JOIN ci_erp_users u ON bd.userid = u.id
#                 #         WHERE 
#                 #             CONCAT(u.first_name, ' ', u.last_name) IS NOT NULL
#                 #             -- AND DATE(bd.login_date) = '2024-07-12'
#                 #             AND DATE(bd.login_date) = %s
#                 #         GROUP BY bd.userid, DATE(bd.login_date)
#                 #         ORDER BY full_name ASC;
#                 # """
#                 #     c.execute(query, [today])

#                 columns = [col[0] for col in c.description]
#                 response = [dict(zip(columns, row)) for row in c.fetchall()]

#             return Response(
#                 {"status": "success", "data": response}, status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occured: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

class AttendanceOverview(APIView):

    def get(self, request):
        today = date.today()

        try:
            with connection.cursor() as c:
                query = """
                    SELECT 
                        CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                        u.profile_photo AS avatar,
                        u.email,
                        bd.login_date,
                        bd.attendance_status,
                        bd.clock_in,
                        bd.clock_out,
                        bd.late_mark,
                        bd.early_mark,
                        bd.is_half_day
                    FROM ci_biomatric_data bd
                    LEFT JOIN ci_erp_users u ON bd.userid = u.id
                    WHERE DATE(bd.login_date) = %s
                    ORDER BY full_name ASC;
                """
                c.execute(query, [today])
                columns = [col[0] for col in c.description]
                rows = c.fetchall()

            response = []
            for row in rows:
                data = dict(zip(columns, row))

                # Format clock_in / clock_out to HH:MM (if present)
                if data["clock_in"]:
                    try:
                        data["clock_in"] = datetime.strptime(data["clock_in"], "%H:%M:%S").strftime("%H:%M")
                    except Exception:
                        pass
                if data["clock_out"]:
                    try:
                        data["clock_out"] = datetime.strptime(data["clock_out"], "%H:%M:%S").strftime("%H:%M")
                    except Exception:
                        pass

                # Calculate total_work from raw times
                if data["clock_in"] and data["clock_out"]:
                    try:
                        clock_in_time = datetime.strptime(data["clock_in"], "%H:%M")
                        clock_out_time = datetime.strptime(data["clock_out"], "%H:%M")
                        total_seconds = (clock_out_time - clock_in_time).seconds
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        data["total_work"] = f"{hours:02}:{minutes:02}"
                    except Exception:
                        data["total_work"] = None
                else:
                    data["total_work"] = None

                response.append(data)

            return Response(
                {"status": "success", "data": response}, status=200
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=500,
            ) 

class ManualAttendance(APIView):

    def get(self, request):

        today = date.today()
        # # # print("today: ", today)

        try:
            with connection.cursor() as c:

                query = """
                    SELECT 
                        bd.ci_biomatric_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                        u.email,
                        DATE_FORMAT(bd.login_date, '%%d-%%m-%%Y') AS date,

                        DATE_FORMAT(MIN(TIME(bd.clock_in)), '%%H:%%i') AS time_in,
                        DATE_FORMAT(MAX(TIME(bd.clock_out)), '%%H:%%i') AS time_out,

                        bd.reason

                    FROM ci_biomatric_data bd
                    LEFT JOIN ci_erp_users u ON bd.userid = u.id
                    WHERE 
                        CONCAT(u.first_name, ' ', u.last_name) IS NOT NULL
                        AND bd.from_od = 'M'
                        -- AND DATE(bd.login_date) = '2024-08-14'
                        AND DATE(bd.login_date) = %s
                        
                    GROUP BY bd.userid, DATE(bd.login_date)
                    ORDER BY full_name ASC;
                """

                c.execute(query, [today])

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):

        today = date.today()

        user_id = request.data.get("user_id")
        emp_id = request.data.get("employee_id")
        time_in = request.data.get("time_in")
        time_out = request.data.get("time_out")
        reason = request.data.get("reason")
        latitude = request.data.get("latitude")  # From frontend
        longitude = request.data.get("longitude")  # From frontend

        location = f"{latitude},{longitude}" if latitude and longitude else ""

        # try:
        #     with connection.cursor() as c:
        #         with transaction.atomic():
        #             c.execute(
        #                 """insert into ci_biomatric_data(emp_id,userid,login_date,clock_in,clock_in_location,clock_out,clock_out_location,state_in_out,late_mark,early_mark,total_work,attendance_date,attendance_status,status,from_od,reason,wfh) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        #                 [
        #                     emp_id,
        #                     user_id,
        #                     today,
        #                     time_in,
        #                     "",
        #                     "",
        #                     "",
        #                     "in",
        #                     "",
        #                     "",
        #                     "",
        #                     today,
        #                     "Present",
        #                     "Y",
        #                     "Y",
        #                     reason,
        #                     "N",
        #                 ],
        #             )

        #             c.execute(
        #                 """insert into ci_biomatric_data(emp_id,userid,login_date,clock_in,clock_in_location,clock_out,clock_out_location,state_in_out,late_mark,early_mark,total_work,attendance_date,attendance_status,status,from_od,reason,wfh) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        #                 [
        #                     emp_id,
        #                     user_id,
        #                     today,
        #                     "",
        #                     "",
        #                     time_out,
        #                     "",
        #                     "out",
        #                     "",
        #                     "",
        #                     "",
        #                     today,
        #                     "Present",
        #                     "Y",
        #                     "M",
        #                     reason,
        #                     "N",
        #                 ],
        #             )

        #     # connection.commit()

        #     return Response(
        #         {
        #             "status": "success",
        #             "message": "manual attendance created successfully",
        #         },
        #         status=status.HTTP_201_CREATED,
        #     )

        # except Exception as e:
        #     return Response(
        #         {"status": "error", "message": f"An error occured: {str(e)}"},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     )

        try:
            with connection.cursor() as c:
                with transaction.atomic():
                    if time_in:
                        c.execute(
                            """INSERT INTO ci_biomatric_data (
                                emp_id, userid, login_date, clock_in, clock_in_location,
                                clock_out, clock_out_location, state_in_out, late_mark,
                                early_mark, total_work, attendance_date, attendance_status,
                                status, from_od, reason, wfh
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            [
                                emp_id,
                                user_id,
                                today,
                                time_in,
                                location,
                                "",
                                "",
                                "in",
                                "",
                                "",
                                "",
                                today,
                                "Present",
                                "Y",
                                "Y",
                                reason,
                                "N",
                            ],
                        )

                    if time_out:
                        c.execute(
                            """INSERT INTO ci_biomatric_data (
                                emp_id, userid, login_date, clock_in, clock_in_location,
                                clock_out, clock_out_location, state_in_out, late_mark,
                                early_mark, total_work, attendance_date, attendance_status,
                                status, from_od, reason, wfh
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            [
                                emp_id,
                                user_id,
                                today,
                                "",
                                "",
                                time_out,
                                location,
                                "out",
                                "",
                                "",
                                "",
                                today,
                                "Present",
                                "Y",
                                "Y",
                                reason,
                                "N",
                            ],
                        )

            return Response(
                {
                    "status": "success",
                    "message": "manual attendance created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StateDropdown(APIView):

    def get(self, request):

        try:
            with connection.cursor() as c:

                c.execute(
                    """select constants_id as state_id, category_name as state_name from ci_erp_constants where type = 'state'"""
                )

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmployeeHubDropdown(APIView):

    def get(self, request, state_id):

        if not state_id:
            return Response(
                {"status": "error", "message": "state_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                c.execute(
                    """select employee_hub_id, employee_hub_name from ci_employee_hub where state_id = %s""",
                    [state_id],
                )

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmployeeHub(APIView):

    def post(self, request):

        state_id = request.data.get("state_id")
        emp_hub_name = request.data.get("employee_hub_name")

        try:
            with connection.cursor() as c:
                with transaction.atomic():
                    c.execute(
                        """insert into ci_employee_hub(state_id, employee_hub_name) values(%s,%s)""",
                        [state_id, emp_hub_name],
                    )

            return Response(
                {"status": "success", "message": "employee hub added successfully"},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:

            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):

        try:
            with connection.cursor() as c:

                c.execute(
                    """select employee_hub_id, constants_id as state_id, category_name as state_name, employee_hub_name, eh.created_at from ci_employee_hub eh join ci_erp_constants ec on eh.state_id = ec.constants_id"""
                )

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):

        employee_hub_id = request.data.get("employee_hub_id")
        state_id = request.data.get("state_id")
        employee_hub_name = request.data.get("employee_hub_name")

        if not employee_hub_id:
            return Response(
                {"status": "error", "message": "employee_hub_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            set_clauses = []
            params = []

            if state_id is not None:
                set_clauses.append("state_id = %s")
                params.append(state_id)

            if employee_hub_name is not None:
                set_clauses.append("employee_hub_name = %s")
                params.append(employee_hub_name)

            if not set_clauses:
                return Response(
                    {"status": "error", "message": "No data provided to update"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            set_clause_str = ", ".join(set_clauses)
            params.append(employee_hub_id)  # for WHERE clause

            query = f"""UPDATE ci_employee_hub SET {set_clause_str} WHERE employee_hub_id = %s"""

            with connection.cursor() as c:
                with transaction.atomic():
                    c.execute(query, params)

            return Response(
                {"status": "success", "message": "Employee hub updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):

        employee_hub_id = request.data.get("employee_hub_id")

        try:
            with connection.cursor() as c:
                with transaction.atomic():

                    c.execute(
                        """delete from ci_employee_hub where employee_hub_id = %s""",
                        [employee_hub_id],
                    )

            return Response(
                {"status": "success", "message": "employee hub deleted successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AttendanceMonthlyReport(APIView):

    def post(self, request):

        employee_id = request.data.get("employee_id")
        year = request.data.get("year")
        month = request.data.get("month")

        try:
            with connection.cursor() as c:

                c.execute(
                    """
                    SELECT 
                        DATE_FORMAT(STR_TO_DATE(login_date, '%%Y-%%m-%%d'), '%%W') AS day,
                        DATE_FORMAT(STR_TO_DATE(login_date, '%%Y-%%m-%%d'), '%%d-%%m-%%Y') AS date,
                        CASE 
                            WHEN MAX(attendance_status) = 'Present' THEN 'Present'
                            ELSE 'Absent'
                        END AS status,
                        DATE_FORMAT(MIN(TIME(clock_in)), '%%H:%%i') AS clock_in,
                        DATE_FORMAT(MAX(TIME(clock_out)), '%%H:%%i') AS clock_out
                    FROM ci_biomatric_data
                    WHERE 
                        emp_id = %s
                        AND YEAR(STR_TO_DATE(login_date, '%%Y-%%m-%%d')) = %s
                        AND MONTH(STR_TO_DATE(login_date, '%%Y-%%m-%%d')) = %s
                    GROUP BY STR_TO_DATE(login_date, '%%Y-%%m-%%d')
                    ORDER BY STR_TO_DATE(login_date, '%%Y-%%m-%%d');
                    """,
                    [employee_id, year, month],
                )

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class Holiday(APIView):

    def get(self, request):

        try:
            with connection.cursor() as c:

                c.execute(
                    """SELECT 
                            h.holiday_id,
                            h.event_name,
                            h.description,
                            CASE 
                                WHEN ec.category_name IS NOT NULL 
                                THEN ec.category_name 
                                ELSE h.state 
                            END AS state,
                            eh.employee_hub_name,
                            h.start_date,
                            h.end_date,
                            h.is_publish AS status,
                            ctry.category_name AS country
                        FROM ci_holidays h
                        LEFT JOIN ci_erp_constants ec 
                            ON h.state = ec.constants_id
                        LEFT JOIN ci_employee_hub eh 
                            ON h.employee_hub = eh.employee_hub_id
                        LEFT JOIN ci_erp_constants ctry 
                            ON h.country = ctry.constants_id;"""
                )

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):

        holiday_id = request.data.get("holiday_id")
        if not holiday_id:
            return Response(
                {"status": "error", "message": "holiday_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        field_map = {
            "event_name": request.data.get("event_title"),
            "state": request.data.get("state"),
            "employee_hub": request.data.get("employee_hub"),
            "start_date": request.data.get("start_date"),
            "end_date": request.data.get("end_date"),
            "is_publish": request.data.get("is_publish"),
            "country": request.data.get("country"),
        }

        set_clauses = []
        values = []

        for column, value in field_map.items():
            if value is not None:
                set_clauses.append(f"{column} = %s")
                values.append(value)

        if not set_clauses:
            return Response(
                {"status": "error", "message": "No fields provided to update."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        set_clause_str = ", ".join(set_clauses)
        values.append(holiday_id)  # for WHERE clause

        try:
            with connection.cursor() as c:
                query = f"""
                    UPDATE ci_holidays
                    SET {set_clause_str}
                    WHERE holiday_id = %s
                """
                c.execute(query, values)

            return Response(
                {"status": "success", "message": "Holiday updated successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):

        fields = {
            "event_name": request.data.get("event_name"),
            "state": request.data.get("state"),
            "employee_hub": request.data.get("employee_hub"),
            "start_date": request.data.get("start_date"),
            "end_date": request.data.get("end_date"),
            "description": request.data.get("description"),
            "is_publish": request.data.get("is_publish"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "country":request.data.get("country")
        }

        fields["company_id"] = 2

        columns = []
        values = []
        placeholders = []

        for column, value in fields.items():
            if value is not None:
                columns.append(column)
                values.append(value)
                placeholders.append("%s")

        if not columns:
            return Response(
                {"status": "error", "message": "No data provided to insert."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        column_str = ", ".join(columns)
        placeholder_str = ", ".join(placeholders)

        try:
            with connection.cursor() as c:
                query = f"""
                    INSERT INTO ci_holidays ({column_str})
                    VALUES ({placeholder_str})
                """
                c.execute(query, values)

            return Response(
                {"status": "success", "message": "Holiday saved successfully."},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):

        holiday_id = request.data.get("holiday_id")

        if not holiday_id:
            return Response(
                {"status": "error", "message": "holiday_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    c.execute(
                        "DELETE FROM ci_holidays WHERE holiday_id = %s", [holiday_id]
                    )

            return Response(
                {
                    "status": "success",
                    "message": "holiday deleted successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
 
class PayrollSetupConfiguration(APIView):

    def get(self, request):

        try:
            with connection.cursor() as c:

                c.execute("""select * from ci_salary_structure""")
                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):

        fields = [
            # Earnings
            "hra",
            "basic_plus_da",
            "medical_allowance_with_esic",
            "medical_allowance_without_esic",
            "conveyance_allowance_with_esic",
            "conveyance_allowance_without_esic",
            # Deductions
            "pf_employee_contribution",
            "esic_employee_contribution",
            "tds",
            "mlwf_deduction",
            "pt_for_male",
            "pt_for_female",
            # Benefits
            "pf_employer_contribution",
            "esic_employer_contribution",
            "gratuity",
        ]

        try:
            with transaction.atomic():
                with connection.cursor() as c:
                    for field in fields:
                        value = request.data.get(field)
                        if value is not None:
                            c.execute(
                                """
                                UPDATE ci_salary_structure
                                SET value = %s
                                WHERE particulars = %s
                                """,
                                [value, field],
                            )

            return Response(
                {"status": "success", "message": "Salary structure updated."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetEmployeeSalary(APIView):

    def get(self, request):

        try:
            with connection.cursor() as c:
                c.execute(
                    """
                            SELECT 
                                u.id, ud.employee_id,CONCAT(first_name, ' ', last_name) AS employee_name, dt.department_name, ds.designation_name, ud.gross_salary as current_salary
                            FROM ci_erp_users u
                                LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
                                INNER JOIN ci_departments dt ON ud.department_id = dt.department_id
                                INNER JOIN ci_designations ds ON dt.department_id = ds.department_id
                                GROUP BY u.id
                          """
                )

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateEmployeeSalary(APIView):

    def patch(self, request):
        salary_updates = request.data.get("salaries")

        if not salary_updates or not isinstance(salary_updates, list):
            return Response(
                {"status": "error", "message": "No salary updates provided or format is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:
                    for item in salary_updates:
                        employee_id = item.get("employee_id")
                        previous_salary = item.get("previous_salary")
                        new_salary = item.get("new_salary")

                        if not all([employee_id, previous_salary, new_salary]):
                            raise ValueError("Missing fields in one of the salary records")

                        c.execute(
                            """UPDATE ci_erp_users_details SET gross_salary = %s WHERE employee_id = %s""",
                            [new_salary, employee_id],
                        )

                        # Insert into salary update log
                        c.execute(
                            """INSERT INTO ci_update_salary (employee_id, previous_salary, current_salary) 
                               VALUES (%s, %s, %s)""",
                            [employee_id, previous_salary, new_salary],
                        )

            return Response(
                {"status": "success", "message": "Salaries updated for all employees"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# class PayrollReport(APIView):

#     @staticmethod
#     def get_sundays_in_month(year, month):
#         sundays = []
#         total_days = calendar.monthrange(year, month)[1]
#         for day in range(1, total_days + 1):
#             current_date = date(year, month, day)
#             if current_date.weekday() == 6:  # Sunday
#                 sundays.append(current_date)
#         return sundays

#     def safe_decimal(self, value, default="0.00"):
#         try:
#             if value is None or value == "" or value == "None":
#                 return Decimal(default)
#             return Decimal(str(value))
#         except (InvalidOperation, ValueError, TypeError):
#             return Decimal(default)
    
#     # def calculate_gross_earning_with_salary_changes(self, employee_id, year, month, payable_days, days_in_month):
#     #     """
#     #     Calculate gross earning considering mid-month salary changes
#     #     """
#     #     with connection.cursor() as cursor:
#     #         # Get current salary
#     #         cursor.execute(
#     #             """SELECT gross_salary FROM ci_erp_users_details WHERE employee_id = %s""",
#     #             [employee_id]
#     #         )
#     #         current_salary_result = cursor.fetchone()
#     #         if not current_salary_result:
#     #             return self.safe_decimal("0.00"), self.safe_decimal("0.00")
            
#     #         # current_salary = Decimal(str(current_salary_result[0]))
#     #         current_salary = self.safe_decimal(current_salary_result[0])
            
#     #         # Get all salary changes for this employee in the given month/year
#     #         cursor.execute(
#     #             """
#     #             SELECT previous_salary, current_salary, updated_at
#     #             FROM ci_update_salary 
#     #             WHERE employee_id = %s 
#     #             AND MONTH(updated_at) = %s 
#     #             AND YEAR(updated_at) = %s
#     #             ORDER BY updated_at ASC
#     #             """,
#     #             [employee_id, month, year]
#     #         )
#     #         salary_changes = cursor.fetchall()
            
#     #         if not salary_changes:
#     #             # No salary changes in this month, use current salary for entire month
#     #             gross = (current_salary / self.safe_decimal(days_in_month)) * payable_days
#     #             return gross, current_salary
            
#     #         # Calculate total earnings based on daily rates for different periods
#     #         total_earnings = self.safe_decimal("0.00")
            
#     #         # Start with the first salary (before any changes)
#     #         previous_day = 1
#     #         # current_month_salary = Decimal(str(salary_changes[0][0]))  # previous_salary from first change
#     #         current_month_salary = self.safe_decimal(salary_changes[0][0])
            
#     #         for change in salary_changes:
#     #             previous_salary, new_salary, updated_at = change
#     #             change_day = updated_at.day
                
#     #             # Calculate days with previous salary (from previous_day to change_day-1)
#     #             days_with_current_salary = change_day - previous_day
#     #             if days_with_current_salary > 0:
#     #                 daily_rate = current_month_salary / self.safe_decimal(days_in_month)
#     #                 total_earnings += daily_rate * days_with_current_salary
                
#     #             # Update for next iteration
#     #             # current_month_salary = Decimal(str(new_salary))
#     #             current_month_salary = self.safe_decimal(new_salary)
#     #             previous_day = change_day
            
#     #         # Add remaining days of the month with the last salary
#     #         remaining_days = days_in_month - previous_day + 1
#     #         if remaining_days > 0:
#     #             daily_rate = current_month_salary / self.safe_decimal(days_in_month)
#     #             total_earnings += daily_rate * remaining_days
            
#     #         # Now calculate the proportional amount based on payable_days
#     #         total_monthly_earnings = total_earnings
#     #         # return (total_monthly_earnings / self.safe_decimal(days_in_month)) * payable_days
#     #         calculated_gross = (total_monthly_earnings / self.safe_decimal(days_in_month)) * payable_days
            
#     #     return calculated_gross, total_monthly_earnings

#     # def get(self, request, month, year):
#     #     try:
#     #         days_in_month = calendar.monthrange(year, month)[1]

#     #         with connection.cursor() as cursor:

#     #             # 1. Get Salary Structure
#     #             cursor.execute("SELECT particulars, value FROM ci_salary_structure")
#     #             salary_structure_raw = cursor.fetchall()
#     #             salary_structure = {k: self.safe_decimal(str(v)) for k, v in salary_structure_raw}

#     #             # 2. Get Employee Details
#     #             cursor.execute(
#     #                 """
#     #                 SELECT u.id, ud.employee_id, CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#     #                     dt.department_name, ds.designation_name,
#     #                     CASE 
#     #                         WHEN u.gender = 1 THEN 'Male'
#     #                         WHEN u.gender = 2 THEN 'Female'
#     #                         ELSE 'Other'
#     #                     END AS gender,
#     #                     ud.gross_salary,
#     #                     u.employee_hub_id,
#     #                     u.state
#     #                 FROM ci_erp_users u
#     #                 LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
#     #                 INNER JOIN ci_departments dt ON ud.department_id = dt.department_id
#     #                 INNER JOIN ci_designations ds ON dt.department_id = ds.department_id
#     #                 GROUP BY u.id
#     #             """
#     #             )
#     #             employees = cursor.fetchall()

#     #             # 3. present days
#     #             cursor.execute(
#     #                 """
#     #                 SELECT ud.employee_id, COUNT(bd.ci_biomatric_id) AS payable_days
#     #                 FROM ci_erp_users u
#     #                 LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
#     #                 INNER JOIN ci_biomatric_data bd ON ud.employee_id = bd.emp_id
#     #                 WHERE MONTH(login_date) = %s AND YEAR(login_date) = %s AND bd.attendance_status = 'Present' AND bd.status = 'P' AND bd.state_in_out = 'out'
#     #                 GROUP BY ud.employee_id
#     #             """,
#     #                 [month, year],
#     #             )
#     #             present_days_map = dict(cursor.fetchall())

#     #             # 4. half days
#     #             cursor.execute(
#     #                 """
#     #                 SELECT ud.employee_id, COUNT(bd.ci_biomatric_id) AS payable_days
#     #                 FROM ci_erp_users u
#     #                 LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
#     #                 INNER JOIN ci_biomatric_data bd ON ud.employee_id = bd.emp_id
#     #                 WHERE MONTH(login_date) = %s AND YEAR(login_date) = %s AND bd.attendance_status = 'Present' AND bd.status = 'H' AND bd.state_in_out = 'out'
#     #                 GROUP BY ud.employee_id
#     #             """,
#     #                 [month, year],
#     #             )
#     #             half_days_map = dict(cursor.fetchall())

#     #             # 5. approved Leaves for each employee
#     #             cursor.execute(
#     #                 """
#     #                 SELECT employee_id, 
#     #                        SUM(CASE 
#     #                            WHEN is_half_day = 1 THEN 0.5 
#     #                            ELSE no_of_days
#     #                        END) AS leave_days
#     #                 FROM ci_leave_applications
#     #                 WHERE status = 1 
#     #                 AND line_manager_status = 1
#     #                 AND ((MONTH(from_date) = %s AND YEAR(from_date) = %s) 
#     #                      OR (MONTH(to_date) = %s AND YEAR(to_date) = %s)
#     #                      OR (from_date <= %s AND to_date >= %s))
#     #                 GROUP BY employee_id;
#     #             """,
#     #                 [
#     #                     month,
#     #                     year,
#     #                     month,
#     #                     year,
#     #                     f"{year}-{month:02d}-01",
#     #                     f"{year}-{month:02d}-{days_in_month}",
#     #                 ],
#     #             )
#     #             leave_days_map = dict(cursor.fetchall())

#     #             # 6. state and employee hub-specific holidays for the month
#     #             # We need to get holidays for each state-employee hub combination
#     #             cursor.execute(
#     #                 """
#     #                 SELECT h.employee_hub, h.state, COUNT(*) as holiday_days
#     #                 FROM ci_holidays h
#     #                 INNER JOIN (
#     #                     SELECT DISTINCT u.employee_hub_id, u.state 
#     #                     FROM ci_erp_users u
#     #                     WHERE u.employee_hub_id IS NOT NULL AND u.state IS NOT NULL
#     #                 ) emp_states ON h.employee_hub = emp_states.employee_hub_id AND h.state = emp_states.state
#     #                 WHERE h.is_publish = 1
#     #                 AND ((MONTH(h.start_date) = %s AND YEAR(h.start_date) = %s) 
#     #                      OR (MONTH(h.end_date) = %s AND YEAR(h.end_date) = %s)
#     #                      OR (h.start_date <= %s AND h.end_date >= %s))
#     #                 GROUP BY h.employee_hub, h.state;
#     #             """,
#     #                 [
#     #                     month,
#     #                     year,
#     #                     month,
#     #                     year,
#     #                     f"{year}-{month:02d}-01",
#     #                     f"{year}-{month:02d}-{days_in_month}",
#     #                 ],
#     #             )
#     #             holidays_data = cursor.fetchall()

#     #             # Create a dictionary with (employee_hub, state) as key
#     #             holidays_map = {
#     #                 (employee_hub, state): holiday_days
#     #                 for employee_hub, state, holiday_days in holidays_data
#     #             }

#     #             sundays = self.get_sundays_in_month(year, month)
#     #             total_sundays = len(sundays)

#     #             results = []

#     #             for emp in employees:
#     #                 (
#     #                     user_id,
#     #                     emp_id,
#     #                     emp_name,
#     #                     dept,
#     #                     desg,
#     #                     gender,
#     #                     gross_salary,
#     #                     employee_hub_id,
#     #                     state,
#     #                 ) = emp
#     #                 gross_salary = self.safe_decimal(gross_salary or 0)

#     #                 # payable_days_from_bio = Decimal(payable_days_map.get(emp_id, 0))
#     #                 # half_payable_days_from_bio = Decimal(half_payable_days_map.get(emp_id, 0))

#     #                 # half_payable_days = half_payable_days_from_bio * Decimal("0.5")

#     #                 # # Add Sundays to payable days
#     #                 # payable_days = payable_days_from_bio + Decimal(total_sundays) + half_payable_days

#     #                 # Get individual components
#     #                 present_days = self.safe_decimal(present_days_map.get(emp_id, 0))
#     #                 half_days_count = self.safe_decimal(half_days_map.get(emp_id, 0))
#     #                 leave_days = self.safe_decimal(str(leave_days_map.get(emp_id, 0)))

#     #                 # Get state and company-specific holidays
#     #                 state_holidays = self.safe_decimal(
#     #                     holidays_map.get((employee_hub_id, state), 0)
#     #                 )

#     #                 # Calculate half days as 0.5
#     #                 half_days_value = half_days_count * self.safe_decimal("0.5")

#     #                 # Calculate total payable days
#     #                 payable_days = (
#     #                     present_days  # Full present days
#     #                     + half_days_value  # Half days (counted as 0.5 each)
#     #                     + leave_days  # Approved leave days (including half-day leaves)
#     #                     + state_holidays  # State and company-specific holidays
#     #                     + self.safe_decimal(total_sundays)  # Sundays
#     #                 )

#     #                 # gross_earning = (
#     #                 #     (gross_salary / Decimal(days_in_month)) * payable_days
#     #                 #     if days_in_month > 0
#     #                 #     else Decimal("0.00")
#     #                 # )

#     #                 gross_earning, total_monthly_earning = self.calculate_gross_earning_with_salary_changes(
#     #                     emp_id, year, month, payable_days, days_in_month
#     #                 )

#     #                 if emp_id == 'V1112':
#     #                     # # print("total monthly earnings: ", total_monthly_earning)


#     def safe_decimal(self, value, default="0.00"):
#         try:
#             if value is None or value == "" or value == "None":
#                 return Decimal(default)
#             return Decimal(str(value))
#         except (InvalidOperation, ValueError, TypeError):
#             return Decimal(default)
    
#     def get_all_salary_changes_batch(self, employee_ids, year, month):
#         """
#         Get all salary changes for multiple employees in a single query
#         """
#         if not employee_ids:
#             return {}
            
#         # Create placeholders for the IN clause
#         placeholders = ','.join(['%s'] * len(employee_ids))
        
#         with connection.cursor() as cursor:
#             cursor.execute(
#                 f"""
#                 SELECT employee_id, previous_salary, current_salary, updated_at
#                 FROM ci_update_salary 
#                 WHERE employee_id IN ({placeholders})
#                 AND MONTH(updated_at) = %s 
#                 AND YEAR(updated_at) = %s
#                 ORDER BY employee_id, updated_at ASC
#                 """,
#                 employee_ids + [month, year]
#             )
            
#             salary_changes_raw = cursor.fetchall()
            
#             # Group by employee_id
#             salary_changes_by_employee = {}
#             for employee_id, prev_salary, curr_salary, updated_at in salary_changes_raw:
#                 if employee_id not in salary_changes_by_employee:
#                     salary_changes_by_employee[employee_id] = []
#                 salary_changes_by_employee[employee_id].append((prev_salary, curr_salary, updated_at))
            
#             return salary_changes_by_employee

#     def calculate_gross_earning_with_salary_changes_batch(self, employees_data, salary_changes_by_employee, year, month, days_in_month):
#         """
#         Calculate gross earning for all employees considering mid-month salary changes
#         """
#         results = {}
        
#         try:
#             days_in_month_decimal = self.safe_decimal(days_in_month)
            
#             for emp_id, payable_days, current_salary in employees_data:
#                 try:
#                     # Ensure all values are properly converted to Decimal
#                     current_salary = self.safe_decimal(current_salary)
#                     payable_days = self.safe_decimal(payable_days)
#                     salary_changes = salary_changes_by_employee.get(emp_id, [])
                    
#                     if not salary_changes:
#                         # No salary changes in this month, use current salary for entire month
#                         if days_in_month_decimal > 0:
#                             gross = (current_salary / days_in_month_decimal) * payable_days
#                         else:
#                             gross = self.safe_decimal("0.00")
                        
#                         results[emp_id] = {
#                             'gross_earning': gross,
#                             'total_monthly_earning': current_salary
#                         }
#                         continue
                    
#                     # Calculate total earnings based on daily rates for different periods
#                     total_earnings = self.safe_decimal("0.00")
                    
#                     # Start with the first salary (before any changes)
#                     previous_day = 1
#                     current_month_salary = self.safe_decimal(salary_changes[0][0])  # previous_salary from first change
                    
#                     for change in salary_changes:
#                         try:
#                             previous_salary, new_salary, updated_at = change
                            
#                             # Ensure updated_at is not None and has day attribute
#                             if not updated_at or not hasattr(updated_at, 'day'):
#                                 continue
                                
#                             change_day = updated_at.day
                            
#                             # Calculate days with previous salary (from previous_day to change_day-1)
#                             days_with_current_salary = change_day - previous_day
#                             if days_with_current_salary > 0 and days_in_month_decimal > 0:
#                                 daily_rate = current_month_salary / days_in_month_decimal
#                                 total_earnings += daily_rate * self.safe_decimal(days_with_current_salary)
                            
#                             # Update for next iteration
#                             current_month_salary = self.safe_decimal(new_salary)
#                             previous_day = change_day
                            
#                         except (AttributeError, TypeError, ValueError) as e:
#                             # Skip this salary change if there's an error
#                             # # print(f"Error processing salary change for employee {emp_id}: {e}")
#                             continue
                    
#                     # Add remaining days of the month with the last salary
#                     remaining_days = days_in_month - previous_day + 1
#                     if remaining_days > 0 and days_in_month_decimal > 0:
#                         daily_rate = current_month_salary / days_in_month_decimal
#                         total_earnings += daily_rate * self.safe_decimal(remaining_days)
                    
#                     # Now calculate the proportional amount based on payable_days
#                     total_monthly_earnings = total_earnings
#                     if days_in_month_decimal > 0:
#                         calculated_gross = (total_monthly_earnings / days_in_month_decimal) * payable_days
#                     else:
#                         calculated_gross = self.safe_decimal("0.00")
                    
#                     results[emp_id] = {
#                         'gross_earning': calculated_gross,
#                         'total_monthly_earning': total_monthly_earnings
#                     }
                    
#                 except Exception as e:
#                     # If there's any error with this employee, set default values
#                     # # print(f"Error calculating salary for employee {emp_id}: {e}")
#                     results[emp_id] = {
#                         'gross_earning': self.safe_decimal("0.00"),
#                         'total_monthly_earning': self.safe_decimal(current_salary) if current_salary else self.safe_decimal("0.00")
#                     }
            
#         except Exception as e:
#             # print(f"Error in batch salary calculation: {e}")
            
#         return results

#     def get(self, request, month, year):
#         try:
#             days_in_month = calendar.monthrange(year, month)[1]

#             with connection.cursor() as cursor:

#                 # 1. Get Salary Structure (unchanged - this is small and fast)
#                 cursor.execute("SELECT particulars, value FROM ci_salary_structure")
#                 salary_structure_raw = cursor.fetchall()
#                 salary_structure = {k: self.safe_decimal(str(v)) for k, v in salary_structure_raw}

#                 # 2. Get Employee Details with all required data in one query
#                 cursor.execute(
#                     """
#                     SELECT u.id, ud.employee_id, CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                         dt.department_name, ds.designation_name,
#                         CASE 
#                             WHEN u.gender = 1 THEN 'Male'
#                             WHEN u.gender = 2 THEN 'Female'
#                             ELSE 'Other'
#                         END AS gender,
#                         ud.gross_salary,
#                         u.employee_hub_id,
#                         u.state
#                     FROM ci_erp_users u
#                     LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
#                     INNER JOIN ci_departments dt ON ud.department_id = dt.department_id
#                     INNER JOIN ci_designations ds ON dt.department_id = ds.department_id
#                     WHERE ud.employee_id IS NOT NULL
#                     GROUP BY u.id
#                 """
#                 )
#                 employees = cursor.fetchall()
                
#                 # Extract employee IDs for batch operations
#                 employee_ids = [emp[1] for emp in employees if emp[1]]  # emp[1] is employee_id
#                 employee_hub_ids = list(set([emp[7] for emp in employees if emp[7]]))
                
#                 if not employee_ids:
#                     return Response({"results": [], "message": "No employees found"})

#                 # 3. Get office shifts data for all employee hubs
#                 office_shifts_map = {}
#                 try:
#                     if employee_hub_ids:
#                         placeholders_hub = ','.join(['%s'] * len(employee_hub_ids))
#                         cursor.execute(
#                             f"""
#                             SELECT employee_hub_id, user_id, shift_name,
#                                 monday_in_time, monday_out_time,
#                                 tuesday_in_time, tuesday_out_time,
#                                 wednesday_in_time, wednesday_out_time,
#                                 thursday_in_time, thursday_out_time,
#                                 friday_in_time, friday_out_time,
#                                 saturday_in_time, saturday_out_time,
#                                 sunday_in_time, sunday_out_time
#                             FROM ci_office_shifts
#                             WHERE employee_hub_id IN ({placeholders_hub})
#                             """,
#                             employee_hub_ids
#                         )
                        
#                         shifts_data = cursor.fetchall()
#                         for shift in shifts_data:
#                             hub_id = shift[0]
#                             user_id = shift[1]
#                             key = (hub_id, user_id) if user_id else hub_id
#                             office_shifts_map[key] = {
#                                 'shift_name': shift[2],
#                                 'monday': {'in': shift[3], 'out': shift[4]},
#                                 'tuesday': {'in': shift[5], 'out': shift[6]},
#                                 'wednesday': {'in': shift[7], 'out': shift[8]},
#                                 'thursday': {'in': shift[9], 'out': shift[10]},
#                                 'friday': {'in': shift[11], 'out': shift[12]},
#                                 'saturday': {'in': shift[13], 'out': shift[14]},
#                                 'sunday': {'in': shift[15], 'out': shift[16]}
#                             }
#                 except Exception as e:
#                     # # print(f"Error fetching office shifts data: {e}")
#                     office_shifts_map = {}

#                 # 4. Get ALL attendance data in one optimized query
#                 try:
#                     placeholders_attendance = ','.join(['%s'] * len(employee_ids))
#                     cursor.execute(
#                         f"""
#                         SELECT 
#                             ud.employee_id,
#                             SUM(CASE WHEN bd.status = 'P' THEN 1 ELSE 0 END) AS present_days,
#                             SUM(CASE WHEN bd.status = 'H' THEN 1 ELSE 0 END) AS half_days
#                         FROM ci_erp_users u
#                         LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
#                         INNER JOIN ci_biomatric_data bd ON ud.employee_id = bd.emp_id
#                         WHERE MONTH(bd.login_date) = %s 
#                         AND YEAR(bd.login_date) = %s 
#                         AND bd.attendance_status = 'Present' 
#                         AND bd.state_in_out = 'out'
#                         AND ud.employee_id IN ({placeholders_attendance})
#                         GROUP BY ud.employee_id
#                         """,
#                         [month, year] + employee_ids
#                     )
                    
#                     attendance_data = cursor.fetchall()
#                     present_days_map = {}
#                     half_days_map = {}
                    
#                     for emp_id, present, half in attendance_data:
#                         present_days_map[emp_id] = present or 0
#                         half_days_map[emp_id] = half or 0
                        
#                 except Exception as e:
#                     # # print(f"Error fetching attendance data: {e}")
#                     present_days_map = {}
#                     half_days_map = {}

#                 # 5. Get approved leaves for all employees in one query
#                 try:
#                     placeholders_leave = ','.join(['%s'] * len(employee_ids))
#                     cursor.execute(
#                         f"""
#                         SELECT employee_id, 
#                                SUM(CASE 
#                                    WHEN is_half_day = 1 THEN 0.5 
#                                    ELSE no_of_days
#                                END) AS leave_days
#                         FROM ci_leave_applications
#                         WHERE status = 1 
#                         AND line_manager_status = 1
#                         AND employee_id IN ({placeholders_leave})
#                         AND ((MONTH(from_date) = %s AND YEAR(from_date) = %s) 
#                              OR (MONTH(to_date) = %s AND YEAR(to_date) = %s)
#                              OR (from_date <= %s AND to_date >= %s))
#                         GROUP BY employee_id
#                         """,
#                         employee_ids + [
#                             month, year, month, year,
#                             f"{year}-{month:02d}-01",
#                             f"{year}-{month:02d}-{days_in_month}",
#                         ],
#                     )
#                     leave_days_map = dict(cursor.fetchall())
#                 except Exception as e:
#                     # # print(f"Error fetching leave data: {e}")
#                     leave_days_map = {}

#                 # 6. Get holidays (unchanged - this is already efficient)
#                 try:
#                     cursor.execute(
#                         """
#                         SELECT h.employee_hub, h.state, COUNT(*) as holiday_days
#                         FROM ci_holidays h
#                         INNER JOIN (
#                             SELECT DISTINCT u.employee_hub_id, u.state 
#                             FROM ci_erp_users u
#                             WHERE u.employee_hub_id IS NOT NULL AND u.state IS NOT NULL
#                         ) emp_states ON h.employee_hub = emp_states.employee_hub_id AND h.state = emp_states.state
#                         WHERE h.is_publish = 1
#                         AND ((MONTH(h.start_date) = %s AND YEAR(h.start_date) = %s) 
#                              OR (MONTH(h.end_date) = %s AND YEAR(h.end_date) = %s)
#                              OR (h.start_date <= %s AND h.end_date >= %s))
#                         GROUP BY h.employee_hub, h.state
#                         """,
#                         [
#                             month, year, month, year,
#                             f"{year}-{month:02d}-01",
#                             f"{year}-{month:02d}-{days_in_month}",
#                         ],
#                     )
#                     holidays_data = cursor.fetchall()
#                     holidays_map = {
#                         (employee_hub, state): holiday_days
#                         for employee_hub, state, holiday_days in holidays_data
#                     }
#                 except Exception as e:
#                     # # print(f"Error fetching holidays data: {e}")
#                     holidays_map = {}

#                 # 7. Get all salary changes in batch
#                 try:
#                     salary_changes_by_employee = self.get_all_salary_changes_batch(employee_ids, year, month)
#                 except Exception as e:
#                     # # print(f"Error fetching salary changes: {e}")
#                     salary_changes_by_employee = {}

#                 # 8. Calculate holiday days from office shifts
#                 try:
#                     holiday_days_data = self.calculate_holiday_days_from_shifts(year, month, office_shifts_map, employees)
#                 except Exception as e:
#                     # # print(f"Error calculating holiday days from shifts: {e}")
#                     # Fallback to original calculation
#                     sundays = self.get_sundays_in_month(year, month)
#                     holiday_days_data = {
#                         'total_sundays': len(sundays),
#                         'holiday_days_by_employee': {}
#                     }

#                 # try:
#                 #     sundays = self.get_sundays_in_month(year, month)
#                 #     total_sundays = len(sundays) 
#                 # except Exception as e:
#                 #     # # print(f"Error calculating sundays: {e}")
#                 #     total_sundays = 0

#                 # Prepare data for batch salary calculation
#                 employees_salary_data = []
#                 payable_days_by_employee = {}
                
#                 for emp in employees:
#                     try:
#                         (
#                             user_id, emp_id, emp_name, dept, desg, gender,
#                             gross_salary, employee_hub_id, state,
#                         ) = emp
                        
#                         # Calculate payable days for this employee with safe conversions
#                         present_days = self.safe_decimal(present_days_map.get(emp_id, 0))
#                         half_days_count = self.safe_decimal(half_days_map.get(emp_id, 0))
#                         leave_days = self.safe_decimal(str(leave_days_map.get(emp_id, 0)))
#                         state_holidays = self.safe_decimal(holidays_map.get((employee_hub_id, state), 0))
#                         half_days_value = half_days_count * self.safe_decimal("0.5")
                        
#                         # payable_days = (
#                         #     present_days + half_days_value + leave_days + 
#                         #     state_holidays + self.safe_decimal(total_sundays)
#                         # )

#                         # Get employee-specific holiday days from shifts or fall back to general calculation
#                         employee_holiday_data = holiday_days_data['holiday_days_by_employee'].get(
#                             emp_id, 
#                             {'shift_holidays': holiday_days_data.get('total_sundays', 0)}
#                         )
#                         shift_holidays = self.safe_decimal(employee_holiday_data.get('shift_holidays', 0))

#                         payable_days = (
#                             present_days + half_days_value + leave_days + 
#                             state_holidays + shift_holidays
#                         )
                        
#                         payable_days_by_employee[emp_id] = payable_days
#                         employees_salary_data.append((emp_id, payable_days, gross_salary))
                        
#                     except Exception as e:
#                         # # print(f"Error processing employee {emp_id if 'emp_id' in locals() else 'unknown'}: {e}")
#                         # Set default values for this employee
#                         if 'emp_id' in locals():
#                             payable_days_by_employee[emp_id] = self.safe_decimal("0.00")
#                             employees_salary_data.append((emp_id, self.safe_decimal("0.00"), gross_salary))

#                 # 9. Calculate gross earnings for all employees in batch
#                 try:
#                     salary_calculations = self.calculate_gross_earning_with_salary_changes_batch(
#                         employees_salary_data, salary_changes_by_employee, year, month, days_in_month
#                     )
#                 except Exception as e:
#                     # # print(f"Error in salary calculations: {e}")
#                     salary_calculations = {}

#                 # 8. Build final results
#                 results = []
#                 for emp in employees:
#                     (
#                         user_id, emp_id, emp_name, dept, desg, gender,
#                         gross_salary, employee_hub_id, state,
#                     ) = emp

#                     if gross_salary is None:
#                         gross_salary = 0
                    
#                     payable_days = payable_days_by_employee.get(emp_id, self.safe_decimal("0.00"))
#                     salary_calc = salary_calculations.get(emp_id, {
#                         'gross_earning': self.safe_decimal("0.00"),
#                         'total_monthly_earning': self.safe_decimal(gross_salary or 0)
#                     })
                    
#                     gross_earning = salary_calc.get('gross_earning', self.safe_decimal("0.00"))
#                     total_monthly_earning = salary_calc.get('total_monthly_earning', self.safe_decimal(gross_salary or 0))
                    
#                     # if emp_id == 'V1112':
#                     #     # # print("total monthly earnings: ", total_monthly_earning)

#                     esic_applicable = gross_salary <= self.safe_decimal("21000")  # Monthly limit

#                     # Get structure percentages
#                     get = lambda key: salary_structure.get(key, self.safe_decimal("0.00"))

#                     # Earnings
#                     basic_da = gross_earning * get("basic_plus_da")
#                     hra = gross_earning * get("hra")
#                     medical = gross_earning * (
#                         get("medical_allowance_with_esic")
#                         if esic_applicable
#                         else get("medical_allowance_without_esic")
#                     )
#                     conveyance = gross_earning * (
#                         get("conveyance_allowance_with_esic")
#                         if esic_applicable
#                         else get("conveyance_allowance_without_esic")
#                     )

#                     total_earnings = basic_da + hra + medical + conveyance

#                     # Deductions
#                     pf = min(
#                         (gross_earning - hra) * get("pf_employee_contribution"),
#                         self.safe_decimal("1800"),
#                     )

#                     if pf > 1800:
#                         pf = 1800

#                     esic_emp = gross_earning * get("esic_employee_contribution")  # Static/user-filled
#                     pt = self.safe_decimal("0")
#                     if gender == "Male":
#                         pt = self.safe_decimal("300") if month == 2 else self.safe_decimal("200")
#                     elif gender == "Female":
#                         if month == 2:
#                             pt = (
#                                 self.safe_decimal("300")
#                                 if gross_earning > self.safe_decimal("25000")
#                                 else self.safe_decimal("0")
#                             )
#                         else:
#                             pt = (
#                                 self.safe_decimal("200")
#                                 if gross_earning > self.safe_decimal("25000")
#                                 else self.safe_decimal("0")
#                             )

#                     # Benefits
#                     pf_employer = min(
#                         (gross_earning - hra) * get("pf_employer_contribution"),
#                         self.safe_decimal("1800"),
#                     )
#                     esic_employer = (
#                         gross_earning * get("esic_employer_contribution")
#                         if esic_applicable
#                         else self.safe_decimal("0.00")
#                     )

#                     total_deduction = pf + esic_emp + pt
#                     total_benefit = pf_employer + esic_employer
#                     net_pay = total_earnings - total_deduction
#                     ctc = total_earnings + total_benefit

#                     results.append(
#                         {
#                             "Sr. No.": len(results) + 1,
#                             "Employee ID": emp_id,
#                             "Employee Name": emp_name,
#                             "Department": dept,
#                             "Designation": desg,
#                             "M/F": gender,
#                             "Gross Salary": float(round(gross_salary, 2)),
#                             "Days": float(payable_days),
#                             "ESIC Applicable": "Yes" if esic_applicable else "No",
#                             "Gross Earning": float(round(gross_earning, 2)),
#                             "Basic": float(round(basic_da, 2)),
#                             "HRA": float(round(hra, 2)),
#                             "Conveyance": float(round(conveyance, 2)),
#                             "Medical": float(round(medical, 2)),
#                             "Arrears": 0.00,
#                             "Total Earnings": float(round(total_earnings, 2)),
#                             "PF": float(round(pf, 2)),
#                             "ESICS": float(round(esic_emp, 2)),
#                             "PT": float(round(pt, 2)),
#                             "MLWF": 0.00,
#                             "Advance": 0.00,
#                             "TDS": 0.00,
#                             "Other Deduction": 0.00,
#                             "Total Deduction": float(round(total_deduction, 2)),
#                             "Net Pay": float(round(net_pay, 2)),
#                             "CTC": float(round(ctc, 2)),
#                         }
#                     )

#                 return Response(results, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
        
#     def calculate_holiday_days_from_shifts(self, year, month, office_shifts_map, employees):
#         """
#         Calculate holiday days from office shifts where in_time or out_time is marked as 'Holiday'.
#         These are paid holidays and should be included in payable days.
#         """
#         import calendar
#         from datetime import datetime
        
#         # Get all dates in the month
#         days_in_month = calendar.monthrange(year, month)[1]
        
#         # Day names mapping
#         day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
#         holiday_days_by_employee = {}
#         total_sundays = 0  # Fallback calculation
        
#         # Calculate total Sundays for fallback
#         for day in range(1, days_in_month + 1):
#             current_date = datetime(year, month, day)
#             if current_date.weekday() == 6:  # Sunday
#                 total_sundays += 1
        
#         # Process each employee
#         for emp in employees:
#             user_id, emp_id, emp_name, dept, desg, gender, gross_salary, employee_hub_id, state = emp
            
#             # Find applicable shift for this employee
#             shift_data = None
            
#             # Try user-specific shift first
#             if (employee_hub_id, user_id) in office_shifts_map:
#                 shift_data = office_shifts_map[(employee_hub_id, user_id)]
#             # Fall back to hub-level shift
#             elif employee_hub_id in office_shifts_map:
#                 shift_data = office_shifts_map[employee_hub_id]
            
#             if not shift_data:
#                 # No shift data, use default Sunday calculation
#                 holiday_days_by_employee[emp_id] = {'shift_holidays': total_sundays}
#                 continue
            
#             # Count holiday days based on shift schedule
#             shift_holiday_days = 0
            
#             for day in range(1, days_in_month + 1):
#                 current_date = datetime(year, month, day)
#                 day_name = day_names[current_date.weekday()]
                
#                 # Check if this day is marked as 'Holiday' in shift schedule
#                 day_shift = shift_data.get(day_name, {})
#                 in_time = day_shift.get('in', '').strip() if day_shift.get('in') else ''
#                 out_time = day_shift.get('out', '').strip() if day_shift.get('out') else ''
                
#                 # If either in_time or out_time is marked as 'Holiday', count it as a paid holiday
#                 if in_time.lower() == 'holiday' or out_time.lower() == 'holiday':
#                     shift_holiday_days += 1
            
#             holiday_days_by_employee[emp_id] = {'shift_holidays': shift_holiday_days}
        
#         return {
#             'holiday_days_by_employee': holiday_days_by_employee,
#             'total_sundays': total_sundays  # For fallback
#         }


class PayrollReport(APIView):

    @staticmethod
    def get_sundays_in_month(year, month):
        sundays = []
        total_days = calendar.monthrange(year, month)[1]
        for day in range(1, total_days + 1):
            current_date = date(year, month, day)
            if current_date.weekday() == 6:  # Sunday
                sundays.append(current_date)
        return sundays

    def safe_decimal(self, value, default="0.00"):
        try:
            if value is None or value == "" or value == "None":
                return Decimal(default)
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal(default)
    
    # def calculate_gross_earning_with_salary_changes(self, employee_id, year, month, payable_days, days_in_month):
    #     """
    #     Calculate gross earning considering mid-month salary changes
    #     """
    #     with connection.cursor() as cursor:
    #         # Get current salary
    #         cursor.execute(
    #             """SELECT gross_salary FROM ci_erp_users_details WHERE employee_id = %s""",
    #             [employee_id]
    #         )
    #         current_salary_result = cursor.fetchone()
    #         if not current_salary_result:
    #             return self.safe_decimal("0.00"), self.safe_decimal("0.00")
            
    #         # current_salary = Decimal(str(current_salary_result[0]))
    #         current_salary = self.safe_decimal(current_salary_result[0])
            
    #         # Get all salary changes for this employee in the given month/year
    #         cursor.execute(
    #             """
    #             SELECT previous_salary, current_salary, updated_at
    #             FROM ci_update_salary 
    #             WHERE employee_id = %s 
    #             AND MONTH(updated_at) = %s 
    #             AND YEAR(updated_at) = %s
    #             ORDER BY updated_at ASC
    #             """,
    #             [employee_id, month, year]
    #         )
    #         salary_changes = cursor.fetchall()
            
    #         if not salary_changes:
    #             # No salary changes in this month, use current salary for entire month
    #             gross = (current_salary / self.safe_decimal(days_in_month)) * payable_days
    #             return gross, current_salary
            
    #         # Calculate total earnings based on daily rates for different periods
    #         total_earnings = self.safe_decimal("0.00")
            
    #         # Start with the first salary (before any changes)
    #         previous_day = 1
    #         # current_month_salary = Decimal(str(salary_changes[0][0]))  # previous_salary from first change
    #         current_month_salary = self.safe_decimal(salary_changes[0][0])
            
    #         for change in salary_changes:
    #             previous_salary, new_salary, updated_at = change
    #             change_day = updated_at.day
                
    #             # Calculate days with previous salary (from previous_day to change_day-1)
    #             days_with_current_salary = change_day - previous_day
    #             if days_with_current_salary > 0:
    #                 daily_rate = current_month_salary / self.safe_decimal(days_in_month)
    #                 total_earnings += daily_rate * days_with_current_salary
                
    #             # Update for next iteration
    #             # current_month_salary = Decimal(str(new_salary))
    #             current_month_salary = self.safe_decimal(new_salary)
    #             previous_day = change_day
            
    #         # Add remaining days of the month with the last salary
    #         remaining_days = days_in_month - previous_day + 1
    #         if remaining_days > 0:
    #             daily_rate = current_month_salary / self.safe_decimal(days_in_month)
    #             total_earnings += daily_rate * remaining_days
            
    #         # Now calculate the proportional amount based on payable_days
    #         total_monthly_earnings = total_earnings
    #         # return (total_monthly_earnings / self.safe_decimal(days_in_month)) * payable_days
    #         calculated_gross = (total_monthly_earnings / self.safe_decimal(days_in_month)) * payable_days
            
    #     return calculated_gross, total_monthly_earnings

    # def get(self, request, month, year):
    #     try:
    #         days_in_month = calendar.monthrange(year, month)[1]

    #         with connection.cursor() as cursor:

    #             # 1. Get Salary Structure
    #             cursor.execute("SELECT particulars, value FROM ci_salary_structure")
    #             salary_structure_raw = cursor.fetchall()
    #             salary_structure = {k: self.safe_decimal(str(v)) for k, v in salary_structure_raw}

    #             # 2. Get Employee Details
    #             cursor.execute(
    #                 """
    #                 SELECT u.id, ud.employee_id, CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    #                     dt.department_name, ds.designation_name,
    #                     CASE 
    #                         WHEN u.gender = 1 THEN 'Male'
    #                         WHEN u.gender = 2 THEN 'Female'
    #                         ELSE 'Other'
    #                     END AS gender,
    #                     ud.gross_salary,
    #                     u.employee_hub_id,
    #                     u.state
    #                 FROM ci_erp_users u
    #                 LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
    #                 INNER JOIN ci_departments dt ON ud.department_id = dt.department_id
    #                 INNER JOIN ci_designations ds ON dt.department_id = ds.department_id
    #                 GROUP BY u.id
    #             """
    #             )
    #             employees = cursor.fetchall()

    #             # 3. present days
    #             cursor.execute(
    #                 """
    #                 SELECT ud.employee_id, COUNT(bd.ci_biomatric_id) AS payable_days
    #                 FROM ci_erp_users u
    #                 LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
    #                 INNER JOIN ci_biomatric_data bd ON ud.employee_id = bd.emp_id
    #                 WHERE MONTH(login_date) = %s AND YEAR(login_date) = %s AND bd.attendance_status = 'Present' AND bd.status = 'P' AND bd.state_in_out = 'out'
    #                 GROUP BY ud.employee_id
    #             """,
    #                 [month, year],
    #             )
    #             present_days_map = dict(cursor.fetchall())

    #             # 4. half days
    #             cursor.execute(
    #                 """
    #                 SELECT ud.employee_id, COUNT(bd.ci_biomatric_id) AS payable_days
    #                 FROM ci_erp_users u
    #                 LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
    #                 INNER JOIN ci_biomatric_data bd ON ud.employee_id = bd.emp_id
    #                 WHERE MONTH(login_date) = %s AND YEAR(login_date) = %s AND bd.attendance_status = 'Present' AND bd.status = 'H' AND bd.state_in_out = 'out'
    #                 GROUP BY ud.employee_id
    #             """,
    #                 [month, year],
    #             )
    #             half_days_map = dict(cursor.fetchall())

    #             # 5. approved Leaves for each employee
    #             cursor.execute(
    #                 """
    #                 SELECT employee_id, 
    #                        SUM(CASE 
    #                            WHEN is_half_day = 1 THEN 0.5 
    #                            ELSE no_of_days
    #                        END) AS leave_days
    #                 FROM ci_leave_applications
    #                 WHERE status = 1 
    #                 AND line_manager_status = 1
    #                 AND ((MONTH(from_date) = %s AND YEAR(from_date) = %s) 
    #                      OR (MONTH(to_date) = %s AND YEAR(to_date) = %s)
    #                      OR (from_date <= %s AND to_date >= %s))
    #                 GROUP BY employee_id;
    #             """,
    #                 [
    #                     month,
    #                     year,
    #                     month,
    #                     year,
    #                     f"{year}-{month:02d}-01",
    #                     f"{year}-{month:02d}-{days_in_month}",
    #                 ],
    #             )
    #             leave_days_map = dict(cursor.fetchall())

    #             # 6. state and employee hub-specific holidays for the month
    #             # We need to get holidays for each state-employee hub combination
    #             cursor.execute(
    #                 """
    #                 SELECT h.employee_hub, h.state, COUNT(*) as holiday_days
    #                 FROM ci_holidays h
    #                 INNER JOIN (
    #                     SELECT DISTINCT u.employee_hub_id, u.state 
    #                     FROM ci_erp_users u
    #                     WHERE u.employee_hub_id IS NOT NULL AND u.state IS NOT NULL
    #                 ) emp_states ON h.employee_hub = emp_states.employee_hub_id AND h.state = emp_states.state
    #                 WHERE h.is_publish = 1
    #                 AND ((MONTH(h.start_date) = %s AND YEAR(h.start_date) = %s) 
    #                      OR (MONTH(h.end_date) = %s AND YEAR(h.end_date) = %s)
    #                      OR (h.start_date <= %s AND h.end_date >= %s))
    #                 GROUP BY h.employee_hub, h.state;
    #             """,
    #                 [
    #                     month,
    #                     year,
    #                     month,
    #                     year,
    #                     f"{year}-{month:02d}-01",
    #                     f"{year}-{month:02d}-{days_in_month}",
    #                 ],
    #             )
    #             holidays_data = cursor.fetchall()

    #             # Create a dictionary with (employee_hub, state) as key
    #             holidays_map = {
    #                 (employee_hub, state): holiday_days
    #                 for employee_hub, state, holiday_days in holidays_data
    #             }

    #             sundays = self.get_sundays_in_month(year, month)
    #             total_sundays = len(sundays)

    #             results = []

    #             for emp in employees:
    #                 (
    #                     user_id,
    #                     emp_id,
    #                     emp_name,
    #                     dept,
    #                     desg,
    #                     gender,
    #                     gross_salary,
    #                     employee_hub_id,
    #                     state,
    #                 ) = emp
    #                 gross_salary = self.safe_decimal(gross_salary or 0)

    #                 # payable_days_from_bio = Decimal(payable_days_map.get(emp_id, 0))
    #                 # half_payable_days_from_bio = Decimal(half_payable_days_map.get(emp_id, 0))

    #                 # half_payable_days = half_payable_days_from_bio * Decimal("0.5")

    #                 # # Add Sundays to payable days
    #                 # payable_days = payable_days_from_bio + Decimal(total_sundays) + half_payable_days

    #                 # Get individual components
    #                 present_days = self.safe_decimal(present_days_map.get(emp_id, 0))
    #                 half_days_count = self.safe_decimal(half_days_map.get(emp_id, 0))
    #                 leave_days = self.safe_decimal(str(leave_days_map.get(emp_id, 0)))

    #                 # Get state and company-specific holidays
    #                 state_holidays = self.safe_decimal(
    #                     holidays_map.get((employee_hub_id, state), 0)
    #                 )

    #                 # Calculate half days as 0.5
    #                 half_days_value = half_days_count * self.safe_decimal("0.5")

    #                 # Calculate total payable days
    #                 payable_days = (
    #                     present_days  # Full present days
    #                     + half_days_value  # Half days (counted as 0.5 each)
    #                     + leave_days  # Approved leave days (including half-day leaves)
    #                     + state_holidays  # State and company-specific holidays
    #                     + self.safe_decimal(total_sundays)  # Sundays
    #                 )

    #                 # gross_earning = (
    #                 #     (gross_salary / Decimal(days_in_month)) * payable_days
    #                 #     if days_in_month > 0
    #                 #     else Decimal("0.00")
    #                 # )

    #                 gross_earning, total_monthly_earning = self.calculate_gross_earning_with_salary_changes(
    #                     emp_id, year, month, payable_days, days_in_month
    #                 )

    #                 if emp_id == 'V1112':
    #                     # # print("total monthly earnings: ", total_monthly_earning)


    def safe_decimal(self, value, default="0.00"):
        try:
            if value is None or value == "" or value == "None":
                return Decimal(default)
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal(default)
    
    def get_all_salary_changes_batch(self, employee_ids, year, month):
        """
        Get all salary changes for multiple employees in a single query
        """
        if not employee_ids:
            return {}
            
        # Create placeholders for the IN clause
        placeholders = ','.join(['%s'] * len(employee_ids))
        
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT employee_id, previous_salary, current_salary, updated_at
                FROM ci_update_salary 
                WHERE employee_id IN ({placeholders})
                AND MONTH(updated_at) = %s 
                AND YEAR(updated_at) = %s
                ORDER BY employee_id, updated_at ASC
                """,
                employee_ids + [month, year]
            )
            
            salary_changes_raw = cursor.fetchall()
            
            # Group by employee_id
            salary_changes_by_employee = {}
            for employee_id, prev_salary, curr_salary, updated_at in salary_changes_raw:
                if employee_id not in salary_changes_by_employee:
                    salary_changes_by_employee[employee_id] = []
                salary_changes_by_employee[employee_id].append((prev_salary, curr_salary, updated_at))
            
            return salary_changes_by_employee

    def calculate_gross_earning_with_salary_changes_batch(self, employees_data, salary_changes_by_employee, year, month, days_in_month):
        """
        Calculate gross earning for all employees considering mid-month salary changes
        """
        results = {}
        
        try:
            days_in_month_decimal = self.safe_decimal(days_in_month)
            
            for emp_id, payable_days, current_salary in employees_data:
                try:
                    # Ensure all values are properly converted to Decimal
                    current_salary = self.safe_decimal(current_salary)
                    payable_days = self.safe_decimal(payable_days)
                    salary_changes = salary_changes_by_employee.get(emp_id, [])
                    
                    if not salary_changes:
                        # No salary changes in this month, use current salary for entire month
                        if days_in_month_decimal > 0:
                            gross = (current_salary / days_in_month_decimal) * payable_days
                        else:
                            gross = self.safe_decimal("0.00")
                        
                        results[emp_id] = {
                            'gross_earning': gross,
                            'total_monthly_earning': current_salary
                        }
                        continue
                    
                    # Calculate total earnings based on daily rates for different periods
                    total_earnings = self.safe_decimal("0.00")
                    
                    # Start with the first salary (before any changes)
                    previous_day = 1
                    current_month_salary = self.safe_decimal(salary_changes[0][0])  # previous_salary from first change
                    
                    for change in salary_changes:
                        try:
                            previous_salary, new_salary, updated_at = change
                            
                            # Ensure updated_at is not None and has day attribute
                            if not updated_at or not hasattr(updated_at, 'day'):
                                continue
                                
                            change_day = updated_at.day
                            
                            # Calculate days with previous salary (from previous_day to change_day-1)
                            days_with_current_salary = change_day - previous_day
                            if days_with_current_salary > 0 and days_in_month_decimal > 0:
                                daily_rate = current_month_salary / days_in_month_decimal
                                total_earnings += daily_rate * self.safe_decimal(days_with_current_salary)
                            
                            # Update for next iteration
                            current_month_salary = self.safe_decimal(new_salary)
                            previous_day = change_day
                            
                        except (AttributeError, TypeError, ValueError) as e:
                            # Skip this salary change if there's an error
                            # # print(f"Error processing salary change for employee {emp_id}: {e}")
                            continue
                    
                    # Add remaining days of the month with the last salary
                    remaining_days = days_in_month - previous_day + 1
                    if remaining_days > 0 and days_in_month_decimal > 0:
                        daily_rate = current_month_salary / days_in_month_decimal
                        total_earnings += daily_rate * self.safe_decimal(remaining_days)
                    
                    # Now calculate the proportional amount based on payable_days
                    total_monthly_earnings = total_earnings
                    if days_in_month_decimal > 0:
                        calculated_gross = (total_monthly_earnings / days_in_month_decimal) * payable_days
                    else:
                        calculated_gross = self.safe_decimal("0.00")
                    
                    results[emp_id] = {
                        'gross_earning': calculated_gross,
                        'total_monthly_earning': total_monthly_earnings
                    }
                    
                except Exception as e:
                    # If there's any error with this employee, set default values
                    # # print(f"Error calculating salary for employee {emp_id}: {e}")
                    results[emp_id] = {
                        'gross_earning': self.safe_decimal("0.00"),
                        'total_monthly_earning': self.safe_decimal(current_salary) if current_salary else self.safe_decimal("0.00")
                    }
            
        except Exception as e:
            print(f"Error in batch salary calculation: {e}")
            
        return results

    def get(self, request, month, year):
        try:
            days_in_month = calendar.monthrange(year, month)[1]

            with connection.cursor() as cursor:

                # 1. Get Salary Structure (unchanged - this is small and fast)
                cursor.execute("SELECT particulars, value FROM ci_salary_structure")
                salary_structure_raw = cursor.fetchall()
                salary_structure = {k: self.safe_decimal(str(v)) for k, v in salary_structure_raw}

                # 2. Get Employee Details with all required data in one query
                cursor.execute(
                    """
                    SELECT u.id, ud.employee_id, CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        dt.department_name, ds.designation_name,
                        CASE 
                            WHEN u.gender = 1 THEN 'Male'
                            WHEN u.gender = 2 THEN 'Female'
                            ELSE 'Other'
                        END AS gender,
                        ud.gross_salary,
                        u.employee_hub_id,
                        u.state,
                        ud.office_shift_id
                    FROM ci_erp_users u
                    LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    INNER JOIN ci_departments dt ON ud.department_id = dt.department_id
                    INNER JOIN ci_designations ds ON dt.department_id = ds.department_id
                    WHERE ud.employee_id IS NOT NULL
                    GROUP BY u.id
                """
                )
                employees = cursor.fetchall()
                
                # Extract employee IDs for batch operations
                employee_ids = [emp[1] for emp in employees if emp[1]]  # emp[1] is employee_id
                employee_hub_ids = list(set([emp[7] for emp in employees if emp[7]]))
                employee_states = list(set([emp[8] for emp in employees if emp[8]]))
                office_shift_ids = list(set([emp[9] for emp in employees if emp[9]]))
                
                if not employee_ids:
                    return Response({"results": [], "message": "No employees found"})

                # 3. Get office shifts data for all employee hubs
                office_shifts_map = {}

                # try:
                    # if employee_hub_ids or office_shift_ids:

                #         placeholders_hub = ','.join(['%s'] * len(employee_hub_ids))
                #         cursor.execute(
                #             f"""
                #             SELECT employee_hub_id, shift_name,
                #                 monday_in_time, monday_out_time,
                #                 tuesday_in_time, tuesday_out_time,
                #                 wednesday_in_time, wednesday_out_time,
                #                 thursday_in_time, thursday_out_time,
                #                 friday_in_time, friday_out_time,
                #                 saturday_in_time, saturday_out_time,
                #                 sunday_in_time, sunday_out_time
                #             FROM ci_office_shifts os LEFT JOIN ci_erp_users_details ud ON os.office_shift_id = ud.office_shift_id
                #             WHERE os.employee_hub_id IN ({placeholders_hub}) OR ud.office_shift_id
                #             """,
                #             employee_hub_ids
                #         )
                        
                #         shifts_data = cursor.fetchall()
                #         for shift in shifts_data:
                #             hub_id = shift[0]
                #             user_id = shift[1]
                #             key = (hub_id, user_id) if user_id else hub_id
                #             office_shifts_map[key] = {
                #                 'shift_name': shift[2],
                #                 'monday': {'in': shift[3], 'out': shift[4]},
                #                 'tuesday': {'in': shift[5], 'out': shift[6]},
                #                 'wednesday': {'in': shift[7], 'out': shift[8]},
                #                 'thursday': {'in': shift[9], 'out': shift[10]},
                #                 'friday': {'in': shift[11], 'out': shift[12]},
                #                 'saturday': {'in': shift[13], 'out': shift[14]},
                #                 'sunday': {'in': shift[15], 'out': shift[16]}
                #             }
                # except Exception as e:
                #     # # print(f"Error fetching office shifts data: {e}")
                #     office_shifts_map = {}

                try:
                    
                    if employee_hub_ids or office_shift_ids:

                        # Prepare parameters for the query
                        query_params = []
                        conditions = []
                        
                        # Add employee_hub_id condition if we have hub IDs
                        if employee_hub_ids:
                            hub_placeholders = ','.join(['%s'] * len(employee_hub_ids))
                            conditions.append(f"os.employee_hub_id IN ({hub_placeholders})")
                            query_params.extend(employee_hub_ids)
                        
                        # Add office_shift_id condition if we have shift IDs
                        if office_shift_ids:
                            shift_placeholders = ','.join(['%s'] * len(office_shift_ids))
                            conditions.append(f"os.office_shift_id IN ({shift_placeholders})")
                            query_params.extend(office_shift_ids)
                        
                        # Combine conditions with OR
                        where_clause = ' OR '.join(conditions)
                        
                        cursor.execute(
                            f"""
                            SELECT os.employee_hub_id, os.office_shift_id, ud.employee_id, os.shift_name,
                                os.monday_in_time, os.monday_out_time,
                                os.tuesday_in_time, os.tuesday_out_time,
                                os.wednesday_in_time, os.wednesday_out_time,
                                os.thursday_in_time, os.thursday_out_time,
                                os.friday_in_time, os.friday_out_time,
                                os.saturday_in_time, os.saturday_out_time,
                                os.sunday_in_time, os.sunday_out_time
                            FROM ci_office_shifts os 
                            LEFT JOIN ci_erp_users_details ud ON os.office_shift_id = ud.office_shift_id
                            WHERE {where_clause}
                            """,
                            query_params
                        )
                        
                        shifts_data = cursor.fetchall()
                        for shift in shifts_data:
                            employee_hub_id = shift[0]
                            office_shift_id = shift[1]
                            employee_id = shift[2]  # This will be None for hub-level shifts
                            shift_name = shift[3]
                            
                            shift_schedule = {
                                'shift_name': shift_name,
                                'monday': {'in': shift[4], 'out': shift[5]},
                                'tuesday': {'in': shift[6], 'out': shift[7]},
                                'wednesday': {'in': shift[8], 'out': shift[9]},
                                'thursday': {'in': shift[10], 'out': shift[11]},
                                'friday': {'in': shift[12], 'out': shift[13]},
                                'saturday': {'in': shift[14], 'out': shift[15]},
                                'sunday': {'in': shift[16], 'out': shift[17]}
                            }
                            
                            # If we have a specific employee_id, map by employee_id
                            if employee_id:
                                office_shifts_map[employee_id] = shift_schedule
                            # Otherwise, map by employee_hub_id for employees without specific shifts
                            elif employee_hub_id:
                                office_shifts_map[employee_hub_id] = shift_schedule
                                
                except Exception as e:
                    # # print(f"Error fetching office shifts data: {e}")
                    office_shifts_map = {}

                # 4. Get ALL attendance data in one optimized query
                try:
                    placeholders_attendance = ','.join(['%s'] * len(employee_ids))
                    cursor.execute(
                        f"""
                        SELECT 
                            ud.employee_id,
                            SUM(CASE WHEN bd.status = 'P' THEN 1 ELSE 0 END) AS present_days,
                            SUM(CASE WHEN bd.status = 'H' THEN 1 ELSE 0 END) AS half_days
                        FROM ci_erp_users u
                        LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
                        INNER JOIN ci_biomatric_data bd ON ud.employee_id = bd.emp_id
                        WHERE MONTH(bd.login_date) = %s 
                        AND YEAR(bd.login_date) = %s 
                        AND bd.attendance_status = 'Present' 
                        AND bd.state_in_out = 'in'
                        AND ud.employee_id IN ({placeholders_attendance})
                        GROUP BY ud.employee_id
                        """,
                        [month, year] + employee_ids
                    )
                    
                    attendance_data = cursor.fetchall()
                    present_days_map = {}
                    half_days_map = {}
                    
                    for emp_id, present, half in attendance_data:
                        present_days_map[emp_id] = present or 0
                        half_days_map[emp_id] = half or 0

                        # # print(present_days_map[emp_id])
                        
                except Exception as e:
                    # # print(f"Error fetching attendance data: {e}")
                    present_days_map = {}
                    half_days_map = {}

                # 5. Get approved leaves for all employees in one query
                try:
                    placeholders_leave = ','.join(['%s'] * len(employee_ids))
                    cursor.execute(
                        f"""
                        SELECT employee_id, 
                               SUM(CASE 
                                   WHEN is_half_day = 1 THEN 0.5 
                                   ELSE no_of_days
                               END) AS leave_days
                        FROM ci_leave_applications
                        WHERE status = 1 
                        AND line_manager_status = 1
                        AND employee_id IN ({placeholders_leave})
                        AND ((MONTH(from_date) = %s AND YEAR(from_date) = %s) 
                             OR (MONTH(to_date) = %s AND YEAR(to_date) = %s)
                             OR (from_date <= %s AND to_date >= %s))
                        GROUP BY employee_id
                        """,
                        employee_ids + [
                            month, year, month, year,
                            f"{year}-{month:02d}-01",
                            f"{year}-{month:02d}-{days_in_month}",
                        ],
                    )
                    leave_days_map = dict(cursor.fetchall())
                except Exception as e:
                    # # print(f"Error fetching leave data: {e}")
                    leave_days_map = {}

                # 6. Get holidays (unchanged - this is already efficient)

                holidays_map = {}

                try:
                    # print("test..")
                    query_params = [
                        month, year, month, year,
                        f"{year}-{month:02d}-01",
                        f"{year}-{month:02d}-{days_in_month}",
                    ]

                    conditions = ["h.is_publish = 1"]

                    if employee_hub_ids:
                        placeholders_employeehub = ','.join(['%s'] * len(employee_hub_ids))
                        conditions.append(f"h.employee_hub IN ({placeholders_employeehub})")
                        query_params.extend(employee_hub_ids)

                    if employee_states:
                        placeholders_state = ','.join(['%s'] * len(employee_states))
                        conditions.append(f"h.state IN ({placeholders_state})")
                        query_params.extend(employee_states)

                    holiday_where_clause = ' AND ' + ' AND '.join(conditions) if conditions else ''

                    cursor.execute(
                        f"""
                        SELECT h.employee_hub, h.state, COUNT(*) as holiday_days
                        FROM ci_holidays h
                        WHERE ((MONTH(h.start_date) = %s AND YEAR(h.start_date) = %s) 
                            OR (MONTH(h.end_date) = %s AND YEAR(h.end_date) = %s)
                            OR (h.start_date <= %s AND h.end_date >= %s))
                        {holiday_where_clause}
                        GROUP BY h.employee_hub, h.state
                        """,
                        query_params
                    )
                    
                    holidays_data = cursor.fetchall()

                    for employee_hub, state, holiday_days in holidays_data:
                        # Convert to consistent string types
                        key = (str(employee_hub) if employee_hub else '', str(state) if state else '')
                        holidays_map[key] = int(holiday_days) if holiday_days else 0
                        # print(f"Holiday found: key={key}, days={holidays_map[key]}")

                    # for employee_hub, state, holiday_days in holidays_data:
                    #     # Store with tuple key
                    #     holidays_map[(employee_hub, state)] = holiday_days or 0
                    #     # print(f"Holiday found: hub={employee_hub}, state={state}, days={holiday_days}")

                except Exception as e:
                    # print(f"Error fetching holidays data: {e}")
                    holidays_map = {}

                # 7. Get all salary changes in batch
                try:
                    salary_changes_by_employee = self.get_all_salary_changes_batch(employee_ids, year, month)
                except Exception as e:
                    # # print(f"Error fetching salary changes: {e}")
                    salary_changes_by_employee = {}

                # 8. Calculate holiday days from office shifts
                try:
                    holiday_days_data = self.calculate_holiday_days_from_shifts(year, month, office_shifts_map, employees)
                except Exception as e:
                    # # print(f"Error calculating holiday days from shifts: {e}")
                    # Fallback to original calculation
                    sundays = self.get_sundays_in_month(year, month)
                    holiday_days_data = {
                        'total_sundays': len(sundays),
                        'holiday_days_by_employee': {}
                    }

                # try:
                #     sundays = self.get_sundays_in_month(year, month)
                #     total_sundays = len(sundays) 
                # except Exception as e:
                #     # # print(f"Error calculating sundays: {e}")
                #     total_sundays = 0

                # Prepare data for batch salary calculation
                employees_salary_data = []
                payable_days_by_employee = {}
                
                for emp in employees:
                    try:
                        (
                            user_id, emp_id, emp_name, dept, desg, gender,
                            gross_salary, employee_hub_id, state, office_shift_id
                        ) = emp

                        lookup_key = (
                            str(employee_hub_id) if employee_hub_id else '', 
                            str(state) if state else ''
                        )
                        
                        # Calculate payable days for this employee with safe conversions
                        present_days = self.safe_decimal(present_days_map.get(emp_id, 0))
                        half_days_count = self.safe_decimal(half_days_map.get(emp_id, 0))
                        leave_days = self.safe_decimal(str(leave_days_map.get(emp_id, 0)))

                        # print(f"Looking up holiday key: {lookup_key}")
                        state_holidays = self.safe_decimal(holidays_map.get(lookup_key, 0))

                        # state_holidays = self.safe_decimal(str(holidays_map.get((employee_hub_id, state), 0)))
                        half_days_value = half_days_count * self.safe_decimal("0.5")

                        # print(f"Employee {emp_id}: hub={employee_hub_id}, state={state}, holidays={state_holidays}")
                        
                        # payable_days = (
                        #     present_days + half_days_value + leave_days + 
                        #     state_holidays + self.safe_decimal(total_sundays)
                        # )

                        # Get employee-specific holiday days from shifts or fall back to general calculation
                        employee_holiday_data = holiday_days_data['holiday_days_by_employee'].get(
                            emp_id, 
                            {'shift_holidays': holiday_days_data.get('total_sundays', 0)}
                        )
                        shift_holidays = self.safe_decimal(employee_holiday_data.get('shift_holidays', 0))

                        # print("employee_hub_id: ", employee_hub_id)
                        # print("state: ", state)
                        # print("present_days: ", present_days)
                        # print("half_days_value: ", half_days_value)
                        # print("leave_days: ", leave_days)
                        # print("state_holidays: ", state_holidays)
                        # print("shift_holidays: ", shift_holidays)

                        # Removed state_holidays from payable days to avoid double counting

                        payable_days = (
                            present_days + half_days_value + leave_days + 
                            shift_holidays
                        )
                        
                        payable_days_by_employee[emp_id] = payable_days
                        employees_salary_data.append((emp_id, payable_days, gross_salary))
                        
                    except Exception as e:
                        # # print(f"Error processing employee {emp_id if 'emp_id' in locals() else 'unknown'}: {e}")
                        # Set default values for this employee
                        if 'emp_id' in locals():
                            payable_days_by_employee[emp_id] = self.safe_decimal("0.00")
                            employees_salary_data.append((emp_id, self.safe_decimal("0.00"), gross_salary))

                # 9. Calculate gross earnings for all employees in batch
                try:
                    salary_calculations = self.calculate_gross_earning_with_salary_changes_batch(
                        employees_salary_data, salary_changes_by_employee, year, month, days_in_month
                    )
                except Exception as e:
                    # # print(f"Error in salary calculations: {e}")
                    salary_calculations = {}

                # 8. Build final results
                results = []
                for emp in employees:
                    (
                        user_id, emp_id, emp_name, dept, desg, gender,
                        gross_salary, employee_hub_id, state, office_shift_id
                    ) = emp

                    if gross_salary is None:
                        gross_salary = 0
                    
                    payable_days = payable_days_by_employee.get(emp_id, self.safe_decimal("0.00"))

                    # # print("payable_days: ", payable_days)

                    salary_calc = salary_calculations.get(emp_id, {
                        'gross_earning': self.safe_decimal("0.00"),
                        'total_monthly_earning': self.safe_decimal(gross_salary or 0)
                    })
                    
                    gross_earning = salary_calc.get('gross_earning', self.safe_decimal("0.00"))
                    total_monthly_earning = salary_calc.get('total_monthly_earning', self.safe_decimal(gross_salary or 0))
                    
                    # if emp_id == 'V1112':
                    #     # # print("total monthly earnings: ", total_monthly_earning)

                    esic_applicable = gross_salary <= self.safe_decimal("21000")  # Monthly limit

                    # Get structure percentages
                    get = lambda key: salary_structure.get(key, self.safe_decimal("0.00"))

                    # Earnings
                    basic_da = gross_earning * get("basic_plus_da")
                    hra = gross_earning * get("hra")
                    medical = gross_earning * (
                        get("medical_allowance_with_esic")
                        if esic_applicable
                        else get("medical_allowance_without_esic")
                    )
                    conveyance = gross_earning * (
                        get("conveyance_allowance_with_esic")
                        if esic_applicable
                        else get("conveyance_allowance_without_esic")
                    )

                    total_earnings = basic_da + hra + medical + conveyance

                    # Deductions
                    pf = min(
                        (gross_earning - hra) * get("pf_employee_contribution"),
                        self.safe_decimal("1800"),
                    )

                    if pf > 1800:
                        pf = 1800

                    esic_emp = gross_earning * get("esic_employee_contribution")  # Static/user-filled
                    pt = self.safe_decimal("0")
                    if gender == "Male":
                        pt = self.safe_decimal("300") if month == 2 else self.safe_decimal("200")
                    elif gender == "Female":
                        if month == 2:
                            pt = (
                                self.safe_decimal("300")
                                if gross_earning > self.safe_decimal("25000")
                                else self.safe_decimal("0")
                            )
                        else:
                            pt = (
                                self.safe_decimal("200")
                                if gross_earning > self.safe_decimal("25000")
                                else self.safe_decimal("0")
                            )

                    # Benefits
                    pf_employer = min(
                        (gross_earning - hra) * get("pf_employer_contribution"),
                        self.safe_decimal("1800"),
                    )
                    esic_employer = (
                        gross_earning * get("esic_employer_contribution")
                        if esic_applicable
                        else self.safe_decimal("0.00")
                    )

                    total_deduction = pf + esic_emp + pt
                    total_benefit = pf_employer + esic_employer
                    net_pay = total_earnings - total_deduction
                    ctc = total_earnings + total_benefit

                    results.append(
                        {
                            "Sr. No.": len(results) + 1,
                            "Employee ID": emp_id,
                            "Employee Name": emp_name,
                            "Department": dept,
                            "Designation": desg,
                            "M/F": gender,
                            "Gross Salary": float(round(gross_salary, 2)),
                            "Days": float(payable_days),
                            "ESIC Applicable": "Yes" if esic_applicable else "No",
                            "Gross Earning": float(round(gross_earning, 2)),
                            "Basic": float(round(basic_da, 2)),
                            "HRA": float(round(hra, 2)),
                            "Conveyance": float(round(conveyance, 2)),
                            "Medical": float(round(medical, 2)),
                            "Arrears": 0.00,
                            "Total Earnings": float(round(total_earnings, 2)),
                            "PF": float(round(pf, 2)),
                            "ESICS": float(round(esic_emp, 2)),
                            "PT": float(round(pt, 2)),
                            "MLWF": 0.00,
                            "Advance": 0.00,
                            "TDS": 0.00,
                            "Other Deduction": 0.00,
                            "Total Deduction": float(round(total_deduction, 2)),
                            "Net Pay": float(round(net_pay, 2)),
                            "CTC": float(round(ctc, 2)),
                        }
                    )

                return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    # def calculate_holiday_days_from_shifts(self, year, month, office_shifts_map, employees):
    #     """
    #     Calculate holiday days from office shifts where in_time or out_time is marked as 'Holiday'.
    #     These are paid holidays and should be included in payable days.
    #     """
    #     import calendar
    #     from datetime import datetime
        
    #     # Get all dates in the month
    #     days_in_month = calendar.monthrange(year, month)[1]
        
    #     # Day names mapping
    #     day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
    #     holiday_days_by_employee = {}
    #     total_sundays = 0  # Fallback calculation
        
    #     # Calculate total Sundays for fallback
    #     for day in range(1, days_in_month + 1):
    #         current_date = datetime(year, month, day)
    #         if current_date.weekday() == 6:  # Sunday
    #             total_sundays += 1
        
    #     # # Process each employee
    #     # for emp in employees:
    #     #     user_id, emp_id, emp_name, dept, desg, gender, gross_salary, employee_hub_id, state = emp
            
    #     #     # Find applicable shift for this employee
    #     #     shift_data = None
            
    #     #     # Try user-specific shift first
    #     #     if (employee_hub_id, user_id) in office_shifts_map:
    #     #         shift_data = office_shifts_map[(employee_hub_id, user_id)]
    #     #     # Fall back to hub-level shift
    #     #     elif employee_hub_id in office_shifts_map:
    #     #         shift_data = office_shifts_map[employee_hub_id]
            
    #     #     if not shift_data:
    #     #         # No shift data, use default Sunday calculation
    #     #         holiday_days_by_employee[emp_id] = {'shift_holidays': total_sundays}
    #     #         continue
            
    #     #     # Count holiday days based on shift schedule
    #     #     shift_holiday_days = 0
            
    #     #     for day in range(1, days_in_month + 1):
    #     #         current_date = datetime(year, month, day)
    #     #         day_name = day_names[current_date.weekday()]
                
    #     #         # Check if this day is marked as 'Holiday' in shift schedule
    #     #         day_shift = shift_data.get(day_name, {})
    #     #         in_time = day_shift.get('in', '').strip() if day_shift.get('in') else ''
    #     #         out_time = day_shift.get('out', '').strip() if day_shift.get('out') else ''
                
    #     #         # If either in_time or out_time is marked as 'Holiday', count it as a paid holiday
    #     #         if in_time.lower() == 'holiday' or out_time.lower() == 'holiday':
    #     #             shift_holiday_days += 1
            
    #     #     holiday_days_by_employee[emp_id] = {'shift_holidays': shift_holiday_days}

    #     # Process each employee - UPDATED TO USE NEW MAPPING STRUCTURE
    #     for emp in employees:
    #         user_id, emp_id, emp_name, dept, desg, gender, gross_salary, employee_hub_id, state, office_shift_id = emp
            
    #         # Find applicable shift for this employee
    #         shift_data = None
            
    #         # Try employee_id specific shift first (from office_shift_id mapping)
    #         if emp_id in office_shifts_map:
    #             shift_data = office_shifts_map[emp_id]
    #         # Fall back to hub-level shift
    #         elif employee_hub_id in office_shifts_map:
    #             shift_data = office_shifts_map[employee_hub_id]
            
    #         if not shift_data:
    #             # No shift data, use default Sunday calculation
    #             holiday_days_by_employee[emp_id] = {'shift_holidays': total_sundays}
    #             continue
            
    #         # Count holiday days based on shift schedule
    #         shift_holiday_days = 0
            
    #         for day in range(1, days_in_month + 1):
    #             current_date = datetime(year, month, day)
    #             day_name = day_names[current_date.weekday()]
                
    #             # Check if this day is marked as 'Holiday' in shift schedule
    #             day_shift = shift_data.get(day_name, {})
    #             in_time = day_shift.get('in', '').strip() if day_shift.get('in') else ''
    #             out_time = day_shift.get('out', '').strip() if day_shift.get('out') else ''
                
    #             # If either in_time or out_time is marked as 'Holiday', count it as a paid holiday
    #             if in_time.lower() == 'holiday' or out_time.lower() == 'holiday':
    #                 shift_holiday_days += 1
            
    #         holiday_days_by_employee[emp_id] = {'shift_holidays': shift_holiday_days}
        
    #     return {
    #         'holiday_days_by_employee': holiday_days_by_employee,
    #         'total_sundays': total_sundays  # For fallback
    #     }

    def calculate_holiday_days_from_shifts(self, year, month, office_shifts_map, employees):
        """
        Calculate holiday days from office shifts where in_time or out_time is marked as 'Holiday'.
        These are paid holidays and should be included in payable days.
        This method now avoids double counting with ci_holidays table dates.
        """
        import calendar
        from datetime import datetime
        
        # Get all dates in the month
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Day names mapping
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        holiday_days_by_employee = {}
        total_sundays = 0  # Fallback calculation
        
        # Calculate total Sundays for fallback
        for day in range(1, days_in_month + 1):
            current_date = datetime(year, month, day)
            if current_date.weekday() == 6:  # Sunday
                total_sundays += 1
        
        # Get actual holiday dates from ci_holidays table to avoid double counting
        actual_holiday_dates = set()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT DISTINCT DATE(holiday_date) as holiday_date
                    FROM (
                        SELECT start_date as holiday_date FROM ci_holidays
                        WHERE is_publish = 1
                        AND ((MONTH(start_date) = %s AND YEAR(start_date) = %s) 
                            OR (MONTH(end_date) = %s AND YEAR(end_date) = %s)
                            OR (start_date <= %s AND end_date >= %s))
                        
                        UNION ALL
                        
                        SELECT DATE(start_date + INTERVAL n DAY) as holiday_date
                        FROM ci_holidays
                        CROSS JOIN (
                            SELECT 0 n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
                            UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9
                            UNION SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14
                            UNION SELECT 15 UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19
                            UNION SELECT 20 UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24
                            UNION SELECT 25 UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29
                            UNION SELECT 30
                        ) numbers
                        WHERE is_publish = 1
                        AND DATE(start_date + INTERVAL n DAY) <= end_date
                        AND MONTH(start_date + INTERVAL n DAY) = %s
                        AND YEAR(start_date + INTERVAL n DAY) = %s
                    ) all_holidays
                    ORDER BY holiday_date
                    """,
                    [month, year, month, year, 
                    f"{year}-{month:02d}-01", f"{year}-{month:02d}-{days_in_month}",
                    month, year]
                )
                
                holiday_results = cursor.fetchall()
                for row in holiday_results:
                    if row[0]:  # holiday_date is not None
                        actual_holiday_dates.add(row[0].day)  # Store just the day number
                        
        except Exception as e:
            # # print(f"Error fetching actual holiday dates: {e}")
            actual_holiday_dates = set()
        
        # Process each employee - UPDATED TO USE NEW MAPPING STRUCTURE
        for emp in employees:
            user_id, emp_id, emp_name, dept, desg, gender, gross_salary, employee_hub_id, state, office_shift_id = emp
            
            # Find applicable shift for this employee
            shift_data = None
            
            # Try employee_id specific shift first (from office_shift_id mapping)
            if emp_id in office_shifts_map:
                shift_data = office_shifts_map[emp_id]
            # Fall back to hub-level shift
            elif employee_hub_id in office_shifts_map:
                shift_data = office_shifts_map[employee_hub_id]
            
            if not shift_data:
                # No shift data, use default Sunday calculation
                holiday_days_by_employee[emp_id] = {'shift_holidays': total_sundays}
                continue
            
            # Count holiday days based on shift schedule, avoiding double counting
            shift_holiday_days = 0
            
            for day in range(1, days_in_month + 1):
                current_date = datetime(year, month, day)
                day_name = day_names[current_date.weekday()]
                
                # Check if this day is marked as 'Holiday' in shift schedule
                day_shift = shift_data.get(day_name, {})
                in_time = day_shift.get('in', '').strip() if day_shift.get('in') else ''
                out_time = day_shift.get('out', '').strip() if day_shift.get('out') else ''
                
                # If either in_time or out_time is marked as 'Holiday', count it as a paid holiday
                # BUT only if this date is NOT already covered by ci_holidays table
                if (in_time.lower() == 'holiday' or out_time.lower() == 'holiday'):
                    if day not in actual_holiday_dates:
                        shift_holiday_days += 1
                    # If day is in actual_holiday_dates, we skip counting it here
                    # because it's already counted in state_holidays
            
            holiday_days_by_employee[emp_id] = {'shift_holidays': shift_holiday_days}
        
        return {
            'holiday_days_by_employee': holiday_days_by_employee,
            'total_sundays': total_sundays  # For fallback
        }


class PreSavedPayrollReport(APIView):

    def post(self, request):

        try:
            with connection.cursor() as c:

                c.execute("""select * from ci_payroll_report""")
                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SavePayrollReport(APIView):

    def post(self, request):
        try:
            payload = request.data
            if isinstance(payload, dict):
                employees = [payload]
            elif isinstance(payload, list):
                employees = payload
            else:
                return Response(
                    {"error": "Invalid JSON format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            required_fields = [
                "employee_id",
                "employee_name",
                "gender",
                "department_id",
                "designation_id",
                "month",
                "year",
                "gross_salary",
                "esic_applicable",
            ]

            for i, emp in enumerate(employees):

                if emp.get("gross_salary") in [None, ""]:
                    emp["gross_salary"] = 0

                for field in required_fields:
                    if not emp.get(field):
                        return Response(
                            {"error": f"'{field}' is required for record {i+1}."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

            with transaction.atomic():
                with connection.cursor() as cursor:
                    for emp in employees:
                        payroll_id = emp.get("payroll_report_id")

                        try:
                            fields = {
                                "employee_id": emp.get("employee_id"),
                                "employee_name": emp.get("employee_name"),
                                "gender": emp.get("gender", "O"),
                                "department_id": emp.get("department_id"),
                                "designation_id": emp.get("designation_id"),
                                "month": emp.get("month"),
                                "year": emp.get("year"),
                                "gross_salary": Decimal(str(emp.get("gross_salary"))),
                                "payable_days": emp.get("payable_days", 0),
                                "esic_applicable": emp.get("esic_applicable"),
                                "gross_earning": Decimal(
                                    str(emp.get("gross_earning", 0.00))
                                ),
                                "basic_plus_da": Decimal(
                                    str(emp.get("basic_plus_da", 0.00))
                                ),
                                "hra": Decimal(str(emp.get("hra", 0.00))),
                                "medical_allowance": Decimal(
                                    str(emp.get("medical_allowance", 0.00))
                                ),
                                "conveyance_allowance": Decimal(
                                    str(emp.get("conveyance_allowance", 0.00))
                                ),
                                "arrears": Decimal(str(emp.get("arrears", 0.00))),
                                "total_earnings": Decimal(
                                    str(emp.get("total_earnings", 0.00))
                                ),
                                "pf": Decimal(str(emp.get("pf", 0.00))),
                                "esic": Decimal(str(emp.get("esic", 0.00))),
                                "pt": Decimal(str(emp.get("pt", 0.00))),
                                "mlwf": Decimal(str(emp.get("mlwf", 0.00))),
                                "tds": Decimal(str(emp.get("tds", 0.00))),
                                "other_deduction": Decimal(
                                    str(emp.get("other_deduction", 0.00))
                                ),
                                "total_deduction": Decimal(
                                    str(emp.get("total_deduction", 0.00))
                                ),
                                "net_pay": Decimal(str(emp.get("net_pay", 0.00))),
                                "ctc": Decimal(str(emp.get("ctc", 0.00))),
                                "status": emp.get("status", "G"),
                                "created_at": datetime.now(),
                            }
                        except (ValueError, TypeError, InvalidOperation) as e:
                            return Response(
                                {
                                    "error": f"Invalid numeric value in employee data: {str(e)}"
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                        if payroll_id:

                            update_query = """
                                UPDATE ci_payroll_report SET
                                    employee_id=%s, employee_name=%s, gender=%s, department_id=%s,
                                    designation_id=%s, month=%s, year=%s, gross_salary=%s, payable_days=%s,
                                    esic_applicable=%s, gross_earning=%s, basic_plus_da=%s, hra=%s,
                                    medical_allowance=%s, conveyance_allowance=%s, arrears=%s,
                                    total_earnings=%s, pf=%s, esic=%s, pt=%s, mlwf=%s, tds=%s,
                                    other_deduction=%s, total_deduction=%s, net_pay=%s, ctc=%s,
                                    status=%s, created_at=%s
                                WHERE payroll_report_id = %s
                            """
                            cursor.execute(
                                update_query, list(fields.values()) + [payroll_id]
                            )
                        else:

                            insert_query = """
                                INSERT INTO ci_payroll_report (
                                    employee_id, employee_name, gender, department_id, designation_id,
                                    month, year, gross_salary, payable_days, esic_applicable,
                                    gross_earning, basic_plus_da, hra, medical_allowance, conveyance_allowance,
                                    arrears, total_earnings, pf, esic, pt, mlwf, tds, other_deduction,
                                    total_deduction, net_pay, ctc, status, created_at
                                ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s, %s, %s, %s
                                )
                            """
                            cursor.execute(insert_query, tuple(fields.values()))

            return Response(
                {"message": "Payroll report(s) saved successfully."},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentInfo(APIView):

    def post(self, request):

        employee_id = request.data.get("employee_id")
        month = request.data.get("month")
        year = request.data.get("year")

        if not employee_id or not month or not year:
            return Response(
                {"status": "error", "message": "some fields are missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                if employee_id == "all":

                    c.execute(
                        """select pr.payroll_report_id, concat(first_name,' ', last_name) as employee_name, u.email, 'Per Month' as payslip_type, pr.net_pay as net_salary, pr.status from ci_payroll_report pr inner join ci_erp_users_details ud on pr.employee_id = ud.employee_id inner join ci_erp_users u on ud.user_id = u.id where pr.month = %s and pr.year = %s""",
                        [month, year],
                    )

                    columns = [col[0] for col in c.description]
                    response = [dict(zip(columns, rows)) for rows in c.fetchall()]

                else:
                    c.execute(
                        """select pr.payroll_report_id, concat(first_name,' ', last_name) as employee_name, u.email, 'Per Month' as payslip_type, pr.net_pay as net_salary, pr.status from ci_payroll_report pr inner join ci_erp_users_details ud on pr.employee_id = ud.employee_id inner join ci_erp_users u on ud.user_id = u.id where pr.month = %s and pr.year = %s and pr.employee_id = %s""",
                        [month, year, employee_id],
                    )

                    columns = [col[0] for col in c.description]
                    response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdatePaymentInfo(APIView):

    def post(self, request):

        payroll_report_id = request.data.get("payroll_report_id")
        pay_status = request.data.get("pay_status")

        if not payroll_report_id or not pay_status:
            return Response(
                {"status": "error", "message": "some fields are missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                with connection.cursor() as c:

                    c.execute(
                        """update ci_payroll_report set status = %s where payroll_report_id = %s""",
                        [pay_status, payroll_report_id],
                    )

            return Response(
                {"status": "success", "message": "payroll status updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SalaryStructure(APIView):

    def post(self, request):

        employee_id = request.data.get("employee_id")
        month = request.data.get("month")
        year = request.data.get("year")

        if not employee_id or not month or not year:
            return Response(
                {"status": "error", "message": "some fields are missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with connection.cursor() as c:

                c.execute(
                    """select employee_name, gross_salary, basic_plus_da, hra, medical_allowance, conveyance_allowance, arrears, total_earnings, pf, esic, tds, mlwf, other_deduction, total_deduction, net_pay from ci_payroll_report where employee_id = %s and month = %s and year = %s""",
                    [employee_id, month, year],
                )

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PayslipHistory(APIView):

    def get(self, request):

        try:
            with connection.cursor() as c:

                c.execute(
                    """select payroll_report_id, employee_id, employee_name, net_pay, month, year, created_at as pay_date from ci_payroll_report where status = 'P'"""
                )

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# class Payslip(APIView):

#     def post(self, request):

#         payroll_report_id = request.data.get("payroll_report_id")

#         if not payroll_report_id:
#             return Response(
#                 {"status": "error", "message": "payroll_report_id is required"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             with connection.cursor() as c:

#                 c.execute(
#                     """select employee_name, month, year, pr.created_at as salary_payment_date, pr.employee_id, pr.employee_name, department_name, ud.date_of_joining, designation_name, u.city as location, payable_days, ud.bank_name, ud.account_number as bank_account_number, pf_number, uan_number, esic_number, pan_number, basic_plus_da, hra, medical_allowance, conveyance_allowance, arrears, total_earnings, pf, esic, pt, tds, mlwf, tds, other_deduction, total_deduction, net_pay from ci_payroll_report pr inner join ci_erp_users_details ud on pr.employee_id = ud.employee_id inner join ci_erp_users u on ud.user_id = u.id inner join ci_departments dpt on ud.department_id = dpt.department_id inner join ci_designations dsg on pr.designation_id = dsg.designation_id where pr.payroll_report_id = %s""",
#                     [payroll_report_id],
#                 )

#                 columns = [col[0] for col in c.description]
#                 response = [dict(zip(columns, rows)) for rows in c.fetchall()]

#             return Response(
#                 {"status": "success", "data": response}, status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occured: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


class Payslip(APIView):
 
    def post(self, request):
 
        payroll_report_id = request.data.get("payroll_report_id")
 
        if not payroll_report_id:
            return Response(
                {"status": "error", "message": "payroll_report_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        try:
            with connection.cursor() as c:
 
                c.execute(
                    """select employee_name, month, year, pr.created_at as salary_payment_date, pr.employee_id, pr.employee_name, department_name, ud.date_of_joining, designation_name, u.city as location, payable_days, ud.bank_name, ud.account_number as bank_account_number, pf_number, uan_number, esic_number, pan_number, basic_plus_da, hra, medical_allowance, conveyance_allowance, arrears, total_earnings, pf, esic, pt, tds, mlwf, tds, other_deduction, total_deduction, net_pay
                    from ci_payroll_report pr left join ci_erp_users_details ud on pr.employee_id = ud.employee_id left join ci_erp_users u on ud.user_id = u.id left join ci_departments dpt on ud.department_id = dpt.department_id left join ci_designations dsg on ud.designation_id = dsg.designation_id
                    where pr.payroll_report_id = %s""",
                    [payroll_report_id],
                )
 
                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]
 
            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )
 
        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SearchByEmailVetTalent(APIView):

    def get(self, request):

        try:
            with connections["raas"].cursor() as c:

                # c.execute("""select bja.*, ba.* from backendapp_jobapplication bja inner join backendapp_applicant ba on bja.applicant_id = ba.id where bja.job_status = 'selected'""")
                c.execute("""select ba.* from backendapp_letters bl inner join backendapp_applicant ba on bl.user_id = ba.id group by email;""")

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, rows)) for rows in c.fetchall()]

            return Response(
                {"status": "success", "data": response}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class HolidayCalendarView(APIView):
    def get(self,request , country_id,state_id,employee_hub):
        query="""
        select h.holiday_id ,c.category_name AS state_name, h.event_name , h.description , h.start_date , h.end_date from ci_holidays h left join ci_erp_constants c on h.state=c.constants_id where h.country= %s and h.state=%s and h.employee_hub=%s
        """

        params=[country_id,state_id,employee_hub]
        with connection.cursor() as cursor:
            cursor.execute(query,params)
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, rows)) for rows in cursor.fetchall()]
        return Response(
            {"status": "success", "data": rows}, status=status.HTTP_200_OK
        )        

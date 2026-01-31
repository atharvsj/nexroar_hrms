from django.core.files.base import ContentFile
from calendar import monthrange
from datetime import date, datetime, time
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import os
from django.http import Http404
from urllib.parse import quote
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import BiomatricDataTemp, ERPUser, ERPUserDetails, TaskDiscussion, TaskFile, TaskNote, ErpUser1, CiStaffRole
from .models import  CiBiomatricData, CIPunchReport, ContractOption, CaseType
from .serializers import ChangePasswordSerializers, ERPUserSerializer, LoginSerializer, MonthlyAttendenceSerializer, OnDutyRequestSerializer
from .serializers import  RegistrationSerializer, TodayAttendenceSerializers, TaskDiscussionSerializer, TaskFileSerializer, TaskNoteSerializer, ErpUserSerializer
from .serializers import  CiStaffRoleSerializer, CiBiomatricDataSerializer, CIPunchReportSerializer, ContractOptionSerializer
from .permissions import IsAdmin,IsEmployee,IsReportingManager
from .permissions import IsAdmin,IsEmployee,IsReportingManager
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

#Aditya Code :
from django.shortcuts import render

# Create your views here.
from datetime import date, datetime, time
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework import serializers
from .serializers import  CIPunchReportSerializer , AssignedTaskSerializer,AssignedTaskDetailView
from django.utils import timezone
import bcrypt
import pytz
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import AssignedTask
from .serializers import AssignedTaskSerializer, AssignedTaskDetailView
# from rest_framework import serializers
from .models import CIPunchReport, ContractOption , AssignedTask
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

import requests

from .utils import validate_file_size
###

class RegistrationView(APIView):
    permission_classes = [IsAuthenticated] # Allow anyone to register

    def post(self, request, *args, **kwargs):
        # Validate and create the user
        serializer = RegistrationSerializer(data=request.data)
        print('serializer: ',serializer)
        if serializer.is_valid():
            
            user = serializer.save()
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
#     permission_classes = [AllowAny]  # Allow anyone to access the login view
#     def post(self, request, *args, **kwargs):
#         # Validate and authenticate using the LoginSerializer
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']  # The user object returned by the serializer
#            # print("User: ", user)
#             # Create JWT token
#             refresh = RefreshToken.for_user(user)
#             access_token = str(refresh.access_token)
#             try:
#                 user_detail = ERPUserDetails.objects.get(user_id=user)
#                 employee_id = user_detail.employee_id
#             except ERPUserDetails.DoesNotExist:
#                 employee_id = None
#             # Return the JWT token along with the role
#             return Response({
#                 'refresh': str(refresh),
#                 'access': access_token,
#                 'user_id': user.id,
#                 'employee_id': employee_id,
#                 'role': user.user_role_id.role_name,  # Assuming you have a `user_role_id` ForeignKey to `StaffRole`
#                  # Added user_id to the response
#             }, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access the login view

    def post(self, request, *args, **kwargs):
        # Validate and authenticate using the LoginSerializer
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]  # The user object returned by the serializer
            # print("User: ", user)

            # Create JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            try:
                user_detail = ERPUserDetails.objects.get(user_id=user)
                employee_id = user_detail.employee_id
            except ERPUserDetails.DoesNotExist:
                employee_id = None

            if user.id:
                with connection.cursor() as c:
                    c.execute(
                        """select u.is_hod,u.email,ud.designation_id,d.designation_name from ci_erp_users u inner join ci_erp_users_details ud on u.id = ud.user_id inner join ci_designations d on ud.designation_id = d.designation_id where u.id = %s""", [user.id]
                    )
                    # is_hod, email = c.fetchone()
                    row = c.fetchone()
                    is_hod = row[0]
                    email = row[1]
                    designation_id = row[2]
                    designation_name = row[3]

            # Return the JWT token along with the role
            return Response(
                {
                    "refresh": str(refresh),
                    "access": access_token,
                    "user_id": user.id,
                    "employee_id": employee_id,
                    "role": user.user_role_id.role_name,  # Assuming you have a `user_role_id` ForeignKey to `StaffRole`
                    "role_id": user.user_role_id.role_id,
                    "is_hod": is_hod,
                    # "email_id": email,
                    "email": email,
                    "designation_id": designation_id,
                    "designation_name": designation_name,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BasicInfo(APIView):
    permission_classes = [IsAuthenticated,IsReportingManager]
    # permission_classes = [AllowAny]  # Allow anyone to access the login view
    
    def get(self,request):
        emp_id = request.user.id
        print("emp_id: ",emp_id)
        user = ERPUser.objects.prefetch_related("erpuserdetails_set").get(id=emp_id)
        serialzer = ERPUserSerializer(user)
        return Response({"status":"Sucess","BasicInfo":serialzer.data})
    
    def patch(self, request):
        
        # Get the authenticated user
        emp_id = request.user.id
        request.data['id'] = emp_id
        user = get_object_or_404(ERPUser.objects.prefetch_related("erpuserdetails_set"), id=emp_id)

        # Pass the data for partial update
        serializer = ERPUserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()  # Save changes
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        # Initialize the serializer with the request data and include emp_id automatically
        serializer = ChangePasswordSerializers(request.user, data=request.data, partial=True)

        # Validate the data
        if serializer.is_valid():
            # Save the changes (this will invoke the update method in the serializer)
            serializer.save()
            return Response({"Message": "Success"})
        return Response({"error": serializer.errors}, status=400)
    





from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date
from .models import BiomatricDataTemp
from .serializers import TodayAttendenceSerializers

User = get_user_model()

class TodayAttendance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()

        # Step 1: Get all active employees
        active_employees = User.objects.filter(is_active=True)

        # Step 2: Get today's attendance entries
        attendance_qs = BiomatricDataTemp.objects.filter(
            attendance_date=today,
            userid__in=active_employees.values_list('id', flat=True)
        ).select_related('userid')

        # Step 3: Map attendance by user id
        attendance_map = {record.userid.id: record for record in attendance_qs}

        # Step 4: Build response data
        response_data = []
        for emp in active_employees:
            record = attendance_map.get(emp.id)
            response_data.append({
                "user_id": emp.id,
                "emp_name": f"{emp.first_name} {emp.last_name}",
                "attendance_date": today,
                "attendance_status": "Present" if record else "Absent",
                "punch_in_time": record.punch_in_time if record else None,
            })

        # Step 5: Serialize manually constructed list
        serializer = TodayAttendenceSerializers(response_data, many=True)
        return Response({"data": serializer.data})        
    def parse_time(clock_in):
       try:
        # Check if the clock_in is in timestamp format
        if " " in clock_in:  # Full timestamp with date and time
            clock_in_time = datetime.strptime(clock_in, "%Y-%m-%d %H:%M:%S.%f").time()
        else:
            # Handle cases like "00:00" (no clock-in recorded)
            clock_in_time = datetime.strptime(clock_in, "%H:%M").time()
        return clock_in_time
       except ValueError:
        # If the format is not valid, return None
        return None



class OnDutyInRequest(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        request.data['userid'] = request.user.id
        
        serializer = OnDutyRequestSerializer(data = request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"OD Created"})
        return Response({"error":serializer.errors})

    

# ci_projects_bugs

from .models import CIProjectBug
from .serializers import CIProjectBugSerializer

class CIProjectBugListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_bugs = CIProjectBug.objects.all()
        serializer = CIProjectBugSerializer(project_bugs, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Set the `employee_id` field to the current authenticated user
        data = request.data
        data['employee_id'] = request.user.id

        serializer = CIProjectBugSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Bug reported successfully!", "project_bug": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, project_bug_id):
        # Fetch the project bug and update
        project_bug = CIProjectBug.objects.filter(project_bug_id=project_bug_id, employee_id=request.user).first()
        if not project_bug:
            return Response({"error": "Bug not found or you do not have permission to edit it."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CIProjectBugSerializer(project_bug, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Bug updated successfully!", "project_bug": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_bug_id):
        # Fetch and delete the project bug
        project_bug = CIProjectBug.objects.filter(project_bug_id=project_bug_id).first()
        if not project_bug:
            return Response({"error": "Bug not found or you do not have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)
        
        project_bug.delete()
        return Response({"message": "Bug deleted successfully!"}, status=status.HTTP_200_OK)


    


# List & Create View
class AssignedTaskListView(APIView):
    def get(self, request):
        tasks = AssignedTask.objects.all()
        serializer = AssignedTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AssignedTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, Update, Delete View
class AssignedTaskDetailView(APIView):
    def get_object(self, task_id):
        try:
            return AssignedTask.objects.get(task_id=task_id)
        except AssignedTask.DoesNotExist:
            raise Http404

    def get(self, request, task_id):
        task = self.get_object(task_id)
        serializer = AssignedTaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, task_id):
        task = self.get_object(task_id)
        serializer = AssignedTaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        task = self.get_object(task_id)
        task.delete()
        return Response({"message": "Task deleted successfully."}, status=status.HTTP_200_OK)
###

class TaskDiscussionAPIView(APIView):
    def get(self, request):
        discussions = TaskDiscussion.objects.all()
        serializer = TaskDiscussionSerializer(discussions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaskDiscussionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TaskFileView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TaskFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Task file created successfully',
                'task_file': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        task_files = TaskFile.objects.all()
        serializer = TaskFileSerializer(task_files, many=True)
        return Response({"task_files": serializer.data}, status=status.HTTP_200_OK)

    def get_task_file(self, request, task_file_id, *args, **kwargs):
        try:
            task_file = TaskFile.objects.get(task_file_id=task_file_id)
            serializer = TaskFileSerializer(task_file)
            return Response({"task_file": serializer.data}, status=status.HTTP_200_OK)
        except TaskFile.DoesNotExist:
            return Response({"error": "Task file not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, task_file_id, *args, **kwargs):
        try:
            task_file = TaskFile.objects.get(task_file_id=task_file_id)
            serializer = TaskFileSerializer(task_file, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Task file updated successfully',
                    'task_file': serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TaskFile.DoesNotExist:
            return Response({"error": "Task file not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, task_file_id, *args, **kwargs):
        try:
            task_file = TaskFile.objects.get(task_file_id=task_file_id)
            task_file.delete()
            return Response({'message': 'Task file deleted successfully'}, status=status.HTTP_200_OK)
        except TaskFile.DoesNotExist:
            return Response({"error": "Task file not found"}, status=status.HTTP_404_NOT_FOUND)


class TaskNoteView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TaskNoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Task note created successfully',
                'task_note': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        task_notes = TaskNote.objects.all()
        serializer = TaskNoteSerializer(task_notes, many=True)
        return Response({"task_notes": serializer.data}, status=status.HTTP_200_OK)

    def get_task_note(self, request, task_note_id, *args, **kwargs):
        try:
            task_note = TaskNote.objects.get(task_note_id=task_note_id)
            serializer = TaskNoteSerializer(task_note)
            return Response({"task_note": serializer.data}, status=status.HTTP_200_OK)
        except TaskNote.DoesNotExist:
            return Response({"error": "Task note not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, task_note_id, *args, **kwargs):
        try:
            task_note = TaskNote.objects.get(task_note_id=task_note_id)
            serializer = TaskNoteSerializer(task_note, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Task note updated successfully',
                    'task_note': serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TaskNote.DoesNotExist:
            return Response({"error": "Task note not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, task_note_id, *args, **kwargs):
        try:
            task_note = TaskNote.objects.get(task_note_id=task_note_id)
            task_note.delete()
            return Response({'message': 'Task note deleted successfully'}, status=status.HTTP_200_OK)
        except TaskNote.DoesNotExist:
            return Response({"error": "Task note not found"}, status=status.HTTP_404_NOT_FOUND)
        


#######punch-report

from .models import CIPunchReport

class CIPunchReportView(APIView):

    def get(self, request):
        reports = CIPunchReport.objects.all()
        serializer = CIPunchReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CIPunchReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
class ErpUserCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ErpUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'User created successfully',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Roles & Privileges 

class CiStaffRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, role_id=None):
        roles = CiStaffRole.objects.all()
        serializer = CiStaffRoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        serializer = CiStaffRoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, role_id=None):
        try:
            # Get the role by its ID
            role = CiStaffRole.objects.get(role_id=role_id)
            role.delete()
            return Response({"message": "Role deleted successfully"}, status=status.HTTP_200_OK)
        except CiStaffRole.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        


#  Shift & Scheduling

from .models import OfficeShift
from .serializers import OfficeShiftSerializer


class OfficeShiftView(APIView):
    permission_classes = [AllowAny]

    # GET method to retrieve all office shifts
    def get(self, request):
        shifts = OfficeShift.objects.all()
        serializer = OfficeShiftSerializer(shifts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST method to create a new office shift
    def post(self, request):
        serializer = OfficeShiftSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE method to delete an office shift by its ID
    def delete(self, request, office_shift_id=None):
        try:
            shift = OfficeShift.objects.get(office_shift_id=office_shift_id)
            shift.delete()
            return Response({"message": "Shift deleted successfully"}, status=status.HTTP_200_OK)
        except OfficeShift.DoesNotExist:
            return Response({"error": "Shift not found"}, status=status.HTTP_404_NOT_FOUND)

    # PUT method to update an office shift by its ID
    def put(self, request, office_shift_id=None):
        try:
            shift = OfficeShift.objects.get(office_shift_id=office_shift_id)
        except OfficeShift.DoesNotExist:
            return Response({"error": "Shift not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OfficeShiftSerializer(shift, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

#  Exit Employee 

class CiEmployeeExitView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    e.exit_id, 
                    e.company_id, 
                    e.employee_id,
                    e.employee_name,
                    e.exit_date, 
                    e.exit_type_id,
                    c.category_name AS exit_type_name,
                    e.sub_exit_type_id,
                    e.exit_interview, 
                    e.is_inactivate_account,
                    e.reason, 
                    e.accountability_to, 
                    e.added_by, 
                    e.created_at
                FROM 
                    ci_employee_exit e
                LEFT JOIN 
                    ci_erp_users u ON u.id = e.employee_id
                LEFT JOIN 
                    ci_erp_constants c ON c.constants_id = e.exit_type_id AND c.type = 'exit_type'
                ORDER BY 
                    STR_TO_DATE(e.created_at, '%Y-%m-%d %H:%i:%s') DESC
            """)
            rows = cursor.fetchall()

        columns = [
            "exit_id", "company_id", "employee_id", "employee_name",
            "exit_date", "exit_type_id", "exit_type_name", "sub_exit_type_id",
            "exit_interview", "is_inactivate_account",
            "reason", "accountability_to", "added_by", "created_at"
        ]

        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Convert 1/0 to yes/no
            row_dict["exit_interview"] = "yes" if row_dict["exit_interview"] == 1 else "no"
            row_dict["is_inactivate_account"] = "yes" if row_dict["is_inactivate_account"] == 1 else "no"
            data.append(row_dict)

        return Response(data, status=status.HTTP_200_OK)


    # def post(self, request):
    #     data = request.data
    #     required_fields = [
    #         "employee_id", "exit_date", "exit_type_id",
    #         "exit_interview", "is_inactivate_account", "reason",
    #         "accountability_to", "added_by"
    #     ]

    #     # Check for missing required fields
    #     missing = [field for field in required_fields if not data.get(field)]
    #     if missing:
    #         return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

    #     # Convert yes/no to 1/0
    #     exit_interview = 1 if str(data["exit_interview"]).lower() == "yes" else 0
    #     is_inactivate_account = 1 if str(data["is_inactivate_account"]).lower() == "yes" else 0

    #     company_id = 2  # Default
    #     sub_exit_type_id = data.get("sub_exit_type_id")
    #     created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             INSERT INTO ci_employee_exit (
    #                 company_id, employee_id, exit_date, exit_type_id,
    #                 sub_exit_type_id, exit_interview, is_inactivate_account,
    #                 reason, accountability_to, added_by, created_at
    #             ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #         """, [
    #             company_id,
    #             data["employee_id"],
    #             data["exit_date"],
    #             data["exit_type_id"],
    #             sub_exit_type_id,
    #             exit_interview,
    #             is_inactivate_account,
    #             data["reason"],
    #             data["accountability_to"],
    #             data["added_by"],
    #             created_at
    #         ])

        # return Response({"message": "Employee exit record created successfully."}, status=status.HTTP_201_CREATED)
    
    
    def post(self, request):
        data = request.data
        required_fields = [
            "employee_id", "exit_date", "exit_type_id",
            "reason", "added_by"
        ]

 
        # Check for missing required fields
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)
 
        employee_id = data.get("employee_id")
        exit_date = data.get("exit_date")
        reason = data.get("reason")
        company_id = 2  # Default
        sub_exit_type_id = data.get("sub_exit_type_id")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
        #get employee name
        with connection.cursor() as c:
            c.execute("""select CONCAT(u.first_name, ' ', u.last_name) as employee_name from ci_erp_users u inner join ci_erp_users_details ud on u.id = ud.user_id where ud.employee_id = %s""", [data["employee_id"]])
 
            row = c.fetchone()
            employee_name = row[0] if row and row[0] is not None else ''
 
 
 
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_employee_exit (
                    company_id, employee_id, employee_id_1, employee_name, exit_date, exit_type_id,
                    sub_exit_type_id,
                    reason, added_by, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, [
                company_id,
                data["employee_id"],
                data["employee_id"],
                employee_name,
                data["exit_date"],
                data["exit_type_id"],
                sub_exit_type_id,
                data["reason"],
                data["added_by"],
            ])

            if cursor.lastrowid > 0:

                #Get admin id
                cursor.execute("""select id from ci_erp_users u inner join ci_staff_roles sr on u.user_role_id = sr.role_id where sr.role_name = 'Admin' and u.is_active = 1 order by u.id desc limit 1""")

                admin_result = cursor.fetchone()
                if not admin_result:
                    raise ValueError("No admin user found in the system")
                
                admin_id = admin_result[0]

                #Get user id
                cursor.execute("""select id from ci_erp_users where username = %s""", [employee_id])

                user_result = cursor.fetchone()
                if not user_result:
                    raise ValueError(f"No user found for employee_id: {employee_id} in the system")
                
                user_id = user_result[0]

                #Send Notification
                notification_text = f"Your exit has been processed. Your last working date is {exit_date}. Kindly complete the pending exit formalities"

                cursor.execute("""
                    INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, [admin_id, user_id, notification_text])
 
        return Response({"message": "Employee exit record created successfully."}, status=status.HTTP_201_CREATED)
    
    def patch(self, request, exit_id):
        data = request.data
        allowed_fields = [
            "employee_id", "exit_date", "exit_type_id", "sub_exit_type_id",
            "exit_interview", "is_inactivate_account", "reason", "accountability_to", "added_by"
        ]

        fields = []
        values = []

        for field in allowed_fields:
            if field in data:
                value = data[field]
                if field in ["exit_interview", "is_inactivate_account"]:
                    value = 1 if str(value).lower() == "yes" else 0
                fields.append(f"{field} = %s")
                values.append(value)

        if not fields:
            return Response({"error": "No valid fields provided for update."}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            # Check if the record exists
            cursor.execute("SELECT COUNT(*) FROM ci_employee_exit WHERE exit_id = %s", [exit_id])
            if cursor.fetchone()[0] == 0:
                return Response({"error": "Exit record not found."}, status=status.HTTP_404_NOT_FOUND)

            # Perform the update
            query = f"UPDATE ci_employee_exit SET {', '.join(fields)} WHERE exit_id = %s"
            values.append(exit_id)
            cursor.execute(query, values)

        return Response({"message": "Employee exit record updated successfully."}, status=status.HTTP_200_OK)



    def delete(self, request, exit_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ci_employee_exit WHERE exit_id = %s", [exit_id])
            if cursor.fetchone()[0] == 0:
                return Response({"error": "Exit record not found"}, status=status.HTTP_404_NOT_FOUND)

            cursor.execute("DELETE FROM ci_employee_exit WHERE exit_id = %s", [exit_id])
        return Response({"message": "Exit record deleted successfully."}, status=status.HTTP_200_OK)




class CiDesignationViewSet(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d.designation_id,
                    d.company_id,
                    d.designation_name,
                    d.designation_code,
                    d.line_manager_id,
                    lm.designation_name AS line_manager_name,
                    d.description,
                    d.created_at,
                    d.department_id,
                    dept.department_name
                FROM ci_designations d
                LEFT JOIN ci_departments dept ON d.department_id = dept.department_id
                LEFT JOIN ci_designations lm ON d.line_manager_id = lm.designation_id
                ORDER BY d.designation_id DESC
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(data, status=status.HTTP_200_OK)

    # def post(self, request, *args, **kwargs):
    #     data = request.data
    #     designation_id = data.get("designation_id")
    #     company_id = data.get("company_id")
    #     company_id = int(company_id) if company_id not in [None, '', 'null', 'None'] else 2
    #     designation_name = data.get("designation_name")
    #     designation_code = data.get("designation_code")
    #     description = data.get("description")
    #     department_id = data.get("department_id")

    #     created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #     with connection.cursor() as cursor:
    #         cursor.execute("SELECT 1 FROM ci_designations WHERE designation_id = %s", [designation_id])
    #         if cursor.fetchone():
    #             return Response({"error": "Designation ID already exists"}, status=status.HTTP_400_BAD_REQUEST)

    #         cursor.execute("""
    #             INSERT INTO ci_designations 
    #             (designation_id, company_id, designation_name, designation_code, description, created_at, department_id)
    #             VALUES (%s, %s, %s, %s, %s, %s, %s)
    #         """, [designation_id, company_id, designation_name, designation_code, description, created_at, department_id])
        
    #     return Response({
    #         "message": "Designation created successfully!",
    #         "created_at": created_at
    #     }, status=status.HTTP_201_CREATED)
    
    
    def post(self, request):
 
        data = request.data
 
        department_id = data.get("department_id")
        company_id = data.get("company_id", 2)
        designation_name = data.get("designation_name")
        designation_code = data.get("designation_code")
        line_manager_id = data.get("line_manager_id")
        description = data.get("description")
 
        if not all([department_id, designation_name, designation_code]):
            return Response({"status":"error","message": "some fields are missing"}, status=status.HTTP_400_BAD_REQUEST)
 
        with connection.cursor() as cursor:
 
            cursor.execute("""
                INSERT INTO ci_designations
                (department_id, company_id, designation_name, designation_code, line_manager_id, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, [department_id, company_id, designation_name, designation_code, line_manager_id, description])
       
        return Response({
            "message": "Designation created successfully!"
        }, status=status.HTTP_201_CREATED)


    def patch(self, request, pk, *args, **kwargs):
        data = request.data
        fields = []
        values = []

        for key in ["designation_code", "company_id", "designation_name", "description", "line_manager_id", "created_at", "department_id"]:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])

        if not fields:
            return Response({"error": "No valid fields provided for update"}, status=status.HTTP_400_BAD_REQUEST)

        values.append(pk)

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM ci_designations WHERE designation_id = %s", [pk])
            if not cursor.fetchone():
                return Response({"error": "Designation not found"}, status=status.HTTP_404_NOT_FOUND)

            cursor.execute(f"""
                UPDATE ci_designations
                SET {', '.join(fields)}
                WHERE designation_id = %s
            """, values)

        return Response({"message": "Designation updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM ci_designations WHERE designation_id = %s", [pk])
            if not cursor.fetchone():
                return Response({"error": "Designation not found"}, status=status.HTTP_404_NOT_FOUND)

            cursor.execute("DELETE FROM ci_designations WHERE designation_id = %s", [pk])

        return Response({"message": "Designation deleted successfully"}, status=status.HTTP_200_OK)




import base64

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class CIPolicyView(APIView):
    # authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    policy_id,
                    company_id,
                    title,
                    description,
                    attachment,
                    added_by,
                    created_at
                FROM ci_policies
            """)
            rows = dictfetchall(cursor)

        for row in rows:
            # Format created_at as date only
            created_at = row.get("created_at")
            if created_at:
                try:
                    # If it's a datetime object
                    row["created_at"] = created_at.strftime("%Y-%m-%d")
                except AttributeError:
                    # If it's already a string
                    try:
                        row["created_at"] = datetime.strptime(created_at, "%Y-%m-%d").strftime("%Y-%m-%d")
                    except:
                        row["created_at"] = created_at  # fallback to original string

       
            # attachment_path = row.get("attachment")
            # if attachment_path:
            #     full_path = os.path.join(settings.MEDIA_ROOT, attachment_path)

            #     if os.path.exists(full_path):
            #         with open(full_path, "rb") as file:
            #             content = file.read()
            #             encoded_content = base64.b64encode(content).decode("utf-8")
                    
            #         row["attachment"] = {
            #             "file_name": os.path.basename(attachment_path),
            #             "file_content": encoded_content
            #         }
            #     else:
            #         row["attachment"] = {
            #             "file_name": os.path.basename(attachment_path),
            #             "file_content": None,
            #             "error": "File not found"
            #         }
            # else:
            #     row["attachment"] = None

            attachment_path = row.get("attachment")
            if attachment_path:
                    row["attachment"] = {
                        "file_name": os.path.basename(attachment_path),
                        "file_url": f"/media/{quote(attachment_path)}"
                    }
            else:
                    row["attachment"] = None


        return Response({
            "message": "Policies retrieved successfully", 
            "data": rows
        }, status=status.HTTP_200_OK)
    
    # def post(self, request):
    #     data = request.data
    #     data["company_id"] = data.get("company_id", 2)  # Default company_id to 2
       
    #     required_fields = ["title", "description", "added_by"]
       
    #     # Validate required fields
    #     for field in required_fields:
    #         if field not in data:
    #             return Response({
    #                 "status": "error",
    #                 "message": f"Missing required field: {field}"
    #             }, status=status.HTTP_400_BAD_REQUEST)
       
    #     try:
    #         with connection.cursor() as cursor:
    #             attachment = request.FILES.get('attachment')
    #             attachment_path = None
               
    #             if attachment:
    #                 # Define paths
    #                 policies_dir = os.path.join(settings.MEDIA_ROOT, 'policies')
    #                 os.makedirs(policies_dir, exist_ok=True)  # Create directory if needed
                   
    #                 # Sanitize filename
    #                 original_name = attachment.name
    #                 base, ext = os.path.splitext(original_name)
    #                 safe_name = f"{base[:50]}{ext}".replace(' ', '_')
    #                 safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-', '.'))
                   
    #                 # Ensure unique filename
    #                 counter = 1
    #                 while os.path.exists(os.path.join(policies_dir, safe_name)):
    #                     safe_name = f"{base[:45]}_{counter}{ext}"
    #                     counter += 1
                   
    #                 # Save file
    #                 file_path = os.path.join(policies_dir, safe_name)
    #                 with open(file_path, 'wb+') as destination:
    #                     for chunk in attachment.chunks():
    #                         destination.write(chunk)
                   
    #                 # Store relative path in DB
    #                 attachment_path = f"policies/{safe_name}"
               
    #             # Insert into database
    #             cursor.execute("""
    #                 INSERT INTO ci_policies (
    #                     company_id,
    #                     title,
    #                     description,
    #                     attachment,
    #                     added_by,
    #                     created_at
    #                 ) VALUES (%s, %s, %s, %s, %s, NOW())
    #             """, [
    #                 data["company_id"],
    #                 data["title"],
    #                 data["description"],
    #                 attachment_path,  # Will be NULL if no attachment
    #                 data["added_by"]
    #             ])
               
    #             # Get the new policy ID
    #             cursor.execute("SELECT LAST_INSERT_ID()")
    #             policy_id = cursor.fetchone()[0]
    #             todays_date = datetime.today()

               
    #             # return Response({
    #             #     "status": "success",
    #             #     "message": "Policy created successfully",
    #             #     "policy_id": policy_id,
    #             #     "attachment_url": f"/media/{quote(attachment_path)}" if attachment_path else None
    #             # }, status=status.HTTP_201_CREATED)
               
    #             cursor.execute("""
    #             UPDATE ci_policy_allocations
    #             SET policy_id = CONCAT_WS(',', policy_id, %s) , allocation_date = %s
    #         """, [policy_id,todays_date])
 
    #             return Response({
    #                 "status": "success",
    #                 "message": "Policy created and allocated to all employees successfully",
    #                 "policy_id": policy_id,
    #                 "attachment_url": f"/media/{quote(attachment_path)}" if attachment_path else None
    #             }, status=status.HTTP_201_CREATED)
               
    #     except Exception as e:
    #         # Clean up if file was saved but DB operation failed
    #         if 'file_path' in locals() and os.path.exists(file_path):
    #             try:
    #                 os.remove(file_path)
    #             except:
    #                 pass
                   
    #         return Response({
    #             "status": "error",
    #             "message": f"Failed to create policy: {str(e)}"
    #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        data = request.data
        data["company_id"] = data.get("company_id", 2)  # Default company_id to 2
 
        descr = data.get("description", '')
       
        required_fields = ["title", "added_by"]
       
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return Response({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }, status=status.HTTP_400_BAD_REQUEST)
       
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    attachment = request.FILES.get('attachment')
                    attachment_path = None
               
                    if attachment:
                        # Define paths
                        policies_dir = os.path.join(settings.MEDIA_ROOT, 'policies')
                        os.makedirs(policies_dir, exist_ok=True)  # Create directory if needed
                   
                        # Sanitize filename
                        original_name = attachment.name
                        base, ext = os.path.splitext(original_name)
                        safe_name = f"{base[:50]}{ext}".replace(' ', '_')
                        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-', '.'))
                   
                        # Ensure unique filename
                        counter = 1
                        while os.path.exists(os.path.join(policies_dir, safe_name)):
                            safe_name = f"{base[:45]}_{counter}{ext}"
                            counter += 1
                   
                        # Save file
                        file_path = os.path.join(policies_dir, safe_name)
                        with open(file_path, 'wb+') as destination:
                            for chunk in attachment.chunks():
                                destination.write(chunk)
                   
                        # Store relative path in DB
                        attachment_path = f"policies/{safe_name}"
               
                    # Insert into database
                    cursor.execute("""
                        INSERT INTO ci_policies (
                            company_id,
                            title,
                            description,
                            attachment,
                            added_by,
                            created_at
                        ) VALUES (%s, %s, %s, %s, %s, NOW())
                    """, [
                        data["company_id"],
                        data["title"],
                        descr,
                        attachment_path,  # Will be NULL if no attachment
                        data["added_by"]
                    ])
               
                    # Get the new policy ID
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    policy_id = cursor.fetchone()[0]
                    todays_date = datetime.today()
 
               
                    # return Response({
                    #     "status": "success",
                    #     "message": "Policy created successfully",
                    #     "policy_id": policy_id,
                    #     "attachment_url": f"/media/{quote(attachment_path)}" if attachment_path else None
                    # }, status=status.HTTP_201_CREATED)
               
                    cursor.execute("""
                    UPDATE ci_policy_allocations
                    SET policy_id = CONCAT_WS(',', policy_id, %s) , allocation_date = %s
                """, [policy_id,todays_date])
 
 
                    #Get admin id
                    cursor.execute("""select id from ci_erp_users u inner join ci_staff_roles sr on u.user_role_id = sr.role_id where sr.role_name = 'Admin' order by u.id desc limit 1""")
 
                    admin_result = cursor.fetchone()
                    if not admin_result:
                        raise ValueError("No admin user found in the system")
                   
                    admin_id = admin_result[0]
 
                    # Get all employee ids
                    cursor.execute("""select id from ci_erp_users u inner join ci_staff_roles sr on u.user_role_id = sr.role_id where sr.role_name != 'Admin' """)
 
                    user_ids = cursor.fetchall()
                    # user_ids = ",".join(str(row[0]) for row in rows)
 
 
                    if user_ids:
                        notification_text = f"A new policy {data['title']} has been assigned to you!"
                       
                        # Prepare bulk insert values
                        notification_values = [
                            (admin_id, user_id[0], notification_text)
                            for user_id in user_ids
                        ]
                       
                        # Bulk insert using executemany
                        cursor.executemany("""
                            INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
                            VALUES (%s, %s, %s, NOW())
                        """, notification_values)
 
                return Response({
                    "status": "success",
                    "message": "Policy created and allocated to all employees successfully",
                    "policy_id": policy_id,
                    "attachment_url": f"/media/{quote(attachment_path)}" if attachment_path else None
                }, status=status.HTTP_201_CREATED)
               
        except Exception as e:
            # Clean up if file was saved but DB operation failed
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
                   
            return Response({
                "status": "error",
                "message": f"Failed to create policy: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # def patch(self, request, pk):
    #     data = request.data
    #     if not data:
    #         return Response({
    #             "status": "error",
    #             "message": "No data provided for update"
    #         }, status=status.HTTP_400_BAD_REQUEST)
        
    #     valid_fields = [
    #         "title", "description", "attachment", "company_id"
    #     ]
        
    #     update_fields = []
    #     update_values = []
        
    #     for field in valid_fields:
    #         if field in data:
    #             update_fields.append(f"{field} = %s")
    #             update_values.append(data[field])
        
    #     if not update_fields:
    #         return Response({
    #             "status": "error",
    #             "message": "No valid fields provided for update"
    #         }, status=status.HTTP_400_BAD_REQUEST)
        
    #     try:
    #         with connection.cursor() as cursor:
    #             # Check if policy exists
    #             cursor.execute("""
    #                 SELECT COUNT(*) FROM ci_policies WHERE policy_id = %s
    #             """, [pk])
    #             if cursor.fetchone()[0] == 0:
    #                 return Response({
    #                     "status": "error",
    #                     "message": "Policy not found"
    #                 }, status=status.HTTP_404_NOT_FOUND)
                
    #             # Prepare and execute update
    #             update_query = f"""
    #                 UPDATE ci_policies
    #                 SET {', '.join(update_fields)}
    #                 WHERE policy_id = %s
    #             """
    #             update_values.append(pk)
    #             cursor.execute(update_query, update_values)
                
    #             return Response({
    #                 "status": "success",
    #                 "message": "Policy updated successfully"
    #             }, status=status.HTTP_200_OK)
                
    #     except Exception as e:
    #         return Response({
    #             "status": "error",
    #             "message": f"Failed to update policy: {str(e)}"
    #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, pk):
        data = request.data
        if not data and not request.FILES:
            return Response({
                "status": "error",
                "message": "No data provided for update"
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_fields = ["title", "description", "attachment", "company_id"]
        update_fields = []
        update_values = []

        # Handle normal fields
        for field in valid_fields:
            if field in data and field != "attachment":  # exclude attachment for now
                update_fields.append(f"{field} = %s")
                update_values.append(data[field])

        # Handle attachment (file upload)
        attachment = request.FILES.get("attachment")
        if attachment:
            policies_dir = os.path.join(settings.MEDIA_ROOT, 'policies')
            os.makedirs(policies_dir, exist_ok=True)

            original_name = attachment.name
            base, ext = os.path.splitext(original_name)
            safe_name = f"{base[:50]}{ext}".replace(' ', '_')
            safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ('_', '-', '.'))

            counter = 1
            while os.path.exists(os.path.join(policies_dir, safe_name)):
                safe_name = f"{base[:45]}_{counter}{ext}"
                counter += 1

            file_path = os.path.join(policies_dir, safe_name)
            with open(file_path, 'wb+') as destination:
                for chunk in attachment.chunks():
                    destination.write(chunk)

            attachment_path = f"policies/{safe_name}"
            update_fields.append("attachment = %s")
            update_values.append(attachment_path)

        if not update_fields:
            return Response({
                "status": "error",
                "message": "No valid fields provided for update"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM ci_policies WHERE policy_id = %s", [pk])
                if cursor.fetchone()[0] == 0:
                    return Response({
                        "status": "error",
                        "message": "Policy not found"
                    }, status=status.HTTP_404_NOT_FOUND)

                update_query = f"""
                    UPDATE ci_policies
                    SET {', '.join(update_fields)}
                    WHERE policy_id = %s
                """
                update_values.append(pk)
                cursor.execute(update_query, update_values)

                return Response({
                    "status": "success",
                    "message": "Policy updated successfully"
                }, status=status.HTTP_200_OK)

        except Exception as e:
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

            return Response({
                "status": "error",
                "message": f"Failed to update policy: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk):
        try:
            with connection.cursor() as cursor:
                # Check if policy exists
                cursor.execute("""
                    SELECT COUNT(*) FROM ci_policies WHERE policy_id = %s
                """, [pk])
                if cursor.fetchone()[0] == 0:
                    return Response({
                        "status": "error",
                        "message": "Policy not found"
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Delete the policy
                cursor.execute("""
                    DELETE FROM ci_policies WHERE policy_id = %s
                """, [pk])
                
                return Response({
                    "status": "success",
                    "message": "Policy deleted successfully"
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Failed to delete policy: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AcknowledgePolicyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, policy_id=None):
        with connection.cursor() as cursor:
            # Base query
            query = """
                SELECT 
                    pa.policies_acknow_id,
                    pa.policy_id,
                    p.title AS policy_title,
                    p.attachment,
                    pa.emp_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    pa.acknowledge,
                    pa.is_policy_view,
                    pa.created_date AS acknowledged_date
                FROM ci_policies_acknowledge pa
                JOIN ci_policies p ON pa.policy_id = p.policy_id
                JOIN ci_erp_users_details ud ON pa.emp_id = ud.employee_id
                JOIN ci_erp_users u ON ud.user_id = u.id
            """

            params = []
            if policy_id:
                query += " WHERE pa.policy_id = %s"
                params.append(policy_id)

            query += " ORDER BY pa.policy_id ASC"

            cursor.execute(query, params)
            rows = dictfetchall(cursor)

        return Response({
            "message": "Policy acknowledgements retrieved successfully",
            "data": rows
        }, status=status.HTTP_200_OK)


# Add this utility function here
def dictfetchall(cursor):
    """
    Return all rows from a cursor as a list of dicts.
    Each row will be a dictionary with column names as keys.
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]






def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]





class PolicyDashboardView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with connection.cursor() as cursor:
            # cursor.execute("""
            #     SELECT 
            #         ud.employee_id AS employee_code,
            #         CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
            #         u.id AS user_id,
            #         COUNT(pa.policy_id) AS total_policies,
            #         SUM(CASE WHEN pa.acknowledge = 'Y' THEN 1 ELSE 0 END) AS acknowledged_count,
            #         MAX(pa.created_date) AS last_acknowledge_date
            #     FROM ci_policies_acknowledge pa
            #     JOIN ci_erp_users_details ud ON pa.emp_id = ud.employee_id
            #     JOIN ci_erp_users u ON ud.user_id = u.id
            #     GROUP BY ud.employee_id, u.first_name, u.last_name, u.id
            #     HAVING COUNT(pa.policy_id) > 0
            #     ORDER BY u.first_name
            # """)
            
            # cursor.execute("""
            #     SELECT 
            #         ud.employee_id AS employee_code,
            #         CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
            #         u.id AS user_id,
            #         (CHAR_LENGTH(alloc.policy_id) - CHAR_LENGTH(REPLACE(alloc.policy_id, ',', ''))) AS total_policies,
            #         SUM(CASE WHEN pa.acknowledge = 'Y' THEN 1 ELSE 0 END) AS acknowledged_count,
            #         MAX(pa.created_date) AS last_acknowledge_date
            #     FROM ci_policy_allocations alloc
            #     JOIN ci_erp_users_details ud ON alloc.emp_id = ud.employee_id
            #     JOIN ci_erp_users u ON ud.user_id = u.id
            #     LEFT JOIN ci_policies_acknowledge pa ON FIND_IN_SET(CONVERT(pa.policy_id USING utf8mb4), CONVERT(alloc.policy_id USING utf8mb4)) > 0
            #         AND CONVERT(alloc.emp_id USING utf8mb4) = CONVERT(pa.emp_id USING utf8mb4)
            #     GROUP BY ud.employee_id, u.first_name, u.last_name, u.id, alloc.policy_id
            #     HAVING total_policies > 0
            #     ORDER BY u.first_name;  
            # """)
#             cursor.execute("""
                           
#                            SELECT 
#     ud.employee_id AS employee_code,
#     CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#     u.id AS user_id,

#     CASE 
#         WHEN alloc.policy_id IS NULL OR TRIM(alloc.policy_id) = '' THEN 0
#         ELSE (
#             LENGTH(REPLACE(TRIM(BOTH ',' FROM REPLACE(REPLACE(alloc.policy_id, ',,', ','), ',,', ',')), ',', '')) 
#             > 0
#         ) + 
#         (LENGTH(TRIM(BOTH ',' FROM REPLACE(REPLACE(alloc.policy_id, ',,', ','), ',,', ','))) 
#         - LENGTH(REPLACE(TRIM(BOTH ',' FROM REPLACE(REPLACE(alloc.policy_id, ',,', ','), ',,', ',')), ',', '')))
#     END AS total_policies,

#     SUM(CASE WHEN pa.acknowledge = 'Y' THEN 1 ELSE 0 END) AS acknowledged_count,
#     MAX(pa.created_date) AS last_acknowledge_date

# FROM ci_policy_allocations alloc
# JOIN ci_erp_users_details ud ON alloc.emp_id = ud.employee_id
# JOIN ci_erp_users u ON ud.user_id = u.id
# LEFT JOIN ci_policies_acknowledge pa 
#     ON FIND_IN_SET(CONVERT(pa.policy_id USING utf8mb4), CONVERT(alloc.policy_id USING utf8mb4)) > 0
#     AND CONVERT(alloc.emp_id USING utf8mb4) = CONVERT(pa.emp_id USING utf8mb4)
# where u.is_active = 1
# GROUP BY ud.employee_id, u.first_name, u.last_name, u.id, alloc.policy_id
# HAVING total_policies > 0
# ORDER BY u.first_name;                          
#                            """)

            cursor.execute("""
                           
                           SELECT 
    ud.employee_id AS employee_code,
    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    u.id AS user_id,

    CASE 
        WHEN alloc.policy_id IS NULL OR TRIM(alloc.policy_id) = '' THEN 0
        ELSE (
            LENGTH(TRIM(BOTH ',' FROM REPLACE(REPLACE(alloc.policy_id, ',,', ','), ',,', ','))) 
            - LENGTH(REPLACE(TRIM(BOTH ',' FROM REPLACE(REPLACE(alloc.policy_id, ',,', ','), ',,', ',')), ',', '')) 
            + 1
        )
    END AS total_policies,

    SUM(CASE WHEN pa.acknowledge = 'Y' THEN 1 ELSE 0 END) AS acknowledged_count,
    MAX(pa.created_date) AS last_acknowledge_date

FROM ci_policy_allocations alloc
JOIN ci_erp_users_details ud ON alloc.emp_id = ud.employee_id
JOIN ci_erp_users u ON ud.user_id = u.id
LEFT JOIN ci_policies_acknowledge pa 
    ON FIND_IN_SET(CONVERT(pa.policy_id USING utf8mb4), CONVERT(alloc.policy_id USING utf8mb4)) > 0
    AND CONVERT(alloc.emp_id USING utf8mb4) = CONVERT(pa.emp_id USING utf8mb4)
WHERE u.is_active = 1
GROUP BY ud.employee_id, u.first_name, u.last_name, u.id, alloc.policy_id
ORDER BY u.first_name;
                          
                           """)
            
            rows = dictfetchall(cursor)

        acknowledged = []
        not_acknowledged = []
        partially_acknowledged = []

        for row in rows:
            total = row["total_policies"]
            ack = row["acknowledged_count"]

            if ack == total:
                ack_status = "Acknowledged"
                acknowledged.append(row)
            elif ack == 0:
                ack_status = "Not Acknowledged"
                not_acknowledged.append(row)
            else:
                ack_status = "Partially Acknowledged"
                partially_acknowledged.append(row)

            row["status"] = ack_status  

        return Response({
            "message": "Employee policy acknowledgement status",
            "acknowledged": acknowledged,
            "not_acknowledged": not_acknowledged,
            "partially_acknowledged": partially_acknowledged
        }, status=status.HTTP_200_OK)





def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class PolicyAcknowledgementDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # def get(self, request, employee_id):
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT 
    #                 ud.employee_id AS employee_code,
    #                 CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    #                 p.policy_id,
    #                 p.title AS policy_name,
    #                 CASE 
    #                     WHEN pa.acknowledge = 'Y' THEN 'Acknowledged'
    #                     ELSE 'Not Acknowledged'
    #                 END AS status,
    #                 pa.created_date AS acknowledge_date
    #             FROM ci_policies_acknowledge pa
    #             LEFT JOIN ci_policies p ON pa.policy_id = p.policy_id
    #             INNER JOIN ci_erp_users_details ud ON pa.emp_id = ud.employee_id
    #             INNER JOIN ci_erp_users u ON ud.user_id = u.id
    #             WHERE pa.emp_id = %s
    #             ORDER BY p.title
    #         """, [employee_id])

    #         policy_details = dictfetchall(cursor)

        
    #     def format_date(dt):
    #         return dt

    #     for row in policy_details:
    #         row["acknowledge_date"] = format_date(row.get("acknowledge_date"))

    #     if not policy_details:
    #         return Response({
    #             "message": "No assigned policies found for this employee."
    #         }, status=status.HTTP_404_NOT_FOUND)

    #     return Response({
    #         "message": "Assigned policy acknowledgement details for employee",
    #         "data": policy_details
    #     }, status=status.HTTP_200_OK)
    
    def get(self, request, employee_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    ud.employee_id AS employee_code,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    p.policy_id,
                    p.title AS policy_name,
                    CASE WHEN pa.acknowledge = 'Y' THEN 'Acknowledged' ELSE 'Pending' END AS status,
                    pa.created_date AS acknowledge_date
                FROM ci_policy_allocations a
                INNER JOIN ci_erp_users_details ud ON a.emp_id = ud.employee_id
                INNER JOIN ci_erp_users u ON ud.user_id = u.id
                INNER JOIN ci_policies p ON FIND_IN_SET(p.policy_id, REPLACE(a.policy_id, ' ', ''))
                LEFT JOIN ci_policies_acknowledge pa 
                    ON pa.policy_id = p.policy_id AND pa.emp_id = a.emp_id
                WHERE a.emp_id = %s
                ORDER BY p.title
            """, [employee_id])

            policy_details = dictfetchall(cursor)

        if not policy_details:
            return Response({
                "message": "No assigned policies found for this employee."
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Separate acknowledged & pending
        acknowledged = [p for p in policy_details if p["status"] == "Acknowledged"]
        pending = [p for p in policy_details if p["status"] == "Pending"]

        # ✅ All policies with status
        all_policies = [
            {
                "policy_name": p["policy_name"],
                "status": p["status"],
                "acknowledge_date": p["acknowledge_date"]
            } for p in policy_details
        ]

        return Response({
            "message": "Policy acknowledgement details for employee",
            "employee_id": policy_details[0]["employee_code"],
            "employee_name": policy_details[0]["employee_name"],

            # ✅ Show all policies with their status first
            "all_policies": all_policies,

            # ✅ Keep previous splits
            "acknowledged_policies": [
                {
                    "policy_name": p["policy_name"],
                    "acknowledge_date": p["acknowledge_date"]
                } for p in acknowledged
            ],
            "pending_policies": [
                {"policy_name": p["policy_name"]}
                for p in pending
            ],

            # ✅ Summary
            "summary": {
                "total_policies": len(policy_details),
                "acknowledged_count": len(acknowledged),
                "pending_count": len(pending)
            }
        }, status=status.HTTP_200_OK)





class EmployeePolicyDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, emp_id):
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    pa.emp_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    p.title AS policy_name,
                    pa.created_date AS acknowledged_date,
                    pa.acknowledge
                FROM ci_policies_acknowledge pa
                JOIN ci_policies p ON pa.policy_id = p.policy_id
                JOIN ci_erp_users_details ud ON pa.emp_id = ud.employee_id
                JOIN ci_erp_users u ON ud.user_id = u.id
                WHERE pa.emp_id = %s
                ORDER BY pa.created_date ASC
            """
            cursor.execute(query, [emp_id])
            rows = dictfetchall(cursor)

        return Response({
            "message": f"Policy acknowledgment details for employee ID {emp_id}",
            "data": rows
        }, status=status.HTTP_200_OK)





class AnnouncementListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.announcement_id,
                    a.title,
                    dpt.department_name,
                    a.description,
                    a.start_date,
                    a.end_date
                FROM ci_announcements a
                LEFT JOIN ci_departments dpt ON a.department_id = dpt.department_id
                GROUP BY a.announcement_id, a.title, dpt.department_name, a.description
            """)
            rows = dictfetchall(cursor)
        return Response({"message": "Announcements retrieved successfully", "data": rows}, status=status.HTTP_200_OK)


    def post(self, request):
        data = request.data
        company_id = 2

        # department_name
        if "department_name" not in data:
            return Response({"message": "Missing field: department_name"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("SELECT department_id FROM ci_departments WHERE department_name = %s", [data["department_name"]])
            dept_row = cursor.fetchone()
            if not dept_row:
                return Response({"message": "Invalid department_name"}, status=status.HTTP_400_BAD_REQUEST)
            department_id = dept_row[0]

        required_fields = ["title", "start_date", "end_date", "summary", "description"]
        for field in required_fields:
            if field not in data:
                return Response({"message": f"Missing field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_announcements (
                    company_id, department_id, title, start_date, end_date,
                     summary, description, is_active, created_at
                ) VALUES ( %s, %s, %s, %s, %s, %s, %s, 1, NOW())
            """, [
                company_id,
                department_id,
                data["title"],
                data["start_date"],
                data["end_date"],
                data["summary"],
                data["description"]
            ])

        return Response({"message": "Announcement created successfully"}, status=status.HTTP_201_CREATED)

    def patch(self, request, announcement_id):
        data = request.data
        if not data:
            return Response({"message": "No data provided for update"}, status=status.HTTP_400_BAD_REQUEST)
 
        valid_fields = [
            "title", "department_id", "start_date", "end_date",
            "summary", "description",  "employee_id"
        ]
 
        update_fields = []
        update_values = []
 
        for field in valid_fields:
            if field in data:
                value = data[field]
                if field == "employee_id":
                    # Expecting a list, convert to comma-separated string
                    if not isinstance(value, list):
                        return Response({"message": "employee_id must be a list of IDs"}, status=status.HTTP_400_BAD_REQUEST)
                    value = ",".join(str(emp_id) for emp_id in value)
                update_fields.append(f"{field} = %s")
                update_values.append(value)
 
        if not update_fields:
            return Response({"message": "No valid fields provided for update"}, status=status.HTTP_400_BAD_REQUEST)
 
        update_query = f"""
            UPDATE ci_announcements
            SET {', '.join(update_fields)}
            WHERE announcement_id = %s
        """
 
        update_values.append(announcement_id)
 
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT COUNT(*) FROM ci_announcements WHERE announcement_id = %s", [announcement_id])
            if cursor.fetchone()[0] == 0:
                return Response({"message": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)
 
           
            cursor.execute(update_query, update_values)
 
        return Response({"message": "Announcement updated successfully"}, status=status.HTTP_200_OK)
 
 
    def delete(self, request, announcement_id):
        if not announcement_id:
            return Response({"message": "announcement_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT COUNT(*) FROM ci_announcements WHERE announcement_id = %s", [announcement_id])
            count = cursor.fetchone()[0]
            if count == 0:
                return Response({"message": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)
 
            
            cursor.execute("DELETE FROM ci_announcements WHERE announcement_id = %s", [announcement_id])
 
        return Response({"message": "Announcement deleted from database successfully"}, status=status.HTTP_200_OK)
       
 



# class DepartmentView(APIView):

#     def get(self, request, format=None):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     d.department_id,
#                     d.department_name,
#                     d.department_code,
#                     d.company_id,
#                     d.department_head,
#                     CONCAT(u.first_name, ' ', IFNULL(u.middle_name, ''), ' ', u.last_name) AS department_head_name,
#                     d.added_by,
#                     d.created_at
#                 FROM ci_departments d
#                 LEFT JOIN ci_erp_users_details ud ON ud.employee_id = d.department_head
#                 LEFT JOIN ci_erp_users u ON u.id = ud.user_id
#             """)
#             columns = [col[0] for col in cursor.description]
#             data = [dict(zip(columns, row)) for row in cursor.fetchall()]
#         return Response(data)

#     def post(self, request, format=None):
#         data = request.data
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO ci_departments 
#                 (department_name, department_code, company_id, department_head, added_by, created_at)
#                 VALUES (%s, %s, %s, %s, %s, NOW())
#             """, [
#                 data.get('department_name'),
#                 data.get('department_code'),
#                 data.get('company_id', 2),
#                 data.get('department_head'),
#                 data.get('added_by', 2),
#             ])
#         return Response({"message": "Department created successfully"}, status=status.HTTP_201_CREATED)

#     def patch(self, request, pk, format=None):
#         data = request.data
#         fields = []
#         values = []

#         for field in ['department_name', 'department_code', 'company_id', 'department_head', 'added_by']:
#             if field in data:
#                 fields.append(f"{field} = %s")
#                 values.append(data[field])

#         if not fields:
#             return Response({"error": "No valid fields provided"}, status=status.HTTP_400_BAD_REQUEST)

#         values.append(pk)

#         with connection.cursor() as cursor:
#             cursor.execute(f"""
#                 UPDATE ci_departments
#                 SET {', '.join(fields)}
#                 WHERE department_id = %s
#             """, values)

#         return Response({"message": "Department updated successfully"}, status=status.HTTP_200_OK)

#     def delete(self, request, pk, format=None):
#         with connection.cursor() as cursor:
#             cursor.execute("DELETE FROM ci_departments WHERE department_id = %s", [pk])
#         return Response({"message": "Department deleted successfully"}, status=status.HTTP_200_OK)




class CiBiomatricDataListCreateView(generics.ListCreateAPIView):
    queryset = CiBiomatricData.objects.all()
    serializer_class = CiBiomatricDataSerializer

class CiBiomatricDataRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CiBiomatricData.objects.all()
    serializer_class = CiBiomatricDataSerializer
    lookup_field = "ci_biomatric_id"


class ContractOptionAPIView(APIView):

    def get(self, request):
        contracts = ContractOption.objects.all()
        serializer = ContractOptionSerializer(contracts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContractOptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .models import BasicInformation
from .serializers import BasicInformationSerializer


class BasicInformationListAPIView(APIView):
    queryset = BasicInformation.objects.all()
    serializer_class = BasicInformationSerializer
    permission_classes = [AllowAny]



class BasicInformation(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        user_id = request.GET.get("user_id")

        if not user_id:
            return Response(
                {"status": "Error", "Message": "user id is required"}, status=400
            )

        try:
            with connection.cursor() as c:

                query = """SELECT 
                                user_id,
                                first_name,
                                middle_name,
                                last_name,
                                contact_number,
                                gender,
                                employee_id,
                                date_of_birth,
                                marital_status,
                                state,
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
                            WHERE
                                id = %s;"""

                c.execute(query, [user_id])
                columns = [col[0] for col in c.description]
                data = [dict(zip(columns, row)) for row in c.fetchone()]

            return Response(
                {"status": "success", "data": data}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occured: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):

        data = request.data.get("data")





class EventViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    e.event_id,
                    e.employee_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    e.company_id,
                    e.event_title,
                    e.event_date,
                    e.event_time,
                    e.event_color,
                    e.event_note,
                    e.created_at
                FROM 
                    ci_events e
                LEFT JOIN 
                    ci_erp_users_details ud ON e.employee_id = ud.employee_id
                LEFT JOIN 
                    ci_erp_users u ON ud.user_id = u.id
                ORDER BY 
                    e.created_at DESC
            """)
            rows = cursor.fetchall()

        columns = [
            "event_id", "employee_id", "employee_name", "company_id", "event_title",
            "event_date", "event_time", "event_color", "event_note", "created_at"
        ]
        data = [dict(zip(columns, row)) for row in rows]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_events 
                        (employee_id, company_id, event_title, event_date, event_time, 
                         event_color, event_note, created_at)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data["employee_id"],
                    data.get("company_id", 2),
                    data["event_title"],
                    data["event_date"],
                    data["event_time"],
                    data["event_color"],
                    data["event_note"],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ])
            return Response({"message": "Event created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, event_id=None):
        data = request.data
        update_fields = []
        params = []

        for field in ["employee_id", "company_id", "event_title", "event_date", "event_time", "event_color", "event_note"]:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])

        if not update_fields:
            return Response({"error": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

        params.append(event_id)

        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE ci_events
                SET {', '.join(update_fields)}
                WHERE event_id = %s
            """, params)

        return Response({"message": "Event updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, event_id=None):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ci_events WHERE event_id = %s", [event_id])
        return Response({"message": "Event deleted successfully"}, status=status.HTTP_200_OK)
 



class EmployeeEventView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, employee_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        event_title,
                        event_date,
                        event_time
                    FROM 
                        ci_events
                    WHERE 
                        employee_id = %s
                    ORDER BY 
                        event_date ASC, event_time ASC
                """, [employee_id])

                rows = cursor.fetchall()

            columns = ["event_title", "event_date", "event_time"]
            data = [dict(zip(columns, row)) for row in rows]
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
 

class CITravelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, travel_id=None):
        with connection.cursor() as cursor:
            if travel_id:
                cursor.execute("""
                    SELECT 
                        t.travel_id,
                        t.company_id,
                        t.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        t.start_date,
                        t.end_date,
                        t.associated_goals,
                        t.visit_purpose,
                        t.visit_place,
                        tm.category_name AS travel_mode,
                        at.category_name AS arrangement_type,
                        t.expected_budget,
                        t.actual_budget,
                        t.description,
                        t.status,
                        t.added_by,
                        t.created_at
                    FROM 
                        ci_travels t
                    LEFT JOIN ci_erp_users_details ud ON t.employee_id = ud.employee_id
                    LEFT JOIN ci_erp_users u ON ud.user_id = u.id
                    LEFT JOIN ci_erp_constants tm ON tm.constants_id = t.travel_mode AND tm.type = 'travel_mood'
                    LEFT JOIN ci_erp_constants at ON at.constants_id = t.arrangement_type AND at.type = 'arrangement_type'
                    WHERE 
                        t.travel_id = %s
                """, [travel_id])
                row = cursor.fetchone()

                if not row:
                    return Response({"error": "Travel not found"}, status=404)

                columns = [
                    "travel_id", "company_id", "employee_id", "employee_name", "start_date",
                    "end_date", "associated_goals", "visit_purpose", "visit_place",
                    "travel_mode", "arrangement_type", "expected_budget", "actual_budget",
                    "description", "status", "added_by", "created_at"
                ]
                data = dict(zip(columns, row))
                return Response({"message": "Travel fetched successfully", "data": data})
            
            else:
                cursor.execute("""
                    SELECT 
                        t.travel_id,
                        t.company_id,
                        t.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        t.start_date,
                        t.end_date,
                        t.associated_goals,
                        t.visit_purpose,
                        t.visit_place,
                        tm.category_name AS travel_mode,
                        at.category_name AS arrangement_type,
                        t.expected_budget,
                        t.actual_budget,
                        t.description,
                        t.status,
                        t.added_by,
                        t.created_at
                    FROM 
                        ci_travels t
                    LEFT JOIN ci_erp_users_details ud ON t.employee_id = ud.employee_id
                    LEFT JOIN ci_erp_users u ON ud.user_id = u.id
                    LEFT JOIN ci_erp_constants tm ON tm.constants_id = t.travel_mode AND tm.type = 'travel_mode'
                    LEFT JOIN ci_erp_constants at ON at.constants_id = t.arrangement_type AND at.type = 'arrangement_type'
                    ORDER BY 
                        t.created_at DESC
                """)
                rows = cursor.fetchall()

                columns = [
                    "travel_id", "company_id", "employee_id", "employee_name", "start_date",
                    "end_date", "associated_goals", "visit_purpose", "visit_place",
                    "travel_mode", "arrangement_type", "expected_budget", "actual_budget",
                    "description", "status", "added_by", "created_at"
                ]
                data = [dict(zip(columns, row)) for row in rows]
                return Response({"message": "All travels fetched successfully", "data": data})


    def post(self, request):
        data = request.data
        company_id = 2  # default or get from request if you want

        travel_mode_name = data.get("travel_mode")
        arrangement_type_name = data.get("arrangement_type")
        employee_id = data.get("employee_id")
        employee_name = data.get("employee_name")

        if not travel_mode_name or not arrangement_type_name:
            return Response({"error": "travel_mode and arrangement_type are required."}, status=400)

        with connection.cursor() as cursor:
            # Lookup travel_mode id by name
            cursor.execute("""
                SELECT constants_id FROM ci_erp_constants 
                WHERE type = 'travel_mode' AND category_name = %s AND company_id = %s
            """, [travel_mode_name, company_id])
            travel_mode_row = cursor.fetchone()
            if not travel_mode_row:
                return Response({"error": f"Invalid travel_mode name: {travel_mode_name}"}, status=400)
            travel_mode_id = travel_mode_row[0]

            # Lookup arrangement_type id by name
            cursor.execute("""
                SELECT constants_id FROM ci_erp_constants 
                WHERE type = 'arrangement_type' AND category_name = %s AND company_id = %s
            """, [arrangement_type_name, company_id])
            arrangement_type_row = cursor.fetchone()
            if not arrangement_type_row:
                return Response({"error": f"Invalid arrangement_type name: {arrangement_type_name}"}, status=400)
            arrangement_type_id = arrangement_type_row[0]


            if not employee_id and employee_name:
                cursor.execute("""
                    SELECT ud.employee_id FROM ci_erp_users u
                    JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    WHERE CONCAT(u.first_name, ' ', u.last_name) = %s
                """, [employee_name])
                emp_row = cursor.fetchone()
                if not emp_row:
                    return Response({"error": f"Employee name '{employee_name}' not found."}, status=400)
                employee_id = emp_row[0]


            if employee_id and not employee_name:
                cursor.execute("""
                    SELECT CONCAT(u.first_name, ' ', u.last_name) FROM ci_erp_users_details ud
                    JOIN ci_erp_users u ON ud.user_id = u.id
                    WHERE ud.employee_id = %s
                """, [employee_id])
                emp_name_row = cursor.fetchone()
                if not emp_name_row:
                    return Response({"error": f"Employee id '{employee_id}' not found."}, status=400)
                employee_name = emp_name_row[0]

            if not employee_id:
                return Response({"error": "Employee ID or Employee Name must be provided."}, status=400)


            start_date = data.get("start_date")
            end_date = data.get("end_date")
            associated_goals = data.get("associated_goals")
            visit_purpose = data.get("visit_purpose")
            visit_place = data.get("visit_place")
            expected_budget = data.get("expected_budget")
            actual_budget = data.get("actual_budget")
            description = data.get("description")
            status = data.get("status")
            added_by = data.get("added_by")
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO ci_travels (
                    company_id, employee_id, start_date, end_date, associated_goals,
                    visit_purpose, visit_place, travel_mode, arrangement_type,
                    expected_budget, actual_budget, description, status,
                    added_by, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                company_id, employee_id, start_date, end_date, associated_goals,
                visit_purpose, visit_place, travel_mode_id, arrangement_type_id,
                expected_budget, actual_budget, description, status,
                added_by, created_at
            ])

            travel_id = cursor.lastrowid

            response_data = {
                "travel_id": travel_id,
                "company_id": company_id,
                "employee_id": employee_id,
                "employee_name": employee_name,
                "start_date": start_date,
                "end_date": end_date,
                "associated_goals": associated_goals,
                "visit_purpose": visit_purpose,
                "visit_place": visit_place,
                "travel_mode": {
                    "id": travel_mode_id,
                    "name": travel_mode_name
                },
                "arrangement_type": {
                    "id": arrangement_type_id,
                    "name": arrangement_type_name
                },
                "expected_budget": expected_budget,
                "actual_budget": actual_budget,
                "description": description,
                "status": status,
                "added_by": added_by,
                "created_at": created_at,
            }

        return Response({"message": "Travel created successfully", "data": response_data}, status=201)

    def patch(self, request, travel_id):
        data = request.data


        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ci_travels WHERE travel_id = %s", [travel_id])
            if cursor.fetchone()[0] == 0:
                return Response({"error": "Travel not found"}, status=404)


        employee_id = data.get("employee_id")
        employee_name = data.get("employee_name")
        if not employee_id and employee_name:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ud.employee_id
                    FROM ci_erp_users u
                    JOIN ci_erp_users_details ud ON u.id = ud.user_id
                    WHERE CONCAT(u.first_name, ' ', u.last_name) = %s
                """, [employee_name])
                result = cursor.fetchone()
                if not result:
                    return Response({"error": "Invalid employee name"}, status=400)
                employee_id = result[0]


        travel_mode = data.get("travel_mode")
        if travel_mode:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT constants_id FROM ci_erp_constants
                    WHERE category_name = %s AND type = 'travel_mode'
                """, [travel_mode])
                result = cursor.fetchone()
                if not result:
                    return Response({"error": "Invalid travel mode"}, status=400)
                travel_mode = result[0]


        arrangement_type = data.get("arrangement_type")
        if arrangement_type:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT constants_id FROM ci_erp_constants
                    WHERE category_name = %s AND type = 'arrangement_type'
                """, [arrangement_type])
                result = cursor.fetchone()
                if not result:
                    return Response({"error": "Invalid arrangement type"}, status=400)
                arrangement_type = result[0]


        update_fields = []
        update_values = []

        fields_map = {
            "company_id": "company_id",
            "start_date": "start_date",
            "end_date": "end_date",
            "associated_goals": "associated_goals",
            "visit_purpose": "visit_purpose",
            "visit_place": "visit_place",
            "expected_budget": "expected_budget",
            "actual_budget": "actual_budget",
            "description": "description",
            "status": "status",
            "added_by": "added_by",
            "created_at": "created_at"
        }

        if employee_id:
            update_fields.append("employee_id = %s")
            update_values.append(employee_id)
        if travel_mode:
            update_fields.append("travel_mode = %s")
            update_values.append(travel_mode)
        if arrangement_type:
            update_fields.append("arrangement_type = %s")
            update_values.append(arrangement_type)

        for key, column in fields_map.items():
            if key in data:
                update_fields.append(f"{column} = %s")
                update_values.append(data[key])

        if not update_fields:
            return Response({"error": "No valid fields to update"}, status=400)

        update_values.append(travel_id)

        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE ci_travels
                SET {", ".join(update_fields)}
                WHERE travel_id = %s
            """, update_values)

        return Response({"message": "Travel updated successfully"}, status=200)

    def delete(self, request, travel_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ci_travels WHERE travel_id = %s", [travel_id])
            if cursor.rowcount == 0:
                return Response({'message': 'Travel not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'message': 'Travel deleted successfully'}, status=status.HTTP_200_OK)



####  EMPLOYEE SECTION 
class BasicInformation(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        user_id = request.GET.get("user_id")

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
    state,
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




class NewHolidayView(APIView):
    def get(self, request, employee_id):
        try:
            with connection.cursor() as cursor:
                # Step 1: Get user_id from employee_id
                cursor.execute("""
                    SELECT user_id FROM ci_erp_users_details
                    WHERE employee_id = %s
                """, [employee_id])
                user_row = cursor.fetchone()

                if not user_row:
                    return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

                user_id = user_row[0]

                # Step 2: Get state and country ID from ci_erp_users
                cursor.execute("""
                    SELECT state, country FROM ci_erp_users
                    WHERE id = %s
                """, [user_id])
                location = cursor.fetchone()

                if not location:
                    return Response({"error": "User details not found."}, status=status.HTTP_404_NOT_FOUND)

                state_id, country_id = location

                # Step 3: Get state and country names from ci_erp_constants
                cursor.execute("""
                    SELECT 
                        MAX(CASE WHEN type = 'state' THEN category_name END) AS state_name,
                        MAX(CASE WHEN type = 'country' THEN category_name END) AS country_name
                    FROM ci_erp_constants
                    WHERE constants_id IN (%s, %s)
                """, [state_id, country_id])
                names_row = cursor.fetchone()

                state_name, country_name = names_row

                # Step 4: Fetch holidays with matching state and country, and resolve names via join
                cursor.execute("""
                    SELECT 
                        h.event_name,
                        h.start_date,
                        h.end_date,
                        c_country.category_name AS country_name,
                        c_state.category_name AS state_name
                    FROM ci_holidays h
                    LEFT JOIN ci_erp_constants c_state ON h.state = c_state.constants_id AND c_state.type = 'state'
                    LEFT JOIN ci_erp_constants c_country ON h.country = c_country.constants_id AND c_country.type = 'country'
                    WHERE h.state = %s AND h.country = %s
                    ORDER BY h.start_date ASC
                """, [state_id, country_id])

                holidays = cursor.fetchall()

            data = [
                {
                    "event_title": row[0],
                    "start_date": row[1],
                    "end_date": row[2],
                    "country": row[3],
                    "state": row[4],
                }
                for row in holidays
            ]

            return Response(data)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class Payroll(APIView):

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


class Policies(APIView):

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



from .models import CITraining
from .serializers import CITrainingSerializer
 
class CITrainingView(APIView):
    permission_classes = [IsAuthenticated]
 
 
    def get(self, request):
        trainings = CITraining.objects.all()
        serializer = CITrainingSerializer(trainings, many=True)
        return Response({
            "message": "Training data fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
 
    def post(self, request):
        serializer = CITrainingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Training created successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Error creating training.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
class CITrainingDetailView(APIView):
    permission_classes = [IsAuthenticated]
 
    def patch(self, request, pk):
        try:
            training = CITraining.objects.get(pk=pk)
        except CITraining.DoesNotExist:
            return Response({"message": "Training not found."}, status=status.HTTP_404_NOT_FOUND)
 
        serializer = CITrainingSerializer(training, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Training updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Error updating training.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pk):
        try:
            training = CITraining.objects.get(pk=pk)
        except CITraining.DoesNotExist:
            return Response({"message": "Training not found."}, status=status.HTTP_404_NOT_FOUND)
 
        training.delete()
        return Response({"message": "Training deleted successfully."}, status=status.HTTP_200_OK)
        

# class AdminDashboard(APIView):

#     def get(self, request):
#         today = date.today()
#         try:
#             with connection.cursor() as c:
#                 # Basic counts
#                 c.execute("""SELECT COUNT(*) FROM ci_erp_users""")
#                 emp_count = c.fetchone()[0]
 
#                 c.execute("""
#                     SELECT
#                         SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
#                         SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive_count
#                     FROM ci_erp_users
#                 """)
#                 row = c.fetchone()
#                 emp_count_active = row[0]
#                 emp_count_inactive = row[1]
                
#                 c.execute("""SELECT COUNT(*) FROM ci_projects""")
#                 project_count = c.fetchone()[0]

#                 c.execute("""SELECT COUNT(*) FROM ci_tasks""")
#                 task_count = c.fetchone()[0]

#                 # Leaves with today's from_date
#                 # Ongoing leaves (covering today) for active employees, distinct count
#                 c.execute("""
#                     SELECT COUNT(DISTINCT u.id)
#                     FROM ci_leave_applications la
#                     INNER JOIN ci_erp_users_details ud
#                         ON la.employee_id = ud.employee_id
#                     INNER JOIN ci_erp_users u
#                         ON ud.user_id = u.id AND u.is_active = 1
#                     WHERE la.from_date <= CURDATE()
#                     AND la.to_date >= CURDATE()
                   
#                 """)
#                 leave_count = c.fetchone()[0]

                # # Department-wise count
                # c.execute("""
                #     SELECT d.department_name, COUNT(*) 
                #     FROM ci_erp_users u 
                #     LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id 
                #     LEFT JOIN ci_departments d ON ud.department_id = d.department_id 
                #     GROUP BY ud.department_id, d.department_name
                # """)
                # rows = c.fetchall()
                # dept_count = [{
                #     "dept_name": row[0],
                #     "dept_count": row[1],
                # } for row in rows]

                # # Designation-wise count
                # c.execute("""
                #     SELECT d.designation_name, COUNT(*) 
                #     FROM ci_erp_users u 
                #     LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id 
                #     LEFT JOIN ci_designations d ON ud.designation_id = d.designation_id 
                #     GROUP BY ud.designation_id, d.designation_name
                # """)
                # designation_results = c.fetchall()
                # desig_count = [{
                #     "desig_name": row[0],
                #     "desig_count": row[1],
                # } for row in designation_results]

#                 # Project-wise status
#                 c.execute("""SELECT status, COUNT(*) FROM ci_projects GROUP BY status""")
#                 project_statuss = c.fetchall()
#                 project_status = [{
#                     "project_status": row[0],
#                     "project_count": row[1],
#                 } for row in project_statuss]

#                 # Task-wise status
#                 c.execute("""SELECT task_status, COUNT(*) FROM ci_tasks GROUP BY task_status""")
#                 task_statuss = c.fetchall()
#                 task_status = [{
#                     "task_status": row[0],
#                     "task_count": row[1],
#                 } for row in task_statuss]

#                 # 🔄 Updated active_employees using ci_biomatric_data
#                 c.execute("""
#                     SELECT 
#                         ud.employee_id, 
#                         CONCAT(u.first_name, ' ', u.last_name) AS emp_name,
#                         'Present' AS attendance_status,
#                         b.clock_in
#                     FROM 
#                         ci_biomatric_data b
#                     INNER JOIN 
#                         ci_erp_users u ON b.userid = u.id
#                     INNER JOIN 
#                         ci_erp_users_details ud ON u.id = ud.user_id
#                     WHERE 
#                         DATE(b.attendance_date) = CURDATE()
#                     AND 
#                         b.clock_in IS NOT NULL
#                     AND 
#                         u.is_active = 1
#                     ORDER BY 
#                         b.clock_in ASC
#                 """)
#                 rows = c.fetchall()
#                 active_employees = [{
#                     "employee_id": row[0],
#                     "employee_name": row[1],
#                     "status": row[2],
#                     "punch_in": row[3]
#                 } for row in rows]

#             return Response({
#                 "status": "success",
#                 "emp_count": emp_count,
#                 "emp_count_active": emp_count_active,
#                 "emp_count_inactive": emp_count_inactive,
#                 "project_count": project_count,
#                 "task_count": task_count,
#                 "leave_count": leave_count,
#                 "dept_count": dept_count,
#                 "desig_count": desig_count,
#                 "project_status": project_status,
#                 "task_status": task_status,
#                 "active_employees": active_employees
#             }, status=200)

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": f"An error occurred: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

         
# class AdminDashboard(APIView):
 
#     def get(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 #  Fetch Revenue Data
#                 cursor.execute("""
#                     SELECT
#                         revenue_id,
#                         MONTHNAME(STR_TO_DATE(month, '%m')) AS month_name,
#                         year, total_revenue,
#                         employee_contribution, average, total_salary, fixed_cost_employee,
#                         total_cost_employee, monthly_total_salary, monthly_expenses,
#                         total_employee_cost, per_employee_cost, per_revenue, exceptional,
#                         exceeds_expectations, meet_expectations, below_expectations,
#                         unsatisfactory, department_attrition_rate, division_attrition_rate,
#                         opened_recruitment_tracker, filed_recruitment_tracker,
#                         in_process_recruitment_tracker, level1_employee, level2_employee,
#                         level3_employee, level4_employee, created_at
#                     FROM ci_revenue
#                     WHERE (year = YEAR(CURRENT_DATE - INTERVAL 1 MONTH)
#                     AND month = MONTH(CURRENT_DATE - INTERVAL 1 MONTH));
#                 """)
#                 revenue_data = cursor.fetchall()
 
#                 # Format column names
#                 columns = [col[0] for col in cursor.description]
#                 revenue_list = [dict(zip(columns, row)) for row in revenue_data]
 
#                 #  Calculate Attrition Rate
#                 cursor.execute("SELECT COUNT(*) FROM ci_erp_users WHERE is_active=1")
#                 active_employees = cursor.fetchone()[0]
 
#                 cursor.execute("SELECT COUNT(*) FROM ci_employee_exit")
#                 total_exits = cursor.fetchone()[0]
 
#                 avg_employees = active_employees + total_exits
#                 avg_employees = avg_employees / 2 if avg_employees > 0 else 1
 
#                 attrition_rate = round((total_exits / avg_employees) * 100, 2)
 
 
#                  #  Fetch Resignation Data
#                 cursor.execute("""
#                     SELECT
#                         MONTHNAME(resignation_date) AS month_name,
#                         YEAR(resignation_date) AS year,
#                         COUNT(*) AS resignation_count
#                     FROM ci_resignations
#                     GROUP BY YEAR(resignation_date), MONTH(resignation_date)
#                     ORDER BY YEAR(resignation_date), MONTH(resignation_date)
#                 """)
#                 resignation_data = cursor.fetchall()
#                 resignation_columns = [col[0] for col in cursor.description]
#                 resignation_list = [dict(zip(resignation_columns, row)) for row in resignation_data]
 
 
#                 return Response({
#                     "status": "success",
#                     "month_wise_data": revenue_list,  # includes month & year
#                     "resignation_data": resignation_list,
#                     "calculated_attrition_rate": attrition_rate
#                 }, status=200)
 
#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=500)
        
 
#     def post(self, request):
#         try:
#             data = request.data
#             month = data.get("month")
#             year = data.get("year")
 
#             with connection.cursor() as cursor:
#                 # Check for existing record
#                 cursor.execute("""
#                     SELECT COUNT(*) FROM ci_revenue
#                     WHERE month = %s AND year = %s
#                 """, [month, year])
#                 exists = cursor.fetchone()[0]
 
#                 if exists > 0:
#                     return Response({
#                         "status": "error",
#                         "message": f"Revenue record for {month}-{year} already exists."
#                     }, status=400)
 
#                 #  Insert Revenue Record
#                 cursor.execute("""
#                     INSERT INTO ci_revenue (
#                         month, year, total_revenue, employee_contribution, average,
#                         total_salary, fixed_cost_employee, total_cost_employee, monthly_total_salary,
#                         monthly_expenses, total_employee_cost, per_employee_cost, per_revenue,
#                         exceptional, exceeds_expectations, meet_expectations, below_expectations,
#                         unsatisfactory, department_attrition_rate, division_attrition_rate,
#                         opened_recruitment_tracker, filed_recruitment_tracker,
#                         in_process_recruitment_tracker, level1_employee, level2_employee,
#                         level3_employee, level4_employee, created_at
#                     ) VALUES (
#                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
#                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#                     )
#                 """, [
#                     data.get("month"), data.get("year"), data.get("total_revenue"),
#                     data.get("employee_contribution"), data.get("average"), data.get("total_salary"),
#                     data.get("fixed_cost_employee"), data.get("total_cost_employee"), data.get("monthly_total_salary"),
#                     data.get("monthly_expenses"), data.get("total_employee_cost"), data.get("per_employee_cost"),
#                     data.get("per_revenue"), data.get("exceptional"), data.get("exceeds_expectations"),
#                     data.get("meet_expectations"), data.get("below_expectations"), data.get("unsatisfactory"),
#                     data.get("department_attrition_rate"), data.get("division_attrition_rate"),
#                     data.get("opened_recruitment_tracker"), data.get("filed_recruitment_tracker"),
#                     data.get("in_process_recruitment_tracker"), data.get("level1_employee"),
#                     data.get("level2_employee"), data.get("level3_employee"), data.get("level4_employee"),
#                     datetime.now()
#                 ])
 
#                 # Get the last inserted ID
#                 cursor.execute("SELECT LAST_INSERT_ID()")
#                 new_id = cursor.fetchone()[0]
 
#                 #  Fetch inserted row
#                 cursor.execute("""
#                     SELECT
#                         revenue_id, month, year, total_revenue,
#                         employee_contribution, average, total_salary, fixed_cost_employee,
#                         total_cost_employee, monthly_total_salary, monthly_expenses,
#                         total_employee_cost, per_employee_cost, per_revenue, exceptional,
#                         exceeds_expectations, meet_expectations, below_expectations,
#                         unsatisfactory, department_attrition_rate, division_attrition_rate,
#                         opened_recruitment_tracker, filed_recruitment_tracker,
#                         in_process_recruitment_tracker, level1_employee, level2_employee,
#                         level3_employee, level4_employee, created_at
#                     FROM ci_revenue
#                     WHERE revenue_id = %s
#                 """, [new_id])
#                 inserted_row = cursor.fetchone()
#                 columns = [col[0] for col in cursor.description]
#                 inserted_data = dict(zip(columns, inserted_row))
 
#             return Response({
#                 "status": "success",
#                 "message": "Revenue record inserted successfully",
#                 "month": inserted_data.get("month"),
#                 "year": inserted_data.get("year"),
#                 "data": inserted_data
#             }, status=201)
 
#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=500)






class AdminDashboard(APIView):

    def get(self, request):
        try:
            with connection.cursor() as cursor:

                 # Basic counts
                cursor.execute("""SELECT COUNT(*) FROM ci_erp_users as eu inner join ci_erp_users_details as eud on eu.id = eud.user_id """)
                emp_count = cursor.fetchone()[0]
 
                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN eu.is_active = 1 THEN 1 ELSE 0 END) AS active_count,
                        SUM(CASE WHEN eu.is_active = 0 THEN 1 ELSE 0 END) AS inactive_count
                    FROM ci_erp_users as eu inner join ci_erp_users_details as eud on eu.id = eud.user_id  
                """)
                row = cursor.fetchone()
                emp_count_active = row[0]
                emp_count_inactive = row[1]

                # ================== Fetch Revenue Data ==================
                cursor.execute("""
                    SELECT
                        revenue_id,
                        MONTHNAME(STR_TO_DATE(month, '%m')) AS month_name,
                        year, total_revenue,
                        employee_contribution, average, total_salary, fixed_cost_employee,
                        total_cost_employee, monthly_total_salary, monthly_expenses,
                        total_employee_cost, per_employee_cost, per_revenue, exceptional,
                        exceeds_expectations, meet_expectations, below_expectations,
                        unsatisfactory, department_attrition_rate, division_attrition_rate,
                        opened_recruitment_tracker, filed_recruitment_tracker,
                        in_process_recruitment_tracker, level1_employee, level2_employee,
                        level3_employee, level4_employee, created_at
                    FROM ci_revenue
                    WHERE (year = YEAR(CURRENT_DATE - INTERVAL 1 MONTH)
                    AND month = MONTH(CURRENT_DATE - INTERVAL 1 MONTH));
                """)
                revenue_data = cursor.fetchall()
                revenue_columns = [col[0] for col in cursor.description]
                revenue_list = [dict(zip(revenue_columns, row)) for row in revenue_data]

                # ================== Resignation Data ==================
                # All resignations
                cursor.execute("""
                    SELECT
                        MONTHNAME(resignation_date) AS month_name,
                        YEAR(resignation_date) AS year,
                        COUNT(*) AS total_resignations
                    FROM ci_resignations
                    GROUP BY YEAR(resignation_date), MONTH(resignation_date)
                    ORDER BY YEAR(resignation_date), MONTH(resignation_date)
                """)
                resignation_data = cursor.fetchall()
                resignation_columns = [col[0] for col in cursor.description]
                resignation_list = [dict(zip(resignation_columns, row)) for row in resignation_data]

                # Approved resignations (status = 1)
                cursor.execute("""
                    SELECT
                        MONTHNAME(resignation_date) AS month_name,
                        YEAR(resignation_date) AS year,
                        COUNT(*) AS approved_resignations
                    FROM ci_resignations
                    WHERE status = 1
                    GROUP BY YEAR(resignation_date), MONTH(resignation_date)
                    ORDER BY YEAR(resignation_date), MONTH(resignation_date)
                """)
                approved_data = cursor.fetchall()
                approved_columns = [col[0] for col in cursor.description]
                approved_list = [dict(zip(approved_columns, row)) for row in approved_data]

                # Exit proceed vs not proceed (join with ci_employee_exit)
                cursor.execute("""
                    SELECT
                        MONTHNAME(r.resignation_date) AS month_name,
                        YEAR(r.resignation_date) AS year,
                        SUM(CASE WHEN e.exit_interview = 1 AND e.is_inactivate_account = 1 THEN 1 ELSE 0 END) AS proceed_count,
                        SUM(CASE WHEN e.exit_interview != 1 OR e.is_inactivate_account != 1 THEN 1 ELSE 0 END) AS not_proceed_count
                    FROM ci_resignations r
                    LEFT JOIN ci_employee_exit e ON r.employee_id = e.employee_id
                    GROUP BY YEAR(r.resignation_date), MONTH(r.resignation_date)
                    ORDER BY YEAR(r.resignation_date), MONTH(r.resignation_date)
                """)
                exit_data = cursor.fetchall()
                exit_columns = [col[0] for col in cursor.description]
                exit_list = [dict(zip(exit_columns, row)) for row in exit_data]

                resignation_summary = {
                    "all_resignations": resignation_list,
                    "approved_resignations": approved_list,
                    "exit_process_status": exit_list
                }

                # ================== Department-wise count (Active Employees) ==================
                cursor.execute("""
                    SELECT d.department_name, COUNT(*) 
                    FROM ci_erp_users u 
                    LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id 
                    LEFT JOIN ci_departments d ON ud.department_id = d.department_id 
                    WHERE u.is_active = 1
                    GROUP BY ud.department_id, d.department_name
                """)
                dept_rows = cursor.fetchall()
                dept_count = [{"dept_name": row[0], "dept_count": row[1]} for row in dept_rows]

                # ================== Designation-wise count (Active Employees) ==================
                cursor.execute("""
                    SELECT d.designation_name, COUNT(*) 
                    FROM ci_erp_users u 
                    LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id 
                    LEFT JOIN ci_designations d ON ud.designation_id = d.designation_id 
                    WHERE u.is_active = 1
                    GROUP BY ud.designation_id, d.designation_name
                """)
                desig_rows = cursor.fetchall()
                desig_count = [{"desig_name": row[0], "desig_count": row[1]} for row in desig_rows]

                # ================== Division-wise count (Active Employees) ==================
                cursor.execute("""
                    SELECT di.division_name, COUNT(*) 
                    FROM ci_erp_users u 
                    LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id 
                    LEFT JOIN ci_division di ON ud.division_id = di.division_id 
                    WHERE u.is_active = 1
                    GROUP BY ud.division_id, di.division_name
                """)
                div_rows = cursor.fetchall()
                div_count = [{"division_name": row[0], "division_count": row[1]} for row in div_rows]


                 # Updated active_employees using ci_biomatric_data
                # cursor.execute("""
                #     SELECT 
                #         ud.employee_id, 
                #         CONCAT(u.first_name, ' ', u.last_name) AS emp_name,
                #         'Present' AS attendance_status,
                #         b.clock_in
                #     FROM 
                #         ci_biomatric_data b
                #     INNER JOIN 
                #         ci_erp_users u ON b.userid = u.id
                #     INNER JOIN 
                #         ci_erp_users_details ud ON u.id = ud.user_id
                #     WHERE 
                #         DATE(b.attendance_date) = CURDATE()
                #     AND 
                #         b.clock_in IS NOT NULL
                #     AND 
                #         u.is_active = 1
                #     ORDER BY 
                #         b.clock_in ASC
                # """)

                cursor.execute("""
                    SELECT 
    ud.employee_id, 
    CONCAT(u.first_name, ' ', u.last_name) AS emp_name,
    'Present' AS attendance_status,
    MIN(b.clock_in) AS clock_in
FROM 
    ci_biomatric_data b
INNER JOIN 
    ci_erp_users u ON b.userid = u.id
INNER JOIN 
    ci_erp_users_details ud ON u.id = ud.user_id
WHERE 
    DATE(b.attendance_date) = CURDATE()
    AND b.clock_in IS NOT NULL
    AND u.is_active = 1
GROUP BY 
    ud.employee_id, u.first_name, u.last_name
ORDER BY 
    clock_in ASC;

                """)
                rows = cursor.fetchall()
                active_employees = [{
                    "employee_id": row[0],
                    "employee_name": row[1],
                    "status": row[2],
                    "punch_in": row[3]
                } for row in rows]


            return Response({
                "status": "success",
                "emp_count": emp_count,
                "emp_count_active": emp_count_active,
                "emp_count_inactive": emp_count_inactive,
                "month_wise_data": revenue_list,      # includes manually entered attrition rates
                "resignation_data": resignation_summary,
                "department_wise_count": dept_count,
                "designation_wise_count": desig_count,
                "division_wise_count": div_count,
                "active_employees": active_employees
            }, status=200)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)

    def post(self, request):
        try:
            data = request.data
            month = data.get("month")
            year = data.get("year")

            with connection.cursor() as cursor:
                # Check for existing record
                cursor.execute("""
                    SELECT COUNT(*) FROM ci_revenue
                    WHERE month = %s AND year = %s
                """, [month, year])
                exists = cursor.fetchone()[0]

                if exists > 0:
                    return Response({
                        "status": "error",
                        "message": f"Revenue record for {month}-{year} already exists."
                    }, status=400)

                # Insert Revenue Record (with manually typed attrition rates)
                cursor.execute("""
                    INSERT INTO ci_revenue (
                        month, year, total_revenue, employee_contribution, average,
                        total_salary, fixed_cost_employee, total_cost_employee, monthly_total_salary,
                        monthly_expenses, total_employee_cost, per_employee_cost, per_revenue,
                        exceptional, exceeds_expectations, meet_expectations, below_expectations,
                        unsatisfactory, department_attrition_rate, division_attrition_rate,
                        opened_recruitment_tracker, filed_recruitment_tracker,
                        in_process_recruitment_tracker, level1_employee, level2_employee,
                        level3_employee, level4_employee, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, [
                    data.get("month"), data.get("year"), data.get("total_revenue"),
                    data.get("employee_contribution"), data.get("average"), data.get("total_salary"),
                    data.get("fixed_cost_employee"), data.get("total_cost_employee"), data.get("monthly_total_salary"),
                    data.get("monthly_expenses"), data.get("total_employee_cost"), data.get("per_employee_cost"),
                    data.get("per_revenue"), data.get("exceptional"), data.get("exceeds_expectations"),
                    data.get("meet_expectations"), data.get("below_expectations"), data.get("unsatisfactory"),
                    data.get("department_attrition_rate"), data.get("division_attrition_rate"),
                    data.get("opened_recruitment_tracker"), data.get("filed_recruitment_tracker"),
                    data.get("in_process_recruitment_tracker"), data.get("level1_employee"),
                    data.get("level2_employee"), data.get("level3_employee"), data.get("level4_employee"),
                    datetime.now()
                ])

                # Get the last inserted ID
                cursor.execute("SELECT LAST_INSERT_ID()")
                new_id = cursor.fetchone()[0]

                # Fetch inserted row
                cursor.execute("""
                    SELECT
                        revenue_id, month, year, total_revenue,
                        employee_contribution, average, total_salary, fixed_cost_employee,
                        total_cost_employee, monthly_total_salary, monthly_expenses,
                        total_employee_cost, per_employee_cost, per_revenue, exceptional,
                        exceeds_expectations, meet_expectations, below_expectations,
                        unsatisfactory, department_attrition_rate, division_attrition_rate,
                        opened_recruitment_tracker, filed_recruitment_tracker,
                        in_process_recruitment_tracker, level1_employee, level2_employee,
                        level3_employee, level4_employee, created_at
                    FROM ci_revenue
                    WHERE revenue_id = %s
                """, [new_id])
                inserted_row = cursor.fetchone()
                columns = [col[0] for col in cursor.description]
                inserted_data = dict(zip(columns, inserted_row))

            return Response({
                "status": "success",
                "message": "Revenue record inserted successfully",
                "month": inserted_data.get("month"),
                "year": inserted_data.get("year"),
                "data": inserted_data
            }, status=201)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)



# Trainers
from .models import CITrainer
from .serializers import CITrainerSerializer
 
class CITrainerView(APIView):
    permission_classes = [IsAuthenticated]
 
    # GET
    def get(self, request, *args, **kwargs):
        trainers = CITrainer.objects.all()
        serializer = CITrainerSerializer(trainers, many=True)
        return Response({'message': 'Trainer data fetched successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)
 
    # POST
    def post(self, request, *args, **kwargs):
        serializer = CITrainerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Trainer created successfully.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    # PATCH
    def patch(self, request, pk=None, *args, **kwargs):
        try:
            trainer = CITrainer.objects.get(pk=pk)
        except CITrainer.DoesNotExist:
            return Response({'error': 'Trainer not found.'}, status=status.HTTP_404_NOT_FOUND)
 
        serializer = CITrainerSerializer(trainer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Trainer updated successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    # DELETE
    def delete(self, request, pk=None, *args, **kwargs):
        try:
            trainer = CITrainer.objects.get(pk=pk)
        except CITrainer.DoesNotExist:
            return Response({'error': 'Trainer not found.'},status=status.HTTP_200_OK)
 
        trainer.delete()
        return Response({'message': 'Trainer deleted successfully.'}, status=status.HTTP_200_OK)




###COMPOFF

from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class CompOffView(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.compoff_id, 
                    c.emp_id, 
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    c.start_date_compoff, 
                    c.end_date_compoff, 
                    DATEDIFF(c.end_date_compoff, c.start_date_compoff) + 1 AS no_of_days,
                    c.compoff_reason, 
                    c.compoff_status, 
                    c.created_at,
                    c.is_expired
                FROM 
                    ci_erp_compoff c
                LEFT JOIN 
                    ci_erp_users_details ud ON c.emp_id = ud.employee_id
                LEFT JOIN 
                    ci_erp_users u ON ud.user_id = u.id 
                ORDER BY 
                    c.created_at DESC
            """)

            rows = cursor.fetchall()

        columns = [
            "compoff_id", "emp_id", "employee_name", "start_date_compoff", "end_date_compoff",
            "no_of_days", "compoff_reason", "compoff_status", "created_at", "is_expired"
        ]
        data = [dict(zip(columns, row)) for row in rows]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        required_fields = ["employee_name", "start_date_compoff", "end_date_compoff", "compoff_reason"]

        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        employee_name = data.get("employee_name").strip()
        if " " not in employee_name:
            return Response({"error": "Please provide full employee name (first and last name)."}, status=status.HTTP_400_BAD_REQUEST)
        first_name, last_name = employee_name.split(" ", 1)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ud.employee_id 
                FROM ci_erp_users u 
                INNER JOIN ci_erp_users_details ud ON u.id = ud.user_id 
                WHERE u.first_name = %s AND u.last_name = %s
            """, [first_name, last_name])
            result = cursor.fetchone()
            if not result:
                return Response({"error": "Employee not found with given name."}, status=status.HTTP_404_NOT_FOUND)

            emp_id = result[0]
            start_date = datetime.strptime(data["start_date_compoff"], "%Y-%m-%d").date()
            end_date = datetime.strptime(data["end_date_compoff"], "%Y-%m-%d").date()

            if end_date < start_date:
                return Response({"error": "End date cannot be before start date."}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Calculate no_of_days
            no_of_days = (end_date - start_date).days + 1
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            is_expired = (start_date + timedelta(days=60)).strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO ci_erp_compoff (
                    emp_id, start_date_compoff, end_date_compoff, no_of_days,
                    compoff_reason, created_at, is_expired, compoff_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                emp_id,
                data["start_date_compoff"],
                data["end_date_compoff"],
                no_of_days,
                data["compoff_reason"],
                created_at,
                is_expired,
                'P'  # default to Pending
            ])

        return Response({"message": "CompOff request submitted successfully."}, status=status.HTTP_201_CREATED)

    def patch(self, request, compoff_id):
        data = request.data
        allowed_fields = ["employee_name", "start_date_compoff", "end_date_compoff", "compoff_reason", "compoff_status"]

        fields = []
        values = []

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ci_erp_compoff WHERE compoff_id = %s", [compoff_id])
            if cursor.fetchone()[0] == 0:
                return Response({"error": "CompOff record not found."}, status=status.HTTP_404_NOT_FOUND)

            if "employee_name" in data:
                employee_name = data["employee_name"].strip()
                if " " not in employee_name:
                    return Response({"error": "Please provide full employee name (first and last name)."}, status=status.HTTP_400_BAD_REQUEST)
                first_name, last_name = employee_name.split(" ", 1)

                cursor.execute("""
                    SELECT ud.employee_id 
                    FROM ci_erp_users u 
                    INNER JOIN ci_erp_users_details ud ON u.id = ud.user_id 
                    WHERE u.first_name = %s AND u.last_name = %s
                """, [first_name, last_name])
                result = cursor.fetchone()
                if not result:
                    return Response({"error": "Employee not found with given name."}, status=status.HTTP_404_NOT_FOUND)

                emp_id = result[0]
                fields.append("emp_id = %s")
                values.append(emp_id)

            # Handle date updates and re-calculate no_of_days
            start_date = data.get("start_date_compoff")
            end_date = data.get("end_date_compoff")

            if start_date and end_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

                if end_dt < start_dt:
                    return Response({"error": "End date cannot be before start date."}, status=status.HTTP_400_BAD_REQUEST)

                no_of_days = (end_dt - start_dt).days + 1
                fields.append("start_date_compoff = %s")
                values.append(start_date)
                fields.append("end_date_compoff = %s")
                values.append(end_date)
                fields.append("no_of_days = %s")
                values.append(no_of_days)

            for field in allowed_fields:
                if field not in ["employee_name", "start_date_compoff", "end_date_compoff"] and field in data:
                    fields.append(f"{field} = %s")
                    values.append(data[field])

            if not fields:
                return Response({"error": "No valid fields provided for update."}, status=status.HTTP_400_BAD_REQUEST)

            query = f"UPDATE ci_erp_compoff SET {', '.join(fields)} WHERE compoff_id = %s"
            values.append(compoff_id)
            cursor.execute(query, values)

        return Response({"message": "CompOff record updated successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, compoff_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ci_erp_compoff WHERE compoff_id = %s", [compoff_id])
            if cursor.fetchone()[0] == 0:
                return Response({"error": "CompOff record not found."}, status=status.HTTP_404_NOT_FOUND)

            cursor.execute("DELETE FROM ci_erp_compoff WHERE compoff_id = %s", [compoff_id])

        return Response({"message": "CompOff record deleted successfully."}, status=status.HTTP_200_OK)
 






from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from datetime import datetime

class VisitorListCreateAPIView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT v.*, d.department_name
                FROM ci_visitors v
                LEFT JOIN ci_departments d ON v.department_id = d.department_id
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(data)

    def post(self, request):
        data = request.data
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_visitors (
                    company_id, department_id, visit_purpose, visitor_name, phone, email,
                    visit_date, check_in, address, description, created_by, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                data.get('company_id', 2),
                data.get('department'),
                data.get('visit_purpose'),
                data.get('visitor_name'),
                data.get('phone'),
                data.get('email'),
                data.get('visit_date'),
                data.get('check_in'),
                data.get('address'),
                data.get('description'),
                data.get('created_by'),
                data.get('created_at') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ])
        return Response({'message': 'Visitor created successfully'}, status=status.HTTP_201_CREATED)


class VisitorDetailAPIView(APIView):
    def get_object(self, pk):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT v.*, d.department_name
                FROM ci_visitors v
                LEFT JOIN ci_departments d ON v.department_id = d.department_id
                WHERE v.visitor_id = %s
            """, [pk])
            row = cursor.fetchone()
            if not row:
                raise Http404
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))

    def get(self, request, pk):
        visitor = self.get_object(pk)
        return Response(visitor)

    def patch(self, request, pk):
        fields = []
        values = []

        for key, value in request.data.items():
            fields.append(f"{key} = %s")
            values.append(value)
        values.append(pk)

        if not fields:
            return Response({'error': 'No fields to update'}, status=status.HTTP_400_BAD_REQUEST)

        query = f"UPDATE ci_visitors SET {', '.join(fields)} WHERE visitor_id = %s"

        with connection.cursor() as cursor:
            cursor.execute(query, values)

        return Response({'message': 'Visitor updated successfully'})

    def delete(self, request, pk):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ci_visitors WHERE visitor_id = %s", [pk])
        return Response({'message': 'Visitor deleted successfully'}, status=status.HTTP_200_OK)



from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class VisitorRawListAPIView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    v.visitor_id,
                    v.company_id,
                    v.department_id,
                    d.department_name,
                    v.visit_purpose,
                    v.visitor_name,
                    v.phone,
                    v.email,
                    v.visit_date,
                    v.check_in,
                    v.check_out,
                    v.address,
                    v.description,
                    v.created_by,
                    v.created_at
                FROM ci_visitors v
                LEFT JOIN ci_departments d ON v.department_id = d.department_id
                ORDER BY v.visitor_id DESC
            """)
            columns = [col[0] for col in cursor.description]
            results = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return Response(results, status=status.HTTP_200_OK)


class StateDropdown(APIView):
    def get(self, request):
        country_name = request.GET.get("country_name")

        if not country_name:
            return Response(
                {"status": "error", "message": "country_name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with connection.cursor() as c:
                # Step 1: Get country_id from country_name
                c.execute("""
                    SELECT constants_id FROM ci_erp_constants
                    WHERE type = 'country' AND category_name = %s
                    LIMIT 1
                """, [country_name])
                country_row = c.fetchone()

                if not country_row:
                    return Response(
                        {"status": "error", "message": f"Country '{country_name}' not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                country_id = country_row[0]

                # Step 2: Fetch states using parent_value = country_id
                c.execute("""
                    SELECT constants_id AS state_id, category_name AS state_name
                    FROM ci_erp_constants
                    WHERE type = 'state' AND parent_value = %s
                """, [country_id])

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": response},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CountryDropdown(APIView):
    def get(self, request):
        try:
            with connection.cursor() as c:
                c.execute("""
                    SELECT constants_id AS country_id, category_name AS country_name
                    FROM ci_erp_constants
                    WHERE type = 'country'
                """)

                columns = [col[0] for col in c.description]
                response = [dict(zip(columns, row)) for row in c.fetchall()]

            return Response(
                {"status": "success", "data": response},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# class EmployeeDropdownView(APIView):
    
#     def get(self, request):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT
#                     cud.user_id AS value,
#                     cud.employee_id AS emp_id,
#                     CONCAT(cu.first_name, ' ', cu.last_name) AS label,
#                     cd.division_name,
#                     cu.email
#                 FROM
#                     ci_erp_users cu
#                 JOIN
#                     ci_erp_users_details cud ON cu.id = cud.user_id
# 				JOIN 
# 					ci_division cd ON cud.division_id  = cd.division_id
#                 WHERE
#                     cu.is_active = 1
#                 ORDER BY
#                     cu.first_name, cu.last_name

#             """)
#             rows = cursor.fetchall()

#         # Convert result to list of dicts
#         data = [{"value": row[0], "emp_id": row[1], "label": row[2], "email": row[3]} for row in rows]

#         return Response(data)


class EmployeeDropdownView(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    cud.user_id AS value,
                    cud.employee_id AS emp_id,
                    CONCAT(cu.first_name, ' ', cu.last_name) AS label,
                    cd.division_name,
                    cu.email
                FROM
                    ci_erp_users cu
                LEFT JOIN
                    ci_erp_users_details cud ON cu.id = cud.user_id
                LEFT JOIN 
                    ci_division cd ON cud.division_id = cd.division_id
                WHERE
                    cu.is_active = 1
                ORDER BY
                    cu.first_name, cu.last_name
            """)
            rows = cursor.fetchall()

        # ✅ Correct mapping
        data = [
            {
                "value": row[0],
                "emp_id": row[1],
                "label": row[2],
                "division_name": row[3],
                "email": row[4],
            }
            for row in rows
        ]

        return Response(data)




class ReligionDropdownView(APIView):
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS name
                FROM 
                    ci_erp_constants
                WHERE 
                    type = 'religion'
                ORDER BY 
                    category_name
            """)
            rows = cursor.fetchall()

        data = [{"value": row[0], "label": row[1]} for row in rows]
        return Response(data)



class LeaveTypeDropdownView(APIView):
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS name
                FROM 
                    ci_erp_constants
                WHERE 
                    type = 'leave_type'
                ORDER BY 
                    category_name
            """)
            rows = cursor.fetchall()

        data = [{"value": row[0], "label": row[1]} for row in rows]
        return Response(data)







class CitizenshipDropdownView(APIView):
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS label
                FROM 
                    ci_erp_constants
                WHERE 
                    type = 'citizenship'
                ORDER BY 
                    category_name
            """)
            rows = cursor.fetchall()

        data = [{"value": row[0], "label": row[1]} for row in rows]
        return Response(data)

    
    

class NationalityDropdownView(APIView):
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS label
                FROM 
                    ci_erp_constants
                WHERE 
                    type = 'nationality'
                ORDER BY 
                    category_name
            """)
            rows = cursor.fetchall()

        data = [{"value": row[0], "label": row[1]} for row in rows]
        return Response(data)




class AwardTypeDropdownView(APIView):

    def patch(self, request, award_type_id):

        award_type_name = request.data.get("award_type_name")
        description = request.data.get("description")
        
        if not award_type_name:
            return Response({"error": "award_type_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        with connection.cursor() as cursor:
            if description is not None:
                cursor.execute("""
                    UPDATE ci_award_type
                    SET award_type_name = %s, description = %s
                    WHERE award_type_id = %s
                """, [award_type_name, description, award_type_id])
            else:
                cursor.execute("""
                    UPDATE ci_award_type
                    SET award_type_name = %s
                    WHERE award_type_id = %s
                """, [award_type_name, award_type_id])
        return Response({"message": "Award type updated successfully."}, status=status.HTTP_200_OK)
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS label,
                    created_at
                FROM 
                    ci_erp_constants
                WHERE 
                    type = 'award_type'
                ORDER BY 
                    category_name
            """)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            created_at = row[2]
            created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
            data.append({
                "value": row[0],
                "label": row[1],
                "created_at": created_at_str
            })
        
        return Response(data)

    def post(self, request):
        category_name = request.data.get("category_name")
        
        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = 2  # Default value
        created_at = datetime.now()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_erp_constants (category_name, type, company_id, created_at)
                VALUES (%s, %s, %s, %s)
            """, [category_name, 'award_type', company_id, created_at])

        return Response({"message": "Award type added successfully."}, status=status.HTTP_201_CREATED)

    def delete(self, request, award_type_id):
        """
        Delete an award type by its ID (constants_id) from ci_erp_constants where type is 'award_type'.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM ci_erp_constants
                WHERE constants_id = %s AND type = 'award_type'
                """,
                [award_type_id]
            )
        return Response({"message": "Award type deleted successfully."}, status=status.HTTP_200_OK)

    




class TrainingSkillDropdownView(APIView):
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS label,
                    created_at
                FROM 
                    ci_erp_constants
                WHERE 
                    type = 'training_skill'
                ORDER BY 
                    category_name
            """)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            created_at = row[2]
            created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
            data.append({
                "value": row[0],
                "label": row[1],
                "created_at": created_at_str
            })
        
        return Response(data)

    def post(self, request):
        category_name = request.data.get("category_name")
        
        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = 2  # Default company ID
        created_at = datetime.now()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_erp_constants (category_name, type, company_id, created_at)
                VALUES (%s, %s, %s, %s)
            """, [category_name, 'training_skill', company_id, created_at])

        return Response({"message": "Training skill added successfully."}, status=status.HTTP_201_CREATED)




class StaffRoleDropdownView(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    role_id AS value,
                    role_name AS label
                FROM 
                    ci_staff_roles
                ORDER BY 
                    role_name
            """)
            rows = cursor.fetchall()

        # Convert result to list of dicts
        data = [{"value": row[0], "label": row[1]} for row in rows]

        return Response(data)

class StaffRoleAPIView(APIView):

    def get(self, request, role_id=None):
        """Fetch all roles or a single role if role_id is given"""
        with connection.cursor() as cursor:
            if role_id:
                cursor.execute("""
                    SELECT role_id, role_name, created_at
                    FROM ci_staff_roles
                    WHERE role_id = %s
                """, [role_id])
                row = cursor.fetchone()
                if not row:
                    return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
                data = {
                    "value": row[0],
                    "label": row[1],
                    "created_at": row[2] 
                }
            else:
                cursor.execute("""
                    SELECT role_id, role_name, created_at
                    FROM ci_staff_roles
                    ORDER BY role_id desc
                """)
                rows = cursor.fetchall()
                data = [
                    {
                        "value": row[0],
                        "label": row[1],
                        "created_at": row[2]
                    }
                    for row in rows
                ]

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, role_id=None):
        """Create a new staff role"""
        role_name = request.data.get("role_name")

        if not role_name:
            return Response({"error": "role_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_staff_roles (role_name, company_id, created_at)
                VALUES (%s, %s, NOW())
            """, [role_name, 2])
            new_id = cursor.lastrowid

            # fetch created_at datetime
            cursor.execute("SELECT created_at FROM ci_staff_roles WHERE role_id = %s", [new_id])
            created_at = cursor.fetchone()[0]

        return Response(
            {
                "message": "Role created successfully",
                "role_id": new_id,
                "role_name": role_name,
                "company_id": 2,
                "created_at": created_at
            },
            status=status.HTTP_201_CREATED
        )

    def patch(self, request, role_id=None):
        """Update an existing staff role (also update created_at to today)"""
        if not role_id:
            return Response({"error": "role_id is required in URL"}, status=status.HTTP_400_BAD_REQUEST)

        role_name = request.data.get("role_name")
        if not role_name:
            return Response({"error": "role_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE ci_staff_roles
                SET role_name = %s
                WHERE role_id = %s
            """, [role_name, role_id])

            cursor.execute("SELECT created_at FROM ci_staff_roles WHERE role_id = %s", [role_id])
            created_at = cursor.fetchone()[0]

        return Response(
            {
                "message": "Role updated successfully",
                "role_id": role_id,
                "role_name": role_name
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request, role_id=None):
        """Delete a staff role"""
        if not role_id:
            return Response({"error": "role_id is required in URL"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ci_staff_roles WHERE role_id = %s", [role_id])

        return Response({"message": "Role deleted successfully"}, status=status.HTTP_200_OK)



class AssetsCategoryDropdownView(APIView):
    
    def get(self, request):
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        constants_id AS value,
                        category_name AS label,
                        created_at
                    FROM 
                        ci_erp_constants
                    WHERE 
                        type = 'assets_category'
                    ORDER BY 
                        category_name
                """)
                rows = cursor.fetchall()

            data = []
            for row in rows:
                created_at = row[2]
                created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
                data.append({
                    "value": row[0],
                    "label": row[1],
                    "created_at": created_at_str
                })
            
            return Response(data)
    
        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        category_name = request.data.get("category_name")
        
        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = 2  # Default company ID
        created_at = datetime.now()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_erp_constants (category_name, type, company_id, created_at)
                    VALUES (%s, %s, %s, %s)
                """, [category_name, 'assets_category', company_id, created_at])

            return Response({"message": "Assets category added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):

        constants_id = request.data.get("constants_id")
        category_name = request.data.get("category_name")

        if not constants_id:
            return Response({"error": "constants_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_erp_constants
                    SET category_name = %s
                    WHERE constants_id = %s
                """, [category_name, constants_id])

            return Response({"status":"success","message": "Assets category updated successfully."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, constants_id):

        if not constants_id:
            return Response({"status":"error","message":"constants_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as c:

                c.execute("""delete from ci_erp_constants where constants_id = %s""", [constants_id])

            return Response({"status":"success","message":"assets category deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssetsTypeDropdownView(APIView):

    def get(self, request):

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ec.constants_id AS value,
                        ec.field_one AS category_id,
                        ec2.category_name AS category_name,
                        ec.category_name AS label,
                        ec.created_at
                    FROM 
                        ci_erp_constants ec inner join ci_erp_constants ec2 on ec.field_one = ec2.constants_id
                    WHERE 
                        ec.type = 'assets_type'
                    ORDER BY 
                        ec.category_name
                """)
                rows = cursor.fetchall()

            data = []
            for row in rows:
                created_at = row[4]
                created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
                data.append({
                    "value": row[0],
                    "category_id": row[1],
                    "category_name": row[2],
                    "label": row[3],
                    "created_at": created_at_str
                })

            return Response(data)

        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):

        category_id = request.data.get("category_id")
        asset_type_name = request.data.get("asset_type_name")

        if not category_id:
            return Response({"error": "category_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = 2  # Default company ID
        created_at = datetime.now()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_erp_constants (company_id, type, category_name, field_one, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, [company_id, 'assets_type', asset_type_name, category_id, created_at])

            return Response({"status":"success","message": "Assets type added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):

        constants_id = request.data.get("constants_id")
        category_id = request.data.get("category_id")
        type_name = request.data.get("type_name")

        if not constants_id:
            return Response({"status":"error", "message": "constants_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_erp_constants
                    SET category_name = %s, field_one = %s, 
                    WHERE constants_id = %s
                """, [type_name, category_id, constants_id])

            return Response({"status":"success","message": "Assets type updated successfully."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, constants_id):

        if not constants_id:
            return Response({"status":"error","message":"constants_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as c:

                c.execute("""delete from ci_erp_constants where constants_id = %s""", [constants_id])

            return Response({"status":"success","message":"assets type deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssetsBrandDropdownView(APIView):
    
    def get(self, request):

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        constants_id AS value,
                        category_name AS label,
                        created_at
                    FROM 
                        ci_erp_constants
                    WHERE 
                        type = 'assets_brand'
                    ORDER BY 
                        category_name
                """)
                rows = cursor.fetchall()

            data = []
            for row in rows:
                created_at = row[2]
                created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
                data.append({
                    "value": row[0],
                    "label": row[1],
                    "created_at": created_at_str
                })
            
            return Response(data)

        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):

        category_name = request.data.get("category_name")
        
        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = 2  # Default company ID
        created_at = datetime.now()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_erp_constants (category_name, type, company_id, created_at)
                    VALUES (%s, %s, %s, %s)
                """, [category_name, 'assets_brand', company_id, created_at])

            return Response({"message": "Assets brand added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):

        constants_id = request.data.get("constants_id")
        category_name = request.data.get("brand_name")

        if not constants_id:
            return Response({"error": "constants_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_erp_constants
                    SET category_name = %s
                    WHERE constants_id = %s
                """, [category_name, constants_id])

            return Response({"status":"success","message": "Assets brand updated successfully."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, constants_id):

        if not constants_id:
            return Response({"status":"error","message":"constants_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as c:

                c.execute("""delete from ci_erp_constants where constants_id = %s""", [constants_id])

            return Response({"status":"success","message":"assets brand deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DepartmentWiseEmployeeCountView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    d.department_id,
                    d.department_name,
                    cud.employee_id,
                    CONCAT(cu.first_name, ' ', cu.last_name) AS employee_name,
                    cu.email
                FROM 
                    ci_departments d
                LEFT JOIN 
                    ci_erp_users_details cud ON d.department_id = cud.department_id
                LEFT JOIN 
                    ci_erp_users cu ON cu.id = cud.user_id
                WHERE 
                    cu.is_active = 1
                ORDER BY 
                    d.department_name, employee_name
            """)
            rows = cursor.fetchall()

        department_map = {}

        for dept_id, dept_name, emp_id, emp_name, email in rows:
            if dept_id not in department_map:
                department_map[dept_id] = {
                    "department_id": dept_id,
                    "department_name": dept_name,
                    "dept_count": 0,
                    "employees": []
                }
            if emp_id:  # Only count employees that exist
                department_map[dept_id]["dept_count"] += 1
                department_map[dept_id]["employees"].append({
                    "employee_id": emp_id,
                    "employee_name": emp_name,
                    "email": email
                })

        data = list(department_map.values())
        return Response(data)





class DesignationWiseEmployeeCountView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    des.designation_id,
                    des.designation_name,
                    cud.employee_id,
                    CONCAT(cu.first_name, ' ', cu.last_name) AS employee_name,
                    cu.email
                FROM 
                    ci_designations des
                LEFT JOIN 
                    ci_erp_users_details cud ON des.designation_id = cud.designation_id
                LEFT JOIN 
                    ci_erp_users cu ON cu.id = cud.user_id AND cu.is_active = 1
                ORDER BY 
                    des.designation_name, employee_name
            """)
            rows = cursor.fetchall()

        designation_map = {}

        for desig_id, desig_name, emp_id, emp_name, email in rows:
            # Initialize designation if not already in the map
            if desig_id not in designation_map:
                designation_map[desig_id] = {
                    "designation_id": desig_id,
                    "designation_name": desig_name,
                    "designation_count": 0,
                    "employees": []
                }

            # Only add active employees (cu.is_active = 1 already handled in JOIN)
            if emp_id is not None:
                designation_map[desig_id]["designation_count"] += 1
                designation_map[desig_id]["employees"].append({
                    "employee_id": emp_id,
                    "employee_name": emp_name,
                    "email": email
                })

        data = list(designation_map.values())
        return Response(data)




class ArrangementTypeDropdownView(APIView):
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS label,
                    created_at
                FROM 
                    ci_erp_constants
                WHERE 
                    type = 'arrangement_type'
                ORDER BY 
                    category_name
            """)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            created_at = row[2]
            created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
            data.append({
                "value": row[0],
                "label": row[1],
                "created_at": created_at_str
            })
        
        return Response(data)

    def post(self, request):
        category_name = request.data.get("category_name")
        
        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = 2  # Default company ID
        created_at = datetime.now()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_erp_constants (category_name, type, company_id, created_at)
                VALUES (%s, %s, %s, %s)
            """, [category_name, 'arrangement_type', company_id, created_at])

        return Response({"message": "Arrangement type added successfully."}, status=status.HTTP_201_CREATED)


class ArrangementTypeDetailView(APIView):
    def patch(self, request, constants_id):
        category_name = request.data.get("category_name")
        if not category_name:
            return Response({"error": "category_name is required."}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE ci_erp_constants
                SET category_name = %s
                WHERE constants_id = %s AND type = 'arrangement_type'
            """, [category_name, constants_id])

        return Response({"message": "Arrangement type updated successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, constants_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM ci_erp_constants
                WHERE constants_id = %s AND type = 'arrangement_type'
            """, [constants_id])

        return Response({"message": "Arrangement type deleted successfully."}, status=status.HTTP_200_OK)




class TravelMoodDropdownView(APIView):
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS label,
                    created_at
                FROM 
                    ci_erp_constants
                WHERE 
                    type = 'travel_mood'
                ORDER BY 
                    category_name
            """)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            created_at = row[2]
            created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
            data.append({
                "value": row[0],
                "label": row[1],
                "created_at": created_at_str
            })
        
        return Response(data)




class ExitEmployeeTypeDropdownView(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    constants_id AS value,
                    category_name AS label,
                    created_at
                FROM
                    ci_erp_constants
                WHERE
                    type = 'exit_type'
                ORDER BY
                    category_name
            """)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            created_at = row[2]
            created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
            data.append({
                "value": row[0],
                "label": row[1],
                "created_at": created_at_str
            })

        return Response(data)
    

    def post(self, request):
        category_name = request.data.get("category_name")

        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        company_id = 2 #Default company ID
        created_at = datetime.now()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_erp_constants (category_name, type, company_id, created_at)     
                VALUES (%s, %s, %s, %s)
            """, [category_name, 'exit_type', company_id, created_at])


        return Response({"message": "Exit tyoe added successfully. "}, status=status.HTTP_201_CREATED)

    
    def patch(self, request, id):
        category_name = request.data.get("category_name")

        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        updated_at = datetime.now()

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE ci_erp_constants
                SET category_name = %s, created_at = %s
                WHERE constants_id = %s AND type = 'exit_type'
            """, [category_name, updated_at, id])

            if cursor.rowcount == 0:
                return Response({"error": "Exit type not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Exit type updated successfully."}, status=status.HTTP_200_OK)


    def delete(self, request, id):
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM ci_erp_constants
                WHERE constants_id = %s AND type = 'exit_type'
            """, [id])

            if cursor.rowcount == 0:
                return Response({"error": "Exit type not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Exit type deleted successfully."}, status=status.HTTP_200_OK)



# class ResignationListCreateView(APIView):
#     def get(self, request):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT
#                     r.resignation_id,
#                     r.company_id,
#                     r.employee_id,
#                     r.resignation_date,
#                     r.last_working_day,
#                     r.reason,
#                     r.added_by,
#                     CASE 
#                         WHEN status = 0 THEN 'Rejected'
#                         WHEN status = 1 THEN 'Approved'
#                         WHEN status = 2 THEN 'Pending'
#                         ELSE 'Unknown'
#                     END AS status,
#                     r.created_at,
#                     GROUP_CONCAT(CONCAT(eu.first_name, ' ', eu.last_name)) AS employee_name,
#                     GROUP_CONCAT(DISTINCT d.department_name) AS department_name
#                 FROM ci_resignations r
#                 LEFT JOIN ci_erp_users_details ed ON FIND_IN_SET(ed.employee_id, r.employee_id)
#                 LEFT JOIN ci_erp_users eu ON ed.user_id = eu.id
#                 LEFT JOIN ci_departments d ON ed.department_id = d.department_id
#                 GROUP BY r.resignation_id
#             """)
#             columns = [col[0] for col in cursor.description]
#             data = [dict(zip(columns, row)) for row in cursor.fetchall()]
#         return Response(data)

#     def post(self, request):
#         data = request.data

#         # Convert status string to integer
#         status_str = str(data.get("status", "")).lower()
#         status_val = 1 if status_str == "approved" else 0 if status_str == "reject" else "pending"

#         if status_val is None:
#             return Response({"error": "Invalid status. Use 'Approved' or 'Reject'."}, status=400)

#         # Fetch department_id from ci_erp_users_details using employee_id
#         employee_id = data.get("employee_id")
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT department_id
#                 FROM ci_erp_users_details
#                 WHERE employee_id = %s
#             """, [employee_id])
#             row = cursor.fetchone()

#         if not row:
#             return Response({"error": "Employee not found or missing department."}, status=404)

#         department_id = row[0]

#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO ci_resignations 
#                 (company_id, employee_id, department_id, notice_date, resignation_date, reason, added_by, status, created_at)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """, [
#                 data.get("company_id"),
#                 employee_id,
#                 department_id,
#                 data.get("notice_date"),
#                 data.get("resignation_date"),
#                 data.get("reason"),
#                 data.get("added_by"),
#                 status_val,
#                 data.get("created_at")
#             ])
#         return Response({"message": "Resignation created successfully."}, status=status.HTTP_201_CREATED)
 



# # Admin / HR approve or reject resignation
# class ResignationDetailView(APIView):

#     def patch(self, request, resignation_id):
#         data = request.data

#         fields = []
#         values = []
#         status_value = None
#         status_str = None
        
#         if "last_working_day" in data:
#             fields.append("last_working_day = %s")
#             values.append(data["last_working_day"])

#         if "status" in data:
#             status_str = str(data["status"]).lower()
#             if status_str == "approved":
#                 status_value = 1
#             elif status_str == "reject":
#                 status_value = 0
#             elif status_str == "pending":
#                 status_value = 2
#             else:
#                 return Response({"error": "Invalid status. Use 'Approved' or 'Reject'."}, status=400)
#             fields.append("status = %s")
#             values.append(status_value)
            
#         if "created_at" in data:
#             fields.append("created_at = %s")
#             values.append(data["created_at"])

#         if not fields:
#             return Response({"error": "No valid fields provided."}, status=400)

#         values.append(resignation_id)

#         # Fetch employee details before updating
#         employee_email = None
#         employee_name = None
#         resignation_date = None
#         reason = None
        
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT eu.email, CONCAT(eu.first_name, ' ', eu.last_name) AS employee_name,
#                        r.resignation_date, r.reason
#                 FROM ci_resignations r
#                 JOIN ci_erp_users_details ed ON r.employee_id = ed.employee_id
#                 JOIN ci_erp_users eu ON ed.user_id = eu.id
#                 WHERE r.resignation_id = %s
#             """, [resignation_id])
#             row = cursor.fetchone()
            
#             if row:
#                 employee_email, employee_name, resignation_date, reason = row

#         # Update the resignation
#         with connection.cursor() as cursor:
#             cursor.execute(f"""
#                 UPDATE ci_resignations SET {', '.join(fields)} WHERE resignation_id = %s
#             """, values)

#         # Send email notification if status was changed
#         if status_value is not None and employee_email:
#             self.send_status_notification(
#                 employee_email, 
#                 employee_name, 
#                 status_str, 
#                 resignation_date, 
#                 reason
#             )

#         return Response({"message": "Resignation updated successfully."})

#     def send_status_notification(self, employee_email, employee_name, status, resignation_date, reason):
#         # Determine email subject and content based on status
#         if status == "approved":
#             subject = "Resignation Approved"
#             status_text = "Approved"
#             status_color = "green"
#             message = "Your resignation has been approved. Please work with HR to complete the offboarding process."
#         elif status == "reject":
#             subject = "Resignation Rejected"
#             status_text = "Rejected"
#             status_color = "red"
#             message = "Your resignation has been rejected. Please contact HR for more details."
#         else:
#             # For pending status, no need to send email
#             return

#         # Create HTML email content
#         html_content = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; color: #333;">
#             <h2>Resignation Status Update</h2>
#             <p>Dear <b>{employee_name}</b>,</p>
#             <p>Your resignation request submitted on <b>{resignation_date}</b> has been updated.</p>
#             <p>Reason: {reason}</p>
#             <p>Status: <span style="color:{status_color}; font-weight:bold;">{status_text}</span></p>
#             <p>{message}</p>
#             <p>Best regards,</p>
#             <div style="margin: 10px 0;">
#                 <img src="cid:company_logo" alt="Company Logo" style="width:150px; height:auto;">
#             </div>
#             <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
#         </body>
#         </html>
#         """

#         # Send email to employee
#         msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [employee_email])
#         msg.attach_alternative(html_content, "text/html")
        
#         # Attach logo inline
#         logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
#         if os.path.exists(logo_path):
#             with open(logo_path, 'rb') as f:
#                 logo_data = f.read()
#             image = MIMEImage(logo_data)
#             image.add_header('Content-ID', '<company_logo>')
#             image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
#             msg.attach(image)
            
#         msg.send(fail_silently=False)

#     def delete(self, request, resignation_id):
#         with connection.cursor() as cursor:
#             cursor.execute("DELETE FROM ci_resignations WHERE resignation_id = %s", [resignation_id])
#         return Response({"message": "Resignation deleted successfully."}, status=status.HTTP_200_OK)


 




# # Employee get its own resigantion or post resignation
# class EmployeeResignationClass(APIView):

#     def get(self, request, employee_id):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     resignation_date, 
#                     reason,
#                     CASE 
#                         WHEN status = 0 THEN 'Rejected'
#                         WHEN status = 1 THEN 'Approved'
#                         WHEN status = 2 THEN 'Pending'
#                         ELSE 'Unknown'
#                     END AS status
#                 FROM ci_resignations
#                 WHERE employee_id = %s
#                 ORDER BY created_at DESC
#             """, [employee_id])
#             rows = cursor.fetchall()

#         if not rows:
#             return Response({"message": "No resignation found for this employee."}, status=404)

#         resignations = []
#         for row in rows:
#             resignations.append({
#                 "employee_id": employee_id,
#                 "resignation_date": row[0],
#                 "reason": row[1],
#                 "status": row[2]
#             })

#         return Response(resignations, status=200)


#     def post(self, request, employee_id):
#         resignation_date = datetime.now().strftime('%Y-%m-%d')
#         reason = request.data.get("reason")
#         created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         # Fetch department_id, employee_name, and email
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     ed.department_id,
#                      d.department_name,
#                     CONCAT(eu.first_name, ' ', eu.last_name) AS employee_name,
#                     eu.email
#                 FROM ci_erp_users_details ed
#                 JOIN ci_erp_users eu ON ed.user_id = eu.id
#                 JOIN ci_departments d ON ed.department_id = d.department_id
#                 WHERE ed.employee_id = %s
#             """, [employee_id])
#             row = cursor.fetchone()

#         if not row:
#             return Response({"error": "Employee not found."}, status=404)

#         department_id,department_name ,employee_name, employee_email = row

#         # Insert resignation
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO ci_resignations (
#                     company_id, employee_id, department_id,
#                     resignation_date, reason,
#                     added_by, status, created_at
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, [
#                 2,  # company_id — static for now
#                 employee_id,
#                 department_id,
#                 resignation_date,
#                 reason,
#                 request.user.id,
#                 2,  # Pending
#                 created_at
#             ])
#             cursor.execute("SELECT LAST_INSERT_ID()")
#             resignation_id = cursor.fetchone()[0]

#         # -------------------- EMAIL SECTION --------------------

#         subject_emp = "Resignation Submitted Successfully"
#         subject_hr = "Employee Resignation Request - Pending Approval"

#         # Employee Email (Acknowledgement)
#         html_emp = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; color: #333;">
#             <h2>Resignation Submitted</h2>
#             <p>Dear <b>{employee_name}</b>,</p>
#             <p>Your resignation request has been submitted successfully on <b>{resignation_date}</b>.</p>
#             <p>Reason: {reason}</p>
#             <p>Status: <span style="color:orange; font-weight:bold;">Pending Approval</span></p>
#             <p>HR will review your request and notify you shortly.</p>
#             <p>Best regards,</p>
#             <div style="margin: 10px 0;">
#                 <img src="cid:company_logo" alt="Company Logo" style="width:150px; height:auto;">
#             </div>
#             <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
#         </body>
#         </html>
#         """

#         # HR Email (With Approve/Reject Buttons)
#         base_url = "https://tdtlworld.com/hrms-backend/"  # Replace with your actual domain
#         approve_url = f"{base_url}approve_resignation_through_mail/{resignation_id}/"  # Your approve endpoint
#         reject_url = f"{base_url}reject_resignation_through_mail/{resignation_id}/"    # Your reject endpoint

#         html_hr = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; color: #333;">
#             <h2>Employee Resignation Request</h2>
#             <p><b>Employee:</b> {employee_name} (ID: {employee_id})</p>
#             <p><b>Department:</b> {department_name}</p>
#             <p><b>Resignation Date:</b> {resignation_date}</p>
#             <p><b>Reason:</b> {reason}</p>
#             <p>Status: <span style="color:orange; font-weight:bold;">Pending</span></p>
            
#             <p>Please take action:</p>
#             <div style="margin:20px 0;">
#                 <a href="{approve_url}" 
#                 style="display:inline-block; background-color: #28a745; color: white; 
#                         padding: 10px 20px; text-decoration: none; border-radius: 8px; margin-right: 10px;">
#                 Approve
#                 </a>
#                 <a href="{reject_url}" 
#                 style="display:inline-block; background-color: #dc3545; color: white; 
#                         padding: 10px 20px; text-decoration: none; border-radius: 8px;">
#                 Reject
#                 </a>
#             </div>

#             <p>Best regards,</p>
#             <div style="margin: 10px 0;">
#                 <img src="cid:company_logo" alt="Company Logo" style="width:150px; height:auto;">
#             </div>
#             <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
#         </body>
#         </html>
#         """

#         # Send email to Employee
#         if employee_email:
#             msg_emp = EmailMultiAlternatives(subject_emp, '', settings.DEFAULT_FROM_EMAIL, [employee_email])
#             msg_emp.attach_alternative(html_emp, "text/html")
#             # Attach logo inline
#             logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
#             if os.path.exists(logo_path):
#                 with open(logo_path, 'rb') as f:
#                     logo_data = f.read()
#                 image = MIMEImage(logo_data)
#                 image.add_header('Content-ID', '<company_logo>')
#                 image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
#                 msg_emp.attach(image)
#             msg_emp.send(fail_silently=False)

#         # Send email to all HRs
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT email FROM ci_erp_users WHERE user_role_id = 5 AND email IS NOT NULL")
#             hr_emails = [row[0] for row in cursor.fetchall()]


#         for hr_email in hr_emails:
#             msg_hr = EmailMultiAlternatives(subject_hr, '', settings.DEFAULT_FROM_EMAIL, [hr_email])
#             msg_hr.attach_alternative(html_hr, "text/html")
#             if os.path.exists(logo_path):
#                 with open(logo_path, 'rb') as f:
#                     logo_data = f.read()
#                 image = MIMEImage(logo_data)
#                 image.add_header('Content-ID', '<company_logo>')
#                 image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
#                 msg_hr.attach(image)
#             msg_hr.send(fail_silently=False)

#         return Response({
#             "message": "Resignation submitted successfully, emails sent to employee and HR.",
#             "employee_id": employee_id,
#             "employee_name": employee_name,
#             "department_id": department_id,
#             "status": "Pending"
#         }, status=status.HTTP_201_CREATED)


class ResignationListCreateView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    r.resignation_id,
                    r.company_id,
                    r.employee_id,
                    r.resignation_date,
                    r.last_working_day,
                    r.reason,
                    r.added_by,
                    CASE 
                        WHEN status = 0 THEN 'Rejected'
                        WHEN status = 1 THEN 'Accepted'
                        WHEN status = 2 THEN 'Pending'
                        ELSE 'Unknown'
                    END AS status,
                    r.created_at,
                    GROUP_CONCAT(CONCAT(eu.first_name, ' ', eu.last_name)) AS employee_name,
                    GROUP_CONCAT(DISTINCT d.department_name) AS department_name
                FROM ci_resignations r
                LEFT JOIN ci_erp_users_details ed ON FIND_IN_SET(ed.employee_id, r.employee_id)
                LEFT JOIN ci_erp_users eu ON ed.user_id = eu.id
                LEFT JOIN ci_departments d ON ed.department_id = d.department_id
                GROUP BY r.resignation_id
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(data)

    def post(self, request):
        data = request.data

        # Convert status string to integer
        status_str = str(data.get("status", "")).lower()
        status_val = 1 if status_str == "approved" else 0 if status_str == "reject" else "pending"

        if status_val is None:
            return Response({"error": "Invalid status. Use 'Approved' or 'Reject'."}, status=400)

        # Fetch department_id from ci_erp_users_details using employee_id
        employee_id = data.get("employee_id")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT department_id
                FROM ci_erp_users_details
                WHERE employee_id = %s
            """, [employee_id])
            row = cursor.fetchone()

        if not row:
            return Response({"error": "Employee not found or missing department."}, status=404)

        department_id = row[0]

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_resignations 
                (company_id, employee_id, department_id, notice_date, resignation_date, reason, added_by, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                data.get("company_id"),
                employee_id,
                department_id,
                data.get("notice_date"),
                data.get("resignation_date"),
                data.get("reason"),
                data.get("added_by"),
                status_val,
                data.get("created_at")
            ])
        return Response({"message": "Resignation created successfully."}, status=status.HTTP_201_CREATED)
 

# -------------------- Admin / HR approve or reject resignation --------------------

class ResignationDetailView(APIView):
 
    def patch(self, request, resignation_id):

        data = request.data
 
        fields = []

        values = []

        status_value = None

        status_str = None
 
        # -------------------- STATUS --------------------

        if "status" in data:

            status_str = str(data["status"]).lower()

            if status_str == "approved":

                status_value = 1

            elif status_str == "reject":

                status_value = 0      # Use 3 for Rejected

            elif status_str == "pending":

                status_value = 2

            else:

                return Response({"error": "Invalid status. Use 'approved', 'reject', or 'pending'."}, status=400)
 
            fields.append("status = %s")

            values.append(status_value)
 
        # -------------------- LAST WORKING DAY --------------------

        if status_str == "approved":

            last_working_day = data.get("last_working_day")

            if not last_working_day:

                return Response({"error": "Last working day is required when approving a resignation."}, status=400)

            fields.append("last_working_day = %s")

            values.append(last_working_day)
 
        # Optional created_at

        if "created_at" in data:

            fields.append("created_at = %s")

            values.append(data["created_at"])
 
        if not fields:

            return Response({"error": "No valid fields provided."}, status=400)
 
        values.append(resignation_id)
 
        # -------------------- UPDATE RESIGNATION --------------------

        with connection.cursor() as cursor:

            cursor.execute(f"""

                UPDATE ci_resignations SET {', '.join(fields)} WHERE resignation_id = %s

            """, values)
 
        return Response({"message": "Resignation updated successfully."})
 
 
    def delete(self, request, resignation_id):

        with connection.cursor() as cursor:

            cursor.execute("DELETE FROM ci_resignations WHERE resignation_id = %s", [resignation_id])

        return Response({"message": "Resignation deleted successfully."}, status=status.HTTP_200_OK)
 
 
# -------------------- Employee get its own resignation or post resignation --------------------

class EmployeeResignationClass(APIView):
 
    def get(self, request, employee_id):

        with connection.cursor() as cursor:

            cursor.execute("""

                SELECT 

                    resignation_date, 

                    reason,

                    CASE 

                        WHEN status = 0 THEN 'Rejected'

                        WHEN status = 1 THEN 'Approved'

                        WHEN status = 2 THEN 'Pending'

                        ELSE 'Unknown'

                    END AS status

                FROM ci_resignations

                WHERE employee_id = %s

                ORDER BY created_at DESC

            """, [employee_id])

            rows = cursor.fetchall()
 
        if not rows:

            return Response({"message": "No resignation found for this employee."}, status=404)
 
        resignations = []

        for row in rows:

            resignations.append({

                "employee_id": employee_id,

                "resignation_date": row[0],

                "reason": row[1],

                "status": row[2]

            })
 
        return Response(resignations, status=200)
 
 
    def post(self, request, employee_id):

        reason = request.data.get("reason")

        if not reason:

            return Response({"error": "The 'reason' field is required."}, status=400)
 
        resignation_date = datetime.now().strftime('%Y-%m-%d')

        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 
        # Fetch employee details

        with connection.cursor() as cursor:

            cursor.execute("""

                SELECT 

                    ed.department_id,

                    d.department_name,

                    CONCAT(eu.first_name, ' ', eu.last_name) AS employee_name,

                    eu.email

                FROM ci_erp_users_details ed

                JOIN ci_erp_users eu ON ed.user_id = eu.id

                JOIN ci_departments d ON ed.department_id = d.department_id

                WHERE ed.employee_id = %s

            """, [employee_id])

            row = cursor.fetchone()
 
        if not row:

            return Response({"error": "Employee not found."}, status=404)
 
        department_id, department_name, employee_name, employee_email = row
 
        # Insert resignation

        with connection.cursor() as cursor:

            cursor.execute("""

                INSERT INTO ci_resignations (

                    company_id, employee_id, department_id,

                    resignation_date, reason,

                    added_by, status, created_at

                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

            """, [

                2,                 # company_id

                employee_id,

                department_id,

                resignation_date,

                reason,

                request.user.id,

                2,                 # Pending

                created_at

            ])

            cursor.execute("SELECT LAST_INSERT_ID()")

            resignation_id = cursor.fetchone()[0]
 
        return Response({

            "message": "Resignation submitted successfully.",

            "employee_id": employee_id,

            "employee_name": employee_name,

            "department_id": department_id,

            "resignation_date": resignation_date,

            "reason": reason,

            "status": "Pending"

        }, status=status.HTTP_201_CREATED)

 


# # Admin / HR approve or reject resignation
# class ResignationDetailView(APIView):

#     # def patch(self, request, resignation_id):
#     #     data = request.data

#     #     fields = []
#     #     values = []
#     #     status_value = None
#     #     status_str = None
        
#     #     if "last_working_day" in data:
#     #         fields.append("last_working_day = %s")
#     #         values.append(data["last_working_day"])

#     #     if "status" in data:
#     #         status_str = str(data["status"]).lower()
#     #         if status_str == "approved":
#     #             status_value = 1
#     #         elif status_str == "reject":
#     #             status_value = 0
#     #         elif status_str == "pending":
#     #             status_value = 2
#     #         else:
#     #             return Response({"error": "Invalid status. Use 'Approved' or 'Reject'."}, status=400)
#     #         fields.append("status = %s")
#     #         values.append(status_value)
            
#     #     if "created_at" in data:
#     #         fields.append("created_at = %s")
#     #         values.append(data["created_at"])

#     #     if not fields:
#     #         return Response({"error": "No valid fields provided."}, status=400)

#     #     values.append(resignation_id)

#     #     # Fetch employee details before updating
#     #     employee_email = None
#     #     employee_name = None
#     #     resignation_date = None
#     #     reason = None
        
#     #     with connection.cursor() as cursor:
#     #         cursor.execute("""
#     #             SELECT eu.email, CONCAT(eu.first_name, ' ', eu.last_name) AS employee_name,
#     #                    r.resignation_date, r.reason
#     #             FROM ci_resignations r
#     #             JOIN ci_erp_users_details ed ON r.employee_id = ed.employee_id
#     #             JOIN ci_erp_users eu ON ed.user_id = eu.id
#     #             WHERE r.resignation_id = %s
#     #         """, [resignation_id])
#     #         row = cursor.fetchone()
            
#     #         if row:
#     #             employee_email, employee_name, resignation_date, reason = row

#     #     # Update the resignation
#     #     with connection.cursor() as cursor:
#     #         cursor.execute(f"""
#     #             UPDATE ci_resignations SET {', '.join(fields)} WHERE resignation_id = %s
#     #         """, values)

#     #     # Send email notification if status was changed
#     #     if status_value is not None and employee_email:
#     #         self.send_status_notification(
#     #             employee_email, 
#     #             employee_name, 
#     #             status_str, 
#     #             resignation_date, 
#     #             reason
#     #         )

#     #     return Response({"message": "Resignation updated successfully."})

#     # def send_status_notification(self, employee_email, employee_name, status, resignation_date, reason):
#     #     # Determine email subject and content based on status
#     #     if status == "approved":
#     #         subject = "Resignation Approved"
#     #         status_text = "Approved"
#     #         status_color = "green"
#     #         message = "Your resignation has been approved. Please work with HR to complete the offboarding process."
#     #     elif status == "reject":
#     #         subject = "Resignation Rejected"
#     #         status_text = "Rejected"
#     #         status_color = "red"
#     #         message = "Your resignation has been rejected. Please contact HR for more details."
#     #     else:
#     #         # For pending status, no need to send email
#     #         return

#     #     # Create HTML email content
#     #     html_content = f"""
#     #     <html>
#     #     <body style="font-family: Arial, sans-serif; color: #333;">
#     #         <h2>Resignation Status Update</h2>
#     #         <p>Dear <b>{employee_name}</b>,</p>
#     #         <p>Your resignation request submitted on <b>{resignation_date}</b> has been updated.</p>
#     #         <p>Reason: {reason}</p>
#     #         <p>Status: <span style="color:{status_color}; font-weight:bold;">{status_text}</span></p>
#     #         <p>{message}</p>
#     #         <p>Best regards,</p>
#     #         <div style="margin: 10px 0;">
#     #             <img src="cid:company_logo" alt="Company Logo" style="width:150px; height:auto;">
#     #         </div>
#     #         <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
#     #     </body>
#     #     </html>
#     #     """

#     #     # Send email to employee
#     #     msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [employee_email])
#     #     msg.attach_alternative(html_content, "text/html")
        
#     #     # Attach logo inline
#     #     logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
#     #     if os.path.exists(logo_path):
#     #         with open(logo_path, 'rb') as f:
#     #             logo_data = f.read()
#     #         image = MIMEImage(logo_data)
#     #         image.add_header('Content-ID', '<company_logo>')
#     #         image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
#     #         msg.attach(image)
            
#     #     msg.send(fail_silently=False)


#     def patch(self, request, resignation_id):
#         data = request.data

#         fields = []
#         values = []
#         status_value = None
#         status_str = None

#         # -------------------- STATUS --------------------
#         if "status" in data:
#             status_str = str(data["status"]).lower()
#             if status_str == "approved":
#                 status_value = 1
#             elif status_str == "reject":
#                 status_value = 3         # Use 3 for Rejected
#             elif status_str == "pending":
#                 status_value = 2
#             else:
#                 return Response({"error": "Invalid status. Use 'approved', 'reject', or 'pending'."}, status=400)
            
#             fields.append("status = %s")
#             values.append(status_value)

#         # -------------------- LAST WORKING DAY --------------------
#         # If status is Approved, last_working_day is mandatory
#         if status_str == "approved":
#             last_working_day = data.get("last_working_day")
#             if not last_working_day:
#                 return Response({"error": "Last working day is required when approving a resignation."}, status=400)
#             fields.append("last_working_day = %s")
#             values.append(last_working_day)

#         # Optional created_at update
#         if "created_at" in data:
#             fields.append("created_at = %s")
#             values.append(data["created_at"])

#         if not fields:
#             return Response({"error": "No valid fields provided."}, status=400)

#         values.append(resignation_id)

#         # -------------------- FETCH EMPLOYEE DETAILS --------------------
#         employee_email = None
#         employee_name = None
#         resignation_date = None
#         reason = None

#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT eu.email, CONCAT(eu.first_name, ' ', eu.last_name) AS employee_name,
#                     r.resignation_date, r.reason
#                 FROM ci_resignations r
#                 JOIN ci_erp_users_details ed ON r.employee_id = ed.employee_id
#                 JOIN ci_erp_users eu ON ed.user_id = eu.id
#                 WHERE r.resignation_id = %s
#             """, [resignation_id])
#             row = cursor.fetchone()

#             if row:
#                 employee_email, employee_name, resignation_date, reason = row

#         # -------------------- UPDATE RESIGNATION --------------------
#         with connection.cursor() as cursor:
#             cursor.execute(f"""
#                 UPDATE ci_resignations SET {', '.join(fields)} WHERE resignation_id = %s
#             """, values)

#         # -------------------- SEND EMAIL NOTIFICATION --------------------
#         if status_value is not None and employee_email:
#             self.send_status_notification(
#                 employee_email,
#                 employee_name,
#                 status_str,
#                 resignation_date,
#                 reason,
#                 data.get("last_working_day")  # Pass LWD for approved status
#             )

#         return Response({"message": "Resignation updated successfully."})


#     # -------------------- EMAIL FUNCTION --------------------
#     # def send_status_notification(self, employee_email, employee_name, status, resignation_date, reason, last_working_day=None):
#     #     # Determine email subject and content
#     #     if status == "approved":
#     #         subject = "Resignation Approved"
#     #         status_text = "Approved"
#     #         status_color = "green"
#     #         message = f"Your resignation has been approved. Your last working day is set as <b>{last_working_day}</b>. Please work with HR to complete the offboarding process."
#     #     elif status == "reject":
#     #         subject = "Resignation Rejected"
#     #         status_text = "Rejected"
#     #         status_color = "red"
#     #         message = "Your resignation has been rejected. Please contact HR for more details."
#     #     else:
#     #         # Pending → no email
#     #         return

#     #     # Create HTML email content
#     #     html_content = f"""
#     #     <html>
#     #     <body style="font-family: Arial, sans-serif; color: #333;">
#     #         <h2>Resignation Status Update</h2>
#     #         <p>Dear <b>{employee_name}</b>,</p>
#     #         <p>Your resignation request submitted on <b>{resignation_date}</b> has been updated.</p>
#     #         <p>Reason: {reason}</p>
#     #         <p>Status: <span style="color:{status_color}; font-weight:bold;">{status_text}</span></p>
#     #         <p>{message}</p>
#     #         <p>Best regards,</p>
#     #         <div style="margin: 10px 0;">
#     #             <img src="cid:company_logo" alt="Company Logo" style="width:150px; height:auto;">
#     #         </div>
#     #         <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
#     #     </body>
#     #     </html>
#     #     """

#     #     # Send email
#     #     msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [employee_email])
#     #     msg.attach_alternative(html_content, "text/html")

#     #     # Attach logo inline
#     #     logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
#     #     if os.path.exists(logo_path):
#     #         with open(logo_path, 'rb') as f:
#     #             logo_data = f.read()
#     #         image = MIMEImage(logo_data)
#     #         image.add_header('Content-ID', '<company_logo>')
#     #         image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
#     #         msg.attach(image)

#     #     msg.send(fail_silently=False)


#     def delete(self, request, resignation_id):
#         with connection.cursor() as cursor:
#             cursor.execute("DELETE FROM ci_resignations WHERE resignation_id = %s", [resignation_id])
#         return Response({"message": "Resignation deleted successfully."}, status=status.HTTP_200_OK)


 




# # Employee get its own resigantion or post resignation
# class EmployeeResignationClass(APIView):

#     def get(self, request, employee_id):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     resignation_date, 
#                     reason,
#                     CASE 
#                         WHEN status = 0 THEN 'Rejected'
#                         WHEN status = 1 THEN 'Approved'
#                         WHEN status = 2 THEN 'Pending'
#                         ELSE 'Unknown'
#                     END AS status
#                 FROM ci_resignations
#                 WHERE employee_id = %s
#                 ORDER BY created_at DESC
#             """, [employee_id])
#             rows = cursor.fetchall()

#         if not rows:
#             return Response({"message": "No resignation found for this employee."}, status=404)

#         resignations = []
#         for row in rows:
#             resignations.append({
#                 "employee_id": employee_id,
#                 "resignation_date": row[0],
#                 "reason": row[1],
#                 "status": row[2]
#             })

#         return Response(resignations, status=200)


#     def post(self, request, employee_id):
#         # ✅ Employee posts ONLY the reason
#         reason = request.data.get("reason")

#         if not reason:
#             return Response({"error": "The 'reason' field is required."}, status=400)

#         # ✅ Both resignation_date and created_at are set to current date/time
#         resignation_date = datetime.now().strftime('%Y-%m-%d')
#         created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         # Fetch department_id, employee_name, and email
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     ed.department_id,
#                      d.department_name,
#                     CONCAT(eu.first_name, ' ', eu.last_name) AS employee_name,
#                     eu.email
#                 FROM ci_erp_users_details ed
#                 JOIN ci_erp_users eu ON ed.user_id = eu.id
#                 JOIN ci_departments d ON ed.department_id = d.department_id
#                 WHERE ed.employee_id = %s
#             """, [employee_id])
#             row = cursor.fetchone()

#         if not row:
#             return Response({"error": "Employee not found."}, status=404)

#         department_id,department_name ,employee_name, employee_email = row

#         # Insert resignation
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO ci_resignations (
#                     company_id, employee_id, department_id,
#                     resignation_date, reason,
#                     added_by, status, created_at
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#             """, [
#                 2,  # company_id — static for now
#                 employee_id,
#                 department_id,
#                 resignation_date,
#                 reason,
#                 request.user.id,
#                 2,  # Pending
#                 created_at 
#             ])
#             cursor.execute("SELECT LAST_INSERT_ID()")
#             resignation_id = cursor.fetchone()[0]

#         # # -------------------- EMAIL SECTION --------------------

#         # subject_emp = "Resignation Submitted Successfully"
#         # subject_hr = "Employee Resignation Request - Pending Approval"

#         # # Employee Email (Acknowledgement)
#         # html_emp = f"""
#         # <html>
#         # <body style="font-family: Arial, sans-serif; color: #333;">
#         #     <h2>Resignation Submitted</h2>
#         #     <p>Dear <b>{employee_name}</b>,</p>
#         #     <p>Your resignation request has been submitted successfully on <b>{resignation_date}</b>.</p>
#         #     <p>Reason: {reason}</p>
#         #     <p>Status: <span style="color:orange; font-weight:bold;">Pending Approval</span></p>
#         #     <p>HR will review your request and notify you shortly.</p>
#         #     <p>Best regards,</p>
#         #     <div style="margin: 10px 0;">
#         #         <img src="cid:company_logo" alt="Company Logo" style="width:150px; height:auto;">
#         #     </div>
#         #     <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
#         # </body>
#         # </html>
#         # """

#         # # HR Email (With Approve/Reject Buttons)
#         # base_url = "https://tdtlworld.com/hrms-backend/"  # Replace with your actual domain
#         # approve_url = f"{base_url}approve_resignation_through_mail/{resignation_id}/"  # Your approve endpoint
#         # reject_url = f"{base_url}reject_resignation_through_mail/{resignation_id}/"    # Your reject endpoint

#         # html_hr = f"""
#         # <html>
#         # <body style="font-family: Arial, sans-serif; color: #333;">
#         #     <h2>Employee Resignation Request</h2>
#         #     <p><b>Employee:</b> {employee_name} (ID: {employee_id})</p>
#         #     <p><b>Department:</b> {department_name}</p>
#         #     <p><b>Resignation Date:</b> {resignation_date}</p>
#         #     <p><b>Reason:</b> {reason}</p>
#         #     <p>Status: <span style="color:orange; font-weight:bold;">Pending</span></p>
            
#         #     <p>Please take action:</p>
#         #     <div style="margin:20px 0;">
#         #         <a href="{approve_url}" 
#         #         style="display:inline-block; background-color: #28a745; color: white; 
#         #                 padding: 10px 20px; text-decoration: none; border-radius: 8px; margin-right: 10px;">
#         #         Approve
#         #         </a>
#         #         <a href="{reject_url}" 
#         #         style="display:inline-block; background-color: #dc3545; color: white; 
#         #                 padding: 10px 20px; text-decoration: none; border-radius: 8px;">
#         #         Reject
#         #         </a>
#         #     </div>

#         #     <p>Best regards,</p>
#         #     <div style="margin: 10px 0;">
#         #         <img src="cid:company_logo" alt="Company Logo" style="width:150px; height:auto;">
#         #     </div>
#         #     <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
#         # </body>
#         # </html>
#         # """

#         # # Send email to Employee
#         # if employee_email:
#         #     msg_emp = EmailMultiAlternatives(subject_emp, '', settings.DEFAULT_FROM_EMAIL, [employee_email])
#         #     msg_emp.attach_alternative(html_emp, "text/html")
#         #     # Attach logo inline
#         #     logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
#         #     if os.path.exists(logo_path):
#         #         with open(logo_path, 'rb') as f:
#         #             logo_data = f.read()
#         #         image = MIMEImage(logo_data)
#         #         image.add_header('Content-ID', '<company_logo>')
#         #         image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
#         #         msg_emp.attach(image)
#         #     msg_emp.send(fail_silently=False)

#         # # Send email to all HRs
#         # with connection.cursor() as cursor:
#         #     cursor.execute("SELECT email FROM ci_erp_users WHERE user_role_id = 5 AND email IS NOT NULL")
#         #     hr_emails = [row[0] for row in cursor.fetchall()]


#         # for hr_email in hr_emails:
#         #     msg_hr = EmailMultiAlternatives(subject_hr, '', settings.DEFAULT_FROM_EMAIL, [hr_email])
#         #     msg_hr.attach_alternative(html_hr, "text/html")
#         #     if os.path.exists(logo_path):
#         #         with open(logo_path, 'rb') as f:
#         #             logo_data = f.read()
#         #         image = MIMEImage(logo_data)
#         #         image.add_header('Content-ID', '<company_logo>')
#         #         image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
#         #         msg_hr.attach(image)
#         #     msg_hr.send(fail_silently=False)

#         return Response({
#             "message": "Resignation submitted successfully, emails sent to employee and HR.",
#             "employee_id": employee_id,
#             "employee_name": employee_name,
#             "department_id": department_id,
#             "resignation_date": resignation_date,
#             "reason": reason,
#             "status": "Pending"
#         }, status=status.HTTP_201_CREATED)


class DisciplinaryCasesView(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    w.warning_id,
                    w.company_id,
                    w.Warning_to,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    sr.role_name AS warning_by,
                    w.warning_date,
                    w.attachment,
                    w.subject,
                    w.description,
                    w.created_at,
                    w.warning_type_id
                FROM 
                    ci_warnings w
                LEFT JOIN 
                    ci_erp_users_details ud ON w.Warning_to = ud.employee_id
                LEFT JOIN 
                    ci_erp_users u ON ud.user_id = u.id
                LEFT JOIN 
                     ci_staff_roles sr ON w.warning_by = sr.role_id
                ORDER BY 
                    w.created_at DESC
            """)
            rows = cursor.fetchall()

# Then build your response JSON with employee_name instead of just Warning_to

        columns = [
            "warning_id", "company_id", "warning_to", "employee_name", "warning_by",
            "warning_date", "attachment", "subject", "description", "created_at", "warning_type_id"
        ]

        data = [dict(zip(columns, row)) for row in rows]
        return Response(data)

    def post(self, request):
        data = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_warnings 
                        (company_id, Warning_to, Warning_by, warning_date, attachment, subject, description, created_at, warning_type_id)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data.get("company_id", 2),
                    data["Warning_to"],
                    data["Warning_by"],
                    data["warning_date"],
                    data.get("attachment"),
                    data["subject"],
                    data.get("description"),
                    datetime.now(),
                    data["warning_type_id"]
                ])
            return Response({"message": "Disciplinary case created successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        data = request.data
        update_fields = []
        params = []

        for field in ["Warning_to", "Warning_by", "warning_date", "attachment", "subject", "description", "warning_type_id"]:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])

        if not update_fields:
            return Response({"error": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

        params.append(pk)

        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE ci_warnings
                SET {', '.join(update_fields)}
                WHERE warning_id = %s
            """, params)

        return Response({"message": "Disciplinary case updated successfully."})

    def delete(self, request, pk):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ci_warnings WHERE warning_id = %s", [pk])
        return Response({"message": "Disciplinary case deleted successfully."}, status=status.HTTP_200)



class DepartmentDropdownAPI(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        department_id, 
                        department_name, 
                        department_code 
                    FROM ci_departments
                """)
                columns = [col[0] for col in cursor.description]
                departments = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
            return Response({"status": True, "data": departments})
        except Exception as e:
            return Response({"status": False, "error": str(e)})




class DesignationDropdownAPI(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        designation_id, 
                        designation_name, 
                        designation_code 
                    FROM ci_designations
                """)
                columns = [col[0] for col in cursor.description]
                designations = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
            return Response({"status": True, "data": designations})
        except Exception as e:
            return Response({"status": False, "error": str(e)})            




class CaseTypeDropdownView(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    constants_id AS value,
                    category_name AS label,
                    created_at
                FROM
                    ci_erp_constants
                WHERE
                    type = 'warning_type'
                ORDER BY
                    category_name ASC
            """)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            created_at = row[2]
            created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None
            data.append({
                "value": row[0],
                "label": row[1],
                "created_at": created_at_str
            })

        return Response(data)

    def post(self, request):
        category_name = request.data.get("category_name")

        if not category_name:
            return Response({"error": "category_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = 2  # Default company ID
        created_at = datetime.now()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_erp_constants (category_name, type, company_id, created_at)
                VALUES (%s, %s, %s, %s)
            """, [category_name, 'warning_type', company_id, created_at])

        return Response({"message": "Case type added successfully."}, status=status.HTTP_201_CREATED)







class TodaysAttendanceReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.today().strftime("%Y-%m-%d")

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    CONCAT(cu.first_name, ' ', cu.last_name) AS employee,
                    cu.email,
                    cb.emp_id,
                    cb.login_date AS date,
                    cb.status,
                    cb.clock_in,
                    cb.clock_out,
                    cb.late_mark AS late,
                    cb.early_mark AS early_leaving,
                    cb.total_work
                FROM 
					ci_biomatric_data cb
                LEFT JOIN 
					ci_erp_users cu
					ON cb.emp_id = cu.id  
                WHERE 
                    date(cb.login_date) = %s 
                ORDER BY 
                    cu.first_name ASC;
            """,[today])

            columns = ["employee", "email", "emp_id", "date", "status", "clock_in", "clock_out", "late", "early_leaving", "total_work"]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({
            "date": today,
            "total_records": len(results),
            "data": results
        })







class AttendanceByDateReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        emp_id = request.data.get("emp_id")
        date = request.data.get("date")
        login_status = request.data.get("status")

        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    CONCAT(cu.first_name, ' ', cu.last_name) AS employee,
                    cu.email,
                    cb.emp_id,
                    cb.attendance_date AS date,
                    cb.attendance_status AS status,
                    cb.clock_in,
                    cb.clock_out,
                    cb.late_mark AS late,
                    cb.early_mark AS early_leaving,
                    cb.total_work
                FROM 
					ci_biomatric_data cb
                LEFT JOIN 
					ci_erp_users cu
					ON cb.emp_id = cu.id  
                WHERE 
                    date(cb.attendance_date) = %s and 
                           cb.emp_id=%s and
                           cb.status=%s 
                ORDER BY 
                    cu.first_name ASC;
            """, [date,emp_id, status])

            columns = ["employee", "email", "emp_id", "date", "status", "clock_in", "clock_out", "late", "early_leaving", "total_work"]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({
            "date": date,
            "total_records": len(results),
            "data": results
        })






class AwardsView(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.award_id,
                    a.company_id,
                    a.employee_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    a.award_type_id,
                    c.category_name AS award_type_name,
                    a.associated_goals,
                    a.gift_item,
                    a.cash_price,
                    a.award_photo,
                    a.award_month_year,
                    a.award_information,
                    a.description,
                    a.created_at
                FROM 
                    ci_awards a
                LEFT JOIN 
                    ci_erp_users_details ud ON a.employee_id = ud.employee_id
                LEFT JOIN 
                    ci_erp_users u ON ud.user_id = u.id
                LEFT JOIN
                    ci_erp_constants c ON a.award_type_id = c.constants_id AND c.type = 'award_type' 
                ORDER BY 
                    a.created_at DESC
            """)
            rows = cursor.fetchall()

        columns = [
            "award_id", "company_id", "employee_id", "employee_name", "award_type_id", "award_type_name",
            "associated_goals", "gift_item", "cash_price", "award_photo", 
            "award_month_year", "award_information", "description", "created_at"
        ]

        data = [dict(zip(columns, row)) for row in rows]
        return Response(data)

    def post(self, request):
        data = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_awards 
                        (company_id, employee_id, award_type_id, associated_goals, gift_item, 
                         cash_price, award_photo, award_month_year, award_information, 
                         description, created_at)
                    VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data.get("company_id", 2),
                    data["employee_id"],
                    data["award_type_id"],
                    data.get("associated_goals"),
                    data.get("gift_item"),
                    data.get("cash_price"),
                    data.get("award_photo"),
                    data["award_month_year"],
                    data.get("award_information"),
                    data.get("description"),
                    datetime.now()
                ])
            return Response({"message": "Award created successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        data = request.data
        update_fields = []
        params = []

        for field in [
            "employee_id", "award_type_id", "associated_goals", "gift_item", "cash_price", 
            "award_photo", "award_month_year", "award_information", "description"
        ]:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])

        if not update_fields:
            return Response({"error": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

        params.append(pk)

        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE ci_awards
                SET {', '.join(update_fields)}
                WHERE award_id = %s
            """, params)

        return Response({"message": "Award updated successfully."})

    def delete(self, request, pk):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ci_awards WHERE award_id = %s", [pk])
        return Response({"message": "Award deleted successfully."}, status=status.HTTP_200_OK)



# Employee award get view
class EmployeeAwardsView(APIView):
    def get(self, request, employee_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.category_name AS award_type,
                    a.gift_item AS award_gift,
                    a.cash_price AS award_cash,
                    a.award_month_year AS month_year
                FROM ci_awards a
                LEFT JOIN ci_erp_constants c ON a.award_type_id = c.constants_id AND c.type = 'award_type'
                WHERE a.employee_id = %s
                ORDER BY a.created_at DESC
            """, [employee_id])

            rows = cursor.fetchall()

        columns = ["award_type", "award_gift", "award_cash", "month_year"]
        data = [dict(zip(columns, row)) for row in rows]

        return Response(data)



class EmployeeEventView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, employee_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        event_title,
                        event_date,
                        event_time
                    FROM 
                        ci_events
                    WHERE 
                        employee_id = %s
                    ORDER BY 
                        event_date ASC, event_time ASC
                """, [employee_id])

                rows = cursor.fetchall()

            columns = ["event_title", "event_date", "event_time"]
            data = [dict(zip(columns, row)) for row in rows]
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





# class AdminAssetsView(APIView):

#     def get(self, request):
        
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     a.id,
#                     a.assets_category_id,
#                     cat.category_name AS assets_category_name,
#                     a.brand_id,
#                     b.category_name AS assets_brand_name,
#                     a.company_id,
#                     a.employee_id,
#                     CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                     a.company_asset_code,
#                     a.assets_name,
#                     a.purchase_date,
#                     a.invoice_number,
#                     a.manufacturer,
#                     a.serial_number,
#                     a.warranty_end_date,
#                     a.asset_note,
#                     a.asset_image,
#                     a.is_working,
#                     a.created_at,
#                     a.returned,
#                     a.employee_confirmation,
#                     a.return_request_status
#                 FROM 
#                     ci_assets a
#                 LEFT JOIN 
#                     ci_erp_constants cat ON a.assets_category_id = cat.constants_id
#                 LEFT JOIN 
#                     ci_erp_constants b ON a.brand_id = b.constants_id AND b.type = 'assets_brand'
#                 LEFT JOIN 
#                     ci_erp_users_details ud ON a.employee_id = ud.employee_id
#                 LEFT JOIN 
#                     ci_erp_users u ON ud.user_id = u.id
#                 ORDER BY 
#                     a.created_at DESC
#             """)
#             rows = cursor.fetchall()

#         columns = [
#             "id", "assets_category_id", "category_name", "brand_id", "brand_name",
#             "company_id", "employee_id", "employee_name", "company_asset_code", "assets_name",
#             "purchase_date", "invoice_number", "manufacturer", "serial_number",
#             "warranty_end_date", "asset_note", "asset_image", "is_working",
#             "created_at", "returned", "employee_confirmation", "return_request_status"
#         ]

#         data = []
#         for row in rows:
#             item = dict(zip(columns, row))
#             item["is_working"] = "Yes" if item["is_working"] in (1, '1', True) else "No"
#             data.append(item)

#         return Response(data)
 
    
#     def post(self, request):
#         data = request.data
#         company_id = 2

#         # Required fields
#         required_fields = [
#             "assets_name", 
#             "assets_category_id", 
#             "brand_id", 
#             "employee_id", 
#             "purchase_date", 
#             "serial_number"
#         ]
#         for field in required_fields:
#             if not data.get(field):
#                 return Response({"error": f"Missing required field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

#         # Handle optional and boolean conversion
#         is_working_input = str(data.get("is_working", "")).strip().lower()
#         is_working = 1 if is_working_input in ("yes", "1", "true") else 0

#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_assets (
#                         assets_category_id, brand_id, employee_id, company_id,
#                         manufacturer, serial_number, company_asset_code, assets_name,
#                         is_working, purchase_date, invoice_number, warranty_end_date,
#                         asset_note, asset_image, created_at, returned, return_request_status
#                     ) VALUES (
#                         %s, %s, %s, %s,
#                         %s, %s, %s, %s,
#                         %s, %s, %s, %s,
#                         %s, %s, %s, %s, %s
#                     )
#                 """, [
#                     data["assets_category_id"],
#                     data["brand_id"],
#                     data["employee_id"],
#                     company_id,
#                     data.get("manufacturer", "") or "",
#                     data["serial_number"],
#                     data.get("company_asset_code", "") or "",
#                     data["assets_name"],
#                     is_working,
#                     data["purchase_date"],
#                     data.get("invoice_number", "") or "",
#                     data.get("warranty_end_date", "") or "",
#                     data.get("asset_note", "") or "",
#                     data.get("asset_image", "") or "",
#                     datetime.now(),
#                     'N',
#                     '0'
#                 ])
#             return Response({"message": "Asset created successfully."}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 

#     def patch(self, request, pk):
#         action = request.data.get("action", "").strip().lower()
#         # user_role = request.user.role 

#         # if user_role == 'employee' and action in ['return_yes', 'return_no']:
#         #     return Response({"error": "Unauthorized action"}, status=403)


#         if action == "return_yes":
#             try:
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE ci_assets
#                         SET returned = 'Y', return_request_status = '2'
#                         WHERE id = %s
#                     """, [pk])
#                 return Response({"message": "Return confirmed. Asset marked as returned."}, status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         elif action == "return_no":
#             try:
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE ci_assets
#                         SET return_request_status = '0'
#                         WHERE id = %s
#                     """, [pk])
#                 return Response({"message": "Return request denied. Asset remains allocated."}, status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         # Default patch for updating asset fields
#         data = request.data
#         update_fields = []
#         params = []

#         for field in [
#             "assets_category_id", "brand_id", "company_id", "employee_id",
#             "company_asset_code", "assets_name", "purchase_date", "invoice_number",
#             "manufacturer", "serial_number", "warranty_end_date", "asset_note",
#             "asset_image", "is_working", "returned", "return_request_status"
#         ]:
#             if field in data:
#                 value = data[field]
#                 if field == "is_working":
#                     value = str(value).strip().lower()
#                     value = 1 if value in ("yes", "1", "true") else 0
#                 update_fields.append(f"{field} = %s")
#                 params.append(value)

#         if not update_fields:
#             return Response({"error": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

#         params.append(pk)

#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute(f"""
#                     UPDATE ci_assets
#                     SET {', '.join(update_fields)}
#                     WHERE id = %s
#                 """, params)
#             return Response({"message": "Asset updated successfully."}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("DELETE FROM ci_assets WHERE id = %s", [pk])
#             return Response({"message": "Asset deleted successfully."}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
from django.core.mail import send_mail
from django.conf import settings

class AdminAssetsView(APIView):

    # def get(self, request, pk=None):
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT 
    #                 a.id,
    #                 a.assets_category_id,
    #                 cat.category_name AS assets_category_name,
    #                 a.brand_id,
    #                 b.category_name AS assets_brand_name,
    #                 a.company_id,
    #                 a.employee_id,
    #                 CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    #                 a.company_asset_code,
    #                 a.assets_name,
    #                 a.purchase_date,
    #                 a.invoice_number,
    #                 a.manufacturer,
    #                 a.serial_number,
    #                 a.warranty_end_date,
    #                 a.asset_note,
    #                 a.asset_image,
    #                 a.is_working,
    #                 a.created_at,
    #                 a.returned,
    #                 a.employee_confirmation,
    #                 a.return_request_status,
    #                 a.quantity
    #             FROM 
    #                 ci_assets a
    #             LEFT JOIN 
    #                 ci_erp_constants cat ON a.assets_category_id = cat.constants_id
    #             LEFT JOIN 
    #                 ci_erp_constants b ON a.brand_id = b.constants_id AND b.type = 'assets_brand'
    #             LEFT JOIN 
    #                 ci_erp_users_details ud ON a.employee_id = ud.employee_id
    #             LEFT JOIN 
    #                 ci_erp_users u ON ud.user_id = u.id
    #             ORDER BY 
    #                 a.created_at DESC
    #         """)
    #         rows = cursor.fetchall()

    #     columns = [
    #         "id", "assets_category_id", "category_name", "brand_id", "brand_name",
    #         "company_id", "employee_id", "employee_name", "company_asset_code", "assets_name",
    #         "purchase_date", "invoice_number", "manufacturer", "serial_number",
    #         "warranty_end_date", "asset_note", "asset_image", "is_working",
    #         "created_at", "returned", "employee_confirmation", "return_request_status","quantity"
    #     ]

    #     data = []
    #     for row in rows:
    #         item = dict(zip(columns, row))
    #         item["is_working"] = "Yes" if item["is_working"] in (1, '1', True) else "No"
    #         data.append(item)

    #     return Response(data)

    # # def post(self, request):
    # #     data = request.data
    # #     company_id = 2

    # #     # Required fields
    # #     required_fields = [
    # #         "assets_name", 
    # #         "assets_category_id", 
    # #         "brand_id", 
    # #         "employee_id", 
    # #         "purchase_date", 
    # #         "serial_number"
    # #     ]
    # #     for field in required_fields:
    # #         if not data.get(field):
    # #             return Response({"error": f"Missing required field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

    # #     # Handle optional and boolean conversion
    # #     is_working_input = str(data.get("is_working", "")).strip().lower()
    # #     is_working = 1 if is_working_input in ("yes", "1", "true") else 0

    # #     try:
    # #         with connection.cursor() as cursor:
    # #             # Insert the new asset
    # #             cursor.execute("""
    # #                 INSERT INTO ci_assets (
    # #                     assets_category_id, brand_id, employee_id, company_id,
    # #                     manufacturer, serial_number, company_asset_code, assets_name,
    # #                     is_working, purchase_date, invoice_number, warranty_end_date,
    # #                     asset_note, asset_image, created_at, returned, return_request_status
    # #                 ) VALUES (
    # #                     %s, %s, %s, %s,
    # #                     %s, %s, %s, %s,
    # #                     %s, %s, %s, %s,
    # #                     %s, %s, %s, %s, %s
    # #                 )
    # #             """, [
    # #                 data["assets_category_id"],
    # #                 data["brand_id"],
    # #                 data["employee_id"],
    # #                 company_id,
    # #                 data.get("manufacturer", "") or "",
    # #                 data["serial_number"],
    # #                 data.get("company_asset_code", "") or "",
    # #                 data["assets_name"],
    # #                 is_working,
    # #                 data["purchase_date"],
    # #                 data.get("invoice_number", "") or "",
    # #                 data.get("warranty_end_date", "") or "",
    # #                 data.get("asset_note", "") or "",
    # #                 data.get("asset_image", "") or "",
    # #                 datetime.now(),
    # #                 'N',
    # #                 '0'
    # #             ])

    # #             # Fetch employee's name & email
    # #             cursor.execute("""
    # #                 SELECT first_name, last_name, email
    # #                 FROM ci_erp_users
    # #                 WHERE username = %s
    # #             """, [data["employee_id"]])
    # #             employee = cursor.fetchone()

    # #         # If employee found, send HTML email
    # #         if employee:
    # #             first_name, last_name, email = employee
    # #             employee_name = f"{first_name} {last_name}".strip()

    # #             # Formatted HTML Email
    # #             subject = f"New Asset Allocated: {data['assets_name']}"
    # #             html_content = f"""
    # #             <html>
    # #             <body style="font-family: Arial, sans-serif; color: #333;">
    # #                 <h2>New Asset Allocation</h2>
    # #                 <p>Dear <b>{employee_name}</b>,</p>
                    
    # #                 <p>A new asset has been allocated to you.</p>
                    
    # #                 <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
    # #                     <p><b>Asset Name:</b> {data['assets_name']}</p>
    # #                     <p><b>Serial Number:</b> {data['serial_number']}</p>
    # #                     <p><b>Purchase Date:</b> {data['purchase_date']}</p>
    # #                 </div>
                    
    # #                 <p style="color: #3794ff; font-weight: bold;">
    # #                     Please log in to your employee dashboard and confirm that you have received this asset.
    # #                 </p>
                    
    # #                 <p>If you have any issues with the asset or require further assistance, 
    # #                 kindly contact the IT department.</p>
                    
    # #                 <p>Best regards,</p>
    # #                 <div style="margin: 10px 0;">
    # #                     <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
    # #                 </div>
    # #                 <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
    # #                 <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
    # #                     © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
    # #                 </div>
    # #             </body>
    # #             </html>
    # #             """
                
    # #             msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
    # #             msg.attach_alternative(html_content, "text/html")

    # #             # Attach logo inline
    # #             logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
    # #             if os.path.exists(logo_path):
    # #                 with open(logo_path, 'rb') as f:
    # #                     logo_data = f.read()
    # #                 image = MIMEImage(logo_data)
    # #                 image.add_header('Content-ID', '<company_logo>')
    # #                 image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
    # #                 msg.attach(image)

    # #             msg.send(fail_silently=False)

    # #         return Response({"message": "Asset created successfully and email sent."}, status=status.HTTP_201_CREATED)

    # #     except Exception as e:
    # #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    # def post(self, request, pk=None):
    #     data = request.data
    #     company_id = 2
    
    #     # Required fields
    #     required_fields = [
    #         "assets_name", 
    #         "assets_category_id", 
    #         "brand_id", 
    #         "employee_id", 
    #         "purchase_date", 
    #         "serial_number",
    #         "product_id"
    #     ]
    #     for field in required_fields:
    #         if not data.get(field):
    #             return Response({"error": f"Missing required field: {field}"}, status=status.HTTP_400_BAD_REQUEST)
    
    #     # Handle optional and boolean conversion
    #     is_working_input = str(data.get("is_working", "")).strip().lower()
    #     is_working = 1 if is_working_input in ("yes", "1", "true") else 0
    
    #     try:
    #         with connection.cursor() as cursor:
    #             # Insert the new asset (fixed quantity placement)
    #             cursor.execute("""
    #                 INSERT INTO ci_assets (
    #                     assets_category_id, brand_id,product_id, employee_id, company_id,
    #                     manufacturer, serial_number, company_asset_code, assets_name, quantity,
    #                     is_working, purchase_date, invoice_number, warranty_end_date,
    #                     asset_note, asset_image, created_at, returned, return_request_status
    #                 ) VALUES (
    #                     %s, %s, %s, %s, %s,%s,
    #                     %s, %s, %s, %s,
    #                     %s, %s, %s, %s,
    #                     %s, %s, %s, %s, %s
    #                 )
    #             """, [
    #                 data["assets_category_id"],
    #                 data["brand_id"],
    #                 data["product_id"],
    #                 data["employee_id"],
    #                 company_id,
    #                 data.get("manufacturer", "") or "",
    #                 data["serial_number"],
    #                 data.get("company_asset_code", "") or "",
    #                 data["assets_name"],
    #                 data.get("quantity", 0),   # ✅ properly mapped quantity
    #                 is_working,
    #                 data["purchase_date"],
    #                 data.get("invoice_number", "") or "",
    #                 data.get("warranty_end_date", "") or "",
    #                 data.get("asset_note", "") or "",
    #                 data.get("asset_image", "") or "",
    #                 datetime.now(),
    #                 'N',
    #                 '0'
    #             ])
    
    #             # Fetch employee's name & email
    #             cursor.execute("""
    #                 SELECT first_name, last_name, email
    #                 FROM ci_erp_users
    #                 WHERE username = %s
    #             """, [data["employee_id"]])
    #             employee = cursor.fetchone()
    
    #         # If employee found, send HTML email
    #         if employee:
    #             first_name, last_name, email = employee
    #             employee_name = f"{first_name} {last_name}".strip()
    
    #             # Formatted HTML Email
    #             subject = f"New Asset Allocated: {data['assets_name']}"
    #             html_content = f"""
    #             <html>
    #             <body style="font-family: Arial, sans-serif; color: #333;">
    #                 <h2>New Asset Allocation</h2>
    #                 <p>Dear <b>{employee_name}</b>,</p>
                    
    #                 <p>A new asset has been allocated to you.</p>
                    
    #                 <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
    #                     <p><b>Asset Name:</b> {data['assets_name']}</p>
    #                     <p><b>Serial Number:</b> {data['serial_number']}</p>
    #                     <p><b>Purchase Date:</b> {data['purchase_date']}</p>
    #                     <p><b>Quantity:</b> {data.get("quantity", 0)}</p>
    #                 </div>
                    
    #                 <p style="color: #3794ff; font-weight: bold;">
    #                     Please log in to your employee dashboard and confirm that you have received this asset.
    #                 </p>
                    
    #                 <p>If you have any issues with the asset or require further assistance, 
    #                 kindly contact the IT department.</p>
                    
    #                 <p>Best regards,</p>
    #                 <div style="margin: 10px 0;">
    #                     <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
    #                 </div>
    #                 <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
    #                 <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
    #                     © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
    #                 </div>
    #             </body>
    #             </html>
    #             """
                
    #             msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
    #             msg.attach_alternative(html_content, "text/html")
    
    #             # Attach logo inline
    #             logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
    #             if os.path.exists(logo_path):
    #                 with open(logo_path, 'rb') as f:
    #                     logo_data = f.read()
    #                 image = MIMEImage(logo_data)
    #                 image.add_header('Content-ID', '<company_logo>')
    #                 image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
    #                 msg.attach(image)
    
    #             msg.send(fail_silently=False)
    
    #         return Response({"message": "Asset created successfully and email sent."}, status=status.HTTP_201_CREATED)
    
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    def get(self, request, pk=None):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.id,
                    a.assets_category_id,
                    cat.category_name AS assets_category_name,
                    a.brand_id,
                    b.category_name AS assets_brand_name,
                    a.company_id,
                    a.employee_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    a.company_asset_code,
                    a.assets_name,
                    a.purchase_date,
                    a.invoice_number,
                    a.manufacturer,
                    a.serial_number,
                    a.warranty_end_date,
                    a.asset_note,
                    a.asset_image,
                    a.is_working,
                    a.created_at,
                    a.returned,
                    a.employee_confirmation,
                    a.return_request_status,
                    a.quantity,
                    a.return_date
                FROM
                    ci_assets a
                LEFT JOIN
                    ci_erp_constants cat ON a.assets_category_id = cat.constants_id
                LEFT JOIN
                    ci_erp_constants b ON a.brand_id = b.constants_id AND b.type = 'assets_brand'
                LEFT JOIN
                    ci_erp_users_details ud ON a.employee_id = ud.employee_id
                LEFT JOIN
                    ci_erp_users u ON ud.user_id = u.id
                ORDER BY
                    a.created_at DESC
            """)
            rows = cursor.fetchall()

        columns = [
            "id", "assets_category_id", "category_name", "brand_id", "brand_name",
            "company_id", "employee_id", "employee_name", "company_asset_code", "assets_name",
            "purchase_date", "invoice_number", "manufacturer", "serial_number",
            "warranty_end_date", "asset_note", "asset_image", "is_working",
            "created_at", "returned", "employee_confirmation", "return_request_status","quantity","return_date"
        ]

        data = []
        for row in rows:
            item = dict(zip(columns, row))
            item["is_working"] = "Yes" if item["is_working"] in (1, '1', True) else "No"
            
            # ✅ Attach the full URL path for asset_image (URL-safe)
            if item.get("asset_image"):
                encoded_path = quote(item["asset_image"])  # encode the actual DB value
                item["asset_image"] = f"https://tdtlworld.com/hrms-backend/media/assets_pictures/{encoded_path}"
            else:
                item["asset_image"] = None

            data.append(item)

        return Response(data)   
   
   
    # def post(self, request, pk=None):
    #     data = request.data
    #     company_id = 2
   
    #     # Required fields
    #     required_fields = [
    #         "assets_name",
    #         "assets_category_id",
    #         "brand_id",
    #         "employee_id",
    #         "purchase_date",
    #         "serial_number",
    #         "product_id"
    #     ]
    #     for field in required_fields:
    #         if not data.get(field):
    #             return Response({"error": f"Missing required field: {field}"}, status=status.HTTP_400_BAD_REQUEST)
   
    #     # Handle optional and boolean conversion
    #     is_working_input = str(data.get("is_working", "")).strip().lower()
    #     is_working = 1 if is_working_input in ("yes", "1", "true") else 0

    #     # Handle asset image upload
    #     asset_image_file = request.FILES.get("asset_image")  # File object from request
    #     asset_image_path = ""
    #     if asset_image_file:
    #         file_name = asset_image_file.name
    #         asset_image_path = default_storage.save(f"assets_pictures/{file_name}", ContentFile(asset_image_file.read()))

   
    #     try:
    #         with connection.cursor() as cursor:
    #             # Insert the new asset (fixed quantity placement)
    #             cursor.execute("""
    #                 INSERT INTO ci_assets (
    #                     assets_category_id, brand_id,product_id, employee_id, company_id,
    #                     manufacturer, serial_number, company_asset_code, assets_name, quantity,
    #                     is_working, purchase_date, invoice_number, warranty_end_date,
    #                     asset_note, asset_image, created_at, returned, return_request_status
    #                 ) VALUES (
    #                     %s, %s, %s, %s, %s,%s,
    #                     %s, %s, %s, %s,
    #                     %s, %s, %s, %s,
    #                     %s, %s, %s, %s, %s
    #                 )
    #             """, [
    #                 data["assets_category_id"],
    #                 data["brand_id"],
    #                 data["product_id"],
    #                 data["employee_id"],
    #                 company_id,
    #                 data.get("manufacturer", "") or "",
    #                 data["serial_number"],
    #                 data.get("company_asset_code", "") or "",
    #                 data["assets_name"],
    #                 data.get("quantity", 0),   # ✅ properly mapped quantity
    #                 is_working,
    #                 data["purchase_date"],
    #                 data.get("invoice_number", "") or "",
    #                 data.get("warranty_end_date", "") or "",
    #                 data.get("asset_note", "") or "",
    #                 data.get("asset_image", "") or "",
    #                 datetime.now(),
    #                 'N',
    #                 '0'
    #             ])
   
    #             # Fetch employee's name & email
    #             cursor.execute("""
    #                 SELECT first_name, last_name, email
    #                 FROM ci_erp_users
    #                 WHERE username = %s
    #             """, [data["employee_id"]])
    #             employee = cursor.fetchone()
   
    #         # If employee found, send HTML email
    #             if employee:
    #                 first_name, last_name, email = employee
    #                 employee_name = f"{first_name} {last_name}".strip()


    #                 cursor.execute("""
    #                         SELECT 
    #                             a.assets_name, a.serial_number, a.company_asset_code,
    #                             CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    #                             u.email AS employee_email,
    #                             u.username AS employee_id ,a.quantity , CASE 
    #     WHEN     a.is_working = 1 THEN 'Working'
    #     WHEN     a.is_working = 0 THEN 'Not Working'
    #     ELSE     'Unknown'
    # END AS i    s_working,
    # eca.cate    gory_name AS brand, 
    #                         ecb.category_name AS category, 
    #                         ecc.category_name AS product,
    #                         a.return_date
    #                         FROM 
    #                             ci_assets a
    #                         LEFT JOIN 
    #                             ci_erp_users_details ud ON a.employee_id = ud.employee_id
    #                         LEFT JOIN 
    #                             ci_erp_users u ON ud.user_id = u.id
    #                         LEFT JOIN 
    #                             ci_erp_constants AS eca ON eca.constants_id = a.brand_id
    #                         LEFT JOIN 
    #                             ci_erp_constants AS ecb ON ecb.constants_id = a.assets_category_id
    #                         LEFT JOIN 
    #                             ci_erp_constants AS ecc ON ecc.constants_id = a.product_id
    #                         WHERE 
    #                             a.id = %s
    #                     """, [pk])
    #                     asset_data = cursor.fetchone()

    #         if asset_data:
    #                         assets_name, serial_number, company_asset_code, employee_name, employee_email,  employee_id ,quantity ,is_working ,brand,product,category,return_date = asset_data 

   
    #             # Formatted HTML Email
    #             subject = f"New Asset Allocated: {data['assets_name']}"
    #             html_content = f"""
    #             <html>
    #             <body style="font-family: Arial, sans-serif; color: #333;">
    #                 <h2>New Asset Allocation</h2>
    #                 <p>Dear <b>{employee_name}</b>,</p>
                   
    #                 <p>A new asset has been allocated to you.</p>
                   
    #                 <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
    #                     <p><b>Asset Name:</b> {data['assets_name']}</p>
    #                     <p><b>Serial Number:</b> {data['serial_number']}</p>
    #                     <p><b>Purchase Date:</b> {data['purchase_date']}</p>
    #                     <p><b>Quantity:</b> {data.get("quantity", 0)}</p>
    #                 </div>
                   
    #                 <p style="color: #3794ff; font-weight: bold;">
    #                     Please log in to your employee dashboard and confirm that you have received this asset.
    #                 </p>
                   
    #                 <p>If you have any issues with the asset or require further assistance,
    #                 kindly contact the IT department.</p>
                   
    #                 <p>Best regards,</p>
    #                 <div style="margin: 10px 0;">
    #                     <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
    #                 </div>
    #                 <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
    #                 <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
    #                     © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
    #                 </div>
    #             </body>
    #             </html>
    #             """
               
    #             msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
    #             msg.attach_alternative(html_content, "text/html")
   
    #             # Attach logo inline
    #             logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
    #             if os.path.exists(logo_path):
    #                 with open(logo_path, 'rb') as f:
    #                     logo_data = f.read()
    #                 image = MIMEImage(logo_data)
    #                 image.add_header('Content-ID', '<company_logo>')
    #                 image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
    #                 msg.attach(image)
   
    #             msg.send(fail_silently=False)
   
    #         return Response({"message": "Asset created successfully and email sent."}, status=status.HTTP_201_CREATED)
   
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    # def post(self, request, pk=None):
    #     data = request.data
    #     company_id = 2
    
    #     # Required fields
    #     required_fields = [
    #         "assets_name",
    #         "assets_category_id",
    #         "brand_id",
    #         "employee_id",
    #         "purchase_date",
    #         "serial_number",
    #         "product_id"
    #     ]
    #     for field in required_fields:
    #         if not data.get(field):
    #             return Response({"error": f"Missing required field: {field}"}, status=status.   HTTP_400_BAD_REQUEST)
    
    #     # Handle optional and boolean conversion
    #     is_working_input = str(data.get("is_working", "")).strip().lower()
    #     is_working = 1 if is_working_input in ("yes", "1", "true") else 0
    
    #     # Handle asset image upload
    #     asset_image_file = request.FILES.get("asset_image")  # File object from request
    #     asset_image_path = ""
    #     if asset_image_file:
    #         file_name = asset_image_file.name
    #         asset_image_path = default_storage.save(f"assets_pictures/{file_name}", ContentFile (asset_image_file.read()))
    
    #     try:
    #         with connection.cursor() as cursor:
    #             # Insert the new asset (fixed quantity placement)
    #             cursor.execute("""
    #                 INSERT INTO ci_assets (
    #                     assets_category_id, brand_id, product_id, employee_id, company_id,
    #                     manufacturer, serial_number, company_asset_code, assets_name, quantity,
    #                     is_working, purchase_date, invoice_number, warranty_end_date,
    #                     asset_note, asset_image, created_at, returned, return_request_status
    #                 ) VALUES (
    #                     %s, %s, %s, %s, %s, %s,
    #                     %s, %s, %s, %s,
    #                     %s, %s, %s, %s,
    #                     %s, %s, %s, %s, %s
    #                 )
    #             """, [
    #                 data["assets_category_id"],
    #                 data["brand_id"],
    #                 data["product_id"],
    #                 data["employee_id"],
    #                 company_id,
    #                 data.get("manufacturer", "") or "",
    #                 data["serial_number"],
    #                 data.get("company_asset_code", "") or "",
    #                 data["assets_name"],
    #                 data.get("quantity", 0),  # ✅ properly mapped quantity
    #                 is_working,
    #                 data["purchase_date"],
    #                 data.get("invoice_number", "") or "",
    #                 data.get("warranty_end_date", "") or "",
    #                 data.get("asset_note", "") or "",
    #                 data.get("asset_image", "") or "",
    #                 datetime.now(),
    #                 'N',
    #                 '0'
    #             ])
    
    #             # Fetch employee's name & email
    #             cursor.execute("""
    #                 SELECT first_name, last_name, email
    #                 FROM ci_erp_users
    #                 WHERE username = %s
    #             """, [data["employee_id"]])
    #             employee = cursor.fetchone()
    
    #             # If employee found, send HTML email
    #             if employee:
    #                 first_name, last_name, email = employee
    #                 employee_name = f"{first_name} {last_name}".strip()
    
    #                 cursor.execute("""
    #                     SELECT 
    #                         a.assets_name, a.serial_number, a.company_asset_code,
    #                         CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    #                         u.email AS employee_email,
    #                         u.username AS employee_id, a.quantity,
    #                         CASE 
    #                             WHEN a.is_working = 1 THEN 'Working'
    #                             WHEN a.is_working = 0 THEN 'Not Working'
    #                             ELSE 'Unknown'
    #                         END AS is_working,
    #                         eca.category_name AS brand,
    #                         ecb.category_name AS category,
    #                         ecc.category_name AS product,
    #                         a.return_date
    #                     FROM 
    #                         ci_assets a
    #                     LEFT JOIN 
    #                         ci_erp_users_details ud ON a.employee_id = ud.employee_id
    #                     LEFT JOIN 
    #                         ci_erp_users u ON ud.user_id = u.id
    #                     LEFT JOIN 
    #                         ci_erp_constants AS eca ON eca.constants_id = a.brand_id
    #                     LEFT JOIN 
    #                         ci_erp_constants AS ecb ON ecb.constants_id = a.assets_category_id
    #                     LEFT JOIN 
    #                         ci_erp_constants AS ecc ON ecc.constants_id = a.product_id
    #                     WHERE 
    #                         a.id = %s
    #                 """, [pk])
    #                 asset_data = cursor.fetchone()
    
    #                 if asset_data:
    #                     (assets_name, serial_number, company_asset_code, employee_name,
    #                      employee_email, employee_id, quantity, is_working,
    #                      brand, product, category, return_date) = asset_data
    
    #                     # Formatted HTML Email
    #                     subject = f"New Asset Allocated: {data['assets_name']}"
    #                     html_content = f"""
    #                     <html>
    #                     <body style="font-family: Arial, sans-serif; color: #333;">
    #                         <h2>New Asset Allocation</h2>
    #                         <p>Dear <b>{employee_name}</b>,</p>
    
    #                         <p>A new asset has been allocated to you.</p>
    
    #                         <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5;   border-radius: 5px;">
    #                             <p><b>Category:</b> {category}</p>                        
    #                             <p><b>Brand:</b> {brand}</p>
    #                             <p><b>Product:</b> {product}</p>
    #                             <p><b>Quantity:</b> {quantity}</p>
    #                             <p><b>Is Working:</b> {is_working}</p>

    #                         </div>
    
    #                         <p style="color: #3794ff; font-weight: bold;">
    #                             Please log in to your employee dashboard and confirm that you have received     this asset.
    #                         </p>
    
    #                         <p>If you have any issues with the asset or require further assistance,
    #                         kindly contact the IT department.</p>
    
    #                         <p>Best regards,</p>
    #                         <div style="margin: 10px 0;">
    #                             <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto; ">
    #                         </div>
    #                         <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
    #                         <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
    #                             © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
    #                         </div>
    #                     </body>
    #                     </html>
    #                     """
    
    #                     msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
    #                     msg.attach_alternative(html_content, "text/html")
    
    #                     # Attach logo inline
    #                     logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
    #                     if os.path.exists(logo_path):
    #                         with open(logo_path, 'rb') as f:
    #                             logo_data = f.read()
    #                         image = MIMEImage(logo_data)
    #                         image.add_header('Content-ID', '<company_logo>')
    #                         image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
    #                         msg.attach(image)
    
    #                     msg.send(fail_silently=False)
    
    #         return Response({"message": "Asset created successfully and email sent."}, status=status.   HTTP_201_CREATED)
    
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk=None):
        data = request.data
        company_id = 2
   
        # Required fields
        required_fields = [
            "assets_name",
            "assets_category_id",
            "brand_id",
            "employee_id",
            "purchase_date",
            "serial_number",
            "product_id"
        ]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"Missing required field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

        employee_id = data["employee_id"]
   
        # Handle optional and boolean conversion
        is_working_input = str(data.get("is_working", "")).strip().lower()
        is_working = 1 if is_working_input in ("yes", "1", "true") else 0

        # Handle asset image upload
        asset_image_file = request.FILES.get("asset_image")  # File object from request
        asset_image_path = ""
        if asset_image_file:
            file_name = asset_image_file.name
            asset_image_path = default_storage.save(f"assets_pictures/{file_name}", ContentFile(asset_image_file.read()))

        try:
            with connection.cursor() as cursor:
                # Insert the new asset (fixed quantity placement)
                cursor.execute("""
                    INSERT INTO ci_assets (
                        assets_category_id, brand_id,product_id, employee_id, company_id,
                        manufacturer, serial_number, company_asset_code, assets_name, quantity,
                        is_working, purchase_date, invoice_number, warranty_end_date,
                        asset_note, asset_image, created_at, returned, return_request_status
                    ) VALUES (
                        %s, %s, %s, %s, %s,%s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                """, [
                    data["assets_category_id"],
                    data["brand_id"],
                    data["product_id"],
                    data["employee_id"],
                    company_id,
                    data.get("manufacturer", "") or "",
                    data["serial_number"],
                    data.get("company_asset_code", "") or "",
                    data["assets_name"],
                    data.get("quantity", 0),
                    is_working,
                    data["purchase_date"],
                    data.get("invoice_number", "") or "",
                    data.get("warranty_end_date", "") or "",
                    data.get("asset_note", "") or "",
                    data.get("asset_image", "") or "",
                    datetime.now(),
                    'N',
                    '0'
                ])

                #Get admin id
                cursor.execute("""select id from ci_erp_users u inner join ci_staff_roles sr on u.user_role_id = sr.role_id where sr.role_name = 'Admin' order by u.id desc limit 1""")

                admin_result = cursor.fetchone()
                if not admin_result:
                    raise ValueError("No admin user found in the system")
                
                admin_id = admin_result[0]

                #Get user id
                cursor.execute("""select id from ci_erp_users where username = %s""", [employee_id])

                user_result = cursor.fetchone()
                if not user_result:
                    raise ValueError(f"No user found for employee_id: {employee_id} in the system")
                
                user_id = user_result[0]

                #Send Notification
                notification_text = "A new asset has been assigned to you."
           
                cursor.execute("""
                    INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, [admin_id, user_id, notification_text])
   
                # Fetch employee's name & email
                cursor.execute("""
                    SELECT 
                            a.assets_name, a.serial_number, a.company_asset_code,
                            CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                            u.email AS email,
                            u.username AS employee_id ,a.quantity , CASE 
        WHEN a.is_working = 1 THEN 'Working'
        WHEN a.is_working = 0 THEN 'Not Working'
        ELSE 'Unknown'
    END AS is_working,
    eca.category_name AS brand, 
                        ecb.category_name AS category, 
                        ecc.category_name AS product,
                        a.return_date
                        FROM 
                            ci_assets a 
                        LEFT JOIN 
                            ci_erp_users_details ud ON a.employee_id = ud.employee_id
                        LEFT JOIN 
                            ci_erp_users u ON ud.user_id = u.id
                        LEFT JOIN 
                            ci_erp_constants AS eca ON eca.constants_id = a.brand_id
                        LEFT JOIN 
                            ci_erp_constants AS ecb ON ecb.constants_id = a.assets_category_id
                        LEFT JOIN 
                            ci_erp_constants AS ecc ON ecc.constants_id = a.product_id
                        where u.username = %s
                """, [data["employee_id"]])
                employee = cursor.fetchone()
   
            # If employee found, send HTML email
            if employee:
                assets_name, serial_number, company_asset_code, employee_name,email, employee_id,quantity,is_working, brand, category, product, return_date  = employee
                
   
                # Formatted HTML Email
                subject = f"New Asset Allocated: {product}"
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2>New Asset Allocation</h2>
                    <p>Dear <b>{employee_name}</b>,</p>
                   
                    <p>A new asset has been allocated to you.</p>
                   
                    <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                        <p><b>Category Name:</b> {category}</p>
                        <p><b>Brand Name:</b> {brand}</p>
                        <p><b>Product Name:</b> {product}</p>                    
                        <p><b>Quantity:</b> {quantity}</p>
                        <p><b>Is Working:</b> {is_working}</p>
                    
                    </div>
                   
                    <p style="color: #3794ff; font-weight: bold;">
                        Please log in to your employee dashboard and confirm that you have received this asset.
                    </p>
                   
                    <p>If you have any issues with the asset or require further assistance,
                    kindly contact the IT department.</p>
                   
                    <p>Best regards,</p>
                    <div style="margin: 10px 0;">
                        <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
                    </div>
                    <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
                    <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
                        © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
                    </div>
                </body>
                </html>
                """
               
                msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
                msg.attach_alternative(html_content, "text/html")
   
                # Attach logo inline
                logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
                if os.path.exists(logo_path):
                    with open(logo_path, 'rb') as f:
                        logo_data = f.read()
                    image = MIMEImage(logo_data)
                    image.add_header('Content-ID', '<company_logo>')
                    image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
                    msg.attach(image)
   
                msg.send(fail_silently=False)
   
            return Response({"message": "Asset created successfully and email sent."}, status=status.HTTP_201_CREATED)
   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    
    
 

    # def patch(self, request, pk):
    #     action = request.data.get("action", "").strip().lower()
    #     # user_role = request.user.role 

    #     # if user_role == 'employee' and action in ['return_yes', 'return_no']:
    #     #     return Response({"error": "Unauthorized action"}, status=403)


    #     if action == "return_yes":
    #         try:
    #             with connection.cursor() as cursor:
    #                 cursor.execute("""
    #                     UPDATE ci_assets
    #                     SET returned = 'Y', return_request_status = '2'
    #                     WHERE id = %s
    #                 """, [pk])
    #             return Response({"message": "Return confirmed. Asset marked as returned."}, status=status.HTTP_200_OK)
    #         except Exception as e:
    #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #     elif action == "return_no":
    #         try:
    #             with connection.cursor() as cursor:
    #                 cursor.execute("""
    #                     UPDATE ci_assets
    #                     SET return_request_status = '0'
    #                     WHERE id = %s
    #                 """, [pk])
    #             return Response({"message": "Return request denied. Asset remains allocated."}, status=status.HTTP_200_OK)
    #         except Exception as e:
    #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    #     # Default patch for updating asset fields
    #     data = request.data
    #     update_fields = []
    #     params = []

    #     for field in [
    #         "assets_category_id", "brand_id", "company_id", "employee_id",
    #         "company_asset_code", "assets_name", "purchase_date", "invoice_number",
    #         "manufacturer", "serial_number", "warranty_end_date", "asset_note",
    #         "asset_image", "is_working", "returned", "return_request_status"
    #     ]:
    #         if field in data:
    #             value = data[field]
    #             if field == "is_working":
    #                 value = str(value).strip().lower()
    #                 value = 1 if value in ("yes", "1", "true") else 0
    #             update_fields.append(f"{field} = %s")
    #             params.append(value)

    #     if not update_fields:
    #         return Response({"error": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

    #     params.append(pk)

    #     try:
    #         with connection.cursor() as cursor:
    #             cursor.execute(f"""
    #                 UPDATE ci_assets
    #                 SET {', '.join(update_fields)}
    #                 WHERE id = %s
    #             """, params)
    #         return Response({"message": "Asset updated successfully."}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk):
    #     try:
    #         with connection.cursor() as cursor:
    #             cursor.execute("DELETE FROM ci_assets WHERE id = %s", [pk])
    #         return Response({"message": "Asset deleted successfully."}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    def patch(self, request, pk):
        action = request.data.get("action", "").strip().lower()

        # if action == "return_yes":
        #     try:
        #         with connection.cursor() as cursor:
        #             # First update the asset status
        #             cursor.execute("""
        #                 UPDATE ci_assets
        #                 SET returned = 'Y', return_request_status = '2'
        #                 WHERE id = %s
        #             """, [pk])
        if action == "return_yes":
            try:
                with connection.cursor() as cursor:
                    # ✅ Get brand_id for this asset
                    cursor.execute("""
                        SELECT brand_id , quantity
                        FROM ci_assets
                        WHERE id = %s
                    """, [pk])
                    row = cursor.fetchone()
                    if not row:
                        return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)
    
                    # brand_id = row[0]
                    brand_id, quantity = row
    
                    # ✅ Update asset return status
                    cursor.execute("""
                        UPDATE ci_assets
                        SET returned = 'Y', return_request_status = '2',return_date = CURDATE()
                        WHERE id = %s
                    """, [pk])
    
                    # ✅ Update stock back in ci_erp_constants (increment by 1)
                    # cursor.execute("""
                    #     UPDATE ci_erp_constants
                    #     SET field_one = COALESCE(field_one, 0) + %s
                    #     WHERE constants_id = %s
                    # """, [quantity, brand_id])
                    # Get asset and employee details for email
                    cursor.execute("""
                        SELECT 
                            a.assets_name, a.serial_number, a.company_asset_code,
                            CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                            u.email AS employee_email,
                            u.username AS employee_id ,a.quantity , CASE 
        WHEN a.is_working = 1 THEN 'Working'
        WHEN a.is_working = 0 THEN 'Not Working'
        ELSE 'Unknown'
    END AS is_working,
    eca.category_name AS brand, 
                        ecb.category_name AS category, 
                        ecc.category_name AS product,
                        a.return_date
                        FROM 
                            ci_assets a
                        LEFT JOIN 
                            ci_erp_users_details ud ON a.employee_id = ud.employee_id
                        LEFT JOIN 
                            ci_erp_users u ON ud.user_id = u.id
                        LEFT JOIN 
                            ci_erp_constants AS eca ON eca.constants_id = a.brand_id
                        LEFT JOIN 
                            ci_erp_constants AS ecb ON ecb.constants_id = a.assets_category_id
                        LEFT JOIN 
                            ci_erp_constants AS ecc ON ecc.constants_id = a.product_id
                        WHERE 
                            a.id = %s
                    """, [pk])
                    asset_data = cursor.fetchone()

                    if asset_data:
                        assets_name, serial_number, company_asset_code, employee_name, employee_email, employee_id ,quantity ,is_working ,brand,product,category,return_date = asset_data 

                        # Email to Employee
                        subject_employee = f"Asset Return Confirmed: {assets_name}"
                        html_content_employee = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; color: #333;">
                            <h2>Asset Return Confirmed</h2>
                            <p>Dear <b>{employee_name}</b>,</p>
                            
                            <p>Your return request for the following asset has been confirmed by the company.</p>
                            
                            <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                                <p><b>Category:</b> {category}</p>
                                <p><b>Brand:</b> {brand}</p>
                                <p><b>Asset Name:</b> {product}</p>
                                <p><b>Quantity:</b> {quantity}</p>
                                <p><b>Is Working:</b> {is_working}</p>                                
                                <p><b>Return Date:</b> {return_date}</p>                                

                            </div>
                            
                            <p style="color: #3794ff; font-weight: bold;">
                                The asset has been successfully returned to the company inventory.
                            </p>
                            
                            <p>If you have any questions regarding this return, please contact the IT department.</p>
                            
                            <p>Best regards,</p>
                            <div style="margin: 10px 0;">
                                <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
                            </div>
                            <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
                            <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
                                © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
                            </div>
                        </body>
                        </html>
                        """
                        
                        msg_employee = EmailMultiAlternatives(
                            subject_employee, 
                            '', 
                            settings.DEFAULT_FROM_EMAIL, 
                            [employee_email]
                        )
                        msg_employee.attach_alternative(html_content_employee, "text/html")

                        # Get all admin and HR emails
                        cursor.execute("""
                            SELECT email, CONCAT(first_name, ' ', last_name) AS name
                            FROM ci_erp_users
                            WHERE user_type IN ('Admin')
                            AND is_active = 1
                        """)
                        #   (, '7', '5', 'hr','HR', 'admin') add this for fetching all emails
                        admin_hr_recipients = cursor.fetchall()

                        # Email to Admin/HR
                        subject_admin = f"Asset Return Completed: {assets_name} by {employee_name} ({employee_id})"
                        html_content_admin = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; color: #333;">
                            <h2>Asset Return Completed</h2>
                            <p>Dear Admin/HR Team,</p>
                            
                            <p>The following asset has been successfully returned to company inventory:</p>
                            
                            <div style="margin: 15px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                                <p><b>Asset Name:</b> {assets_name}</p>
                                <p><b>Serial Number:</b> {serial_number}</p>
                                <p><b>Company Asset Code:</b> {company_asset_code}</p>
                                <p><b>Returned By:</b> {employee_name} (ID: {employee_id})</p>
                            </div>
                            
                            <p style="color: #3794ff; font-weight: bold;">
                                The asset is now available for reallocation or other company use.
                            </p>
                            
                            <p>Please update your records accordingly.</p>
                            
                            <p>Best regards,</p>
                            <div style="margin: 10px 0;">
                                <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
                            </div>
                            <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
                            <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
                                © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
                            </div>
                        </body>
                        </html>
                        """

                        # Send email to employee
                        logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
                        if os.path.exists(logo_path):
                            with open(logo_path, 'rb') as f:
                                logo_data = f.read()
                            image = MIMEImage(logo_data)
                            image.add_header('Content-ID', '<company_logo>')
                            image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
                            msg_employee.attach(image)
                        msg_employee.send(fail_silently=False)

                        # Send email to each admin/HR
                        for email, name in admin_hr_recipients:
                            msg_admin = EmailMultiAlternatives(
                                subject_admin, 
                                '', 
                                settings.DEFAULT_FROM_EMAIL, 
                                [email]
                            )
                            msg_admin.attach_alternative(html_content_admin, "text/html")
                            
                            if os.path.exists(logo_path):
                                with open(logo_path, 'rb') as f:
                                    logo_data = f.read()
                                image = MIMEImage(logo_data)
                                image.add_header('Content-ID', '<company_logo>')
                                image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
                                msg_admin.attach(image)
                            msg_admin.send(fail_silently=False)

                return Response({
                    "message": "Return confirmed. Asset marked as returned and notifications sent."
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif action == "return_no":
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE ci_assets
                        SET return_request_status = '0'
                        WHERE id = %s
                    """, [pk])
                return Response({"message": "Return request denied. Asset remains allocated."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Default patch for updating asset fields
        data = request.data
        update_fields = []
        params = []

        for field in [
            "assets_category_id", "brand_id", "company_id", "employee_id",
            "company_asset_code", "assets_name", "purchase_date", "invoice_number",
            "manufacturer", "serial_number", "warranty_end_date", "asset_note",
            "asset_image", "is_working", "returned", "return_request_status"
        ]:
            if field in data:
                value = data[field]
                if field == "is_working":
                    value = str(value).strip().lower()
                    value = 1 if value in ("yes", "1", "true") else 0
                update_fields.append(f"{field} = %s")
                params.append(value)

        if not update_fields:
            return Response({"error": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

        params.append(pk)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE ci_assets
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """, params)
            return Response({"message": "Asset updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ci_assets WHERE id = %s", [pk])
            return Response({"message": "Asset deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from datetime import datetime

# Asset Requisition API
class AssetRequisitionView(APIView):
    def post(self, request):
        data = request.data
        required_fields = [
            "requisition_number", "asset_name", "assets_category_id", "assets_type_id",
            "assets_brand_id", "specification", "quantity", "expected_date"
        ]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"Missing required field: {field}"}, status=status.HTTP_400_BAD_REQUEST)

        status_value = data.get("status", "P")  # Default to 'P' (pending)
        if status_value not in ["P", "R"]:
            return Response({"error": "Invalid status. Use 'P' for pending or 'R' for received."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_assets_requisition (
                        requisition_number, asset_name, assets_category_id, assets_type_id,
                        assets_brand_id, specification, quantity, expected_date, status, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data["requisition_number"], data["asset_name"], data["assets_category_id"],
                    data["assets_type_id"], data["assets_brand_id"], data["specification"],
                    data["quantity"], data["expected_date"], status_value, datetime.now()
                ])
            return Response({"message": "Asset requisition created successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT requisition_id, requisition_number, asset_name, assets_category_id, assets_type_id,
                           assets_brand_id, specification, quantity, expected_date, status, created_at
                    FROM ci_assets_requisition
                    ORDER BY created_at DESC
                """)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, requisition_id):
        data = request.data
        update_fields = []
        params = []
        allowed_fields = [
            "asset_name", "assets_category_id", "assets_type_id", "assets_brand_id",
            "specification", "quantity", "expected_date", "status"
        ]
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])

        if not update_fields:
            return Response({"error": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

        params.append(requisition_id)
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE ci_assets_requisition
                    SET {', '.join(update_fields)}
                    WHERE requisition_id = %s
                """, params)
            return Response({"message": "Asset requisition updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class EmployeeHolidayAPIView(APIView):
    def get(self, request, employee_id):
        with connection.cursor() as cursor:
            # Fetch the state and hub for the given employee_id
            cursor.execute("""
                SELECT u.state,
                    u.employee_hub_id
                FROM ci_erp_users u
                JOIN ci_erp_users_details d ON u.id = d.user_id
                WHERE d.employee_id = %s
            """, [employee_id])
            row = cursor.fetchone()
 
            if not row:
                return JsonResponse({"error": "Employee not found."}, status=404)
 
            state_code = row[0]
            hub_id = row[1]   #  extract employee_hub_id also
 
            # Fetch published holidays for the employee's state + hub
            cursor.execute("""
                SELECT
                    holiday_id,
                    event_name,
                    description,
                    start_date,
                    end_date,
                    is_publish
                FROM ci_holidays
                WHERE state = %s AND employee_hub = %s
                ORDER BY start_date ASC
            """, [state_code, hub_id])   #  pass both parameters
 
            holidays = cursor.fetchall()
 
            holiday_list = [
                {
                    "holiday_id": r[0],
                    "event_name": r[1],
                    "description": r[2],
                    "start_date": r[3],
                    "end_date": r[4],
                    "status": "published" if r[5] == 1 else "restricted"  # convert is_publish to status
                }
                for r in holidays
            ]
 
            return Response(holiday_list)
 
 
 
 
 
class HolidayView(APIView):
    def post(self, request):
        # Get raw input from frontend
        country_name = request.data.get("country")           # e.g., "India"
        state_name = request.data.get("state")               # e.g., "Maharashtra"
        hub_name = request.data.get("employee_hub")          # e.g., "Pune Hub"
        status_raw = request.data.get("is_publish")      # "published" or "restricted"
 
        # # Convert is_publish from string to integer
        # if is_publish_raw == "published":
        #     is_publish = 1
        # elif is_publish_raw == "restricted":
        #     is_publish = 0
        # else:
        #     return Response(
        #         {"status": "error", "message": "Invalid value for is_publish. Use 'published' or 'restricted'."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
 
 
         # Convert status to is_publish for DB storage
        if status_raw == "published":
            is_publish = 1
        elif status_raw == "restricted":
            is_publish = 0
        else:
            return Response(
                {"status": "error", "message": "Invalid value for status. Use 'published' or 'restricted'."},
                status=status.HTTP_400_BAD_REQUEST
        )
 
 
        try:
            with connection.cursor() as cursor:
                # Fetch country ID
                cursor.execute("""
                    SELECT constants_id FROM ci_erp_constants
                    WHERE type = 'country' AND category_name = %s
                    LIMIT 1
                """, [country_name])
                country_row = cursor.fetchone()
                if not country_row:
                    return Response(
                        {"status": "error", "message": f"Country '{country_name}' not found."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                country_id = country_row[0]
 
                # Fetch state ID (with parent country)
                cursor.execute("""
                    SELECT constants_id FROM ci_erp_constants
                    WHERE type = 'state' AND category_name = %s AND parent_value = %s
                    LIMIT 1
                """, [state_name, country_id])
                state_row = cursor.fetchone()
                if not state_row:
                    return Response(
                        {"status": "error", "message": f"State '{state_name}' not found under country '{country_name}'."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                state_id = state_row[0]
 
                # Fetch employee_hub ID from ci_employee_hub
                cursor.execute("""
                    SELECT employee_hub_id FROM ci_employee_hub
                    WHERE employee_hub_name = %s
                    LIMIT 1
                """, [hub_name])
                hub_row = cursor.fetchone()
                if not hub_row:
                    return Response(
                        {"status": "error", "message": f"Employee hub '{hub_name}' not found."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                hub_id = hub_row[0]
 
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Error fetching IDs: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
       
        fields = {
            "event_name": request.data.get("event_name"),
            "country": country_id,        
            "state": state_id,            
            "employee_hub": hub_id,        
            "start_date": request.data.get("start_date"),
            "end_date": request.data.get("end_date"),
            "description": request.data.get("description"),
            "is_publish": is_publish,      # 1 or 0
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "company_id": 2
        }
 
        # Build SQL query
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
                status=status.HTTP_400_BAD_REQUEST
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
                status=status.HTTP_201_CREATED
            )
 
        except Exception as e:
            return Response(
                {"status": "error", "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
 
 
    def get(self, request, holiday_id=None):
        try:
            with connection.cursor() as cursor:
                if holiday_id:
                    cursor.execute("""
                        SELECT h.holiday_id, h.event_name, h.start_date, h.end_date, h.description,
                               h.is_publish, h.created_at,
                               c.category_name AS country, s.category_name AS state,
                               e.employee_hub_name AS employee_hub
                        FROM ci_holidays h
                        LEFT JOIN ci_erp_constants c ON h.country = c.constants_id
                        LEFT JOIN ci_erp_constants s ON h.state = s.constants_id
                        LEFT JOIN ci_employee_hub e ON h.employee_hub = e.employee_hub_id
                        WHERE h.holiday_id = %s
                    """, [holiday_id])
                    row = cursor.fetchone()
                    if not row:
                        return Response({"status": "error", "message": "Holiday not found."}, status=404)
 
                    columns = [col[0] for col in cursor.description]
                    result = dict(zip(columns, row))
 
                    # Convert is_publish -> status
                    result["status"] = "published" if result["is_publish"] == 1 else "restricted"
                    result.pop("is_publish", None)
 
                    return Response(result, status=200)
                else:
                    cursor.execute("""
                        SELECT h.holiday_id, h.event_name, h.start_date, h.end_date, h.description,
                               h.is_publish, h.created_at,
                               c.category_name AS country, s.category_name AS state,
                               e.employee_hub_name AS employee_hub
                        FROM ci_holidays h
                        LEFT JOIN ci_erp_constants c ON h.country = c.constants_id
                        LEFT JOIN ci_erp_constants s ON h.state = s.constants_id
                        LEFT JOIN ci_employee_hub e ON h.employee_hub = e.employee_hub_id
                        ORDER BY h.start_date DESC
                    """)
                    rows = cursor.fetchall()
                    columns = [col[0] for col in cursor.description]
 
                    results = []
 
                    for row in rows:
                        record = dict(zip(columns, row))
                        record["status"] = "published" if record["is_publish"] == 1 else "restricted"
                        record.pop("is_publish", None)
                        results.append(record)
 
                    return Response(results, status=200)
 
        except Exception as e:
            return Response({"status": "error", "message": f"Error fetching holidays: {str(e)}"},
                            status=500)
 
    def patch(self, request, holiday_id):
        country_name = request.data.get("country")
        state_name = request.data.get("state")
        hub_name = request.data.get("employee_hub")
        status_raw = request.data.get("status")   # frontend sends "published" or "restricted"
 
        try:
            with connection.cursor() as cursor:
                # Convert status -> is_publish
                if status_raw is not None:
                    if status_raw == "published":
                        is_publish = 1
                    elif status_raw == "restricted":
                        is_publish = 0
                    else:
                        return Response({"status": "error", "message": "Invalid status value."}, status=400)
                else:
                    is_publish = None
 
                # Resolve names to IDs (if provided)
                country_id = None
                state_id = None
                hub_id = None
 
                if country_name:
                    cursor.execute("SELECT constants_id FROM ci_erp_constants WHERE type='country' AND category_name=%s", [country_name])
                    row = cursor.fetchone()
                    if row:
                        country_id = row[0]
 
                if state_name and country_id:
                    cursor.execute("SELECT constants_id FROM ci_erp_constants WHERE type='state' AND category_name=%s AND parent_value=%s", [state_name, country_id])
                    row = cursor.fetchone()
                    if row:
                        state_id = row[0]
 
                if hub_name:
                    cursor.execute("SELECT employee_hub_id FROM ci_employee_hub WHERE employee_hub_name=%s", [hub_name])
                    row = cursor.fetchone()
                    if row:
                        hub_id = row[0]
 
                # Build update set
                updates = []
                params = []
 
                for field, value in [
                    ("event_name", request.data.get("event_name")),
                    ("country", country_id),
                    ("state", state_id),
                    ("employee_hub", hub_id),
                    ("start_date", request.data.get("start_date")),
                    ("end_date", request.data.get("end_date")),
                    ("description", request.data.get("description")),
                    ("is_publish", is_publish)   #mapping from status
                ]:
                    if value is not None:
                        updates.append(f"{field} = %s")
                        params.append(value)
 
                if not updates:
                    return Response({"status": "error", "message": "No valid fields to update."}, status=400)
 
                params.append(holiday_id)
                query = f"UPDATE ci_holidays SET {', '.join(updates)} WHERE holiday_id = %s"
                cursor.execute(query, params)
 
            return Response({"status": "success", "message": "Holiday updated successfully."}, status=200)
 
        except Exception as e:
            return Response({"status": "error", "message": f"Update error: {str(e)}"}, status=500)
 
    def delete(self, request, holiday_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ci_holidays WHERE holiday_id = %s", [holiday_id])
                if cursor.rowcount == 0:
                    return Response({"status": "error", "message": "Holiday not found."}, status=404)
            return Response({"status": "success", "message": "Holiday deleted."}, status=200)
        except Exception as e:
            return Response({"status": "error", "message": f"Delete error: {str(e)}"}, status=500)
 
 




# class LeaveApplicationDashboardAPI(APIView):

#     def get(self, request):
#         data = {}

#         with connection.cursor() as cursor:
#             # ✅ Upcoming Holiday with only DATE
#             cursor.execute("""
#                 SELECT 
#                     event_name,
#                     DATE_FORMAT(start_date, '%Y-%m-%d') AS start_date,
#                     state AS location,
#                     CASE 
#                         WHEN is_publish = 1 THEN 'Published'
#                         ELSE 'Unpublished'
#                     END AS status
#                 FROM 
#                     ci_holidays
#                 WHERE 
#                     start_date >= CURDATE()
#                 ORDER BY 
#                     start_date ASC
#                 LIMIT 1
#             """)
#             holiday = cursor.fetchone()
#             data["upcoming_holiday"] = {
#                 "event_name": holiday[0],
#                 "start_date": holiday[1],   # already formatted in SQL
#                 "location": holiday[2],
#                 "status": holiday[3]
#             } if holiday else "No upcoming holiday found"

#             # ✅ Leave Type-wise Leaves (All)
#             cursor.execute("""
#                 SELECT 
#                     la.leave_id,
#                     CONCAT_WS(' ', u.first_name, u.last_name) AS employee_name,
#                     lt.category_name AS leave_type,
#                     CONCAT(DATE_FORMAT(la.from_date, '%d %b %Y'), ' to ', DATE_FORMAT(la.to_date, '%d %b %Y')) AS duration,
#                     DATEDIFF(la.to_date, la.from_date) + 1 AS day_count,
#                     DATE_FORMAT(la.created_at, '%Y-%m-%d') AS applied_on,
#                     la.reason
#                 FROM 
#                     ci_leave_applications la
#                 LEFT JOIN 
#                     ci_erp_users u ON la.employee_id = u.id
#                 LEFT JOIN 
#                     ci_erp_constants lt ON la.leave_type_id = lt.constants_id
#                 ORDER BY lt.category_name, la.created_at DESC
#             """)
#             type_rows = cursor.fetchall()
#             data["leave_type_wise_leaves"] = [
#                 {
#                     "leave_id": row[0],
#                     "employee_name": row[1],
#                     "leave_type": row[2],
#                     "duration": row[3],
#                     "day_count": int(row[4]) if row[4] is not None else 0,
#                     "applied_on": row[5],  # already formatted in SQL
#                     "reason": row[6]
#                 } for row in type_rows
#             ]

#             # ✅ Department-wise Leaves (All)
#             cursor.execute("""
#                 SELECT 
#                     la.leave_id,
#                     CONCAT_WS(' ', u.first_name, u.last_name) AS employee_name,
#                     d.department_name,
#                     lt.category_name AS leave_type,
#                     CONCAT(DATE_FORMAT(la.from_date, '%d %b %Y'), ' to ', DATE_FORMAT(la.to_date, '%d %b %Y')) AS duration,
#                     DATEDIFF(la.to_date, la.from_date) + 1 AS day_count,
#                     DATE_FORMAT(la.created_at, '%Y-%m-%d') AS applied_on,
#                     la.reason
#                 FROM 
#                     ci_leave_applications la
#                 LEFT JOIN 
#                     ci_erp_users u ON la.employee_id = u.id
#                 LEFT JOIN 
#                     ci_erp_users_details ud ON u.id = ud.user_id
#                 LEFT JOIN 
#                     ci_departments d ON ud.department_id = d.department_id
#                 LEFT JOIN 
#                     ci_erp_constants lt ON la.leave_type_id = lt.constants_id
#                 ORDER BY d.department_name, la.created_at DESC
#             """)
#             dept_rows = cursor.fetchall()
#             data["department_wise_leaves"] = [
#                 {
#                     "leave_id": row[0],
#                     "employee_name": row[1],
#                     "department_name": row[2],
#                     "leave_type": row[3],
#                     "duration": row[4],
#                     "day_count": int(row[5]) if row[5] is not None else 0,
#                     "applied_on": row[6],  # already formatted in SQL
#                     "reason": row[7]
#                 } for row in dept_rows
#             ]

#         return Response(data, status=status.HTTP_200_OK)




class LeaveApplicationDashboardAPI(APIView):

    def get(self, request):
        data = {}

        with connection.cursor() as cursor:
        # Upcoming Holiday with proper joins and aliasing
            cursor.execute("""
                SELECT
                    h.event_name,
                    h.start_date,
                    h.end_date,
                    c.category_name AS country_name,
                    s.category_name AS state_name,
                    eh.employee_hub_name,
                    CASE
                        WHEN h.is_publish = 1 THEN 'Published'
                        ELSE 'Unpublished'
                    END AS status
                FROM ci_holidays h
                LEFT JOIN ci_erp_constants c ON h.country = c.constants_id
                LEFT JOIN ci_erp_constants s ON h.state = s.constants_id
                LEFT JOIN ci_employee_hub eh ON h.employee_hub = eh.employee_hub_id
                WHERE h.start_date >= CURDATE()
                ORDER BY h.start_date ASC
                LIMIT 1
            """)
            holiday = cursor.fetchone()
            data["upcoming_holiday"] = {
                "event_name": holiday[0],
                "start_date": holiday[1],
                "end_date": holiday[2],
                "country": holiday[3],        # country_name
                "state": holiday[4],          # state_name
                "employee_hub": holiday[5],   # employee_hub_name
                "status": holiday[6]
            } if holiday else "No upcoming holiday found"

            # Leave Type-wise Leaves (All)
            cursor.execute("""
                SELECT 
                    la.leave_id,
                    CONCAT_WS(' ', u.first_name, u.last_name) AS employee_name,
                    lt.category_name AS leave_type,
                    CONCAT(DATE_FORMAT(la.from_date, '%d %b %Y'), ' to ', DATE_FORMAT(la.to_date, '%d %b %Y')) AS duration,
                    DATEDIFF(la.to_date, la.from_date) + 1 AS day_count,
                    la.created_at,
                    la.reason
                FROM 
                    ci_leave_applications la
                LEFT JOIN 
                    ci_erp_users u ON la.employee_id = u.id
                LEFT JOIN 
                    ci_erp_constants lt ON la.leave_type_id = lt.constants_id
                ORDER BY lt.category_name, la.created_at DESC
            """)
            type_rows = cursor.fetchall()
            data["leave_type_wise_leaves"] = [
                {
                    "leave_id": row[0],
                    "employee_name": row[1],
                    "leave_type": row[2],
                    "duration": row[3],
                    "day_count": int(row[4]) if row[4] is not None else 0,
                    "applied_on": row[5],
                    "reason": row[6]
                } for row in type_rows
            ]

            # Department-wise Leaves (All)
            cursor.execute("""
                SELECT 
                    la.leave_id,
                    CONCAT_WS(' ', u.first_name, u.last_name) AS employee_name,
                    d.department_name,
                    lt.category_name AS leave_type,
                    CONCAT(DATE_FORMAT(la.from_date, '%d %b %Y'), ' to ', DATE_FORMAT(la.to_date, '%d %b %Y')) AS duration,
                    DATEDIFF(la.to_date, la.from_date) + 1 AS day_count,
                    la.created_at,
                    la.reason
                FROM 
                    ci_leave_applications la
                LEFT JOIN 
                    ci_erp_users u ON la.employee_id = u.id
                LEFT JOIN 
                    ci_erp_users_details ud ON u.id = ud.user_id
                LEFT JOIN 
                    ci_departments d ON ud.department_id = d.department_id
                LEFT JOIN 
                    ci_erp_constants lt ON la.leave_type_id = lt.constants_id
                ORDER BY d.department_name, la.created_at DESC
            """)
            dept_rows = cursor.fetchall()
            data["department_wise_leaves"] = [
                {
                    "leave_id": row[0],
                    "employee_name": row[1],
                    "department_name": row[2],
                    "leave_type": row[3],
                    "duration": row[4],
                    "day_count": int(row[5]) if row[5] is not None else 0,
                    "applied_on": row[6],
                    "reason": row[7]
                } for row in dept_rows
            ]

        return Response(data, status=status.HTTP_200_OK)



            #  Pending Leaves (All)
            # cursor.execute("""
            #     SELECT 
            #         la.leave_id,
            #         CONCAT_WS(' ', u.first_name, u.last_name) AS employee_name,
            #         lt.category_name AS leave_type,
            #         CONCAT(DATE_FORMAT(la.from_date, '%d %b %Y'), ' to ', DATE_FORMAT(la.to_date, '%d %b %Y')) AS duration,
            #         DATEDIFF(la.to_date, la.from_date) + 1 AS day_count,
            #         la.created_at,
            #         CASE
            #             WHEN la.is_half_day = 1 AND la.status = 1 THEN 'Half Day (Pending)'
            #             ELSE 'Pending'
            #         END AS status,
            #         la.reason
            #     FROM 
            #         ci_leave_applications la
            #     LEFT JOIN 
            #         ci_erp_users u ON la.employee_id = u.id
            #     LEFT JOIN 
            #         ci_erp_constants lt ON la.leave_type_id = lt.constants_id
            #     WHERE la.status = 1
            #     ORDER BY la.created_at DESC
            # """)
            # pending_rows = cursor.fetchall()
            # data["pending_leaves"] = [
            #     {
            #         "leave_id": row[0],
            #         "employee_name": row[1],
            #         "leave_type": row[2],
            #         "duration": row[3],
            #         "day_count": int(row[4]) if row[4] is not None else 0,
            #         "applied_on": row[5],
            #         "status": row[6],
            #         "reason": row[7]
            #     } for row in pending_rows
            # ]

        #     #  Leave Type-wise Leaves (All)
        #     cursor.execute("""
        #         SELECT 
        #             la.leave_id,
        #             CONCAT_WS(' ', u.first_name, u.last_name) AS employee_name,
        #             lt.category_name AS leave_type,
        #             CONCAT(DATE_FORMAT(la.from_date, '%d %b %Y'), ' to ', DATE_FORMAT(la.to_date, '%d %b %Y')) AS duration,
        #             DATEDIFF(la.to_date, la.from_date) + 1 AS day_count,
        #             la.created_at,
        #             CASE
        #                 WHEN la.is_half_day = 1 AND la.status = 2 THEN 'Half Day (Approved)'
        #                 WHEN la.is_half_day = 1 AND la.status = 3 THEN 'Half Day (Rejected)'
        #                 WHEN la.status = 2 THEN 'Approved'
        #                 WHEN la.status = 3 THEN 'Rejected'
        #                 ELSE 'Pending'
        #             END AS status,
        #             la.reason
        #         FROM 
        #             ci_leave_applications la
        #         LEFT JOIN 
        #             ci_erp_users u ON la.employee_id = u.id
        #         LEFT JOIN 
        #             ci_erp_constants lt ON la.leave_type_id = lt.constants_id
        #         ORDER BY lt.category_name, la.created_at DESC
        #     """)
        #     type_rows = cursor.fetchall()
        #     data["leave_type_wise_leaves"] = [
        #         {
        #             "leave_id": row[0],
        #             "employee_name": row[1],
        #             "leave_type": row[2],
        #             "duration": row[3],
        #             "day_count": int(row[4]) if row[4] is not None else 0,
        #             "applied_on": row[5],
        #             "status": row[6],
        #             "reason": row[7]
        #         } for row in type_rows
        #     ]

        #     #  Department-wise Leaves (All)
        #     cursor.execute("""
        #         SELECT 
        #             la.leave_id,
        #             CONCAT_WS(' ', u.first_name, u.last_name) AS employee_name,
        #             d.department_name,
        #             lt.category_name AS leave_type,
        #             CONCAT(DATE_FORMAT(la.from_date, '%d %b %Y'), ' to ', DATE_FORMAT(la.to_date, '%d %b %Y')) AS duration,
        #             DATEDIFF(la.to_date, la.from_date) + 1 AS day_count,
        #             la.created_at,
        #             CASE
        #                 WHEN la.is_half_day = 1 AND la.status = 2 THEN 'Half Day (Approved)'
        #                 WHEN la.is_half_day = 1 AND la.status = 3 THEN 'Half Day (Rejected)'
        #                 WHEN la.status = 2 THEN 'Approved'
        #                 WHEN la.status = 3 THEN 'Rejected'
        #                 WHEN la.status = 1 THEN 'Pending'
        #                 ELSE 'Unknown'
        #             END AS status,
        #             la.reason
        #         FROM 
        #             ci_leave_applications la
        #         LEFT JOIN 
        #             ci_erp_users u ON la.employee_id = u.id
        #         LEFT JOIN 
        #             ci_erp_users_details ud ON u.id = ud.user_id
        #         LEFT JOIN 
        #             ci_departments d ON ud.department_id = d.department_id
        #         LEFT JOIN 
        #             ci_erp_constants lt ON la.leave_type_id = lt.constants_id
        #         ORDER BY d.department_name, la.created_at DESC
        #     """)
        #     dept_rows = cursor.fetchall()
        #     data["department_wise_leaves"] = [
        #         {
        #             "leave_id": row[0],
        #             "employee_name": row[1],
        #             "department_name": row[2],
        #             "leave_type": row[3],
        #             "duration": row[4],
        #             "day_count": int(row[5]) if row[5] is not None else 0,
        #             "applied_on": row[6],
        #             "status": row[7],
        #             "reason": row[8]
        #         } for row in dept_rows
        #     ]

        # return Response(data, status=status.HTTP_200_OK)







class LeavePendingCurrentMonthView(APIView):
    def get(self, request):
        today = datetime.today()
        current_month = today.month
        current_year = today.year

        with connection.cursor() as cursor:
            query = """
                SELECT 
                    CONCAT_WS(' ',
                        IFNULL(u.first_name, ''),
                        IFNULL(u.middle_name, ''),
                        IFNULL(u.last_name, '')
                    ) AS employee_name,
                    CONCAT(DATE_FORMAT(l.from_date, '%%Y-%%m-%%d'), ' to ', DATE_FORMAT(l.to_date, '%%Y-%%m-%%d')) AS date,
                    DATEDIFF(l.to_date, l.from_date) + 1 AS number_of_days,
                    l.reason,
                    'Pending' AS status
                FROM ci_leave_applications AS l
                JOIN ci_leave_count AS lc ON lc.employee_id = l.employee_id
                JOIN ci_erp_users_details AS d ON l.employee_id = d.employee_id
                JOIN ci_erp_users AS u ON d.user_id = u.id
                WHERE lc.status_lc = 'P'
                  AND MONTH(l.from_date) = %s
                  AND YEAR(l.from_date) = %s
            """
            cursor.execute(query, [current_month, current_year])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(results)






class LeaveSetupAPI(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id,
                    category_name AS leave_type,
                    field_one AS days_per_year,
                    field_two AS setup_rules
                FROM ci_erp_constants
                WHERE type = 'leave_type' AND company_id = 2
            """)
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(result)

    def post(self, request):
        data = request.data
        category_name = data.get('category_name')  # Leave type
        field_one = data.get('field_one')          # Days per year
        field_two = data.get('field_two')          # Setup rules

        if not category_name or not field_one:
            return Response({'error': 'category_name and field_one are required'}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_erp_constants (type, category_name, field_one, field_two, company_id)
                VALUES ('leave_type', %s, %s, %s, 2)
            """, [category_name, field_one, field_two])
        return Response({'message': 'Leave type added successfully'}, status=status.HTTP_201_CREATED)

    def patch(self, request, id):
        data = request.data
        category_name = data.get('category_name')
        field_one = data.get('field_one')
        field_two = data.get('field_two')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE ci_erp_constants
                SET category_name = %s, field_one = %s, field_two = %s
                WHERE constants_id = %s AND type = 'leave_type' AND company_id = 2
            """, [category_name, field_one, field_two, id])
        return Response({'message': 'Leave type updated successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, id):
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM ci_erp_constants
                WHERE constants_id = %s AND type = 'leave_type' AND company_id = 2
            """, [id])
        return Response({'message': 'Leave type deleted successfully'}, status=status.HTTP_200_OK)




 
class DivisionAPI(APIView):
 
    def get(self, request):
        """Fetch all divisions"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT division_id, division_name, division_code, created_at FROM ci_division")
                rows = cursor.fetchall()
                divisions = []
                for row in rows:
                    divisions.append({
                        'division_id': row[0],
                        'division_name': row[1],
                        'division_code': row[2],
                        'created_at': row[3]  # No .strftime(), since it's already a string
                    })
            return Response(divisions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
    def post(self, request):
        """Insert a new division"""
        division_name = request.data.get('division_name')
        division_code = request.data.get('division_code')
 
        if not division_name or not division_code:
            return Response({'error': 'division_name and division_code are required'}, status=status.HTTP_400_BAD_REQUEST)
 
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # <- formatted timestamp
 
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_division (division_name, division_code, created_at)
                    VALUES (%s, %s, %s)
                """, [division_name, division_code, created_at])
            return Response({'message': 'Division created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
    def patch(self, request, division_id):
        """Update a division by ID"""
        division_name = request.data.get('division_name')
        division_code = request.data.get('division_code')
 
        if not division_name and not division_code:
            return Response({'error': 'At least one of division_name or division_code must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)
 
        try:
            with connection.cursor() as cursor:
                updates = []
                params = []
 
                if division_name:
                    updates.append("division_name = %s")
                    params.append(division_name)
                if division_code:
                    updates.append("division_code = %s")
                    params.append(division_code)
 
                params.append(division_id)
                sql = f"UPDATE ci_division SET {', '.join(updates)} WHERE division_id = %s"
                cursor.execute(sql, params)
 
                if cursor.rowcount == 0:
                    return Response({'error': 'Division not found'}, status=status.HTTP_404_NOT_FOUND)
 
            return Response({'message': 'Division updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def delete(self, request, division_id):
        """Delete a division by ID"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ci_division WHERE division_id = %s", [division_id])
 
                if cursor.rowcount == 0:
                    return Response({'error': 'Division not found'}, status=status.HTTP_404_NOT_FOUND)
 
            return Response({'message': 'Division deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class GradeAPI(APIView):
 
#     def get(self, request):
#         """Fetch all grades"""
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT grade_id, grade_name, grade_code, created_date FROM ci_grade")
#                 rows = cursor.fetchall()
#                 grades = []
#                 for row in rows:
#                     grades.append({
#                         'grade_id': row[0],
#                         'grade_name': row[1],
#                         'grade_code': row[2],
#                         'created_date': row[3]  # Already string, don't format
#                     })
#             return Response(grades, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
#     def post(self, request):
#         """Insert a new grade"""
#         grade_name = request.data.get('grade_name')
#         grade_code = request.data.get('grade_code')
 
#         if not grade_name or not grade_code:
#             return Response({'error': 'grade_name and grade_code are required'}, status=status.HTTP_400_BAD_REQUEST)
 
#         created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_grade (grade_name, grade_code, created_date)
#                     VALUES (%s, %s, %s)
#                 """, [grade_name, grade_code, created_date])
#             return Response({'message': 'Grade created successfully'}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
#     def patch(self, request, grade_id):
#         """Update a grade by ID"""
#         grade_name = request.data.get('grade_name')
#         grade_code = request.data.get('grade_code')
 
#         if not grade_name and not grade_code:
#             return Response({'error': 'At least one of grade_name or grade_code must be provided.'},
#                             status=status.HTTP_400_BAD_REQUEST)
 
#         try:
#             with connection.cursor() as cursor:
#                 updates = []
#                 params = []
 
#                 if grade_name:
#                     updates.append("grade_name = %s")
#                     params.append(grade_name)
#                 if grade_code:
#                     updates.append("grade_code = %s")
#                     params.append(grade_code)
 
#                 params.append(grade_id)
#                 sql = f"UPDATE ci_grade SET {', '.join(updates)} WHERE grade_id = %s"
#                 cursor.execute(sql, params)
 
#                 if cursor.rowcount == 0:
#                     return Response({'error': 'Grade not found'}, status=status.HTTP_404_NOT_FOUND)
 
#             return Response({'message': 'Grade updated successfully'}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
#     def delete(self, request, grade_id):
#         """Delete a grade by ID"""
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("DELETE FROM ci_grade WHERE grade_id = %s", [grade_id])
 
#                 if cursor.rowcount == 0:
#                     return Response({'error': 'Grade not found'}, status=status.HTTP_404_NOT_FOUND)
 
#             return Response({'message': 'Grade deleted successfully'}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompanySetupDashboardAPI(APIView):

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        d.department_id,
                        d.department_name,
                        COUNT(u.id) AS active_employee_count
                    FROM ci_departments d
                    LEFT JOIN ci_erp_users_details ud ON d.department_id = ud.department_id
                    LEFT JOIN ci_erp_users u ON ud.user_id = u.id AND u.is_active = 1
                    GROUP BY d.department_id, d.department_name
                """)
                rows = cursor.fetchall()
                response = []
                for row in rows:
                    response.append({
                        "department_id": row[0],
                        "department_name": row[1],
                        "active_employee_count": row[2]
                    })
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class EmployeeDesignationWiseCount(APIView):
    """
    GET API to fetch designation-wise user count
    """

    def get(self, request, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        eud.designation_id, 
                        d.designation_name, 
                        COUNT(*) AS total_users
                    FROM ci_erp_users AS eu
                    INNER JOIN ci_erp_users_details AS eud ON eu.id = eud.user_id
                    INNER JOIN ci_designations AS d ON d.designation_id = eud.designation_id
                    WHERE eu.is_active = 1
                    GROUP BY eud.designation_id, d.designation_name
                    ORDER BY total_users DESC;
                """)
                rows = cursor.fetchall()

                # Convert results to a list of dicts
                data = []
                for row in rows:
                    data.append({
                        "designation_id": row[0],
                        "designation_name": row[1],
                        "total_users": row[2]
                    })

            return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GradeWiseCount(APIView):
    """
    GET API to fetch grade-wise user count
    """

    def get(self, request, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        eud.grade_id, 
                        g.grade_name, 
                        COUNT(*) AS total_users
                    FROM ci_erp_users AS eu
                    INNER JOIN ci_erp_users_details AS eud ON eu.id = eud.user_id
                    INNER JOIN ci_grade AS g ON g.grade_id = eud.grade_id
                    WHERE eu.is_active = 1
                    GROUP BY eud.grade_id, g.grade_name
                    ORDER BY total_users DESC;
                """)
                rows = cursor.fetchall()

                # Convert results to a list of dicts
                data = []
                for row in rows:
                    data.append({
                        "grade_id": row[0],
                        "grade_name": row[1],
                        "total_users": row[2]
                    })

            return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class HeadquarterAPI(APIView):
 
#     def post(self, request):
#             try:
#                 data = request.data
#                 headquarter_id = data.get('headquarter_id')   # maps to location_id
#                 headquarter_name = data.get('headquarter_name')  # maps to location_name
#                 headquarter_code = data.get('headquarter_code')  # maps to location_short_name
#                 headquarter_address = data.get('headquarter_address')  # maps to location_address
#                 created_at = datetime.now().strftime('%Y-%m-%d')
 
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         INSERT INTO ci_headquarters (location_id, location_name, location_short_name, location_address, created_at)
#                         VALUES (%s, %s, %s, %s, %s)
#                     """, [headquarter_id, headquarter_name, headquarter_code, headquarter_address, created_at])
 
#                 return Response({
#                     "headquarter_id": headquarter_id,
#                     "headquarter_name": headquarter_name,
#                     "headquarter_code": headquarter_code,
#                     "headquarter_address": headquarter_address,
#                     "created_at": created_at
#                 }, status=status.HTTP_201_CREATED)
           
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
#     def get(self, request, headquarter_id=None):
#         try:
#             with connection.cursor() as cursor:
#                 if headquarter_id:
#                     cursor.execute("""
#                         SELECT location_id, location_name, location_short_name, location_address, created_at
#                         FROM ci_headquarters
#                         WHERE location_id = %s
#                     """, [headquarter_id])
#                     row = cursor.fetchone()
#                     if row:
#                         result = {
#                             "headquarter_id": row[0],
#                             "headquarter_name": row[1],
#                             "headquarter_code": row[2],
#                             "headquarter_address": row[3],
#                             "created_at": row[4].strftime('%Y-%m-%d') if row[4] else None
#                         }
#                     else:
#                         return Response({"error": "Headquarter not found."}, status=status.HTTP_404_NOT_FOUND)
#                 else:
#                     cursor.execute("""
#                         SELECT location_id, location_name, location_short_name, location_address, created_at
#                         FROM ci_headquarters
#                     """)
#                     rows = cursor.fetchall()
#                     result = [
#                         {
#                             "headquarter_id": row[0],
#                             "headquarter_name": row[1],
#                             "headquarter_code": row[2],
#                             "headquarter_address": row[3],
#                             "created_at": row[4].strftime('%Y-%m-%d') if row[4] else None
#                         }
#                         for row in rows
#                     ]
#             return Response(result, status=status.HTTP_200_OK)
 
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
#     def patch(self, request, headquarter_id):
#         try:
#             data = request.data
#             fields_to_update = []
#             values = []
 
#             if 'headquarter_name' in data:
#                 fields_to_update.append("location_name = %s")
#                 values.append(data.get('headquarter_name'))
 
#             if 'headquarter_code' in data:
#                 fields_to_update.append("location_short_name = %s")
#                 values.append(data.get('headquarter_code'))
 
#             if 'headquarter_address' in data:
#                 fields_to_update.append("location_address = %s")
#                 values.append(data.get('headquarter_address'))
 
#             if not fields_to_update:
#                 return Response({"message": "No valid fields provided for update."}, status=status.HTTP_400_BAD_REQUEST)
 
#             values.append(headquarter_id)
 
#             with connection.cursor() as cursor:
#                 cursor.execute(f"""
#                     UPDATE ci_headquarters
#                     SET {', '.join(fields_to_update)}
#                     WHERE location_id = %s
#                 """, values)
 
#             return Response({"message": "Headquarter updated successfully."}, status=status.HTTP_200_OK)
 
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
#     def delete(self, request, headquarter_id):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     DELETE FROM ci_headquarters
#                     WHERE location_id = %s
#                 """, [headquarter_id])
 
#             return Response({"message": "Headquarter deleted successfully."}, status=status.HTTP_200_OK)
 
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GradeAPI(APIView):
 
    def get(self, request):
        """Fetch all grades"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT grade_id, grade_name, grade_code, created_date FROM ci_grade")
                rows = cursor.fetchall()
                grades = []
                for row in rows:
                    grades.append({
                        
                        'grade_id': row[0],
                        'grade_name': row[1],
                        'grade_code': row[2],
                        'created_date': row[3]  # Already string, don't format
                    })
            return Response(grades, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def post(self, request):
        """Insert a new grade"""
        grade_name = request.data.get('grade_name')
        grade_code = request.data.get('grade_code')
        grade_id = request.data.get('grade_id')
 
        if not grade_name or not grade_code:
            return Response({'error': 'grade_id, grade_name and grade_code are required'}, status=status.HTTP_400_BAD_REQUEST)
 
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_grade (grade_id, grade_name, grade_code, created_date)
                    VALUES (%s, %s, %s, %s)
                """, [grade_id, grade_name, grade_code, created_date])
            return Response({'message': 'Grade created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
    def patch(self, request, id):
        """Update a grade by ID"""
        grade_name = request.data.get('grade_name')
        grade_code = request.data.get('grade_code')
        grade_id = request.data.get('grade_id')
 
        if not any([grade_id, grade_name, grade_code]):
            return Response({'error': 'At least one of grade_id, grade_name or grade_code must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)
 
        try:
            with connection.cursor() as cursor:
                updates = []
                params = []
 
                if grade_name:
                    updates.append("grade_name = %s")
                    params.append(grade_name)
                if grade_code:
                    updates.append("grade_code = %s")
                    params.append(grade_code)
                if grade_id:
                    updates.append("grade_id = %s")
                    params.append(grade_id)
 
 
                params.append(id)
                sql = f"UPDATE ci_grade SET {', '.join(updates)} WHERE grade_id = %s"
                cursor.execute(sql, params)
 
                if cursor.rowcount == 0:
                    return Response({'error': 'Grade not found'}, status=status.HTTP_404_NOT_FOUND)
 
            return Response({'message': 'Grade updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def delete(self, request, id):
        """Delete a grade by ID"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ci_grade WHERE grade_id = %s", [id])
 
                if cursor.rowcount == 0:
                    return Response({'error': 'Grade not found'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'message': 'Grade deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DepartmentView(APIView):
 
    def get(self, request, format=None):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    d.department_id,
                    d.department_name,
                    d.department_code,
                    d.company_id,
                    d.department_head,
                    CONCAT(u.first_name, ' ', IFNULL(u.middle_name, ''), ' ', u.last_name) AS department_head_name,
                    d.added_by,
                    d.created_at
                FROM ci_departments d
                LEFT JOIN ci_erp_users_details ud ON ud.employee_id = d.department_head
                LEFT JOIN ci_erp_users u ON u.id = ud.user_id
                ORDER BY d.department_id DESC
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(data)
 
    # def post(self, request, format=None):
    #     data = request.data
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             INSERT INTO ci_departments
    #             (department_name, department_code, company_id, department_head, added_by, created_at)
    #             VALUES (%s, %s, %s, %s, %s, NOW())
    #         """, [
    #             data.get('department_name'),
    #             data.get('department_code'),
    #             data.get('company_id', 2),
    #             data.get('department_head'),
    #             data.get('added_by', 2),
    #         ])
    #     return Response({"message": "Department created successfully"}, status=status.HTTP_201_CREATED)
    
    def post(self, request, format=None):
        data = request.data
        with connection.cursor() as cursor:
 
            department_code = request.data.get("department_code")
            department_name = request.data.get("department_name")
            department_head = request.data.get("department_head")
 
            if not all([department_code, department_name, department_head]):
                return Response({"status":"error","message": "some fields are missing"}, status=status.HTTP_400_BAD_REQUEST)
           
            cursor.execute("""
                INSERT INTO ci_departments
                (department_name, department_code, company_id, department_head, added_by, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, [
                department_name,
                department_code,
                data.get('company_id', 2),
                department_head,
                data.get('added_by', 2),
            ])
        return Response({"message": "Department created successfully"}, status=status.HTTP_201_CREATED)
    
    def patch(self, request, pk, format=None):
        data = request.data
        fields = []
        values = []
 
        for field in ['department_name', 'department_code', 'company_id', 'department_head', 'added_by']:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])
 
        if not fields:
            return Response({"error": "No valid fields provided"}, status=status.HTTP_400_BAD_REQUEST)
 
        values.append(pk)
 
        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE ci_departments
                SET {', '.join(fields)}
                WHERE department_id = %s
            """, values)
 
        return Response({"message": "Department updated successfully"}, status=status.HTTP_200_OK)
 
    def delete(self, request, pk, format=None):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ci_departments WHERE department_id = %s", [pk])
        return Response({"message": "Department deleted successfully"}, status=status.HTTP_200_OK)
 
 
class HeadquarterAPI(APIView):
 
    # def post(self, request):
    #         try:
    #             data = request.data
    #             headquarter_id = data.get('headquarter_id')   # maps to location_id
    #             headquarter_name = data.get('headquarter_name')  # maps to location_name
    #             headquarter_code = data.get('headquarter_code')  # maps to location_short_name
    #             headquarter_address = data.get('headquarter_address')  # maps to location_address
    #             created_at = datetime.now().strftime('%Y-%m-%d')
 
    #             with connection.cursor() as cursor:
    #                 cursor.execute("""
    #                     INSERT INTO ci_headquarters (location_id, location_name, location_short_name, location_address, created_at)
    #                     VALUES (%s, %s, %s, %s, %s)
    #                 """, [headquarter_id, headquarter_name, headquarter_code, headquarter_address, created_at])

    #             return Response({
    #                 "headquarter_id": headquarter_id,
    #                 "headquarter_name": headquarter_name,
    #                 "headquarter_code": headquarter_code,
    #                 "headquarter_address": headquarter_address,
    #                 "created_at": created_at
    #             }, status=status.HTTP_201_CREATED)
           
    #         except Exception as e:
    #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
    def post(self, request):
        try:
            data = request.data
 
            # Frontend fields
            headquarter_name = data.get('headquarter_name')
            headquarter_code = data.get('headquarter_code')
            headquarter_address = data.get('headquarter_address')
            created_at = data.get('created_at', datetime.now().strftime('%Y-%m-%d'))  # allow frontend to send date
            company_id = data.get('company_id', 2)   # default company_id if not provided
            status_value = data.get('status', 'Y')     # default status=1 (active)
 
            # Validation
            if not all([headquarter_name, headquarter_code, headquarter_address]):
                return Response(
                    {"error": " headquarter_name, headquarter_code, and headquarter_address are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
 
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_headquarters
                        ( location_name, location_short_name, location_address, created_at, company_id, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                   
                    headquarter_name,           # maps to location_name
                    headquarter_code,           # maps to location_short_name
                    headquarter_address,        # maps to location_address
                    created_at,                 # created date
                    company_id,                 # default or from frontend
                    status_value                # default active
                ])

            # Respond back in the same frontend format
            return Response({

                "headquarter_name": headquarter_name,
                "headquarter_code": headquarter_code,
                "headquarter_address": headquarter_address,
                "created_at": created_at,
                "company_id": company_id,
                "status": status_value
            }, status=status.HTTP_201_CREATED)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, headquarter_id=None):
        try:
            with connection.cursor() as cursor:
                if headquarter_id:
                    cursor.execute("""
                        SELECT location_id, location_name, location_short_name, location_address, created_at
                        FROM ci_headquarters
                        WHERE location_id = %s
                    """, [headquarter_id])
                    row = cursor.fetchone()
                    if row:
                        result = {
                            "headquarter_id": row[0],
                            "headquarter_name": row[1],
                            "headquarter_code": row[2],
                            "headquarter_address": row[3],
                            "created_at": row[4].strftime('%Y-%m-%d') if row[4] else None
                        }
                    else:
                        return Response({"error": "Headquarter not found."}, status=status.HTTP_404_NOT_FOUND)
                else:
                    cursor.execute("""
                        SELECT location_id, location_name, location_short_name, location_address, created_at
                        FROM ci_headquarters
                    """)
                    rows = cursor.fetchall()
                    result = [
                        {
                            "headquarter_id": row[0],
                            "headquarter_name": row[1],
                            "headquarter_code": row[2],
                            "headquarter_address": row[3],
                            "created_at": row[4].strftime('%Y-%m-%d') if row[4] else None
                        }
                        for row in rows
                    ]
            return Response(result, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, headquarter_id):
        try:
            data = request.data
            fields_to_update = []
            values = []
 
            if 'headquarter_name' in data:
                fields_to_update.append("location_name = %s")
                values.append(data.get('headquarter_name'))
 
            if 'headquarter_code' in data:
                fields_to_update.append("location_short_name = %s")
                values.append(data.get('headquarter_code'))
 
            if 'headquarter_address' in data:
                fields_to_update.append("location_address = %s")
                values.append(data.get('headquarter_address'))
 
            if not fields_to_update:
                return Response({"message": "No valid fields provided for update."}, status=status.HTTP_400_BAD_REQUEST)
 
            values.append(headquarter_id)
 
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE ci_headquarters
                    SET {', '.join(fields_to_update)}
                    WHERE location_id = %s
                """, values)
 
            return Response({"message": "Headquarter updated successfully."}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, headquarter_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM ci_headquarters
                    WHERE location_id = %s
                """, [headquarter_id])
 
            return Response({"message": "Headquarter deleted successfully."}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class CompanyDetailsAPI(APIView):

#     def post(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SUNT(*) FROM ci_company_details WHERE is_posted = 1")
#                 posted = cursor.fetchone()[0]
#                 if posted > 0:
#                     return Response({"error": "Company details already posted. Use PUT to update."},
#                                     status=status.HTTP_400_BAD_REQUEST)

#             data = request.data
#             company_name = data.get('company_name')
#             register_address = data.get('register_address')
#             manufacturing_address = data.get('manufacturing_address')
#             phone_number = data.get('phone_number')
#             pan_number = data.get('pan_number')

#             if not (phone_number and len(phone_number) == 10 and phone_number.isdigit()):
#                 return Response({"error": "Phone number must be exactly 10 digits."},
#                                 status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO ci_company_details 
#                     (company_name, register_address, manufacturing_address, phone_number, pan_number, is_posted)
#                     VALUES (%s, %s, %s, %s, %s, 1)
#                 """, [company_name, register_address, manufacturing_address, phone_number, pan_number])

#             return Response({"message": "Company details created and marked as posted."},
#                             status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def patch(self, request):
#         try:
#             data = request.data

#             allowed_fields = [
#                 "company_name",
#                 "register_address",
#                 "manufacturing_address",
#                 "phone_number",
#                 "pan_number"
#             ]

#             if "phone_number" in data:
#                 phone_number = data.get("phone_number")
#                 if not (phone_number and len(phone_number) == 10 and phone_number.isdigit()):
#                     return Response({"error": "Phone number must be exactly 10 digits."},
#                                     status=status.HTTP_400_BAD_REQUEST)

#             update_fields = {field: data[field] for field in allowed_fields if field in data}

#             if not update_fields:
#                 return Response({"error": "No valid fields provided for update."}, status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT company_detail_id FROM ci_company_details WHERE is_posted = 1 LIMIT 1")
#                 row = cursor.fetchone()
#                 if not row:
#                     return Response({"error": "No posted company details found to update."},
#                                     status=status.HTTP_404_NOT_FOUND)

#                 company_id = row[0]

#                 set_clause = ", ".join([f"{key} = %s" for key in update_fields])
#                 values = list(update_fields.values())
#                 values.append(company_id)

#                 cursor.execute(f"""
#                     UPDATE ci_company_details
#                     SET {set_clause}
#                     WHERE company_detail_id = %s
#                 """, values)

#             return Response({"message": "Company details updated successfully."}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def get(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT company_detail_id, company_name, register_address, manufacturing_address, phone_number, pan_number, created_date
#                     FROM ci_company_details
#                     ORDER BY company_detail_id DESC
#                     LIMIT 1
#                 """)
#                 row = cursor.fetchone()
#                 if not row:
#                     return Response({"message": "No company details found."}, status=status.HTTP_404_NOT_FOUND)

#                 result = {
#                     "company_detail_id": row[0],
#                     "company_name": row[1],
#                     "register_address": row[2],
#                     "manufacturing_address": row[3],
#                     "phone_number": row[4],
#                     "pan_number": row[5],
#                     "created_date": row[6]
#                 }

#                 return Response(result, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyDetailsAPI(APIView):
 
    def post(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SUNT(*) FROM ci_company_details WHERE is_posted = 1")
                posted = cursor.fetchone()[0]
                if posted > 0:
                    return Response({"error": "Company details already posted. Use PATCH to update."},
                                    status=status.HTTP_400_BAD_REQUEST)
 
            data = request.data
            company_name = data.get('company_name')
            register_address = data.get('register_address')
            manufacturing_address = data.get('manufacturing_address')
            phone_number = data.get('phone_number')
            pan_number = data.get('pan_number')
            company_stamp = data.get('company_stamp')
 
            if not (phone_number and len(phone_number) == 10 and phone_number.isdigit()):
                return Response({"error": "Phone number must be exactly 10 digits."},
                                status=status.HTTP_400_BAD_REQUEST)
 
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_company_details
                    (company_name, register_address, manufacturing_address, phone_number, pan_number, is_posted, company_stamp)
                    VALUES (%s, %s, %s, %s, %s, 1, %s)
                """, [company_name, register_address, manufacturing_address, phone_number, pan_number, company_stamp])
 
            return Response({"message": "Company details created and marked as posted."},
                            status=status.HTTP_201_CREATED)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def patch(self, request):
        try:
            data = request.data
 
            allowed_fields = [
                "company_name",
                "register_address",
                "manufacturing_address",
                "phone_number",
                "pan_number",
                "company_stamp"
            ]
 
            if "phone_number" in data:
                phone_number = data.get("phone_number")
                if not (phone_number and len(phone_number) == 10 and phone_number.isdigit()):
                    return Response({"error": "Phone number must be exactly 10 digits."},
                                    status=status.HTTP_400_BAD_REQUEST)
 
            update_fields = {field: data[field] for field in allowed_fields if field in data}
 
            if not update_fields:
                return Response({"error": "No valid fields provided for update."}, status=status.HTTP_400_BAD_REQUEST)
 
            with connection.cursor() as cursor:
                cursor.execute("SELECT company_detail_id FROM ci_company_details WHERE is_posted = 1 LIMIT 1")
                row = cursor.fetchone()
                if not row:
                    return Response({"error": "No posted company details found to update."},
                                    status=status.HTTP_404_NOT_FOUND)
 
                company_id = row[0]
 
                set_clause = ", ".join([f"{key} = %s" for key in update_fields])
                values = list(update_fields.values())
                values.append(company_id)
 
                cursor.execute(f"""
                    UPDATE ci_company_details
                    SET {set_clause}
                    WHERE company_detail_id = %s
                """, values)
 
            return Response({"message": "Company details updated successfully."}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT company_detail_id, company_name, register_address, manufacturing_address, phone_number, pan_number, created_date, company_stamp
                    FROM ci_company_details
                    ORDER BY company_detail_id DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                if not row:
                    return Response({"message": "No company details found."}, status=status.HTTP_404_NOT_FOUND)
 
                result = {
                    "company_detail_id": row[0],
                    "company_name": row[1],
                    "register_address": row[2],
                    "manufacturing_address": row[3],
                    "phone_number": row[4],
                    "pan_number": row[5],
                    "created_date": row[6],
                    "company_stamp": row[7]
                }
 
                return Response(result, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ClientAPI(APIView):
    def post(self, request):
        try:
            full_name = request.data.get('full_name')
            company_name = request.data.get('company_name')
            contact_number = request.data.get('contact_number')
            gender = request.data.get('gender')
            email_address = request.data.get('email_address')
            profile_picture = request.FILES.get('profile_picture')
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            filename = None
            if profile_picture:
                # Normalize file path for DB (forward slashes)
                filename = f"clients_profile_pictures/{profile_picture.name}".replace("\\", "/")
                # File save path for disk (OS specific)
                save_path = os.path.join(settings.MEDIA_ROOT, filename.replace("/", os.sep))

                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb+') as f:
                    for chunk in profile_picture.chunks():
                        f.write(chunk)

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_clients
                    (full_name, company_name, contact_number, gender, email_address, profile_picture, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [full_name, company_name, contact_number, gender, email_address, filename, created_at])

            return Response({"message": "Client details Created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, client_id=None):
        try:
            with connection.cursor() as cursor:
                if client_id:
                    cursor.execute("""
                        SELECT id, full_name, company_name, contact_number, gender, email_address, profile_picture, created_at
                        FROM ci_clients
                        WHERE id = %s
                    """, [client_id])
                else:
                    cursor.execute("""
                        SELECT id, full_name, company_name, contact_number, gender, email_address, profile_picture, created_at
                        FROM ci_clients
                    """)
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    result.append({
                        "id": row[0],
                        "full_name": row[1],
                        "company_name": row[2],
                        "contact_number": row[3],
                        "gender": row[4],
                        "email_address": row[5],
                        "profile_picture": request.build_absolute_uri(settings.MEDIA_URL + row[6]) if row[6] else None,
                        "created_at": row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else None,
                    })
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, client_id):
        try:
            data = request.data
            profile_picture = request.FILES.get('profile_picture')
 
            update_fields = []
            params = []
 
            # Add fields only if they are provided
            if 'full_name' in data:
                update_fields.append("full_name = %s")
                params.append(data.get('full_name'))
 
            if 'company_name' in data:
                update_fields.append("company_name = %s")
                params.append(data.get('company_name'))
 
            if 'contact_number' in data:
                update_fields.append("contact_number = %s")
                params.append(data.get('contact_number'))
 
            if 'gender' in data:
                update_fields.append("gender = %s")
                params.append(data.get('gender'))
 
            if 'email_address' in data:
                update_fields.append("email_address = %s")
                params.append(data.get('email_address'))
 
            if profile_picture:
                folder_path = os.path.join(settings.MEDIA_ROOT, 'clients_profile_pictures')
                os.makedirs(folder_path, exist_ok=True)
                filename = os.path.join('clients_profile_pictures', profile_picture.name)
                with open(os.path.join(settings.MEDIA_ROOT, filename), 'wb+') as f:
                    for chunk in profile_picture.chunks():
                        f.write(chunk)
                update_fields.append("profile_picture = %s")
                params.append(filename)
 
            if not update_fields:
                return Response({"message": "No valid fields provided for update."}, status=status.HTTP_400_BAD_REQUEST)

            # Finalize query
            update_query = f"""
                UPDATE ci_clients
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            params.append(client_id)

            with connection.cursor() as cursor:
                cursor.execute(update_query, params)
 
            return Response({"message": "Client updated successfully."}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, client_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM ci_clients WHERE id = %s
                """, [client_id])
            return Response({"message": "Client deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminProjectAPI(APIView):

    def post(self, request):
        try:
            data = request.data
            client_full_name = data.get('client_id')  # full name passed in place of ID
            title = data.get('title')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            assigned_to = data.get('assigned_to')
            priority = data.get('priority')
            budget_hours = data.get('budget_hours')
            project_progress = data.get('project_progress')
            summary = data.get('summary')
            description = data.get('description')
            project_note = data.get('project_note')
            associated_goals = data.get('associated_goals')
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            project_status = 1
            company_id = 2
            added_by = 1  # Set appropriately for your use case

            # Look up actual client ID using full name (case-insensitive and trimmed)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM ci_clients 
                    WHERE LOWER(TRIM(full_name)) = LOWER(TRIM(%s))
                """, [client_full_name])
                client = cursor.fetchone()
                if not client:
                    return Response({"error": "Client with given name not found."}, status=status.HTTP_400_BAD_REQUEST)
                client_id = client[0]

            # Insert into ci_projects
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_projects (
                        title, client_id, company_id, start_date, end_date, assigned_to,
                        priority, budget_hours, project_progress, summary, description,
                        project_note, associated_goals, status, created_at, added_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    title, client_id, company_id, start_date, end_date, assigned_to,
                    priority, budget_hours, project_progress, summary, description,
                    project_note, associated_goals, project_status, created_at, added_by
                ])

            return Response({"message": "Project created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.project_id, p.title, c.full_name AS client_name, p.start_date, p.end_date,
                        p.assigned_to, p.priority, p.budget_hours, p.project_progress,
                        p.summary, p.description, p.project_note, p.associated_goals,
                        p.status, p.created_at
                    FROM ci_projects p
                    LEFT JOIN ci_clients c ON p.client_id = c.id
                """)
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    assigned_to_ids = row[5].split(',') if row[5] else []
                    assigned_to_names = []

                    if assigned_to_ids:
                        with connection.cursor() as emp_cursor:
                            emp_cursor.execute("""
                                SELECT username, first_name, last_name FROM ci_erp_users
                                WHERE username IN %s
                            """, [tuple(assigned_to_ids)])
                            emp_rows = emp_cursor.fetchall()
                            emp_map = {str(emp[0]): f"{emp[1]} {emp[2]}" for emp in emp_rows}
                            assigned_to_names = [emp_map.get(emp_id, emp_id) for emp_id in assigned_to_ids]

                    result.append({
                        "id": row[0],
                        "title": row[1],
                        "client_name": row[2],
                        "start_date": row[3],
                        "end_date": row[4],
                        "assigned_to": ", ".join(assigned_to_names),
                        "priority": row[6],
                        "budget_hours": row[7],
                        "project_progress": row[8],
                        "summary": row[9],
                        "description": row[10],
                        "project_note": row[11],
                        "associated_goals": row[12],
                        "status": row[13],
                        "created_at": row[14],
                    })
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, project_id):
        try:
            data = request.data
            fields = []
            values = []
 
            # Check and resolve client_id if client_id (actually full_name) is passed
            client_full_name = data.get('client_id')
            if client_full_name:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM ci_clients WHERE full_name = %s", [client_full_name])
                    client = cursor.fetchone()
                    if not client:
                        return Response({"error": "Client with given name not found."}, status=status.HTTP_400_BAD_REQUEST)
                    fields.append("client_id = %s")
                    values.append(client[0])
 
            # Map optional fields
            field_mappings = {
                'title': 'title',
                'start_date': 'start_date',
                'end_date': 'end_date',
                'assigned_to': 'assigned_to',
                'priority': 'priority',
                'budget_hours': 'budget_hours',
                'project_progress': 'project_progress',
                'summary': 'summary',
                'description': 'description',
                'project_note': 'project_note',
                'associated_goals': 'associated_goals',
            }
 
            for key, column in field_mappings.items():
                if key in data:
                    fields.append(f"{column} = %s")
                    values.append(data.get(key))
 
            if not fields:
                return Response({"error": "No valid fields to update."}, status=status.HTTP_400_BAD_REQUEST)
 
            values.append(project_id)
 
            # Update only the provided fields
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE ci_projects
                    SET {', '.join(fields)}
                    WHERE project_id = %s
                """, values)
 
            return Response({"message": "Project updated successfully."}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def delete(self, request, project_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ci_projects WHERE project_id = %s", [project_id])
            return Response({"message": "Project deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class ProjectProgressCountAPI(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        CAST(SUM(CASE WHEN project_progress = 100 THEN 1 ELSE 0 END) AS SIGNED) AS completed,
                        CAST(SUM(CASE WHEN project_progress BETWEEN 1 AND 99 THEN 1 ELSE 0 END) AS SIGNED) AS in_progress,
                        CAST(SUM(CASE WHEN project_progress = 0 THEN 1 ELSE 0 END) AS SIGNED) AS not_started,
                        CAST(SUM(CASE WHEN status = 0 THEN 1 ELSE 0 END) AS SIGNED) AS on_hold
                    FROM ci_projects
                """)
                row = cursor.fetchone()
                result = {
                    "completed": row[0],
                    "in_progress": row[1],
                    "not_started": row[2],
                    "on_hold": row[3]
                }
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TaskAPI(APIView):

    def post(self, request):
        try:
            data = request.data
            project_title = data.get('project_title')
            company_id = 2  # default
            task_name = data.get('task_name')
            description = data.get('description')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            task_progress = int(data.get('task_progress', 0))
            assigned_to = data.get('assigned_to')
            task_status = data.get('task_status')
            priority = data.get('priority')
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Get project_id from title
            with connection.cursor() as cursor:
                cursor.execute("SELECT project_id FROM ci_projects WHERE title = %s", [project_title])
                project = cursor.fetchone()
                if not project:
                    return Response({"error": "Project with given title not found."}, status=status.HTTP_400_BAD_REQUEST)
                project_id = project[0]

                # Insert task
                cursor.execute("""
                    INSERT INTO ci_tasks (
                        project_id, company_id, task_name, description, start_date, end_date,
                        task_progress, assigned_to, task_status, priority, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    project_id, company_id, task_name, description, start_date, end_date,
                    task_progress, assigned_to, task_status, priority, created_at
                ])

            return Response({"message": "Task created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        t.task_id, p.title as project_title, t.task_name, t.description,
                        t.start_date, t.end_date, t.task_progress, t.assigned_to,
                        t.task_status, t.priority, t.created_at
                    FROM ci_tasks t
                    LEFT JOIN ci_projects p ON t.project_id = p.project_id
                """)
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    result.append({
                        "task_id": row[0],
                        "project_title": row[1],
                        "task_name": row[2],
                        "description": row[3],
                        "start_date": row[4],
                        "end_date": row[5],
                        "task_progress": row[6],
                        "assigned_to": row[7],
                        "task_status": row[8],
                        "priority": row[9],
                        "created_at": row[10]
                    })
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, task_id):
        try:
            data = request.data
            fields = []
            values = []
 
            # Handle optional project_title -> project_id conversion
            project_title = data.get('project_title')
            if project_title:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT project_id FROM ci_projects WHERE title = %s", [project_title])
                    project = cursor.fetchone()
                    if not project:
                        return Response({"error": "Invalid project_title"}, status=status.HTTP_400_BAD_REQUEST)
                    fields.append("project_id = %s")
                    values.append(project[0])
 
            # Map remaining fields
            field_mappings = {
                'task_name': 'task_name',
                'description': 'description',
                'start_date': 'start_date',
                'end_date': 'end_date',
                'task_progress': 'task_progress',
                'assigned_to': 'assigned_to',
                'task_status': 'task_status',
                'priority': 'priority',
                'summary': 'summary',
            }
 
            for key, column in field_mappings.items():
                if key in data:
                    fields.append(f"{column} = %s")
                    values.append(data.get(key))
 
            if not fields:
                return Response({"error": "No fields provided for update"}, status=status.HTTP_400_BAD_REQUEST)
 
            values.append(task_id)
 
            # Execute update with only provided fields
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE ci_tasks
                    SET {', '.join(fields)}
                    WHERE task_id = %s
                """, values)
 
            return Response({"message": "Task updated successfully"}, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, task_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ci_tasks WHERE task_id = %s", [task_id])
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


####### Employee Tasks section
class EmployeeTasksView(APIView):
    def get(self, request, employee_id):
        try:
            with connection.cursor() as cursor:
                # Get distinct project IDs for this employee
                cursor.execute("""
                    SELECT DISTINCT project_id FROM ci_tasks
                    WHERE FIND_IN_SET(%s, assigned_to)
                """, [employee_id])
                project_rows = cursor.fetchall()

                response_data = []

                for project_row in project_rows:
                    project_id = project_row[0]

                    # Get tasks under this project for this employee
                    cursor.execute("""
                        SELECT * FROM ci_tasks
                        WHERE project_id = %s AND FIND_IN_SET(%s, assigned_to)
                    """, [project_id, employee_id])
                    task_rows = cursor.fetchall()
                    task_columns = [col[0] for col in cursor.description]

                    tasks = []
                    for task_row in task_rows:
                        task_dict = dict(zip(task_columns, task_row))
                        task_id = task_dict['task_id']

                        # Get discussions for this task
                        cursor.execute("""
                            SELECT * FROM ci_tasks_discussion WHERE task_id = %s
                        """, [task_id])
                        discussions = dictfetchall(cursor)

                        # Get files for this task
                        cursor.execute("""
                            SELECT * FROM ci_tasks_files WHERE task_id = %s
                        """, [task_id])
                        files = dictfetchall(cursor)

                        # Get notes for this task
                        cursor.execute("""
                            SELECT * FROM ci_tasks_notes WHERE task_id = %s
                        """, [task_id])
                        notes = dictfetchall(cursor)

                        task_dict['discussions'] = discussions
                        task_dict['files'] = files
                        task_dict['notes'] = notes

                        tasks.append(task_dict)

                    response_data.append({
                        'project_id': project_id,
                        'tasks': tasks
                    })

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddTaskDiscussion(APIView):
    def post(self, request, task_id):
        try:
            employee_id = request.data.get('employee_id')
            discussion_text = request.data.get('discussion_text')

            if not all([employee_id, discussion_text]):
                return Response(
                    {"error": "employee_id and discussion_text are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with connection.cursor() as cursor:
                # Get company_id from tasks table
                cursor.execute("""
                    SELECT company_id FROM ci_tasks WHERE task_id = %s
                """, [task_id])
                row = cursor.fetchone()

                if not row:
                    return Response({"error": "Invalid task_id."}, status=status.HTTP_404_NOT_FOUND)

                company_id = row[0]

                # Insert into ci_tasks_discussion
                cursor.execute("""
                    INSERT INTO ci_tasks_discussion 
                    (company_id, task_id, employee_id, discussion_text, created_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, [company_id, task_id, employee_id, discussion_text])

            return Response({"message": "Discussion added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddTaskNote(APIView):
    def post(self, request, task_id):
        try:
            employee_id = request.data.get('employee_id')
            task_note = request.data.get('task_note')

            if not all([employee_id, task_note]):
                return Response(
                    {"error": "employee_id and task_note are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with connection.cursor() as cursor:
                # Fetch company_id from ci_tasks
                cursor.execute("""
                    SELECT company_id FROM ci_tasks WHERE task_id = %s
                """, [task_id])
                row = cursor.fetchone()

                if not row:
                    return Response({"error": "Invalid task_id."}, status=status.HTTP_404_NOT_FOUND)

                company_id = row[0]

                # Insert into ci_tasks_notes
                cursor.execute("""
                    INSERT INTO ci_tasks_notes 
                    (company_id, task_id, employee_id, task_note, created_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, [company_id, task_id, employee_id, task_note])

            return Response({"message": "Task note added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.utils.crypto import get_random_string
class AddTaskAttachment(APIView):
    def post(self, request, task_id):
        try:
            employee_id = request.data.get('employee_id')
            file_title = request.data.get('file_title')
            attachment_file = request.FILES.get('attachment_file')

            if not all([employee_id, file_title, attachment_file]):
                return Response(
                    {"error": "employee_id, file_title, and attachment_file are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with connection.cursor() as cursor:
                # Fetch company_id from ci_tasks
                cursor.execute("""
                    SELECT company_id FROM ci_tasks WHERE task_id = %s
                """, [task_id])
                row = cursor.fetchone()

                if not row:
                    return Response({"error": "Invalid task_id."}, status=status.HTTP_404_NOT_FOUND)

                company_id = row[0]

            # Save file to media/task_attachment/
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'task_attachment')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            # Generate unique file name
            filename = get_random_string(10) + '_' + attachment_file.name
            file_path = os.path.join(upload_dir, filename)

            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in attachment_file.chunks():
                    destination.write(chunk)

            # Save path relative to MEDIA_ROOT in DB (you can customize this if needed)
            relative_file_path = f'task_attachment/{filename}'

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_tasks_files 
                    (company_id, task_id, employee_id, file_title, attachment_file, created_at)
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, [company_id, task_id, employee_id, file_title, relative_file_path])

            return Response({"message": "Attachment uploaded successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse
from django.db import connection
import json
from datetime import datetime
 
@method_decorator(csrf_exempt, name='dispatch')
class EmployeeSupportTicketView(View):
    def get(self, request, employee_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.id, e.employee_id, e.subject, e.priority, e.description, e.created_at , e.ticket_status,
                           n.ticket_note, r.reply_text, f.attachment_file
                FROM ci_support_tickets_employee e
                LEFT JOIN ci_support_ticket_notes n ON e.id=n.ticket_id
                LEFT JOIN ci_support_ticket_reply r ON e.id=r.ticket_id
                LEFT JOIN ci_support_ticket_files f ON e.id=f.ticket_id
                WHERE e.employee_id = %s
                ORDER BY e.created_at DESC
            """, [employee_id])
            rows = cursor.fetchall()

            status_map = {0: "Open", 1: "Closed"}
 
            tickets = []
            for row in rows:
                tickets.append({
                    "id": row[0],
                    "employee_id": row[1],
                    "subject": row[2],
                    "priority": row[3],
                    "description": row[4],
                    "created_at": row[5].strftime('%Y-%m-%d %H:%M:%S'),
                    "ticket_status": status_map.get(row[6], "Unknown"),                    
                    "note":row[7],
                    "reply":row[8],
                    "attachment":row[9],
 
                })
 
        return JsonResponse(tickets, safe=False)
 
    def post(self, request, employee_id):
        try:
            data = json.loads(request.body)
            subject = data.get('subject')
            priority = data.get('priority')
            description = data.get('description')
 
            if not subject or priority not in ['Low', 'Medium', 'High', 'Critical']:
                return JsonResponse({'error': 'Invalid subject or priority'}, status=400)
 
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_support_tickets_employee (employee_id, subject, priority, description, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, [employee_id, subject, priority, description, datetime.now()])
 
            return JsonResponse({'message': 'Ticket created successfully'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
 
 


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
@method_decorator(csrf_exempt, name='dispatch')
class AdminSupportTicketView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)


    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ste.id,
                        ste.employee_id,
                        CONCAT(eu.first_name, ' ', eu.last_name) AS employee_name,
                        d.department_name AS department_name,
                        ste.subject,
                        ste.priority,
                        ste.description,
                        ste.created_at,
                        ste.ticket_status,
                        ste.updated_at
                    FROM ci_support_tickets_employee ste
                    LEFT JOIN ci_erp_users_details eud ON ste.employee_id = eud.employee_id
                    LEFT JOIN ci_erp_users eu ON eud.user_id = eu.id
                    LEFT JOIN ci_departments d ON eud.department_id = d.department_id
                    ORDER BY ste.created_at DESC
                """)
                rows = cursor.fetchall()

                status_map = {0: "Open", 1: "Closed"}

                tickets = [{
                    "id": row[0],
                    "employee_id": row[1],
                    "employee_name": row[2],
                    "department_name": row[3],
                    "subject": row[4],
                    "priority": row[5],
                    "description": row[6],
                    "created_at": row[7].strftime('%Y-%m-%d') if row[7] else None,
                    "ticket_status": status_map.get(row[8], "Unknown"),
                    "updated_at": row[9]
                } for row in rows]

            return Response(tickets, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)



    def patch(self, request, ticket_id):
        status_value = request.data.get('status')
        note = request.data.get('note')
        reply = request.data.get('reply')
        files = request.FILES.getlist('attachments')

        # Map status text to int
        status_map = {"Open": 0, "Closed": 1}
        ticket_status_value = status_map.get(str(status_value).capitalize())

        if ticket_status_value is None:
            return Response({"error": "Invalid status value"}, status=400)

        try:
            with connection.cursor() as cursor:
                # Check if ticket exists
                cursor.execute("""
                    SELECT id FROM ci_support_tickets_employee
                    WHERE id = %s
                """, [ticket_id])
                ticket = cursor.fetchone()

                if not ticket:
                    return Response({"error": "Ticket not found"}, status=404)

                # Update ticket status in ci_support_tickets_employee
                cursor.execute("""
                    UPDATE ci_support_tickets_employee
                    SET ticket_status = %s
                    WHERE id = %s
                """, [ticket_status_value, ticket_id])

                # Update ticket status in ci_support_tickets (if entry exists)
                cursor.execute("""
                    UPDATE ci_support_tickets
                    SET ticket_status = %s
                    WHERE ticket_code = %s
                """, [ticket_status_value, ticket_id])

                # Insert or Update Note
                if note:
                    cursor.execute("""
                        SELECT ticket_note_id FROM ci_support_ticket_notes WHERE ticket_id = %s
                    """, [ticket_id])
                    note_exists = cursor.fetchone()

                    if note_exists:
                        cursor.execute("""
                            UPDATE ci_support_ticket_notes
                            SET ticket_note = %s, created_at = %s
                            WHERE ticket_id = %s
                        """, [ note, timezone.now(), ticket_id])
                    else:
                        cursor.execute("""
                            INSERT INTO ci_support_ticket_notes (ticket_id, ticket_note, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [ticket_id, note, timezone.now()])

                # Insert or Update Reply
                if reply:
                    cursor.execute("""
                        SELECT ticket_reply_id FROM ci_support_ticket_reply WHERE ticket_id = %s
                    """, [ticket_id])
                    reply_exists = cursor.fetchone()

                    if reply_exists:
                        cursor.execute("""
                            UPDATE ci_support_ticket_reply
                            SET  sent_by = %s, assign_to = %s, reply_text = %s, created_at = %s
                            WHERE ticket_id = %s
                        """, [ reply, timezone.now(), ticket_id])
                    else:
                        cursor.execute("""
                            INSERT INTO ci_support_ticket_reply ( sent_by, assign_to, reply_text, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, [ ticket_id, reply, timezone.now()])

                # Insert or Update File (only first file)
                if files:
                    file = files[0]
                    file_path = os.path.join('ticket_attachment', file.name)
                    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

                    with open(full_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)

                    cursor.execute("""
                        SELECT ticket_file_id FROM ci_support_ticket_files WHERE ticket_id = %s
                    """, [ticket_id])
                    file_exists = cursor.fetchone()

                    if file_exists:
                        cursor.execute("""
                            UPDATE ci_support_ticket_files
                            file_title = %s, attachment_file = %s, created_at = %s
                            WHERE ticket_id = %s
                        """, [ file.name, file_path, timezone.now(), ticket_id])
                    else:
                        cursor.execute("""
                            INSERT INTO ci_support_ticket_files ( file_title, attachment_file, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, [ticket_id, file.name, file_path, timezone.now()])


            return Response({"message": "Ticket status updated successfully"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


    def delete(self, request, ticket_id):
        try:
            with connection.cursor() as cursor:
                # Check if ticket exists in employee table
                cursor.execute("""
                    SELECT id FROM ci_support_tickets_employee
                    WHERE id = %s
                """, [ticket_id])
                ticket = cursor.fetchone()

                if not ticket:
                    return Response({"error": "Ticket not found"}, status=404)

                # Delete related records (notes, replies, files)
                cursor.execute("""
                    DELETE FROM ci_support_ticket_notes
                    WHERE ticket_id = %s
                """, [ticket_id])

                cursor.execute("""
                    DELETE FROM ci_support_ticket_reply
                    WHERE ticket_id = %s
                """, [ticket_id])

                cursor.execute("""
                    DELETE FROM ci_support_ticket_files
                    WHERE ticket_id = %s
                """, [ticket_id])

                # Delete from support_tickets
                cursor.execute("""
                    DELETE FROM ci_support_tickets
                    WHERE ticket_code = %s
                """, [ticket_id])

                # Finally, delete from support_tickets_employee
                cursor.execute("""
                    DELETE FROM ci_support_tickets_employee
                    WHERE id = %s
                """, [ticket_id])

            return Response({"message": "Ticket deleted successfully"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)




# Leave Application API



# class LeaveApplicationAPI(APIView):

#     def get(self, request):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                         la.leave_id,
#                         la.company_id,
#                         ud.employee_id,  -- Employee ID from ci_erp_users_details
#                         CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                         u.email AS employee_email,
#                         c.category_name AS leave_type,
#                         la.from_date,
#                         la.to_date,
#                         CASE 
#                             WHEN la.from_date IS NOT NULL AND la.to_date IS NOT NULL 
#                                 AND la.to_date >= la.from_date
#                             THEN DATEDIFF(la.to_date, la.from_date) + 1
#                             ELSE 0
#                         END AS leave_days,
#                         la.reason,
#                         la.remarks,
#                         la.status,
#                         la.created_at
#                     FROM 
#                         ci_leave_applications la
#                     LEFT JOIN 
#                         ci_erp_users u ON u.id = la.employee_id
#                     LEFT JOIN 
#                         ci_erp_users_details ud ON ud.user_id = u.id   -- New JOIN to get employee_id
#                     LEFT JOIN 
#                         ci_erp_constants c ON c.constants_id = la.leave_type_id AND c.type = 'leave_type'
#                     ORDER BY 
#                         STR_TO_DATE(la.created_at, '%Y-%m-%d') DESC

#             """)
#             columns = [col[0] for col in cursor.description]
#             leave_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

#             # Sum of leave days only where dates are valid
#             cursor.execute("""
#                 SELECT 
#                     SUM(
#                         CASE 
#                             WHEN from_date IS NOT NULL AND to_date IS NOT NULL 
#                                 AND to_date >= from_date
#                             THEN DATEDIFF(to_date, from_date) + 1
#                             ELSE 0
#                         END
#                     ) AS total_leave_days
#                 FROM ci_leave_applications
#             """)
#             total_days_row = cursor.fetchone()
#             total_leave_days = total_days_row[0] if total_days_row[0] is not None else 0

#         return Response({
#             "leave_count": total_leave_days,
#             "leaves": leave_data
#         })


#     def post(self, request):
#         data = request.data
#         employee_name = data.get('employee_name')
#         leave_type_id = data.get('leave_type_id')
#         from_date = data.get('from_date')
#         to_date = data.get('to_date')
#         reason = data.get('reason')
#         remarks = data.get('remarks')
#         attachment = request.FILES.get('attachment')

#         if not employee_name:
#             return Response({'error': 'employee_name is required'}, status=400)

#         try:
#             first_name, last_name = employee_name.strip().split(' ', 1)
#         except ValueError:
#             return Response({'error': 'Full employee name (first and last) is required'}, status=400)

#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT u.id
#                 FROM ci_erp_users u
#                 JOIN ci_erp_users_details e ON u.id = e.user_id
#                 WHERE u.first_name = %s AND u.last_name = %s
#             """, [first_name, last_name])
#             row = cursor.fetchone()

#             if not row:
#                 return Response({'error': 'Employee not found for given name'}, status=404)

#             employee_id = row[0]
#             file_name = None

#             if attachment:
#                 allowed_extensions = ['.pdf', '.png', '.gif', '.jpeg', '.jpg']
#                 ext = os.path.splitext(attachment.name)[1].lower()
#                 if ext not in allowed_extensions:
#                     return Response({'error': f'Invalid file type: {ext}'}, status=400)

#                 fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'leave_attachments'))
#                 file_name = fs.save(attachment.name, attachment)

#             if file_name:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_applications 
#                         (employee_id, leave_type_id, from_date, to_date, reason, created_at, remarks, company_id, leave_attachment)
#                     VALUES 
#                         (%s, %s, %s, %s, %s, NOW(), %s, 2, %s)
#                 """, [employee_id, leave_type_id, from_date, to_date, reason, remarks, file_name])
#             else:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_applications 
#                         (employee_id, leave_type_id, from_date, to_date, reason, created_at, remarks, company_id)
#                     VALUES 
#                         (%s, %s, %s, %s, %s, NOW(), %s, 2)
#                 """, [employee_id, leave_type_id, from_date, to_date, reason, remarks])

#         return Response({"message": "Leave application submitted successfully."}, status=201)

#     def patch(self, request, leave_id):
#         status = request.data.get("status")
#         attachment = request.FILES.get('attachment')

#         with connection.cursor() as cursor:
#             if attachment:
#                 allowed_extensions = ['.pdf', '.png', '.gif', '.jpeg', '.jpg']
#                 ext = os.path.splitext(attachment.name)[1].lower()
#                 if ext not in allowed_extensions:
#                     return Response({'error': f'Invalid file type: {ext}'}, status=400)

#                 fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'leave_attachments'))
#                 file_name = fs.save(attachment.name, attachment)

#                 cursor.execute("""
#                     UPDATE ci_leave_applications
#                     SET status = %s, leave_attachment = %s
#                     WHERE leave_id = %s
#                 """, [status, file_name, leave_id])
#             else:
#                 cursor.execute("""
#                     UPDATE ci_leave_applications
#                     SET status = %s
#                     WHERE leave_id = %s
#                 """, [status, leave_id])

#         return Response({"message": "Leave application updated successfully."})

#     def delete(self, request, leave_id):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 DELETE FROM ci_leave_applications
#                 WHERE leave_id = %s
#             """, [leave_id])
#         return Response({"message": "Leave application deleted successfully."})

# class LeaveApplicationAPI(APIView):

#     def get(self, request):
#         with connection.cursor() as cursor:
#             cursor.execute("""    
#                 SELECT 
#                         la.leave_id,
#                         la.company_id,
#                         ud.employee_id,  -- Employee ID from ci_erp_users_details
#                         CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                         u.email AS employee_email,
#                         c.category_name AS leave_type,
#                         la.from_date,
#                         la.to_date,
#                         CASE 
#                             WHEN la.from_date IS NOT NULL AND la.to_date IS NOT NULL 
#                                 AND la.to_date >= la.from_date
#                             THEN DATEDIFF(la.to_date, la.from_date) + 1
#                             ELSE 0
#                         END AS leave_days,
#                         la.reason,
#                         la.remarks,
#                         la.status,
#                         la.created_at
#                     FROM 
#                         ci_leave_applications la
#                     LEFT JOIN 
#                         ci_erp_users_details ud ON la.employee_id = ud.employee_id
#                     LEFT JOIN 
#                         ci_erp_users u ON ud.user_id = u.id
#                     LEFT JOIN 
#                         ci_erp_constants c ON la.leave_type_id = c.constants_id AND c.type = 'leave_type'
#                     ORDER BY 
#                         STR_TO_DATE(la.created_at, '%Y-%m-%d') DESC

#             """)
#             columns = [col[0] for col in cursor.description]
#             leave_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

#             # Sum of leave days only where dates are valid
#             cursor.execute("""
#                 SELECT 
#                     SUM(
#                         CASE 
#                             WHEN from_date IS NOT NULL AND to_date IS NOT NULL 
#                                 AND to_date >= from_date
#                             THEN DATEDIFF(to_date, from_date) + 1
#                             ELSE 0
#                         END
#                     ) AS total_leave_days
#                 FROM ci_leave_applications
#             """)
#             total_days_row = cursor.fetchone()
#             total_leave_days = total_days_row[0] if total_days_row[0] is not None else 0

#         return Response({
#             "leave_count": total_leave_days,
#             "leaves": leave_data
#         })


#     def post(self, request):
#         data = request.data
#         employee_name = data.get('employee_name')
#         leave_type_id = data.get('leave_type_id')
#         from_date = data.get('from_date')
#         to_date = data.get('to_date')
#         reason = data.get('reason')
#         remarks = data.get('remarks')
#         attachment = request.FILES.get('attachment')

#         if not employee_name:
#             return Response({'error': 'employee_name is required'}, status=400)

#         try:
#             first_name, last_name = employee_name.strip().split(' ', 1)
#         except ValueError:
#             return Response({'error': 'Full employee name (first and last) is required'}, status=400)

#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT u.id
#                 FROM ci_erp_users u
#                 JOIN ci_erp_users_details e ON u.id = e.user_id
#                 WHERE u.first_name = %s AND u.last_name = %s
#             """, [first_name, last_name])
#             row = cursor.fetchone()

#             if not row:
#                 return Response({'error': 'Employee not found for given name'}, status=404)

#             employee_id = row[0]
#             file_name = None

#             if attachment:
#                 allowed_extensions = ['.pdf', '.png', '.gif', '.jpeg', '.jpg']
#                 ext = os.path.splitext(attachment.name)[1].lower()
#                 if ext not in allowed_extensions:
#                     return Response({'error': f'Invalid file type: {ext}'}, status=400)

#                 fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'leave_attachments'))
#                 file_name = fs.save(attachment.name, attachment)

#             if file_name:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_applications 
#                         (employee_id, leave_type_id, from_date, to_date, reason, created_at, remarks, company_id, leave_attachment)
#                     VALUES 
#                         (%s, %s, %s, %s, %s, NOW(), %s, 2, %s)
#                 """, [employee_id, leave_type_id, from_date, to_date, reason, remarks, file_name])
#             else:
#                 cursor.execute("""
#                     INSERT INTO ci_leave_applications 
#                         (employee_id, leave_type_id, from_date, to_date, reason, created_at, remarks, company_id)
#                     VALUES 
#                         (%s, %s, %s, %s, %s, NOW(), %s, 2)
#                 """, [employee_id, leave_type_id, from_date, to_date, reason, remarks])

#         return Response({"message": "Leave application submitted successfully."}, status=201)

#     def patch(self, request, leave_id):
#         status = request.data.get("status")
#         attachment = request.FILES.get('attachment')

#         with connection.cursor() as cursor:
#             if attachment:
#                 allowed_extensions = ['.pdf', '.png', '.gif', '.jpeg', '.jpg']
#                 ext = os.path.splitext(attachment.name)[1].lower()
#                 if ext not in allowed_extensions:
#                     return Response({'error': f'Invalid file type: {ext}'}, status=400)

#                 fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'leave_attachments'))
#                 file_name = fs.save(attachment.name, attachment)

#                 cursor.execute("""
#                     UPDATE ci_leave_applications
#                     SET status = %s, leave_attachment = %s
#                     WHERE leave_id = %s
#                 """, [status, file_name, leave_id])
#             else:
#                 cursor.execute("""
#                     UPDATE ci_leave_applications
#                     SET status = %s
#                     WHERE leave_id = %s
#                 """, [status, leave_id])

#         return Response({"message": "Leave application updated successfully."})

#     def delete(self, request, leave_id):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 DELETE FROM ci_leave_applications
#                 WHERE leave_id = %s
#             """, [leave_id])
#         return Response({"message": "Leave application deleted successfully."})


class LeaveApplicationAPI(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                        la.leave_id,
                        la.company_id,
                        ud.employee_id,  -- Employee ID from ci_erp_users_details
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        u.email AS employee_email,
                        c.category_name AS leave_type,
                        la.from_date,
                        la.to_date,
                        CASE 
                            WHEN la.from_date IS NOT NULL AND la.to_date IS NOT NULL 
                                AND la.to_date >= la.from_date
                            THEN DATEDIFF(la.to_date, la.from_date) + 1
                            ELSE 0
                        END AS leave_days,
                        la.reason,
                        la.remarks,
                        la.line_manager_status,
                        la.created_at
                    FROM 
                        ci_leave_applications la
                    LEFT JOIN 
                        ci_erp_users_details ud ON la.employee_id = ud.employee_id
                    LEFT JOIN 
                        ci_erp_users u ON ud.user_id = u.id
                    LEFT JOIN 
                        ci_erp_constants c ON la.leave_type_id = c.constants_id AND c.type = 'leave_type'
                    ORDER BY 
                        STR_TO_DATE(la.created_at, '%Y-%m-%d') DESC

            """)
            columns = [col[0] for col in cursor.description]
            leave_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Sum of leave days only where dates are valid
            cursor.execute("""
                SELECT 
                    SUM(
                        CASE 
                            WHEN from_date IS NOT NULL AND to_date IS NOT NULL 
                                AND to_date >= from_date
                            THEN DATEDIFF(to_date, from_date) + 1
                            ELSE 0
                        END
                    ) AS total_leave_days
                FROM ci_leave_applications
            """)
            total_days_row = cursor.fetchone()
            total_leave_days = total_days_row[0] if total_days_row[0] is not None else 0

        return Response({
            "leave_count": total_leave_days,
            "leaves": leave_data
        })


    def post(self, request):
        data = request.data
        employee_name = data.get('employee_name')
        leave_type_id = data.get('leave_type_id')
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        reason = data.get('reason')
        remarks = data.get('remarks')
        attachment = request.FILES.get('attachment')

        if not employee_name:
            return Response({'error': 'employee_name is required'}, status=400)

        try:
            first_name, last_name = employee_name.strip().split(' ', 1)
        except ValueError:
            return Response({'error': 'Full employee name (first and last) is required'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.id
                FROM ci_erp_users u
                JOIN ci_erp_users_details e ON u.id = e.user_id
                WHERE u.first_name = %s AND u.last_name = %s
            """, [first_name, last_name])
            row = cursor.fetchone()

            if not row:
                return Response({'error': 'Employee not found for given name'}, status=404)

            employee_id = row[0]
            file_name = None

            if attachment:
                allowed_extensions = ['.pdf', '.png', '.gif', '.jpeg', '.jpg']
                ext = os.path.splitext(attachment.name)[1].lower()
                if ext not in allowed_extensions:
                    return Response({'error': f'Invalid file type: {ext}'}, status=400)

                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'leave_attachments'))
                file_name = fs.save(attachment.name, attachment)

            if file_name:
                cursor.execute("""
                    INSERT INTO ci_leave_applications 
                        (employee_id, leave_type_id, from_date, to_date, reason, created_at, remarks, company_id, leave_attachment)
                    VALUES 
                        (%s, %s, %s, %s, %s, NOW(), %s, 2, %s)
                """, [employee_id, leave_type_id, from_date, to_date, reason, remarks, file_name])
            else:
                cursor.execute("""
                    INSERT INTO ci_leave_applications 
                        (employee_id, leave_type_id, from_date, to_date, reason, created_at, remarks, company_id)
                    VALUES 
                        (%s, %s, %s, %s, %s, NOW(), %s, 2)
                """, [employee_id, leave_type_id, from_date, to_date, reason, remarks])

        return Response({"message": "Leave application submitted successfully."}, status=201)

    def patch(self, request, leave_id):
        status = request.data.get("status")
        attachment = request.FILES.get('attachment')

        with connection.cursor() as cursor:
            if attachment:
                allowed_extensions = ['.pdf', '.png', '.gif', '.jpeg', '.jpg']
                ext = os.path.splitext(attachment.name)[1].lower()
                if ext not in allowed_extensions:
                    return Response({'error': f'Invalid file type: {ext}'}, status=400)

                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'leave_attachments'))
                file_name = fs.save(attachment.name, attachment)

                cursor.execute("""
                    UPDATE ci_leave_applications
                    SET status = %s, leave_attachment = %s
                    WHERE leave_id = %s
                """, [status, file_name, leave_id])
            else:
                cursor.execute("""
                    UPDATE ci_leave_applications
                    SET status = %s
                    WHERE leave_id = %s
                """, [status, leave_id])

        return Response({"message": "Leave application updated successfully."})

    def delete(self, request, leave_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM ci_leave_applications
                WHERE leave_id = %s
            """, [leave_id])
        return Response({"message": "Leave application deleted successfully."})
 
 



# # Leave Type Master API


class LeaveTypeListAPI(APIView):

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    constants_id AS value,
                    category_name AS name,
                    field_one AS days_per_year, 
                    field_two AS requires_approval
                FROM ci_erp_constants
                WHERE type = 'leave_type'
            """)
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(result)

 


class TodoAPIView(APIView):
    def get(self, request):
        """Get all todos for the logged-in user"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    todo_item_id, 
                    description, 
                    is_done, 
                    created_at
                FROM 
                    ci_todo_items
                WHERE 
                    user_id = %s
                ORDER BY 
                    created_at DESC
            """, [request.user.id])
            
            columns = [col[0] for col in cursor.description]
            todos = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for todo in todos:
                if todo['created_at']:
                    if isinstance(todo['created_at'], str):
                        try:
                            dt = datetime.strptime(todo['created_at'], '%Y-%m-%d %H:%M:%S')
                            todo['created_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            pass
                    else:
                        todo['created_at'] = todo['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return Response(todos)
    def post(self, request):
        """Create a new todo for the logged-in user"""
        description = request.data.get('description')
        
        if not description:
            return Response(
                {"error": "Description is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_todo_items (
                    company_id,
                    user_id,
                    description,
                    is_done,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s)
            """, [
                2,  # Default company_id
                request.user.id,
                description,
                False,  # Default is_done
                timezone.now()
            ])
            
            # Get the last inserted ID (MySQL specific)
            cursor.execute("SELECT LAST_INSERT_ID()")
            todo_id = cursor.fetchone()[0]
            
            return Response(
                {
                    "message": "Todo created successfully",
                    "todo_item_id": todo_id,
                    "created_at": timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                status=status.HTTP_201_CREATED
            )

    def patch(self, request, todo_id):
        """Update todo fields - flexible update without requiring specific fields"""
        with connection.cursor() as cursor:
            # Verify todo belongs to user
            cursor.execute("""
                SELECT 1 FROM ci_todo_items 
                WHERE todo_item_id = %s AND user_id = %s
            """, [todo_id, request.user.id])
            
            if not cursor.fetchone():
                return Response(
                    {"error": "Todo not found or access denied"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Build dynamic update query based on provided fields
            update_fields = []
            update_values = []
            
            # Check which fields are provided in request
            if 'description' in request.data:
                update_fields.append("description = %s")
                update_values.append(request.data['description'])
            
            if 'is_done' in request.data:
                update_fields.append("is_done = %s")
                update_values.append(request.data['is_done'])
            
            # If no valid fields to update
            if not update_fields:
                return Response(
                    {"error": "No valid fields provided for update"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add todo_id to values for WHERE clause
            update_values.append(todo_id)
            
            # Execute update
            update_query = f"""
                UPDATE ci_todo_items
                SET {', '.join(update_fields)}
                WHERE todo_item_id = %s
            """
            cursor.execute(update_query, update_values)
            
            # Get updated todo
            cursor.execute("""
                SELECT todo_item_id, description, is_done, created_at
                FROM ci_todo_items
                WHERE todo_item_id = %s
            """, [todo_id])
            
            columns = [col[0] for col in cursor.description]
            updated_todo = dict(zip(columns, cursor.fetchone()))
            
            # Format datetime if needed
            if updated_todo.get('created_at') and not isinstance(updated_todo['created_at'], str):
                updated_todo['created_at'] = updated_todo['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return Response(updated_todo)

    def delete(self, request, todo_id):
        """Delete a todo"""
        with connection.cursor() as cursor:
            # Verify todo belongs to user
            cursor.execute("""
                SELECT 1 FROM ci_todo_items 
                WHERE todo_item_id = %s AND user_id = %s
            """, [todo_id, request.user.id])
            
            if not cursor.fetchone():
                return Response(
                    {"error": "Todo not found or access denied"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            cursor.execute("""
                DELETE FROM ci_todo_items
                WHERE todo_item_id = %s
            """, [todo_id])
            
            return Response(
                {"message": "Todo deleted successfully"},
                status=status.HTTP_200_OK
            )

# class EmployeeDashboardView(APIView):
#     def get(self, request):
#         current_month = timezone.now().month
#         response_data = {
#             'birthday_employees': [],
#             'work_anniversary_employees': [],
#             'probation_employees': []  # New section
#         }

#         with connection.cursor() as cursor:
#             # --- Birthday Employees ---
#             cursor.execute("""
#                 SELECT 
#                     CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                     ud.date_of_birth,
#                     d.department_name,
#                     (SELECT designation_name FROM ci_designations WHERE designation_id = ud.designation_id) AS designation
#                 FROM 
#                     ci_erp_users u
#                 JOIN 
#                     ci_erp_users_details ud ON u.id = ud.user_id
#                 LEFT JOIN 
#                     ci_departments d ON ud.department_id = d.department_id
#                 WHERE 
#                     EXTRACT(MONTH FROM ud.date_of_birth) = %s
#                 ORDER BY 
#                     EXTRACT(DAY FROM ud.date_of_birth),
#                     u.last_name, 
#                     u.first_name
#             """, [current_month])

#             columns = [col[0] for col in cursor.description]
#             for row in cursor.fetchall():
#                 emp_data = dict(zip(columns, row))
#                 if isinstance(emp_data['date_of_birth'], str):
#                     try:
#                         emp_data['date_of_birth'] = datetime.strptime(
#                             emp_data['date_of_birth'], '%Y-%m-%d'
#                         ).date().strftime('%d-%m-%Y')
#                     except ValueError:
#                         emp_data['date_of_birth'] = "Unknown"
#                 response_data['birthday_employees'].append(emp_data)

#             # --- Work Anniversary Employees ---
#             cursor.execute("""
#                 SELECT 
#                     CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                     ud.date_of_joining,
#                     d.department_name,
#                     (SELECT designation_name FROM ci_designations WHERE designation_id = ud.designation_id) AS designation
#                 FROM 
#                     ci_erp_users u
#                 JOIN 
#                     ci_erp_users_details ud ON u.id = ud.user_id
#                 LEFT JOIN 
#                     ci_departments d ON ud.department_id = d.department_id
#                 WHERE 
#                     EXTRACT(MONTH FROM ud.date_of_joining) = %s
#                     AND ud.date_of_joining < CURRENT_DATE
#                 ORDER BY 
#                     EXTRACT(DAY FROM ud.date_of_joining),
#                     u.last_name, 
#                     u.first_name
#             """, [current_month])

#             columns = [col[0] for col in cursor.description]
#             for row in cursor.fetchall():
#                 emp_data = dict(zip(columns, row))
#                 if emp_data['date_of_joining']:
#                     try:
#                         if isinstance(emp_data['date_of_joining'], str):
#                             join_date = datetime.strptime(
#                                 emp_data['date_of_joining'], '%Y-%m-%d'
#                             )
#                         else:
#                             join_date = emp_data['date_of_joining']
#                         emp_data['date_of_joining'] = join_date.strftime('%d-%m-%Y')                      
#                     except (ValueError, AttributeError):
#                         emp_data['date_of_joining'] = "Unknown"
#                 response_data['work_anniversary_employees'].append(emp_data)

#             # --- Probation Employees (NEW) ---
#             cursor.execute("""
#                 SELECT 
#                     ud.date_of_joining,
#                     CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                     d.department_name,
#                     'pending' AS status
#                 FROM 
#                     ci_erp_users u
#                 JOIN 
#                     ci_erp_users_details ud ON u.id = ud.user_id
#                 LEFT JOIN 
#                     ci_departments d ON ud.department_id = d.department_id
#                 WHERE 
#                     ud.probation = 'Y'

#             """)
            
#             columns = [col[0] for col in cursor.description]
#             for row in cursor.fetchall():
#                 emp_data = dict(zip(columns, row))
#                 response_data['probation_employees'].append(emp_data)

#         return Response(response_data)

class EmployeeDashboardView(APIView):
    def get(self, request):
        from django.utils import timezone
        current_month = timezone.now().month
        current_day = timezone.now().day
        response_data = {
            'birthday_employees': [],
            'work_anniversary_employees': [],
            'probation_employees': []
        }

        with connection.cursor() as cursor:
            # --- Birthday Employees ---
            cursor.execute('''
                SELECT
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    ud.date_of_birth,
                    d.department_name,
                    (SELECT designation_name FROM ci_designations WHERE designation_id = ud.designation_id) AS designation
                FROM
                    ci_erp_users u
                JOIN
                    ci_erp_users_details ud ON u.id = ud.user_id
                LEFT JOIN
                    ci_departments d ON ud.department_id = d.department_id
                WHERE
                    EXTRACT(MONTH FROM ud.date_of_birth) = %s
                ORDER BY
                    CASE
                        WHEN EXTRACT(DAY FROM ud.date_of_birth) = %s THEN 0
                        WHEN EXTRACT(DAY FROM ud.date_of_birth) > %s THEN 1
                        ELSE 2
                    END,
                    EXTRACT(DAY FROM ud.date_of_birth)
            ''', [current_month, current_day, current_day])

            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                emp_data = dict(zip(columns, row))
                dob = emp_data.get('date_of_birth')
                if dob:
                    try:
                        if isinstance(dob, str):
                            dob_dt = datetime.strptime(dob, '%Y-%m-%d')
                        else:
                            dob_dt = dob
                        emp_data['date_of_birth'] = dob_dt.strftime('%d-%m-%Y')
                    except Exception:
                        emp_data['date_of_birth'] = "Unknown"
                else:
                    emp_data['date_of_birth'] = "Unknown"
                response_data['birthday_employees'].append(emp_data)

            # --- Work Anniversary Employees ---
            cursor.execute('''
                SELECT
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    ud.date_of_joining,
                    d.department_name,
                    (SELECT designation_name FROM ci_designations WHERE designation_id = ud.designation_id) AS designation
                FROM
                    ci_erp_users u
                JOIN
                    ci_erp_users_details ud ON u.id = ud.user_id
                LEFT JOIN
                    ci_departments d ON ud.department_id = d.department_id
                WHERE
                    EXTRACT(MONTH FROM ud.date_of_joining) = %s
                    AND ud.date_of_joining < CURRENT_DATE
                ORDER BY
                    CASE
                        WHEN EXTRACT(DAY FROM ud.date_of_joining) = %s THEN 0
                        WHEN EXTRACT(DAY FROM ud.date_of_joining) > %s THEN 1
                        ELSE 2
                    END,
                    EXTRACT(DAY FROM ud.date_of_joining),
                    u.last_name,
                    u.first_name
            ''', [current_month, current_day, current_day])

            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                emp_data = dict(zip(columns, row))
                doj = emp_data.get('date_of_joining')
                if doj:
                    try:
                        if isinstance(doj, str):
                            doj_dt = datetime.strptime(doj, '%Y-%m-%d')
                        else:
                            doj_dt = doj
                        emp_data['date_of_joining'] = doj_dt.strftime('%d-%m-%Y')
                    except Exception:
                        emp_data['date_of_joining'] = "Unknown"
                else:
                    emp_data['date_of_joining'] = "Unknown"
                response_data['work_anniversary_employees'].append(emp_data)

            # --- Probation Employees (NEW) ---
            cursor.execute('''
                SELECT
                    ud.date_of_joining,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    d.department_name,
                    'pending' AS status
                FROM
                    ci_erp_users u
                JOIN
                    ci_erp_users_details ud ON u.id = ud.user_id
                LEFT JOIN
                    ci_departments d ON ud.department_id = d.department_id
                WHERE
                    ud.probation = 'Y'
                ORDER BY
                    u.created_at DESC
            ''')
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                emp_data = dict(zip(columns, row))
                doj = emp_data.get('date_of_joining')
                if doj:
                    try:
                        if isinstance(doj, str):
                            doj_dt = datetime.strptime(doj, '%Y-%m-%d')
                        else:
                            doj_dt = doj
                        emp_data['date_of_joining'] = doj_dt.strftime('%d-%m-%Y')
                    except Exception:
                        emp_data['date_of_joining'] = "Unknown"
                else:
                    emp_data['date_of_joining'] = "Unknown"
                response_data['probation_employees'].append(emp_data)

        return Response(response_data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class EmployeeRoleDropdownAPI(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        u.id,
                        ud.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                        r.role_id,
                        r.role_name
                     FROM (ci_erp_users u
                    JOIN ci_erp_users_details ud ON u.id = ud.user_id)
                    LEFT JOIN ci_staff_roles r ON u.user_role_id = r.role_id
                    WHERE u.is_active = 1
                """)
                rows = cursor.fetchall()

            result = [
                {
                    "id": row[0],
                    "employee_id": row[1],
                    "employee_name": row[2],
                    "role_id": row[3],
                    "role_name": row[4]
                }
                for row in rows
            ]

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# class EmployeeAssetsView(APIView):

#     def get(self, request, employee_id):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT 
#                     a.id,
#                     a.assets_category_id,
#                     cat.category_name AS assets_category_name,
#                     a.brand_id,
#                     b.category_name AS assets_brand_name,
#                     a.company_id,
#                     a.employee_id,
#                     CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
#                     a.company_asset_code,
#                     a.assets_name,
#                     a.purchase_date,
#                     a.invoice_number,
#                     a.manufacturer,
#                     a.serial_number,
#                     a.warranty_end_date,
#                     a.asset_note,
#                     a.asset_image,
#                     a.is_working,
#                     a.created_at,
#                     a.returned,
#                     a.employee_confirmation,
#                     a.return_request_status
#                 FROM 
#                     ci_assets a
#                 LEFT JOIN 
#                     ci_erp_constants cat ON a.assets_category_id = cat.constants_id
#                 LEFT JOIN 
#                     ci_erp_constants b ON a.brand_id = b.constants_id AND b.type = 'assets_brand'
#                 LEFT JOIN 
#                     ci_erp_users_details ud ON a.employee_id = ud.employee_id
#                 LEFT JOIN 
#                     ci_erp_users u ON ud.user_id = u.id
#                 WHERE 
#                     a.employee_id = %s 
#                 ORDER BY 
#                     a.created_at DESC
#             """, [employee_id])
#             rows = cursor.fetchall()

#         columns = [
#             "id", "assets_category_id", "category_name", "brand_id", "brand_name",
#             "company_id", "employee_id", "employee_name", "company_asset_code", "assets_name",
#             "purchase_date", "invoice_number", "manufacturer", "serial_number",
#             "warranty_end_date", "asset_note", "asset_image", "is_working",
#             "created_at", "returned", "employee_confirmation", "return_request_status"
#         ]

#         data = []
#         for row in rows:
#             item = dict(zip(columns, row))
#             item["is_working"] = "Yes" if item["is_working"] in (1, '1', True) else "No"
#             data.append(item)

#         return Response(data)

#     def patch(self, request, pk):
#         action = request.data.get("action", "").strip().lower()

#         if action == "received":
#             try:
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE ci_assets
#                         SET employee_confirmation = 'accepted'
#                         WHERE id = %s
#                     """, [pk])
#                 return Response({"message": "Asset marked as received."}, status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         elif action == "not_received":
#             return Response({"message": "Asset not received. Status remains pending."}, status=status.HTTP_200_OK)

#         elif action == "return":
#             try:
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE ci_assets
#                         SET return_request_status = '1'
#                         WHERE id = %s
#                     """, [pk])
#                 return Response({"message": "Return request submitted. Awaiting admin approval."}, status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#         else:
#             return Response({"error": "Invalid action. Use 'received', 'not_received', or 'return'."}, status=status.HTTP_400_BAD_REQUEST)



class EmployeeAssetsView(APIView):
 
    # def get(self, request, employee_id):
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT
    #                 a.id,
    #                 a.assets_category_id,
    #                 cat.category_name AS assets_category_name,
    #                 a.brand_id,
    #                 b.category_name AS assets_brand_name,
    #                 a.company_id,
    #                 a.employee_id,
    #                 CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    #                 a.company_asset_code,
    #                 a.assets_name,
    #                 a.purchase_date,
    #                 a.invoice_number,
    #                 a.manufacturer,
    #                 a.serial_number,
    #                 a.warranty_end_date,
    #                 a.asset_note,
    #                 a.asset_image,
    #                 a.is_working,
    #                 a.created_at,
    #                 a.returned,
    #                 a.employee_confirmation,
    #                 a.return_request_status,
    #                 a.quantity
    #             FROM
    #                 ci_assets a
    #             LEFT JOIN
    #                 ci_erp_constants cat ON a.assets_category_id = cat.constants_id
    #             LEFT JOIN
    #                 ci_erp_constants b ON a.brand_id = b.constants_id AND b.type = 'assets_brand'
    #             LEFT JOIN
    #                 ci_erp_users_details ud ON a.employee_id = ud.employee_id
    #             LEFT JOIN
    #                 ci_erp_users u ON ud.user_id = u.id
    #             WHERE
    #                 a.employee_id = %s
    #             ORDER BY
    #                 a.created_at DESC
    #         """, [employee_id])
    #         rows = cursor.fetchall()
 
    #     columns = [
    #         "id", "assets_category_id", "category_name", "brand_id", "brand_name",
    #         "company_id", "employee_id", "employee_name", "company_asset_code", "assets_name",
    #         "purchase_date", "invoice_number", "manufacturer", "serial_number",
    #         "warranty_end_date", "asset_note", "asset_image", "is_working",
    #         "created_at", "returned", "employee_confirmation", "return_request_status","quantity"
    #     ]
 
    #     data = []
    #     for row in rows:
    #         item = dict(zip(columns, row))
    #         item["is_working"] = "Yes" if item["is_working"] in (1, '1', True) else "No"
    #         data.append(item)
 
    #     return Response(data)
 
 
 
    def get(self, request, employee_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.id,
                    a.assets_category_id,
                    cat.category_name AS assets_category_name,
                    a.brand_id,
                    b.category_name AS assets_brand_name,
                    a.company_id,
                    a.employee_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    a.company_asset_code,
                    a.assets_name,
                    a.purchase_date,
                    a.invoice_number,
                    a.manufacturer,
                    a.serial_number,
                    a.warranty_end_date,
                    a.asset_note,
                    a.asset_image,
                    a.is_working,
                    a.created_at,
                    a.returned,
                    a.employee_confirmation,
                    a.return_request_status ,
                    a.return_date
                FROM
                    ci_assets a
                LEFT JOIN
                    ci_erp_constants cat ON a.assets_category_id = cat.constants_id
                LEFT JOIN
                    ci_erp_constants b ON a.brand_id = b.constants_id AND b.type = 'assets_brand'
                LEFT JOIN
                    ci_erp_users_details ud ON a.employee_id = ud.employee_id
                LEFT JOIN
                    ci_erp_users u ON ud.user_id = u.id
                WHERE
                    a.employee_id = %s
                ORDER BY
                    a.created_at DESC
            """, [employee_id])
            rows = cursor.fetchall()
 
        columns = [
            "id", "assets_category_id", "category_name", "brand_id", "brand_name",
            "company_id", "employee_id", "employee_name", "company_asset_code", "assets_name",
            "purchase_date", "invoice_number", "manufacturer", "serial_number",
            "warranty_end_date", "asset_note", "asset_image", "is_working",
            "created_at", "returned", "employee_confirmation", "return_request_status","return_date"
        ]

        data = []
        for row in rows:
            item = dict(zip(columns, row))
 
            # ✅ Convert working status to readable text
            item["is_working"] = "Yes" if item["is_working"] in (1, '1', True) else "No"
 
            # ✅ Safely attach full image URL
            if item.get("asset_image"):
                encoded_path = quote(item["asset_image"])  # encode DB filename
                item["asset_image"] = f"https://tdtlworld.com/hrms-backend/media/assets_pictures/{encoded_path}"
            else:
                item["asset_image"] = None
 
            data.append(item)
 
        return Response(data)
 
    # def patch(self, request, pk):
    #     action = request.data.get("action", "").strip().lower()
 
    #     if action == "received":
    #         try:
    #             with connection.cursor() as cursor:
    #                 cursor.execute("""
    #                     UPDATE ci_assets
    #                     SET employee_confirmation = 'accepted'
    #                     WHERE id = %s
    #                 """, [pk])
                   
    #             return Response({"message": "Asset marked as received."}, status=status.HTTP_200_OK)
    #         except Exception as e:
    #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   
   
    def patch(self, request, pk):
        action = request.data.get("action", "").strip().lower()
   
        if action == "received":
            try:
                with connection.cursor() as cursor:
                    # ✅ Get brand_id for this asset
                    cursor.execute("""
                        SELECT brand_id , quantity
                        FROM ci_assets
                        WHERE id = %s
                    """, [pk])
                    row = cursor.fetchone()
                    if not row:
                        return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)
   
                    # brand_id = row[0]  # fetched brand_id
                    brand_id, quantity = row
   
                    # ✅ Update employee confirmation
                    cursor.execute("""
                        UPDATE ci_assets
                        SET employee_confirmation = 'accepted'
                        WHERE id = %s
                    """, [pk])
   
                    # ✅ Update stock in ci_erp_constants using brand_id
                    # cursor.execute("""
                    #     UPDATE ci_erp_constants
                    #     SET field_one = COALESCE(field_one, 0) - %s
                    #     WHERE constants_id = %s
                    # """, [quantity, brand_id])
   
                return Response({"message": "Asset marked as received."}, status=status.HTTP_200_OK)
   
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
        elif action == "not_received":
            return Response({"message": "Asset not received. Status remains pending."}, status=status.HTTP_200_OK)
 
        elif action == "return":
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE ci_assets
                        SET return_request_status = '1'
                        WHERE id = %s
                    """, [pk])
                return Response({"message": "Return request submitted. Awaiting admin approval."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
 
        else:
            return Response({"error": "Invalid action. Use 'received', 'not_received', or 'return'."}, status=status.HTTP_400_BAD_REQUEST)
 
 
 
 


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from datetime import datetime

class EmployeePolicyView(APIView):

    def get(self, request, employee_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.policy_id,
                    p.title AS policy_name,
                    p.description,
                    p.attachment,
                    pa.acknowledge,
                    pa.created_date AS acknowledge_date
                FROM ci_policies_acknowledge pa
                JOIN ci_policies p ON pa.policy_id = p.policy_id
                WHERE pa.emp_id = %s
                ORDER BY pa.created_date DESC
            """, [employee_id])

            rows = cursor.fetchall()

        columns = [
            "policy_id", "policy_name", "description", "attachment",
            "acknowledge", "acknowledge_date"
        ]

        data = []
        acknowledged_count = 0
        for row in rows:
            item = dict(zip(columns, row))
            item["acknowledge"] = "Acknowledged" if item["acknowledge"] == 'Y' else "Not Acknowledged"
            if item["acknowledge"] == "Acknowledged":
                acknowledged_count += 1

            # Format date
            if isinstance(item["acknowledge_date"], datetime):
                suffix = lambda d: 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')
                item["acknowledge_date"] = item["acknowledge_date"].strftime(
                    f"%-d{suffix(item['acknowledge_date'].day)} %B %Y %I:%M %p"
                ).lower()
            else:
                item["acknowledge_date"] = "Not yet acknowledged"

            data.append(item)

        # Alert if not all acknowledged
        total = len(data)
        alert = None
        if acknowledged_count < total:
            alert = "Alert! You Need to Accept All Policy to Avail your Attendance and Payroll"

        return Response({
            "message": "Employee assigned policy list",
            "total_policies": total,
            "acknowledged_count": acknowledged_count,
            "data": data,
            "alert": alert
        }, status=status.HTTP_200_OK)

    def patch(self, request, employee_id):
        policy_id = request.data.get("policy_id")

        if not policy_id:
            return Response({"error": "policy_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_policies_acknowledge
                    SET acknowledge = 'Y', created_date = NOW()
                    WHERE emp_id = %s AND policy_id = %s
                """, [employee_id, policy_id])

            return Response({"message": "Policy acknowledged successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





####  ADMIN POLICY Allocation

from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
class PolicyAllocationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        employee_ids = data.get("employee_ids", [])

        if not employee_ids:
            return Response({"error": "Employee IDs are required."}, status=400)

        with connection.cursor() as cursor:
            # Handle 'ALL'
            if employee_ids == ["ALL"]:
                cursor.execute("SELECT username FROM ci_erp_users")
                employee_ids = [row[0] for row in cursor.fetchall()]

            # Fetch all policy IDs
            cursor.execute("SELECT policy_id FROM ci_policies")
            policies = cursor.fetchall()
            policy_ids = [str(row[0]) for row in policies]
            policy_ids_str = ",".join(policy_ids)
            now = datetime.now()

            already_allocated = []

            for emp_id in employee_ids:
                # Check if already allocated
                cursor.execute("""
                    SELECT 1
                    FROM ci_policy_allocations
                    WHERE emp_id = %s
                """, [emp_id])
                if cursor.fetchone():
                    already_allocated.append(emp_id)
                    continue

                # Insert new allocation
                cursor.execute("""
                    INSERT INTO ci_policy_allocations (emp_id, policy_id, allocation_date)
                    VALUES (%s, %s, %s)
                """, [emp_id, policy_ids_str, now])

                # Fetch employee details from ci_erp_users
                cursor.execute("""
                    SELECT first_name, last_name, email
                    FROM ci_erp_users
                    WHERE username = %s
                """, [emp_id])
                emp_row = cursor.fetchone()

                if emp_row:
                    first_name, last_name, email = emp_row
                    if email:
                        subject = "New Policy Allocation"
                        html_content = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; color: #333;">
                            <h2>New Policy Allocation</h2>
                            <p>Dear <b>{first_name} {last_name}</b>,</p>
                            <p>Policies have been allocated to you. Please review and acknowledge them at the earliest.</p>
                            <p style="color: #3794ff; font-weight: bold;">
                                You Need to Accept All Policy to Avail your Punch in / out, leave request, attendance, and payroll.
                            </p>
                            <p>Please log in to your employee portal to review and acknowledge these policies.</p>
                            <p>Best regards,</p>
                            <div style="margin: 10px 0;">
                                <img src="cid:company_logo" alt="Vetrina Logo" style="width:150px; height:auto;">
                            </div>
                            <p style="color: #3794ff; font-weight: bold;">Vetrina Healthcare Pvt. Ltd.</p>
                            <div style="margin-top:20px; font-size:12px; color:#b380ff; text-align:center;">
                                © 2025 Vetrina Healthcare Pvt. Ltd. All rights reserved.
                            </div>
                        </body>
                        </html>
                        """
                        msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [email])
                        msg.attach_alternative(html_content, "text/html")

                        # Attach logo inline
                        logo_path = os.path.join(settings.MEDIA_ROOT, "logo", "vetrina_logo.png")
                        if os.path.exists(logo_path):
                            with open(logo_path, 'rb') as f:
                                logo_data = f.read()
                            image = MIMEImage(logo_data)
                            image.add_header('Content-ID', '<company_logo>')
                            image.add_header('Content-Disposition', 'inline', filename="vetrina_logo.png")
                            msg.attach(image)

                        msg.send(fail_silently=False)

        if already_allocated:
            return Response({
                "message": f"Policies already allocated for: {', '.join(already_allocated)}"
            }, status=400)

        return Response({"message": "All policies allocated to selected employees successfully and emails sent."}, status=201)

 
    # def get(self, request):
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT 
    #                 pa.policy_allocation_id,
    #                 ud.employee_id AS emp_id,
    #                 CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
    #                 p.policy_id,
    #                 p.title AS policy_name,
    #                 COALESCE(ack.acknowledge, 'N') AS acknowledgement_status,
    #                 pa.allocation_date
    #             FROM ci_policy_allocations pa
    #             JOIN ci_erp_users_details ud ON pa.emp_id = ud.employee_id
    #             JOIN ci_erp_users u ON u.id = ud.user_id
    #             LEFT JOIN ci_policies p ON FIND_IN_SET(p.policy_id, pa.policy_id) > 0
    #             LEFT JOIN ci_policies_acknowledge ack
    #                 ON ack.policy_id = p.policy_id
    #             AND ack.emp_id COLLATE utf8mb4_unicode_ci = pa.emp_id COLLATE utf8mb4_unicode_ci
    #             WHERE u.is_active = 1
    #             ORDER BY pa.policy_allocation_id DESC
    #         """)
    #         rows = cursor.fetchall()

    #     result_dict = {}

    #     for row in rows:
    #         allocation_id = row[0]
    #         if allocation_id not in result_dict:
    #             result_dict[allocation_id] = {
    #                 "policy_allocation_id": allocation_id,
    #                 "emp_id": row[1],
    #                 "employee_name": row[2],
    #                 "policy_ids": [],
    #                 "policy_names": [],
    #                 "policy_acknowledgement_status": [],
    #                 "allocation_date": row[6]
    #             }

    #         result_dict[allocation_id]["policy_ids"].append(str(row[3]))
    #         result_dict[allocation_id]["policy_names"].append(row[4])
    #         result_dict[allocation_id]["policy_acknowledgement_status"].append(row[5])

    #     result = []
    #     for data in result_dict.values():
            
    #         data["policy_ids"].reverse()
    #         data["policy_names"].reverse()
    #         data["policy_acknowledgement_status"].reverse()
    #         result.append({
    #             "policy_allocation_id": data["policy_allocation_id"],
    #             "emp_id": data["emp_id"],
    #             "employee_name": data["employee_name"],
    #             "policy_id": ",".join(data["policy_ids"]),
    #             "policy_name": ",".join(data["policy_names"]),
    #             "policy_acknowledgement_status": ",".join(data["policy_acknowledgement_status"]),
    #             "allocation_date": data["allocation_date"]
    #         })
            
    #     response_data = {
    #     "total_entries": len(result),
    #     "data": result
    # }


    #     return Response(response_data, status=200)
    
    
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pa.policy_allocation_id,
                    ud.employee_id AS emp_id,
                    CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                    p.policy_id,
                    p.title AS policy_name,
                    COALESCE(ack.acknowledge, 'N') AS acknowledgement_status,
                    pa.allocation_date
                FROM ci_policy_allocations pa
                LEFT JOIN ci_erp_users_details ud ON pa.emp_id = ud.employee_id
                LEFT JOIN ci_erp_users u ON u.id = ud.user_id
                LEFT JOIN ci_policies p ON FIND_IN_SET(p.policy_id, pa.policy_id) > 0
                LEFT JOIN ci_policies_acknowledge ack
                    ON ack.policy_id = p.policy_id
                    AND ack.emp_id COLLATE utf8mb4_unicode_ci = pa.emp_id COLLATE utf8mb4_unicode_ci
                WHERE u.is_active = 1
                ORDER BY pa.policy_allocation_id DESC
            """)
            rows = cursor.fetchall()
            
            total_query_entries = len(rows)

        result_dict = {}
        for row in rows:
            allocation_id = row[0]
            if allocation_id not in result_dict:
                result_dict[allocation_id] = {
                    "policy_allocation_id": allocation_id,
                    "emp_id": row[1],
                    "employee_name": row[2],
                    "policy_ids": [],
                    "policy_names": [],
                    "policy_acknowledgement_status": [],
                    "allocation_date": row[6]
                }

            # Append each policy info (handle None values)
            result_dict[allocation_id]["policy_ids"].append(str(row[3] or ""))
            result_dict[allocation_id]["policy_names"].append(row[4] or "")
            result_dict[allocation_id]["policy_acknowledgement_status"].append(row[5] or "N")

        result = []
        for data in result_dict.values():
            # Reverse lists as before
            data["policy_ids"].reverse()
            data["policy_names"].reverse()
            data["policy_acknowledgement_status"].reverse()
            result.append({
                "policy_allocation_id": data["policy_allocation_id"],
                "emp_id": data["emp_id"],
                "employee_name": data["employee_name"],
                "policy_id": ",".join(data["policy_ids"]),
                "policy_name": ",".join(data["policy_names"]),
                "policy_acknowledgement_status": ",".join(data["policy_acknowledgement_status"]),
                "allocation_date": data["allocation_date"]
            })

        # Include total entries
        response_data = {
            "total_query_entries": total_query_entries,
            "total_entries": len(result),
            "data": result
        }

        return Response(response_data, status=200)

    def patch(self, request, policy_allocation_id):
        data = request.data
        emp_id = data.get("employee_id")
        policies_to_add_names = data.get("policies_to_add", [])
        policies_to_remove_names = data.get("policies_to_remove", [])

        if not emp_id:
            return Response({"error": "Employee ID is required."}, status=400)

        if not policies_to_add_names and not policies_to_remove_names:
            return Response({"error": "At least one of policies_to_add or policies_to_remove must be provided."}, status=400)

        with connection.cursor() as cursor:
            # Fetch current policies
            cursor.execute("""
                SELECT policy_id FROM ci_policy_allocations
                WHERE policy_allocation_id = %s AND emp_id = %s
            """, [policy_allocation_id, emp_id])
            row = cursor.fetchone()

            if not row:
                return Response({"error": "Policy allocation not found for the given employee."}, status=404)

            current_policies = set(row[0].split(","))

            # Fetch policy_id for given policy names to add
            add_set = set()
            if policies_to_add_names:
                cursor.execute("""
                    SELECT policy_id FROM ci_policies
                    WHERE title IN %s
                """, [tuple(policies_to_add_names)])
                add_rows = cursor.fetchall()
                add_set = set(str(r[0]) for r in add_rows)

            # Fetch policy_id for given policy names to remove
            remove_set = set()
            if policies_to_remove_names:
                cursor.execute("""
                    SELECT policy_id FROM ci_policies
                    WHERE title IN %s
                """, [tuple(policies_to_remove_names)])
                remove_rows = cursor.fetchall()
                remove_set = set(str(r[0]) for r in remove_rows)

            # ✅ Check if any of the remove_set are acknowledged
            if remove_set:
                cursor.execute("""
                    SELECT policy_id FROM ci_policies_acknowledge
                    WHERE emp_id = %s AND acknowledge = 'Y' AND policy_id IN %s
                """, [emp_id, tuple(remove_set)])
                acknowledged_rows = cursor.fetchall()
                acknowledged_set = set(str(r[0]) for r in acknowledged_rows)

                if acknowledged_set:
                    return Response({
                        "error": f"Cannot remove acknowledged policies: {', '.join(acknowledged_set)}"
                    }, status=400)

            # Perform update
            updated_policies = (current_policies | add_set) - remove_set

            if not updated_policies:
                return Response({"error": "At least one policy must remain assigned."}, status=400)

            updated_policy_str = ",".join(sorted(updated_policies))

            cursor.execute("""
                UPDATE ci_policy_allocations
                SET policy_id = %s, allocation_date = CURDATE()
                WHERE policy_allocation_id = %s AND emp_id = %s
            """, [updated_policy_str, policy_allocation_id, emp_id,])

        return Response({"message": "Policy allocation updated successfully."}, status=200)

    
    def delete(self, request, policy_allocation_id):
        with connection.cursor() as cursor:
            # Confirm the allocation exists
            cursor.execute("""
                SELECT 1 FROM ci_policy_allocations
                WHERE policy_allocation_id = %s
            """, [policy_allocation_id])
            if not cursor.fetchone():
                return Response({"error": "Policy allocation not found."}, status=404)

            # Delete the allocation row
            cursor.execute("""
                DELETE FROM ci_policy_allocations
                WHERE policy_allocation_id = %s
            """, [policy_allocation_id])

        return Response({"message": "Policy allocation deleted successfully."}, status=200)



## Employee Policy Section

class EmployeePolicyAcknowledgeView(APIView):
    def get(self, request, emp_id):
        with connection.cursor() as cursor:
            # Get assigned policy IDs
            cursor.execute("""
                SELECT policy_id 
                FROM ci_policy_allocations 
                WHERE emp_id = %s
            """, [emp_id])
            row = cursor.fetchone()

            if not row or not row[0]:
                return Response({"message": "No policies assigned to this employee."}, status=200)

            policy_ids = row[0].split(',')

            # Get acknowledged policy_ids (cast to string for comparison)
            cursor.execute("""
                SELECT policy_id 
                FROM ci_policies_acknowledge 
                WHERE emp_id = %s AND acknowledge = 'Y'
            """, [emp_id])
            ack_rows = cursor.fetchall()
            acknowledged_ids = set(str(row[0]) for row in ack_rows)  # Cast to str to match policy_ids from split

            result = []

            for pid in policy_ids:
                pid = pid.strip()  # Clean any whitespace
                cursor.execute("""
                    SELECT policy_id, title, attachment
                    FROM ci_policies
                    WHERE policy_id = %s
                """, [pid])
                policy = cursor.fetchone()
                if policy:
                    # result.append({
                    #     "policy_id": policy[0],
                    #     "policy_name": policy[1],
                    #     "attachment_text": f"https://tdtlworld.com/hrms-backend/media/{policy[2]}" if policy[2] else None,
                    #     "acknowledged": str(policy[0]) in acknowledged_ids
                    # })

                    attachment = None
                    if policy[2]:
                        attachment = policy[2]
                        # If somehow full URL is stored in DB, strip the base
                        if attachment.startswith("http"):
                            attachment = attachment.replace("https://tdtlworld.com/hrms-backend/media/", "")

                    result.append({
                        "policy_id": policy[0],
                        "policy_name": policy[1],
                        "attachment_text": attachment,
                        "acknowledged": str(policy[0]) in acknowledged_ids
                    })

            all_acknowledged = all(p["acknowledged"] for p in result)
            alert = None
            if not all_acknowledged:
                alert = "Alert! You Need to Accept All Policy to Avail your Attendance and Payroll"

            return Response({
                "alert": alert,
                "policies": result
            }, status=200)

    def post(self, request, emp_id):
        policy_id = request.data.get("policy_id")
        if not policy_id:
            return Response({"error": "policy_id is required."}, status=400)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with connection.cursor() as cursor:
            # Get user_id from emp_id
            cursor.execute("""
                SELECT user_id FROM ci_erp_users_details WHERE employee_id = %s
            """, [emp_id])
            user_row = cursor.fetchone()
            if not user_row:
                return Response({"error": "Employee not found."}, status=404)

            user_id = user_row[0]

            # Check if already acknowledged
            cursor.execute("""
                SELECT 1 FROM ci_policies_acknowledge
                WHERE emp_id = %s AND policy_id = %s
            """, [emp_id, policy_id])
            if cursor.fetchone():
                return Response({"message": "Policy already acknowledged."}, status=200)

            # Insert acknowledgment
            cursor.execute("""
                INSERT INTO ci_policies_acknowledge (policy_id, userid, emp_id, acknowledge, is_policy_view, created_date)
                VALUES (%s, %s, %s, 'Y', 'Y', %s)
            """, [policy_id, user_id, emp_id, now])

        return Response({"message": "Policy acknowledged successfully."}, status=201)




from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from datetime import datetime

# class AdminMyAccountView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]

#     ACCOUNT_SETTINGS_MAP = {
#         "Default Language": "default_language",
#         "Date Format": "date_format_xi",
#         "Default Currency": "default_currency",
#         "Timezone": "system_timezone",
#         "Invoice Terms & Condition": "invoice_terms_condition"
#     }

#     COMPANY_INFO_MAP = {
#         "Company Name": "company_name",
#         "Company Type": "company_type",
#         "Trading Name": "company_trading_name",
#         "Tax Number/EIN": "tax_number/ein",
#         "Registration Number": "registration_number"
#     }

#     def get(self, request, pk):
#         user = request.user
#         # Validate employee ID matches the authenticated admin user
#         if user.user_type.lower() != 'admin' or user.username != pk:
#             return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)
        


#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT 
#                         first_name, last_name, email, contact_number,
#                         username, gender, country, address_1, address_2,
#                         state, city, zipcode, profile_photo
#                     FROM ci_erp_users
#                     WHERE username = %s AND user_type = 'admin' AND is_active = 1
#                     LIMIT 1
#                 """, [pk])
#                 user_row = cursor.fetchone()
#                 if not user_row:
#                     return Response({"message": "Admin not found."}, status=status.HTTP_404_NOT_FOUND)

#                 cursor.execute("""
#                     SELECT 
#                         default_language, date_format_xi, default_currency,
#                         system_timezone, invoice_terms_condition
#                     FROM ci_erp_company_settings
#                     WHERE company_id = %s
#                     LIMIT 1
#                 """, [user.company_id])
#                 settings_row = cursor.fetchone()

#                 cursor.execute("""
#                     SELECT type, category_name
#                     FROM ci_erp_constants
#                     WHERE company_id = %s AND type IN %s
#                 """, [user.company_id, tuple(self.COMPANY_INFO_MAP.values())])
#                 company_rows = cursor.fetchall()
#                 company_info = {field: None for field in self.COMPANY_INFO_MAP.values()}
#                 for row in company_rows:
#                     company_info[row[0]] = row[1]

#                 response_data = {
#                     "my_account": {
#                         "full_name": f"{user_row[0]} {user_row[1]}",
#                         "email": user_row[2],
#                         "contact_number": user_row[3]
#                     },
#                     "personal_info": {
#                         "first_name": user_row[0],
#                         "last_name": user_row[1],
#                         "username": user_row[4],
#                         "contact_number": user_row[3],
#                         "email": user_row[2],
#                         "gender": user_row[5],
#                         "country": user_row[6],
#                         "address": user_row[7],
#                         "address_line_2": user_row[8],
#                         "state": user_row[9],
#                         "city": user_row[10],
#                         "zip_code": user_row[11]
#                     },
#                     "account_settings": dict(zip(self.ACCOUNT_SETTINGS_MAP.keys(), settings_row)) if settings_row else None,
#                     "profile_picture": {
#                         "url": settings.MEDIA_URL + user_row[12] if user_row[12] else None
#                     },
#                     "company_information": {
#                         "Company Name": company_info["company_name"],
#                         "Company Type": company_info["company_type"],
#                         "Trading Name": company_info["company_trading_name"],
#                         "Tax Number/EIN": company_info["tax_number/ein"],
#                         "Registration Number": company_info["registration_number"]
#                     }
#                 }

#                 return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def patch(self, request, pk):
#         user = request.user
#         data = request.data

#         # Ensure the authenticated admin is only updating their own profile
#         if user.user_type.lower() != 'admin' or user.username != pk:
#             return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

#         file = request.FILES.get("profile_picture")

#         try:
#             # Profile fields
#             user_update_fields = {
#                 "first_name": data.get("first_name"),
#                 "last_name": data.get("last_name"),
#                 "username": data.get("username"),
#                 "email": data.get("email"),
#                 "contact_number": data.get("contact_number"),
#                 "gender": data.get("gender"),
#                 "country": data.get("country"),
#                 "address_1": data.get("address"),
#                 "address_2": data.get("address_line_2"),
#                 "state": data.get("state"),
#                 "city": data.get("city"),
#                 "zipcode": data.get("zip_code"),
#             }

#             # Allowed file extensions
#             ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']

#             if file:
#                 # Get file extension
#                 file_ext = os.path.splitext(file.name)[1].lower()
                
#                 # Validate file extension
#                 if file_ext not in ALLOWED_EXTENSIONS:
#                     raise ValidationError("Only JPG and PNG formats are acceptable for profile pictures.")
                
#                 # Process the file if extension is valid
#                 filename = f"profile_{user.id}_{file.name}"
#                 folder = os.path.join(settings.MEDIA_ROOT, 'profile_pictures')
#                 os.makedirs(folder, exist_ok=True)
#                 filepath = os.path.join(folder, filename)
                
#                 with open(filepath, 'wb+') as destination:
#                     for chunk in file.chunks():
#                         destination.write(chunk)
                
#                 user_update_fields["profile_photo"] = f"profile_pictures/{filename}"

#             # Apply user field updates
#             user_set_clause = ", ".join([f"{field} = %s" for field in user_update_fields if user_update_fields[field] is not None])
#             user_values = [v for v in user_update_fields.values() if v is not None]

#             if user_set_clause:
#                 with connection.cursor() as cursor:
#                     cursor.execute(f"""
#                         UPDATE ci_erp_users
#                         SET {user_set_clause}
#                         WHERE id = %s AND user_type = 'admin'
#                     """, user_values + [user.id])

#             # Account settings update
#             settings_update_fields = {}
#             for display_key, db_field in self.ACCOUNT_SETTINGS_MAP.items():
#                 value = data.get(display_key)
#                 if value is not None:
#                     settings_update_fields[db_field] = value

#             if settings_update_fields:
#                 settings_set_clause = ", ".join([f"{field} = %s" for field in settings_update_fields])
#                 settings_values = list(settings_update_fields.values())

#                 with connection.cursor() as cursor:
#                     cursor.execute(f"""
#                         UPDATE ci_erp_company_settings
#                         SET {settings_set_clause}
#                         WHERE company_id = %s
#                     """, settings_values + [user.company_id])

#             # Company constants update
#             with connection.cursor() as cursor:
#                 for frontend_key, db_type in self.COMPANY_INFO_MAP.items():
#                     value = data.get(frontend_key)
#                     if value is not None:
#                         cursor.execute("""
#                             SELECT constants_id FROM ci_erp_constants
#                             WHERE company_id = %s AND type = %s
#                         """, [user.company_id, db_type])
#                         row = cursor.fetchone()

#                         if row:
#                             cursor.execute("""
#                                 UPDATE ci_erp_constants
#                                 SET category_name = %s
#                                 WHERE constants_id = %s
#                             """, [value, row[0]])
#                         else:
#                             cursor.execute("""
#                                 INSERT INTO ci_erp_constants (company_id, type, category_name, created_at)
#                                 VALUES (%s, %s, %s, %s)
#                             """, [user.company_id, db_type, value, datetime.now()])

#             # Password update (bcrypt)
#             current_password = data.get("current_password")
#             new_password = data.get("new_password")
#             confirm_password = data.get("confirm_password")

#             if any([current_password, new_password, confirm_password]):
#                 if not all([current_password, new_password, confirm_password]):
#                     return Response({"error": "All password fields are required."}, status=status.HTTP_400_BAD_REQUEST)

#                 if new_password != confirm_password:
#                     return Response({"error": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

#                 with connection.cursor() as cursor:
#                     cursor.execute("SELECT password FROM ci_erp_users WHERE id = %s AND user_type = 'admin'", [user.id])
#                     row = cursor.fetchone()
#                     if not row:
#                         return Response({"error": "Admin not found."}, status=status.HTTP_404_NOT_FOUND)

#                     stored_hash = row[0]
#                     if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash.encode('utf-8')):
#                         return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

#                     hashed_new = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
#                     cursor.execute("""
#                         UPDATE ci_erp_users
#                         SET password = %s
#                         WHERE id = %s AND user_type = 'admin'
#                     """, [hashed_new.decode('utf-8'), user.id])

#             return Response({"message": "Account information updated successfully."}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminMyAccountView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    ACCOUNT_SETTINGS_MAP = {
        "Default Language": "default_language",
        "Date Format": "date_format_xi",
        "Default Currency": "default_currency",
        "Timezone": "system_timezone",
        "Invoice Terms & Condition": "invoice_terms_condition"
    }

    COMPANY_INFO_MAP = {
        "Company Name": "company_name",
        "Company Type": "company_type",
        "Trading Name": "company_trading_name",
        "Tax Number/EIN": "tax_number/ein",
        "Registration Number": "registration_number"
    }

    def get(self, request, pk):
        user = request.user
        # Validate employee ID matches the authenticated admin user
        if str(user.user_type).lower() not in ['admin', '7'] or user.username != pk:
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)
        


        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        first_name, last_name, email, contact_number,
                        username, gender, country, address_1, address_2,
                        state, city, zipcode, profile_photo
                    FROM ci_erp_users
                    WHERE username = %s AND user_type IN ('admin','7') AND is_active = 1
                    LIMIT 1
                """, [pk])
                user_row = cursor.fetchone()
                if not user_row:
                    return Response({"message": "Admin not found."}, status=status.HTTP_404_NOT_FOUND)

                cursor.execute("""
                    SELECT 
                        default_language, date_format_xi, default_currency,
                        system_timezone, invoice_terms_condition
                    FROM ci_erp_company_settings
                    WHERE company_id = %s
                    LIMIT 1
                """, [user.company_id])
                settings_row = cursor.fetchone()

                cursor.execute("""
                    SELECT type, category_name
                    FROM ci_erp_constants
                    WHERE company_id = %s AND type IN %s
                """, [user.company_id, tuple(self.COMPANY_INFO_MAP.values())])
                company_rows = cursor.fetchall()
                company_info = {field: None for field in self.COMPANY_INFO_MAP.values()}
                for row in company_rows:
                    company_info[row[0]] = row[1]

                response_data = {
                    "my_account": {
                        "full_name": f"{user_row[0]} {user_row[1]}",
                        "email": user_row[2],
                        "contact_number": user_row[3]
                    },
                    "personal_info": {
                        "first_name": user_row[0],
                        "last_name": user_row[1],
                        "username": user_row[4],
                        "contact_number": user_row[3],
                        "email": user_row[2],
                        "gender": user_row[5],
                        "country": user_row[6],
                        "address": user_row[7],
                        "address_line_2": user_row[8],
                        "state": user_row[9],
                        "city": user_row[10],
                        "zip_code": user_row[11]
                    },
                    "account_settings": dict(zip(self.ACCOUNT_SETTINGS_MAP.keys(), settings_row)) if settings_row else None,
                    "profile_picture": {
                        "url": settings.MEDIA_URL + user_row[12] if user_row[12] else None
                    },
                    "company_information": {
                        "Company Name": company_info["company_name"],
                        "Company Type": company_info["company_type"],
                        "Trading Name": company_info["company_trading_name"],
                        "Tax Number/EIN": company_info["tax_number/ein"],
                        "Registration Number": company_info["registration_number"]
                    }
                }

                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        user = request.user
        data = request.data

        # Ensure the authenticated admin is only updating their own profile
        if str(user.user_type).lower() not in ['admin', '7'] or user.username != pk:
            return Response({"error": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get("profile_picture")

        try:
            # Profile fields
            user_update_fields = {
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "username": data.get("username"),
                "email": data.get("email"),
                "contact_number": data.get("contact_number"),
                "gender": data.get("gender"),
                "country": data.get("country"),
                "address_1": data.get("address"),
                "address_2": data.get("address_line_2"),
                "state": data.get("state"),
                "city": data.get("city"),
                "zipcode": data.get("zip_code"),
            }

            # Allowed file extensions
            ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png']

            if file:
                # Get file extension
                file_ext = os.path.splitext(file.name)[1].lower()
                
                # Validate file extension
                if file_ext not in ALLOWED_EXTENSIONS:
                    raise ValidationError("Only JPG and PNG formats are acceptable for profile pictures.")
                
                # Process the file if extension is valid
                filename = f"profile_{user.id}_{file.name}"
                folder = os.path.join(settings.MEDIA_ROOT, 'profile_pictures')
                os.makedirs(folder, exist_ok=True)
                filepath = os.path.join(folder, filename)
                
                with open(filepath, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                user_update_fields["profile_photo"] = f"profile_pictures/{filename}"

            # Apply user field updates
            user_set_clause = ", ".join([f"{field} = %s" for field in user_update_fields if user_update_fields[field] is not None])
            user_values = [v for v in user_update_fields.values() if v is not None]

            if user_set_clause:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        UPDATE ci_erp_users
                        SET {user_set_clause}
                        WHERE id = %s AND user_type IN ('admin','7')
                    """, user_values + [user.id])

            # Account settings update
            settings_update_fields = {}
            for display_key, db_field in self.ACCOUNT_SETTINGS_MAP.items():
                value = data.get(display_key)
                if value is not None:
                    settings_update_fields[db_field] = value

            if settings_update_fields:
                settings_set_clause = ", ".join([f"{field} = %s" for field in settings_update_fields])
                settings_values = list(settings_update_fields.values())

                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        UPDATE ci_erp_company_settings
                        SET {settings_set_clause}
                        WHERE company_id = %s
                    """, settings_values + [user.company_id])

            # Company constants update
            with connection.cursor() as cursor:
                for frontend_key, db_type in self.COMPANY_INFO_MAP.items():
                    value = data.get(frontend_key)
                    if value is not None:
                        cursor.execute("""
                            SELECT constants_id FROM ci_erp_constants
                            WHERE company_id = %s AND type = %s
                        """, [user.company_id, db_type])
                        row = cursor.fetchone()

                        if row:
                            cursor.execute("""
                                UPDATE ci_erp_constants
                                SET category_name = %s
                                WHERE constants_id = %s
                            """, [value, row[0]])
                        else:
                            cursor.execute("""
                                INSERT INTO ci_erp_constants (company_id, type, category_name, created_at)
                                VALUES (%s, %s, %s, %s)
                            """, [user.company_id, db_type, value, datetime.now()])

            # Password update (bcrypt)
            current_password = data.get("current_password")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")

            if any([current_password, new_password, confirm_password]):
                if not all([current_password, new_password, confirm_password]):
                    return Response({"error": "All password fields are required."}, status=status.HTTP_400_BAD_REQUEST)

                if new_password != confirm_password:
                    return Response({"error": "New passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

                with connection.cursor() as cursor:
                    cursor.execute("SELECT password FROM ci_erp_users WHERE id = %s AND user_type IN ('admin','7')", [user.id])
                    row = cursor.fetchone()
                    if not row:
                        return Response({"error": "Admin not found."}, status=status.HTTP_404_NOT_FOUND)

                    stored_hash = row[0]
                    if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash.encode('utf-8')):
                        return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

                    hashed_new = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    cursor.execute("""
                        UPDATE ci_erp_users
                        SET password = %s
                        WHERE id = %s AND user_type IN ('admin','7')
                    """, [hashed_new.decode('utf-8'), user.id])

            return Response({"message": "Account information updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#### employee section dashbaord

####my attendance

from datetime import date

class MyAttendanceAPIView(APIView):
    def get(self, request, empid):
        try:
            with connection.cursor() as cursor:
                # Get user_id of the requested empid
                cursor.execute("""
                    SELECT user_id FROM ci_erp_users_details
                    WHERE employee_id = %s
                    LIMIT 1
                """, [empid])
                user_row = cursor.fetchone()

                if not user_row:
                    return Response({'error': 'Employee not found'}, status=404)

                user_id = user_row[0]

                # Get all employees under this manager or self
                cursor.execute("""
                    SELECT ced.employee_id, ceu.first_name, ceu.last_name, ceu.email
                    FROM ci_erp_users_details ced
                    JOIN ci_erp_users ceu ON ceu.id = ced.user_id
                    WHERE ced.manager = %s OR ced.employee_id = %s
                """, [user_id, empid])
                employees = cursor.fetchall()

                if not employees:
                    return Response({'message': 'No subordinates found'}, status=200)

                emp_data_map = {}
                emp_ids = []

                for employee_id, first_name, last_name, email in employees:
                    full_name = f"{first_name} {last_name}".strip()
                    emp_data_map[employee_id] = {
                        'employee_name': full_name,
                        'email': email
                    }
                    emp_ids.append(employee_id)

                today_str = date.today().strftime('%Y-%m-%d')

                cursor.execute("""
                    SELECT emp_id, attendance_date, attendance_status, clock_in,
                           clock_out, late_mark, early_mark, is_half_day
                    FROM ci_biomatric_data
                    WHERE emp_id IN %s
                    AND attendance_date = %s
                """, [tuple(emp_ids), today_str])
                records = cursor.fetchall()

                results = []
                for row in records:
                    emp_id, attendance_date, status, clock_in, clock_out, late_mark, early_mark, is_half_day = row

                    total_work = "00:00:00"
                    if clock_in and clock_out:
                        try:
                            fmt = "%H:%M:%S" if len(clock_in) > 5 else "%H:%M"
                            in_time = datetime.strptime(clock_in, fmt)
                            out_time = datetime.strptime(clock_out, fmt)
                            diff = out_time - in_time
                            total_seconds = int(diff.total_seconds())
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            total_work = f"{hours:02}:{minutes:02}:{seconds:02}"
                        except Exception:
                            total_work = "00:00:00"

                    emp_info = emp_data_map.get(emp_id, {})
                    results.append({
                        'employee_name': emp_info.get('employee_name', ''),
                        'email': emp_info.get('email', ''),
                        'attendance_date': attendance_date,
                        'status': status,
                        'clock_in': clock_in or '00:00:00',
                        'clock_out': clock_out or '00:00:00',
                        'late_mark': late_mark or 'N',
                        'early_mark': early_mark or 'N',
                        'total_work': total_work,
                        'is_half_day': is_half_day
                    })

                results.sort(key=lambda x: x['email'] != emp_data_map[empid]['email'])

                return Response({'attendance': results}, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=500)


###employee dropdown--- manager wise employee
class EmpNameDropdownAPIView(APIView): 
    def get(self, request, empid):
        try:
            with connection.cursor() as cursor:
                # Step 1: Get user_id of the given empid
                cursor.execute("""
                    SELECT user_id FROM ci_erp_users_details
                    WHERE employee_id = %s
                    LIMIT 1
                """, [empid])
                user_row = cursor.fetchone()
                if not user_row:
                    return Response({'error': 'Employee not found'}, status=404)

                user_id = user_row[0]

                # Step 2: Get manager's own name and employee_id
                cursor.execute("""
                    SELECT ceu.first_name, ceu.last_name, ced.employee_id
                    FROM ci_erp_users ceu
                    JOIN ci_erp_users_details ced ON ced.user_id = ceu.id
                    WHERE ceu.id = %s
                    LIMIT 1
                """, [user_id])
                manager_row = cursor.fetchone()

                result = []
                if manager_row:
                    first_name, last_name, manager_empid = manager_row
                    manager_name = f"{first_name} {last_name}".strip()
                    result.append({
                        "name": manager_name,
                        "employee_id": manager_empid
                    })

                # Step 3: Get subordinates' names and employee_ids
                cursor.execute("""
                    SELECT ceu.first_name, ceu.last_name, ced.employee_id
                    FROM ci_erp_users_details ced
                    JOIN ci_erp_users ceu ON ceu.id = ced.user_id
                    WHERE ced.manager = %s
                """, [user_id])
                subordinates = cursor.fetchall()

                for first_name, last_name, sub_empid in subordinates:
                    full_name = f"{first_name} {last_name}".strip()
                    result.append({
                        "name": full_name,
                        "employee_id": sub_empid
                    })

                return Response(result, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=500)



####monthly report manager wise employee and each employee

class MonthlyReportView(APIView):
    def post(self, request):
        try:
            employee_id = request.data.get('employee_id')
            month_str = request.data.get('month')  # Format: YYYY-MM

            if not employee_id or not month_str:
                return Response({'error': 'employee_id and month are required'}, status=400)
            
            if month_str:
                year, month = map(int, month_str.split('-'))
            else:
                now = datetime.now()
                year = now.year
                month = now.month

            # try:
            #     month_date = datetime.strptime(month, '%Y-%m')
            # except ValueError:
            #     return Response({'error': 'Invalid month format. Use YYYY-MM'}, status=400)

            # today = datetime.today()
            # is_current_month = today.year == month_date.year and today.month == month_date.month
            # day_limit = today.day if is_current_month else 31

            # start_date = f"{month}-01"
            # end_date = f"{month}-{day_limit:02d}"

            # with connection.cursor() as cursor:
        #         cursor.execute("""
        #             SELECT attendance_date, clock_in, clock_out, total_work, attendance_status
        #             FROM ci_biomatric_data
        #             WHERE emp_id = %s
        #             AND attendance_date BETWEEN %s AND %s
        #             ORDER BY attendance_date ASC
        #         """, [employee_id, start_date, end_date])

        #         rows = cursor.fetchall()

        #     result = []
        #     for row in rows:
        #         attendance_date, clock_in, clock_out, total_work, attendance_status = row

        #         # Convert string to datetime.date if necessary
        #         if isinstance(attendance_date, str):
        #             attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()

        #         day_name = attendance_date.strftime('%A')
        #         date_str = attendance_date.strftime('%Y-%m-%d')

        #         # Format clock in/out if available
        #         def fmt_time(val):
        #             try:
        #                 return datetime.strptime(val, '%H:%M:%S').strftime('%I:%M %p').lstrip("0").lower() if val else ""
        #             except Exception:
        #                 return val  # return as-is if not in expected format

        #         result.append({
        #             "day": day_name,
        #             "date": date_str,
        #             "status": attendance_status or "Absent",
        #             "clock_in": fmt_time(clock_in),
        #             "clock_out": fmt_time(clock_out),
        #             "total_work": total_work or ""
        #         })

        #     return Response(result, status=200)

        # except Exception as e:
        #     return Response({'error': str(e)}, status=500)

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
                        DATE_FORMAT(MAX(TIME(clock_out)), '%%H:%%i') AS clock_out,
                        TIMEDIFF(
                            MAX(TIME(clock_out)),
                            MIN(TIME(clock_in))
                        ) AS total_work
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


# Notification

class GlobalNotificationAPIView(APIView):
    def dictfetchall(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def get(self, request, employee_id):
        today = datetime.today()
        today_str = today.strftime('%Y-%m-%d')
        yesterday_str = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        today_md = today.strftime('%m-%d')

        with connection.cursor() as cursor:
            # 1. Birthdays
            cursor.execute("""
                SELECT 
                    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                    ud.date_of_birth,
                    d.department_name
                FROM ci_erp_users u
                JOIN ci_erp_users_details ud ON u.id = ud.user_id
                LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                WHERE DATE_FORMAT(ud.date_of_birth, '%%m-%%d') = %s
                AND u.is_active = 1
            """, [today_md])
            birthdays = self.dictfetchall(cursor)

            # 2. Work Anniversaries
            cursor.execute("""
                SELECT 
                    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                    ud.date_of_joining,
                    TIMESTAMPDIFF(YEAR, ud.date_of_joining, CURDATE()) AS years_completed
                FROM ci_erp_users u
                JOIN ci_erp_users_details ud ON u.id = ud.user_id
                WHERE DATE_FORMAT(ud.date_of_joining, '%%m-%%d') = %s
                AND YEAR(ud.date_of_joining) < YEAR(CURRENT_DATE())
                AND u.is_active = 1
            """, [today_md])
            anniversaries = self.dictfetchall(cursor)

            # 3. New Joinees
            cursor.execute("""
                SELECT 
                    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                    d.department_name,
                    ud.role_description,
                    ud.date_of_joining
                FROM ci_erp_users u
                JOIN ci_erp_users_details ud ON u.id = ud.user_id
                LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                WHERE ud.date_of_joining = %s
                AND u.is_active = 1
            """, [today_str])
            new_joins = self.dictfetchall(cursor)

            # 4. Get department_id of the requesting employee
            cursor.execute("""
                SELECT department_id 
                FROM ci_erp_users_details 
                WHERE employee_id = %s
            """, [employee_id])
            dept_result = cursor.fetchone()
            department_id = dept_result[0] if dept_result else None

            # 5. Announcements for today, yesterday and future only
            announcements = []
            if department_id:
                cursor.execute("""
                    SELECT 
                        title,
                        summary,
                        description,
                        start_date,
                        end_date
                    FROM ci_announcements
                    WHERE department_id = %s
                    AND DATE(start_date) >= %s
                    AND is_active = 1
                """, [str(department_id), yesterday_str])
                announcements = self.dictfetchall(cursor)
            
            # 6 Event assigned for the employee today
            cursor.execute("""
                SELECT event_title,
                           event_time,
                           event_note,
                           event_date,
                           event_color
                    FROM ci_events
                    WHERE employee_id=%s
                    AND event_date=%s
                """,[employee_id, today_str])
            events=self.dictfetchall(cursor)

            # 7. Awards allocated today (for all employees)
            cursor.execute("""
                SELECT 
                    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                    a.award_type_id,
                    a.gift_item,
                    a.cash_price,
                    a.award_information,
                    a.description,
                    a.created_at
                FROM ci_awards a
                LEFT JOIN ci_erp_users u ON a.employee_id = u.username
                WHERE DATE(a.created_at) = %s
            """, [today_str])
            awards = self.dictfetchall(cursor)

            
            # 8. ✅ Policy Allocation Notification (with count)
            cursor.execute("""
                SELECT policy_id 
                FROM ci_policy_allocations
                WHERE emp_id = %s AND DATE(allocation_date) = %s
                """, [employee_id, today_str])
                
            rows = cursor.fetchall()
            policy_message = ""
            policy_count = 0

            if rows:
                for row in rows:
                    if row[0]:  # policy_id column
                        policy_ids = [p.strip() for p in row[0].split(",") if p.strip()]
                        policy_count += len(policy_ids)
 
            if policy_count > 0:
                    # policy_message = f"{policy_count} new polic{'y' if policy_count == 1 else 'ies'} have been allocated to you. Please review them."
                    policy_message = "New policies have been allocated to you. Please review them."

            
            # 9. ✅ Asset Assignment Notification 
            cursor.execute("""
                SELECT 1 FROM ci_assets
                WHERE employee_id = %s 
                AND DATE(STR_TO_DATE(created_at, '%%Y-%%m-%%d %%H:%%i:%%s')) = %s
            """, [employee_id, today_str])
            asset_row = cursor.fetchone()

            asset_message = ""
            if asset_row:
                asset_message = "New asset has been assigned to you. Please confirm that you have received the asset."



        # Final response
        return Response({
            "birthdays": birthdays,
            "work_anniversaries": anniversaries,
            "new_joinees": new_joins,
            "announcements": announcements,
            "events":events,
            "awards":awards,
            # "policy_notification": policy_message,
            # "asset_notification": asset_message,
        }, status=status.HTTP_200_OK)
######## Employee Project section

class EmployeeAssignedProjects(APIView):

    def get(self, request, employee_id):
        try:
            result = []

            # Fetch all projects where this employee is assigned (in assigned_to)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        p.project_id, p.title, c.full_name AS client_name, p.start_date, p.end_date,
                        p.assigned_to, p.priority, p.project_progress
                    FROM ci_projects p
                    LEFT JOIN ci_clients c ON p.client_id = c.id
                    WHERE FIND_IN_SET(%s, p.assigned_to)
                """, [employee_id])

                projects = cursor.fetchall()

            for proj in projects:
                project_id = proj[0]

                # Resolve assigned_to names (team)
                assigned_to_ids = proj[5].split(",") if proj[5] else []
                assigned_to_names = []
                for emp_id in assigned_to_ids:
                    with connection.cursor() as emp_cursor:
                        emp_cursor.execute("""
                            SELECT first_name, last_name FROM ci_erp_users
                            WHERE username = %s
                        """, [emp_id.strip()])
                        emp = emp_cursor.fetchone()
                        if emp:
                            assigned_to_names.append(f"{emp[0]} {emp[1]}")

                # Fetch discussions for this project
                with connection.cursor() as disc_cursor:
                    disc_cursor.execute("""
                        SELECT employee_id, discussion_text, created_at
                        FROM ci_projects_discussion
                        WHERE project_id = %s
                    """, [project_id])
                    discussions = disc_cursor.fetchall()
                    discussion_list = []
                    for disc in discussions:
                        with connection.cursor() as emp_cursor:
                            emp_cursor.execute("""
                                SELECT first_name, last_name FROM ci_erp_users
                                WHERE username = %s
                            """, [disc[0]])
                            emp = emp_cursor.fetchone()
                            emp_name = f"{emp[0]} {emp[1]}" if emp else disc[0]
                        discussion_list.append({
                            "employee_name": emp_name,
                            "discussion_text": disc[1],
                            "created_at": disc[2],
                        })

                # Fetch attached files for this project
                with connection.cursor() as file_cursor:
                    file_cursor.execute("""
                        SELECT employee_id, file_title, attachment_file, created_at
                        FROM ci_projects_files
                        WHERE project_id = %s
                    """, [project_id])
                    files = file_cursor.fetchall()
                    file_list = []
                    for file in files:
                        with connection.cursor() as emp_cursor:
                            emp_cursor.execute("""
                                SELECT first_name, last_name FROM ci_erp_users
                                WHERE username = %s
                            """, [file[0]])
                            uploader = emp_cursor.fetchone()
                            uploader_name = f"{uploader[0]} {uploader[1]}" if uploader else file[0]
                        file_list.append({
                            "uploaded_by": uploader_name,
                            "file_title": file[1],
                            "attachment_file": file[2],
                            "created_at": file[3],
                        })

                # Append project details with team, discussions, attachments
                result.append({
                    "project_id": proj[0],
                    "title": proj[1],
                    "client_name": proj[2],
                    "start_date": proj[3],
                    "end_date": proj[4],
                    "team": ", ".join(assigned_to_names),
                    "priority": proj[6],
                    "progress": proj[7],
                    "discussions": discussion_list,
                    "attachments": file_list
                })

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddProjectDiscussion(APIView):

    def post(self, request, project_id):
        try:
            employee_id = request.data.get('employee_id')
            discussion_text = request.data.get('discussion_text')

            if not all([employee_id, discussion_text]):
                return Response({"error": "employee_id and discussion_text are required."},
                                status=status.HTTP_400_BAD_REQUEST)

            with connection.cursor() as cursor:
                # Fetch company_id for the given project_id
                cursor.execute("""
                    SELECT company_id FROM ci_projects WHERE project_id = %s
                """, [project_id])
                row = cursor.fetchone()

                if not row:
                    return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

                company_id = row[0]

                # Insert discussion record
                cursor.execute("""
                    INSERT INTO ci_projects_discussion 
                    (company_id, project_id, employee_id, discussion_text, created_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, [company_id, project_id, employee_id, discussion_text])

            return Response({"message": "Discussion added successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.parsers import MultiPartParser, FormParser

class ProjectAttachmentAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, project_id):
        employee_id = request.data.get('employee_id')
        file_title = request.data.get('file_title')
        file_obj = request.FILES.get('file')

        if not employee_id or not file_title or not file_obj:
            return Response({"error": "employee_id, file_title, and file are required."}, status=400)

        # Save File
        fs = FileSystemStorage(location='media/project_attachments/')
        filename = fs.save(file_obj.name, file_obj)
        file_path = os.path.join('media/project_attachments/', filename)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_projects_files (company_id, project_id, employee_id, file_title, attachment_file, created_at)
                VALUES (
                    (SELECT company_id FROM ci_projects WHERE project_id = %s),
                    %s, %s, %s, %s, %s
                )
            """, [project_id, project_id, employee_id, file_title, file_path, timezone.now()])

        return Response({"message": "File uploaded successfully.", "file_path": file_path}, status=201)



from datetime import datetime
datetime.now()
import calendar

class EmpDashApi(APIView):
    def get(self, request, employee_id):
        current_year = now().year
        current_month = now().month
        today = date.today()
        day_name = calendar.day_name[now().weekday()].lower()

        # 1. Support tickets
        ticket_query = """
            SELECT id, subject, priority, ticket_status
            FROM ci_support_tickets_employee
            WHERE employee_id = %s AND YEAR(created_at) = %s
            ORDER BY created_at DESC
        """
        with connection.cursor() as cursor:
            cursor.execute(ticket_query, [employee_id, current_year])
            ticket_rows = cursor.fetchall()
            ticket_columns = [col[0] for col in cursor.description]

        tickets = []
        for row in ticket_rows:
            record = dict(zip(ticket_columns, row))
            record["ticket_status"] = "Open" if record["ticket_status"] == 0 else "Closed"
            tickets.append(record)

        # 2. Late mark count (current month)
        late_mark_query = """
            SELECT COUNT(*) 
            FROM ci_biomatric_data
            WHERE emp_id = %s 
              AND late_mark = 'Y'
              AND MONTH(login_date) = %s
              AND YEAR(login_date) = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(late_mark_query, [employee_id, current_month, current_year])
            late_mark_count = cursor.fetchone()[0]

        # 3. Leave days taken (current year)
        # leave_query = """
        #     SELECT SUM(CAST(no_of_days AS DECIMAL(5,2))) 
        #     FROM ci_leave_applications
        #     WHERE employee_id = %s
        #       AND YEAR(from_date) = %s and line_manager_status = 1;
        # """
        
        leave_query = """
            SELECT SUM(
           CASE 
               WHEN is_half_day = 1 THEN 0.5
               ELSE CAST(no_of_days AS DECIMAL(5,2))
           END
               ) AS total_leave_days
            FROM ci_leave_applications
            WHERE employee_id = %s
              AND YEAR(from_date) = %s
              AND line_manager_status = 1;

        """
        with connection.cursor() as cursor:
            cursor.execute(leave_query, [employee_id, current_year])
            leave_days = cursor.fetchone()[0] or 0

        # 4. Award count
        award_query = """
            SELECT COUNT(*) 
            FROM ci_awards
            WHERE employee_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(award_query, [employee_id])
            award_count = cursor.fetchone()[0]

        # 5. Asset count (not returned)
        asset_query = """
            SELECT COUNT(*)
            FROM ci_assets
            WHERE employee_id = %s
              AND return_request_status != '2'
              AND employee_confirmation = 'accepted'
        """
        with connection.cursor() as cursor:
            cursor.execute(asset_query, [employee_id])
            asset_count = cursor.fetchone()[0]

        # fetch office_shift_id
        with connection.cursor() as c:
            c.execute("""
                select office_shift_id from vetrina_hrms.ci_erp_users_details where employee_id=%s
            """, [employee_id])
            result = c.fetchone()
            office_shift_id = result[0] if result else 0

        # 6. Office shift
        office_shift_query = f"""
            SELECT shift_name, {day_name}_in_time, {day_name}_out_time
            FROM ci_office_shifts
            WHERE office_shift_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(office_shift_query, [office_shift_id])
            result = cursor.fetchone()
            if result:
                office_shift = {
                    "shift_name": result[0],
                    "in_time": result[1],
                    "out_time": result[2]
                }
            else:
                office_shift = {
                    "shift_name": None,
                    "in_time": None,
                    "out_time": None
                }

        # 7. latest_in_out (ci_biomatric_data_2)
        latest_in_out_query = """
            SELECT clock_in, clock_out
            FROM ci_biomatric_data_2
            WHERE emp_id = %s AND login_date = %s
            ORDER BY id DESC
            LIMIT 1
        """
        with connection.cursor() as cursor:
            cursor.execute(latest_in_out_query, [employee_id, today])
            result = cursor.fetchone()
            latest_in_out = {
                "clock_in": result[0] if result else None,
                "clock_out": result[1] if result else None
            }

        # 8. todays_attendance (ci_biomatric_data)
        todays_attendance_query = """
            SELECT clock_in, clock_out
            FROM ci_biomatric_data
            WHERE emp_id = %s AND attendance_date = %s
            LIMIT 1
        """
        with connection.cursor() as cursor:
            cursor.execute(todays_attendance_query, [employee_id, today])
            result = cursor.fetchone()
            todays_attendance = {
                "clock_in": result[0] if result else None,
                "clock_out": result[1] if result else None
            }

        # 9. monthly_report (ci_biomatric_data)
        monthly_report_query = """
            SELECT attendance_date, clock_in, clock_out
            FROM ci_biomatric_data
            WHERE emp_id = %s
              AND MONTH(attendance_date) = %s
              AND YEAR(attendance_date) = %s
            ORDER BY attendance_date ASC
        """
        with connection.cursor() as cursor:
            cursor.execute(monthly_report_query, [employee_id, current_month, current_year])
            rows = cursor.fetchall()
            monthly_report = [
                {"date": row[0], "clock_in": row[1], "clock_out": row[2]}
                for row in rows
            ]

        return Response({
            "support_tickets": {
                "count": len(tickets),
                "data": tickets
            },
            "late_mark_count": late_mark_count,
            "leave_days_taken": float(leave_days),
            "award_count": award_count,
            "asset_count": asset_count,
            "office_shift": office_shift,
            "latest_in_out": latest_in_out,
            "todays_attendance": todays_attendance,
            "monthly_report": monthly_report
        }) 


class EmpConfirmationAPI(APIView):
    def get(self, request, employee_id):
        query="""SELECT employee_id , probation, confirmation_date
                FROM ci_erp_users_details
                WHERE employee_id=%s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [employee_id])
            result = cursor.fetchone()

        if result:
            employee_id, probation, confirmation_date = result
            return Response({
                "employee_id": employee_id,
                "employee_confirm": probation,
                "confirmation_date": confirmation_date
            })
        return Response({"error": "Employee not found"}, status=404)
 


class PolicyAcknowledgementStatusView(APIView):
    def get(self, request, emp_id):
        try:
            with connection.cursor() as cursor:
                # 1. Get allocated policy count
                cursor.execute("""
                    SELECT
                        CASE 
                            WHEN policy_id IS NULL OR TRIM(policy_id) = '' THEN 0
                            ELSE 
                                (
                                    LENGTH(
                                        REPLACE(
                                            TRIM(BOTH ',' FROM REPLACE(REPLACE(REPLACE(policy_id, ',,', ','), ',,', ','), ',,', ',')),
                                            ',',
                                            ''
                                        )
                                    ) = 0
                                ) + 
                                (
                                    LENGTH(TRIM(BOTH ',' FROM REPLACE(REPLACE(REPLACE(policy_id, ',,', ','), ',,', ','), ',,', ','))) 
                                    - LENGTH(REPLACE(TRIM(BOTH ',' FROM REPLACE(REPLACE(REPLACE(policy_id, ',,', ','), ',,', ','), ',,', ',')), ',', ''))
                                    + 1
                                )
                        END AS policy_count
                    FROM ci_policy_allocations
                    WHERE emp_id = %s;
                """, [emp_id])

                alloc_row = cursor.fetchone()
                allocated_count = alloc_row[0] if alloc_row and alloc_row[0] is not None else 0

                # 2. Get acknowledged policy count
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM ci_policies_acknowledge
                    WHERE emp_id = %s AND acknowledge = 'Y';
                """, [emp_id])
                ack_row = cursor.fetchone()
                acknowledged_count = ack_row[0] if ack_row else 0

            # 3. Determine overall status
            status_value = "Y" if acknowledged_count >= allocated_count and allocated_count > 0 else "N"

            return Response({
                "emp_id": emp_id,
                "allocated_policies": allocated_count,
                "acknowledged_policies": acknowledged_count,
                "status": status_value
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from collections import defaultdict
class DepartmentLeaveReportView(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                # Get all leave types for the company
                cursor.execute("""
                    SELECT constants_id, category_name
                    FROM ci_erp_constants
                    WHERE type = 'leave_type'
                """)
                leave_types = cursor.fetchall()
                leave_type_map = {lt[0]: lt[1].lower().replace(" ", "_") for lt in leave_types}

                # Get active employees per department
                cursor.execute("""
                    SELECT 
                        d.department_id,
                        d.department_name,
                        COUNT(u.id) AS total_employees
                    FROM ci_departments d
                    LEFT JOIN ci_erp_users_details ud 
                        ON d.department_id = ud.department_id
                    LEFT JOIN ci_erp_users u 
                        ON ud.user_id = u.id AND u.is_active = 1
                    GROUP BY d.department_id, d.department_name
                """)
                dept_employee_counts = {row[0]: {"department_name": row[1], "total_employees": row[2]} for row in cursor.fetchall()}

                # Get today's leave counts for active employees
                cursor.execute("""
                    SELECT 
                        d.department_id,
                        la.leave_type_id,
                        COUNT(DISTINCT u.id) AS leave_count
                    FROM ci_leave_applications la
                    INNER JOIN ci_erp_users_details ud 
                        ON la.employee_id = ud.employee_id
                    INNER JOIN ci_erp_users u 
                        ON ud.user_id = u.id AND u.is_active = 1
                    INNER JOIN ci_departments d 
                        ON ud.department_id = d.department_id
                    WHERE la.from_date <= CURDATE()
                      AND la.to_date >= CURDATE()
        
                    GROUP BY d.department_id, la.leave_type_id
                """)
                leave_data = defaultdict(lambda: defaultdict(int))
                employees_on_leave = defaultdict(set)

                for row in cursor.fetchall():
                    dept_id = row[0]
                    leave_type_id = row[1]
                    count = row[2]
                    leave_name = leave_type_map.get(leave_type_id, f"leave_type_{leave_type_id}")
                    leave_data[dept_id][leave_name] = count
                    employees_on_leave[dept_id].add(leave_type_id)

                # Build response
                final_data = []
                for dept_id, info in dept_employee_counts.items():
                    breakdown = {name: leave_data[dept_id].get(name, 0) for name in leave_type_map.values()}
                    final_data.append({
                        "department_name": info["department_name"],
                        "total_employees": info["total_employees"],
                        "employees_on_leave": sum(breakdown.values()),
                        "leave_breakdown": breakdown
                    })

            return Response({"data": final_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection

def dictfetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))
 
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
 
# class EmployeeDetailsAPIView(APIView):
#     def get(self, request, user_id):
#         try:
#             with connection.cursor() as cursor:
#                 # ==================== EMPLOYEE DETAILS ====================
#                 cursor.execute("""
#                     SELECT
#                         u.id as user_id,
#                         d.employee_id,
#                         CONCAT(u.first_name, ' ', COALESCE(u.middle_name,''), ' ', u.last_name) as full_name,
#                         u.profile_photo,
                       
#                         dept.department_name as department,
#                         desg.designation_name as designation,
#                         divi.division_name as division,
                       
#                         u.contact_number,
#                         u.email,
#                         d.date_of_birth,
#                         u.gender,
#                         CASE
#                             WHEN d.marital_status = 0 THEN 'Unmarried'
#                             WHEN d.marital_status = 1 THEN 'Married'
#                             ELSE 'Unknown'
#                         END as marital_status,
                       
#                         d.blood_group,
#                         d.aadhar_no,
#                         d.pan_number,
#                         d.uan_number,
#                         d.passport_no,
#                         d.vehicle_no,
#                         d.driving_licence_no,
                       
#                         u.address_1, u.address_2, u.city,
#                         st.category_name as state,
#                         ctry.category_name as country,
#                         u.zipcode,
#                         u.city_address_2, st.category_name as state_address_2,
#                         ctry.category_name as country_address_2,
#                         u.zipcode_address_2,
                               
 
#                         u.police_station_address, ctry.category_name as police_station_country, st.category_name as police_station_state,
#                         u.police_station_district, u.police_station_tehsil, u.police_station_village, u.police_station_pincode,
                       
#                         d.contact_full_name, d.contact_phone_no, d.contact_email, d.contact_address,
#                         d.date_of_joining, d.date_of_leaving, d.last_promotion_date,
                       
#                         u.is_active,
                       
#                         d.basic_salary, d.gross_salary, d.ctc_monthly, d.ctc_yearly,
                       
#                         d.account_holder_name, d.account_number, d.bank_name, d.ifsc_code, d.swift_code, d.bank_branch
                       
#                     FROM ci_erp_users u
#                     JOIN ci_erp_users_details d ON u.id = d.user_id
#                     LEFT JOIN ci_departments dept ON d.department_id = dept.department_id
#                     LEFT JOIN ci_designations desg ON d.designation_id = desg.designation_id
#                     LEFT JOIN ci_division divi ON d.division_id = divi.division_id
#                     LEFT JOIN ci_erp_constants st ON u.state = st.constants_id
#                     LEFT JOIN ci_erp_constants ctry ON u.country = ctry.constants_id
#                     WHERE u.id = %s
#                 """, [user_id])
               
#                 user = dictfetchone(cursor)
#                 if not user:
#                     return Response({"error": "Employee not found"}, status=404)
               
#                  # Calculate age from date_of_birth
#                 if user.get("date_of_birth"):
#                     dob = user["date_of_birth"]
#                     if isinstance(dob, str):  # convert if DB returns string
#                         dob = datetime.strptime(dob, "%d-%m-%Y").date()
#                     today = date.today()
#                     user["age"] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
#                 else:
#                     user["age"] = None
 
#                 # ==================== ASSETS ====================
#                 cursor.execute("""
#                     SELECT
#                         a.assets_name,
#                         cat.category_name as category_name,
#                         br.category_name as brand_name,
#                         a.manufacturer,
#                         a.serial_number
#                     FROM ci_assets a
#                     LEFT JOIN ci_erp_constants cat ON a.assets_category_id = cat.constants_id
#                     LEFT JOIN ci_erp_constants br ON a.brand_id = br.constants_id
#                     JOIN ci_erp_users_details d ON d.employee_id = a.employee_id
#                     WHERE d.user_id = %s
#                 """, [user_id])
#                 assets = dictfetchall(cursor)
 
#                 cursor.execute("""
#                     SELECT
#                         pr.year,
#                         pr.basic_plus_da,
#                         pr.gross_salary,
#                         pr.ctc
#                     FROM ci_payroll_report pr
#                     JOIN ci_erp_users_details d ON d.employee_id = pr.employee_id
#                     WHERE d.user_id = %s
                   
#                 """, [user_id])
#                 compensation = dictfetchone(cursor)
 
 
 
 
#             profile_photo = None
#             if user.get("profile_photo"):
#                 profile_photo = f"https://tdtlworld.com/hrms-backend/media/{user['profile_photo']}"
 
           
#             response_data = {
#                 "employee_info": {
#                     "employee_id": user["employee_id"],
#                     "user_id": user["user_id"],
#                     "full_name": user["full_name"],
#                     "profile_photo": profile_photo,
#                     "department": user["department"],
#                     "designation": user["designation"],
#                     "division": user["division"],
#                     "sub_division": "N/A",
#                     "head_quarter": "N/A",
#                 },
#                 "personal_details": {
#                     "contact_number": user["contact_number"],
#                     "email": user["email"],
#                     "date_of_birth": user["date_of_birth"],
#                     "age": user["age"],
#                     "gender": user["gender"],
#                     "marital_status": user["marital_status"],
#                     "blood_group": user["blood_group"],
#                     "aadhar_no": user["aadhar_no"],
#                     "pan_number": user["pan_number"],
#                     "uan_number": user["uan_number"],
#                     "passport_no": user["passport_no"],
#                     "vehicle_no": user["vehicle_no"],
#                     "driving_licence_no": user["driving_licence_no"],
#                     "permanent_address": {
#                         "address_1": user["address_1"],
#                         "city": user["city"],
#                         "state": user["state"],
#                         "country": user["country"],
#                         "zipcode": user["zipcode"]
#                     },
#                     "correspondence_address": {
#                         "address_2": user["address_2"],
#                         "city": user["city_address_2"],
#                         "state": user["state_address_2"],
#                         "country": user["country_address_2"],
#                         "zipcode": user["zipcode_address_2"]
#                     }
#                 },
#                     "nearest_police_station": {
#                         "address": user["police_station_address"],
#                         "country": user["police_station_country"],
#                         "state": user["police_station_state"],
#                         "district" :user["police_station_district"],
#                         "tehsil": user["police_station_tehsil"],
#                         "village": user["police_station_village"],
#                         "pincode": user["police_station_pincode"]
 
#                 },
 
 
#                 "emergency_contact": {
#                     "name": user["contact_full_name"],
#                     "phone": user["contact_phone_no"],
#                     "email": user["contact_email"],
#                     "address": user["contact_address"]
#                 },
               
#                 "work_details": {
#                     "date_of_joining": user["date_of_joining"],
#                     "date_of_leaving": user["date_of_leaving"],
#                     "date_of_promotion": user["last_promotion_date"],
#                     "employee_status": "Active" if user["is_active"] == 1 else "Inactive" if user["is_active"] == 0 else "null"
#                 },
#                 "compensation_details": {
#                     "current_salary": user["basic_salary"],
#                     "current_ctc": user["ctc_yearly"],
#                     "joining_salary": user["basic_salary"],
#                     "joining_ctc": user["ctc_yearly"]
                   
#                 },
#                 "bank_details": {
#                     "account_title": user["account_holder_name"],
#                     "account_number": user["account_number"],
#                     "bank_name": user["bank_name"],
#                     "ifsc_code": user["ifsc_code"],
#                     "swift_code": user["swift_code"],
#                     "bank_branch": user["bank_branch"]
#                 },
               
#                 "assets": assets,
#                 "employee_journey": {
#                     "date_of_joining": user["date_of_joining"],
#                     "department": user["department"],
#                     "designation": user["designation"],
#                     "division": user["division"],
#                     "sub_division": "N/A",
#                     "head_quarter": "N/A",
#                     "level": "N/A",
#                     "compensation": f"{user['ctc_yearly']} yearly",
#                     "duration": "N/A"
#                 },0614
                           
#                 "compensation": {
#                     "designation": user["designation"],
#                     "level": "N/A",
#                     "year": compensation["year"] if compensation else None,
#                     "wef": "N/A",
#                     "basic_plus_da": compensation["basic_plus_da"] if compensation else None,
#                     "gross_salary": compensation["gross_salary"] if compensation else None,
#                     "ctc": compensation["ctc"] if compensation else None
#                 }
               
#             }
 
#             return Response(response_data)
 
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)
        

        
    
# def dictfetchall(cursor):
#     """Return all rows from a cursor as a dict"""
#     columns = [col[0] for col in cursor.description]
#     return [dict(zip(columns, row)) for row in cursor.fetchall()]

from decimal import Decimal, InvalidOperation
from dateutil.relativedelta import relativedelta

class EmployeeDetailsAPIView(APIView):

    def safe_decimal(self, value, default="0.00"):
        try:
            if value is None or value == "" or value == "None":
                return Decimal(default)
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal(default)

    def calculate_duration(self, date_of_joining, date_of_leaving):
        if not date_of_joining:
            return "N/A"
        
        if isinstance(date_of_joining, str):
            date_of_joining = datetime.strptime(date_of_joining, "%Y-%m-%d").date()
        
        end_date = date_of_leaving
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = date.today()
        
        if isinstance(date_of_joining, datetime):
            date_of_joining = date_of_joining.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        
        delta = relativedelta(end_date, date_of_joining)
        
        years = delta.years
        months = delta.months
        
        if years > 0 and months > 0:
            return f"{years} year{'s' if years > 1 else ''} {months} month{'s' if months > 1 else ''}"
        elif years > 0:
            return f"{years} year{'s' if years > 1 else ''}"
        elif months > 0:
            return f"{months} month{'s' if months > 1 else ''}"
        else:
            return "Less than a month"

    def get(self, request, user_id):
        try:
            with connection.cursor() as cursor:
                # ==================== EMPLOYEE DETAILS ====================
                cursor.execute("""
                    SELECT
                        u.id as user_id,
                        d.employee_id,
                        CONCAT(u.first_name, ' ', COALESCE(u.middle_name,''), ' ', u.last_name) as full_name,
                        u.profile_photo,
                        dept.department_name as department,
                        desg.designation_name as designation,
                        divi.division_name as division,
                        d.sub_division,
                        hq.location_name as headquarter,
                        g.grade_name,
                        u.contact_number,
                        u.email,
                        d.date_of_birth,
                        u.gender,
                        CASE
                            WHEN d.marital_status = 0 THEN 'Unmarried'
                            WHEN d.marital_status = 1 THEN 'Married'
                            ELSE 'Unknown'
                        END as marital_status,
                        d.blood_group,
                        d.aadhar_no,
                        d.pan_number,
                        d.uan_number,
                        d.passport_no,
                        d.vehicle_no,
                        d.driving_licence_no,
                        u.address_1, u.address_2, u.city,
                        st.category_name as state,
                        ctry.category_name as country,
                        u.zipcode,
                        u.city_address_2, st.category_name as state_address_2,
                        ctry.category_name as country_address_2,
                        u.zipcode_address_2,
                        d.police_station_address, ctry.category_name as police_station_country, st.category_name as police_station_state, d.police_station_district, d.police_station_village, d.police_station_pincode,
                        d.contact_full_name, d.contact_phone_no, d.contact_phone_no_2, d.contact_email, d.contact_address,
                        d.date_of_joining, d.date_of_leaving, d.last_promotion_date,
                        u.is_active,
                        d.basic_salary, d.gross_salary, d.ctc_monthly, d.ctc_yearly,
                        d.account_title, d.account_number, d.bank_name, d.ifsc_code, d.swift_code, d.bank_branch
                    FROM ci_erp_users u
                    JOIN ci_erp_users_details d ON u.id = d.user_id
                    LEFT JOIN ci_departments dept ON d.department_id = dept.department_id
                    LEFT JOIN ci_designations desg ON d.designation_id = desg.designation_id
                    LEFT JOIN ci_division divi ON d.division_id = divi.division_id
                    LEFT JOIN ci_headquarters hq ON d.headquarter = hq.location_id
                    LEFT JOIN ci_grade g ON d.grade_id = g.grade_id
                    LEFT JOIN ci_erp_constants st ON d.police_station_state = st.constants_id AND st.type = 'state'
                    LEFT JOIN ci_erp_constants ctry ON u.country = ctry.constants_id AND ctry.type = 'country'
                    WHERE u.id = %s
                """, [user_id])
               
                user = dictfetchone(cursor)
                if not user:
                    return Response({"error": "Employee not found"}, status=404)
               
                 # Calculate age from date_of_birth
                if user.get("date_of_birth"):
                    dob = user["date_of_birth"]
                    if isinstance(dob, str):  # convert if DB returns string
                        dob = datetime.strptime(dob, "%Y-%m-%d").date()
                    today = date.today()
                    user["age"] = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                else:
                    user["age"] = None
 
                # ==================== ASSETS ====================
                cursor.execute("""
                    SELECT
                        a.assets_name,
                        cat.category_name as category_name,
                        br.category_name as brand_name,
                        a.manufacturer,
                        a.serial_number
                    FROM ci_assets a
                    LEFT JOIN ci_erp_constants cat ON a.assets_category_id = cat.constants_id
                    LEFT JOIN ci_erp_constants br ON a.brand_id = br.constants_id
                    JOIN ci_erp_users_details d ON d.employee_id = a.employee_id
                    WHERE d.user_id = %s
                """, [user_id])
                assets = dictfetchall(cursor)

                # ==================== COMPENSATION ====================

                cursor.execute("""
                    SELECT
                        gross_salary, ctc_monthly, date_of_joining
                    FROM ci_erp_users_details
                    WHERE user_id = %s
                   
                """, [user_id])
                compensation = dictfetchone(cursor)

                gross_salary = self.safe_decimal("0.00")
                ctc_monthly = self.safe_decimal("0.00")
                date_of_joining = None

                if compensation:
                    gross_salary = self.safe_decimal(compensation.get("gross_salary", "0.00")) 
                    ctc_monthly = self.safe_decimal(compensation.get("ctc_monthly", "0.00"))
                    date_of_joining = compensation.get("date_of_joining")

                cursor.execute("""
                    SELECT particulars, value
                    FROM ci_salary_structure;
                """)
                rows = cursor.fetchall()

                # Convert to dict: {"hra": 0.25, "basic_plus_da": 0.6, ...}
                salary_structure = {row[0]: row[1] for row in rows}

                hra = self.safe_decimal("0.00")
                basic_plus_da = self.safe_decimal("0.00")
                esic_employer_contribution = self.safe_decimal("0.00")
                pf_employer_contribution = self.safe_decimal("0.00")

                if salary_structure:
                    hra = self.safe_decimal(salary_structure.get("hra", "0.00"))  
                    basic_plus_da = self.safe_decimal(salary_structure.get("basic_plus_da", "0.00"))  
                    esic_employer_contribution = self.safe_decimal(salary_structure.get("esic_employer_contribution", "0.00"))  
                    pf_employer_contribution = self.safe_decimal(salary_structure.get("pf_employer_contribution", "0.00"))  

                if gross_salary is None or gross_salary < 0:
                    gross_salary = self.safe_decimal("0.00")

                basic_plus_da_salary = basic_plus_da * gross_salary

                esic_applicable = gross_salary <= self.safe_decimal("21000")

                try:
                    if gross_salary and hra and pf_employer_contribution:
                        pf_employer = min(
                            (gross_salary - hra) * pf_employer_contribution,
                            self.safe_decimal("1800"),
                        )
                    else:
                        pf_employer = self.safe_decimal("0.00")
                except (TypeError, ValueError):
                    pf_employer = self.safe_decimal("0.00")

                try:
                    esic_employer = (
                        gross_salary * esic_employer_contribution
                        if esic_applicable and gross_salary and esic_employer_contribution
                        else self.safe_decimal("0.00")
                    )
                except (TypeError, ValueError):
                    esic_employer = self.safe_decimal("0.00")

                no_of_employment_year = 0
                if date_of_joining:
                    try:
                        if isinstance(date_of_joining, str):
                            date_of_joining = datetime.strptime(date_of_joining, "%Y-%m-%d")
                            # print("date_of_joining: ", date_of_joining)
                        
                        if date_of_joining <= datetime.now():
                            no_of_employment_year = (datetime.now() - date_of_joining).days / 365.25
                            # print("no_of_employment_year: ", no_of_employment_year)
                        else:
                            no_of_employment_year = 0
                    except (TypeError, ValueError, AttributeError) as e:
                        no_of_employment_year = 0

                no_of_employment_year = max(0, no_of_employment_year)
                # print("updated_no_of_employment_year: ", no_of_employment_year)

                try:
                    if no_of_employment_year > 5 and basic_plus_da:
                        gratuity = (basic_plus_da * self.safe_decimal("15") / self.safe_decimal("26")) * self.safe_decimal(str(no_of_employment_year))
                        # print("gratuity: ", gratuity)
                    else:
                        gratuity = self.safe_decimal("0.00")
                except (TypeError, ValueError, ZeroDivisionError):
                    gratuity = self.safe_decimal("0.00")

                if gratuity < 0:
                    gratuity = self.safe_decimal("0.00")

                if ctc_monthly in (None, "", self.safe_decimal("0.00")):
                    # print("pf: ", pf_employer, " esic: ", esic_employer, " gratuity: ", gratuity)
                    new_ctc_monthly = pf_employer + esic_employer + gratuity

                    # print("new_ctc_monthly: ", new_ctc_monthly)

                    ctc_monthly = gross_salary + new_ctc_monthly


                # ==================== AWARDS ====================

                # Get employee_id

                cursor.execute("""select employee_id from ci_erp_users_details where user_id = %s""", [user_id])

                employee_id = cursor.fetchone()[0]

                cursor.execute("""SELECT 
                    c.category_name AS award_type,
                    a.gift_item AS award_gift,
                    a.cash_price AS award_cash,
                    a.award_month_year AS month_year
                FROM ci_awards a
                LEFT JOIN ci_erp_constants c ON a.award_type_id = c.constants_id AND c.type = 'award_type'
                WHERE a.employee_id = %s
                ORDER BY a.created_at DESC""", [employee_id])

                columns = [col[0] for col in cursor.description]
                rewards = [dict(zip(columns, row)) for row in cursor.fetchall()]

                # ==================== EXIT INTERVIEW QUESTIONNAIRE ====================

                cursor.execute("""select exit_interview_questionnaire from ci_employee_exit_final where employee_id = %s""", [employee_id])

                row = cursor.fetchone()
                exit_interview_questionnaire = row if row and row[0] is not None else 'N/A'


            current_year = datetime.now().year
                

            profile_photo = None
            if user.get("profile_photo"):
                # profile_photo = f"https://tdtlworld.com/hrms-backend/media/{user['profile_photo']}"
                # profile_photo = f"https://tdtlworld.com/hrms-backend/{user['profile_photo']}"
                profile_photo = f"https://tdtlworld.com/hrms-backend/{quote(user['profile_photo'])}"
 
           
            response_data = {
                "employee_info": {
                    "employee_id": user["employee_id"],
                    "user_id": user["user_id"],
                    "full_name": user["full_name"],
                    "profile_photo": profile_photo,
                    "department": user["department"],
                    "designation": user["designation"],
                    "division": user["division"],
                    "sub_division": user["sub_division"],
                    "head_quarter": user["headquarter"],
                },
                "personal_details": {
                    "contact_number": user["contact_number"],
                    "email": user["email"],
                    "date_of_birth": user["date_of_birth"],
                    "age": user["age"],
                    "gender": user["gender"],
                    "marital_status": user["marital_status"],
                    "blood_group": user["blood_group"],
                    "aadhar_no": user["aadhar_no"],
                    "pan_number": user["pan_number"],
                    "uan_number": user["uan_number"],
                    "passport_no": user["passport_no"],
                    "vehicle_no": user["vehicle_no"],
                    "driving_licence_no": user["driving_licence_no"],
                    "permanent_address": {
                        "address_1": user["address_1"],
                        "city": user["city"],
                        "state": user["state"],
                        "country": user["country"],
                        "zipcode": user["zipcode"]
                    },
                    "correspondence_address": {
                        "address_2": user["address_2"],
                        "city": user["city_address_2"],
                        "state": user["state_address_2"],
                        "country": user["country_address_2"],
                        "zipcode": user["zipcode_address_2"]
                    }
                },
                    "nearest_police_station": {
                        "address": user["police_station_address"],
                        "country": user["police_station_country"],
                        "state": user["police_station_state"],
                        "district" :user["police_station_district"],
                        # "village": user["police_station_village"],
                        "pincode": user["police_station_pincode"]
 
                },
 
 
                "emergency_contact": {
                    "name": user["contact_full_name"],
                    "phone": user["contact_phone_no"],
                    # "phone_2": user["contact_phone_no_2"],
                    # "email": user["contact_email"],
                    "address": user["contact_address"]
                },
               
                "work_details": {
                    "date_of_joining": user["date_of_joining"],
                    "date_of_leaving": user["date_of_leaving"],
                    "date_of_promotion": user["last_promotion_date"],
                    "employee_status": "Active" if user["is_active"] == 1 else "Inactive" if user["is_active"] == 0 else "null"
                },
                # "compensation_details": {
                #     "current_salary": user["basic_salary"],
                #     "current_ctc": user["ctc_yearly"],
                #     "joining_salary": user["basic_salary"],
                #     "joining_ctc": user["ctc_yearly"]
                   
                # },
                "bank_details": {
                    "account_title": user["account_title"],
                    "account_number": user["account_number"],
                    "bank_name": user["bank_name"],
                    "ifsc_code": user["ifsc_code"],
                    # "swift_code": user["swift_code"],
                    "bank_branch": user["bank_branch"]
                },
               
                "assets": assets,
                "employee_journey": {
                    "date_of_joining": user["date_of_joining"],
                    "department": user["department"],
                    "designation": user["designation"],
                    "division": user["division"],
                    "sub_division": user["sub_division"],
                    "head_quarter": user["headquarter"],
                    "level": user["grade_name"],
                    "compensation": f"{user['ctc_yearly']} yearly",
                    "duration": self.calculate_duration(user["date_of_joining"], user["date_of_leaving"])
                },
                           
                "compensation": {
                    "designation": user["designation"],
                    "level": user["grade_name"],
                    "year": current_year,
                    "wef": "N/A",
                    "basic_plus_da": round(basic_plus_da_salary),
                    "gross_salary": round(gross_salary),
                    "ctc": round(ctc_monthly)
                },
                "rewards": rewards,
                "exit_interview_questionnaire": exit_interview_questionnaire
               
            }
 
            return Response(response_data)
 
        except Exception as e:
            return Response({"error": str(e)}, status=500)
 


class FamilyMembersAPIView(APIView):
    """
    API for managing family members:
    - GET: fetch family members by user_id
    - POST: add a family member (requires user_id)
    - PATCH: update a family member by family_member_id
    - DELETE: remove a family member by family_member_id
    """

    # GET by userid
    def get(self, request, user_id):
        try:
            if not user_id:
                return Response({"error": "user_id is required"}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT family_member_id, user_id, name, age, relation,
                           occupation, date_of_birth, contact_number, gender, created_at
                    FROM ci_family_members
                    WHERE user_id = %s
                """, [user_id])
                rows = dictfetchall(cursor)

            return Response(rows, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # POST (create for a userid)
    def post(self, request, user_id):
        try:
            data = request.data
            name = data.get("name")
            age = data.get("age")
            relation = data.get("relation")
            occupation = data.get("occupation")
            date_of_birth = data.get("date_of_birth")
            contact_number = data.get("contact_number") 
            gender = data.get("gender")
            created_at = datetime.now()

            if not (user_id and name and relation and date_of_birth and gender):
                return Response({"error": "user_id, name, relation, date_of_birth, gender are required"}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_family_members
                        (user_id, name, age, relation, occupation, date_of_birth, contact_number, gender, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                               
                """, [user_id, name, age, relation, occupation, date_of_birth, contact_number, gender, created_at])

                family_member_id = cursor.lastrowid 

            return Response({
                "message": "Family member added successfully",
                "data": {
                    "family_member_id": family_member_id,
                    "user_id": user_id,
                    "name": name,
                    "age": age,
                    "relation": relation,
                    "occupation": occupation,
                    "date_of_birth": date_of_birth,
                    "contact_number": contact_number,
                    "gender": gender,
                    "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            }, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


    # PATCH by family_member_id
    def patch(self, request, family_member_id):
        try:
            if not family_member_id:
                return Response({"error": "family_member_id is required"}, status=400)

            data = request.data
            fields = []
            values = []

            if "name" in data:
                fields.append("name = %s")
                values.append(data.get("name"))
            if "age" in data:
                fields.append("age = %s")
                values.append(data.get("age"))
            if "relation" in data:
                fields.append("relation = %s")
                values.append(data.get("relation"))
            if "occupation" in data:
                fields.append("occupation = %s")
                values.append(data.get("occupation"))
            if "date_of_birth" in data:
                fields.append("date_of_birth = %s")
                values.append(data.get("date_of_birth"))
            if "contact_number" in data:
                fields.append("contact_number = %s")
                values.append(data.get("contact_number"))
            if "gender" in data:
                fields.append("gender = %s")
                values.append(data.get("gender"))    
            

            if not fields:
                return Response({"error": "No fields to update"}, status=400)

            values.append(family_member_id)
            query = f"UPDATE ci_family_members SET {', '.join(fields)} WHERE family_member_id = %s"

            with connection.cursor() as cursor:
                cursor.execute(query, values)

            return Response({"message": "Family member updated successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    #  DELETE by family_member_id
    def delete(self, request, family_member_id):
        try:
            if not family_member_id:
                return Response({"error": "family_member_id is required"}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ci_family_members WHERE family_member_id = %s", [family_member_id])

            return Response({"message": "Family member deleted successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
 
 
class GetEmployeeShiftAPIView(APIView):
    def get(self, request, user_id):
        if not user_id:
            return Response(
                {"status": "error", "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        try:
            with connection.cursor() as cursor:
                # Fetch employee's shift details
                cursor.execute("""
                    SELECT
                        u.user_id,
                        u.employee_id,
                        u.office_shift_id,
                        s.shift_name,
                        s.monday_in_time, s.monday_out_time,
                        s.tuesday_in_time, s.tuesday_out_time,
                        s.wednesday_in_time, s.wednesday_out_time,
                        s.thursday_in_time, s.thursday_out_time,
                        s.friday_in_time, s.friday_out_time,
                        s.saturday_in_time, s.saturday_out_time,
                        s.sunday_in_time, s.sunday_out_time
                    FROM ci_erp_users_details u
                    INNER JOIN ci_office_shifts s
                        ON u.office_shift_id = s.office_shift_id
                    WHERE u.user_id = %s
                """, [user_id])
                shift_data = dictfetchone(cursor)
 
                if not shift_data:
                    return Response(
                        {"status": "error", "message": "Shift not found for this user"},
                        status=status.HTTP_404_NOT_FOUND
                    )
 
                return Response(
                    {"status": "success", "shift": shift_data},
                    status=status.HTTP_200_OK
                )
 
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



from django.http import HttpResponse
class ApproveResignationThroughMail(APIView):
    def get(self, request, resignation_id):
        try:
            with connection.cursor() as cursor:

                cursor.execute("select resignation_id, employee_id from ci_resignations where resignation_id=%s", [resignation_id])
                row = cursor.fetchone()

                if not row:
                    return HttpResponse("<h2 style='color:red;'>Resignation not found.</h2>", status=404)
                
                employee_id = row[1]
                
                cursor.execute("update ci_resignations set status=1 where resignation_id=%s", [resignation_id])

                # Send Notification
                #Get user id
                cursor.execute("""select id from ci_erp_users where username = %s""", [employee_id])

                user_result = cursor.fetchone()
                if not user_result:
                    raise ValueError(f"No user found for employee_id: {employee_id} in the system")
                
                user_id = user_result[0]

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

                notification_text = f"Your resignation has been processed. Kindly proceed with the exit formalities"
                cursor.execute("""
                    INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, [admin_id, user_id, notification_text])

                return HttpResponse("<h2 style='color:green;'>Resignation approved.</h2>", status=200)
        except Exception as e:
            return HttpResponse(f"<h2 style='color:red;'>Error: {str(e)}</h2>", status=500)
        
class RejectResignationThroughMail(APIView):
    def get(self, request, resignation_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("select resignation_id from ci_resignations where resignation_id=%s", [resignation_id])
                resignation = cursor.fetchone()
                if not resignation:
                    return HttpResponse("<h2 style='color:red;'>Resignation not found.</h2>", status=404)
                cursor.execute("update ci_resignations set status=0 where resignation_id=%s", [resignation_id])
                return HttpResponse("<h2 style='color:orange;'>Resignation rejected.</h2>", status=200)
        except Exception as e:
            return HttpResponse(f"<h2 style='color:red;'>Error: {str(e)}</h2>", status=500)
 

 


# Employee Exit Procedure - 28-07-2025

# # 17-09-2025

# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status
# # from django.db import connection

# # class CreateExitQuestionnaire(APIView):

# #     def get(self, request):
# #         try:
# #             with connection.cursor() as cursor:
# #                 cursor.execute("SELECT ques_id, question, created_date FROM ci_employee_exit_questionnaire")
# #                 rows = cursor.fetchall()
# #                 data = [
# #                     {"ques_id": row[0], "question": row[1], "created_date": row[2].strftime("%Y-%m-%d %H:%M:%S")}
# #                     for row in rows
# #                 ]
# #             return Response(data, status=status.HTTP_200_OK)

# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# #     def post(self, request):
# #         try:
# #             question = request.data.get("question")
# #             if not question:
# #                 return Response({"error": "Question is required."}, status=status.HTTP_400_BAD_REQUEST)

# #             with connection.cursor() as cursor:
# #                 cursor.execute(
# #                     "INSERT INTO ci_employee_exit_questionnaire (question) VALUES (%s)",
# #                     [question]
# #                 )
# #             return Response({"message": "Question added successfully."}, status=status.HTTP_201_CREATED)

# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# #     def put(self, request):
# #         try:
# #             ques_id = request.data.get("ques_id")
# #             question = request.data.get("question")

# #             if not ques_id or not question:
# #                 return Response({"error": "ques_id and question are required."}, status=status.HTTP_400_BAD_REQUEST)

# #             with connection.cursor() as cursor:
# #                 cursor.execute(
# #                     "UPDATE ci_employee_exit_questionnaire SET question = %s WHERE ques_id = %s",
# #                     [question, ques_id]
# #                 )
# #                 if cursor.rowcount == 0:
# #                     return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

# #             return Response({"message": "Question updated successfully."}, status=status.HTTP_200_OK)

# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# #     def delete(self, request):
# #         try:
# #             ques_id = request.data.get("ques_id")
# #             if not ques_id:
# #                 return Response({"error": "ques_id is required."}, status=status.HTTP_400_BAD_REQUEST)

# #             with connection.cursor() as cursor:
# #                 cursor.execute(
# #                     "DELETE FROM ci_employee_exit_questionnaire WHERE ques_id = %s",
# #                     [ques_id]
# #                 )
# #                 if cursor.rowcount == 0:
# #                     return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

# #             return Response({"message": "Question deleted successfully."}, status=status.HTTP_200_OK)

# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# # # Get Form Data For Questionneair Form 

# # from django.db import connection
# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status

# # class GetEmployeeExitQuestionneair(APIView):
# #     def get(self, request):
# #         try:
# #             with connection.cursor() as cursor:
# #                 cursor.execute("""
# #                     SELECT 
# #                         u.id,
# #                         ud.employee_id,
# #                         CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
# #                         dt.department_name,
# #                         ds.designation_name,
# #                         CASE
# #                             WHEN u.gender = 1 THEN 'Male'
# #                             WHEN u.gender = 2 THEN 'Female'
# #                             ELSE 'Other'
# #                         END AS gender,
# #                         ud.date_of_joining,
# #                         ud.date_of_leaving,
# #                         dv.division_name,
# #                         CONCAT(mgr.first_name, ' ', mgr.last_name) AS manager_name
# #                     FROM ci_erp_users u
# #                     LEFT JOIN ci_erp_users_details ud ON u.id = ud.user_id
# #                     INNER JOIN ci_departments dt ON ud.department_id = dt.department_id
# #                     INNER JOIN ci_designations ds ON dt.department_id = ds.department_id
# #                     INNER JOIN ci_division dv ON ud.division_id = dv.division_id
# #                     LEFT JOIN ci_erp_users mgr ON ud.manager = mgr.id
# #                     GROUP BY u.id;
# #                 """)

# #                 columns = [col[0] for col in cursor.description]
# #                 data = [dict(zip(columns, row)) for row in cursor.fetchall()]

# #             return Response({"status": True, "data": data}, status=status.HTTP_200_OK)

# #         except Exception as e:
# #             return Response({"status": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # # Save Feedback Form 

# # class SubmitEmployeeFeedbackForm(APIView):
# #     def post(self, request):
# #         try:
# #             employee_id = request.data.get('employee_id')
# #             feedback_list = request.data.get('feedback', [])

# #             if not employee_id or not feedback_list:
# #                 return Response({"error": "employee_id and feedback are required."}, status=status.HTTP_400_BAD_REQUEST)

# #             with connection.cursor() as cursor:
# #                 for item in feedback_list:
# #                     ques_id = item.get('ques_id')
# #                     answer = item.get('answer')
# #                     brief_answer = item.get('brief_answer', None)

# #                     if not ques_id or not answer:
# #                         continue  # Skip incomplete entries

# #                     cursor.execute("""
# #                         INSERT INTO ci_employee_feedback (employee_id, ques_id, answer, brief_answer)
# #                         VALUES (%s, %s, %s, %s)
# #                     """, [employee_id, ques_id, answer, brief_answer])

# #             return Response({"message": "Feedback submitted successfully."}, status=status.HTTP_201_CREATED)

# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# # class ViewCompletedFeedbackForm(APIView):
# #     def get(self, request):
# #         try:
# #             employee_id = request.GET.get('employee_id')
 
# #             if not employee_id:
# #                 return Response({"status": False, "error": "employee_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
# #             with connection.cursor() as cursor:
# #                 query = """
# #                     SELECT *
# #                     FROM ci_erp_users_details AS ud
# #                     INNER JOIN ci_employee_feedback AS ef
# #                         ON ud.employee_id = ef.employee_id
# #                     INNER JOIN ci_employee_exit_questionnaire AS eq
# #                         ON ef.ques_id = eq.ques_id
# #                     WHERE ef.employee_id = %s
# #                 """
# #                 cursor.execute(query, [employee_id])
# #                 columns = [col[0] for col in cursor.description]
# #                 results = [dict(zip(columns, row)) for row in cursor.fetchall()]
 
# #             return Response({"status": True, "data": results}, status=status.HTTP_200_OK)
 
# #         except Exception as e:
# #             return Response({"status": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# #Exit-Employee Exit-Dashboard HR

# class ExitQuestionnaireAPIView(APIView):
#     def post(self, request):
#         try:
#             question = request.data.get("question")
#             options = request.data.get("options", [])

#             if not question or not options:
#                 return Response({"status": "error", "message": "Question and options are required"}, status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
#                 # Insert question
#                 cursor.execute("""
#                     INSERT INTO ci_employee_exit_questionnaire (question, created_date)
#                     VALUES (%s, %s)
                   
#                 """, [question, datetime.now().date()])

#                 ques_id = cursor.lastrowid

#                 # Insert options
#                 for opt in options:
#                     cursor.execute("""
#                         INSERT INTO ci_employee_exit_option (ques_id, answer_option, created_at)
#                         VALUES (%s, %s, %s)
#                     """, [ques_id, opt, datetime.now().date()])

#             return Response({
#                 "status": "success",
#                 "message": "Question and options added successfully",
#                 "data": {
#                     "question": question,
#                     "options": options
#                 }
#             }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def get(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT q.ques_id, q.question, o.answer_option
#                     FROM ci_employee_exit_questionnaire q
#                     LEFT JOIN ci_employee_exit_option o ON q.ques_id = o.ques_id
#                     ORDER BY q.ques_id, o.answer_id
#                 """)
#                 rows = cursor.fetchall()

#             data = {}
#             for row in rows:
#                 ques_id, question, option = row
#                 if ques_id not in data:
#                     data[ques_id] = {
#                         "question": question,
#                         "options": []   # start with empty list
#                     }
#                 if option:  # add option only if it exists
#                     data[ques_id]["options"].append(option)

#             return Response({
#                 "status": "success",
#                 "data": list(data.values())
#             }, status=200)

#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=500)


#     def patch(self, request, ques_id):
#         """
#         Update question text or replace options for a given ques_id
#         """
#         try:
#             question = request.data.get("question")
#             options = request.data.get("options")  # should be list if provided

#             updated_question = False
#             updated_options = False

#             with connection.cursor() as cursor:
#                 # Update question text
#                 if question:
#                     rows = cursor.execute("""
#                         UPDATE ci_employee_exit_questionnaire
#                         SET question = %s
#                         WHERE ques_id = %s
#                     """, [question, ques_id])
#                     if rows > 0:
#                         updated_question = True

#                 # Replace options if provided
#                 if options is not None:
#                     cursor.execute("DELETE FROM ci_employee_exit_option WHERE ques_id = %s", [ques_id])
#                     for opt in options:
#                         cursor.execute("""
#                             INSERT INTO ci_employee_exit_option (ques_id, answer_option, created_at)
#                             VALUES (%s, %s, %s)
#                         """, [ques_id, opt, datetime.now().date()])
#                     updated_options = True

#             # Prepare response message
#             if updated_question and updated_options:
#                 message = "Question and/or options updated successfully"
#             elif updated_question:
#                 message = "Question updated successfully"
#             elif updated_options:
#                 message = "Options updated successfully"
#             else:
#                 message = "No changes made. Invalid ques_id or same data."

#             return Response({
#                 "status": "success" if (updated_question or updated_options) else "error",
#                 "message": message
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
            
#     def delete(self, request, ques_id):
#         """
#         Delete question and its options by ques_id
#         """
#         try:
#             with connection.cursor() as cursor:
#                 # Delete options first (foreign key dependency)
#                 cursor.execute("DELETE FROM ci_employee_exit_option WHERE ques_id = %s", [ques_id])
#                 # Delete question
#                 cursor.execute("DELETE FROM ci_employee_exit_questionnaire WHERE ques_id = %s", [ques_id])

#             return Response({
#                 "status": "success",
#                 "message": f"Question {ques_id} and its options deleted successfully"
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ##Employee Exit - Employee Panel
# # class SubmitEmployeeExitFeedbackForm(APIView):
# #     def post(self, request):
# #         try:
# #             employee_id = request.data.get('employee_id')
# #             feedback_list = request.data.get('feedback', [])

# #             if not employee_id or not feedback_list:
# #                 return Response({"error": "employee_id and feedback are required."}, status=status.HTTP_400_BAD_REQUEST)

# #             with connection.cursor() as cursor:
# #                 for item in feedback_list:
# #                     ques_id = item.get('ques_id')
# #                     answer = item.get('answer')
# #                     brief_answer = item.get('brief_answer', None)

# #                     if not ques_id or not answer:
# #                         continue  # Skip incomplete entries

# #                     cursor.execute("""
# #                         INSERT INTO ci_employee_exit_feedback (employee_id, ques_id, answer, brief_answer)
# #                         VALUES (%s, %s, %s, %s)
# #                     """, [employee_id, ques_id, answer, brief_answer])

# #             return Response({"message": "Exit Interview Questionnaire submitted successfully."}, status=status.HTTP_201_CREATED)

# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# # class SubmitEmployeeExitFeedbackForm(APIView):
# #     def post(self, request):
# #         try:
# #             employee_id = request.data.get('employee_id')
# #             # user_id = request.data.get('user_id')  # 👈 Add user_id
# #             feedback_list = request.data.get('feedback', [])

# #             if not employee_id or not feedback_list:
# #                 return Response(
# #                     {"error": "employee_id, user_id and feedback are required."},
# #                     status=status.HTTP_400_BAD_REQUEST
# #                 )

# #             with connection.cursor() as cursor:
# #                 # Insert feedback list
# #                 for item in feedback_list:
# #                     ques_id = item.get('ques_id')
# #                     answer = item.get('answer')
# #                     brief_answer = item.get('brief_answer', None)

# #                     if not ques_id or not answer:
# #                         continue  # Skip incomplete entries

# #                     cursor.execute("""
# #                         INSERT INTO ci_employee_exit_feedback (employee_id, ques_id, answer, brief_answer)
# #                         VALUES (%s, %s, %s, %s)
# #                         ON DUPLICATE KEY UPDATE 
# #                             answer = VALUES(answer),
# #                             brief_answer = VALUES(brief_answer)
# #                     """, [employee_id, ques_id, answer, brief_answer])

# #                 # === Check if all questions are answered ===
# #                 cursor.execute("SELECT COUNT(*) FROM ci_employee_exit_questionnaire")
# #                 total_questions = cursor.fetchone()[0]

# #                 cursor.execute("""
# #                     SELECT COUNT(DISTINCT ques_id) 
# #                     FROM ci_employee_exit_feedback 
# #                     WHERE employee_id = %s
# #                 """, [employee_id])
# #                 answered_questions = cursor.fetchone()[0]

# #                 if answered_questions == total_questions and total_questions > 0:
# #                     # ✅ Auto-update final table
# #                     cursor.execute("""
# #                         INSERT INTO ci_employee_exit_final (employee_id, user_id, exit_interview_questionnaire)
# #                         VALUES (%s, %s, 'Yes')
# #                         ON DUPLICATE KEY UPDATE 
# #                             exit_interview_questionnaire = 'Yes',
# #                             user_id = VALUES(user_id)
# #                     """, [employee_id])

# #             return Response(
# #                 {"message": "Exit Interview Questionnaire submitted successfully."},
# #                 status=status.HTTP_201_CREATED
# #             )

# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # class SubmitEmployeeExitFeedbackForm(APIView):
# #     def post(self, request):
# #         try:
# #             employee_id = request.data.get('employee_id')
# #             # user_id = request.data.get('user_id')  # 👈 Add user_id
# #             feedback_list = request.data.get('feedback', [])

# #             if not employee_id or not feedback_list:
# #                 return Response(
# #                     {"error": "employee_id, user_id and feedback are required."},
# #                     status=status.HTTP_400_BAD_REQUEST
# #                 )

# #             with connection.cursor() as cursor:
# #                 # Insert feedback list
# #                 for item in feedback_list:
# #                     ques_id = item.get('ques_id')
# #                     answer = item.get('answer')
# #                     brief_answer = item.get('brief_answer', None)

# #                     if not ques_id or not answer:
# #                         continue  # Skip incomplete entries

# #                     cursor.execute("""
# #                         INSERT INTO ci_employee_exit_feedback (employee_id, ques_id, answer, brief_answer)
# #                         VALUES (%s, %s, %s, %s)
# #                         ON DUPLICATE KEY UPDATE 
# #                             answer = VALUES(answer),
# #                             brief_answer = VALUES(brief_answer)
# #                     """, [employee_id, ques_id, answer, brief_answer])

# #                     # ✅ Auto-update final table
# #                 cursor.execute("""
# #                         INSERT INTO ci_employee_exit_final (employee_id, user_id, exit_interview_questionnaire)
# #                         VALUES (%s, %s, 'Yes')
# #                         ON DUPLICATE KEY UPDATE 
# #                             exit_interview_questionnaire = 'Yes',
# #                             user_id = VALUES(user_id)
# #                     """, [employee_id])

# #             return Response(
# #                 {"message": "Exit Interview Questionnaire submitted successfully."},
# #                 status=status.HTTP_201_CREATED
# #             )

# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





# ##======   When the employee submit the form then automatically status updated YES in the final table
# class SubmitEmployeeExitFeedbackForm(APIView):
#     def post(self, request):
#         try:
#             employee_id = request.data.get('employee_id')
#             feedback_list = request.data.get('feedback', [])

#             if not employee_id or not feedback_list:
#                 return Response({"error": "employee_id and feedback are required."}, status=status.HTTP_400_BAD_REQUEST)

#             with connection.cursor() as cursor:
              
#                 cursor.execute(
#                     """SELECT COUNT(*) FROM ci_employee_exit_feedback WHERE employee_id = %s""",
#                     [employee_id]
#                 )
#                 already_exists = cursor.fetchone()[0]

#                 if already_exists > 0:
#                     return Response(
#                         {"message": "You have already answered the questionnaire."},
#                         status=status.HTTP_200_OK
#                     )

             
#                 for item in feedback_list:
#                     ques_id = item.get('ques_id')
#                     answer = item.get('answer')
#                     brief_answer = item.get('brief_answer', None)

#                     if not ques_id or not answer:
#                         continue 

#                     cursor.execute("""
#                         INSERT INTO ci_employee_exit_feedback (employee_id, ques_id, answer, brief_answer)
#                         VALUES (%s, %s, %s, %s)
#                     """, [employee_id, ques_id, answer, brief_answer])

                
#                 cursor.execute("SELECT id FROM ci_erp_users WHERE username = %s", [employee_id])
#                 user_id = cursor.fetchone()[0]

#                 cursor.execute("""
#                     INSERT INTO ci_employee_exit_final (user_id, employee_id, exit_interview_questionnaire)
#                     VALUES (%s, %s, %s)
#                 """, [user_id, employee_id, 'Y'])

#             return Response({"message": "Feedback submitted successfully."}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# class ViewCompletedFeedbackForm(APIView):
#     def get(self, request):
#         try:
#             employee_id = request.GET.get("employee_id")
#             user_id = request.user.id  # logged-in user submitting

#             if not employee_id:
#                 return Response({"status": False, "error": "employee_id is required"}, status=400)

            

#             with connection.cursor() as cursor:


#                 cursor.execute("""SELECT
#                     u.id as user_id,
#                     d.employee_id,
#                     CONCAT(u.first_name, ' ', COALESCE(u.middle_name,''), ' ', u.last_name) as full_name,
#                     dept.department_name as department,
#                     desg.designation_name as designation,
#                     divi.division_name as division,
#                     d.date_of_joining,
#                     h.location_name as headquarter,
#                     r.last_working_day,
                   
#                     d.manager_emp_id,
                    
#                     CONCAT(mu.first_name, ' ', COALESCE(mu.middle_name,''), ' ', mu.last_name) AS manager_full_name

#                     FROM ci_erp_users u
#                     JOIN ci_erp_users_details d ON u.id = d.user_id
                 
#                     LEFT JOIN ci_departments dept ON d.department_id = dept.department_id
#                     LEFT JOIN ci_designations desg ON d.designation_id = desg.designation_id
#                     LEFT JOIN ci_division divi ON d.division_id = divi.division_id
#                     LEFT JOIN ci_headquarters h ON d.location_id = h.location_id
#                     LEFT JOIN ci_resignations r ON d.employee_id = r.employee_id
#                     LEFT JOIN ci_erp_users_details md ON d.manager_emp_id = md.employee_id
#                     LEFT JOIN ci_erp_users mu ON md.user_id = mu.id
#                     WHERE d.employee_id = %s
#                     """,[employee_id])
#                 emp_data=dictfetchall(cursor)

#                 # Fetch required fields
#                 cursor.execute("""
#                     SELECT 
#                         ef.employee_id,
#                         eq.ques_id,
#                         eq.question,
#                         ef.answer,
#                         ef.brief_answer
#                     FROM ci_employee_exit_feedback ef
#                     INNER JOIN ci_employee_exit_questionnaire eq 
#                         ON ef.ques_id = eq.ques_id
#                     WHERE ef.employee_id = %s


#                 """, [employee_id])
#                 columns = [col[0] for col in cursor.description]
#                 results = [dict(zip(columns, row)) for row in cursor.fetchall()]


#             return Response({"status": True, "emp_data":emp_data,"data": results}, status=200)

#         except Exception as e:
#             return Response({"status": False, "error": str(e)}, status=500)



# class HRAssetsDashboard(APIView):
#     def get(self,request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("select constants_id,category_name from ci_erp_constants where type='assets_category';")
#                 assets_list=dictfetchall(cursor)


#                 # List of assets and their status as per employees whose last working day is present .
#                 cursor.execute("""
#                        SELECT 
#                             e.username AS employee_id,
#                             CONCAT(e.first_name,' ',e.last_name) AS name,
#                             a.id AS asset_id,
#                             a.assets_category_id,
#                             c.category_name AS Asset_name,
#                             a.employee_confirmation,
#                             CASE 
#                                 WHEN a.return_request_status = 2 THEN 'returned'
#                                 ELSE 'pending' 
#                             END AS return_status
#                         FROM ci_resignations r
#                         JOIN ci_erp_users e 
#                             ON TRIM(r.employee_id) = TRIM(e.username)
#                         JOIN ci_assets a 
#                             ON e.username = a.employee_id
#                         JOIN ci_erp_constants c 
#                             ON a.assets_category_id = c.constants_id
#                         WHERE r.last_working_day IS NOT NULL
#                         ORDER BY e.id, a.id;
                        
#                     """)

#                 assets_status=dictfetchall(cursor)
#                 return Response({"assets_list":assets_list,"assets_status":assets_status},status=200)
#         except Exception as e:
#             return Response({"error":str(e)},status=500)



# class HRAssetsApprovalDashboard(APIView):
#     def patch(self, request, pk):
#         action = request.data.get("action", "").strip().lower()
 
       
#         if action == "return_yes":
           
#                 with connection.cursor() as cursor:
#                     #  Get brand_id for this asset
#                     cursor.execute("""
#                         SELECT brand_id , quantity
#                         FROM ci_assets
#                         WHERE id = %s
#                     """, [pk])
#                     row = cursor.fetchone()
#                     if not row:
#                         return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)
   
#                     # brand_id = row[0]
#                     brand_id, quantity = row
   
#                     #  Update asset return status
#                     cursor.execute("""
#                         UPDATE ci_assets
#                         SET returned = 'Y', return_request_status = '2'
#                         WHERE id = %s
#                     """, [pk])
   
#                     #  Update stock back in ci_erp_constants (increment by 1)
#                     cursor.execute("""
#                         UPDATE ci_erp_constants
#                         SET field_one = COALESCE(field_one, 0) + %s
#                         WHERE constants_id = %s
#                     """, [quantity, brand_id])

#                     # Update ci_employee_exit_final if all assets returned

#                     cursor.execute("select employee_id from ci_assets where id=%s",[pk])
#                     emp_id=cursor.fetchone()[0]

#                     cursor.execute("""select count(id) as accepted_count from ci_assets where employee_id=%s and employee_confirmation="accepted";""",[emp_id])

#                     accepted_count=cursor.fetchone()[0]


#                     cursor.execute("""select count(id) as returned_count from ci_assets where employee_id=%s and employee_confirmation="accepted" and return_request_status='2';""",[emp_id])

#                     returned_count=cursor.fetchone()[0]


#                     if accepted_count==returned_count:
#                         cursor.execute("update ci_employee_exit_final set return_asset='Y' where employee_id=%s",[emp_id])
#                         transaction.commit()

#                 return Response({
#                     "message": "Return confirmed. Asset marked as returned and notifications sent."
#                 }, status=status.HTTP_200_OK)

#         elif action == "return_no":
#             try:
#                 with connection.cursor() as cursor:
#                     cursor.execute("""
#                         UPDATE ci_assets
#                         SET return_request_status = '0'
#                         WHERE id = %s
#                     """, [pk])
#                 return Response({"message": "Return request denied. Asset remains allocated."}, status=status.HTTP_200_OK)
#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    


# class GetExitDate(APIView):
#     def get(self,request,employee_id):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("select employee_id from ci_resignations where employee_id=%s",[employee_id])
#                 emp=cursor.fetchone()
#                 if emp:
#                     cursor.execute("select case when last_working_day then last_working_day else 'NA' end as last_working_day from ci_resignations where employee_id=%s;",[employee_id])
#                     exit_date=cursor.fetchone()
#                     return Response({"last_working_day":exit_date},status=200)
#                 return Response({"last_working_day":'NA'})

#         except Exception as e:
#             return Response({"error":str(e)},status=500)



# class ResignedEmployeesDropdownAPIView(APIView):
#     """
#     API to fetch employees whose last_working_day is in the past
#     for showing in a dropdown.
#     """

#     def get(self, request):
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                    SELECT 
#                         u.id AS user_id,
#                         r.employee_id,
# 						CONCAT(u.first_name,' ',u.last_name) AS employee_name,
#                         r.last_working_day
#                     FROM ci_resignations r
#                     INNER JOIN ci_erp_users u ON r.employee_id = u.username
#                     WHERE r.last_working_day < CURRENT_DATE
#                     ORDER BY u.username ASC
#                 """)
#                 rows = cursor.fetchall()

#             data = [
#                 {
#                     "user_id": row[0],
#                     "employee_id": row[1],
#                     "employee_name": row[2],
#                     "last_working_day": row[3].strftime("%Y-%m-%d"),
#                 }
#                 for row in rows
#             ]

#             return Response(data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





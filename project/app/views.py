from calendar import monthrange
from datetime import date, datetime, time
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.files.storage import default_storage
import os
from django.http import Http404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import BiomatricDataTemp, ERPUser, ERPUserDetails, Task, TaskDiscussion, TaskFile, TaskNote, ErpUser1, CiStaffRole, Department,  Announcement
from .models import CiDesignation, Policy, CiBiomatricData, CIPunchReport, ContractOption, Event, Holiday
from .serializers import ApplyLeaveSerializer, ChangePasswordSerializers, ERPUserSerializer, LoginSerializer, MonthlyAttendenceSerializer, OnDutyRequestSerializer
from .serializers import  RegistrationSerializer, TodayAttendenceSerializers,TaskSerializer, TaskDiscussionSerializer, TaskFileSerializer, TaskNoteSerializer, ErpUserSerializer
from .serializers import  CiStaffRoleSerializer,AnnouncementSerializer, DepartmentSerializer, CiDesignationSerializer, PolicySerializer, CiBiomatricDataSerializer, CIPunchReportSerializer, ContractOptionSerializer
from .serializers import EventSerializer, HolidaySerializer
from .permissions import IsAdmin,IsEmployee,IsReportingManager
from .permissions import IsAdmin,IsEmployee,IsReportingManager
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated

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
from .serializers import  CIPunchReportSerializer, My_ProjectSerializer , AssignedTaskSerializer,AssignedTaskDetailView
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
from .models import CIPunchReport, ContractOption,My_Project , AssignedTask
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_datetime
import requests
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


class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access the login view

    def post(self, request, *args, **kwargs):
        # Validate and authenticate using the LoginSerializer
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']  # The user object returned by the serializer
           # print("User: ", user)
            
            # Create JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Return the JWT token along with the role
            return Response({
                'refresh': str(refresh),
                'access': access_token,
                'role': user.user_role_id.role_name,  # Assuming you have a `user_role_id` ForeignKey to `StaffRole`
                 # Added user_id to the response
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApplyLeave(APIView):
    permission_classes = [IsAuthenticated,IsReportingManager]  # Ensure the user is authenticated
   # permission_classes = [AllowAny]  # Allow anyone to access the login view
    
    def post(self, request):
        emp_id = request.user.id
        # print("empi_id: ",emp_id)
        request.data['employee_id'] = emp_id
        serializer = ApplyLeaveSerializer(data = request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"Message":"Leave applied sucessfully!!"})
        return Response({"error":serializer.errors})

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
    

class TodayAttendance(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = date.today().strftime('%Y-%m-%d')
        user_id = request.user.id
        
        # Fetch employees under the current user
        under_emp_ids = ERPUserDetails.objects.filter(manager=user_id).values_list('user_id', flat=True)
        
        # Debug: Print under_emp_ids
        print("Under Employee IDs:", list(under_emp_ids))
        
        # Fetch today's attendance data for these employees
        attendance_under_data = BiomatricDataTemp.objects.filter(
            attendance_date=today,
            userid__in=under_emp_ids
        )
        
        # Debug: Print attendance_under_data
        print("Attendance Under Data:", attendance_under_data)
        
        # Fetch today's attendance data for the current user
        attendance_own_data = BiomatricDataTemp.objects.filter(
            attendance_date=today,
            userid=user_id,
        )
        
        # Combine both attendance datasets
        combined_attendance_data = attendance_under_data | attendance_own_data
        
        # Serialize the data
        serializer = TodayAttendenceSerializers(combined_attendance_data, many=True)
                
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
class MonthlyAttendence(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user_id = request.user.id  # Replace with request.user.id in production
        if not request.data.get('var'):
            return Response({"var": "Please provide this fields"})
        if request.data.get('var') == "current":
            date_str = datetime.today().strftime("%Y-%m")
        elif request.data.get('var') == "monthly":
            date_str = request.data.get('date')
        
        if not date_str:
            return Response({"error": "Date is required"}, status=400)
        
        try:
            # Convert the string to a datetime object
            date_obj = datetime.strptime(date_str, "%Y-%m")
            year = date_obj.year
            month = date_obj.month
        except ValueError:
            return Response({"error": "Invalid date format. Expected format: YYYY-MM"}, status=400)
        
        # Generate all dates in the given month
        num_days = monthrange(year, month)[1]
        all_dates = [datetime(year, month, day).date() for day in range(1, num_days + 1)]
        
        # Query to get present data
        present_data = list(
            BiomatricDataTemp.objects.filter(
                userid=user_id,
                attendance_date__startswith=f"{year}-{month:02d}"
            )
            .values("attendance_date", "emp_id", "attendance_status")
            .annotate(count=Count("emp_id"))
        )
        
        # Convert present_data to a dictionary for quick lookup
        present_dict = {
            datetime.strptime(entry["attendance_date"], "%Y-%m-%d").date(): entry
            for entry in present_data
        }
        
        # Build the final data, including absent dates and clock_in times
        final_data = []
        for date in all_dates:
            if date in present_dict:
                record = present_dict[date]
                clock_in_record = BiomatricDataTemp.objects.filter(
                    userid=user_id,
                    attendance_date=date,
                    state_in_out="in"
                ).order_by('clock_in').values('clock_in').first()
                record["clock_in"] = clock_in_record["clock_in"] if clock_in_record else "00:00"
                final_data.append(record)
            else:
                final_data.append({
                    "attendance_date": date,
                    "emp_id": user_id,
                    "attendance_status": "absent",
                    "count": 0,
                    "clock_in": "00:00"
                })
        
        # Serialize the final data
        serializer = MonthlyAttendenceSerializer(final_data, many=True)
        
        valid_time = time(9, 45)

        # Count records where clock_in > 9:30 AM
        valid_clock_in_count = sum(
            1 for record in serializer.data
            if record["clock_in"] and parse_time(record["clock_in"]) and parse_time(record["clock_in"]) > valid_time
        )
        
        return Response({"data": serializer.data, "late_count": valid_clock_in_count})
 
class OnDutyInRequest(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        request.data['userid'] = request.user.id
        
        serializer = OnDutyRequestSerializer(data = request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"OD Created"})
        return Response({"error":serializer.errors})




# ci_projects


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CIProjects
from .serializers import CIProjectsSerializer

#  ci_projects_files

from .models import CIProjectFile
from .serializers import CIProjectFileSerializer

class CIProjectFileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_files = CIProjectFile.objects.all()
        serializer = CIProjectFileSerializer(project_files, many=True)
        return Response(serializer.data)


    def post(self, request):
        # Set the `employee_id` field to the current authenticated user
        data = request.data
        data['employee_id'] = request.user.id

        # Validate and save the new project file
        serializer = CIProjectFileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Project file uploaded successfully!", "project_file": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, project_file_id):
        # Fetch the project file and update
        project_file = CIProjectFile.objects.filter(project_file_id=project_file_id, employee_id=request.user).first()
        if not project_file:
            return Response({"error": "File not found or you do not have permission to edit it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CIProjectFileSerializer(project_file, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "File updated successfully!", "project_file": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_file_id=None):
        if not project_file_id:
            return Response({"error": "Project file ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project_file = CIProjectFile.objects.get(pk=project_file_id)
            project_file.delete()
            return Response({"message": "Project file deleted successfully."}, status=status.HTTP_200_OK)
        except CIProjectFile.DoesNotExist:
            return Response({"error": "Project file not found."}, status=status.HTTP_404_NOT_FOUND)

from .models import My_Project

class My_projectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_files = My_Project.objects.all()
        serializer = My_ProjectSerializer(project_files, many=True)
        return Response(serializer.data)


    def post(self, request):
        # Set the `employee_id` field to the current authenticated user
        data = request.data
        data['employee_id'] = request.user.id

        # Validate and save the new project file
        serializer = My_ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Project file uploaded successfully!", "project_file": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, project_file_id):
        # Fetch the project file and ensure permission
        project_file = My_Project.objects.filter(project_file_id=project_file_id, employee_id=request.user.id).first()
        if not project_file:
            return Response({"error": "File not found or you do not have permission to edit it."}, status=status.HTTP_404_NOT_FOUND)

        serializer = My_ProjectSerializer(project_file, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "File updated successfully!",
                "project_file": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_file_id):
        # Ensure the project file exists and belongs to the user
        project_file = My_Project.objects.filter(project_file_id=project_file_id, employee_id=request.user.id).first()
        if not project_file:
            return Response({"error": "Project file not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        
        project_file.delete()
        return Response({"message": "Project file deleted successfully."}, status=status.HTTP_200_OK)
    

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


        

#task_view

class TaskView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
        return Response({"message": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
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
            return Response({'message': 'Task file deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
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
            return Response({'message': 'Task note deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
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

    def get(self, request):
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
            return Response({"message": "Role deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except CiStaffRole.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        


#  Shift & Scheduling

from .models import OfficeShift
from .serializers import OfficeShiftSerializer


class OfficeShiftView(APIView):
    permission_classes = [IsAuthenticated]

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
            return Response({"message": "Shift deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except OfficeShift.DoesNotExist:
            return Response({"error": "Shift not found"}, status=status.HTTP_404_NOT_FOUND)
        

#  Exit Employee 

from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import ci_employee_exit
from .serializers import ci_employee_exitSerializer

# GET & POST View
class CiEmployeeExitView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        exits = ci_employee_exit.objects.all()
        serializer = ci_employee_exitSerializer(exits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ci_employee_exitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, exit_id):
        try:
            exit_instance = ci_employee_exit.objects.get(exit_id=exit_id)
            exit_instance.delete()
            return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ci_employee_exit.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)


# Priti Designation - Core HR -


class CiDesignationViewSet(generics.GenericAPIView):
    serializer_class = CiDesignationSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CiDesignation.objects.all()

    def get(self, request, *args, **kwargs):
        designations = self.get_queryset()
        serializer = self.serializer_class(designations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        designation_id = request.data.get('designation_id')
        if CiDesignation.objects.filter(designation_id=designation_id).exists():
            return Response({'error': 'Designation ID already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Designation created successfully!", "ci_designations": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        designation = self.get_queryset().filter(pk=kwargs.get('pk')).first()
        if not designation:
            return Response({'error': 'Designation not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(designation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Designation Updated successfully!", "ci_designations": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        designation = self.get_queryset().filter(pk=kwargs.get('pk')).first()
        if not designation:
            return Response({'error': 'Designation not found'}, status=status.HTTP_404_NOT_FOUND)
        designation.delete()
        return Response({'message': 'Designation deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class CIPolicyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        policies = Policy.objects.all()
        serializer = PolicySerializer(policies, many=True)
        return Response({"message": "Policies retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
 
    def post(self, request):
 
        try:
            file_obj = request.FILES.get("attachment")  # ✅ Correct way to get uploaded file
       
            if not file_obj or not hasattr(file_obj, 'name'):
                return Response({"status": "error", "message": "No valid file uploaded"}, status=400)
       
            upload_dir = os.path.join(settings.MEDIA_ROOT, "policies")
            os.makedirs(upload_dir, exist_ok=True)
       
            destination_path = os.path.join(upload_dir, file_obj.name)
       
            with default_storage.open(destination_path, "wb+") as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
       
            return Response({"status": "success", "message": "Attachment saved successfully"}, status=status.       HTTP_200_OK)
       
        except Exception as e:
            return Response({"status": "error", "message": f"An error occurred: {str(e)}"}, status=status.      HTTP_500_INTERNAL_SERVER_ERROR)
       
       
 
        serializer = PolicySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Policy created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Failed to create policy", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    def patch(self, request, pk):
        try:
            policy = Policy.objects.get(pk=pk)
        except Policy.DoesNotExist:
            return Response({"message": "Policy not found"}, status=status.HTTP_404_NOT_FOUND)
       
        serializer = PolicySerializer(policy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Policy updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Failed to update policy", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pk):
        try:
            policy = Policy.objects.get(pk=pk)
            policy.delete()
            return Response({"message": "Policy deleted successfully"}, status=status.HTTP_200_OK)
        except Policy.DoesNotExist:
            return Response({"message": "Policy not found"}, status=status.HTTP_404_NOT_FOUND)


class AnnouncementListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
 
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
 
    def get(self, request):
        announcements = self.get_queryset()
        serializer = self.get_serializer(announcements, many=True)
        return Response({"message": "Announcements retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
 
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Announcement created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Failed to create announcement", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
# ✅ GET a single announcement, PATCH (update), and DELETE by ID (Authenticated)
class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
 
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    lookup_field = 'announcement_id'
 
    def get(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"message": "Announcement retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
 
    def patch(self, request, pk):
        try:
            announcement = Announcement.objects.get(pk=pk)
        except Announcement.DoesNotExist:
            return Response({"message": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)
 
        serializer = AnnouncementSerializer(announcement, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Announcement updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "Failed to update announcement", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pk):
        try:
            announcement = Announcement.objects.get(pk=pk)
            announcement.delete()
            return Response({"message": "Announcement deleted successfully"}, status=status.HTTP_200_OK)
        except Announcement.DoesNotExist:
            return Response({"message": "Announcement not found"}, status=status.HTTP_404_NOT_FOUND)


class DepartmentView(APIView):

    # GET: Retrieve all departments
    def get(self, request, format=None):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    # POST: Create a new department
    def post(self, request, format=None):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH: Update a specific department (Partial Update)
    def patch(self, request, pk, format=None):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            raise Http404  # Return 404 if not found

        serializer = DepartmentSerializer(department, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Delete a specific department
    def delete(self, request, pk, format=None):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

        department.delete()
        return Response({"message": "Department deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



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

# GET all employee basic info (no emp_id needed)
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



###Events (Appssection) ####
class EventViewSet(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response (serializer.data, status=status.HTTP_200_OK)
   
    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response({"This Method is not working"}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, event_id=None, *args, **kwargs):
        event = get_object_or_404(Event, event_id=event_id)
        event.delete()
        return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
 
 
 
###Holidays (AppSection)###
class HolidayViewSet(APIView):
    def get(self, request, *args, **kwargs):
        holidays = Holiday.objects.all().order_by('start_date')
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, *args, **kwargs):
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def put(self, request, holiday_id=None, *args, **kwargs):
        holiday = get_object_or_404(Holiday, pk=holiday_id)
        serializer = HolidaySerializer(holiday, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, holiday_id=None, *args, **kwargs):
        holiday = get_object_or_404(Holiday, pk=holiday_id)
        holiday.delete()
        return Response({"message": "Holiday deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



# Travels
from .models import CITravel
from .serializers import CITravelSerializer
from django.shortcuts import get_object_or_404
 
class CITravelAPIView(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self, request, travel_id=None):
        if travel_id:
            travel = get_object_or_404(CITravel, travel_id=travel_id)
            serializer = CITravelSerializer(travel)
            return Response({'message': 'Travel fetched successfully', 'data': serializer.data})
        else:
            travels = CITravel.objects.all()
            serializer = CITravelSerializer(travels, many=True)
            return Response({'message': 'All travels fetched successfully', 'data': serializer.data})
 
    def post(self, request):
        serializer = CITravelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Travel created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Error creating travel', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    def patch(self, request, travel_id):
        travel = get_object_or_404(CITravel, travel_id=travel_id)
        serializer = CITravelSerializer(travel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Travel updated successfully', 'data': serializer.data})
        return Response({'message': 'Error updating travel', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, travel_id):
        travel = get_object_or_404(CITravel, travel_id=travel_id)
        travel.delete()
        return Response({'message': 'Travel deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
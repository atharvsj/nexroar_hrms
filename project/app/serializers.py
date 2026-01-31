from datetime import date, datetime, time
from django.utils import timezone
import bcrypt
import pytz
from rest_framework import serializers
from .models import BiomatricDataTemp, ERPUser, ERPUserDetails, LeaveApplication, NewTableLeave,Task, TaskDiscussion, TaskFile
from .models import  TaskNote, ErpUser1, CiStaffRole, Announcement, Department,  CiDesignation,Policy,  CiBiomatricData, CIPunchReport, ContractOption
from .models import Event, Holiday
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_datetime
import requests


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # Check if username and password are provided
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")

        try:
            # Retrieve the user by username
            user = ERPUser.objects.get(username=username)
           # print(f"User found: {user}")  # Debug: check if the user is found
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        # print('user.password: ', user.password)  # Debug: Check the stored hashed password
        
        # Check if the password is correct using check_password
       # print(password )
       # print(user.password)
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_pw.decode('utf-8')  # Save as string

       
        # if not check_password(password, user.password):  # Corrected condition
           # print(f"Password incorrect for user: {username}")  # Debug: Check password validation
            raise serializers.ValidationError("Invalid credentials.")
        
        

        # If authentication is successful, return the user object
        data['user'] = user
        
        return data
    
    class Meta:
        model = ERPUser
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}} 
        
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True)
    
    def validate_username(self, value):
        # Custom validation for username field
        if ERPUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    # Field-wise validation for the email
    def validate_email(self, value):
        # Custom validation for email field
        if ERPUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value
    
    def create(self, validated_data):
        # Hash the password before saving the user
        password = validated_data.pop('password')
        hashed_password = make_password(password)
        
        # Create the user instance
        user = ERPUser(
            username=validated_data['username'],
            email=validated_data['email'],
            password=hashed_password,
            user_role_id=validated_data['user_role_id'],
            company_id=validated_data['company_id'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            middle_name=validated_data.get('middle_name', ''),
            profile_photo=validated_data.get('profile_photo'),
            gender=validated_data.get('gender'),
            custome_unique_id=validated_data.get('custome_unique_id'),
        )
        
        # Save the user to the database
        user.save()
        
        return user

    class Meta:
        model = ERPUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'middle_name', 'user_role_id', 'company_id', 'profile_photo', 'gender', 'custome_unique_id']    
                
class ApplyLeaveSerializer(serializers.ModelSerializer):
    leave_type = serializers.CharField(required=True)  # Ensure `leave_type` is provided
    
    class Meta:
        model = LeaveApplication
        fields = ('employee_id', 'from_date', 'to_date', 'reason', 'remarks', 'leave_attachment', 'leave_type')

    def validate_employee_id(self, value):
        if not value:
            raise serializers.ValidationError("Employee ID is required.")
        return value

    def validate(self, attrs):
        if attrs['from_date'] < date.today():
            raise serializers.ValidationError({"from_date": "From date cannot be in the past."})
        if attrs["to_date"] < attrs["from_date"]:
            raise serializers.ValidationError({"to_date": "To date cannot be earlier than from date."})
        return attrs

    def create(self, validated_data):
        # Fetch the leave type ID from NewTableLeave
        leave = NewTableLeave.objects.filter(leave_type=validated_data['leave_type']).values('leave_id').first()
        if not leave:
            raise serializers.ValidationError({'leave_type': 'Invalid leave type.'})

        # Create the LeaveApplication instance
        leave_application = LeaveApplication.objects.create(
            company_id=1,  # Replace with a dynamic value if needed
            employee_id=validated_data['employee_id'],
            leave_type_id=leave['leave_id'],
            from_date=validated_data['from_date'],
            to_date=validated_data['to_date'],
            reason=validated_data['reason'],
            remarks=validated_data['remarks'],
            status=1,  # Replace with a dynamic value if needed
            is_half_day=0,  # Replace with a dynamic value if needed
            leave_attachment=validated_data.get('leave_attachment', '')  # Optional
        )
        return leave_application
       
class ERPUSerDetailsSeialzer(serializers.ModelSerializer):
    class Meta:
        model = ERPUserDetails
        fields = "__all__"
        
class ERPUserSerializer(serializers.ModelSerializer):
    details = ERPUSerDetailsSeialzer(source="erpuserdetails_set", many=True)
    
    def validate(self, attrs):
        if attrs['password']:
            raise serializers.ValidationError({"password":"This api is not used for password"})

    class Meta:
        model = ERPUser
        fields = "__all__"

    def update(self, instance, validated_data):
        # Extract and remove nested 'details' data
        details_data = validated_data.pop('erpuserdetails_set', [])

        # Update the ERPUser instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create related ERPUserDetails records
        for detail_data in details_data:
            ERPUserDetails.objects.update_or_create(
                user_id=instance.id,  # Ensure this matches your ForeignKey field in ERPUserDetails
                defaults=detail_data
            )

        return instance        


class ChangePasswordSerializers(serializers.ModelSerializer):
    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError({"password": "Field is required"})
        return value

    class Meta:
        model = ERPUser
        fields = ["password"]

    def update(self, instance, validated_data):
        # Hash the new password
        password_bytes = validated_data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        # Update the password field in the instance
        instance.password = hashed_password
        instance.save()  # Save the instance to persist changes
        return instance
    
    
class TodayAttendenceSerializers(serializers.ModelSerializer):
    late_by = serializers.SerializerMethodField()
    early_leaving_by = serializers.SerializerMethodField()

    def get_late_by(self, obj):
        
    
        if obj.clock_in:  # Ensure clock_in is not None
            try:
                # Parse clock_in as a time object
                clock_in = datetime.strptime(obj.clock_in, "%Y-%m-%d %H:%M:%S.%f").time()
                print("Parsed clock_in: ", clock_in)

                # Comparison with 9:30 AM
                comparison_time = time(9, 30, 0)
                print("Comparison time: ", comparison_time)

                if clock_in > comparison_time:
                    late_duration = (
                        datetime.combine(datetime.min, clock_in) - 
                        datetime.combine(datetime.min, comparison_time)
                    )
                    print("Late duration in seconds: ", late_duration.seconds)
                    return round(((late_duration.seconds)/60),2)  # Return late duration in seconds
                else:
                    print("Clock-in is on time or early.")
            except ValueError as e:
                print("Error parsing clock_in:", e)
        return 00

    def get_early_leaving_by(self, obj):
        """Calculate the early leaving duration if clock_out is before 6:30 PM."""
        if obj.clock_out:  # Ensure clock_out is not None
            clock_out = datetime.strptime(obj.clock_out, "%Y-%m-%d %H:%M:%S.%f").time()
            if clock_out < time(18, 30,00):
                early_leaving_duration = (
                    datetime.combine(datetime.min, time(18, 30)) - 
                    datetime.combine(datetime.min, clock_out)
                )
                return round(((early_leaving_duration.seconds)/60),2)  # Return early leaving duration in seconds
        return 00

    class Meta:
        model = BiomatricDataTemp
        fields = [
            "emp_id",
            "attendance_date",
            "attendance_status",
            "clock_in",
            "status",
            "clock_out",
            "late_by",
            "early_leaving_by",
        ]
        
class MonthlyAttendenceSerializer(serializers.ModelSerializer):
    attendance_date = serializers.DateField()
    count = serializers.IntegerField()
    class Meta:
        model = BiomatricDataTemp
        
        fields = [
            'emp_id',
            "attendance_date",
           "attendance_status",
            "count" ,
              'clock_in'
            
        ]
        
        
class OnDutyRequestSerializer(serializers.ModelSerializer):
    def validate_from_od(self, attrs):
        if attrs == 'N' or not attrs:
            raise serializers.ValidationError({"error": "This API is only for from_od is Y or from_od is required"})
        return attrs
    
    def validate_state_in_out(self, value):
        if not value:
            raise serializers.ValidationError({"state_in_out": "Field is empty"})
        return value
             
    def create(self, validated_data):
        user_id = validated_data.get("userid").id  # Safely retrieve the user ID
        if user_id:
            # Ensure user_id is numeric before querying
            user = ERPUserDetails.objects.filter(user_id=user_id).first()
            if user:
                emp_id = user.employee_id
                validated_data["emp_id"] = emp_id
        
        if validated_data.get("state_in_out") == "in":
            utc_time = timezone.now()

    # Convert to local timezone
            local_timezone = pytz.timezone('Asia/Kolkata')  # Replace with your timezone
            local_time = utc_time.astimezone(local_timezone)

            # Format the time to include milliseconds
            formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S.000")
            validated_data["clock_in"] = formatted_time
            validated_data["clock_out"] = "" 
            
            response = requests.get('https://ipinfo.io')
            data = response.json()

            # Extract latitude and longitude
            location = data.get('loc')  # Ensure safe extraction
            validated_data["clock_in_location"] = location or "Unknown Location"
            validated_data["clock_out_location"] = ""
        if validated_data.get("state_in_out") == "out":
            utc_time = timezone.now()

    # Convert to local timezone
            local_timezone = pytz.timezone('Asia/Kolkata')  # Replace with your timezone
            local_time = utc_time.astimezone(local_timezone)

            # Format the time to include milliseconds
            formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S.000")
            validated_data["clock_in"] = ""
            validated_data["clock_out"] = formatted_time 
            
            response = requests.get('https://ipinfo.io')
            data = response.json()

            # Extract latitude and longitude
            location = data.get('loc')  # Ensure safe extraction
            validated_data["clock_out_location"] = location or "Unknown Location"
            validated_data["clock_in_location"] = ""
        
        return super().create(validated_data)
                
    class Meta:
        model = BiomatricDataTemp
        fields = [
            "emp_id",  # calculated
            "userid",  # from token
            # "login_date"
            "clock_in",  # default
            "clock_in_location",  # default
            "clock_out",  # default
            "clock_out_location",  # default
            "state_in_out",  # pass
            "reason",  # pass
            "from_od",  # pass
            "wfh"  # calculated
        ]
        
        extra_kwargs = {
            "emp_id": {"read_only": True},
            "clock_in": {"read_only": True},
            "clock_in_location": {"read_only": True},
            "clock_out": {"read_only": True},
            "clock_out_location": {"read_only": True},
        }




from rest_framework import serializers
from .models import CIProjects

class CIProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIProjects
        fields = '__all__'
        read_only_fields = ['added_by']


# files

from .models import CIProjectFile

class CIProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIProjectFile
        fields = '__all__'



# ci_projects_bugs

from .models import CIProjectBug

class CIProjectBugSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIProjectBug
        fields = '__all__'



class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskDiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDiscussion
        fields = '__all__'


class TaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFile
        fields = '__all__'


class TaskNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskNote
        fields = '__all__'



class CIPunchReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIPunchReport
        fields = '__all__'




class ErpUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErpUser1
        fields = ['user_id', 'user_role_id', 'user_type', 'company_id', 'first_name', 'middle_name', 'last_name', 
                  'email', 'username', 'password', 'company_name', 'trading_name', 'registration_no', 'government_tax', 
                  'company_type_id', 'profile_photo', 'contact_number', 'gender', 'address_1', 'address_2', 'city', 
                  'state', 'zipcode', 'country', 'last_login_date', 'last_logout_date', 'last_login_ip', 'is_logged_in', 
                  'is_active', 'created_at', 'custome_unique_id']

# Roles & Privileges

class CiStaffRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CiStaffRole
        fields = '__all__'

#  Shift & Scheduling

from .models import OfficeShift

class OfficeShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficeShift
        fields = '__all__'


# Exit Employee 

from rest_framework import serializers
from .models import ci_employee_exit

class ci_employee_exitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ci_employee_exit
        fields = '__all__'


class CiDesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CiDesignation
        fields = '__all__'

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
 
    class Meta:
        model = Announcement
        fields = '__all__'
 
    def get_created_at(self, obj):
        """Ensure created_at is always returned as a proper datetime object."""
        if isinstance(obj.created_at, str):  # If it's stored as a string, convert it
            return parse_datetime(obj.created_at)
        return obj.created_at  # Otherwise, return it as is



class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'  # Include all fields in the response
    def get_created_at(self, obj):
        if isinstance(obj.created_at, str):  # If it's a string, convert it
            return parse_datetime(obj.created_at)
        return obj.created_at  # Otherwise, return as is
    

class CiBiomatricDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CiBiomatricData
        fields = '__all__'


class ContractOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractOption
        fields ='__all__'




from rest_framework import serializers
from .models import BasicInformation

class BasicInformationSerializer(serializers.ModelSerializer):
    marital_status = serializers.SerializerMethodField()

    class Meta:
        model = BasicInformation
        fields = [
            'id',
            'first_name', 'middle_name', 'last_name',
            'contact_number', 'gender', 'emp_id',
            'date_of_birth', 'marital_status',
            'state', 'city', 'zipcode',
            'religion', 'bloodgroup',
            'nationality', 'citizenship',
            'address_1', 'address_2'
        ]

    def get_marital_status(self, obj):
        return 'single' if obj.marital_status == 0 else 'married'

    def to_internal_value(self, data):
        if 'marital_status' in data:
            if data['marital_status'].lower() == 'single':
                data['marital_status'] = 0
            elif data['marital_status'].lower() == 'married':
                data['marital_status'] = 1
        return super().to_internal_value(data)


#######Aditya Serializer :
from datetime import date, datetime, time
from django.utils import timezone
import bcrypt
import pytz
from rest_framework import serializers
from .models import  CIPunchReport, ContractOption,My_Project,AssignedTask
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_datetime
import requests




from rest_framework import serializers
from .models import My_Project

class My_ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = My_Project
        fields = '__all__'
        read_only_fields = ['added_by']


# files

from .models import My_Project

class My_ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = My_Project
        fields = '__all__'




class CIPunchReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIPunchReport
        fields = '__all__'






class ContractOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractOption
        fields ='__all__'




from rest_framework import serializers
from .models import BasicInformation

class BasicInformationSerializer(serializers.ModelSerializer):
    marital_status = serializers.SerializerMethodField()

    class Meta:
        model = BasicInformation
        fields = [
            'id',
            'first_name', 'middle_name', 'last_name',
            'contact_number', 'gender', 'emp_id',
            'date_of_birth', 'marital_status',
            'state', 'city', 'zipcode',
            'religion', 'bloodgroup',
            'nationality', 'citizenship',
            'address_1', 'address_2'
        ]

    def get_marital_status(self, obj):
        return 'single' if obj.marital_status == 0 else 'married'

    def to_internal_value(self, data):
        if 'marital_status' in data:
            if data['marital_status'].lower() == 'single':
                data['marital_status'] = 0
            elif data['marital_status'].lower() == 'married':
                data['marital_status'] = 1
        return super().to_internal_value(data)





class AssignedTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedTask
        fields = '__all__'

class AssignedTaskDetailView(serializers.ModelSerializer):
    class Meta : 
        model = AssignedTask
        fields = '__all__'




class EventSerializer(serializers.ModelSerializer):
    class Meta :
        model = Event
        fields = '__all__'
 
 
 
 
 
class HolidaySerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
 
    class Meta:
        model = Holiday
        fields = '__all__'
 
    def get_status(self, obj):
        return "Published" if obj.is_publish else "Restricted"



from .models import CITravel
 
class CITravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CITravel
        fields = '__all__'
        extra_kwargs = {
            'travel_id': {'read_only': True}
        }

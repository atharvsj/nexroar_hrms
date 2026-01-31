from datetime import date, datetime, time
from django.utils import timezone
import bcrypt
import pytz
from rest_framework import serializers
from .models import BiomatricDataTemp, ERPUser, ERPUserDetails, TaskDiscussion, TaskFile, User
from .models import  TaskNote, ErpUser1, CiStaffRole, CiBiomatricData, CIPunchReport, ContractOption
from .models import  Holiday, CITraining,  BasicInformation
from .models import  CIPunchReport, ContractOption,AssignedTask
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_datetime
import requests
from rest_framework import serializers
from django.conf import settings
from .models import YourMediaModel  # change this to your actual model


import hashlib
from django.contrib.auth.hashers import check_password, identify_hasher
from django.core.exceptions import ValidationError as DjangoValidationError




class MediaUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourMediaModel
        fields = ['file']

    def validate_file(self, value):
        if value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError("File too large. Maximum allowed size is 5 MB.")
        return value


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(write_only=True, required=True)

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')

#         # Check if username and password are provided
#         if not username or not password:
#             raise serializers.ValidationError("Username and password are required.")

#         try:
#             # Retrieve the user by username
#             user = ERPUser.objects.get(username=username)
#            # print(f"User found: {user}")  # Debug: check if the user is found
#         except ERPUser.DoesNotExist:
#             raise serializers.ValidationError("Invalid credentials.")
        
#         # print('user.password: ', user.password)  # Debug: Check the stored hashed password
        
#         # Check if the password is correct using check_password
#        # print(password )
#        # print(user.password)
#         if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
#             hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#             user.password = hashed_pw.decode('utf-8')  # Save as string

       
#         # if not check_password(password, user.password):  # Corrected condition
#            # print(f"Password incorrect for user: {username}")  # Debug: Check password validation
#             raise serializers.ValidationError("Invalid credentials.")
        
        

#         # If authentication is successful, return the user object
#         data['user'] = user
        
#         return data
    
#     class Meta:
#         model = ERPUser
#         fields = ['username', 'password']
#         extra_kwargs = {'password': {'write_only': True}} 



# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(write_only=True, required=True)
 
#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')
 
#         # Check if username and password are provided
#         if not username or not password:
#             raise serializers.ValidationError("Username and password are required.")
 
#         try:
#             # Retrieve the user by username
#             # user = ERPUser.objects.get(username=username)
#             user = ERPUser.objects.get(username__exact=username)
 
#            # print(f"User found: {user}")  # Debug: check if the user is found
#         except ERPUser.DoesNotExist:
#             raise serializers.ValidationError("Invalid credentials.")
       
       
#         if user.username != username:
#             raise serializers.ValidationError("Invalid credentials.")
       
#         # print('user.password: ', user.password)  # Debug: Check the stored hashed password
       
#         # Check if the password is correct using check_password
#        # print(password )
#        # print(user.password)
#         if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
#             hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#             user.password = hashed_pw.decode('utf-8')  # Save as string
 
       
#         # if not check_password(password, user.password):  # Corrected condition
#            # print(f"Password incorrect for user: {username}")  # Debug: Check password validation
#             raise serializers.ValidationError("Invalid credentials.")
       
       
 
#         # If authentication is successful, return the user object
#         data['user'] = user
       
#         return data



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
            user = ERPUser.objects.get(username__exact=username)
        except ERPUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        # 🔹 Check if the employee is active
        if user.is_active == 0:
            raise serializers.ValidationError("Your account is deactivated. Please contact HR.")

        # Double-check username match
        if user.username != username:
            raise serializers.ValidationError("Invalid credentials.")

        # 🔹 Verify the password using bcrypt
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            raise serializers.ValidationError("Invalid credentials.")

        # If authentication is successful, return the user object
        data['user'] = user
        return data




# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(write_only=True, required=True)

#     def validate(self, data):
#         username = data.get("username")
#         password = data.get("password")

#         if not username or not password:
#             raise serializers.ValidationError("Username and password are required.")

#         try:
#             user = ERPUser.objects.get(username=username)
#         except ERPUser.DoesNotExist:
#             raise serializers.ValidationError("Invalid credentials.")

#         stored_password = user.password.strip()

#         # Check if this is a known Django format
#         django_prefixes = (
#             "pbkdf2_sha256$", "pbkdf2_sha1$", "argon2$", "sha1$", "bcrypt_sha256$", "md5$", "unsalted_md5$", "crypt$"
#         )

#         try:
#             if stored_password.startswith(django_prefixes):
#                 # ✅ Standard Django password hash
#                 if check_password(password, stored_password):
#                     data["user"] = user
#                     return data

#             elif stored_password.startswith(("$2b$", "$2a$", "$2y$", "$12$")):
#                 # ✅ Raw bcrypt hash
#                 if bcrypt.checkpw(password.encode(), stored_password.encode()):
#                     data["user"] = user
#                     return data

#             else:
#                 # ❌ Unknown hash format — reject safely
#                 raise serializers.ValidationError("Unsupported password format. Please reset your password.")

#         except ValueError:
#             raise serializers.ValidationError("Corrupted password hash. Please reset your password.")
#         except Exception:
#             raise serializers.ValidationError("Invalid credentials.")

#         # ❌ Password didn't match
#         raise serializers.ValidationError("Invalid credentials.") 
        
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



class TodayAttendenceSerializers(serializers.Serializer):
    user_id = serializers.IntegerField()
    emp_name = serializers.CharField()
    attendance_date = serializers.DateField()
    attendance_status = serializers.CharField()
    punch_in_time = serializers.DateTimeField(allow_null=True)
        
        
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





# ci_projects_bugs

from .models import CIProjectBug

class CIProjectBugSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIProjectBug
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

class CIPunchReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CIPunchReport
        fields = '__all__'



class ContractOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractOption
        fields ='__all__'



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
 
 
 
 
class HolidaySerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
 
    class Meta:
        model = Holiday
        fields = '__all__'
 
    def get_status(self, obj):
        return "Published" if obj.is_publish else "Restricted"


class CITrainingSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    employee_names = serializers.SerializerMethodField()
 
    class Meta:
        model = CITraining
        fields = '__all__'
        extra_fields = ['trainer_name', 'employee_names']
 
    def get_trainer_name(self, obj):
        from .models import CITrainer
        try:
            trainer = CITrainer.objects.filter(trainer_id=obj.trainer_id).first()
            if trainer:
                return f"{trainer.first_name} {trainer.last_name}"
        except:
            pass
        return None
 
    def get_employee_names(self, obj):
        from .models import ERPUserDetails, ERPUser
        try:
            emp_ids = [eid.strip() for eid in obj.employee_id.split(',') if eid.strip().isdigit()]
            user_details = ERPUserDetails.objects.filter(employee_id__in=emp_ids)
            user_ids = user_details.values_list('user_id', flat=True)
            users = ERPUser.objects.filter(id__in=user_ids)
            return [f"{u.first_name} {u.last_name}" for u in users]
        except:
            return []
        


from .models import CITrainer
 
class CITrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CITrainer
        fields = '__all__'
 
    def validate_trainer_id(self, value):
        if self.instance is None and CITrainer.objects.filter(trainer_id=value).exists():
            raise serializers.ValidationError("Trainer ID already exists.")
        return value


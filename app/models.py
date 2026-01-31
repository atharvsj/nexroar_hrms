# from django.utils import timezone
# from datetime import datetime
# from django.db import models
# from django.contrib.auth.models import User
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# from django.db import models

# class YourMediaModel(models.Model):
#     file = models.FileField(upload_to='uploads/')



# # Create your models here.
# class StaffRole(models.Model):
#     role_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()                                              #Not Found
#     role_name = models.CharField(max_length=200)
#     role_access = models.CharField(max_length=200)
#     role_resources = models.TextField(null=True, blank=True)
#     created_at = models.CharField(max_length=200, null=True, blank=True)

#     class Meta:
#         db_table = 'ci_staff_roles'
#         verbose_name = 'Staff Role'
#         verbose_name_plural = 'Staff Roles'
#         managed = False  # Django will not manage this table

#     def __str__(self):
#         return self.role_name

# ####Aditya Code :
# # class BasicInformation (models.Model):
# #     GENDER_CHOICES = (
# #         ('M', 'Male'),
# #         ('F', 'Female'),
# #         ('O', 'Other'),
# #     )

# #     MARITAL_STATUS_CHOICES = (
# #         (0, 'Single'),
# #         (1, 'Married')

# #     )
# #     # id = models.IntegerField(null=True, blank=True)
# #     first_name = models.CharField(max_length=100)
# #     middle_name = models.CharField(max_length=100, blank=True, null=True)
# #     last_name = models.CharField(max_length=100)
# #     contact_number = models.CharField(max_length=20)
# #     gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
# #     emp_id = models.CharField(max_length=50)
# #     date_of_birth = models.DateField()
# #     marital_status = models.IntegerField(choices=MARITAL_STATUS_CHOICES)
# #     state = models.CharField(max_length=100)
# #     city = models.CharField(max_length=100)
# #     zipcode = models.CharField(max_length=10)
# #     religion = models.CharField(max_length=100)
# #     bloodgroup = models.CharField(max_length=5)
# #     nationality = models.CharField(max_length=100)
# #     citizenship = models.CharField(max_length=100)
# #     address_1 = models.TextField()
# #     address_2 = models.TextField(blank=True, null=True)
# #     profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
# #     def __str__(self):
# #         return f"{self.first_name}{self.last_name}"
    
# # class  Meta:
# #     db_table = '`ci_erp_users`'
# #     managed = False



# class ERPUserManager(BaseUserManager):
#     def create_user(self, username, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set.")
#         if not username:
#             raise ValueError("The Username field must be set.")
#         email = self.normalize_email(email)
#         user = self.model(username=username, email=email, **extra_fields)
#         user.set_password(password)  # Hash the password
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         return self.create_user(username, email, password, **extra_fields)

# class ERPUser(AbstractBaseUser, PermissionsMixin):
#     id = models.AutoField(primary_key=True, db_column='id')
#     user_role_id = models.ForeignKey(
#         StaffRole, 
#         on_delete=models.CASCADE,  # Handle deletion behavior
#         related_name='role',
#         db_column='user_role_id',  # Optional: reverse lookup name
#     )
#     user_type = models.CharField(max_length=50)
#     company_id = models.IntegerField()
#     first_name = models.CharField(max_length=255)
#     middle_name = models.CharField(max_length=100, null=True, blank=True)
#     last_name = models.CharField(max_length=255)
#     email = models.EmailField(max_length=255, unique=True)
#     username = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     company_name = models.CharField(max_length=100, null=True, blank=True)
#     trading_name = models.CharField(max_length=100, null=True, blank=True)
#     registration_no = models.CharField(max_length=100, null=True, blank=True)
#     government_tax = models.CharField(max_length=100, null=True, blank=True)
#     company_type_id = models.IntegerField()
#     profile_photo = models.CharField(max_length=255, null=True, blank=True)
#     contact_number = models.CharField(max_length=255, null=True, blank=True)
#     gender = models.CharField(max_length=20, null=True, blank=True)
#     address_1 = models.TextField(null=True, blank=True)
#     address_2 = models.TextField(null=True, blank=True)
#     city = models.CharField(max_length=255, null=True, blank=True)
#     state = models.CharField(max_length=255, null=True, blank=True)
#     zipcode = models.CharField(max_length=255, null=True, blank=True)
#     country = models.IntegerField()
#     last_login_date = models.CharField(max_length=255, null=True, blank=True)
#     last_logout_date = models.CharField(max_length=200, null=True, blank=True)
#     last_login_ip = models.CharField(max_length=255, null=True, blank=True)
#     is_logged_in = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     created_at = models.CharField(max_length=255, null=False,default=timezone.now())    
#     custome_unique_id = models.IntegerField(null=True, blank=True)
#     last_login = None
#     is_superuser = None
    
#     groups = None
#     user_permissions = None
    
#     objects = ERPUserManager()

#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['email']
    
#     class Meta:
#         db_table = 'ci_erp_users'
#         verbose_name = 'ERP User'
#         verbose_name_plural = 'ERP Users'
#         managed = False 

#     def __str__(self):
#         return self.username


# class ERPUserDetails(models.Model):
#     staff_details_id = models.AutoField(primary_key=True)
#     user_id = models.ForeignKey(
#         ERPUser, 
#         on_delete=models.CASCADE,  # Handle deletion behavior
#         related_name='erpuserdetails_set',  # Optional: reverse lookup name
#         db_column='user_id',
#     )
#     employee_id = models.CharField(max_length=255, null=True, blank=True)
#     department_id = models.IntegerField(null=True, blank=True, db_column='department_id')

    
#     designation_id = models.IntegerField()
#     manager = models.IntegerField()
#     office_shift_id = models.IntegerField()
#     basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
#     emp_ctc = models.CharField(max_length=100, null=True, blank=True)
#     hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
#     salay_type = models.IntegerField()
#     role_description = models.TextField(null=True, blank=True)
#     date_of_joining = models.CharField(max_length=200, null=True, blank=True)
#     date_of_leaving = models.CharField(max_length=200, null=True, blank=True)
#     date_of_birth = models.CharField(max_length=200, null=True, blank=True)
#     marital_status = models.IntegerField()
#     religion_id = models.IntegerField()
#     blood_group = models.CharField(max_length=200, null=True, blank=True)
#     citizenship_id = models.IntegerField()
#     bio = models.TextField(null=True, blank=True)
#     experience = models.IntegerField()
#     fb_profile = models.TextField(null=True, blank=True)
#     twitter_profile = models.TextField(null=True, blank=True)
#     gplus_profile = models.TextField(null=True, blank=True)
#     linkedin_profile = models.TextField(null=True, blank=True)
#     account_title = models.CharField(max_length=255, null=True, blank=True)
#     account_number = models.CharField(max_length=255, null=True, blank=True)
#     bank_name = models.CharField(max_length=255, null=True, blank=True)
#     iban = models.CharField(max_length=255, null=True, blank=True)
#     swift_code = models.CharField(max_length=255, null=True, blank=True)
#     bank_branch = models.TextField(null=True, blank=True)
#     ifsc_code = models.CharField(max_length=100, null=True, blank=True)
#     contact_full_name = models.CharField(max_length=200, null=True, blank=True)
#     contact_phone_no = models.CharField(max_length=200, null=True, blank=True)
#     contact_email = models.CharField(max_length=200, null=True, blank=True)
#     contact_address = models.TextField(null=True, blank=True)
#     created_at = models.CharField(max_length=200, null=True, blank=True)
#     probation = models.CharField(max_length=1, null=True, blank=True)
#     probation_end_date = models.CharField(max_length=255, null=True, blank=True)
#     pro_edit_permission = models.CharField(max_length=1, null=True, blank=True)
#     billing = models.CharField(max_length=1, null=True, blank=True)

#     class Meta:
#         db_table = 'ci_erp_users_details'
#         verbose_name = 'ERP User Detail'
#         verbose_name_plural = 'ERP User Details'
#         managed = False  # Django will not manage this table

#     def __str__(self):
#         return f"ERPUserDetails: {self.staff_details_id}"
    

# class PIErpUserDetails (models.Model):
#     #bio (bio,experience )
#     bio = models.CharField(max_length=100, null=True,blank=True)
#     experience = models.IntegerField()
#     #social Profile (facebook,twitter, Google Plus , linkedin )
#     fb_profile = models.TextField(max_length=100, null=True , blank=True)
#     twitter_profile = models.TextField(max_length=100, null=True , blank=True)
#     gplus_profile = models.TextField(max_length=100, null=True , blank=True)
#     linkedin_profile = models.TextField(max_length=100, null=True , blank=True)
#     #bank acc (acc title , acc num , bank name , IBAN,swift code ,bank Branch )
#     account_title = models.CharField(max_length=100 , null=True , blank=True)
#     account_number = models.IntegerField(null=True , blank=True)
#     bank_name = models.CharField(max_length=200 , null=True, blank=True)
#     iban = models.CharField(max_length=100 , null=True, blank=True)
#     swift_code = models.CharField(max_length=100, null=True , blank=True)
#     bank_branch = models.TextField(max_length=100, null=True, blank=True)

#     #emg contact (full name,contact number )
#     contact_full_name = models.CharField(max_length=100, null=True , blank=True)
#     contact_phone_no = models.IntegerField(null=True , blank=True)
#     contact_email = models.EmailField(max_length=100 , null=True , blank=True)
#     contact_address = models.CharField(max_length=100 , null=True , blank=True)

#     def __str__(self):
#         return f"ErpUserDetails:{self.staff_details_id}"
    
# class Meta:
#     db_table = 'ci_erp_users_details'
#     managed = False




# class BiomatricDataTemp(models.Model):
#     ci_biomatric_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key (INT)
#     emp_id = models.CharField(max_length=50)  # VARCHAR(50)
#     userid = models.ForeignKey(
#         ERPUser, 
#         on_delete=models.CASCADE,  # Handle deletion behavior
#         # related_name='erpuserdetails_set',  # Optional: reverse lookup name
#         db_column='userid',
#     )
#     login_date = models.CharField(max_length=100,default=timezone.now().today,
#                                    db_column='login_date',)  # VARCHAR(100)
#     clock_in = models.CharField(max_length=100)  # VARCHAR(100)
#     clock_in_location = models.CharField(max_length=100)  # VARCHAR(100)
#     clock_out = models.CharField(max_length=100)  # VARCHAR(100)
#     clock_out_location = models.CharField(max_length=100)  # VARCHAR(100)
#     state_in_out = models.CharField(max_length=100)  # VARCHAR(100)
#     late_mark = models.CharField(max_length=100)  # VARCHAR(100)
#     early_mark = models.CharField(max_length=100, default='0')  # VARCHAR(100)
#     total_work = models.CharField(max_length=100, default='0')  # VARCHAR(100)
#     attendance_date = models.DateField(db_column='attendance_date',  )  # VARCHAR(100)
#     attendance_status = models.CharField(max_length=100,default="Present",
#                                        db_column='attendance_status',  )  # VARCHAR(100)
#     status = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], default='Y')  # ENUM(1)
#     from_od = models.CharField(max_length=2, choices=[('Y', 'Yes'), ('N', 'No')], default='N')  # ENUM(2)
#     reason = models.CharField(max_length=200, blank=True, null=True)  # VARCHAR(200)
#     wfh = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], default='N')  # ENUM(1)

#     def __str__(self):
#         return f"Biometric Data for Employee ID {self.emp_id}"

#     class Meta:
#         db_table = 'ci_biomatric_data'  # Specifies the table name
#         managed = False





# # 1. ci_projects

# from django.db import models

# class CIProjects(models.Model):
#     project_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     client_id = models.IntegerField()
#     title = models.CharField(max_length=255)
#     start_date = models.CharField(max_length=255)
#     end_date = models.CharField(max_length=255)
#     assigned_to = models.TextField()
#     associated_goals = models.TextField()
#     priority = models.CharField(max_length=255)
#     project_no = models.CharField(max_length=255)
#     budget_hours = models.CharField(max_length=255)
#     summary = models.TextField()
#     description = models.TextField()
#     project_progress = models.CharField(max_length=255)
#     project_note = models.TextField()
#     status = models.BooleanField(default=True)
#     added_by = models.IntegerField()
#     created_at = models.CharField(max_length=255)

#     class Meta:
#         db_table = 'ci_projects'




# #  2.ci_project_file

# from django.db import models

# class CIProjectFile(models.Model):
#     project_file_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     project_id = models.IntegerField()
#     employee_id = models.IntegerField()
#     file_title = models.CharField(max_length=255)
#     attachment_file = models.FileField(upload_to='attachments/', blank=True, null=True)
#     created_at = models.CharField(max_length=200)

#     class Meta:
#         db_table = 'ci_projects_files'
  

# #####Aditya Code :###


# #3. ci_projects_bugs

# from django.db import models



# class CIProjectBug(models.Model):
#     project_bug_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     project_id = models.IntegerField()
#     employee_id = models.IntegerField()
#     bug_note = models.TextField()
#     created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     class Meta:
#         db_table = 'ci_projects_bugs'



# class Company(models.Model):
#     name = models.CharField(max_length=255)

#     def __str__(self):
#         return self.name

# class Project(models.Model):
#     name = models.CharField(max_length=255)
#     company = models.ForeignKey(Company, related_name='projects', on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name



# ###code2 uncomment this if theres any error related to this field

# class AssignedTask(models.Model):
#     task_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     project_id = models.IntegerField()
#     task_name = models.CharField(max_length=255)
#     assigned_to = models.CharField(max_length=100)
#     associated_goals = models.TextField(blank=True, null=True)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     task_hour = models.DecimalField(max_digits=5, decimal_places=2)
#     task_progress = models.DecimalField(max_digits=5, decimal_places=2)
#     summary = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     task_status = models.IntegerField()
#     task_note = models.TextField(blank=True, null=True)
#     created_by = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.task_name
    
#     class Meta:
#          db_table = 'ci_tasks'
#          managed = False
      


# class TaskDiscussion(models.Model):
#     task_discussion_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     task_id = models.IntegerField()
#     #employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
#     employee_id =  models.IntegerField()
#     discussion_text = models.TextField()
#     created_at = models.CharField(max_length=255)

#     def __str__(self):
#         return f"TaskDiscussion {self.task_discussion_id}"
    
#     class Meta:
#         db_table = 'ci_tasks_discussion'
#         verbose_name = 'Discusion Text'
#         verbose_name_plural = 'Discusion Texts'
#         managed = False 


# class TaskFile(models.Model):
#     task_file_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     task_id = models.IntegerField()
#     employee_id = models.IntegerField()  # Use an IntegerField for employee_id if not linking to a model
#     file_title = models.CharField(max_length=255)
#     attachment_file = models.FileField(upload_to='attachments/')  # Ensure MEDIA_URL and MEDIA_ROOT are configured
#     created_at = models.CharField(max_length=200)
#     def __str__(self):
#         return self.file_title
    
#     class Meta:
#         db_table = 'ci_tasks_files'
#         verbose_name = 'File Title'
#         verbose_name_plural = 'File Titles'
#         managed = False 


# class TaskNote(models.Model):
#     task_note_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     task_id = models.IntegerField()
#     employee_id = models.IntegerField()  # Use IntegerField if not linking to another model
#     task_note = models.TextField()
#     created_at = models.CharField(max_length=255)

#     def __str__(self):
#         return f"TaskNote {self.task_note_id}: {self.task_note[:50]}"
    
#     class Meta:
#         db_table = 'ci_tasks_notes'
#         verbose_name = 'Task Note'
#         verbose_name_plural = 'Task Notes'
#         managed = False 



# class CIPunchReport(models.Model):
#     punch_id = models.AutoField(primary_key=True)
#     email = models.EmailField()
#     empid = models.CharField(max_length=50)
#     userid = models.CharField(max_length=50)
#     punch_in_location = models.CharField(max_length=255)
#     punchdate = models.DateField()
#     punch_in_time = models.CharField(max_length=100)
#     punch_out_time = models.CharField(max_length=100)
#     punch_out_location = models.CharField(max_length=255, blank=True, null=True)

#     def __str__(self):
#         return f"{self.empid} - {self.punchdate}"
    
#     class Meta:
#         db_table = 'ci_punch_report'
#         managed = False
 


# class ErpUser1(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     user_role_id = models.IntegerField()
#     user_type = models.CharField(max_length=50)
#     company_id = models.IntegerField()
#     first_name = models.CharField(max_length=255)
#     middle_name = models.CharField(max_length=255, null=True, blank=True)
#     last_name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     company_name = models.CharField(max_length=255)
#     trading_name = models.CharField(max_length=255, null=True, blank=True)
#     registration_no = models.CharField(max_length=255, null=True, blank=True)
#     government_tax = models.CharField(max_length=255, null=True, blank=True)
#     company_type_id = models.IntegerField()
#     profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
#     contact_number = models.CharField(max_length=15)
#     gender = models.CharField(max_length=10)
#     address_1 = models.CharField(max_length=255)
#     address_2 = models.CharField(max_length=255, null=True, blank=True)
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     zipcode = models.CharField(max_length=20)
#     country = models.CharField(max_length=100)
#     last_login_date = models.DateTimeField(null=True, blank=True)
#     last_logout_date = models.DateTimeField(null=True, blank=True)
#     last_login_ip = models.GenericIPAddressField(null=True, blank=True)
#     is_logged_in = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     custome_unique_id = models.CharField(max_length=255, unique=True)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"

#     class Meta:
#         db_table = 'ci_erp_users'



# # Roles & Privileges 
# from django.db import models
# class CiStaffRole(models.Model):
#     role_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     role_name = models.CharField(max_length=200)
#     role_access = models.CharField(max_length=200)
#     role_resources = models.TextField()
#     created_at = models.CharField(max_length=200)

#     # def __str__(self):
#     #     return self.role_name

#     class Meta:
#         db_table = 'ci_staff_roles'


# #  Shift & Scheduling 

# class OfficeShift(models.Model):
#     office_shift_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     shift_name = models.CharField(max_length=255)
#     monday_in_time = models.CharField(max_length=222)
#     monday_out_time = models.CharField(max_length=222)
#     tuesday_in_time = models.CharField(max_length=222)
#     tuesday_out_time = models.CharField(max_length=222)
#     wednesday_in_time = models.CharField(max_length=222)
#     wednesday_out_time = models.CharField(max_length=222)
#     thursday_in_time = models.CharField(max_length=222)
#     thursday_out_time = models.CharField(max_length=222)
#     friday_in_time = models.CharField(max_length=222)
#     friday_out_time = models.CharField(max_length=222)
#     saturday_in_time = models.CharField(max_length=222)
#     saturday_out_time = models.CharField(max_length=222)
#     sunday_in_time = models.CharField(max_length=222)
#     sunday_out_time = models.CharField(max_length=222)
#     created_at = models.CharField(max_length=222)

#     class Meta:
#         db_table = 'ci_office_shifts'





# class CiBiomatricData(models.Model):
#     ci_biomatric_id = models.AutoField(primary_key=True)
#     emp_id = models.CharField(max_length=50)
#     userid = models.CharField(max_length=50)
#     login_date = models.DateField()
#     clock_in = models.TimeField(null=True, blank=True)
#     clock_in_location = models.CharField(max_length=255, null=True, blank=True)
#     clock_out = models.TimeField(null=True, blank=True)
#     clock_out_location = models.CharField(max_length=255, null=True, blank=True)
#     state_in_out = models.CharField(max_length=50, null=True, blank=True)
#     late_mark = models.BooleanField(default=False)
#     early_mark = models.BooleanField(default=False)
#     total_work = models.DurationField(null=True, blank=True)
#     attendance_date = models.DateField()
#     attendance_status = models.CharField(max_length=50)
#     status = models.CharField(max_length=50)
#     from_od = models.CharField(max_length=1, choices=[("Y", "Yes"), ("N", "No")], default="N")

#     reason = models.TextField(null=True, blank=True)

#     class Meta:
#         db_table = "ci_biomatric_data"
#         managed = False 


#     def __str__(self):
#         return f"Biometric Record {self.ci_biomatric_id} - {self.userid}"




# #16-04-2025

# from django.db import models

# class ContractOption(models.Model):
#     contract_date = models.DateField()
#     billing = models.CharField(max_length=10, choices=[("Yes", "Yes"), ("No", "No")])
#     department = models.CharField(max_length=100)
#     designation = models.CharField(max_length=100)
#     basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
#     hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
#     payslip_type = models.CharField(max_length=20)
#     office_shift = models.CharField(max_length=50)
#     contract_end = models.DateField(null=True, blank=True)
#     probation = models.BooleanField(default=False)
#     manager = models.CharField(max_length=100)
#     profile_edit_permission = models.BooleanField(default=False)
#     role_description = models.TextField(blank=True)

#     def __str__(self):
#         return f"{self.designation} ({self.department})"
    
# class Meta:
#     db_table='ci_contract_options'




# from django.db import models

# class BasicInformation(models.Model):
#     GENDER_CHOICES = (
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('O', 'Other'),
#     )

#     MARITAL_STATUS_CHOICES = (
#         (0, 'Single'),
#         (1, 'Married'),
#     )

#     first_name = models.CharField(max_length=100)
#     middle_name = models.CharField(max_length=100, blank=True, null=True)
#     last_name = models.CharField(max_length=100)
#     contact_number = models.CharField(max_length=20)
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
#     users_id = models.CharField(max_length=50)
#     date_of_birth = models.DateField()
#     marital_status = models.IntegerField(choices=MARITAL_STATUS_CHOICES)
#     state = models.CharField(max_length=100)
#     city = models.CharField(max_length=100)
#     zipcode = models.CharField(max_length=10)
#     religion = models.CharField(max_length=100)
#     bloodgroup = models.CharField(max_length=5)
#     nationality = models.CharField(max_length=100)
#     citizenship = models.CharField(max_length=100)
#     address_1 = models.TextField()
#     address_2 = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"

    
# class Meta:
#      db_table='ci_basic_information'




# ##Event Section ##
# #sample code checking 
# class User(models.Model):  # ci_erp_users
   
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)


#     class Meta:
#         db_table = 'ci_erp_users'
#         managed = False

#     def __str__(self):
#         return self.name


# class UserId(models.Model):
#     employee_id = models.IntegerField(primary_key=True)
#     user = models.OneToOneField(User, on_delete=models.DO_NOTHING, db_column='user_id', related_name='user_detail')

#     class Meta:
#         db_table = 'ci_erp_users_details'
#         managed = False

#     def __str__(self):
#         return str(self.employee_id)


 
 
# ##Holidays Section ##
# class Holiday(models.Model):
#     holiday_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField(blank=True, null=True)
#     event_name = models.CharField(max_length=255)
#     description = models.CharField(max_length=255, blank=True, null=True)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     is_publish = models.BooleanField(default=False)
#     created_at = models.CharField(max_length=200)
 
#     def __str__(self):
#         return self.event_name
 
#     class Meta:
#         db_table = "ci_holidays"
#         managed = False





# class CITraining(models.Model):
#     training_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     employee_id = models.CharField(max_length=200)
#     training_type_id = models.IntegerField()
#     associated_goals = models.TextField()
#     trainer_id = models.IntegerField()
#     start_date = models.CharField(max_length=200)
#     finish_date = models.CharField(max_length=200)
#     training_cost = models.DecimalField(max_digits=65, decimal_places=2)
#     training_status = models.IntegerField()
#     description = models.TextField()
#     performance = models.CharField(max_length=200)
#     remarks = models.TextField()
#     created_at = models.CharField(max_length=200)
#     training_skills = models.CharField(max_length=200)
 
#     def __str__(self):
#         return f"Training {self.training_id} for Employee {self.employee_id}"
#     class Meta:
#         db_table='ci_training'




# class CITrainer(models.Model):
#     trainer_id = models.AutoField(primary_key=True)
#     company_id = models.IntegerField()
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     contact_number = models.CharField(max_length=255)
#     email = models.CharField(max_length=255)
#     expertise = models.TextField()
#     address = models.TextField()
#     created_at = models.CharField(max_length=255)
 
#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"
#     class Meta:
#         db_table='ci_trainers'

 



# class CaseType(models.Model):
#     id = models.AutoField(primary_key=True)
#     type = models.CharField(max_length=50)
#     category_name = models.CharField(max_length=100)

#     class Meta:
#         db_table = 'ci_erp_constants'
#         managed = False

#     def __str__(self):
#         return self.category_name





from django.utils import timezone
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


from django.db import models

class YourMediaModel(models.Model):
    file = models.FileField(upload_to='uploads/')



# Create your models here.
class StaffRole(models.Model):
    role_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()                                              #Not Found
    role_name = models.CharField(max_length=200)
    role_access = models.CharField(max_length=200)
    role_resources = models.TextField(null=True, blank=True)
    created_at = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'ci_staff_roles'
        verbose_name = 'Staff Role'
        verbose_name_plural = 'Staff Roles'
        managed = False  # Django will not manage this table

    def __str__(self):
        return self.role_name

####Aditya Code :
# class BasicInformation (models.Model):
#     GENDER_CHOICES = (
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('O', 'Other'),
#     )

#     MARITAL_STATUS_CHOICES = (
#         (0, 'Single'),
#         (1, 'Married')

#     )
#     # id = models.IntegerField(null=True, blank=True)
#     first_name = models.CharField(max_length=100)
#     middle_name = models.CharField(max_length=100, blank=True, null=True)
#     last_name = models.CharField(max_length=100)
#     contact_number = models.CharField(max_length=20)
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
#     emp_id = models.CharField(max_length=50)
#     date_of_birth = models.DateField()
#     marital_status = models.IntegerField(choices=MARITAL_STATUS_CHOICES)
#     state = models.CharField(max_length=100)
#     city = models.CharField(max_length=100)
#     zipcode = models.CharField(max_length=10)
#     religion = models.CharField(max_length=100)
#     bloodgroup = models.CharField(max_length=5)
#     nationality = models.CharField(max_length=100)
#     citizenship = models.CharField(max_length=100)
#     address_1 = models.TextField()
#     address_2 = models.TextField(blank=True, null=True)
#     profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
#     def __str__(self):
#         return f"{self.first_name}{self.last_name}"
    
# class  Meta:
#     db_table = '`ci_erp_users`'
#     managed = False



class ERPUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        if not username:
            raise ValueError("The Username field must be set.")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class ERPUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True, db_column='id')
    user_role_id = models.ForeignKey(
        StaffRole, 
        on_delete=models.CASCADE,  # Handle deletion behavior
        related_name='role',
        db_column='user_role_id',  # Optional: reverse lookup name
    )
    user_type = models.CharField(max_length=50)
    company_id = models.IntegerField()
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    trading_name = models.CharField(max_length=100, null=True, blank=True)
    registration_no = models.CharField(max_length=100, null=True, blank=True)
    government_tax = models.CharField(max_length=100, null=True, blank=True)
    company_type_id = models.IntegerField()
    profile_photo = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    address_1 = models.TextField(null=True, blank=True)
    address_2 = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=255, null=True, blank=True)
    country = models.IntegerField()
    last_login_date = models.CharField(max_length=255, null=True, blank=True)
    last_logout_date = models.CharField(max_length=200, null=True, blank=True)
    last_login_ip = models.CharField(max_length=255, null=True, blank=True)
    is_logged_in = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.CharField(max_length=255, null=False,default=timezone.now())    
    custome_unique_id = models.IntegerField(null=True, blank=True)
    last_login = None
    is_superuser = None
    
    groups = None
    user_permissions = None
    
    objects = ERPUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'ci_erp_users'
        verbose_name = 'ERP User'
        verbose_name_plural = 'ERP Users'
        managed = False 

    def __str__(self):
        return self.username


class ERPUserDetails(models.Model):
    staff_details_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        ERPUser, 
        on_delete=models.CASCADE,  # Handle deletion behavior
        related_name='erpuserdetails_set',  # Optional: reverse lookup name
        db_column='user_id',
    )
    employee_id = models.CharField(max_length=255, null=True, blank=True)
    department_id = models.IntegerField(null=True, blank=True, db_column='department_id')

    
    designation_id = models.IntegerField()
    manager = models.IntegerField()
    office_shift_id = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    emp_ctc = models.CharField(max_length=100, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    salay_type = models.IntegerField()
    role_description = models.TextField(null=True, blank=True)
    date_of_joining = models.CharField(max_length=200, null=True, blank=True)
    date_of_leaving = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.CharField(max_length=200, null=True, blank=True)
    marital_status = models.IntegerField()
    religion_id = models.IntegerField()
    blood_group = models.CharField(max_length=200, null=True, blank=True)
    citizenship_id = models.IntegerField()
    bio = models.TextField(null=True, blank=True)
    experience = models.IntegerField()
    fb_profile = models.TextField(null=True, blank=True)
    twitter_profile = models.TextField(null=True, blank=True)
    gplus_profile = models.TextField(null=True, blank=True)
    linkedin_profile = models.TextField(null=True, blank=True)
    account_title = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    iban = models.CharField(max_length=255, null=True, blank=True)
    swift_code = models.CharField(max_length=255, null=True, blank=True)
    bank_branch = models.TextField(null=True, blank=True)
    ifsc_code = models.CharField(max_length=100, null=True, blank=True)
    contact_full_name = models.CharField(max_length=200, null=True, blank=True)
    contact_phone_no = models.CharField(max_length=200, null=True, blank=True)
    contact_email = models.CharField(max_length=200, null=True, blank=True)
    contact_address = models.TextField(null=True, blank=True)
    created_at = models.CharField(max_length=200, null=True, blank=True)
    probation = models.CharField(max_length=1, null=True, blank=True)
    probation_end_date = models.CharField(max_length=255, null=True, blank=True)
    pro_edit_permission = models.CharField(max_length=1, null=True, blank=True)
    billing = models.CharField(max_length=1, null=True, blank=True)

    class Meta:
        db_table = 'ci_erp_users_details'
        verbose_name = 'ERP User Detail'
        verbose_name_plural = 'ERP User Details'
        managed = False  # Django will not manage this table

    def __str__(self):
        return f"ERPUserDetails: {self.staff_details_id}"
    

class PIErpUserDetails (models.Model):
    #bio (bio,experience )
    bio = models.CharField(max_length=100, null=True,blank=True)
    experience = models.IntegerField()
    #social Profile (facebook,twitter, Google Plus , linkedin )
    fb_profile = models.TextField(max_length=100, null=True , blank=True)
    twitter_profile = models.TextField(max_length=100, null=True , blank=True)
    gplus_profile = models.TextField(max_length=100, null=True , blank=True)
    linkedin_profile = models.TextField(max_length=100, null=True , blank=True)
    #bank acc (acc title , acc num , bank name , IBAN,swift code ,bank Branch )
    account_title = models.CharField(max_length=100 , null=True , blank=True)
    account_number = models.IntegerField(null=True , blank=True)
    bank_name = models.CharField(max_length=200 , null=True, blank=True)
    iban = models.CharField(max_length=100 , null=True, blank=True)
    swift_code = models.CharField(max_length=100, null=True , blank=True)
    bank_branch = models.TextField(max_length=100, null=True, blank=True)

    #emg contact (full name,contact number )
    contact_full_name = models.CharField(max_length=100, null=True , blank=True)
    contact_phone_no = models.IntegerField(null=True , blank=True)
    contact_email = models.EmailField(max_length=100 , null=True , blank=True)
    contact_address = models.CharField(max_length=100 , null=True , blank=True)

    def __str__(self):
        return f"ErpUserDetails:{self.staff_details_id}"
    
class Meta:
    db_table = 'ci_erp_users_details'
    managed = False




class BiomatricDataTemp(models.Model):
    ci_biomatric_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key (INT)
    emp_id = models.CharField(max_length=50)  # VARCHAR(50)
    userid = models.ForeignKey(
        ERPUser, 
        on_delete=models.CASCADE,  # Handle deletion behavior
        # related_name='erpuserdetails_set',  # Optional: reverse lookup name
        db_column='userid',
    )
    login_date = models.CharField(max_length=100,default=timezone.now().today,
                                   db_column='login_date',)  # VARCHAR(100)
    clock_in = models.CharField(max_length=100)  # VARCHAR(100)
    clock_in_location = models.CharField(max_length=100)  # VARCHAR(100)
    clock_out = models.CharField(max_length=100)  # VARCHAR(100)
    clock_out_location = models.CharField(max_length=100)  # VARCHAR(100)
    state_in_out = models.CharField(max_length=100)  # VARCHAR(100)
    late_mark = models.CharField(max_length=100)  # VARCHAR(100)
    early_mark = models.CharField(max_length=100, default='0')  # VARCHAR(100)
    total_work = models.CharField(max_length=100, default='0')  # VARCHAR(100)
    attendance_date = models.DateField(db_column='attendance_date',  )  # VARCHAR(100)
    attendance_status = models.CharField(max_length=100,default="Present",
                                       db_column='attendance_status',  )  # VARCHAR(100)
    status = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], default='Y')  # ENUM(1)
    from_od = models.CharField(max_length=2, choices=[('Y', 'Yes'), ('N', 'No')], default='N')  # ENUM(2)
    reason = models.CharField(max_length=200, blank=True, null=True)  # VARCHAR(200)
    wfh = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], default='N')  # ENUM(1)

    def __str__(self):
        return f"Biometric Data for Employee ID {self.emp_id}"

    class Meta:
        db_table = 'ci_biomatric_data'  # Specifies the table name
        managed = False





# 1. ci_projects

from django.db import models

class CIProjects(models.Model):
    project_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    client_id = models.IntegerField()
    title = models.CharField(max_length=255)
    start_date = models.CharField(max_length=255)
    end_date = models.CharField(max_length=255)
    assigned_to = models.TextField()
    associated_goals = models.TextField()
    priority = models.CharField(max_length=255)
    project_no = models.CharField(max_length=255)
    budget_hours = models.CharField(max_length=255)
    summary = models.TextField()
    description = models.TextField()
    project_progress = models.CharField(max_length=255)
    project_note = models.TextField()
    status = models.BooleanField(default=True)
    added_by = models.IntegerField()
    created_at = models.CharField(max_length=255)

    class Meta:
        db_table = 'ci_projects'




#  2.ci_project_file

from django.db import models

class CIProjectFile(models.Model):
    project_file_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    project_id = models.IntegerField()
    employee_id = models.CharField(max_length=255)
    file_title = models.CharField(max_length=255)
    attachment_file = models.FileField(upload_to='attachments/', blank=True, null=True)
    created_at = models.CharField(max_length=200)

    class Meta:
        db_table = 'ci_projects_files'
  

#####Aditya Code :###


#3. ci_projects_bugs

from django.db import models



class CIProjectBug(models.Model):
    project_bug_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    project_id = models.IntegerField()
    employee_id = models.CharField(max_length=255)
    bug_note = models.TextField()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        db_table = 'ci_projects_bugs'



class Company(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, related_name='projects', on_delete=models.CASCADE)

    def __str__(self):
        return self.name



###code2 uncomment this if theres any error related to this field

class AssignedTask(models.Model):
    task_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    project_id = models.IntegerField()
    task_name = models.CharField(max_length=255)
    assigned_to = models.CharField(max_length=100)
    associated_goals = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    task_hour = models.DecimalField(max_digits=5, decimal_places=2)
    task_progress = models.DecimalField(max_digits=5, decimal_places=2)
    summary = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    task_status = models.IntegerField()
    task_note = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_name
    
    class Meta:
         db_table = 'ci_tasks'
         managed = False
      


class TaskDiscussion(models.Model):
    task_discussion_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    task_id = models.IntegerField()
    #employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    employee_id =  models.CharField(max_length=255)
    discussion_text = models.TextField()
    created_at = models.CharField(max_length=255)

    def __str__(self):
        return f"TaskDiscussion {self.task_discussion_id}"
    
    class Meta:
        db_table = 'ci_tasks_discussion'
        verbose_name = 'Discusion Text'
        verbose_name_plural = 'Discusion Texts'
        managed = False 


class TaskFile(models.Model):
    task_file_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    task_id = models.IntegerField()
    employee_id = models.CharField(max_length=255)  # Use an IntegerField for employee_id if not linking to a model
    file_title = models.CharField(max_length=255)
    attachment_file = models.FileField(upload_to='attachments/')  # Ensure MEDIA_URL and MEDIA_ROOT are configured
    created_at = models.CharField(max_length=200)
    def __str__(self):
        return self.file_title
    
    class Meta:
        db_table = 'ci_tasks_files'
        verbose_name = 'File Title'
        verbose_name_plural = 'File Titles'
        managed = False 


class TaskNote(models.Model):
    task_note_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    task_id = models.IntegerField()
    employee_id = models.CharField(max_length=255)  # Use IntegerField if not linking to another model
    task_note = models.TextField()
    created_at = models.CharField(max_length=255)

    def __str__(self):
        return f"TaskNote {self.task_note_id}: {self.task_note[:50]}"
    
    class Meta:
        db_table = 'ci_tasks_notes'
        verbose_name = 'Task Note'
        verbose_name_plural = 'Task Notes'
        managed = False 



class CIPunchReport(models.Model):
    punch_id = models.AutoField(primary_key=True)
    email = models.EmailField()
    empid = models.CharField(max_length=50)
    userid = models.CharField(max_length=50)
    punch_in_location = models.CharField(max_length=255)
    punchdate = models.DateField()
    punch_in_time = models.CharField(max_length=100)
    punch_out_time = models.CharField(max_length=100)
    punch_out_location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.empid} - {self.punchdate}"
    
    class Meta:
        db_table = 'ci_punch_report'
        managed = False
 


class ErpUser1(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_role_id = models.IntegerField()
    user_type = models.CharField(max_length=50)
    company_id = models.IntegerField()
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    trading_name = models.CharField(max_length=255, null=True, blank=True)
    registration_no = models.CharField(max_length=255, null=True, blank=True)
    government_tax = models.CharField(max_length=255, null=True, blank=True)
    company_type_id = models.IntegerField()
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    contact_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    last_login_date = models.DateTimeField(null=True, blank=True)
    last_logout_date = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_logged_in = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    custome_unique_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'ci_erp_users'



# Roles & Privileges 
from django.db import models
class CiStaffRole(models.Model):
    role_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    role_name = models.CharField(max_length=200)
    role_access = models.CharField(max_length=200)
    role_resources = models.TextField()
    created_at = models.CharField(max_length=200)

    # def __str__(self):
    #     return self.role_name

    class Meta:
        db_table = 'ci_staff_roles'


#  Shift & Scheduling 

class OfficeShift(models.Model):
    office_shift_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    state_id = models.IntegerField()
    employee_hub_id = models.IntegerField()
    shift_name = models.CharField(max_length=255)
    monday_in_time = models.CharField(max_length=222)
    monday_out_time = models.CharField(max_length=222)
    tuesday_in_time = models.CharField(max_length=222)
    tuesday_out_time = models.CharField(max_length=222)
    wednesday_in_time = models.CharField(max_length=222)
    wednesday_out_time = models.CharField(max_length=222)
    thursday_in_time = models.CharField(max_length=222)
    thursday_out_time = models.CharField(max_length=222)
    friday_in_time = models.CharField(max_length=222)
    friday_out_time = models.CharField(max_length=222)
    saturday_in_time = models.CharField(max_length=222)
    saturday_out_time = models.CharField(max_length=222)
    sunday_in_time = models.CharField(max_length=222)
    sunday_out_time = models.CharField(max_length=222)
    created_at = models.CharField(max_length=222)

    class Meta:
        db_table = 'ci_office_shifts'





class CiBiomatricData(models.Model):
    ci_biomatric_id = models.AutoField(primary_key=True)
    emp_id = models.CharField(max_length=50)
    userid = models.CharField(max_length=50)
    login_date = models.DateField()
    clock_in = models.TimeField(null=True, blank=True)
    clock_in_location = models.CharField(max_length=255, null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    clock_out_location = models.CharField(max_length=255, null=True, blank=True)
    state_in_out = models.CharField(max_length=50, null=True, blank=True)
    late_mark = models.BooleanField(default=False)
    early_mark = models.BooleanField(default=False)
    total_work = models.DurationField(null=True, blank=True)
    attendance_date = models.DateField()
    attendance_status = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    from_od = models.CharField(max_length=1, choices=[("Y", "Yes"), ("N", "No")], default="N")

    reason = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "ci_biomatric_data"
        managed = False 


    def __str__(self):
        return f"Biometric Record {self.ci_biomatric_id} - {self.userid}"




#16-04-2025

from django.db import models

class ContractOption(models.Model):
    contract_date = models.DateField()
    billing = models.CharField(max_length=10, choices=[("Yes", "Yes"), ("No", "No")])
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    payslip_type = models.CharField(max_length=20)
    office_shift = models.CharField(max_length=50)
    contract_end = models.DateField(null=True, blank=True)
    probation = models.BooleanField(default=False)
    manager = models.CharField(max_length=100)
    profile_edit_permission = models.BooleanField(default=False)
    role_description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.designation} ({self.department})"
    
class Meta:
    db_table='ci_contract_options'




from django.db import models

class BasicInformation(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    MARITAL_STATUS_CHOICES = (
        (0, 'Single'),
        (1, 'Married'),
    )

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    users_id = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    marital_status = models.IntegerField(choices=MARITAL_STATUS_CHOICES)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)
    religion = models.CharField(max_length=100)
    bloodgroup = models.CharField(max_length=5)
    nationality = models.CharField(max_length=100)
    citizenship = models.CharField(max_length=100)
    address_1 = models.TextField()
    address_2 = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    
class Meta:
     db_table='ci_basic_information'




##Event Section ##
#sample code checking 
class User(models.Model):  # ci_erp_users
   
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


    class Meta:
        db_table = 'ci_erp_users'
        managed = False

    def __str__(self):
        return self.name


class UserId(models.Model):
    employee_id = models.CharField(max_length=255, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, db_column='user_id', related_name='user_detail')

    class Meta:
        db_table = 'ci_erp_users_details'
        managed = False

    def __str__(self):
        return str(self.employee_id)


 
 
##Holidays Section ##
class Holiday(models.Model):
    holiday_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField(blank=True, null=True)
    event_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_publish = models.BooleanField(default=False)
    created_at = models.CharField(max_length=200)
 
    def __str__(self):
        return self.event_name
 
    class Meta:
        db_table = "ci_holidays"
        managed = False





class CITraining(models.Model):
    training_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    employee_id = models.CharField(max_length=200)
    training_type_id = models.IntegerField()
    associated_goals = models.TextField()
    trainer_id = models.IntegerField()
    start_date = models.CharField(max_length=200)
    finish_date = models.CharField(max_length=200)
    training_cost = models.DecimalField(max_digits=65, decimal_places=2)
    training_status = models.IntegerField()
    description = models.TextField()
    performance = models.CharField(max_length=200)
    remarks = models.TextField()
    created_at = models.CharField(max_length=200)
    training_skills = models.CharField(max_length=200)
 
    def __str__(self):
        return f"Training {self.training_id} for Employee {self.employee_id}"
    class Meta:
        db_table='ci_training'




class CITrainer(models.Model):
    trainer_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    expertise = models.TextField()
    address = models.TextField()
    created_at = models.CharField(max_length=255)
 
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    class Meta:
        db_table='ci_trainers'

 



class CaseType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)
    category_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'ci_erp_constants'
        managed = False

    def __str__(self):
        return self.category_name










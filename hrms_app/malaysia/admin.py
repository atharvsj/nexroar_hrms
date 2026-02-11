"""
Malaysian Payroll Django Admin Configuration
==============================================
Optional Django admin configuration for Malaysian statutory data.
Note: Since this module uses raw SQL, these are placeholder model registrations.
"""

from django.contrib import admin

# This module uses raw SQL queries with connection.cursor()
# Rather than Django ORM models, therefore no models to register with admin.

# If you need Django admin for Malaysian payroll, you would need to:
# 1. Create Django models that mirror the SQL tables in DATABASE_TABLES.sql
# 2. Register those models here
# 3. Use managed = False in the Meta class to avoid migrations

# Example (uncomment and modify if needed):
# 
# from django.db import models
# 
# class MalaysianEmployeeDetails(models.Model):
#     """Malaysian employee statutory details"""
#     my_employee_id = models.AutoField(primary_key=True)
#     employee_id = models.IntegerField()
#     # ... other fields
#     
#     class Meta:
#         managed = False  # Don't let Django manage this table
#         db_table = 'ci_my_employee_details'
# 
# @admin.register(MalaysianEmployeeDetails)
# class MalaysianEmployeeDetailsAdmin(admin.ModelAdmin):
#     list_display = ('employee_id', 'ic_number', 'worker_type')
#     search_fields = ('ic_number', 'tax_reference_no')

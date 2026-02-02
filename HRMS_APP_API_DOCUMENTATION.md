# Complete HRMS App API Documentation

This document contains the complete documentation of all APIs in the `hrms_app` module.

**Base URL Prefix:** `/api/`

---

## Table of Contents

1. [Dropdown APIs](#dropdown-apis)
2. [Account Details APIs](#account-details-apis)
3. [Employee Panel APIs](#employee-panel-apis)
4. [Admin Panel APIs](#admin-panel-apis)
5. [Reports APIs](#reports-apis)
6. [Dashboard APIs](#dashboard-apis)
7. [OTP & Authentication APIs](#otp--authentication-apis)
8. [Role Management APIs](#role-management-apis)
9. [Training Management APIs](#training-management-apis)

---

## Dropdown APIs

### 1. Employee Manager Dropdown
```json
{
  "name": "Employee Manager Dropdown",
  "url": "/api/emp_manager_dropdown/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "employee_data": [
      {
        "id": "integer - user id",
        "employee_name": "string - full name",
        "employee_id": "string - employee code"
      }
    ],
    "manager_data": [
      {
        "manager_id": "integer",
        "manager_name": "string"
      }
    ]
  }
}
```

### 2. Designation Department Dropdown
```json
{
  "name": "Designation Department Dropdown",
  "url": "/api/desig_dept_dropdown/",
  "method": "GET",
  "request_payload": {
    "dept_id": "integer (optional) - if provided, returns designations for that department"
  },
  "response": {
    "status": "success",
    "dept_data": [
      {
        "dept_id": "integer",
        "dept_name": "string"
      }
    ],
    "desig_data": [
      {
        "desig_id": "integer",
        "desig_name": "string"
      }
    ]
  }
}
```

### 3. Employees By Designation
```json
{
  "name": "Employees By Designation",
  "url": "/api/employees_by_designation/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of employees filtered by designation"
  }
}
```

### 4. Designation Dropdown Filter By Line Manager
```json
{
  "name": "Designation Dropdown Filter By Line Manager",
  "url": "/api/designation_dropdown_filter_by_line_manager/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of designations filtered by line manager"
  }
}
```

### 5. Ekach Line Manager
```json
{
  "name": "Ekach Line Manager",
  "url": "/api/ekach_line_manager/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "line manager data"
  }
}
```

### 6. State Dropdown
```json
{
  "name": "State Dropdown",
  "url": "/api/state_dropdown/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of states"
  }
}
```

### 7. Employee Hub Dropdown
```json
{
  "name": "Employee Hub Dropdown",
  "url": "/api/employee_hub_dropdown/<int:state_id>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of employee hubs for the state"
  }
}
```

### 8. Office Shift Dropdown
```json
{
  "name": "Office Shift Dropdown",
  "url": "/api/office_shift_dropdown/<int:employee_hub_id>/<int:state_id>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of office shifts"
  }
}
```

---

## Account Details APIs

### 9. Contract Details
```json
{
  "name": "Contract Details - Get",
  "url": "/api/contract_details/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer - required",
    "type": "integer - required (1=contract info, 2=allowances, 3=commissions, 4=deductions, 5=other payments)"
  },
  "response": {
    "user_info": {
      "user_type": "string",
      "email": "string"
    },
    "contract_details": [
      {
        "contract_date": "date",
        "billing": "string",
        "department_id": "integer",
        "department": "string",
        "designation_id": "integer",
        "designation": "string",
        "basic_salary": "decimal",
        "gross_salary": "decimal",
        "hourly_rate": "decimal",
        "payslip_type": "string",
        "office_shift_id": "integer",
        "office_shift": "string",
        "contract_end": "date",
        "probation": "string (Y/N)",
        "probation_end_date": "date",
        "manager_name": "string",
        "role_description": "string"
      }
    ]
  }
}
```

```json
{
  "name": "Contract Details - Update",
  "url": "/api/contract_details/",
  "method": "PATCH",
  "request_payload": {
    "user_id": "integer - required",
    "type": "integer - required",
    "department_id": "integer (optional)",
    "designation_id": "integer (optional)",
    "basic_salary": "decimal (optional)",
    "gross_salary": "decimal (optional)",
    "hourly_rate": "decimal (optional)",
    "payslip_type": "string (optional)",
    "office_shift_id": "integer (optional)",
    "probation": "string Y/N (optional)",
    "probation_end_date": "date (optional)",
    "manager": "integer (optional)",
    "role_description": "string (optional)",
    "billing": "string (optional)",
    "contract_date": "date (optional)",
    "pay_id": "integer (required for type 2-5)",
    "pay_title": "string (for type 2-5)",
    "pay_amount": "decimal (for type 2-5)",
    "is_taxable": "string (for type 2,3,5)",
    "is_fixed": "string (for type 2-5)",
    "salary_month": "string (for type 2-5)"
  },
  "response": {
    "status": "success",
    "message": "Contract details updated successfully"
  }
}
```

```json
{
  "name": "Contract Details - Delete",
  "url": "/api/contract_details/",
  "method": "DELETE",
  "request_payload": {
    "type": "integer - required (2=allowance, 3=commission, 4=deduction, 5=other payment)",
    "pay_id": "integer - required"
  },
  "response": {
    "status": "success",
    "message": "contract details deleted successfully"
  }
}
```

### 10. Employee Basic Information
```json
{
  "name": "Employee Basic Information - Get",
  "url": "/api/emp_basic_info/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer - required"
  },
  "response": {
    "status": "success",
    "data": [
      {
        "first_name": "string",
        "middle_name": "string",
        "last_name": "string",
        "contact_number": "string",
        "gender": "string (Male/Female/Others)",
        "age": "integer",
        "employee_id": "string",
        "manager": "string",
        "date_of_birth": "date",
        "is_active": "string (Active/Inactive)",
        "marital_status": "string (Married/Unmarried)",
        "role_id": "integer",
        "role_name": "string",
        "state_id": "integer",
        "state": "string",
        "country_id": "integer",
        "country": "string",
        "employee_hub_name": "string",
        "city": "string",
        "zipcode": "string",
        "blood_group": "string",
        "address_1": "string",
        "address_2": "string",
        "correspondence_state": "string",
        "correspondence_country": "string",
        "correspondence_city": "string",
        "correspondence_pincode": "string"
      }
    ]
  }
}
```

```json
{
  "name": "Employee Basic Information - Update",
  "url": "/api/emp_basic_info/",
  "method": "PATCH",
  "request_payload": {
    "user_id": "integer - required",
    "first_name": "string (optional)",
    "middle_name": "string (optional)",
    "last_name": "string (optional)",
    "contact_number": "string (optional)",
    "gender": "integer/string (optional)",
    "age": "integer (optional)",
    "employee_id": "string (optional)",
    "date_of_birth": "date (optional)",
    "is_active": "integer (optional)",
    "marital_status": "string (optional)",
    "role_id": "integer (optional)",
    "state_id": "integer (optional)",
    "country_id": "integer (optional)",
    "employee_hub_id": "integer (optional)",
    "city": "string (optional)",
    "zipcode": "string (optional)",
    "blood_group": "string (optional)",
    "address_1": "string (optional)",
    "address_2": "string (optional)",
    "correspondence_state": "string (optional)",
    "correspondence_country": "string (optional)",
    "correspondence_city": "string (optional)",
    "correspondence_pincode": "string (optional)"
  },
  "response": {
    "status": "success",
    "message": "User details updated successfully"
  }
}
```

### 11. Personal Information
```json
{
  "name": "Personal Information - Get",
  "url": "/api/personal_info/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer - required",
    "type": "integer - required (1=bio/experience, 2=social links, 3=bank details, 4=emergency contact, 6=documents)"
  },
  "response": {
    "status": "success",
    "personal_details": {
      "bio": "string (type 1)",
      "experience": "string (type 1)",
      "fb_profile": "string (type 2)",
      "twitter_profile": "string (type 2)",
      "gplus_profile": "string (type 2)",
      "linkedin_profile": "string (type 2)",
      "account_title": "string (type 3)",
      "account_number": "string (type 3)",
      "bank_name": "string (type 3)",
      "iban": "string (type 3)",
      "bank_branch": "string (type 3)",
      "pan_number": "string (type 3)",
      "esic_number": "string (type 3)",
      "pf_number": "string (type 3)",
      "uan_number": "string (type 3)",
      "ifsc_code": "string (type 3)",
      "swift_code": "string (type 3)",
      "contact_full_name": "string (type 4)",
      "contact_phone_no": "string (type 4)",
      "contact_email": "string (type 4)",
      "contact_address": "string (type 4)",
      "passport_no": "string (type 6)",
      "vehicle_no": "string (type 6)",
      "driving_licence_no": "string (type 6)",
      "aadhar_no": "string (type 6)"
    }
  }
}
```

```json
{
  "name": "Personal Information - Update",
  "url": "/api/personal_info/",
  "method": "PATCH",
  "request_payload": {
    "user_id": "integer - required",
    "type": "integer - required",
    "...fields based on type": "values"
  },
  "response": {
    "status": "success",
    "message": "Personal details updated successfully"
  }
}
```

### 12. Get Profile Photo
```json
{
  "name": "Get Profile Photo",
  "url": "/api/get_profile_photo/<str:employee_id>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "profile_photo": "URL string"
  }
}
```

### 13. Update Profile Photo
```json
{
  "name": "Update Profile Photo",
  "url": "/api/update_profile_photo/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer - required",
    "file": "File (multipart/form-data) - JPG, JPEG, PNG"
  },
  "response": {
    "status": "success",
    "message": "Profile photo updated successfully"
  }
}
```

### 14. Account Information
```json
{
  "name": "Account Information",
  "url": "/api/account_info/",
  "method": "POST/PATCH",
  "request_payload": {
    "user_id": "integer - required"
  },
  "response": {
    "status": "success",
    "data": "account information"
  }
}
```

### 15. Document Details
```json
{
  "name": "Document Details",
  "url": "/api/document_details/",
  "method": "POST/PATCH",
  "request_payload": {
    "user_id": "integer - required"
  },
  "response": {
    "status": "success",
    "data": "document details"
  }
}
```

### 16. Change Password
```json
{
  "name": "Change Password",
  "url": "/api/change_password/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer - required",
    "old_password": "string - required",
    "new_password": "string - required"
  },
  "response": {
    "status": "success",
    "message": "Password changed successfully"
  }
}
```

### 17. Timesheet Agenda
```json
{
  "name": "Timesheet Agenda",
  "url": "/api/timesheet_agenda/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer - required"
  },
  "response": {
    "status": "success",
    "data": "timesheet agenda data"
  }
}
```

### 18. Leave Statistics
```json
{
  "name": "Leave Statistics",
  "url": "/api/leave_statistics/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer - required"
  },
  "response": {
    "status": "success",
    "data": "leave statistics"
  }
}
```

---

## Employee Panel APIs

### 19. Dashboard Attendance
```json
{
  "name": "Dashboard Attendance",
  "url": "/api/dashboard_attendance/<str:employee_id>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "dashboard attendance data"
  }
}
```

### 20. Employee Attendance (Clock In/Out)
```json
{
  "name": "Employee Attendance",
  "url": "/api/employee_attendance/",
  "method": "POST",
  "request_payload": {
    "emp_id": "string - required - employee ID",
    "punch_time": "string - required - format: YYYY-MM-DD HH:MM:SS",
    "punch_type": "string - required - IN or OUT",
    "location": "string - optional"
  },
  "response": {
    "status": "Clock-In recorded / Clock-Out recorded",
    "punch_time": "datetime",
    "late_mark": "Y/N",
    "is_half_day": "Y/N",
    "half_day_reason": "string or N/A"
  }
}
```

### 21. Basic Information
```json
{
  "name": "Basic Information",
  "url": "/api/basic_info/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer - required"
  },
  "response": {
    "status": "success",
    "data": "basic employee information"
  }
}
```

### 22. Holiday List
```json
{
  "name": "Holiday List",
  "url": "/api/holiday_list/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of holidays"
  }
}
```

### 23. Project List
```json
{
  "name": "Project List",
  "url": "/api/project_list/<int:user_id>/<int:type>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of projects"
  }
}
```

### 24. Project Details
```json
{
  "name": "Project Details",
  "url": "/api/project_details/<int:user_id>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "project details"
  }
}
```

### 25. Project Discussion
```json
{
  "name": "Project Discussion",
  "url": "/api/project_discussion/",
  "method": "POST",
  "request_payload": {
    "project_id": "integer - required"
  },
  "response": {
    "status": "success",
    "data": "project discussions"
  }
}
```

### 26. Project Attach File
```json
{
  "name": "Project Attach File",
  "url": "/api/project_attach_file/",
  "method": "POST",
  "request_payload": {
    "project_id": "integer - required",
    "file": "File (multipart/form-data)"
  },
  "response": {
    "status": "success",
    "message": "File attached successfully"
  }
}
```

### 27. Payroll
```json
{
  "name": "Payroll",
  "url": "/api/payroll/<int:user_id>/<int:type>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "payroll data"
  }
}
```

### 28. Policies
```json
{
  "name": "Policies",
  "url": "/api/policies/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of policies"
  }
}
```

---

## Admin Panel APIs

### 29. Employee Details
```json
{
  "name": "Employee Details - List All",
  "url": "/api/employee_details/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": [
      {
        "index": "integer",
        "user_id": "integer",
        "employee_id": "string",
        "employee_name": "string",
        "department_id": "integer",
        "department_name": "string",
        "designation_id": "integer",
        "designation_name": "string",
        "join_date": "date",
        "status": "integer (1=active, 0=inactive)",
        "manager": "string",
        "profile_photo": "URL string"
      }
    ]
  }
}
```

### 30. Edit Employee
```json
{
  "name": "Edit Employee - Get",
  "url": "/api/edit_employee/<int:user_id>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": [
      {
        "emp_name": "string",
        "email": "string",
        "phone": "string",
        "manager": "string",
        "designation": "string",
        "department": "string",
        "status": "integer",
        "join_date": "date",
        "manager_id": "integer",
        "designation_id": "integer",
        "department_id": "integer",
        "profile_photo": "URL string",
        "probation": "string",
        "division_id": "integer",
        "employee_hub_id": "integer",
        "state": "integer",
        "office_shift_id": "integer",
        "office_shift": "string",
        "country_name": "string",
        "headquarter_id": "integer",
        "headquarter": "string",
        "sub_division": "string",
        "employee_id": "string",
        "address": "string",
        "gross_salary": "decimal",
        "grade_id": "integer",
        "grade_name": "string"
      }
    ]
  }
}
```

```json
{
  "name": "Edit Employee - Update",
  "url": "/api/edit_employee/",
  "method": "PUT",
  "request_payload": {
    "user_id": "integer - required",
    "emp_name": "string (optional)",
    "email": "string (optional)",
    "phone": "string (optional)",
    "manager_id": "integer (optional)",
    "designation_id": "integer (optional)",
    "department_id": "integer (optional)",
    "office_shift": "integer (optional)",
    "status": "integer (optional)",
    "join_date": "date (optional)",
    "is_probation": "string Y/N (optional)",
    "country_id": "integer (optional)",
    "headquarter_id": "integer (optional)",
    "subDivision": "string (optional)",
    "employee_hub_id": "integer (optional)",
    "address": "string (optional)",
    "division_id": "integer (optional)",
    "state_id": "integer (optional)",
    "grade_id": "integer (optional)",
    "file": "File (optional - multipart/form-data)"
  },
  "response": {
    "status": "success",
    "message": "Employee updated successfully."
  }
}
```

```json
{
  "name": "Edit Employee - Delete",
  "url": "/api/edit_employee/",
  "method": "DELETE",
  "request_payload": {
    "user_id": "integer - required"
  },
  "response": {
    "status": "success",
    "message": "employee deleted successfully"
  }
}
```

### 31. Change Manager
```json
{
  "name": "Change Manager",
  "url": "/api/change_manager/",
  "method": "PUT",
  "request_payload": {
    "user_id": "integer - required",
    "manager_id": "integer - required"
  },
  "response": {
    "status": "success",
    "message": "manager updated successfully"
  }
}
```

### 32. Get Max Employee ID
```json
{
  "name": "Get Max Employee ID",
  "url": "/api/get_max_employee_id/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "employee_id": "string - next available employee ID (e.g., V0924)"
  }
}
```

### 33. Fetch Documents
```json
{
  "name": "Fetch Documents",
  "url": "/api/fetch_documents/",
  "method": "POST",
  "request_payload": {
    "email_id": "string - required"
  },
  "response": {
    "status": "success",
    "documents": {
      "aadhar": "URL or null",
      "pan": "URL or null",
      "hsc": "URL or null",
      "ssc": "URL or null",
      "degree": "URL or null",
      "other": "URL or null",
      "passport_photo": "URL or null",
      "driving_licence": "URL or null",
      "cheque_photo": "URL or null",
      "experience_letter": "URL or null",
      "appointment_letter": "URL or null",
      "offer_letter": "URL or null",
      "resume": "URL or null"
    }
  }
}
```

### 34. Check Existing Email
```json
{
  "name": "Check Existing Email",
  "url": "/api/check_existing_email/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": [
      {
        "email": "string"
      }
    ]
  }
}
```

### 35. Add Employee
```json
{
  "name": "Add Employee",
  "url": "/api/add_employee/",
  "method": "POST",
  "request_payload": {
    "first_name": "string - required",
    "middle_name": "string (optional)",
    "last_name": "string - required",
    "emp_id": "string - required - employee ID",
    "phone": "string - required",
    "gender": "string - Male/Female/Other",
    "email": "string - required",
    "username": "string - required",
    "password": "string - required",
    "office_shift": "integer",
    "role": "integer - user role ID",
    "department_id": "integer",
    "designation_id": "integer",
    "division_id": "integer",
    "gross_salary": "decimal",
    "manager_id": "integer",
    "status": "integer",
    "company_id": "integer",
    "is_probation": "string Y/N",
    "state_id": "integer",
    "country_id": "integer",
    "employee_hub_id": "integer",
    "headquarter": "integer (optional)",
    "sub_division": "string (optional)",
    "file": "File (optional - profile photo)"
  },
  "response": {
    "status": "success",
    "message": "Employee added successfully."
  }
}
```

### 36. Role List (Legacy)
```json
{
  "name": "Role List - Get",
  "url": "/api/role_list/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of roles"
  }
}
```

```json
{
  "name": "Role List - Update",
  "url": "/api/role_list/",
  "method": "PUT",
  "request_payload": {
    "role_id": "integer - required",
    "role_name": "string",
    "permissions": "array"
  },
  "response": {
    "status": "success",
    "message": "Role updated"
  }
}
```

```json
{
  "name": "Role List - Delete",
  "url": "/api/role_list/<int:role_id>/",
  "method": "DELETE",
  "request_payload": {},
  "response": {
    "status": "success",
    "message": "Role deleted"
  }
}
```

### 37. Add Role (Legacy)
```json
{
  "name": "Add Role",
  "url": "/api/add_role/",
  "method": "POST",
  "request_payload": {
    "role_name": "string - required",
    "permissions": "array"
  },
  "response": {
    "status": "success",
    "message": "Role added"
  }
}
```

### 38. Office Shift
```json
{
  "name": "Office Shift - List",
  "url": "/api/office_shift/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "array of office shifts"
  }
}
```

```json
{
  "name": "Office Shift - Create",
  "url": "/api/office_shift/",
  "method": "POST",
  "request_payload": {
    "shift_name": "string - required",
    "monday_in_time": "time",
    "monday_out_time": "time",
    "tuesday_in_time": "time",
    "tuesday_out_time": "time",
    "...": "other day timings"
  },
  "response": {
    "status": "success",
    "message": "Shift created"
  }
}
```

```json
{
  "name": "Office Shift - Update",
  "url": "/api/office_shift/",
  "method": "PUT",
  "request_payload": {
    "shift_id": "integer - required",
    "shift_name": "string",
    "...": "shift timings"
  },
  "response": {
    "status": "success",
    "message": "Shift updated"
  }
}
```

```json
{
  "name": "Office Shift - Delete",
  "url": "/api/office_shift/<int:shift_id>/",
  "method": "DELETE",
  "request_payload": {},
  "response": {
    "status": "success",
    "message": "Shift deleted"
  }
}
```

### 39. Attendance Overview
```json
{
  "name": "Attendance Overview",
  "url": "/api/attendance_overview/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "attendance overview data"
  }
}
```

### 40. Manual Attendance
```json
{
  "name": "Manual Attendance",
  "url": "/api/manual_attendance/",
  "method": "GET/POST",
  "request_payload": {
    "employee_id": "string (for POST)",
    "date": "date (for POST)",
    "clock_in": "time (for POST)",
    "clock_out": "time (for POST)"
  },
  "response": {
    "status": "success",
    "data/message": "attendance data or success message"
  }
}
```

### 41. Employee Hub
```json
{
  "name": "Employee Hub",
  "url": "/api/employee_hub/",
  "method": "GET/POST/PUT/DELETE",
  "request_payload": {
    "employee_hub_id": "integer (for PUT/DELETE)",
    "employee_hub_name": "string",
    "state_id": "integer",
    "designation_id": "integer"
  },
  "response": {
    "status": "success",
    "data/message": "hub data or success message"
  }
}
```

### 42. Monthly Report (Attendance)
```json
{
  "name": "Monthly Report",
  "url": "/api/monthly_report/",
  "method": "POST",
  "request_payload": {
    "month": "integer",
    "year": "integer"
  },
  "response": {
    "status": "success",
    "data": "monthly attendance report"
  }
}
```

### 43. Holiday
```json
{
  "name": "Holiday Management",
  "url": "/api/holiday/",
  "method": "GET/POST/PUT/DELETE",
  "request_payload": {
    "holiday_id": "integer (for PUT/DELETE)",
    "holiday_name": "string",
    "holiday_date": "date",
    "holiday_type": "string"
  },
  "response": {
    "status": "success",
    "data/message": "holiday data or success message"
  }
}
```

### 44. Payroll Setup Configuration
```json
{
  "name": "Payroll Setup Configuration",
  "url": "/api/payroll_setup_configuration/",
  "method": "GET/POST/PATCH",
  "request_payload": {
    "...": "payroll configuration fields"
  },
  "response": {
    "status": "success",
    "data": "payroll configuration"
  }
}
```

### 45. Payroll Employee TDS
```json
{
  "name": "Payroll Employee TDS",
  "url": "/api/payroll_employee_tds/",
  "method": "GET/POST",
  "request_payload": {
    "employee_id": "string",
    "tds_amount": "decimal"
  },
  "response": {
    "status": "success",
    "data": "TDS data"
  }
}
```

### 46. Payroll Report
```json
{
  "name": "Payroll Report",
  "url": "/api/payroll_report/<int:month>/<int:year>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "payroll report for the month"
  }
}
```

### 47. Pre Saved Payroll Report
```json
{
  "name": "Pre Saved Payroll Report",
  "url": "/api/pre_saved_payroll_report/",
  "method": "GET/POST",
  "request_payload": {
    "month": "integer",
    "year": "integer"
  },
  "response": {
    "status": "success",
    "data": "pre-saved payroll data"
  }
}
```

### 48. Save Payroll Report
```json
{
  "name": "Save Payroll Report",
  "url": "/api/save_payroll_report/",
  "method": "POST",
  "request_payload": {
    "month": "integer",
    "year": "integer",
    "payroll_data": "array"
  },
  "response": {
    "status": "success",
    "message": "Payroll saved"
  }
}
```

### 49. Payment Info
```json
{
  "name": "Payment Info",
  "url": "/api/payment_info/",
  "method": "GET/POST",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "payment information"
  }
}
```

### 50. Update Payment Info
```json
{
  "name": "Update Payment Info",
  "url": "/api/update_payment_info/",
  "method": "POST/PATCH",
  "request_payload": {
    "...": "payment info fields"
  },
  "response": {
    "status": "success",
    "message": "Payment info updated"
  }
}
```

### 51. Salary Structure
```json
{
  "name": "Salary Structure",
  "url": "/api/salary_structure/",
  "method": "GET/POST",
  "request_payload": {
    "employee_id": "string"
  },
  "response": {
    "status": "success",
    "data": "salary structure data"
  }
}
```

### 52. Payslip History
```json
{
  "name": "Payslip History",
  "url": "/api/payslip_history/",
  "method": "GET/POST",
  "request_payload": {
    "employee_id": "string",
    "year": "integer (optional)"
  },
  "response": {
    "status": "success",
    "data": "array of payslips"
  }
}
```

### 53. Payslip
```json
{
  "name": "Payslip",
  "url": "/api/payslip/",
  "method": "GET/POST",
  "request_payload": {
    "employee_id": "string",
    "month": "integer",
    "year": "integer"
  },
  "response": {
    "status": "success",
    "data": "payslip details"
  }
}
```

### 54. Assets Inventory
```json
{
  "name": "Assets Inventory",
  "url": "/api/assets_inventory/",
  "method": "GET/POST/PATCH/DELETE",
  "request_payload": {
    "asset_id": "integer (for PATCH/DELETE)",
    "asset_name": "string",
    "category_id": "integer",
    "serial_number": "string",
    "employee_id": "string (optional)"
  },
  "response": {
    "status": "success",
    "data/message": "assets data or success message"
  }
}
```

### 55. Search By Email Vet Talent
```json
{
  "name": "Search By Email Vet Talent",
  "url": "/api/search_by_email_vet_talent/",
  "method": "POST",
  "request_payload": {
    "email": "string - required"
  },
  "response": {
    "status": "success",
    "data": "talent data from VetHR"
  }
}
```

### 56. Employee Leave Pattern
```json
{
  "name": "Employee Leave Pattern",
  "url": "/api/employee_leave_pattern/",
  "method": "POST",
  "request_payload": {
    "year": "integer - required"
  },
  "response": {
    "status": "success",
    "year": "integer",
    "data": [
      {
        "month": "string (e.g., January)",
        "CL": "integer - casual leave count",
        "ML": "integer - medical leave count",
        "PL": "integer - paid leave count",
        "MTL": "integer - maternity leave count",
        "PTL": "integer - paternity leave count",
        "LWP": "integer - leave without pay count",
        "Total": "integer"
      }
    ]
  }
}
```

### 57. Holiday Calendar
```json
{
  "name": "Holiday Calendar",
  "url": "/api/holidays/calendar/<int:country_id>/<int:state_id>/<int:employee_hub>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "holiday calendar data"
  }
}
```

### 58. View Notification
```json
{
  "name": "View Notification",
  "url": "/api/view_notification/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "notifications array"
  }
}
```

### 59. Check Phasewise Parameters
```json
{
  "name": "Check Phasewise Parameters",
  "url": "/api/check_phasewise_parameters/",
  "method": "GET/POST",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "phasewise parameter data"
  }
}
```

### 60. Get Employee Details Clearance Form
```json
{
  "name": "Get Employee Details Clearance Form",
  "url": "/api/get_employee_details_clearance_form/",
  "method": "GET/POST",
  "request_payload": {
    "employee_id": "string"
  },
  "response": {
    "status": "success",
    "data": "clearance form details"
  }
}
```

### 61. View Employee Salary Slip
```json
{
  "name": "View Employee Salary Slip",
  "url": "/api/view_employee_salary_slip/<str:employee_id>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": "salary slip details"
  }
}
```

### 62. Save HR Revenue Expense
```json
{
  "name": "Save HR Revenue Expense - Create/List",
  "url": "/api/save_hr_revenue_expense/",
  "method": "GET/POST",
  "request_payload": {
    "month": "integer",
    "year": "integer",
    "total_revenue": "decimal",
    "total_expense": "decimal"
  },
  "response": {
    "status": "success",
    "data/message": "revenue expense data or success message"
  }
}
```

```json
{
  "name": "Save HR Revenue Expense - Update",
  "url": "/api/save_hr_revenue_expense/<int:hr_rev_exp_id>/",
  "method": "PATCH",
  "request_payload": {
    "total_revenue": "decimal",
    "total_expense": "decimal"
  },
  "response": {
    "status": "success",
    "message": "Updated successfully"
  }
}
```

---

## Reports APIs

### 63. Monthly Attendance Report
```json
{
  "name": "Monthly Attendance Report",
  "url": "/api/attendance/monthly-report/",
  "method": "POST",
  "request_payload": {
    "year": "integer - required (financial year start)"
  },
  "response": [
    {
      "Employee ID": "string",
      "Name": "string",
      "Department": "string",
      "Designation": "string",
      "Division": "string",
      "Sub-Division": "string",
      "Level": "string",
      "Headquarter": "string",
      "Line Manager": "string",
      "D.O.J": "date string",
      "Apr": "float - days present",
      "May": "float",
      "June": "float",
      "July": "float",
      "Aug": "float",
      "Sept": "float",
      "Oct": "float",
      "Nov": "float",
      "Dec": "float",
      "Jan": "float",
      "Feb": "float",
      "March": "float",
      "Total": "float"
    }
  ]
}
```

### 64. Monthly Leave Report
```json
{
  "name": "Monthly Leave Report",
  "url": "/api/leave/monthly-report/",
  "method": "POST",
  "request_payload": {
    "year": "integer - required"
  },
  "response": [
    {
      "Employee ID": "string",
      "Name": "string",
      "Department": "string",
      "Designation": "string",
      "Division": "string",
      "Sub-Division": "string",
      "Level": "string",
      "Headquarter": "string",
      "Line Manager": "string",
      "D.O.J": "date string",
      "Apr": "float - leave days",
      "May": "float",
      "...": "other months",
      "Total": "float"
    }
  ]
}
```

### 65. Leave Balance Report
```json
{
  "name": "Leave Balance Report",
  "url": "/api/leave/balance-report/",
  "method": "POST",
  "request_payload": {
    "year": "integer - required"
  },
  "response": [
    {
      "Employee ID": "string",
      "Name": "string",
      "Department": "string",
      "Designation": "string",
      "Division": "string",
      "Sub-Division": "string",
      "Level": "string",
      "Headquarter": "string",
      "Line Manager": "string",
      "D.O.J": "date string",
      "CASUAL LEAVE": {
        "ALLOCATED": "float",
        "USED": "float",
        "BALANCE": "float"
      },
      "MEDICAL": {
        "ALLOCATED": "float",
        "USED": "float",
        "BALANCE": "float"
      },
      "PAID LEAVE": {
        "OPENING BALANCE": "float",
        "EARN": "float",
        "USED": "float",
        "BALANCE": "float"
      },
      "MATERNITY LEAVE": "...",
      "PATERNITY LEAVE": "..."
    }
  ]
}
```

### 66. New Joiner Report
```json
{
  "name": "New Joiner Report",
  "url": "/api/new-joiner-report/",
  "method": "POST",
  "request_payload": {
    "from": "date string (YYYY-MM-DD) - required",
    "to": "date string (YYYY-MM-DD) - required"
  },
  "response": [
    {
      "Employee ID": "string",
      "Name": "string",
      "Department": "string",
      "Designation": "string",
      "Division": "string",
      "Sub-Division": "string",
      "Level": "string",
      "Headquarter": "string",
      "Line Manager": "string",
      "D.O.J": "date string"
    }
  ]
}
```

### 67. Annual Manpower Report
```json
{
  "name": "Annual Manpower Report",
  "url": "/api/manpower-report/",
  "method": "GET",
  "request_payload": {
    "year": "integer - query param - required"
  },
  "response": {
    "financial_year": "string (e.g., 2024-2025)",
    "months": ["Apr-2024", "May-2024", "..."],
    "data": [
      {
        "sr_no": "integer",
        "department_id": "integer",
        "department_name": "string",
        "manpower_counts": [
          {"month": "Apr-2024", "count": "integer"}
        ],
        "total_for_department": "integer"
      }
    ]
  }
}
```

### 68. Employee Attrition Rate Report
```json
{
  "name": "Employee Attrition Rate Report",
  "url": "/api/employee-attrition-report/",
  "method": "GET",
  "request_payload": {
    "year": "integer - query param - required",
    "department_id": "integer - query param (optional)",
    "division_id": "integer - query param (optional)"
  },
  "response": [
    {
      "Sr No": "integer",
      "Month": "string",
      "Start": "integer - employees at month start",
      "New Joinees": "integer",
      "Exit": "integer",
      "End": "integer - employees at month end",
      "Attrition Rate (%)": "float"
    },
    {"Month": "Q I", "...quarterly totals..."},
    {"Grand Total": true, "...annual totals..."}
  ]
}
```

### 69. Employee Master Report
```json
{
  "name": "Employee Master Report",
  "url": "/api/employee_master_report/",
  "method": "GET",
  "request_payload": {},
  "response": [
    {
      "Sr No.": "integer",
      "Employee ID": "string",
      "Name": "string",
      "Contact Number (Personal)": "string",
      "Email Id (Personal)": "string",
      "Gender": "string",
      "Date of Birth": "date",
      "Age": "integer",
      "Marital Status": "string",
      "Blood Group": "string",
      "Education": "string",
      "Degree": "string",
      "Address": "string",
      "Country": "string",
      "State": "string",
      "Pin code": "string",
      "Department": "string",
      "Designation": "string",
      "Division": "string",
      "D.O.J.": "date",
      "Status": "string",
      "Account Holder Name": "string",
      "Account Number": "string",
      "Bank Name": "string",
      "IFSC": "string",
      "Emergency Contact Name": "string",
      "Emergency Contact Number": "string",
      "Exit Date": "date or null",
      "No. of Asset Allocated": "integer",
      "Assets": "array of asset objects"
    }
  ]
}
```

### 70. HR Master Data
```json
{
  "name": "HR Master Data",
  "url": "/api/hr-master-data/",
  "method": "POST",
  "request_payload": {
    "status": "string - Active/Inactive/All (default: All)"
  },
  "response": {
    "status": "success",
    "data": [
      {
        "Employee ID": "string",
        "Name": "string",
        "Gender": "string",
        "Date of Birth": "date",
        "Age": "integer",
        "Marital Status": "string",
        "Blood Group": "string",
        "Department": "string",
        "Designation": "string",
        "Division": "string",
        "D.O.J.": "date",
        "Work Duration": "string",
        "Holiday Hub": "string",
        "Adhar No.": "string",
        "PAN No.": "string",
        "UAN No.": "string",
        "Line Manager": "string",
        "Manager Name": "string",
        "CTC": "decimal",
        "Gross Salary": "decimal",
        "Basic + DA": "decimal",
        "Date of Confirmation": "date",
        "Status": "string"
      }
    ]
  }
}
```

### 71. Employee Exit Report
```json
{
  "name": "Employee Exit Report",
  "url": "/api/employee-exit-report/",
  "method": "POST",
  "request_payload": {
    "from": "date string (YYYY-MM-DD) - required",
    "to": "date string (YYYY-MM-DD) - required"
  },
  "response": {
    "status": "success",
    "data": [
      {
        "Employee ID": "string",
        "Name": "string",
        "Department": "string",
        "Designation": "string",
        "Division": "string",
        "Line Manager": "string",
        "D.O.J": "date string",
        "Exit Type": "string",
        "Last Working Date": "date string",
        "Return Asset": "Yes/No",
        "Exit Interview Questionnaire": "string",
        "Employee Clearance Form": "string",
        "Full & Final settlement": "string",
        "Relieving letter": "string",
        "Experience Letter": "string"
      }
    ]
  }
}
```

### 72. Performance Management Report
```json
{
  "name": "Performance Management Report",
  "url": "/api/performance-management-report/",
  "method": "POST",
  "request_payload": {
    "employee_id": "string/integer - required (0 for all employees)"
  },
  "response": {
    "status": "success",
    "data": [
      {
        "Employee ID": "string",
        "Name": "string",
        "Department": "string",
        "Designation": "string",
        "Division": "string",
        "Sub-Division": "string",
        "Level": "string",
        "Headquarter": "string",
        "Line Manager": "string",
        "D.O.J": "date string",
        "Financial Year": "string (e.g., 2025-2026)",
        "PDR": "string"
      }
    ]
  }
}
```

### 73. Annual Appraisal Report
```json
{
  "name": "Annual Appraisal Report",
  "url": "/api/annual-appraisal-report/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": "success",
    "data": [
      {
        "Employee ID": "string",
        "Name": "string",
        "Department": "string",
        "Designation": "string",
        "Division": "string",
        "Line Manager": "string",
        "D.O.J": "date string",
        "KIP Ach %": "string",
        "KRA Ach %": "string",
        "Total Ach %": "string",
        "Final Rating": "string",
        "LM Feedback": "string",
        "HOD Feedback": "string",
        "HR Feedback": "string",
        "Employee Comment": "string",
        "Reccommended Action": "string",
        "% of Increment": "string",
        "Status": "string"
      }
    ]
  }
}
```

### 74. Salary Report
```json
{
  "name": "Salary Report",
  "url": "/api/salary-report/",
  "method": "GET",
  "request_payload": {
    "month": "integer - query param - required",
    "year": "integer - query param - required"
  },
  "response": [
    {
      "sr_no": "integer",
      "employee_id": "string",
      "employee_name": "string",
      "department": "string",
      "designation": "string",
      "gender": "string",
      "gross_salary": "decimal",
      "days": "integer - payable days",
      "esic_applicable": "string",
      "gross_earning": "decimal",
      "basic_da": "decimal",
      "hra": "decimal",
      "conveyance_allowance": "decimal",
      "medical_allowance": "decimal",
      "arrears": "decimal",
      "pf": "decimal",
      "esic": "decimal",
      "pt": "decimal",
      "tds": "decimal",
      "total_deduction": "decimal",
      "net_pay": "decimal",
      "remark": "string",
      "bank_name": "string",
      "ifsc_code": "string",
      "account_number": "string",
      "account_holder_name": "string"
    }
  ]
}
```

### 75. PT Report
```json
{
  "name": "PT Report",
  "url": "/api/pt-report/",
  "method": "GET",
  "request_payload": {
    "month": "integer - query param - required",
    "year": "integer - query param - required"
  },
  "response": [
    {
      "sr_no": "integer",
      "employee_id": "string",
      "employee_name": "string",
      "days": "integer",
      "salary_per_month": "decimal",
      "total_earnings": "decimal",
      "pt": "decimal"
    }
  ]
}
```

---

## Dashboard APIs

### 76. HR Dashboard Metrics
```json
{
  "name": "HR Dashboard Metrics",
  "url": "/api/hr_dashboard_metrics/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "status": true,
    "message": "HR Dashboard metrics fetched successfully",
    "data": {
      "period": {
        "month": "integer",
        "year": "integer",
        "month_name": "string"
      },
      "total_number_of_employees": "integer",
      "last_month_total_revenue": "float",
      "per_employee_contribution": "float",
      "monthly_total_salary": "float",
      "monthly_expenses": "float",
      "total_employee_cost": "float",
      "per_employee_cost": "float",
      "per_employee_revenue": "float"
    }
  }
}
```

### 77. HR Dashboard Metrics By Month
```json
{
  "name": "HR Dashboard Metrics By Month",
  "url": "/api/hr_dashboard_metrics_by_month/",
  "method": "GET",
  "request_payload": {
    "month": "integer - query param (1-12) - required",
    "year": "integer - query param - required"
  },
  "response": {
    "status": true,
    "message": "HR Dashboard metrics fetched successfully",
    "data": {
      "period": {
        "month": "integer",
        "year": "integer",
        "month_name": "string"
      },
      "total_number_of_employees": "integer",
      "total_revenue": "float",
      "per_employee_contribution": "float",
      "monthly_total_salary": "float",
      "monthly_expenses": "float",
      "total_employee_cost": "float",
      "per_employee_cost": "float",
      "per_employee_revenue": "float"
    }
  }
}
```

### 78. HR Dashboard Graphs
```json
{
  "name": "HR Dashboard Graphs",
  "url": "/api/hr_dashboard_graphs/",
  "method": "GET",
  "request_payload": {
    "year": "integer - query param (optional, defaults to current FY)"
  },
  "response": {
    "status": true,
    "message": "HR Dashboard graph data fetched successfully",
    "financial_year": "string (e.g., FY 2025-26)",
    "data": {
      "ticket": {
        "labels": ["CRITICAL", "HIGH", "MEDIAL", "LOW"],
        "datasets": [
          {"label": "Raised", "data": "..."},
          {"label": "Closed", "data": "..."}
        ]
      },
      "payroll": [
        {"month": "April", "total_employee_cost": "float"}
      ],
      "attrition_rate": [
        {"month": "April", "attrition_rate": "float"}
      ],
      "employee_level": {
        "labels": ["L1", "L2", "L3", "L4"],
        "datasets": [
          {"label": "0 to 3 yr", "data": "..."},
          {"label": "3 to 5 yr", "data": "..."},
          {"label": "5+ yr", "data": "..."}
        ]
      },
      "recruitment_tracker": {
        "labels": ["Total", "Open", "In process"],
        "data": "..."
      },
      "employee_separation": {
        "labels": ["April", "May", "..."],
        "datasets": [
          {"label": "Total Resigned", "data": "..."},
          {"label": "Accepted", "data": "..."},
          {"label": "F & F Proceed", "data": "..."}
        ]
      },
      "performance_management_matrix": {
        "labels": ["Q I", "Q II", "Q III", "Q IV"],
        "datasets": [
          {"label": "Exceed Expectation", "data": "..."},
          {"label": "Exceptional", "data": "..."},
          {"label": "Meet Exp.", "data": "..."},
          {"label": "Below Exp.", "data": "..."},
          {"label": "Unsatisfactory", "data": "..."}
        ]
      }
    }
  }
}
```

---

## OTP & Authentication APIs

### 79. Send OTP
```json
{
  "name": "Send OTP",
  "url": "/api/send_otp/",
  "method": "POST",
  "request_payload": {
    "email_id": "string - required"
  },
  "response": {
    "status": true,
    "message": "OTP sent successfully to your email",
    "email": "string"
  }
}
```

### 80. Verify OTP
```json
{
  "name": "Verify OTP",
  "url": "/api/verify_otp/",
  "method": "POST",
  "request_payload": {
    "email_id": "string - required",
    "otp": "string - required (6 digits)"
  },
  "response": {
    "status": true,
    "message": "OTP verified successfully"
  }
}
```

### 81. Reset Password
```json
{
  "name": "Reset Password",
  "url": "/api/reset_password/",
  "method": "POST",
  "request_payload": {
    "email_id": "string - required",
    "new_password": "string - required"
  },
  "response": {
    "status": true,
    "message": "Password reset successfully"
  }
}
```

---

## Role Management APIs

### 82. User Role Permissions
```json
{
  "name": "User Role Permissions",
  "url": "/api/roles/user-permissions/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "user_id": "integer",
    "user_type": "string",
    "role_id": "integer",
    "role_name": "string",
    "role_access": "string (1=All Menu, 2=Custom Menu)",
    "role_access_label": "string",
    "permissions": ["array of permission strings"],
    "has_all_access": "boolean"
  }
}
```

```json
{
  "name": "User Role Permissions By ID",
  "url": "/api/roles/user-permissions/<int:user_id>/",
  "method": "GET",
  "request_payload": {},
  "response": "same as above"
}
```

### 83. Check Permission
```json
{
  "name": "Check Permission",
  "url": "/api/roles/check-permission/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer (optional - uses JWT if not provided)",
    "permission": "string - required"
  },
  "response": {
    "has_permission": "boolean",
    "permission": "string",
    "user_id": "integer",
    "role_name": "string"
  }
}
```

### 84. Check Multiple Permissions
```json
{
  "name": "Check Multiple Permissions",
  "url": "/api/roles/check-multiple-permissions/",
  "method": "POST",
  "request_payload": {
    "user_id": "integer (optional)",
    "permissions": ["array of permission strings - required"]
  },
  "response": {
    "user_id": "integer",
    "role_name": "string",
    "has_all_access": "boolean",
    "results": {
      "permission1": "boolean",
      "permission2": "boolean"
    },
    "granted": ["array of granted permissions"],
    "denied": ["array of denied permissions"]
  }
}
```

### 85. Create Role
```json
{
  "name": "Create Role",
  "url": "/api/roles/create/",
  "method": "POST",
  "request_payload": {
    "type": "add_record - required",
    "role_name": "string - required (min 3 chars)",
    "role_access": "string - required (1=All Menu, 2=Custom Menu)",
    "role_resources": ["array of permission strings"]
  },
  "response": {
    "result": "Role has been successfully added.",
    "error": "",
    "csrf_hash": ""
  }
}
```

### 86. Update Role
```json
{
  "name": "Update Role",
  "url": "/api/roles/update/",
  "method": "POST",
  "request_payload": {
    "type": "edit_record - required",
    "role_id": "integer - required",
    "role_name": "string - required",
    "role_access": "string - required",
    "role_resources": ["array of permission strings"]
  },
  "response": {
    "result": "Role has been successfully updated.",
    "error": "",
    "csrf_hash": ""
  }
}
```

### 87. Delete Role
```json
{
  "name": "Delete Role",
  "url": "/api/roles/delete/<int:role_id>/",
  "method": "POST",
  "request_payload": {},
  "response": {
    "result": "Role has been successfully deleted.",
    "error": "",
    "csrf_hash": ""
  }
}
```

### 88. List Roles
```json
{
  "name": "List Roles",
  "url": "/api/roles/list/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "data": [
      {
        "role_id": "integer",
        "role_name": "string",
        "role_access": "string",
        "role_resources": "string (comma-separated)",
        "role_resources_array": ["array"],
        "role_access_label": "string",
        "created_at": "datetime string"
      }
    ]
  }
}
```

---

## Training Management APIs

### 89. Create Training
```json
{
  "name": "Create Training",
  "url": "/api/training/create/",
  "method": "POST",
  "request_payload": {
    "type": "add_record - required",
    "trainer": "integer - trainer ID - required",
    "training_type": "integer - training type/skill ID - required",
    "training_cost": "string/decimal",
    "employee_id": ["array of employee IDs"],
    "start_date": "date string (YYYY-MM-DD) - required",
    "end_date": "date string (YYYY-MM-DD) - required",
    "description": "string"
  },
  "response": {
    "result": "Training session has been successfully added.",
    "error": "",
    "csrf_hash": ""
  }
}
```

### 90. Update Training
```json
{
  "name": "Update Training",
  "url": "/api/training/update/",
  "method": "POST",
  "request_payload": {
    "type": "edit_record - required",
    "training_id": "integer - required",
    "trainer": "integer",
    "training_type": "integer",
    "training_cost": "string/decimal",
    "employee_id": ["array of employee IDs"],
    "start_date": "date string",
    "end_date": "date string",
    "description": "string"
  },
  "response": {
    "result": "Training session has been successfully updated.",
    "error": "",
    "csrf_hash": ""
  }
}
```

### 91. Delete Training
```json
{
  "name": "Delete Training",
  "url": "/api/training/delete/<int:training_id>/",
  "method": "POST",
  "request_payload": {},
  "response": {
    "result": "Training session has been successfully deleted.",
    "error": "",
    "csrf_hash": ""
  }
}
```

### 92. List Trainings
```json
{
  "name": "List Trainings",
  "url": "/api/training/list/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "data": [
      {
        "training_id": "integer",
        "company_id": "integer",
        "employee_id": "string (comma-separated)",
        "employee_id_array": ["array"],
        "training_type_id": "integer",
        "training_type_name": "string",
        "trainer_id": "integer",
        "trainer_name": "string",
        "start_date": "date",
        "finish_date": "date",
        "training_cost": "decimal",
        "description": "string",
        "training_status": "integer (0=Pending, 1=Active, 2=Completed, 3=Cancelled)",
        "status_label": "string",
        "performance": "integer",
        "remarks": "string",
        "created_at": "datetime string"
      }
    ]
  }
}
```

### 93. Training Details
```json
{
  "name": "Training Details",
  "url": "/api/training/details/<int:training_id>/",
  "method": "GET",
  "request_payload": {},
  "response": {
    "data": {
      "training_id": "integer",
      "employee_id": "string",
      "trainer_id": "integer",
      "trainer_name": "string",
      "trainer_email": "string",
      "training_type_name": "string",
      "start_date": "date",
      "finish_date": "date",
      "training_cost": "decimal",
      "description": "string",
      "training_status": "integer",
      "performance": "integer",
      "remarks": "string",
      "assigned_employees": [
        {
          "user_id": "integer",
          "first_name": "string",
          "last_name": "string",
          "full_name": "string",
          "email": "string",
          "emp_code": "string"
        }
      ]
    }
  }
}
```

### 94. Update Training Status
```json
{
  "name": "Update Training Status",
  "url": "/api/training/update-status/",
  "method": "POST",
  "request_payload": {
    "training_id": "integer - required",
    "training_status": "integer - required (0=Pending, 1=Active, 2=Completed, 3=Cancelled)",
    "performance": "integer (0-100)",
    "remarks": "string"
  },
  "response": {
    "result": "Training status has been successfully updated.",
    "error": "",
    "csrf_hash": ""
  }
}
```

---

## Summary

**Total APIs Documented: 94 endpoints**

| Category | Count |
|----------|-------|
| Dropdown APIs | 8 |
| Account Details APIs | 10 |
| Employee Panel APIs | 10 |
| Admin Panel APIs | 28 |
| Reports APIs | 13 |
| Dashboard APIs | 3 |
| OTP & Authentication APIs | 3 |
| Role Management APIs | 7 |
| Training Management APIs | 6 |

---

*Document generated from hrms_app module analysis*

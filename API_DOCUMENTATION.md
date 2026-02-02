# HRMS API Documentation

> **Complete API Reference for Frontend Development**  
> Last Updated: January 31, 2026

---

## Table of Contents

1. [App Module APIs](#1-app-module-apis-base-url-)
2. [HRMS App Module APIs](#2-hrms-app-module-apis-base-url-api)
3. [M_App Module APIs](#3-m_app-module-apis-base-url-apps)
4. [New HRMS Module APIs](#4-new-hrms-module-apis-base-url-apis)
5. [VetHR Module APIs](#5-vethr-module-apis-base-url-api)

---

# 1. App Module APIs (Base URL: `/`)

## 1.1 Authentication APIs

### Login
| Field | Value |
|-------|-------|
| **Name** | User Login |
| **URL** | `/login/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "username": "string (required)",
    "password": "string (required)"
}
```

**Response:**
```json
{
    "refresh": "string (JWT refresh token)",
    "access": "string (JWT access token)",
    "user_id": 1,
    "employee_id": "EMP001",
    "role": "Admin",
    "role_id": 1,
    "is_hod": true,
    "email": "user@example.com",
    "designation_id": 1,
    "designation_name": "Manager",
    "role_resources": "string (comma-separated permissions)"
}
```

---

### Registration
| Field | Value |
|-------|-------|
| **Name** | User Registration |
| **URL** | `/register/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "username": "string (required)",
    "email": "string (required)",
    "password": "string (required)"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "user": {
        "username": "string",
        "email": "string"
    }
}
```

---

### Change Password
| Field | Value |
|-------|-------|
| **Name** | Change Password |
| **URL** | `/change-password/` |
| **Method** | `PATCH` |

**Request Payload:**
```json
{
    "old_password": "string (required)",
    "new_password": "string (required)"
}
```

**Response:**
```json
{
    "Message": "Success"
}
```

---

### Forgot Password
| Field | Value |
|-------|-------|
| **Name** | Forgot Password |
| **URL** | `/forgot-password/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "email": "string (required)"
}
```

**Response:**
```json
{
    "message": "Password reset link sent to your email"
}
```

---

### Reset Password Confirm
| Field | Value |
|-------|-------|
| **Name** | Reset Password Confirm |
| **URL** | `/reset-password-confirm/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "token": "string (required)",
    "new_password": "string (required)"
}
```

**Response:**
```json
{
    "message": "Password reset successful"
}
```

---

## 1.2 Employee/User APIs

### Basic Info
| Field | Value |
|-------|-------|
| **Name** | Get/Update Basic Info |
| **URL** | `/basic-info/` |
| **Method** | `GET`, `PATCH` |

**Request Payload (PATCH):**
```json
{
    "first_name": "string",
    "middle_name": "string",
    "last_name": "string",
    "contact_number": "string",
    "gender": "string",
    "date_of_birth": "YYYY-MM-DD",
    "marital_status": "string",
    "state": "string",
    "city": "string",
    "zipcode": "string",
    "religion_id": 1,
    "blood_group": "string",
    "country": "string",
    "citizenship_id": 1,
    "address_1": "string",
    "address_2": "string"
}
```

**Response (GET):**
```json
{
    "status": "Success",
    "BasicInfo": {
        "id": 1,
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "email": "string"
    }
}
```

---

### Employee Details
| Field | Value |
|-------|-------|
| **Name** | Get Employee Details |
| **URL** | `/api/employee/<int:user_id>/` |
| **Method** | `GET` |

**Response:**
```json
{
    "user_id": 1,
    "employee_id": "EMP001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "designation": "Software Engineer",
    "department": "IT"
}
```

---

### Family Members
| Field | Value |
|-------|-------|
| **Name** | Family Members CRUD |
| **URL** | `/api/family-members-user/<int:user_id>/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/family-members/<int:family_member_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "user_id": 1,
    "family_member_name": "string (required)",
    "relationship": "string (required)",
    "contact_number": "string"
}
```

**Response:**
```json
{
    "message": "Family member added successfully"
}
```

---

### Employee Shift
| Field | Value |
|-------|-------|
| **Name** | Get Employee Shift |
| **URL** | `/api/employee/shift/<int:user_id>/` |
| **Method** | `GET` |

**Response:**
```json
{
    "shift_id": 1,
    "shift_name": "Day Shift",
    "start_time": "09:00:00",
    "end_time": "18:00:00"
}
```

---

## 1.3 Attendance APIs

### Today Attendance
| Field | Value |
|-------|-------|
| **Name** | Today's Attendance |
| **URL** | `/today-attendence/` |
| **Method** | `GET` |

**Response:**
```json
{
    "data": [
        {
            "user_id": 1,
            "emp_name": "John Doe",
            "attendance_date": "2026-01-31",
            "attendance_status": "Present",
            "punch_in_time": "09:00:00"
        }
    ]
}
```

---

### Today's Attendance Report
| Field | Value |
|-------|-------|
| **Name** | Today's Attendance Report |
| **URL** | `/attendance/today/` |
| **Method** | `GET` |

**Response:**
```json
{
    "date": "2026-01-31",
    "total_records": 50,
    "data": [
        {
            "employee": "John Doe",
            "email": "john@example.com",
            "emp_id": 1,
            "date": "2026-01-31",
            "status": "Present",
            "clock_in": "09:00:00",
            "clock_out": "18:00:00",
            "late": "No",
            "early_leaving": "No",
            "total_work": "09:00:00"
        }
    ]
}
```

---

### Attendance By Date Report
| Field | Value |
|-------|-------|
| **Name** | Attendance By Date Report |
| **URL** | `/attendance/by-date/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "emp_id": 1,
    "date": "2026-01-31",
    "status": "Present"
}
```

**Response:**
```json
{
    "date": "2026-01-31",
    "total_records": 10,
    "data": []
}
```

---

### My Attendance (Employee)
| Field | Value |
|-------|-------|
| **Name** | My Attendance |
| **URL** | `/my_attendance/<str:empid>/` |
| **Method** | `GET` |

**Response:**
```json
{
    "attendance_records": []
}
```

---

### Monthly Report (Manager-wise)
| Field | Value |
|-------|-------|
| **Name** | Monthly Report |
| **URL** | `/emp_monthly_report/` |
| **Method** | `GET` |

---

### Punch Report
| Field | Value |
|-------|-------|
| **Name** | Punch Report |
| **URL** | `/punch_reports/` |
| **Method** | `GET`, `POST` |

---

## 1.4 Leave Management APIs

### Leave Applications
| Field | Value |
|-------|-------|
| **Name** | Leave Applications |
| **URL** | `/api/leave-applications/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/leave-applications/<int:leave_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "employee_id": "EMP001",
    "leave_type_id": 1,
    "from_date": "2026-02-01",
    "to_date": "2026-02-03",
    "reason": "Personal work",
    "is_half_day": false
}
```

**Response:**
```json
{
    "message": "Leave application submitted successfully"
}
```

---

### Leave Types
| Field | Value |
|-------|-------|
| **Name** | Leave Types List |
| **URL** | `/api/leave-types/` |
| **Method** | `GET` |

**Response:**
```json
[
    {
        "constants_id": 1,
        "category_name": "Casual Leave"
    },
    {
        "constants_id": 2,
        "category_name": "Sick Leave"
    }
]
```

---

### Leave Setup
| Field | Value |
|-------|-------|
| **Name** | Leave Setup |
| **URL** | `/api/leave-setup/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/leave-setup/<int:id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "category_name": "string (leave type)",
    "field_one": 12,
    "field_two": "setup rules"
}
```

---

### Leave Applications Dashboard
| Field | Value |
|-------|-------|
| **Name** | Leave Applications Dashboard |
| **URL** | `/api/leave-applications-dashboard/` |
| **Method** | `GET` |

**Response:**
```json
{
    "upcoming_holiday": {
        "event_name": "Republic Day",
        "start_date": "2026-01-26",
        "end_date": "2026-01-26",
        "country": "India",
        "state": "Maharashtra",
        "employee_hub": "Mumbai",
        "status": "Published"
    },
    "leave_type_wise_leaves": [],
    "department_wise_leaves": []
}
```

---

### Leave Pending Current Month
| Field | Value |
|-------|-------|
| **Name** | Leave Pending Current Month |
| **URL** | `/api/leave-pending-current-month/` |
| **Method** | `GET` |

**Response:**
```json
[
    {
        "employee_name": "John Doe",
        "date": "2026-02-01 to 2026-02-03",
        "number_of_days": 3,
        "reason": "Personal work",
        "status": "Pending"
    }
]
```

---

### Department Leave Report
| Field | Value |
|-------|-------|
| **Name** | Department Leave Report |
| **URL** | `/department_leave_report/` |
| **Method** | `GET` |

---

## 1.5 CompOff APIs

### CompOff Management
| Field | Value |
|-------|-------|
| **Name** | CompOff CRUD |
| **URL** | `/compoff/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/compoff/<int:compoff_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "employee_name": "John Doe",
    "start_date_compoff": "2026-01-25",
    "end_date_compoff": "2026-01-25",
    "compoff_reason": "Worked on holiday"
}
```

**Request Payload (PATCH):**
```json
{
    "compoff_status": "A"
}
```

**Response (GET):**
```json
[
    {
        "compoff_id": 1,
        "emp_id": "EMP001",
        "employee_name": "John Doe",
        "start_date_compoff": "2026-01-25",
        "end_date_compoff": "2026-01-25",
        "no_of_days": 1,
        "compoff_reason": "Worked on holiday",
        "compoff_status": "Pending",
        "created_at": "2026-01-26 10:00:00",
        "is_expired": "2026-04-25"
    }
]
```

---

### On Duty Request
| Field | Value |
|-------|-------|
| **Name** | On Duty Request |
| **URL** | `/on-duty-request/` |
| **Method** | `POST` |

**Response:**
```json
{
    "message": "OD Created"
}
```

---

## 1.6 Department APIs

### Departments CRUD
| Field | Value |
|-------|-------|
| **Name** | Departments |
| **URL** | `/departments/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/departments/<int:pk>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "department_name": "Human Resources",
    "department_code": "HR",
    "department_head": "EMP001",
    "company_id": 2,
    "added_by": 1
}
```

**Response (GET):**
```json
[
    {
        "department_id": 1,
        "department_name": "Human Resources",
        "department_code": "HR",
        "company_id": 2,
        "department_head": "EMP001",
        "department_head_name": "John Doe",
        "added_by": 1,
        "created_at": "2026-01-01 10:00:00"
    }
]
```

---

## 1.7 Designation APIs

### Designations CRUD
| Field | Value |
|-------|-------|
| **Name** | Designations |
| **URL** | `/ci_designations/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/ci_designations/<int:pk>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "department_id": 1,
    "designation_name": "Software Engineer",
    "designation_code": "SE",
    "line_manager_id": 2,
    "description": "Engineering role",
    "company_id": 2
}
```

**Response (GET):**
```json
[
    {
        "designation_id": 1,
        "company_id": 2,
        "designation_name": "Software Engineer",
        "designation_code": "SE",
        "line_manager_id": 2,
        "line_manager_name": "Senior Engineer",
        "description": "Engineering role",
        "created_at": "2026-01-01",
        "department_id": 1,
        "department_name": "IT"
    }
]
```

---

## 1.8 Division APIs

### Divisions CRUD
| Field | Value |
|-------|-------|
| **Name** | Divisions |
| **URL** | `/api/division/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/division/<int:division_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "division_name": "North Region",
    "division_code": "NR"
}
```

**Response (GET):**
```json
[
    {
        "division_id": 1,
        "division_name": "North Region",
        "division_code": "NR",
        "created_at": "2026-01-01"
    }
]
```

---

## 1.9 Grade APIs

### Grades CRUD
| Field | Value |
|-------|-------|
| **Name** | Grades |
| **URL** | `/api/grade/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/grade/<int:id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "grade_id": "G1",
    "grade_name": "Grade 1",
    "grade_code": "G1"
}
```

**Response (GET):**
```json
[
    {
        "grade_id": 1,
        "grade_name": "Grade 1",
        "grade_code": "G1",
        "created_date": "2026-01-01"
    }
]
```

---

## 1.10 Headquarters APIs

### Headquarters CRUD
| Field | Value |
|-------|-------|
| **Name** | Headquarters |
| **URL** | `/api/headquarters/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/headquarters/<int:headquarter_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "headquarter_name": "Mumbai HQ",
    "headquarter_code": "MUM",
    "headquarter_address": "123 Business Park, Mumbai",
    "company_id": 2,
    "status": "Y"
}
```

**Response (GET):**
```json
[
    {
        "headquarter_id": 1,
        "headquarter_name": "Mumbai HQ",
        "headquarter_code": "MUM",
        "headquarter_address": "123 Business Park, Mumbai",
        "created_at": "2026-01-01"
    }
]
```

---

## 1.11 Staff Roles APIs

### Staff Roles CRUD
| Field | Value |
|-------|-------|
| **Name** | Staff Roles |
| **URL** | `/roles/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/roles/<int:role_id>/` |
| **Detail Method** | `DELETE` |

**Request Payload (POST):**
```json
{
    "role_name": "Team Lead",
    "role_resources": "dashboard,employees,reports"
}
```

**Response (GET):**
```json
[
    {
        "role_id": 1,
        "role_name": "Admin"
    },
    {
        "role_id": 2,
        "role_name": "Employee"
    }
]
```

---

### Staff Role API (Full CRUD)
| Field | Value |
|-------|-------|
| **Name** | Staff Role API |
| **URL** | `/api/staffrole/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/staffrole/<int:role_id>/` |
| **Detail Method** | `GET`, `PATCH`, `DELETE` |

**Response (POST):**
```json
{
    "message": "Role created successfully",
    "role_id": 5,
    "role_name": "Team Lead",
    "company_id": 2,
    "created_at": "2026-01-31 10:00:00"
}
```

---

## 1.12 Office Shifts APIs

### Office Shifts CRUD
| Field | Value |
|-------|-------|
| **Name** | Office Shifts |
| **URL** | `/shifts/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/shifts/<int:office_shift_id>/` |
| **Detail Method** | `PUT`, `DELETE` |

**Request Payload (POST):**
```json
{
    "shift_name": "Morning Shift",
    "start_time": "06:00:00",
    "end_time": "14:00:00"
}
```

---

## 1.13 Policy APIs

### Policies CRUD
| Field | Value |
|-------|-------|
| **Name** | Policies |
| **URL** | `/policies/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/policies/<int:pk>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST - multipart/form-data):**
```json
{
    "title": "Leave Policy",
    "description": "Company leave policy document",
    "added_by": 1,
    "attachment": "file (PDF)",
    "company_id": 2
}
```

**Response (GET):**
```json
{
    "message": "Policies retrieved successfully",
    "data": [
        {
            "policy_id": 1,
            "company_id": 2,
            "title": "Leave Policy",
            "description": "Company leave policy",
            "attachment": {
                "file_name": "leave_policy.pdf",
                "file_url": "/media/policies/leave_policy.pdf"
            },
            "added_by": 1,
            "created_at": "2026-01-01"
        }
    ]
}
```

---

### Acknowledge Policy
| Field | Value |
|-------|-------|
| **Name** | Acknowledge Policy |
| **URL** | `/acknowledge_policy/` |
| **Method** | `GET` |
| **Detail URL** | `/acknowledge_policy/<int:policy_id>/` |

**Response:**
```json
{
    "message": "Policy acknowledgements retrieved successfully",
    "data": []
}
```

---

### Policy Dashboard
| Field | Value |
|-------|-------|
| **Name** | Policy Dashboard |
| **URL** | `/policy-dashboard/` |
| **Method** | `GET` |

**Response:**
```json
{
    "message": "Employee policy acknowledgement status",
    "acknowledged": [],
    "not_acknowledged": [],
    "partially_acknowledged": []
}
```

---

### Policy Allocation
| Field | Value |
|-------|-------|
| **Name** | Policy Allocation |
| **URL** | `/api/policy-allocation/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/policy-allocation/<int:policy_allocation_id>/` |
| **Detail Method** | `PATCH` |
| **Delete URL** | `/api/policy-allocation/<str:employee_id>/` |
| **Delete Method** | `DELETE` |

---

### Employee Assigned Policies
| Field | Value |
|-------|-------|
| **Name** | Employee Assigned Policies |
| **URL** | `/policies/assigned/<str:emp_id>/` |
| **Method** | `GET` |

---

### Acknowledge Policy (Employee)
| Field | Value |
|-------|-------|
| **Name** | Acknowledge Policy |
| **URL** | `/policies/acknowledge/<str:emp_id>/` |
| **Method** | `POST` |

---

### Policy Signed Document APIs

#### Download Acknowledgement Template
| Field | Value |
|-------|-------|
| **URL** | `/policies/download-acknowledgement-template/<str:emp_id>/` |
| **Method** | `GET` |

#### Upload Signed Document
| Field | Value |
|-------|-------|
| **URL** | `/policies/upload-signed-document/<str:emp_id>/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "signed_document": "file"
}
```

#### Signed Document Status
| Field | Value |
|-------|-------|
| **URL** | `/policies/signed-document-status/<str:emp_id>/` |
| **Method** | `GET` |

#### View Signed Document
| Field | Value |
|-------|-------|
| **URL** | `/policies/view-signed-document/<str:emp_id>/` |
| **Method** | `GET` |

#### All Signed Documents
| Field | Value |
|-------|-------|
| **URL** | `/policies/all-signed-documents/` |
| **Method** | `GET` |

---

## 1.14 Holiday APIs

### Admin Holidays CRUD
| Field | Value |
|-------|-------|
| **Name** | Admin Holidays |
| **URL** | `/admin-holidays/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/admin-holidays/<int:holiday_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "event_name": "Republic Day",
    "country": "India",
    "state": "Maharashtra",
    "employee_hub": "Mumbai",
    "start_date": "2026-01-26",
    "end_date": "2026-01-26",
    "description": "National Holiday",
    "is_publish": "published"
}
```

**Response (GET):**
```json
[
    {
        "holiday_id": 1,
        "event_name": "Republic Day",
        "start_date": "2026-01-26",
        "end_date": "2026-01-26",
        "description": "National Holiday",
        "status": "published",
        "created_at": "2026-01-01",
        "country": "India",
        "state": "Maharashtra",
        "employee_hub": "Mumbai"
    }
]
```

---

### Employee Holidays
| Field | Value |
|-------|-------|
| **Name** | Employee Holidays |
| **URL** | `/employee/holidays/<str:employee_id>/` |
| **Method** | `GET` |
| **Alt URL** | `/Empholidays/<str:employee_id>/` |

**Response:**
```json
[
    {
        "holiday_id": 1,
        "event_name": "Republic Day",
        "description": "National Holiday",
        "start_date": "2026-01-26",
        "end_date": "2026-01-26",
        "status": "published"
    }
]
```

---

## 1.15 Event APIs

### Events CRUD
| Field | Value |
|-------|-------|
| **Name** | Events |
| **URL** | `/events/` |
| **Method** | `GET`, `POST`, `PATCH` |
| **Detail URL** | `/events/<int:event_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "employee_id": "EMP001",
    "company_id": 2,
    "event_title": "Team Meeting",
    "event_date": "2026-02-01",
    "event_time": "10:00:00",
    "event_color": "#FF5733",
    "event_note": "Monthly team sync"
}
```

**Response (GET):**
```json
[
    {
        "event_id": 1,
        "employee_id": "EMP001",
        "employee_name": "John Doe",
        "company_id": 2,
        "event_title": "Team Meeting",
        "event_date": "2026-02-01",
        "event_time": "10:00:00",
        "event_color": "#FF5733",
        "event_note": "Monthly team sync",
        "created_at": "2026-01-30"
    }
]
```

---

### Employee Events
| Field | Value |
|-------|-------|
| **Name** | Employee Events |
| **URL** | `/employee_events/<str:employee_id>/` |
| **Method** | `GET` |

---

## 1.16 Announcement APIs

### Announcements CRUD
| Field | Value |
|-------|-------|
| **Name** | Announcements |
| **URL** | `/announcements/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/announcements/<int:announcement_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "department_name": "All Departments",
    "title": "Company Update",
    "start_date": "2026-02-01",
    "end_date": "2026-02-28",
    "summary": "Important company announcement",
    "description": "Detailed description here"
}
```

**Response (GET):**
```json
{
    "message": "Announcements retrieved successfully",
    "data": [
        {
            "announcement_id": 1,
            "title": "Company Update",
            "department_name": "All Departments",
            "description": "Detailed description",
            "start_date": "2026-02-01",
            "end_date": "2026-02-28"
        }
    ]
}
```

---

## 1.17 Travel APIs

### Travels CRUD
| Field | Value |
|-------|-------|
| **Name** | Travels |
| **URL** | `/travels/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/travels/<int:travel_id>/` |
| **Detail Method** | `GET`, `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "start_date": "2026-02-15",
    "end_date": "2026-02-17",
    "associated_goals": "Client meeting",
    "visit_purpose": "Business development",
    "visit_place": "New Delhi",
    "travel_mode": "Flight",
    "arrangement_type": "Company arranged",
    "expected_budget": 50000.00,
    "actual_budget": 45000.00,
    "description": "Q1 client visit",
    "status": "Pending",
    "added_by": 1
}
```

**Response (GET):**
```json
{
    "message": "All travels fetched successfully",
    "data": [
        {
            "travel_id": 1,
            "company_id": 2,
            "employee_id": "EMP001",
            "employee_name": "John Doe",
            "start_date": "2026-02-15",
            "end_date": "2026-02-17",
            "associated_goals": "Client meeting",
            "visit_purpose": "Business development",
            "visit_place": "New Delhi",
            "travel_mode": "Flight",
            "arrangement_type": "Company arranged",
            "expected_budget": 50000.00,
            "actual_budget": 45000.00,
            "description": "Q1 client visit",
            "status": "Pending",
            "added_by": 1,
            "created_at": "2026-01-31"
        }
    ]
}
```

---

## 1.18 Training APIs

### Trainings CRUD
| Field | Value |
|-------|-------|
| **Name** | Trainings |
| **URL** | `/trainings/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/trainings/<int:pk>/` |
| **Detail Method** | `PATCH`, `DELETE` |

---

### Trainers CRUD
| Field | Value |
|-------|-------|
| **Name** | Trainers |
| **URL** | `/trainers/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/trainers/<int:pk>/` |
| **Detail Method** | `PATCH`, `DELETE` |

---

## 1.19 Award APIs

### Awards CRUD
| Field | Value |
|-------|-------|
| **Name** | Awards |
| **URL** | `/api/awards/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/awards/<int:pk>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "employee_id": "EMP001",
    "award_type_id": 1,
    "associated_goals": "Sales target achieved",
    "gift_item": "Watch",
    "cash_price": 5000.00,
    "award_photo": "url_to_photo",
    "award_month_year": "January 2026",
    "award_information": "Best performer",
    "description": "Achieved 150% of target"
}
```

**Response (GET):**
```json
[
    {
        "award_id": 1,
        "company_id": 2,
        "employee_id": "EMP001",
        "employee_name": "John Doe",
        "award_type_id": 1,
        "award_type_name": "Best Performer",
        "associated_goals": "Sales target achieved",
        "gift_item": "Watch",
        "cash_price": 5000.00,
        "award_photo": "url",
        "award_month_year": "January 2026",
        "award_information": "Best performer",
        "description": "Achieved 150% of target",
        "created_at": "2026-01-31"
    }
]
```

---

### Employee Awards
| Field | Value |
|-------|-------|
| **Name** | Employee Awards |
| **URL** | `/employee_awards/<str:employee_id>/` |
| **Method** | `GET` |

---

## 1.20 Assets APIs

### Admin Assets CRUD
| Field | Value |
|-------|-------|
| **Name** | Admin Assets |
| **URL** | `/assets/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/assets/<int:pk>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST - multipart/form-data):**
```json
{
    "assets_name": "Dell Laptop",
    "assets_category_id": 1,
    "brand_id": 1,
    "product_id": 1,
    "employee_id": "EMP001",
    "purchase_date": "2026-01-15",
    "serial_number": "DELL123456",
    "manufacturer": "Dell Inc",
    "company_asset_code": "AST001",
    "quantity": 1,
    "is_working": "yes",
    "invoice_number": "INV2026001",
    "warranty_end_date": "2029-01-15",
    "asset_note": "Assigned to IT department",
    "asset_image": "file"
}
```

**Request Payload (PATCH for action):**
```json
{
    "action": "return_yes"
}
```

**Response (GET):**
```json
[
    {
        "id": 1,
        "assets_category_id": 1,
        "category_name": "Laptop",
        "brand_id": 1,
        "brand_name": "Dell",
        "company_id": 2,
        "employee_id": "EMP001",
        "employee_name": "John Doe",
        "company_asset_code": "AST001",
        "assets_name": "Dell Laptop",
        "purchase_date": "2026-01-15",
        "invoice_number": "INV2026001",
        "manufacturer": "Dell Inc",
        "serial_number": "DELL123456",
        "warranty_end_date": "2029-01-15",
        "asset_note": "Assigned to IT department",
        "asset_image": "/media/assets/laptop.jpg",
        "is_working": "Yes",
        "created_at": "2026-01-15",
        "returned": "N",
        "employee_confirmation": "Confirmed",
        "return_request_status": "None",
        "quantity": 1,
        "return_date": null
    }
]
```

---

### Employee Assets
| Field | Value |
|-------|-------|
| **Name** | Employee Assets |
| **URL** | `/employee_assets/<str:employee_id>/` |
| **Method** | `GET` |
| **Confirm URL** | `/employee_confirm_asset/<str:pk>/` |
| **Confirm Method** | `PATCH` |

---

### Asset Requisition
| Field | Value |
|-------|-------|
| **Name** | Asset Requisition |
| **URL** | `/api/assets-requisition/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/assets-requisition/<int:requisition_id>/` |
| **Detail Method** | `PATCH` |

**Request Payload (POST):**
```json
{
    "requisition_number": "REQ001",
    "asset_name": "Laptop",
    "assets_category_id": 1,
    "assets_type_id": 1,
    "assets_brand_id": 1,
    "specification": "16GB RAM, 512GB SSD",
    "quantity": 1,
    "expected_date": "2026-02-15",
    "status": "P"
}
```

---

### HR Assets Dashboard
| Field | Value |
|-------|-------|
| **Name** | HR Assets Dashboard |
| **URL** | `/hr-assets-dashboard/` |
| **Method** | `GET` |

---

### HR Assets Approval
| Field | Value |
|-------|-------|
| **Name** | HR Assets Approval |
| **URL** | `/hr-return-approval/<int:pk>/` |
| **Method** | `PATCH` |

---

## 1.21 Resignation APIs

### Resignations CRUD
| Field | Value |
|-------|-------|
| **Name** | Resignations |
| **URL** | `/resignations/` |
| **Method** | `GET`, `POST` |

**Request Payload (POST):**
```json
{
    "company_id": 2,
    "employee_id": "EMP001",
    "notice_date": "2026-02-01",
    "resignation_date": "2026-02-01",
    "reason": "Personal reasons",
    "added_by": 1,
    "status": "pending"
}
```

**Response (GET):**
```json
[
    {
        "resignation_id": 1,
        "company_id": 2,
        "employee_id": "EMP001",
        "resignation_date": "2026-02-01",
        "last_working_day": "2026-03-01",
        "reason": "Personal reasons",
        "added_by": 1,
        "status": "Pending",
        "created_at": "2026-02-01",
        "employee_name": "John Doe",
        "department_name": "IT"
    }
]
```

---

### Resignation Detail
| Field | Value |
|-------|-------|
| **Name** | Resignation Detail |
| **URL** | `/resignations/<int:resignation_id>/` |
| **Method** | `PATCH`, `DELETE` |

**Request Payload (PATCH):**
```json
{
    "status": "approved",
    "last_working_day": "2026-03-01"
}
```

---

### Employee Resignation
| Field | Value |
|-------|-------|
| **Name** | Employee Resignation |
| **URL** | `/employee_resignations/<str:employee_id>/` |
| **Method** | `GET`, `POST` |

**Request Payload (POST):**
```json
{
    "reason": "Career growth opportunity"
}
```

**Response (POST):**
```json
{
    "message": "Resignation submitted successfully.",
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "department_id": 1,
    "resignation_date": "2026-01-31",
    "reason": "Career growth opportunity",
    "status": "Pending"
}
```

---

### Email-based Resignation Actions
| Field | Value |
|-------|-------|
| **Approve URL** | `/approve_resignation_through_mail/<int:resignation_id>/` |
| **Approve Method** | `GET` |
| **Reject URL** | `/reject_resignation_through_mail/<int:resignation_id>/` |
| **Reject Method** | `GET` |

---

## 1.22 Exit Employee APIs

### Employee Exits CRUD
| Field | Value |
|-------|-------|
| **Name** | Employee Exits |
| **URL** | `/employee-exits/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/employee-exits/<int:exit_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "employee_id": "EMP001",
    "exit_date": "2026-03-01",
    "exit_type_id": 1,
    "sub_exit_type_id": 1,
    "reason": "Resignation",
    "added_by": 1
}
```

**Response (GET):**
```json
[
    {
        "exit_id": 1,
        "company_id": 2,
        "employee_id": "EMP001",
        "employee_name": "John Doe",
        "exit_date": "2026-03-01",
        "exit_type_id": 1,
        "exit_type_name": "Resignation",
        "sub_exit_type_id": 1,
        "exit_interview": "yes",
        "is_inactivate_account": "no",
        "reason": "Career growth",
        "accountability_to": "Manager",
        "added_by": 1,
        "created_at": "2026-01-31"
    }
]
```

---

### Exit Employee Tables
| Field | Value |
|-------|-------|
| **Table 1 URL** | `/exit-employee-table1/` |
| **Update 1 URL** | `/update-exit-employee-table1/<str:employee_id>/` |
| **Table 2 URL** | `/exit-employee-table2/` |
| **Update 2 URL** | `/update-exit-employee-table2/<str:employee_id>/` |
| **Table 3 URL** | `/exit-employee-table3/` |
| **Update 3 URL** | `/update-exit-employee-table3/<str:employee_id>/` |
| **Final Table URL** | `/exit-employee-finaltable/` |
| **Method** | `GET` for tables, `PATCH` for updates |

---

### Exit Questionnaire
| Field | Value |
|-------|-------|
| **Name** | Exit Questionnaire |
| **URL** | `/exit-questionnaire/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/exit-questionnaire/<int:ques_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

---

### Submit Exit Feedback
| Field | Value |
|-------|-------|
| **Name** | Submit Exit Feedback |
| **URL** | `/post_exit_procedure_feedback/` |
| **Method** | `POST` |

---

### View Feedback Forms
| Field | Value |
|-------|-------|
| **Employee-wise URL** | `/view_employeewise_feedback_form/` |
| **All Employees URL** | `/view_all_employee_feedback_form/` |
| **Method** | `GET` |

---

## 1.23 Termination APIs

### Termination Dashboard
| Field | Value |
|-------|-------|
| **Get All URL** | `/get-terminations/` |
| **Method** | `GET` |
| **Post URL** | `/post-terminations/` |
| **Method** | `POST` |
| **Update URL** | `/update-terminations/<int:pk>/` |
| **Method** | `PATCH` |

---

### Pending/Send Terminations
| Field | Value |
|-------|-------|
| **Pending URL** | `/pending-terminations/` |
| **Send URL** | `/send-terminations/` |
| **Method** | `GET` |

---

### Upload Clearance Form
| Field | Value |
|-------|-------|
| **URL** | `/Upload-Clearance-Form/<str:employee_id>/` |
| **Method** | `PATCH` |

---

## 1.24 Project APIs

### Admin Projects CRUD
| Field | Value |
|-------|-------|
| **Name** | Admin Projects |
| **URL** | `/api/projects/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/projects/<int:project_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "client_id": "Client Name",
    "title": "Project Alpha",
    "start_date": "2026-02-01",
    "end_date": "2026-06-30",
    "assigned_to": "EMP001,EMP002,EMP003",
    "priority": "High",
    "budget_hours": 500.00,
    "project_progress": 0,
    "summary": "New development project",
    "description": "Detailed project description",
    "project_note": "Important notes",
    "associated_goals": "Q1 Goals"
}
```

**Response (GET):**
```json
[
    {
        "id": 1,
        "title": "Project Alpha",
        "client_name": "Client Name",
        "start_date": "2026-02-01",
        "end_date": "2026-06-30",
        "assigned_to": "John Doe, Jane Smith",
        "priority": "High",
        "budget_hours": 500.00,
        "project_progress": 25,
        "summary": "New development project",
        "description": "Detailed description",
        "project_note": "Important notes",
        "associated_goals": "Q1 Goals",
        "status": 1,
        "created_at": "2026-01-31"
    }
]
```

---

### Employee Assigned Projects
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_projects/<str:employee_id>/` |
| **Method** | `GET` |

---

### Project Progress Summary
| Field | Value |
|-------|-------|
| **URL** | `/api/projects/progress-summary/` |
| **Method** | `GET` |

---

### Project Discussion
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_projects/discussions/<int:project_id>/` |
| **Method** | `POST` |

---

### Project Attachment
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_projects/attachment/<int:project_id>/` |
| **Method** | `POST` |

---

## 1.25 Task APIs

### Tasks CRUD
| Field | Value |
|-------|-------|
| **Name** | Tasks |
| **URL** | `/api/tasks/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/tasks/<int:task_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

---

### Employee Tasks
| Field | Value |
|-------|-------|
| **URL** | `/employee/tasks/<str:employee_id>/` |
| **Method** | `GET` |

---

### Task Discussion/Note/Attachment
| Field | Value |
|-------|-------|
| **Discussion URL** | `/employee/task/discussion/<int:task_id>/` |
| **Note URL** | `/employee/task/note/<int:task_id>/` |
| **Attachment URL** | `/employee/task/attachment/<int:task_id>/` |
| **Method** | `POST` |

---

### Task Discussions
| Field | Value |
|-------|-------|
| **URL** | `/task-discussions/` |
| **Method** | `GET`, `POST` |

---

### Task Files
| Field | Value |
|-------|-------|
| **URL** | `/task-files/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/task-files/<int:task_file_id>/` |
| **Detail Method** | `GET`, `PATCH`, `DELETE` |

---

### Task Notes
| Field | Value |
|-------|-------|
| **URL** | `/task-notes/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/task-notes/<int:task_note_id>/` |
| **Detail Method** | `GET`, `PATCH`, `DELETE` |

---

### Assigned Task Detail
| Field | Value |
|-------|-------|
| **URL** | `/assigned_tasks/<int:task_id>/` |
| **Method** | `GET`, `PUT`, `DELETE` |

---

## 1.26 Project Bugs
| Field | Value |
|-------|-------|
| **URL** | `/ci_projects_bugs/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/ci_projects_bugs/<int:project_bug_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

---

## 1.27 Support Ticket APIs

### Employee Support Tickets
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_support_tickets/<str:employee_id>/` |
| **Method** | `GET`, `POST` |

---

### Admin Support Tickets
| Field | Value |
|-------|-------|
| **URL** | `/admin_support_tickets/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/admin_support_tickets/<int:ticket_id>/` |
| **Detail Method** | `GET`, `PATCH`, `DELETE` |

---

## 1.28 Visitor APIs

### Visitors CRUD
| Field | Value |
|-------|-------|
| **URL** | `/visitors/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/visitors/<int:pk>/` |
| **Detail Method** | `GET`, `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "company_id": 2,
    "department": 1,
    "visit_purpose": "Meeting",
    "visitor_name": "John Smith",
    "phone": "9876543210",
    "email": "john@example.com",
    "visit_date": "2026-02-01",
    "check_in": "10:00:00",
    "address": "123 Main Street",
    "description": "Client meeting",
    "created_by": 1
}
```

---

### Visitors Raw List
| Field | Value |
|-------|-------|
| **URL** | `/visitors/raw/` |
| **Method** | `GET` |

---

## 1.29 Disciplinary Cases
| Field | Value |
|-------|-------|
| **URL** | `/api/disciplinary-cases/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/disciplinary-cases/<int:pk>/` |
| **Detail Method** | `PATCH`, `DELETE` |

**Request Payload (POST):**
```json
{
    "company_id": 2,
    "Warning_to": "EMP001",
    "Warning_by": 1,
    "warning_date": "2026-01-31",
    "attachment": "url",
    "subject": "Policy Violation",
    "description": "Details",
    "warning_type_id": 1
}
```

---

## 1.30 Client APIs
| Field | Value |
|-------|-------|
| **URL** | `/api/clients/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/clients/<int:client_id>/` |
| **Detail Method** | `GET`, `PATCH`, `DELETE` |

**Request Payload (POST - multipart/form-data):**
```json
{
    "full_name": "Client Company",
    "company_name": "Client Corp",
    "contact_number": "9876543210",
    "gender": "Male",
    "email_address": "client@example.com",
    "profile_picture": "file"
}
```

---

## 1.31 Dashboard APIs

### Admin Dashboard
| Field | Value |
|-------|-------|
| **URL** | `/admin_dashboard/` |
| **Method** | `GET`, `POST` |

**Response (GET):**
```json
{
    "status": "success",
    "emp_count": 100,
    "emp_count_active": 95,
    "emp_count_inactive": 5,
    "month_wise_data": [],
    "resignation_data": {
        "all_resignations": [],
        "approved_resignations": [],
        "exit_process_status": []
    },
    "department_wise_count": [],
    "designation_wise_count": [],
    "division_wise_count": [],
    "active_employees": []
}
```

---

### Employee Dashboard
| Field | Value |
|-------|-------|
| **URL** | `/api/employee-dashboard/` |
| **Method** | `GET` |

---

### Emp Dashboard
| Field | Value |
|-------|-------|
| **URL** | `/empdashboard/<str:employee_id>/` |
| **Method** | `GET` |

---

### Company Setup Dashboard
| Field | Value |
|-------|-------|
| **URL** | `/api/company-setup-dashboard/` |
| **Method** | `GET` |

**Response:**
```json
[
    {
        "department_id": 1,
        "department_name": "IT",
        "active_employee_count": 25
    }
]
```

---

## 1.32 Todo APIs
| Field | Value |
|-------|-------|
| **URL** | `/api/todos/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/todos/<int:todo_id>/` |
| **Detail Method** | `PATCH`, `DELETE` |

---

## 1.33 Notification APIs
| Field | Value |
|-------|-------|
| **URL** | `/notifications/global/<str:employee_id>/` |
| **Method** | `GET` |

---

## 1.34 Biometric APIs
| Field | Value |
|-------|-------|
| **URL** | `/biometric/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/biometric/<int:ci_biomatric_id>/` |
| **Detail Method** | `GET`, `PUT`, `PATCH`, `DELETE` |

---

## 1.35 Employee Confirmation
| Field | Value |
|-------|-------|
| **URL** | `/EmpConfirmation/<str:employee_id>/` |
| **Method** | `GET`, `POST`, `PATCH` |

---

## 1.36 Policy Acknowledgement Status
| Field | Value |
|-------|-------|
| **URL** | `/policy_ack/<str:emp_id>/` |
| **Method** | `GET` |

---

## 1.37 Company Details
| Field | Value |
|-------|-------|
| **URL** | `/api/company-details/` |
| **Method** | `GET`, `POST`, `PATCH` |

**Request Payload (POST):**
```json
{
    "company_name": "Company Name",
    "register_address": "Address",
    "manufacturing_address": "Address",
    "phone_number": "9876543210",
    "pan_number": "ABCDE1234F",
    "company_stamp": "url"
}
```

---

## 1.38 Payroll
| Field | Value |
|-------|-------|
| **URL** | `/payroll/<int:user_id>/<int:type>/` |
| **Method** | `GET` |

---

## 1.39 Dropdown APIs

| API Name | URL | Method |
|----------|-----|--------|
| States Dropdown | `/api/states/` | GET |
| Countries Dropdown | `/api/countries/` | GET |
| Employee Dropdown | `/employee-dropdown/` | GET |
| Case Types Dropdown | `/api/case-types/` | GET, POST |
| Religion Dropdown | `/api/religion-dropdown/` | GET |
| Leave Type Dropdown | `/api/leavetype-dropdown/` | GET |
| Citizenship Dropdown | `/api/citizenship-dropdown/` | GET |
| Nationality Dropdown | `/api/nationality-dropdowns/` | GET |
| Staff Role Dropdown | `/api/staffrole-dropdown/` | GET |
| Department Employee Count | `/api/department-employee-count/` | GET |
| Designation Employee Count | `/api/designation-employee-count/` | GET |
| Award Types | `/api/award-types/` | GET, POST |
| Award Types Detail | `/api/award-types/<int:award_type_id>/` | DELETE |
| Training Skills | `/api/training-skills/` | GET, POST |
| Assets Category | `/api/assets-category/` | GET, POST |
| Assets Category Detail | `/api/assets-category/<int:constants_id>/` | PATCH, DELETE |
| Assets Type | `/api/assets-type/` | GET, POST |
| Assets Type Detail | `/api/assets-type/<int:constants_id>/` | PATCH, DELETE |
| Assets Brand | `/api/assets-brand/` | GET, POST |
| Assets Brand Detail | `/api/assets-brand/<int:constants_id>/` | PATCH, DELETE |
| Arrangement Type | `/api/arrangement-type/` | GET, POST |
| Arrangement Type Detail | `/api/arrangement-type/<int:constants_id>/` | PATCH, DELETE |
| Exit Type | `/api/exit-type/` | GET, POST |
| Exit Type Detail | `/api/exit-type/<int:id>/` | PATCH, DELETE |
| Travel Mood | `/api/travel-mood/` | GET |
| Departments Dropdown | `/api/departments/dropdown/` | GET |
| Designations Dropdown | `/api/designations/dropdown/` | GET |
| Employee Role Dropdown | `/api/dropdown/employee-role/` | GET |
| Resigned Employees | `/resigned-employees-dropdown/` | GET |
| Confirmation Employees | `/confirmation-employees-dropdown/` | GET |
| Emp Name Dropdown (Manager-wise) | `/dropdown/<str:empid>/` | GET |
| Designation-wise Count | `/get_designationwise_count/` | GET |
| Grade-wise Count | `/get_gradewise_count/` | GET |

---

## 1.40 HR Exit Employee APIs

| API Name | URL | Method |
|----------|-----|--------|
| Get Exit Date | `/get-exit-date/<str:employee_id>/` | GET |
| Check Asset Status | `/check-asset-status/<str:employee_id>/` | GET |
| Get Letters | `/get-letters/<str:employee_id>/` | GET |
| Get Letters (All) | `/get-letters/` | GET |
| HR Exit Employee | `/hr-exit-employee/` | GET |
| Upload HR Sign | `/upload-sign/<str:employee_id>/` | PATCH |
| Upload Company Stamp | `/upload-stamp/<int:company_detail_id>/` | PATCH |
| Data For Letters | `/data-for-letters/<str:employee_id>/` | GET |
| Get Employee Exit | `/get-exit-employee/` | GET |
| Add Employee Exit | `/add-new-exit-employee/` | POST |
| Update Employee Exit | `/exit-employee/<int:exit_id>/` | PATCH, DELETE |

---

# 2. HRMS App Module APIs (Base URL: `/api/`)

## 2.1 Dropdown APIs

### Employee Manager Dropdown
| Field | Value |
|-------|-------|
| **URL** | `/api/emp_manager_dropdown/` |
| **Method** | `GET` |

---

### Designation Department Dropdown
| Field | Value |
|-------|-------|
| **URL** | `/api/desig_dept_dropdown/` |
| **Method** | `GET` |
| **Detail URL** | `/api/desig_dept_dropdown/<int:dept_id>/` |

---

### Employees By Designation
| Field | Value |
|-------|-------|
| **URL** | `/api/employees_by_designation/` |
| **Method** | `GET` |

---

### Designation Dropdown Filter By Line Manager
| Field | Value |
|-------|-------|
| **URL** | `/api/designation_dropdown_filter_by_line_manager/` |
| **Method** | `GET` |

---

### State Dropdown
| Field | Value |
|-------|-------|
| **URL** | `/api/state_dropdown/` |
| **Method** | `GET` |

---

### Employee Hub Dropdown
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_hub_dropdown/<int:state_id>/` |
| **Method** | `GET` |

---

### Office Shift Dropdown
| Field | Value |
|-------|-------|
| **URL** | `/api/office_shift_dropdown/<int:employee_hub_id>/<int:state_id>/` |
| **Method** | `GET` |

---

## 2.2 Account Details APIs

### Contract Details
| Field | Value |
|-------|-------|
| **URL** | `/api/contract_details/` |
| **Method** | `GET` |

---

### Employee Basic Information
| Field | Value |
|-------|-------|
| **URL** | `/api/emp_basic_info/` |
| **Method** | `GET` |

---

### Personal Information
| Field | Value |
|-------|-------|
| **URL** | `/api/personal_info/` |
| **Method** | `GET` |

---

### Get Profile Photo
| Field | Value |
|-------|-------|
| **URL** | `/api/get_profile_photo/<str:employee_id>/` |
| **Method** | `GET` |

---

### Update Profile Photo
| Field | Value |
|-------|-------|
| **URL** | `/api/update_profile_photo/` |
| **Method** | `POST` |

---

### Account Information
| Field | Value |
|-------|-------|
| **URL** | `/api/account_info/` |
| **Method** | `GET` |

---

### Document Details
| Field | Value |
|-------|-------|
| **URL** | `/api/document_details/` |
| **Method** | `GET` |

---

### Change Password
| Field | Value |
|-------|-------|
| **URL** | `/api/change_password/` |
| **Method** | `POST` |

---

### Timesheet Agenda
| Field | Value |
|-------|-------|
| **URL** | `/api/timesheet_agenda/` |
| **Method** | `GET` |

---

### Leave Statistics
| Field | Value |
|-------|-------|
| **URL** | `/api/leave_statistics/` |
| **Method** | `GET` |

---

## 2.3 Employee Panel APIs

### Dashboard Attendance
| Field | Value |
|-------|-------|
| **URL** | `/api/dashboard_attendance/<str:employee_id>/` |
| **Method** | `GET` |

---

### Employee Attendance
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_attendance/` |
| **Method** | `GET` |

---

### Basic Info
| Field | Value |
|-------|-------|
| **URL** | `/api/basic_info/` |
| **Method** | `GET` |

---

### Holiday List
| Field | Value |
|-------|-------|
| **URL** | `/api/holiday_list/` |
| **Method** | `GET` |

---

### Project List
| Field | Value |
|-------|-------|
| **URL** | `/api/project_list/<int:user_id>/<int:type>/` |
| **Method** | `GET` |

---

### Project Details
| Field | Value |
|-------|-------|
| **URL** | `/api/project_details/<int:user_id>/` |
| **Method** | `GET` |

---

### Project Discussion
| Field | Value |
|-------|-------|
| **URL** | `/api/project_discussion/` |
| **Method** | `POST` |

---

### Project Attach File
| Field | Value |
|-------|-------|
| **URL** | `/api/project_attach_file/` |
| **Method** | `POST` |

---

### Payroll
| Field | Value |
|-------|-------|
| **URL** | `/api/payroll/<int:user_id>/<int:type>/` |
| **Method** | `GET` |

---

### Policies
| Field | Value |
|-------|-------|
| **URL** | `/api/policies/` |
| **Method** | `GET` |

---

## 2.4 Admin Panel - Employee Management

### Employee Details
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_details/` |
| **Method** | `GET` |

---

### Edit Employee
| Field | Value |
|-------|-------|
| **Get URL** | `/api/edit_employee/<int:user_id>/` |
| **Get Method** | `GET` |
| **Put URL** | `/api/edit_employee/` |
| **Put Method** | `PUT` |
| **Delete Method** | `DELETE` |

---

### Change Manager
| Field | Value |
|-------|-------|
| **URL** | `/api/change_manager/` |
| **Method** | `POST` |

---

### Get Max Employee ID
| Field | Value |
|-------|-------|
| **URL** | `/api/get_max_employee_id/` |
| **Method** | `GET` |

---

### Fetch Documents
| Field | Value |
|-------|-------|
| **URL** | `/api/fetch_documents/` |
| **Method** | `GET` |

---

### Check Existing Email
| Field | Value |
|-------|-------|
| **URL** | `/api/check_existing_email/` |
| **Method** | `POST` |

---

### Add Employee
| Field | Value |
|-------|-------|
| **URL** | `/api/add_employee/` |
| **Method** | `POST` |

---

## 2.5 Admin Panel - Roles & Privileges

### Role List
| Field | Value |
|-------|-------|
| **URL** | `/api/role_list/` |
| **Method** | `GET`, `PUT` |
| **Detail URL** | `/api/role_list/<int:role_id>/` |
| **Detail Method** | `DELETE` |

---

### Add Role
| Field | Value |
|-------|-------|
| **URL** | `/api/add_role/` |
| **Method** | `POST` |

---

## 2.6 Admin Panel - Shift & Scheduling

### Office Shift
| Field | Value |
|-------|-------|
| **URL** | `/api/office_shift/` |
| **Method** | `GET`, `POST`, `PUT` |
| **Detail URL** | `/api/office_shift/<int:shift_id>/` |
| **Detail Method** | `DELETE` |

---

## 2.7 Admin Panel - Attendance

### Attendance Overview
| Field | Value |
|-------|-------|
| **URL** | `/api/attendance_overview/` |
| **Method** | `GET` |

---

### Manual Attendance
| Field | Value |
|-------|-------|
| **URL** | `/api/manual_attendance/` |
| **Method** | `GET`, `POST` |

---

### Employee Hub
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_hub/` |
| **Method** | `GET`, `POST`, `PUT`, `DELETE` |

---

### Monthly Report
| Field | Value |
|-------|-------|
| **URL** | `/api/monthly_report/` |
| **Method** | `GET` |

---

### Holiday
| Field | Value |
|-------|-------|
| **URL** | `/api/holiday/` |
| **Method** | `GET`, `POST` |

---

## 2.8 Admin Panel - Payroll

### Payroll Setup Configuration
| Field | Value |
|-------|-------|
| **URL** | `/api/payroll_setup_configuration/` |
| **Method** | `GET`, `POST` |

---

### Payroll Employee TDS
| Field | Value |
|-------|-------|
| **URL** | `/api/payroll_employee_tds/` |
| **Method** | `GET`, `POST` |

---

### Payroll Report
| Field | Value |
|-------|-------|
| **URL** | `/api/payroll_report/<int:month>/<int:year>/` |
| **Method** | `GET` |

---

### Pre-Saved Payroll Report
| Field | Value |
|-------|-------|
| **URL** | `/api/pre_saved_payroll_report/` |
| **Method** | `GET` |

---

### Save Payroll Report
| Field | Value |
|-------|-------|
| **URL** | `/api/save_payroll_report/` |
| **Method** | `POST` |

---

### Payment Info
| Field | Value |
|-------|-------|
| **URL** | `/api/payment_info/` |
| **Method** | `GET` |

---

### Update Payment Info
| Field | Value |
|-------|-------|
| **URL** | `/api/update_payment_info/` |
| **Method** | `PUT` |

---

### Salary Structure
| Field | Value |
|-------|-------|
| **URL** | `/api/salary_structure/` |
| **Method** | `GET` |

---

### Payslip History
| Field | Value |
|-------|-------|
| **URL** | `/api/payslip_history/` |
| **Method** | `GET` |

---

### Payslip
| Field | Value |
|-------|-------|
| **URL** | `/api/payslip/` |
| **Method** | `GET` |

---

### View Employee Salary Slip
| Field | Value |
|-------|-------|
| **URL** | `/api/view_employee_salary_slip/<str:employee_id>/` |
| **Method** | `GET` |

---

## 2.9 Admin Panel - Assets

### Assets Inventory
| Field | Value |
|-------|-------|
| **URL** | `/api/assets_inventory/` |
| **Method** | `GET`, `POST` |

---

## 2.10 Reports APIs

### Monthly Attendance Report
| Field | Value |
|-------|-------|
| **URL** | `/api/attendance/monthly-report/` |
| **Method** | `GET` |

---

### Monthly Leave Report
| Field | Value |
|-------|-------|
| **URL** | `/api/leave/monthly-report/` |
| **Method** | `GET` |

---

### Leave Balance Report
| Field | Value |
|-------|-------|
| **URL** | `/api/leave/balance-report/` |
| **Method** | `GET` |

---

### New Joiner Report
| Field | Value |
|-------|-------|
| **URL** | `/api/new-joiner-report/` |
| **Method** | `GET` |

---

### Manpower Report
| Field | Value |
|-------|-------|
| **URL** | `/api/manpower-report/` |
| **Method** | `GET` |

---

### Employee Attrition Report
| Field | Value |
|-------|-------|
| **URL** | `/api/employee-attrition-report/` |
| **Method** | `GET` |

---

### Employee Master Report
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_master_report/` |
| **Method** | `GET` |

---

### HR Master Data
| Field | Value |
|-------|-------|
| **URL** | `/api/hr-master-data/` |
| **Method** | `GET` |

---

### Employee Exit Report
| Field | Value |
|-------|-------|
| **URL** | `/api/employee-exit-report/` |
| **Method** | `GET` |

---

### Performance Management Report
| Field | Value |
|-------|-------|
| **URL** | `/api/performance-management-report/` |
| **Method** | `GET` |

---

### Annual Appraisal Report
| Field | Value |
|-------|-------|
| **URL** | `/api/annual-appraisal-report/` |
| **Method** | `GET` |

---

### Salary Report
| Field | Value |
|-------|-------|
| **URL** | `/api/salary-report/` |
| **Method** | `GET` |

---

### PT Report
| Field | Value |
|-------|-------|
| **URL** | `/api/pt-report/` |
| **Method** | `GET` |

---

## 2.11 Holiday Calendar

### Holiday Calendar View
| Field | Value |
|-------|-------|
| **URL** | `/api/holidays/calendar/<int:country_id>/<int:state_id>/<int:employee_hub>/` |
| **Method** | `GET` |

---

## 2.12 Notifications

### View Notification
| Field | Value |
|-------|-------|
| **URL** | `/api/view_notification/` |
| **Method** | `GET` |

---

## 2.13 HR Revenue/Expense

### Save HR Revenue Expense
| Field | Value |
|-------|-------|
| **URL** | `/api/save_hr_revenue_expense/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/api/save_hr_revenue_expense/<int:hr_rev_exp_id>/` |
| **Detail Method** | `PATCH` |

---

## 2.14 OTP & Password Reset APIs

### Send OTP
| Field | Value |
|-------|-------|
| **URL** | `/api/send_otp/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "email": "user@example.com"
}
```

---

### Verify OTP
| Field | Value |
|-------|-------|
| **URL** | `/api/verify_otp/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "email": "user@example.com",
    "otp": "123456"
}
```

---

### Reset Password
| Field | Value |
|-------|-------|
| **URL** | `/api/reset_password/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "email": "user@example.com",
    "new_password": "newpassword123"
}
```

---

## 2.15 HR Dashboard APIs

### HR Dashboard Metrics
| Field | Value |
|-------|-------|
| **URL** | `/api/hr_dashboard_metrics/` |
| **Method** | `GET` |

---

### HR Dashboard Metrics By Month
| Field | Value |
|-------|-------|
| **URL** | `/api/hr_dashboard_metrics_by_month/` |
| **Method** | `GET` |

---

### HR Dashboard Graphs
| Field | Value |
|-------|-------|
| **URL** | `/api/hr_dashboard_graphs/` |
| **Method** | `GET` |

---

## 2.16 Role Management APIs

### User Role Permissions
| Field | Value |
|-------|-------|
| **URL** | `/api/roles/user-permissions/` |
| **Method** | `GET` |
| **Detail URL** | `/api/roles/user-permissions/<int:user_id>/` |

---

### Check Permission
| Field | Value |
|-------|-------|
| **URL** | `/api/roles/check-permission/` |
| **Method** | `POST` |

---

### Check Multiple Permissions
| Field | Value |
|-------|-------|
| **URL** | `/api/roles/check-multiple-permissions/` |
| **Method** | `POST` |

---

### Role CRUD
| Field | Value |
|-------|-------|
| **Create URL** | `/api/roles/create/` |
| **Create Method** | `POST` |
| **Update URL** | `/api/roles/update/` |
| **Update Method** | `PUT` |
| **Delete URL** | `/api/roles/delete/<int:role_id>/` |
| **Delete Method** | `DELETE` |
| **List URL** | `/api/roles/list/` |
| **List Method** | `GET` |

---

## 2.17 Training Management APIs

### Training CRUD
| Field | Value |
|-------|-------|
| **Create URL** | `/api/training/create/` |
| **Create Method** | `POST` |
| **Update URL** | `/api/training/update/` |
| **Update Method** | `PUT` |
| **Delete URL** | `/api/training/delete/<int:training_id>/` |
| **Delete Method** | `DELETE` |
| **List URL** | `/api/training/list/` |
| **List Method** | `GET` |
| **Details URL** | `/api/training/details/<int:training_id>/` |
| **Details Method** | `GET` |
| **Update Status URL** | `/api/training/update-status/` |
| **Update Status Method** | `PATCH` |

---

## 2.18 Other APIs

### Search By Email Vet Talent
| Field | Value |
|-------|-------|
| **URL** | `/api/search_by_email_vet_talent/` |
| **Method** | `GET` |

---

### Employee Leave Pattern
| Field | Value |
|-------|-------|
| **URL** | `/api/employee_leave_pattern/` |
| **Method** | `GET` |

---

### Check Phasewise Parameters
| Field | Value |
|-------|-------|
| **URL** | `/api/check_phasewise_parameters/` |
| **Method** | `GET` |

---

### Get Employee Details Clearance Form
| Field | Value |
|-------|-------|
| **URL** | `/api/get_employee_details_clearance_form/` |
| **Method** | `GET` |

---

# 3. M_App Module APIs (Base URL: `/apps/`)

## 3.1 Announcements APIs

### Announcements List/Create
| Field | Value |
|-------|-------|
| **URL** | `/apps/announcements/` |
| **Method** | `GET`, `POST` |

**Request Payload (POST):**
```json
{
    "title": "string (required)",
    "department_id": 1,
    "start_date": "2026-02-01",
    "end_date": "2026-02-28",
    "summary": "string (required)",
    "description": "string"
}
```

**Response (GET):**
```json
[
    {
        "announcement_id": 1,
        "department_id": 1,
        "title": "Company Update",
        "department_name": "All",
        "start_date": "2026-02-01",
        "end_date": "2026-02-28",
        "summary": "Brief summary",
        "description": "Full description"
    }
]
```

---

### Announcement Details
| Field | Value |
|-------|-------|
| **URL** | `/apps/announcements_details/<int:announcement_id>/` |
| **Method** | `GET`, `PUT`, `DELETE` |

---

## 3.2 Policy APIs

### Policies List/Create
| Field | Value |
|-------|-------|
| **URL** | `/apps/policies/` |
| **Method** | `GET`, `POST` |

**Request Payload (POST - multipart/form-data):**
```json
{
    "title": "string (required)",
    "description": "string (required)",
    "attachment": "file (required)"
}
```

---

### Policy Details
| Field | Value |
|-------|-------|
| **URL** | `/apps/policies_details/<int:policy_id>/` |
| **Method** | `GET`, `PUT`, `DELETE` |

---

### Policy Acknowledgements
| Field | Value |
|-------|-------|
| **URL** | `/apps/policies_acknowledgements/` |
| **Method** | `GET` |

---

### Policy Dashboard
| Field | Value |
|-------|-------|
| **URL** | `/apps/policies_dashboard/` |
| **Method** | `GET` |

---

## 3.3 Support Ticket APIs

### Create/Update Ticket
| Field | Value |
|-------|-------|
| **URL** | `/apps/create_tickets/` |
| **Method** | `POST`, `PUT` |

**Request Payload (POST):**
```json
{
    "subject": "string (required)",
    "department_id": 1,
    "ticket_priority": 1,
    "description": "string (required)",
    "employee_id": "EMP001"
}
```

---

### Ticket Details
| Field | Value |
|-------|-------|
| **URL** | `/apps/ticket_view/<int:ticket_id>/` |
| **Method** | `GET`, `POST`, `DELETE` |

**Request Payload (POST - Update Status):**
```json
{
    "status": 1,
    "remarks": "string (required)",
    "employee_id": "EMP001"
}
```

---

### Department Wise Employees
| Field | Value |
|-------|-------|
| **URL** | `/apps/department_wise_employee/?department_id=1` |
| **Method** | `GET` |

---

# 4. New HRMS Module APIs (Base URL: `/apis/`)

## 4.1 Confirmation Parameter APIs

### Confirmation Parameters CRUD
| Field | Value |
|-------|-------|
| **URL** | `/apis/confirmation_parameter/` |
| **Method** | `GET`, `POST`, `PUT`, `DELETE` |

**Request Payload (POST):**
```json
{
    "para_name": "string (required)"
}
```

---

### Save Phase-wise Data
| Field | Value |
|-------|-------|
| **URL** | `/apis/save_phasewise_data/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "entries": [
        {
            "emp_id": 1,
            "parameter_id": 1,
            "phase": 1,
            "points_by_lm": 8,
            "comment_by_lm": "Good performance",
            "points_by_head": 9,
            "comment_by_head": "Excellent",
            "points_by_hr": 8,
            "comment_by_hr": "Meets expectations"
        }
    ],
    "role_id": 13
}
```

---

### Final Confirmation Action
| Field | Value |
|-------|-------|
| **URL** | `/apis/final_confirmation_action/` |
| **Method** | `PATCH` |

**Request Payload:**
```json
{
    "user_id": 1,
    "action": "confirm",
    "comment_by_lm": "Recommended",
    "comment_by_head": "Approved",
    "comment_by_hr": "Confirmed"
}
```

---

### Employee Confirmation Dashboard
| Field | Value |
|-------|-------|
| **URL** | `/apis/employee_confirmation_dashboard/` |
| **Method** | `GET` |

---

## 4.2 Designation-wise Parameter APIs

### Save Designation-wise Parameters
| Field | Value |
|-------|-------|
| **URL** | `/apis/save_Desigwise_parameters/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "parameter_id": 1,
    "designation_id": 1,
    "phase": 1,
    "created_by": 1
}
```

---

### Get Designation-wise Table Data
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_desigwise_tabledata/?phase=1&designation_id=1` |
| **Method** | `GET` |

---

### Delete Designation-wise Parameter
| Field | Value |
|-------|-------|
| **URL** | `/apis/delete_desigwise_para/<int:pk>/` |
| **Method** | `DELETE` |

---

## 4.3 Employee Performance APIs

### Get Employee Performance
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_performance/<int:role_id>/<int:user_id>/` |
| **Method** | `GET` |

---

### Get Employee Overall Phase-wise Marks
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_overall_phasewise/?user_id=1` |
| **Method** | `GET` |

---

### Save Employee Overall Analysis
| Field | Value |
|-------|-------|
| **URL** | `/apis/save_employee_overall_analysis/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "user_id": 1,
    "emp_id": "EMP001",
    "performance_analysis": "Excellent",
    "kra_kpi_total": 85.5,
    "average": 80.0,
    "percent_achievement": 90.0,
    "comment_by_lm": "Good",
    "comment_by_hr": "Approved",
    "comment_by_head": "Confirmed"
}
```

---

### Get Phase-wise Data
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_phasewise_data/<int:user_id>/` |
| **Method** | `GET` |

---

## 4.4 Report APIs

### Employee Leave Request Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_leave_request_report/?year=2026&month=1` |
| **Method** | `GET` |

---

### Employee Type Five Details
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_type_five_details/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "type": 5,
    "user_id": 1
}
```

---

### Employee Daily Attendance Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_daily_attendence_get_report/?date=2026-01-31` |
| **Method** | `GET` |

---

### Monthly Check-In/Out Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_monthly_check_in_check_out_get_report/?month=1&year=2026` |
| **Method** | `GET` |

---

### All Employee Leave Summary Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_all_employee_leave_summary_get_report/?year=2026` |
| **Method** | `GET` |

---

### Employee Confirmation Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_confirmation_get_report/?year=2026` |
| **Method** | `GET` |

---

### Employee PIP Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_pip_report_get_report/?year=2026&division_id=1` |
| **Method** | `GET` |

---

### Employee Promotion Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_promotion_get_report/?employee_id=EMP001` |
| **Method** | `GET` |

---

### Gratuity Eligibility Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_gratuity_eligibility_get_report/` |
| **Method** | `GET` |

---

### PF Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_pf_get_report/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "from_date": "2026-01-01",
    "to_date": "2026-01-31"
}
```

---

### Employee Payroll Salary Report
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_employee_payroll_salary_report/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "month": 1,
    "year": 2026
}
```

---

### Get Employees by Dept & Designation
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_promotion_report_employee_drop/?dept=1&desig=1` |
| **Method** | `GET` |

---

## 4.5 Leave Setup APIs

### Save and Freeze Leave Setup
| Field | Value |
|-------|-------|
| **URL** | `/apis/save_and_freeze_leave_setup/` |
| **Method** | `POST` |

**Request Payload:**
```json
[
    {
        "constants_id": 1,
        "leave_type": "CL",
        "days_per_year": 12,
        "current_leave_name": "Casual Leave",
        "current_leave_days": 12,
        "year": 2026
    }
]
```

---

## 4.6 Assets APIs

### Add New Assets to Stock
| Field | Value |
|-------|-------|
| **URL** | `/apis/add_new_asset_to_stock/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "brand_id": 1,
    "category_id": 1,
    "product_id": 1,
    "quantity": 10,
    "price": 50000.00,
    "invoice_number": "INV2026001",
    "purchase_date": "2026-01-15",
    "warranty_end_date": "2029-01-15"
}
```

---

### Update/Delete Category
| Field | Value |
|-------|-------|
| **URL** | `/apis/update_delete_category/?constants_id=1` |
| **Method** | `PUT`, `DELETE` |

---

### Product CRUD
| Field | Value |
|-------|-------|
| **URL** | `/apis/create_edit_product/` |
| **Method** | `GET`, `POST` |
| **Detail URL** | `/apis/create_edit_product/?product_id=1` |
| **Detail Method** | `PUT`, `DELETE` |

---

### Get Available Product Quantity
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_available_qty/?category_id=1&brand_id=1` |
| **Method** | `GET` |

---

### Get Metrics Form Data
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_metrics_form_data/?month=1&year=2026` |
| **Method** | `GET` |

---

### Get Assets In Stock Table
| Field | Value |
|-------|-------|
| **URL** | `/apis/get_assets_instock_data/` |
| **Method** | `GET` |

---

# 5. VetHR Module APIs (Base URL: `/api/`)

## 5.1 Leave Management APIs

### Employee Leave Balance
| Field | Value |
|-------|-------|
| **URL** | `/api/leave-balance/?employee_id=EMP001` |
| **Method** | `GET` |

**Response:**
```json
[
    {
        "leave_type_id": 1,
        "type": "leave_type",
        "category_name": "Casual Leave",
        "days_per_year": "12",
        "balance_leave": 10.5,
        "year": "2026"
    }
]
```

---

### Apply Leave
| Field | Value |
|-------|-------|
| **URL** | `/api/apply-leave/` |
| **Method** | `GET`, `POST` |

**Request Payload (POST):**
```json
{
    "employee_id": "EMP001",
    "user_id": 1,
    "company_id": 2,
    "leave_type_id": 1,
    "from_date": "2026-02-01",
    "to_date": "2026-02-03",
    "reason": "Personal work",
    "remarks": "Optional remarks",
    "is_half_day": false,
    "leave_attachment": "url"
}
```

**Response (POST):**
```json
{
    "message": "Leave application submitted successfully",
    "leave_id": 1,
    "no_of_days": 3.0,
    "leave_type": "Casual Leave",
    "note": "Sandwich rule information if applicable"
}
```

---

### Employee Leaves List
| Field | Value |
|-------|-------|
| **URL** | `/api/employee-leaves-list/?employee_id=EMP001` |
| **Method** | `GET` |

**Response:**
```json
{
    "leave_applications": [
        {
            "employee_name": "John Doe",
            "email": "john@example.com",
            "leave_type": "Casual Leave",
            "from_date": "2026-02-01",
            "to_date": "2026-02-03",
            "days_applied": 3.0,
            "status": "Pending"
        }
    ]
}
```

---

### Leave Details/History
| Field | Value |
|-------|-------|
| **URL** | `/api/leave-details/?employee_id=EMP001` |
| **Method** | `GET` |

**Response:**
```json
[
    {
        "leave_type": "Casual Leave",
        "days_per_year": 12,
        "approved_leave_days": 3.0,
        "balance": 9.0
    }
]
```

---

### Line Manager Approval
| Field | Value |
|-------|-------|
| **URL** | `/api/line-manager-approval/` |
| **Method** | `GET` |
| **Detail URL** | `/api/line-manager-approval/<int:leave_id>/` |
| **Detail Method** | `PATCH` |

**Request Payload (PATCH):**
```json
{
    "line_manager_status": "approved"
}
```

**Response:**
```json
{
    "message": "Leave status updated successfully",
    "new_status": "Approved"
}
```

---

### Sandwich Rule Check
| Field | Value |
|-------|-------|
| **URL** | `/api/sandwich-rule-check/` |
| **Method** | `POST` |

**Request Payload:**
```json
{
    "employee_id": "EMP001",
    "from_date": "2026-02-01",
    "to_date": "2026-02-03"
}
```

**Response:**
```json
{
    "from_date": "2026-02-01",
    "to_date": "2026-02-03",
    "sandwich_applied": 0
}
```

---

# API Summary

| Module | Base URL | Total Endpoints |
|--------|----------|-----------------|
| App Module | `/` | ~140 |
| HRMS App Module | `/api/` | ~94 |
| M_App Module | `/apps/` | ~16 |
| New HRMS Module | `/apis/` | ~30 |
| VetHR Module | `/api/` | ~7 |
| **Total** | - | **~287 endpoints** |

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

---

## Authentication

All APIs (except Login and Registration) require JWT authentication.

**Header:**
```
Authorization: Bearer <access_token>
```

---

## Notes for Frontend Developers

1. **Date Format**: Use `YYYY-MM-DD` for all date fields
2. **Time Format**: Use `HH:MM:SS` for all time fields
3. **File Uploads**: Use `multipart/form-data` content type
4. **Pagination**: Some list APIs support `?page=1` query parameter
5. **Filtering**: Check individual API documentation for filter parameters

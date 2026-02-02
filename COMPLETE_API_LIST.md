# Complete API List - Policy Management with Signed Documents & Reminders

## 📋 All Policy-Related APIs (Phase 1 + Phase 2)

**Total APIs: 19**
- 10 Unchanged (existing functionality)
- 1 Updated (backward compatible)
- 8 New (signed documents + reminders)

---

## EXISTING APIs (No Changes) - 10 APIs

### 1. Create/List Policies (Admin)
**GET** `/policies/`
```json
// Response
{
    "message": "Policies retrieved successfully",
    "data": [
        {
            "policy_id": 1,
            "title": "Code of Conduct",
            "description": "Company code of conduct",
            "attachment": "policies/code_of_conduct.pdf",
            "created_at": "2026-01-15 10:00:00"
        }
    ]
}
```

**POST** `/policies/`
```json
// Request (multipart/form-data)
{
    "title": "Data Privacy Policy",
    "description": "Company data privacy guidelines",
    "attachment": [File]
}

// Response
{
    "message": "Policy created and allocated to all employees successfully",
    "policy_id": 5
}
```

---

### 2. Update/Delete Policy (Admin)
**PATCH** `/policies/{policy_id}/`
```json
// Request (multipart/form-data)
{
    "title": "Updated Policy Title",
    "description": "Updated description"
}

// Response
{
    "message": "Policy updated successfully"
}
```

**DELETE** `/policies/{policy_id}/`
```json
// Response
{
    "message": "Policy deleted successfully"
}
```

---

### 3. Policy Dashboard (Admin)
**GET** `/policy-dashboard/`
```json
// Response
{
    "message": "Employee policy acknowledgement status",
    "acknowledged": [...],
    "not_acknowledged": [...],
    "partially_acknowledged": [...]
}
```

---

### 4. Policy Allocation (Admin)
**GET** `/api/policy-allocation/`
```json
// Response
{
    "total_query_entries": 50,
    "total_entries": 50,
    "data": [
        {
            "policy_allocation_id": 1,
            "emp_id": "EMP001",
            "employee_name": "John Doe",
            "policy_id": "1,2,3",
            "policy_name": "Policy 1,Policy 2,Policy 3",
            "policy_acknowledgement_status": "Y,Y,N",
            "allocation_date": "2026-01-15"
        }
    ]
}
```

**POST** `/api/policy-allocation/`
```json
// Request
{
    "employee_id": "EMP001",
    "policies_to_add": ["Policy Name 1", "Policy Name 2"]
}

// Response
{
    "message": "Policies allocated successfully"
}
```

**PATCH** `/api/policy-allocation/{policy_allocation_id}/`
```json
// Request
{
    "employee_id": "EMP001",
    "policies_to_add": ["New Policy"],
    "policies_to_remove": ["Old Policy"]
}

// Response
{
    "message": "Policy allocation updated successfully."
}
```

**DELETE** `/api/policy-allocation/{policy_allocation_id}/`
```json
// Response
{
    "message": "Policy allocation deleted successfully."
}
```

---

### 5. Acknowledge Policy (Employee)
**POST** `/policies/acknowledge/{emp_id}/`
```json
// Request
{
    "policy_id": 1
}

// Response
{
    "message": "Policy acknowledged successfully."
}
```

---

## ✨ UPDATED API (Added New Fields)

### 6. Get Assigned Policies (Employee) - **UPDATED**
**GET** `/policies/assigned/{emp_id}/`

**Old Response:**
```json
{
    "alert": "Alert! You Need to Accept All Policy...",
    "policies": [...]
}
```

**NEW Response (Additional Fields):**
```json
{
    "alert": "Alert! You Need to Accept All Policy to Avail your Attendance and Payroll",
    "all_acknowledged": false,
    "total_policies": 5,
    "acknowledged_count": 3,
    "signed_document": {
        "has_uploaded": false,
        "document_path": null,
        "uploaded_at": null,
        "email_status": "not_uploaded"
    },
    "policies": [
        {
            "policy_id": 1,
            "policy_name": "Code of Conduct",
            "attachment_text": "policies/code_of_conduct.pdf",
            "acknowledged": true
        },
        {
            "policy_id": 2,
            "policy_name": "Data Privacy",
            "attachment_text": "policies/data_privacy.pdf",
            "acknowledged": false
        }
    ]
}
```

**New Fields:**
- ✨ `all_acknowledged`: Boolean - true when all policies acknowledged
- ✨ `total_policies`: Integer - total assigned policies count
- ✨ `acknowledged_count`: Integer - how many acknowledged so far
- ✨ `signed_document`: Object with upload status:
  - `has_uploaded`: Boolean
  - `document_path`: String or null
  - `uploaded_at`: DateTime or null
  - `email_status`: "sent" | "pending" | "failed" | "not_uploaded"

---

## 🆕 NEW APIs (Signed Document Feature)

### 7. Download Acknowledgement Template (Employee)
**GET** `/policies/download-acknowledgement-template/{emp_id}/`

```bash
# Request
GET /policies/download-acknowledgement-template/EMP001/
Authorization: Bearer <jwt_token>

# Response (File Download)
Content-Type: application/pdf
Content-Disposition: attachment; filename="Policy_Acknowledgement_Template.pdf"
[PDF Binary Data]
```

**Purpose:** Download the ebook.pdf template for signing

**Validation:**
- ✅ Employee must exist
- ✅ Template file must exist in media folder

---

### 8. Upload Signed Document (Employee)
**POST** `/policies/upload-signed-document/{emp_id}/`

```bash
# Request (multipart/form-data)
POST /policies/upload-signed-document/EMP001/
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

FormData:
- signed_document: [File] (PDF/JPG/PNG/DOCX, Max 10MB)
```

**Success Response:**
```json
{
    "message": "Signed document uploaded successfully and email sent to HR",
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "file_path": "signed_acknowledgements/EMP001_policy_acknowledgement_20260131_143025.pdf",
    "uploaded_at": "2026-01-31 14:30:25",
    "email_sent": true,
    "hr_email": "hr@thedatatechlabs.com"
}
```

**Error Responses:**
```json
// No file uploaded
{
    "error": "No file uploaded. Please upload a signed document."
}

// File too large
{
    "error": "File size exceeds maximum limit of 10.0MB"
}

// Invalid file type
{
    "error": "Invalid file type. Allowed types: .pdf, .jpg, .jpeg, .png, .docx"
}

// Not all policies acknowledged
{
    "error": "Please acknowledge all assigned policies before uploading the signed document",
    "acknowledged": 3,
    "total_policies": 5
}

// Employee not found
{
    "error": "Employee not found"
}
```

**Features:**
- ✅ Validates file type (PDF, JPG, JPEG, PNG, DOCX only)
- ✅ Validates file size (max 10MB)
- ✅ Checks all policies are acknowledged first
- ✅ Generates unique filename with timestamp
- ✅ Stores in `media/signed_acknowledgements/`
- ✅ Saves path to database
- ✅ Automatically sends email to HR with attachment
- ✅ CC's employee on email

---

### 9. Check Signed Document Status (Employee)
**GET** `/policies/signed-document-status/{emp_id}/`

```bash
# Request
GET /policies/signed-document-status/EMP001/
Authorization: Bearer <jwt_token>
```

**Response (Document Uploaded):**
```json
{
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "has_uploaded": true,
    "document_path": "signed_acknowledgements/EMP001_policy_acknowledgement_20260131_143025.pdf",
    "uploaded_at": "2026-01-31 14:30:25",
    "email_status": "sent",
    "email_sent_at": "2026-01-31 14:30:30"
}
```

**Response (Not Uploaded):**
```json
{
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "has_uploaded": false,
    "document_path": null,
    "uploaded_at": null,
    "email_status": "not_uploaded",
    "email_sent_at": null
}
```

**Purpose:** Check if employee has uploaded their signed document

**Email Status Values:**
- `"sent"` - Email successfully sent to HR
- `"pending"` - Upload successful, email queued
- `"failed"` - Upload successful, but email failed
- `"not_uploaded"` - No document uploaded yet

---

### 10. View/Download Signed Document (HR/Admin)
**GET** `/policies/view-signed-document/{emp_id}/`

```bash
# Request
GET /policies/view-signed-document/EMP001/
Authorization: Bearer <jwt_token>

# Response (File Download)
Content-Type: application/pdf
Content-Disposition: attachment; filename="EMP001_John_Doe_signed_policy.pdf"
[File Binary Data]
```

**Purpose:** HR/Admin can download employee's signed document

**Error Responses:**
```json
// Employee not found
{
    "error": "Employee not found"
}

// No document uploaded
{
    "error": "No signed document found for this employee"
}

// File missing on server
{
    "error": "Signed document file not found on server"
}
```

---

### 11. All Signed Documents Dashboard (HR/Admin)
**GET** `/policies/all-signed-documents/`

```bash
# Request
GET /policies/all-signed-documents/
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "summary": {
        "total_employees": 150,
        "uploaded": 120,
        "pending": 30
    },
    "data": [
        {
            "employee_id": "EMP001",
            "employee_name": "John Doe",
            "email": "john.doe@company.com",
            "document_path": "signed_acknowledgements/EMP001_policy_acknowledgement_20260131_143025.pdf",
            "uploaded_at": "2026-01-31 14:30:25",
            "email_status": "sent",
            "email_sent_at": "2026-01-31 14:30:30",
            "status": "Uploaded"
        },
        {
            "employee_id": "EMP002",
            "employee_name": "Jane Smith",
            "email": "jane.smith@company.com",
            "document_path": null,
            "uploaded_at": null,
            "email_status": "not_uploaded",
            "email_sent_at": null,
            "status": "Pending"
        }
    ]
}
```

**Purpose:** HR dashboard showing all employees with upload status

**Features:**
- ✅ Summary statistics (total, uploaded, pending)
- ✅ Complete employee list with upload status
- ✅ Email status tracking
- ✅ Sortable by upload date
- ✅ Shows both uploaded and pending employees

---

## 🔐 Authentication

**All APIs require JWT authentication:**
```http
Authorization: Bearer <jwt_token>
```

---

## 📊 Complete API Summary Table

| # | Endpoint | Method | Type | Purpose | Changes |
|---|----------|--------|------|---------|---------|
| 1 | `/policies/` | GET | Admin | List all policies | None |
| 2 | `/policies/` | POST | Admin | Create policy | None |
| 3 | `/policies/{id}/` | PATCH | Admin | Update policy | None |
| 4 | `/policies/{id}/` | DELETE | Admin | Delete policy | None |
| 5 | `/policy-dashboard/` | GET | Admin | Policy dashboard | None |
| 6 | `/api/policy-allocation/` | GET | Admin | List allocations | None |
| 7 | `/api/policy-allocation/` | POST | Admin | Create allocation | None |
| 8 | `/api/policy-allocation/{id}/` | PATCH | Admin | Update allocation | None |
| 9 | `/api/policy-allocation/{id}/` | DELETE | Admin | Delete allocation | None |
| 10 | `/policies/assigned/{emp_id}/` | GET | Employee | Get assigned policies | ✨ **UPDATED** |
| 11 | `/policies/acknowledge/{emp_id}/` | POST | Employee | Acknowledge policy | None |
| 12 | `/policies/download-acknowledgement-template/{emp_id}/` | GET | Employee | Download template | 🆕 **NEW** |
| 13 | `/policies/upload-signed-document/{emp_id}/` | POST | Employee | Upload signed doc | 🆕 **NEW** |
| 14 | `/policies/signed-document-status/{emp_id}/` | GET | Employee | Check upload status | 🆕 **NEW** |
| 15 | `/policies/view-signed-document/{emp_id}/` | GET | HR/Admin | Download signed doc | 🆕 **NEW** |
| 16 | `/policies/all-signed-documents/` | GET | HR/Admin | Dashboard | 🆕 **NEW** |

**Total APIs:** 16
- **Existing (Unchanged):** 10
- **Updated:** 1
- **New:** 5

---

## 🔄 User Journey

### Employee Complete Flow:

```bash
# Step 1: View assigned policies
GET /policies/assigned/EMP001/
Response: { all_acknowledged: false, total_policies: 5, acknowledged_count: 0, ... }

# Step 2: Acknowledge each policy (repeat for all policies)
POST /policies/acknowledge/EMP001/
Body: { "policy_id": 1 }
Response: { "message": "Policy acknowledged successfully." }

# Step 3: Verify all acknowledged
GET /policies/assigned/EMP001/
Response: { all_acknowledged: true, total_policies: 5, acknowledged_count: 5, ... }

# Step 4: Download template
GET /policies/download-acknowledgement-template/EMP001/
Response: [PDF File]

# Step 5: (Employee signs document offline)

# Step 6: Upload signed document
POST /policies/upload-signed-document/EMP001/
FormData: { signed_document: [file] }
Response: { 
    "message": "Signed document uploaded successfully and email sent to HR",
    "email_sent": true
}

# Step 7: Verify upload
GET /policies/signed-document-status/EMP001/
Response: { "has_uploaded": true, "email_status": "sent", ... }
```

### HR Complete Flow:

```bash
# Step 1: View all employees' status
GET /policies/all-signed-documents/
Response: {
    "summary": { "total_employees": 150, "uploaded": 120, "pending": 30 },
    "data": [...]
}

# Step 2: Download specific employee's document
GET /policies/view-signed-document/EMP001/
Response: [PDF File]

# Step 3: Also receive email automatically
# Email sent to HR with document attached when employee uploads
```

---

## 📧 Email Automation

**When employee uploads signed document:**
- **To:** HR Admin (from database or hr@thedatatechlabs.com)
- **CC:** Employee's email
- **Subject:** "Policy Acknowledgement - Signed Document from [Name]"
- **Body:** Employee details and upload info
- **Attachment:** The signed document

**Email Body:**
```
Dear HR Team,

Employee John Doe (ID: EMP001) has uploaded their signed policy acknowledgement document.

Employee Details:
- Name: John Doe
- Employee ID: EMP001
- Email: john.doe@company.com
- Upload Date: 2026-01-31 14:30:25
- Policies Acknowledged: 5

Please find the signed document attached.

Best Regards,
HRMS System
```

---

## 🎯 Frontend Implementation Guide

### Employee Portal:

1. **Policy List Page:**
   - Show all policies with checkboxes for acknowledgement
   - Track progress: "3/5 policies acknowledged"
   - Disable "Download Template" button until all acknowledged

2. **After All Acknowledged:**
   - Show "Download Template" button
   - Show upload form for signed document
   - Show current upload status

3. **Status Indicators:**
   ```html
   <div>
     {all_acknowledged ? (
       signed_document.has_uploaded ? (
         <span class="badge-success">✅ Document Uploaded</span>
       ) : (
         <button>Upload Signed Document</button>
       )
     ) : (
       <span class="badge-warning">⚠️ Complete all acknowledgements first</span>
     )}
   </div>
   ```

### HR Dashboard:

1. **Summary Cards:**
   - Total Employees
   - Documents Uploaded
   - Pending Uploads
   - Ready for Reminder
   - Email Failed
   - Total Reminders Sent

2. **Employee Table:**
   - Filter: All / Uploaded / Pending / Failed
   - Sort: By date, name, status, reminder count
   - Actions: 
     - Download button for uploaded documents
     - Send Reminder button (enabled when eligible)
     - Resend Email button (enabled when failed)

3. **Status Icons:**
   - ✅ Uploaded & Email Sent
   - ⏳ Uploaded & Email Pending
   - ❌ Uploaded & Email Failed
   - 🔔 Pending with Reminders
   - ⚪ Pending without Reminders

---

## 📊 PHASE 2: REMINDER & MONITORING APIs - 3 NEW APIs

### 8. Enhanced Dashboard with Reminders (HR/Admin) ⭐ RECOMMENDED
**GET** `/policies/signed-documents-dashboard/`

**Purpose:** Replaces basic dashboard with enhanced statistics and reminder tracking.

```json
// Response
{
    "summary": {
        "total_employees": 150,
        "uploaded": 120,
        "pending": 30,
        "pending_ready_for_reminder": 25,    // NEW
        "pending_not_acknowledged": 5,        // NEW
        "email_failed": 2,                    // NEW
        "total_reminders_sent": 47            // NEW
    },
    "data": [
        {
            "employee_id": "EMP001",
            "employee_name": "John Doe",
            "email": "john.doe@company.com",
            "document_path": "signed_acknowledgements/EMP001_signed_20250110_143022.pdf",
            "uploaded_at": "2025-01-10 14:30:22",
            "email_status": "sent",
            "email_sent_at": "2025-01-10 14:30:25",
            "reminder_sent_count": 0,               // NEW
            "last_reminder_sent_at": null,          // NEW
            "last_reminded_by_name": null,          // NEW
            "status": "Uploaded",
            "total_policies": 5,
            "acknowledged_policies": 5,
            "all_acknowledged": true,
            "can_send_reminder": false              // NEW - Frontend flag
        },
        {
            "employee_id": "EMP002",
            "employee_name": "Jane Smith",
            "email": "jane.smith@company.com",
            "document_path": null,
            "uploaded_at": null,
            "email_status": "not_uploaded",
            "email_sent_at": null,
            "reminder_sent_count": 3,               // NEW
            "last_reminder_sent_at": "2025-01-09 10:15:30",  // NEW
            "last_reminded_by_name": "HR Manager",  // NEW
            "status": "Pending",
            "total_policies": 5,
            "acknowledged_policies": 5,
            "all_acknowledged": true,
            "can_send_reminder": true               // NEW - Enable button
        }
    ]
}
```

**New Fields Explained:**
- `pending_ready_for_reminder` - Acknowledged all but not uploaded (can send reminder)
- `pending_not_acknowledged` - Still reviewing policies (cannot send reminder)
- `email_failed` - Count of failed email deliveries
- `total_reminders_sent` - Cumulative reminders across all employees
- `reminder_sent_count` - How many times this employee was reminded
- `last_reminder_sent_at` - Timestamp of last reminder
- `last_reminded_by_name` - Name of HR who sent last reminder
- `can_send_reminder` - Boolean flag for frontend button enablement

---

### 9. Send Reminder to Employee (HR/Admin)
**POST** `/policies/send-reminder/{emp_id}/`

**Purpose:** Send notification to employee + track reminder in database.

**Validation:**
- Employee must exist
- Employee must have acknowledged ALL assigned policies
- Employee must NOT have uploaded document yet

**Integration:** Creates notification in `ci_notification` table (appears in `/notifications/global/{emp_id}/`)

```json
// Request
POST /policies/send-reminder/EMP002/
Body: {
    "user_id": 123  // HR/Admin user ID (required)
}

// Success Response
{
    "message": "Reminder sent successfully to employee",
    "employee_id": "EMP002",
    "employee_name": "Jane Smith",
    "employee_email": "jane.smith@company.com",
    "reminder_sent_at": "2025-01-10 15:30:45",
    "total_reminders_sent": 3,
    "notification_sent": true
}

// Error: Not all policies acknowledged
{
    "error": "Employee has not acknowledged all policies yet",
    "acknowledged": 3,
    "total_policies": 5
}

// Error: Already uploaded
{
    "error": "Employee has already uploaded the signed document",
    "document_path": "signed_acknowledgements/EMP002_signed_20250110_143022.pdf",
    "email_status": "sent"
}
```

**Notification Text Sent:**
```
"Please download, sign, and upload your Policy Acknowledgement Document. Go to Policies section to complete this action."
```

**Database Updates:**
```sql
-- Creates notification
INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
VALUES (hr_user_id, employee_user_id, 'Please download...', NOW())

-- Tracks reminder
UPDATE ci_policy_signed_documents
SET reminder_sent_count = reminder_sent_count + 1,
    last_reminder_sent_at = NOW(),
    last_reminded_by = hr_user_id
WHERE emp_id = 'EMP002'
```

---

### 10. Resend Email to HR (HR/Admin)
**POST** `/policies/resend-email/{emp_id}/`

**Purpose:** Retry sending email to HR if it failed previously (SMTP error, network issue, etc.)

**Validation:**
- Employee must exist
- Signed document must be uploaded
- Document file must physically exist on server

```json
// Request (no body needed)
POST /policies/resend-email/EMP003/

// Success Response
{
    "message": "Email resent successfully to HR",
    "employee_id": "EMP003",
    "employee_name": "Mike Johnson",
    "hr_email": "hr@thedatatechlabs.com",
    "email_sent_at": "2025-01-10 16:45:30",
    "previous_status": "failed"
}

// Error: No document uploaded
{
    "error": "No signed document found for this employee"
}

// Error: File missing on server
{
    "error": "Signed document file not found on server"
}

// Error: Email failed again
{
    "error": "Failed to send email: SMTP authentication error",
    "employee_id": "EMP003",
    "employee_name": "Mike Johnson"
}
```

**Email Content:**
- Subject: `Policy Acknowledgement - Signed Document from {employee_name}`
- To: HR email (from admin users table, falls back to `hr@thedatatechlabs.com`)
- CC: Employee email
- Attachment: Signed document PDF

**Database Update:**
```sql
-- On success
UPDATE ci_policy_signed_documents
SET email_status = 'sent', email_sent_at = NOW()
WHERE emp_id = 'EMP003'

-- On failure
UPDATE ci_policy_signed_documents
SET email_status = 'failed'
WHERE emp_id = 'EMP003'
```

---

## 🗄️ Database Schema Updates (Phase 2)

Execute this in MySQL Workbench:

```sql
-- Add reminder tracking columns
ALTER TABLE ci_policy_signed_documents
ADD COLUMN reminder_sent_count INT DEFAULT 0,
ADD COLUMN last_reminder_sent_at DATETIME DEFAULT NULL,
ADD COLUMN last_reminded_by INT DEFAULT NULL,
ADD INDEX idx_reminder_count (reminder_sent_count),
ADD INDEX idx_last_reminder (last_reminder_sent_at);

-- Update email_status enum to include 'not_uploaded'
ALTER TABLE ci_policy_signed_documents
MODIFY COLUMN email_status ENUM('pending', 'sent', 'failed', 'not_uploaded') DEFAULT 'pending';
```

**Updated Table Structure:**
```sql
CREATE TABLE ci_policy_signed_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    signed_document VARCHAR(255) NOT NULL,
    uploaded_at DATETIME DEFAULT NULL,
    email_sent_at DATETIME DEFAULT NULL,
    email_status ENUM('pending', 'sent', 'failed', 'not_uploaded') DEFAULT 'pending',
    reminder_sent_count INT DEFAULT 0,              -- NEW
    last_reminder_sent_at DATETIME DEFAULT NULL,    -- NEW
    last_reminded_by INT DEFAULT NULL,              -- NEW (user_id from ci_erp_users)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_emp_id (emp_id),
    INDEX idx_email_status (email_status),
    INDEX idx_reminder_count (reminder_sent_count), -- NEW
    INDEX idx_last_reminder (last_reminder_sent_at) -- NEW
);
```

---

## 🔔 Notification System Integration

### How Reminders Appear to Employees

When HR sends reminder via `POST /policies/send-reminder/EMP002/`:

**1. Database Insert:**
```sql
INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
VALUES (hr_user_id, employee_user_id, 'Please download, sign and upload...', NOW())
```

**2. Employee Sees It:**
```json
GET /notifications/global/EMP002/

Response:
{
    "notifications": [
        {
            "notification_text": "Please download, sign, and upload your Policy Acknowledgement Document. Go to Policies section to complete this action.",
            "created_at": "2025-01-10 15:30:45",
            "sent_by": "HR Manager"
        }
    ]
}
```

**3. Tracking:**
- Notification stored in `ci_notification` table
- Reminder count incremented in `ci_policy_signed_documents` table
- Dashboard shows "Last reminded: 2025-01-10 15:30:45 by HR Manager"

---

## 📱 Frontend Implementation Guide (Phase 2)

### Enhanced Dashboard Component

```jsx
import React, { useState, useEffect } from 'react';

const PolicyDashboard = () => {
    const [data, setData] = useState(null);
    
    useEffect(() => {
        fetchDashboard();
    }, []);
    
    const fetchDashboard = async () => {
        const response = await fetch('/policies/signed-documents-dashboard/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        setData(await response.json());
    };
    
    const sendReminder = async (empId) => {
        const response = await fetch(`/policies/send-reminder/${empId}/`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUserId  // Get from logged-in HR user
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            toast.success(`Reminder sent to ${result.employee_name}`);
            fetchDashboard(); // Refresh
        } else {
            toast.error(result.error);
        }
    };
    
    const resendEmail = async (empId) => {
        if (!confirm('Resend email to HR?')) return;
        
        const response = await fetch(`/policies/resend-email/${empId}/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            toast.success('Email resent successfully');
            fetchDashboard();
        } else {
            toast.error(result.error);
        }
    };
    
    return (
        <div>
            {/* Summary Cards */}
            <div className="stats-grid">
                <StatCard title="Total Employees" value={data?.summary.total_employees} />
                <StatCard title="Uploaded" value={data?.summary.uploaded} color="green" />
                <StatCard title="Pending" value={data?.summary.pending} color="orange" />
                <StatCard title="Ready for Reminder" value={data?.summary.pending_ready_for_reminder} color="blue" />
                <StatCard title="Email Failed" value={data?.summary.email_failed} color="red" />
                <StatCard title="Total Reminders" value={data?.summary.total_reminders_sent} />
            </div>
            
            {/* Employee Table */}
            <table>
                <thead>
                    <tr>
                        <th>Employee</th>
                        <th>Status</th>
                        <th>Email Status</th>
                        <th>Reminders Sent</th>
                        <th>Last Reminder</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {data?.data.map(emp => (
                        <tr key={emp.employee_id}>
                            <td>
                                {emp.employee_name}<br />
                                <small>{emp.employee_id}</small>
                            </td>
                            <td>
                                <StatusBadge status={emp.status} />
                            </td>
                            <td>
                                <EmailBadge status={emp.email_status} />
                            </td>
                            <td>{emp.reminder_sent_count}</td>
                            <td>
                                {emp.last_reminder_sent_at ? (
                                    <>
                                        {emp.last_reminder_sent_at}<br />
                                        <small>by {emp.last_reminded_by_name}</small>
                                    </>
                                ) : '-'}
                            </td>
                            <td>
                                {emp.can_send_reminder && (
                                    <button onClick={() => sendReminder(emp.employee_id)}>
                                        📧 Send Reminder
                                    </button>
                                )}
                                {emp.email_status === 'failed' && (
                                    <button onClick={() => resendEmail(emp.employee_id)}>
                                        🔄 Resend Email
                                    </button>
                                )}
                                {emp.status === 'Uploaded' && (
                                    <a href={`/policies/view-signed-document/${emp.employee_id}/`}>
                                        📄 View Doc
                                    </a>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
```

### Bulk Reminder Function

```javascript
const sendBulkReminders = async () => {
    const eligible = data.data.filter(emp => emp.can_send_reminder);
    
    if (!confirm(`Send reminders to ${eligible.length} employees?`)) return;
    
    let success = 0;
    let failed = 0;
    
    for (const emp of eligible) {
        try {
            await sendReminder(emp.employee_id);
            success++;
            await new Promise(resolve => setTimeout(resolve, 500)); // Rate limiting
        } catch (error) {
            failed++;
        }
    }
    
    toast.success(`Sent ${success} reminders, ${failed} failed`);
    fetchDashboard();
};
```

---

## ⚠️ Important Notes (Updated)

1. **File Size Limit:** 10MB maximum (configurable in settings.py)
2. **Allowed File Types:** PDF, JPG, JPEG, PNG, DOCX
3. **Template File:** Must place `ebook.pdf` in `media/` folder
4. **Database Tables:** 
   - Must create `ci_policy_signed_documents` table (Phase 1)
   - Must run ALTER TABLE for reminder columns (Phase 2)
5. **Email:** Sends automatically; if fails, document still saved with status='failed'
6. **Re-upload:** Replaces previous document; no version history
7. **Reminder Eligibility:** Employee must acknowledge ALL policies before reminder can be sent
8. **Notification Integration:** Uses existing `ci_notification` table and `/notifications/global/` endpoint
9. **Email Resend:** Only works if document uploaded and file exists on server
10. **Rate Limiting:** Frontend should implement delays for bulk reminder operations

---

## 🔄 Workflow Diagrams

### Complete Employee Journey
```
Employee Login
    ↓
Views Policies (GET /policies/assigned/{emp_id}/)
    ↓
Acknowledges Each Policy (POST /policies/acknowledge/)
    ↓
Downloads Template (GET /policies/download-acknowledgement-template/{emp_id}/)
    ↓
Signs Offline
    ↓
Uploads Signed Doc (POST /policies/upload-signed-document/{emp_id}/)
    ↓
System Auto-Emails HR
    ↓
Employee Sees "Uploaded ✅" Status
```

### HR Monitoring & Reminder Flow
```
HR Opens Dashboard (GET /policies/signed-documents-dashboard/)
    ↓
Sees Summary:
  - 120 Uploaded
  - 25 Pending (Ready for Reminder)
  - 5 Pending (Not Acknowledged)
  - 2 Email Failed
    ↓
HR Actions:
  ├─ Send Reminder (POST /policies/send-reminder/{emp_id}/)
  │     → Creates notification
  │     → Employee receives in-app notification
  │     → Reminder count increments
  │
  ├─ Resend Failed Email (POST /policies/resend-email/{emp_id}/)
  │     → Retries email to HR
  │     → Updates email_status
  │
  └─ View Document (GET /policies/view-signed-document/{emp_id}/)
        → Downloads signed PDF
```

---

## 📊 API Comparison Table

| API Endpoint | Method | Phase | User Type | Purpose |
|-------------|--------|-------|-----------|---------|
| `/policies/` | GET/POST | Existing | Admin | Create/List policies |
| `/policies/{id}/` | PATCH/DELETE | Existing | Admin | Update/Delete policy |
| `/policies/allocated/` | GET | Existing | Admin | View allocations |
| `/policies/allocate/` | POST | Existing | Admin | Allocate to employees |
| `/policies/deallocate/` | POST | Existing | Admin | Remove from employees |
| `/policies/assigned/{emp_id}/` | GET | **Updated** | Employee | View assigned (includes signed_document object) |
| `/policies/acknowledge/` | POST | Existing | Employee | Acknowledge policy |
| `/policies/check-acknowledge/` | GET | Existing | Employee | Check status |
| `/policies/documents/` | GET | Existing | Employee | Get policy PDFs |
| `/policies/view-document/{id}/` | GET | Existing | Employee | Download PDF |
| `/policies/download-acknowledgement-template/{emp_id}/` | GET | **Phase 1** | Employee | Download template |
| `/policies/upload-signed-document/{emp_id}/` | POST | **Phase 1** | Employee | Upload signed doc |
| `/policies/signed-document-status/{emp_id}/` | GET | **Phase 1** | Employee | Check upload status |
| `/policies/view-signed-document/{emp_id}/` | GET | **Phase 1** | HR/Admin | Download employee doc |
| `/policies/all-signed-documents/` | GET | **Phase 1** | HR/Admin | Basic dashboard |
| `/policies/signed-documents-dashboard/` | GET | **Phase 2** ⭐ | HR/Admin | Enhanced dashboard |
| `/policies/send-reminder/{emp_id}/` | POST | **Phase 2** | HR/Admin | Send notification |
| `/policies/resend-email/{emp_id}/` | POST | **Phase 2** | HR/Admin | Retry failed email |

**Total: 19 APIs**

---

## 🧪 Testing Scenarios

### Test Case 1: Employee Complete Flow
```bash
# 1. Get assigned policies
curl -X GET "http://localhost:8000/policies/assigned/EMP001/" \
  -H "Authorization: Bearer <token>"

# 2. Acknowledge each policy
curl -X POST "http://localhost:8000/policies/acknowledge/" \
  -H "Authorization: Bearer <token>" \
  -d '{"policy_id": 1, "emp_id": "EMP001"}'

# 3. Download template
curl -X GET "http://localhost:8000/policies/download-acknowledgement-template/EMP001/" \
  -H "Authorization: Bearer <token>" \
  -o template.pdf

# 4. Upload signed document
curl -X POST "http://localhost:8000/policies/upload-signed-document/EMP001/" \
  -H "Authorization: Bearer <token>" \
  -F "signed_document=@signed_template.pdf"

# 5. Verify upload status
curl -X GET "http://localhost:8000/policies/signed-document-status/EMP001/" \
  -H "Authorization: Bearer <token>"
```

### Test Case 2: HR Reminder Flow
```bash
# 1. View enhanced dashboard
curl -X GET "http://localhost:8000/policies/signed-documents-dashboard/" \
  -H "Authorization: Bearer <hr_token>"

# 2. Send reminder to employee
curl -X POST "http://localhost:8000/policies/send-reminder/EMP002/" \
  -H "Authorization: Bearer <hr_token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'

# 3. Employee checks notifications
curl -X GET "http://localhost:8000/notifications/global/EMP002/" \
  -H "Authorization: Bearer <employee_token>"

# 4. Resend failed email
curl -X POST "http://localhost:8000/policies/resend-email/EMP003/" \
  -H "Authorization: Bearer <hr_token>"

# 5. View uploaded document
curl -X GET "http://localhost:8000/policies/view-signed-document/EMP001/" \
  -H "Authorization: Bearer <hr_token>" \
  -o employee_signed_doc.pdf
```

---

## 🚀 Quick Start Checklist

### Phase 1 Setup (Signed Documents)
- [ ] Create `ci_policy_signed_documents` table in MySQL
- [ ] Place `ebook.pdf` template in `media/` folder
- [ ] Test download template API
- [ ] Test upload signed document API
- [ ] Verify email is sent to HR
- [ ] Test HR dashboard (`/policies/all-signed-documents/`)
- [ ] Test HR document download

### Phase 2 Setup (Reminders)
- [ ] Run ALTER TABLE to add reminder columns
- [ ] Test enhanced dashboard (`/policies/signed-documents-dashboard/`)
- [ ] Test send reminder API
- [ ] Verify notification appears in `/notifications/global/{emp_id}/`
- [ ] Test resend email for failed status
- [ ] Update frontend to use enhanced dashboard
- [ ] Add "Send Reminder" button to UI
- [ ] Add "Resend Email" button to UI
- [ ] Test bulk reminder functionality
- [ ] Deploy to production

---

## 📞 Support & Documentation

**Detailed Documentation:**
- **Phase 1:** See `POLICY_SIGNED_DOCUMENT_API_DOCUMENTATION.md`
- **Phase 2:** See `POLICY_REMINDER_MONITORING_API.md`
- **Implementation Summary:** See `PHASE_2_IMPLEMENTATION_SUMMARY.md`

**Common Issues:**
1. **Email not sending:** Check SMTP settings in `settings.py`
2. **Template not found:** Verify `ebook.pdf` exists in `media/` folder
3. **Reminder button disabled:** Employee must acknowledge all policies first
4. **Cannot resend email:** Document must be uploaded and file must exist on server
5. **Notification not appearing:** Check `ci_notification` table for INSERT

---

## 🔮 Future Enhancements (Optional)

1. **Auto-Reminders:** Scheduled job to auto-send reminders after X days
2. **Custom Templates:** Allow HR to customize notification text
3. **HTML Emails:** Rich email templates for HR notifications
4. **Reminder History:** Track each individual reminder (not just count)
5. **Bulk Operations:** Single API to send reminders to multiple employees
6. **Version Control:** Track multiple document versions
7. **Digital Signature:** In-app signing instead of offline
8. **Analytics Dashboard:** Graphs showing upload trends, reminder effectiveness

---

**Last Updated:** Phase 2 - January 2025  
**API Version:** v2.0 (Phase 1 + Phase 2)  
**Total APIs:** 19 (10 Unchanged + 1 Updated + 8 New)

---**Last Updated:** January 31, 2026
**Version:** 1.0

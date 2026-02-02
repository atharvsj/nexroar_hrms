# Policy Reminder & Monitoring API Documentation

## Overview
These APIs enable HR/Admin to monitor policy signed document submissions, send reminders to employees, and resend failed emails. All APIs integrate with the existing notification system.

---

## Database Schema Update Required

Before using these APIs, execute this SQL in MySQL Workbench:

```sql
ALTER TABLE ci_policy_signed_documents
ADD COLUMN reminder_sent_count INT DEFAULT 0,
ADD COLUMN last_reminder_sent_at DATETIME DEFAULT NULL,
ADD COLUMN last_reminded_by INT DEFAULT NULL,
ADD INDEX idx_reminder_count (reminder_sent_count),
ADD INDEX idx_last_reminder (last_reminder_sent_at);

-- Also update email_status enum to include 'not_uploaded'
ALTER TABLE ci_policy_signed_documents
MODIFY COLUMN email_status ENUM('pending', 'sent', 'failed', 'not_uploaded') DEFAULT 'pending';
```

---

## API Endpoints

### 1. Enhanced Dashboard (Recommended for HR/Admin)
**Endpoint:** `GET /policies/signed-documents-dashboard/`

**Description:** Enhanced version of the basic dashboard with reminder statistics and actionable insights.

**Authorization:** Bearer Token (JWT)

**Request Example:**
```http
GET /policies/signed-documents-dashboard/ HTTP/1.1
Host: your-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
    "summary": {
        "total_employees": 150,
        "uploaded": 120,
        "pending": 30,
        "pending_ready_for_reminder": 25,
        "pending_not_acknowledged": 5,
        "email_failed": 2,
        "total_reminders_sent": 47
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
            "reminder_sent_count": 0,
            "last_reminder_sent_at": null,
            "last_reminded_by_name": null,
            "status": "Uploaded",
            "total_policies": 5,
            "acknowledged_policies": 5,
            "all_acknowledged": true,
            "can_send_reminder": false
        },
        {
            "employee_id": "EMP002",
            "employee_name": "Jane Smith",
            "email": "jane.smith@company.com",
            "document_path": null,
            "uploaded_at": null,
            "email_status": "not_uploaded",
            "email_sent_at": null,
            "reminder_sent_count": 3,
            "last_reminder_sent_at": "2025-01-09 10:15:30",
            "last_reminded_by_name": "HR Manager",
            "status": "Pending",
            "total_policies": 5,
            "acknowledged_policies": 5,
            "all_acknowledged": true,
            "can_send_reminder": true
        },
        {
            "employee_id": "EMP003",
            "employee_name": "Mike Johnson",
            "email": "mike.johnson@company.com",
            "document_path": "signed_acknowledgements/EMP003_signed_20250109_091530.pdf",
            "uploaded_at": "2025-01-09 09:15:30",
            "email_status": "failed",
            "email_sent_at": null,
            "reminder_sent_count": 0,
            "last_reminder_sent_at": null,
            "last_reminded_by_name": null,
            "status": "Uploaded",
            "total_policies": 5,
            "acknowledged_policies": 5,
            "all_acknowledged": true,
            "can_send_reminder": false
        }
    ]
}
```

**Field Descriptions:**
- `pending_ready_for_reminder`: Employees who acknowledged all policies but haven't uploaded document
- `pending_not_acknowledged`: Employees who haven't finished acknowledging policies
- `email_failed`: Count of uploaded documents where email to HR failed
- `total_reminders_sent`: Sum of all reminders sent across all employees
- `can_send_reminder`: Boolean flag indicating if reminder button should be enabled for this employee
- `last_reminded_by_name`: Name of HR/Admin who sent the last reminder

---

### 2. Send Reminder to Employee
**Endpoint:** `POST /policies/send-reminder/{emp_id}/`

**Description:** Send a notification to employee to upload their signed policy document. Creates entry in `ci_notification` table and tracks reminder statistics.

**Authorization:** Bearer Token (JWT) - HR/Admin only

**Request Example:**
```http
POST /policies/send-reminder/EMP002/ HTTP/1.1
Host: your-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
    "user_id": 123
}
```

**Request Body:**
- `user_id` (required): The user ID of the HR/Admin sending the reminder

**Success Response (200 OK):**
```json
{
    "message": "Reminder sent successfully to employee",
    "employee_id": "EMP002",
    "employee_name": "Jane Smith",
    "employee_email": "jane.smith@company.com",
    "reminder_sent_at": "2025-01-10 15:30:45",
    "total_reminders_sent": 3,
    "notification_sent": true
}
```

**Error Responses:**

**400 Bad Request** - Missing user_id:
```json
{
    "error": "user_id is required in request body"
}
```

**404 Not Found** - Employee doesn't exist:
```json
{
    "error": "Employee not found"
}
```

**400 Bad Request** - No policies assigned:
```json
{
    "error": "No policies assigned to this employee"
}
```

**400 Bad Request** - Not all policies acknowledged:
```json
{
    "error": "Employee has not acknowledged all policies yet",
    "acknowledged": 3,
    "total_policies": 5
}
```

**400 Bad Request** - Already uploaded:
```json
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

**How It Works:**
1. Extracts `user_id` from request body (HR/Admin user ID)
2. Validates employee exists and has acknowledged all policies
3. Checks if document is not already uploaded
4. Creates notification in `ci_notification` table (appears in `/notifications/global/{employee_id}/`)
5. Updates/inserts reminder tracking in `ci_policy_signed_documents`:
   - Increments `reminder_sent_count`
   - Updates `last_reminder_sent_at` timestamp
   - Records `last_reminded_by` (HR user ID from request)
6. Returns confirmation with reminder statistics

---

### 3. Resend Email to HR
**Endpoint:** `POST /policies/resend-email/{emp_id}/`

**Description:** Retry sending email to HR if it failed previously. Useful when SMTP was down or there was a network issue.

**Authorization:** Bearer Token (JWT) - HR/Admin only

**Request Example:**
```http
POST /policies/resend-email/EMP003/ HTTP/1.1
Host: your-domain.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Success Response (200 OK):**
```json
{
    "message": "Email resent successfully to HR",
    "employee_id": "EMP003",
    "employee_name": "Mike Johnson",
    "hr_email": "hr@thedatatechlabs.com",
    "email_sent_at": "2025-01-10 16:45:30",
    "previous_status": "failed"
}
```

**Error Responses:**

**404 Not Found** - Employee doesn't exist:
```json
{
    "error": "Employee not found"
}
```

**404 Not Found** - No document uploaded:
```json
{
    "error": "No signed document found for this employee"
}
```

**404 Not Found** - File missing on server:
```json
{
    "error": "Signed document file not found on server"
}
```

**500 Internal Server Error** - Email sending failed:
```json
{
    "error": "Failed to send email: SMTP authentication error",
    "employee_id": "EMP003",
    "employee_name": "Mike Johnson"
}
```

**How It Works:**
1. Validates employee exists and has uploaded document
2. Checks if document file physically exists on server
3. Gets HR email from admin user (falls back to `hr@thedatatechlabs.com`)
4. Sends email with document attachment and employee details
5. Updates `email_status` to `sent` and records `email_sent_at` timestamp
6. If email fails, updates status to `failed`

---

## Integration with Existing Notification System

### Notification Flow
When HR/Admin sends a reminder using `POST /policies/send-reminder/{emp_id}/`:

1. **Database Insert:**
```sql
INSERT INTO ci_notification (send_from_id, send_to_id, notification_text, created_at)
VALUES (hr_user_id, employee_user_id, 'Please download, sign...', NOW())
```

2. **Employee Sees Notification:**
Employee calls `GET /notifications/global/{employee_id}/` and receives:
```json
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

---

## Complete Workflow Example

### Scenario: HR monitors and reminds employees

**Step 1:** HR opens dashboard
```http
GET /policies/signed-documents-dashboard/
```

Response shows:
- 25 employees ready for reminder (`can_send_reminder: true`)
- 2 employees with failed emails
- 5 employees still acknowledging policies

**Step 2:** HR sends reminder to employee who acknowledged all but didn't upload
```http
POST /policies/send-reminder/EMP002/
```

Result:
- Notification appears in employee's notification list
- `reminder_sent_count` becomes 1
- `last_reminder_sent_at` updated
- Dashboard now shows "Last reminded: 2025-01-10 15:30:45 by HR Manager"

**Step 3:** Employee uploads document
```http
POST /policies/upload-signed-document/EMP002/
```

Result:
- Document saved
- Email auto-sent to HR
- Status changes from "Pending" to "Uploaded"
- Employee no longer appears in "ready for reminder" list

**Step 4:** HR notices failed email for EMP003
```http
POST /policies/resend-email/EMP003/
```

Result:
- Email re-attempted
- If successful, `email_status` changes from "failed" to "sent"
- HR receives email with document attachment

---

## Frontend Implementation Guide

### Dashboard UI Components

**1. Summary Cards:**
```jsx
<div className="stats-grid">
    <StatCard title="Total Employees" value={summary.total_employees} />
    <StatCard title="Uploaded" value={summary.uploaded} color="green" />
    <StatCard title="Pending" value={summary.pending} color="orange" />
    <StatCard title="Ready for Reminder" value={summary.pending_ready_for_reminder} color="blue" />
    <StatCard title="Email Failed" value={summary.email_failed} color="red" />
    <StatCard title="Total Reminders Sent" value={summary.total_reminders_sent} />
</div>
```

**2. Employee Table:**
```jsx
<table>
    <thead>
        <tr>
            <th>Employee ID</th>
            <th>Name</th>
            <th>Status</th>
            <th>Uploaded At</th>
            <th>Email Status</th>
            <th>Reminders Sent</th>
            <th>Last Reminder</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {data.map(employee => (
            <tr key={employee.employee_id}>
                <td>{employee.employee_id}</td>
                <td>{employee.employee_name}</td>
                <td>
                    <StatusBadge status={employee.status} />
                </td>
                <td>{employee.uploaded_at || '-'}</td>
                <td>
                    <EmailStatusBadge status={employee.email_status} />
                </td>
                <td>{employee.reminder_sent_count}</td>
                <td>
                    {employee.last_reminder_sent_at ? (
                        <>
                            {employee.last_reminder_sent_at}<br />
                            <small>by {employee.last_reminded_by_name}</small>
                        </>
                    ) : '-'}
                </td>
                <td>
                    {employee.can_send_reminder && (
                        <Button onClick={() => sendReminder(employee.employee_id)}>
                            Send Reminder
                        </Button>
                    )}
                    {employee.email_status === 'failed' && (
                        <Button onClick={() => resendEmail(employee.employee_id)}>
                            Resend Email
                        </Button>
                    )}
                    {employee.status === 'Uploaded' && (
                        <Button onClick={() => viewDocument(employee.employee_id)}>
                            View Document
                        </Button>
                    )}
                </td>
            </tr>
        ))}
    </tbody>
</table>
```

**3. Send Reminder Function:**
```javascript
const sendReminder = async (empId) => {
    try {
        const response = await fetch(`/policies/send-reminder/${empId}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUserId  // Get from logged-in user context
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            toast.success(`Reminder sent to ${data.employee_name}. Total reminders: ${data.total_reminders_sent}`);
            refreshDashboard(); // Reload dashboard data
        } else {
            toast.error(data.error);
        }
    } catch (error) {
        toast.error('Failed to send reminder');
    }
};
```

**4. Resend Email Function:**
```javascript
const resendEmail = async (empId) => {
    if (!confirm('Are you sure you want to resend the email to HR?')) return;
    
    try {
        const response = await fetch(`/policies/resend-email/${empId}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            toast.success(`Email resent successfully to ${data.hr_email}`);
            refreshDashboard();
        } else {
            toast.error(data.error);
        }
    } catch (error) {
        toast.error('Failed to resend email');
    }
};
```

---

## Tracking Manual Follow-ups

### Question: How to track when HR sends manual emails outside the system?

**Answer:** The system tracks automatic reminders through the notification system. For manual email follow-ups:

**Option 1: Use the Send Reminder API**
Even if HR manually emails the employee, they should click "Send Reminder" button in the dashboard. This:
- Creates a notification in the system
- Tracks the reminder count and timestamp
- Provides audit trail of when employee was contacted
- HR can then send additional manual email if needed

**Option 2: Manual Tracking Field (Future Enhancement)**
If you need to track purely manual emails (sent outside the system), you could add:
```sql
ALTER TABLE ci_policy_signed_documents
ADD COLUMN manual_followup_notes TEXT,
ADD COLUMN last_manual_followup_at DATETIME;
```

Then create an API:
```http
POST /policies/add-manual-followup/{emp_id}/
Body: {
    "note": "Called employee on phone, sent email reminder from Outlook",
    "timestamp": "2025-01-10 16:00:00"
}
```

**Recommended Approach:**
Use the Send Reminder API for all employee contacts. This ensures:
- Employee receives in-app notification
- Complete audit trail in database
- Statistics are accurate
- Consistent tracking mechanism

---

## Status & Email Status Values

### Document Status
- `Pending`: Employee has not uploaded document
- `Uploaded`: Employee has uploaded document

### Email Status
- `not_uploaded`: Document not yet uploaded
- `pending`: Document uploaded, email queued (rarely used)
- `sent`: Email successfully sent to HR
- `failed`: Email sending failed due to SMTP/network error

---

## Common Use Cases

### Use Case 1: Bulk Reminder to All Pending Employees
Frontend can filter `can_send_reminder: true` and provide "Send to All" button:
```javascript
const sendBulkReminders = async () => {
    const eligibleEmployees = dashboardData.data.filter(emp => emp.can_send_reminder);
    
    for (const emp of eligibleEmployees) {
        await sendReminder(emp.employee_id);
        await new Promise(resolve => setTimeout(resolve, 500)); // Rate limiting
    }
    
    toast.success(`Reminders sent to ${eligibleEmployees.length} employees`);
};
```

### Use Case 2: Follow-up on Old Reminders
Filter employees by `last_reminder_sent_at` older than 7 days:
```javascript
const oldReminders = dashboardData.data.filter(emp => {
    if (!emp.last_reminder_sent_at || emp.status !== 'Pending') return false;
    
    const daysSince = (new Date() - new Date(emp.last_reminder_sent_at)) / (1000 * 60 * 60 * 24);
    return daysSince > 7;
});
```

### Use Case 3: Retry All Failed Emails
```javascript
const retryFailedEmails = async () => {
    const failedEmails = dashboardData.data.filter(emp => emp.email_status === 'failed');
    
    for (const emp of failedEmails) {
        await resendEmail(emp.employee_id);
    }
    
    toast.success(`Retried ${failedEmails.length} failed emails`);
};
```

---

## API Summary Table

| Endpoint | Method | Purpose | User Type |
|----------|--------|---------|-----------|
| `/policies/signed-documents-dashboard/` | GET | Enhanced dashboard with reminder stats | HR/Admin |
| `/policies/send-reminder/{emp_id}/` | POST | Send notification reminder to employee | HR/Admin |
| `/policies/resend-email/{emp_id}/` | POST | Retry failed email to HR | HR/Admin |
| `/policies/all-signed-documents/` | GET | Basic dashboard (deprecated, use enhanced version) | HR/Admin |

---

## Testing Checklist

- [ ] HR can view enhanced dashboard with summary statistics
- [ ] Send reminder button only enabled for eligible employees (`can_send_reminder: true`)
- [ ] Reminder notification appears in employee's `/notifications/global/{emp_id}/`
- [ ] `reminder_sent_count` increments correctly
- [ ] `last_reminder_sent_at` timestamp updates
- [ ] `last_reminded_by_name` shows HR name correctly
- [ ] Cannot send reminder if employee hasn't acknowledged all policies
- [ ] Cannot send reminder if employee already uploaded document
- [ ] Resend email works for `failed` status
- [ ] Email status changes from `failed` to `sent` after successful resend
- [ ] Dashboard refreshes automatically after reminder sent
- [ ] Bulk reminder sending works without API rate limiting issues
- [ ] All fields in dashboard display correctly (null handling)

---

## Notes
- All APIs use JWT authentication via `Authorization: Bearer <token>` header
- HR/Admin user ID is extracted from `request.user.id`
- Notification system integration is automatic (no extra configuration needed)
- Email SMTP settings must be configured in Django settings for email functionality
- Dashboard is sorted by: uploaded_at DESC → last_reminder_sent_at DESC → employee_id ASC

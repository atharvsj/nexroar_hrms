# Phase 2 Implementation Summary - Policy Reminder & Monitoring

## What Was Added

### 3 New API Endpoints
1. **Enhanced Dashboard** - `GET /policies/signed-documents-dashboard/`
   - Replaces basic dashboard with advanced statistics
   - Shows reminder counts, last reminder timestamps, HR names
   - Includes actionable flags (`can_send_reminder`)
   
2. **Send Reminder** - `POST /policies/send-reminder/{emp_id}/`
   - Creates notification in `ci_notification` table
   - Tracks reminder count and timestamps
   - Validates eligibility before sending
   
3. **Resend Email** - `POST /policies/resend-email/{emp_id}/`
   - Retries failed email sending
   - Updates email status on success/failure

### Database Schema Changes Required

Execute this SQL in MySQL Workbench:

```sql
-- Add reminder tracking columns
ALTER TABLE ci_policy_signed_documents
ADD COLUMN reminder_sent_count INT DEFAULT 0,
ADD COLUMN last_reminder_sent_at DATETIME DEFAULT NULL,
ADD COLUMN last_reminded_by INT DEFAULT NULL,
ADD INDEX idx_reminder_count (reminder_sent_count),
ADD INDEX idx_last_reminder (last_reminder_sent_at);

-- Update email_status enum
ALTER TABLE ci_policy_signed_documents
MODIFY COLUMN email_status ENUM('pending', 'sent', 'failed', 'not_uploaded') DEFAULT 'pending';
```

### Files Modified

**1. `app/views.py`** - Added 3 new class-based views (approx. 350 lines):
   - `SendPolicyReminderView` (lines ~16050-16180)
   - `ResendEmailToHRView` (lines ~16183-16300)
   - `PolicySignedDocumentsDashboardView` (lines ~16303-16450)

**2. `app/urls.py`** - Added 3 new URL patterns:
   ```python
   path('policies/send-reminder/<str:emp_id>/', SendPolicyReminderView.as_view()),
   path('policies/resend-email/<str:emp_id>/', ResendEmailToHRView.as_view()),
   path('policies/signed-documents-dashboard/', PolicySignedDocumentsDashboardView.as_view()),
   ```

**3. Documentation Files Created:**
   - `POLICY_REMINDER_MONITORING_API.md` - Complete API documentation with examples
   - `PHASE_2_IMPLEMENTATION_SUMMARY.md` - This file

---

## How It Works

### Reminder Flow
```
HR clicks "Send Reminder" button
    ↓
POST /policies/send-reminder/EMP002/
    ↓
System validates:
  - Employee exists
  - All policies acknowledged
  - Document not already uploaded
    ↓
System creates:
  - Notification in ci_notification table
  - Tracking record in ci_policy_signed_documents
    ↓
Employee sees notification in:
  - GET /notifications/global/{employee_id}/
    ↓
Employee uploads document
    ↓
Status changes to "Uploaded"
```

### Email Retry Flow
```
HR sees "Email Failed" badge
    ↓
HR clicks "Resend Email" button
    ↓
POST /policies/resend-email/EMP003/
    ↓
System validates:
  - Employee exists
  - Document uploaded
  - File exists on server
    ↓
System sends email to HR
    ↓
Updates email_status:
  - Success → "sent"
  - Failure → "failed"
```

---

## Integration Points

### With Existing Notification System
- Uses `ci_notification` table (same as birthdays, announcements, etc.)
- Appears in `GET /notifications/global/{employee_id}/` response
- Follows same pattern: `send_from_id`, `send_to_id`, `notification_text`, `created_at`

### With Email System
- Uses Django `EmailMessage` class
- Same SMTP configuration as upload email
- Falls back to `hr@thedatatechlabs.com` if no admin email found

---

## Frontend Requirements

### Dashboard UI Components Needed
1. **Summary Stats Cards** - Display 6 metrics from `summary` object
2. **Employee Table** - Show all employees with status, reminder count, actions
3. **Action Buttons**:
   - "Send Reminder" - Enabled only when `can_send_reminder: true`
   - "Resend Email" - Enabled only when `email_status: "failed"`
   - "View Document" - Enabled when `status: "Uploaded"`
4. **Filters/Search** - Filter by status, email status, reminder count
5. **Bulk Actions** - Send reminders to all eligible employees

### API Integration Example
```javascript
// Fetch dashboard data
const response = await fetch('/policies/signed-documents-dashboard/', {
    headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Send reminder
const sendReminder = async (empId) => {
    const response = await fetch(`/policies/send-reminder/${empId}/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const result = await response.json();
    // Show success toast, refresh dashboard
};

// Resend email
const resendEmail = async (empId) => {
    const response = await fetch(`/policies/resend-email/${empId}/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const result = await response.json();
    // Show success toast, refresh dashboard
};
```

---

## Key Features

### 1. Smart Reminder System
- **Eligibility Check**: Only allows reminders for employees who:
  - Acknowledged all assigned policies
  - Haven't uploaded document yet
- **Duplicate Prevention**: Cannot send reminder to employees who already uploaded
- **Audit Trail**: Tracks who sent reminder and when

### 2. Email Failure Recovery
- **Status Tracking**: Marks emails as `sent`, `failed`, or `not_uploaded`
- **Retry Mechanism**: HR can manually retry failed emails
- **File Validation**: Checks if document physically exists before resending

### 3. Enhanced Monitoring
- **Dashboard Metrics**:
  - Total employees
  - Uploaded count
  - Pending count
  - Ready for reminder (acknowledged but not uploaded)
  - Pending not acknowledged (still reviewing policies)
  - Email failed count
  - Total reminders sent (cumulative)
- **Per-Employee Details**:
  - Reminder count
  - Last reminder timestamp
  - Who sent the last reminder
  - Can send reminder flag
  - Email status with color coding

---

## Answer to User's Question

**Q: How will we keep track when admin/hr tries to notify the employee?**

**A: Tracking is automatic through 3 mechanisms:**

1. **Database Tracking** (`ci_policy_signed_documents` table):
   - `reminder_sent_count` - How many reminders sent
   - `last_reminder_sent_at` - When was last reminder sent
   - `last_reminded_by` - Which HR user sent it

2. **Notification System** (`ci_notification` table):
   - Every reminder creates a notification record
   - Visible in employee's notification list
   - Historical record of all reminders

3. **Dashboard Display**:
   - Shows "Last Reminder: 2025-01-10 15:30:45 by HR Manager"
   - Summary shows "Total Reminders Sent: 47" across all employees
   - Per-employee shows "Reminders Sent: 3"

**For Manual Emails Outside System:**
If HR sends email from Outlook/Gmail manually:
- Recommended: Still click "Send Reminder" button to track it
- Alternative: Add manual notes field (future enhancement)

---

## Testing Scenarios

### Scenario 1: Happy Path
1. Employee acknowledges all policies
2. HR sees employee in "Ready for Reminder" (25 employees)
3. HR clicks "Send Reminder" for EMP002
4. Employee receives notification
5. Employee uploads document
6. Dashboard shows status changed to "Uploaded"
7. HR receives email with attachment

### Scenario 2: Email Failure Recovery
1. Employee uploads document
2. Email fails due to SMTP error
3. Dashboard shows "Email Failed" badge
4. HR clicks "Resend Email"
5. Email sends successfully
6. Status changes to "Sent"

### Scenario 3: Multiple Reminders
1. HR sends reminder on Day 1
2. Employee doesn't respond
3. HR sends reminder on Day 7 (count becomes 2)
4. Employee doesn't respond
5. HR sends reminder on Day 14 (count becomes 3)
6. Dashboard shows "3 reminders sent, last on 2025-01-14"

---

## Migration from Phase 1

If you were using `GET /policies/all-signed-documents/`, migrate to:
- **New Endpoint**: `GET /policies/signed-documents-dashboard/`
- **Benefits**: More data, better statistics, actionable insights
- **Backward Compatibility**: Old endpoint still works

**Changes in Response:**
- ✅ All old fields still present
- ✅ New fields added: `reminder_sent_count`, `last_reminder_sent_at`, `last_reminded_by_name`, `can_send_reminder`
- ✅ Enhanced summary with more metrics

---

## Deployment Checklist

- [ ] Run ALTER TABLE SQL in MySQL Workbench
- [ ] Verify 3 new columns exist in `ci_policy_signed_documents`
- [ ] Test `/policies/signed-documents-dashboard/` endpoint
- [ ] Test sending reminder to eligible employee
- [ ] Verify notification appears in `/notifications/global/{emp_id}/`
- [ ] Test resend email for failed status
- [ ] Update frontend to use enhanced dashboard
- [ ] Add "Send Reminder" button to UI
- [ ] Add "Resend Email" button to UI
- [ ] Deploy to production

---

## Support

For questions or issues:
1. Check `POLICY_REMINDER_MONITORING_API.md` for detailed API documentation
2. Review error responses in documentation
3. Check Django logs for SMTP errors if email fails
4. Verify SMTP settings in `settings.py` for email functionality

---

## Future Enhancements (Optional)

1. **Scheduled Reminders**
   - Auto-send reminder after 7 days of no upload
   - Configure in settings (e.g., reminder_interval_days)

2. **Reminder Templates**
   - Allow HR to customize notification text
   - Store templates in database

3. **Email Templates**
   - Customizable email body for resend
   - HTML email support

4. **Reminder History**
   - Separate table for reminder audit trail
   - Track each reminder individually (not just count)

5. **Bulk Actions API**
   - Single endpoint to send reminders to multiple employees
   - Returns success/failure for each employee

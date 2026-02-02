# 🚀 Quick Reference - Policy Signed Documents APIs

## Database Setup (Run First!)

```sql
-- Step 1: Create table
CREATE TABLE ci_policy_signed_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    signed_document VARCHAR(255) NOT NULL,
    uploaded_at DATETIME DEFAULT NULL,
    email_sent_at DATETIME DEFAULT NULL,
    email_status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_emp_id (emp_id),
    INDEX idx_email_status (email_status)
);

-- Step 2: Add reminder tracking
ALTER TABLE ci_policy_signed_documents
ADD COLUMN reminder_sent_count INT DEFAULT 0,
ADD COLUMN last_reminder_sent_at DATETIME DEFAULT NULL,
ADD COLUMN last_reminded_by INT DEFAULT NULL,
ADD INDEX idx_reminder_count (reminder_sent_count),
ADD INDEX idx_last_reminder (last_reminder_sent_at);

-- Step 3: Update enum
ALTER TABLE ci_policy_signed_documents
MODIFY COLUMN email_status ENUM('pending', 'sent', 'failed', 'not_uploaded') DEFAULT 'pending';
```

---

## 8 New API Endpoints

### Employee APIs (3)

**1. Download Template**
```http
GET /policies/download-acknowledgement-template/{emp_id}/
Headers: Authorization: Bearer <token>
Response: PDF file (ebook.pdf)
```

**2. Upload Signed Document**
```http
POST /policies/upload-signed-document/{emp_id}/
Headers: Authorization: Bearer <token>
Body: multipart/form-data
  - signed_document: File (PDF/JPG/JPEG/PNG/DOCX, max 10MB)

Response:
{
    "message": "Document uploaded successfully and email sent to HR",
    "document_path": "signed_acknowledgements/EMP001_signed_20250110_143022.pdf",
    "uploaded_at": "2025-01-10 14:30:22",
    "email_sent_at": "2025-01-10 14:30:25",
    "email_status": "sent"
}
```

**3. Check Upload Status**
```http
GET /policies/signed-document-status/{emp_id}/
Headers: Authorization: Bearer <token>

Response:
{
    "employee_id": "EMP001",
    "uploaded": true,
    "document_path": "signed_acknowledgements/EMP001_signed_20250110_143022.pdf",
    "uploaded_at": "2025-01-10 14:30:22",
    "email_status": "sent",
    "email_sent_at": "2025-01-10 14:30:25"
}
```

---

### HR/Admin APIs (5)

**4. Enhanced Dashboard** ⭐ RECOMMENDED
```http
GET /policies/signed-documents-dashboard/
Headers: Authorization: Bearer <hr_token>

Response:
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
            "status": "Uploaded",
            "email_status": "sent",
            "reminder_sent_count": 0,
            "last_reminder_sent_at": null,
            "can_send_reminder": false,
            ...
        }
    ]
}
```

**5. Send Reminder**
```http
POST /policies/send-reminder/{emp_id}/
Headers: Authorization: Bearer <hr_token>
Body: {
    "user_id": 123  // HR/Admin user ID (required)
}

Response:
{
    "message": "Reminder sent successfully to employee",
    "employee_name": "Jane Smith",
    "reminder_sent_at": "2025-01-10 15:30:45",
    "total_reminders_sent": 3,
    "notification_sent": true
}

Note: Creates notification in ci_notification table
      Visible in GET /notifications/global/{emp_id}/
```

**6. Resend Failed Email**
```http
POST /policies/resend-email/{emp_id}/
Headers: Authorization: Bearer <hr_token>

Response:
{
    "message": "Email resent successfully to HR",
    "hr_email": "hr@thedatatechlabs.com",
    "email_sent_at": "2025-01-10 16:45:30",
    "previous_status": "failed"
}
```

**7. View Employee Document**
```http
GET /policies/view-signed-document/{emp_id}/
Headers: Authorization: Bearer <hr_token>
Response: PDF file download
```

**8. Basic Dashboard** (Use Enhanced Dashboard instead)
```http
GET /policies/all-signed-documents/
Headers: Authorization: Bearer <hr_token>

Response: Similar to enhanced dashboard but without reminder stats
```

---

## 1 Updated API

**Get Assigned Policies** (now includes signed_document object)
```http
GET /policies/assigned/{emp_id}/
Headers: Authorization: Bearer <token>

Response:
{
    "message": "Policies retrieved successfully",
    "data": [...policies...],
    "signed_document": {  // NEW
        "uploaded": true,
        "document_path": "signed_acknowledgements/EMP001_signed_20250110_143022.pdf",
        "uploaded_at": "2025-01-10 14:30:22",
        "email_status": "sent",
        "email_sent_at": "2025-01-10 14:30:25"
    }
}
```

---

## Frontend Quick Start

### Employee Panel
```javascript
// Download template
const downloadTemplate = async (empId) => {
    const response = await fetch(`/policies/download-acknowledgement-template/${empId}/`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const blob = await response.blob();
    saveAs(blob, 'acknowledgement_template.pdf');
};

// Upload signed document
const uploadDocument = async (empId, file) => {
    const formData = new FormData();
    formData.append('signed_document', file);
    
    const response = await fetch(`/policies/upload-signed-document/${empId}/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
    });
    
    const result = await response.json();
    if (response.ok) {
        toast.success('Document uploaded and emailed to HR!');
    } else {
        toast.error(result.error);
    }
};
```

### HR Dashboard
```javascript
// Fetch dashboard
const fetchDashboard = async () => {
    const response = await fetch('/policies/signed-documents-dashboard/', {
        headers: { 'Authorization': `Bearer ${hrToken}` }
    });
    return await response.json();
};

// Send reminder
const sendReminder = async (empId) => {
    const response = await fetch(`/policies/send-reminder/${empId}/`, {
        method: 'POST',
        headers: { 
            'Authorization': `Bearer ${hrToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: currentUserId  // Get from logged-in HR user
        })
    });
    
    const result = await response.json();
    if (response.ok) {
        toast.success(`Reminder sent! Total: ${result.total_reminders_sent}`);
        refreshDashboard();
    }
};

// Resend failed email
const resendEmail = async (empId) => {
    const response = await fetch(`/policies/resend-email/${empId}/`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${hrToken}` }
    });
    
    const result = await response.json();
    if (response.ok) {
        toast.success('Email resent successfully!');
        refreshDashboard();
    }
};
```

---

## File Setup

```bash
# Place template file
cp ebook.pdf /path/to/media/

# Create upload directory
mkdir -p /path/to/media/signed_acknowledgements/

# Set permissions
chmod 755 /path/to/media/signed_acknowledgements/
```

---

## Status Values Reference

### email_status
- `not_uploaded` - No document uploaded yet
- `pending` - Document uploaded, email queued (rarely used)
- `sent` - Email successfully sent to HR
- `failed` - Email sending failed (SMTP error)

### status
- `Pending` - Document not uploaded
- `Uploaded` - Document uploaded

---

## Testing Checklist

**Employee Flow:**
- [ ] Can download template
- [ ] Can upload signed document
- [ ] Receives success message
- [ ] Can check upload status
- [ ] Sees notification when HR sends reminder

**HR Flow:**
- [ ] Can view enhanced dashboard
- [ ] Sees correct summary statistics
- [ ] Send reminder button enabled only for eligible employees
- [ ] Reminder creates notification for employee
- [ ] Reminder count increments correctly
- [ ] Can resend failed emails
- [ ] Can download employee documents
- [ ] Dashboard refreshes after actions

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Template not found | Place `ebook.pdf` in `media/` folder |
| Upload fails | Check file type (PDF/JPG/JPEG/PNG/DOCX) and size (max 10MB) |
| Email not sent | Verify SMTP settings in `settings.py` |
| Reminder disabled | Employee must acknowledge ALL policies first |
| Resend fails | Document must be uploaded and file must exist on server |
| Notification missing | Check `ci_notification` table, verify `send_to_id` is correct |

---

## Documentation Files

| File | Purpose |
|------|---------|
| `POLICY_SIGNED_DOCUMENT_API_DOCUMENTATION.md` | Phase 1 complete reference |
| `POLICY_REMINDER_MONITORING_API.md` | Phase 2 complete reference |
| `PHASE_2_IMPLEMENTATION_SUMMARY.md` | Quick setup guide |
| `COMPLETE_API_LIST.md` | All 19 policy APIs |
| `IMPLEMENTATION_COMPLETE.md` | Full implementation summary |
| `QUICK_REFERENCE.md` | This file |

---

## URL Patterns

```python
# Phase 1 (Signed Documents)
path('policies/download-acknowledgement-template/<str:emp_id>/', ...),
path('policies/upload-signed-document/<str:emp_id>/', ...),
path('policies/signed-document-status/<str:emp_id>/', ...),
path('policies/view-signed-document/<str:emp_id>/', ...),
path('policies/all-signed-documents/', ...),

# Phase 2 (Reminders)
path('policies/send-reminder/<str:emp_id>/', ...),
path('policies/resend-email/<str:emp_id>/', ...),
path('policies/signed-documents-dashboard/', ...),
```

---

**All systems ready!** Execute database SQL and start testing.

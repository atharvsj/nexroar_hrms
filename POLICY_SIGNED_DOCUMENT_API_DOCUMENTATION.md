# Policy Signed Acknowledgement Document - API Documentation

## Overview
This document contains all API endpoints related to the Policy Signed Acknowledgement Document feature where employees can download a template, sign it, and upload it back to the system which then emails it to HR.

---

## Database Table Required

Please create this table in MySQL Workbench before using these APIs:

```sql
CREATE TABLE ci_policy_signed_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(50) NOT NULL,
    signed_document VARCHAR(255) NOT NULL,
    uploaded_at DATETIME NOT NULL,
    email_sent_at DATETIME DEFAULT NULL,
    email_status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_emp_id (emp_id),
    INDEX idx_email_status (email_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## Prerequisites

1. Place the template file `ebook.pdf` in the `media/` folder
2. Create the database table above
3. Ensure email settings are configured in `settings.py`

---

## API Endpoints

### 1. **Download Policy Acknowledgement Template**

Download the policy acknowledgement template (ebook.pdf) for employees to sign offline.

**Endpoint:** `GET /policies/download-acknowledgement-template/{emp_id}/`

**Authentication:** Required (JWT Token)

**Request:**
```http
GET /policies/download-acknowledgement-template/EMP001/
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="Policy_Acknowledgement_Template.pdf"

[PDF File Binary Data]
```

**Error Responses:**

404 - Employee Not Found:
```json
{
    "error": "Employee not found"
}
```

404 - Template Not Found:
```json
{
    "error": "Template file not found"
}
```

500 - Server Error:
```json
{
    "error": "Failed to download template: <error_message>"
}
```

---

### 2. **Upload Signed Policy Document**

Upload the signed policy acknowledgement document. Automatically sends email to HR with the document attached.

**Endpoint:** `POST /policies/upload-signed-document/{emp_id}/`

**Authentication:** Required (JWT Token)

**Content-Type:** `multipart/form-data`

**Request:**
```http
POST /policies/upload-signed-document/EMP001/
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

Form Data:
- signed_document: [File] (PDF, JPG, JPEG, PNG, or DOCX, Max 10MB)
```

**Example using cURL:**
```bash
curl -X POST \
  'http://localhost:8000/policies/upload-signed-document/EMP001/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -F 'signed_document=@/path/to/signed_document.pdf'
```

**Success Response (201 Created):**
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

**Success Response (201 Created) - Email Failed:**
```json
{
    "message": "Document uploaded but failed to send email to HR",
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "file_path": "signed_acknowledgements/EMP001_policy_acknowledgement_20260131_143025.pdf",
    "uploaded_at": "2026-01-31 14:30:25",
    "email_sent": false,
    "email_error": "SMTP connection failed"
}
```

**Error Responses:**

400 - No File Uploaded:
```json
{
    "error": "No file uploaded. Please upload a signed document."
}
```

400 - File Too Large:
```json
{
    "error": "File size exceeds maximum limit of 10.0MB"
}
```

400 - Invalid File Type:
```json
{
    "error": "Invalid file type. Allowed types: .pdf, .jpg, .jpeg, .png, .docx"
}
```

400 - Policies Not Acknowledged:
```json
{
    "error": "Please acknowledge all assigned policies before uploading the signed document",
    "acknowledged": 2,
    "total_policies": 5
}
```

404 - Employee Not Found:
```json
{
    "error": "Employee not found"
}
```

500 - Server Error:
```json
{
    "error": "Failed to upload document: <error_message>"
}
```

---

### 3. **Check Signed Document Status**

Check if an employee has uploaded their signed policy document.

**Endpoint:** `GET /policies/signed-document-status/{emp_id}/`

**Authentication:** Required (JWT Token)

**Request:**
```http
GET /policies/signed-document-status/EMP001/
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK) - Document Uploaded:**
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

**Success Response (200 OK) - Document Not Uploaded:**
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

**Error Responses:**

404 - Employee Not Found:
```json
{
    "error": "Employee not found"
}
```

500 - Server Error:
```json
{
    "error": "Failed to check status: <error_message>"
}
```

---

### 4. **View/Download Signed Document (HR/Admin)**

Download an employee's signed policy document. Typically used by HR/Admin.

**Endpoint:** `GET /policies/view-signed-document/{emp_id}/`

**Authentication:** Required (JWT Token)

**Request:**
```http
GET /policies/view-signed-document/EMP001/
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK):**
```
Content-Type: application/pdf (or image/jpeg, etc.)
Content-Disposition: attachment; filename="EMP001_John_Doe_signed_policy.pdf"

[File Binary Data]
```

**Error Responses:**

404 - Employee Not Found:
```json
{
    "error": "Employee not found"
}
```

404 - No Document:
```json
{
    "error": "No signed document found for this employee"
}
```

404 - File Not Found:
```json
{
    "error": "Signed document file not found on server"
}
```

500 - Server Error:
```json
{
    "error": "Failed to retrieve document: <error_message>"
}
```

---

### 5. **Get All Signed Documents (HR/Admin Dashboard)**

Get a list of all employees with their signed document upload status.

**Endpoint:** `GET /policies/all-signed-documents/`

**Authentication:** Required (JWT Token)

**Request:**
```http
GET /policies/all-signed-documents/
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK):**
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

**Error Response:**

500 - Server Error:
```json
{
    "error": "Failed to retrieve documents list: <error_message>"
}
```

---

## UPDATED API: Get Assigned Policies (Modified)

**Endpoint:** `GET /policies/assigned/{emp_id}/`

This existing API has been **updated** to include signed document status.

**Request:**
```http
GET /policies/assigned/EMP001/
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK) - Updated Response Format:**
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
            "policy_name": "Data Privacy Policy",
            "attachment_text": "policies/data_privacy.pdf",
            "acknowledged": false
        }
    ]
}
```

**New Fields Added:**
- `all_acknowledged`: Boolean - true if all policies are acknowledged
- `total_policies`: Integer - total number of assigned policies
- `acknowledged_count`: Integer - number of acknowledged policies
- `signed_document`: Object containing:
  - `has_uploaded`: Boolean
  - `document_path`: String or null
  - `uploaded_at`: DateTime string or null
  - `email_status`: String ("sent", "pending", "failed", "not_uploaded")

---

## Complete User Flow

### Employee Flow:

1. **View Assigned Policies**
   ```
   GET /policies/assigned/EMP001/
   ```

2. **Acknowledge Each Policy**
   ```
   POST /policies/acknowledge/EMP001/
   Body: { "policy_id": 1 }
   ```

3. **Check Status (after acknowledging all policies)**
   ```
   GET /policies/assigned/EMP001/
   Response will show all_acknowledged: true
   ```

4. **Download Template**
   ```
   GET /policies/download-acknowledgement-template/EMP001/
   ```

5. **Sign Document Offline** (Employee signs the downloaded PDF)

6. **Upload Signed Document**
   ```
   POST /policies/upload-signed-document/EMP001/
   FormData: signed_document=[file]
   ```

7. **Check Upload Status**
   ```
   GET /policies/signed-document-status/EMP001/
   ```

### HR/Admin Flow:

1. **View All Employees' Status**
   ```
   GET /policies/all-signed-documents/
   ```

2. **Download Specific Employee's Document**
   ```
   GET /policies/view-signed-document/EMP001/
   ```

3. **Receive Email** (Automatically sent when employee uploads document)

---

## Email Details

When an employee uploads a signed document, an email is automatically sent to:
- **To:** HR Admin email (from database or default: hr@thedatatechlabs.com)
- **CC:** Employee's email
- **Subject:** "Policy Acknowledgement - Signed Document from [Employee Name]"
- **Attachment:** The signed document PDF/image

**Email Body Template:**
```
Dear HR Team,

Employee [Name] (ID: [emp_id]) has uploaded their signed policy acknowledgement document.

Employee Details:
- Name: [Full Name]
- Employee ID: [emp_id]
- Email: [email]
- Upload Date: [timestamp]
- Policies Acknowledged: [count]

Please find the signed document attached.

Best Regards,
HRMS System
```

---

## File Storage Structure

```
media/
├── ebook.pdf                          (Template file - must exist)
└── signed_acknowledgements/           (Auto-created)
    ├── EMP001_policy_acknowledgement_20260131_143025.pdf
    ├── EMP002_policy_acknowledgement_20260131_150530.pdf
    └── ...
```

**File Naming Convention:**
```
{emp_id}_policy_acknowledgement_{timestamp}.{extension}
```

**Example:**
```
EMP001_policy_acknowledgement_20260131_143025.pdf
```

---

## Validation Rules

1. **File Upload:**
   - Max size: 10MB
   - Allowed formats: PDF, JPG, JPEG, PNG, DOCX
   - Employee must acknowledge ALL policies first

2. **Download Template:**
   - Employee must exist in system
   - Template file (ebook.pdf) must exist in media folder

3. **Email:**
   - Sends automatically on successful upload
   - Retries not implemented (status marked as 'failed' if email fails)
   - Document still saved even if email fails

---

## Error Handling

All APIs return appropriate HTTP status codes:
- `200 OK` - Successful GET request
- `201 Created` - Successful upload
- `400 Bad Request` - Invalid input or validation failure
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

---

## Frontend Implementation Notes

### For Employee Portal:

1. **Show Download Button** only when `all_acknowledged: true` in GET /policies/assigned/{emp_id}/

2. **Upload Form:**
   ```html
   <form enctype="multipart/form-data">
     <input type="file" name="signed_document" accept=".pdf,.jpg,.jpeg,.png,.docx" />
     <button>Upload</button>
   </form>
   ```

3. **Show Upload Status** using badge/icon based on `signed_document.email_status`

4. **Disable Upload** if not all policies acknowledged

### For HR Dashboard:

1. **Show Summary Stats** from `/policies/all-signed-documents/`

2. **Table with filters:**
   - Uploaded / Pending
   - Sort by upload date
   - Search by employee name/ID

3. **Download Button** for each employee linking to `/policies/view-signed-document/{emp_id}/`

4. **Email Status Icons:**
   - ✅ sent
   - ⏳ pending
   - ❌ failed
   - ⚪ not_uploaded

---

## Testing Checklist

- [ ] Template download works for valid employee
- [ ] Upload validates file type and size
- [ ] Upload rejects if policies not acknowledged
- [ ] Email is sent to HR with attachment
- [ ] Multiple uploads replace previous document
- [ ] Status API shows correct upload state
- [ ] HR can download employee documents
- [ ] Dashboard shows all employees correctly
- [ ] Error handling works for invalid inputs

---

## Security Considerations

✅ All endpoints require JWT authentication
✅ Employee ID validation before any operation
✅ File type and size validation
✅ Files stored outside web root with relative paths
✅ Unique filename generation prevents overwrites
✅ Email sent securely via SMTP with TLS

---

## Postman Collection

Import this into Postman for testing:

```json
{
    "info": {
        "name": "Policy Signed Documents API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Download Template",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/policies/download-acknowledgement-template/EMP001/",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ]
            }
        },
        {
            "name": "Upload Signed Document",
            "request": {
                "method": "POST",
                "url": "{{base_url}}/policies/upload-signed-document/EMP001/",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ],
                "body": {
                    "mode": "formdata",
                    "formdata": [
                        {
                            "key": "signed_document",
                            "type": "file",
                            "src": "/path/to/file.pdf"
                        }
                    ]
                }
            }
        },
        {
            "name": "Check Status",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/policies/signed-document-status/EMP001/",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ]
            }
        },
        {
            "name": "View Signed Document",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/policies/view-signed-document/EMP001/",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ]
            }
        },
        {
            "name": "All Signed Documents",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/policies/all-signed-documents/",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ]
            }
        },
        {
            "name": "Get Assigned Policies (Updated)",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/policies/assigned/EMP001/",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ]
            }
        }
    ]
}
```

---

## Support

For any issues or questions, contact the backend development team.

**Last Updated:** January 31, 2026

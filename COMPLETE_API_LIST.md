# Complete API List - Policy Management with Signed Documents

## 📋 All Policy-Related APIs (Updated + New)

---

## EXISTING APIs (No Changes)

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

2. **Employee Table:**
   - Filter: All / Uploaded / Pending
   - Sort: By date, name, status
   - Actions: Download button for uploaded documents

3. **Email Status Icons:**
   - ✅ Sent
   - ⏳ Pending
   - ❌ Failed
   - ⚪ Not Uploaded

---

## ⚠️ Important Notes

1. **File Size Limit:** 10MB maximum
2. **Allowed File Types:** PDF, JPG, JPEG, PNG, DOCX
3. **Template File:** Must place `ebook.pdf` in `media/` folder
4. **Database Table:** Must create `ci_policy_signed_documents` table
5. **Email:** Sends automatically; if fails, document still saved
6. **Re-upload:** Replaces previous document; no version history

---

## 🧪 Quick Test

```bash
# Test complete flow
curl -X GET "http://localhost:8000/policies/assigned/EMP001/" \
  -H "Authorization: Bearer <token>"

curl -X GET "http://localhost:8000/policies/download-acknowledgement-template/EMP001/" \
  -H "Authorization: Bearer <token>" \
  -o template.pdf

curl -X POST "http://localhost:8000/policies/upload-signed-document/EMP001/" \
  -H "Authorization: Bearer <token>" \
  -F "signed_document=@signed_template.pdf"

curl -X GET "http://localhost:8000/policies/all-signed-documents/" \
  -H "Authorization: Bearer <token>"
```

---

**Last Updated:** January 31, 2026
**Version:** 1.0

# 🔄 API Update Notice - user_id Required in Request

## Change Summary

The `SendPolicyReminderView` API has been updated to work with your project's authentication pattern.

### What Changed

**Before:**
```python
hr_user_id = request.user.id  # ❌ Doesn't work in this project
```

**After:**
```python
hr_user_id = request.data.get('user_id')  # ✅ Works correctly
```

---

## Updated API Endpoint

### Send Reminder to Employee
**Endpoint:** `POST /policies/send-reminder/{emp_id}/`

**Request (UPDATED):**
```http
POST /policies/send-reminder/EMP002/ HTTP/1.1
Host: your-domain.com
Authorization: Bearer <token>
Content-Type: application/json

{
    "user_id": 123
}
```

**Required Fields:**
- `user_id` (integer, required): The user ID of the HR/Admin sending the reminder

**Success Response:**
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

**New Error Response:**
```json
{
    "error": "user_id is required in request body"
}
```

---

## Frontend Update Required

### Before:
```javascript
const sendReminder = async (empId) => {
    const response = await fetch(`/policies/send-reminder/${empId}/`, {
        method: 'POST',
        headers: { 
            'Authorization': `Bearer ${token}`
        }
    });
};
```

### After (UPDATED):
```javascript
const sendReminder = async (empId, userId) => {
    const response = await fetch(`/policies/send-reminder/${empId}/`, {
        method: 'POST',
        headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId  // Pass logged-in HR user ID
        })
    });
    
    const result = await response.json();
    if (response.ok) {
        toast.success(`Reminder sent! Total: ${result.total_reminders_sent}`);
    } else {
        toast.error(result.error);
    }
};

// Usage
const currentUserId = 123; // Get from logged-in user context
sendReminder('EMP002', currentUserId);
```

---

## React Component Example

```jsx
const PolicyDashboard = () => {
    const [currentUserId, setCurrentUserId] = useState(null);
    
    useEffect(() => {
        // Get current user ID from your auth context/state
        const userId = getUserIdFromContext(); // Your method
        setCurrentUserId(userId);
    }, []);
    
    const sendReminder = async (empId) => {
        if (!currentUserId) {
            toast.error('User not authenticated');
            return;
        }
        
        try {
            const response = await fetch(`/policies/send-reminder/${empId}/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: currentUserId
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                toast.success(`Reminder sent to ${result.employee_name}`);
                refreshDashboard();
            } else {
                toast.error(result.error);
            }
        } catch (error) {
            toast.error('Failed to send reminder');
        }
    };
    
    return (
        <div>
            {data?.data.map(emp => (
                <tr key={emp.employee_id}>
                    {/* ... other cells ... */}
                    <td>
                        {emp.can_send_reminder && (
                            <button onClick={() => sendReminder(emp.employee_id)}>
                                Send Reminder
                            </button>
                        )}
                    </td>
                </tr>
            ))}
        </div>
    );
};
```

---

## Testing

### cURL Test:
```bash
curl -X POST "http://localhost:8000/policies/send-reminder/EMP002/" \
  -H "Authorization: Bearer <hr_token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123}'
```

### Postman Test:
```
Method: POST
URL: http://localhost:8000/policies/send-reminder/EMP002/
Headers:
  - Authorization: Bearer <token>
  - Content-Type: application/json
Body (raw JSON):
{
    "user_id": 123
}
```

---

## Other APIs (No Changes)

All other APIs remain unchanged:
- ✅ Enhanced Dashboard - `GET /policies/signed-documents-dashboard/`
- ✅ Resend Email - `POST /policies/resend-email/{emp_id}/`
- ✅ Upload Document - `POST /policies/upload-signed-document/{emp_id}/`
- ✅ Download Template - `GET /policies/download-acknowledgement-template/{emp_id}/`
- ✅ All other endpoints

---

## Documentation Updates

All documentation files have been updated to reflect this change:
- ✅ [POLICY_REMINDER_MONITORING_API.md](POLICY_REMINDER_MONITORING_API.md)
- ✅ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- ✅ [COMPLETE_API_LIST.md](COMPLETE_API_LIST.md)
- ✅ [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

---

## Summary

**What to do:**
1. Pass `user_id` in request body when calling `POST /policies/send-reminder/{emp_id}/`
2. Get `user_id` from your logged-in HR/Admin user context
3. Update frontend code to include `user_id` in the request body

**What NOT to do:**
- ❌ Don't rely on `request.user.id` (doesn't work in this project)
- ❌ Don't forget `Content-Type: application/json` header
- ❌ Don't forget to validate user_id exists before sending request

---

**Date:** February 2, 2026  
**Status:** ✅ Updated and ready to use

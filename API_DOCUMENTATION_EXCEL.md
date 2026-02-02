# HRMS API Documentation - Excel Format

> **Complete API Reference for Frontend Development**  
> Last Updated: January 31, 2026

---

## App Module APIs (Base URL: `/`)

| Name | API URL | Method | Request Payload | Response |
|------|---------|--------|-----------------|----------|
| User Login | /login/ | POST | {"username": "string", "password": "string"} | {"refresh": "JWT token", "access": "JWT token", "user_id": 1, "employee_id": "EMP001", "role": "Admin", "role_id": 1, "is_hod": true, "email": "user@example.com", "designation_id": 1, "designation_name": "Manager", "role_resources": "permissions"} |
| User Registration | /register/ | POST | {"username": "string", "email": "string", "password": "string"} | {"message": "User registered successfully", "user": {"username": "string", "email": "string"}} |
| Change Password | /change-password/ | PATCH | {"old_password": "string", "new_password": "string"} | {"Message": "Success"} |
| Forgot Password | /forgot-password/ | POST | {"email": "string"} | {"message": "Password reset link sent to your email"} |
| Reset Password Confirm | /reset-password-confirm/ | POST | {"token": "string", "new_password": "string"} | {"message": "Password reset successful"} |
| Get/Update Basic Info | /basic-info/ | GET, PATCH | PATCH: {"first_name": "string", "middle_name": "string", "last_name": "string", "contact_number": "string", "gender": "string", "date_of_birth": "YYYY-MM-DD", "marital_status": "string", "state": "string", "city": "string", "zipcode": "string", "religion_id": 1, "blood_group": "string", "country": "string", "citizenship_id": 1, "address_1": "string", "address_2": "string"} | GET: {"status": "Success", "BasicInfo": {"id": 1, "username": "string", "first_name": "string", "last_name": "string", "email": "string"}} |
| Get Employee Details | /api/employee/<int:user_id>/ | GET | None | {"user_id": 1, "employee_id": "EMP001", "first_name": "John", "last_name": "Doe", "email": "john.doe@example.com", "designation": "Software Engineer", "department": "IT"} |
| Family Members CRUD | /api/family-members-user/<int:user_id>/ | GET, POST | POST: {"user_id": 1, "family_member_name": "string", "relationship": "string", "contact_number": "string"} | {"message": "Family member added successfully"} |
| Family Members Detail | /api/family-members/<int:family_member_id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Family member updated/deleted successfully"} |
| Get Employee Shift | /api/employee/shift/<int:user_id>/ | GET | None | {"shift_id": 1, "shift_name": "Day Shift", "start_time": "09:00:00", "end_time": "18:00:00"} |
| Today's Attendance | /today-attendence/ | GET | None | {"data": [{"user_id": 1, "emp_name": "John Doe", "attendance_date": "2026-01-31", "attendance_status": "Present", "punch_in_time": "09:00:00"}]} |
| Today's Attendance Report | /attendance/today/ | GET | None | {"date": "2026-01-31", "total_records": 50, "data": [{"employee": "John Doe", "email": "john@example.com", "emp_id": 1, "date": "2026-01-31", "status": "Present", "clock_in": "09:00:00", "clock_out": "18:00:00", "late": "No", "early_leaving": "No", "total_work": "09:00:00"}]} |
| Attendance By Date Report | /attendance/by-date/ | POST | {"emp_id": 1, "date": "2026-01-31", "status": "Present"} | {"date": "2026-01-31", "total_records": 10, "data": []} |
| My Attendance | /my_attendance/<str:empid>/ | GET | None | {"attendance_records": []} |
| Monthly Report | /emp_monthly_report/ | GET | None | Attendance data |
| Punch Report | /punch_reports/ | GET, POST | POST: Punch data fields | Punch report data |
| Leave Applications List | /api/leave-applications/ | GET, POST | POST: {"employee_id": "EMP001", "leave_type_id": 1, "from_date": "2026-02-01", "to_date": "2026-02-03", "reason": "Personal work", "is_half_day": false} | {"message": "Leave application submitted successfully"} |
| Leave Application Detail | /api/leave-applications/<int:leave_id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Leave updated/deleted"} |
| Leave Types List | /api/leave-types/ | GET | None | [{"constants_id": 1, "category_name": "Casual Leave"}, {"constants_id": 2, "category_name": "Sick Leave"}] |
| Leave Setup | /api/leave-setup/ | GET, POST | POST: {"category_name": "string", "field_one": 12, "field_two": "setup rules"} | {"message": "Leave type added successfully"} |
| Leave Setup Detail | /api/leave-setup/<int:id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Leave setup updated/deleted"} |
| Leave Applications Dashboard | /api/leave-applications-dashboard/ | GET | None | {"upcoming_holiday": {"event_name": "Republic Day", "start_date": "2026-01-26", "end_date": "2026-01-26", "country": "India", "state": "Maharashtra", "employee_hub": "Mumbai", "status": "Published"}, "leave_type_wise_leaves": [], "department_wise_leaves": []} |
| Leave Pending Current Month | /api/leave-pending-current-month/ | GET | None | [{"employee_name": "John Doe", "date": "2026-02-01 to 2026-02-03", "number_of_days": 3, "reason": "Personal work", "status": "Pending"}] |
| Department Leave Report | /department_leave_report/ | GET | None | Department-wise leave data |
| CompOff List/Create | /compoff/ | GET, POST | POST: {"employee_name": "John Doe", "start_date_compoff": "2026-01-25", "end_date_compoff": "2026-01-25", "compoff_reason": "Worked on holiday"} | GET: [{"compoff_id": 1, "emp_id": "EMP001", "employee_name": "John Doe", "start_date_compoff": "2026-01-25", "end_date_compoff": "2026-01-25", "no_of_days": 1, "compoff_reason": "Worked on holiday", "compoff_status": "Pending", "created_at": "2026-01-26 10:00:00", "is_expired": "2026-04-25"}] |
| CompOff Detail | /compoff/<int:compoff_id>/ | PATCH, DELETE | PATCH: {"compoff_status": "A"} | {"message": "CompOff record updated/deleted successfully"} |
| On Duty Request | /on-duty-request/ | POST | OD request fields | {"message": "OD Created"} |
| Departments List | /departments/ | GET, POST | POST: {"department_name": "Human Resources", "department_code": "HR", "department_head": "EMP001", "company_id": 2, "added_by": 1} | GET: [{"department_id": 1, "department_name": "Human Resources", "department_code": "HR", "company_id": 2, "department_head": "EMP001", "department_head_name": "John Doe", "added_by": 1, "created_at": "2026-01-01 10:00:00"}] |
| Department Detail | /departments/<int:pk>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Department updated/deleted"} |
| Designations List | /ci_designations/ | GET, POST | POST: {"department_id": 1, "designation_name": "Software Engineer", "designation_code": "SE", "line_manager_id": 2, "description": "Engineering role", "company_id": 2} | GET: [{"designation_id": 1, "company_id": 2, "designation_name": "Software Engineer", "designation_code": "SE", "line_manager_id": 2, "line_manager_name": "Senior Engineer", "description": "Engineering role", "created_at": "2026-01-01", "department_id": 1, "department_name": "IT"}] |
| Designation Detail | /ci_designations/<int:pk>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Designation updated/deleted"} |
| Divisions List | /api/division/ | GET, POST | POST: {"division_name": "North Region", "division_code": "NR"} | GET: [{"division_id": 1, "division_name": "North Region", "division_code": "NR", "created_at": "2026-01-01"}] |
| Division Detail | /api/division/<int:division_id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Division updated/deleted"} |
| Grades List | /api/grade/ | GET, POST | POST: {"grade_id": "G1", "grade_name": "Grade 1", "grade_code": "G1"} | GET: [{"grade_id": 1, "grade_name": "Grade 1", "grade_code": "G1", "created_date": "2026-01-01"}] |
| Grade Detail | /api/grade/<int:id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Grade updated/deleted"} |
| Headquarters List | /api/headquarters/ | GET, POST | POST: {"headquarter_name": "Mumbai HQ", "headquarter_code": "MUM", "headquarter_address": "123 Business Park, Mumbai", "company_id": 2, "status": "Y"} | GET: [{"headquarter_id": 1, "headquarter_name": "Mumbai HQ", "headquarter_code": "MUM", "headquarter_address": "123 Business Park, Mumbai", "created_at": "2026-01-01"}] |
| Headquarter Detail | /api/headquarters/<int:headquarter_id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Headquarter updated/deleted"} |
| Staff Roles List | /roles/ | GET, POST | POST: {"role_name": "Team Lead", "role_resources": "dashboard,employees,reports"} | GET: [{"role_id": 1, "role_name": "Admin"}, {"role_id": 2, "role_name": "Employee"}] |
| Staff Role Delete | /roles/<int:role_id>/ | DELETE | None | {"message": "Role deleted"} |
| Staff Role API | /api/staffrole/ | GET, POST | POST: {"role_name": "string"} | POST: {"message": "Role created successfully", "role_id": 5, "role_name": "Team Lead", "company_id": 2, "created_at": "2026-01-31 10:00:00"} |
| Staff Role Detail API | /api/staffrole/<int:role_id>/ | GET, PATCH, DELETE | PATCH: {"role_name": "string"} | {"message": "Role updated/deleted"} |
| Office Shifts List | /shifts/ | GET, POST | POST: {"shift_name": "Morning Shift", "start_time": "06:00:00", "end_time": "14:00:00"} | GET: Shifts data |
| Office Shift Detail | /shifts/<int:office_shift_id>/ | PUT, DELETE | PUT: Same as POST | {"message": "Shift updated/deleted"} |
| Policies List | /policies/ | GET, POST | POST (multipart/form-data): {"title": "Leave Policy", "description": "Company leave policy document", "added_by": 1, "attachment": "file", "company_id": 2} | GET: {"message": "Policies retrieved successfully", "data": [{"policy_id": 1, "company_id": 2, "title": "Leave Policy", "description": "Company leave policy", "attachment": {"file_name": "leave_policy.pdf", "file_url": "/media/policies/leave_policy.pdf"}, "added_by": 1, "created_at": "2026-01-01"}]} |
| Policy Detail | /policies/<int:pk>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Policy updated/deleted"} |
| Acknowledge Policy | /acknowledge_policy/ | GET | None | {"message": "Policy acknowledgements retrieved successfully", "data": []} |
| Acknowledge Policy Detail | /acknowledge_policy/<int:policy_id>/ | GET | None | Policy acknowledgement data |
| Policy Dashboard | /policy-dashboard/ | GET | None | {"message": "Employee policy acknowledgement status", "acknowledged": [], "not_acknowledged": [], "partially_acknowledged": []} |
| Policy Allocation | /api/policy-allocation/ | GET, POST | POST: Policy allocation fields | Policy allocation data |
| Policy Allocation Detail | /api/policy-allocation/<int:policy_allocation_id>/ | PATCH | PATCH: Policy allocation fields | {"message": "Updated"} |
| Policy Allocation Delete | /api/policy-allocation/<str:employee_id>/ | DELETE | None | {"message": "Deleted"} |
| Employee Assigned Policies | /policies/assigned/<str:emp_id>/ | GET | None | Assigned policies data |
| Acknowledge Policy Employee | /policies/acknowledge/<str:emp_id>/ | POST | Acknowledgement data | {"message": "Acknowledged"} |
| Download Acknowledgement Template | /policies/download-acknowledgement-template/<str:emp_id>/ | GET | None | PDF file |
| Upload Signed Document | /policies/upload-signed-document/<str:emp_id>/ | POST | {"signed_document": "file"} | {"message": "Uploaded"} |
| Signed Document Status | /policies/signed-document-status/<str:emp_id>/ | GET | None | Status data |
| View Signed Document | /policies/view-signed-document/<str:emp_id>/ | GET | None | Document file |
| All Signed Documents | /policies/all-signed-documents/ | GET | None | All signed documents list |
| Admin Holidays List | /admin-holidays/ | GET, POST | POST: {"event_name": "Republic Day", "country": "India", "state": "Maharashtra", "employee_hub": "Mumbai", "start_date": "2026-01-26", "end_date": "2026-01-26", "description": "National Holiday", "is_publish": "published"} | GET: [{"holiday_id": 1, "event_name": "Republic Day", "start_date": "2026-01-26", "end_date": "2026-01-26", "description": "National Holiday", "status": "published", "created_at": "2026-01-01", "country": "India", "state": "Maharashtra", "employee_hub": "Mumbai"}] |
| Admin Holiday Detail | /admin-holidays/<int:holiday_id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Holiday updated/deleted"} |
| Employee Holidays | /employee/holidays/<str:employee_id>/ | GET | None | [{"holiday_id": 1, "event_name": "Republic Day", "description": "National Holiday", "start_date": "2026-01-26", "end_date": "2026-01-26", "status": "published"}] |
| Employee Holidays Alt | /Empholidays/<str:employee_id>/ | GET | None | Same as above |
| Events List | /events/ | GET, POST, PATCH | POST: {"employee_id": "EMP001", "company_id": 2, "event_title": "Team Meeting", "event_date": "2026-02-01", "event_time": "10:00:00", "event_color": "#FF5733", "event_note": "Monthly team sync"} | GET: [{"event_id": 1, "employee_id": "EMP001", "employee_name": "John Doe", "company_id": 2, "event_title": "Team Meeting", "event_date": "2026-02-01", "event_time": "10:00:00", "event_color": "#FF5733", "event_note": "Monthly team sync", "created_at": "2026-01-30"}] |
| Event Detail | /events/<int:event_id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Event updated/deleted"} |
| Employee Events | /employee_events/<str:employee_id>/ | GET | None | Employee events list |
| Announcements List | /announcements/ | GET, POST | POST: {"department_name": "All Departments", "title": "Company Update", "start_date": "2026-02-01", "end_date": "2026-02-28", "summary": "Important company announcement", "description": "Detailed description here"} | GET: {"message": "Announcements retrieved successfully", "data": [{"announcement_id": 1, "title": "Company Update", "department_name": "All Departments", "description": "Detailed description", "start_date": "2026-02-01", "end_date": "2026-02-28"}]} |
| Announcement Detail | /announcements/<int:announcement_id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Announcement updated/deleted"} |
| Travels List | /travels/ | GET, POST | POST: {"employee_id": "EMP001", "employee_name": "John Doe", "start_date": "2026-02-15", "end_date": "2026-02-17", "associated_goals": "Client meeting", "visit_purpose": "Business development", "visit_place": "New Delhi", "travel_mode": "Flight", "arrangement_type": "Company arranged", "expected_budget": 50000.00, "actual_budget": 45000.00, "description": "Q1 client visit", "status": "Pending", "added_by": 1} | GET: {"message": "All travels fetched successfully", "data": [travel objects]} |
| Travel Detail | /travels/<int:travel_id>/ | GET, PATCH, DELETE | PATCH: Same as POST | {"message": "Travel updated/deleted"} |
| Trainings List | /trainings/ | GET, POST | POST: Training fields | Training data |
| Training Detail | /trainings/<int:pk>/ | PATCH, DELETE | PATCH: Training fields | {"message": "Training updated/deleted"} |
| Trainers List | /trainers/ | GET, POST | POST: Trainer fields | Trainer data |
| Trainer Detail | /trainers/<int:pk>/ | PATCH, DELETE | PATCH: Trainer fields | {"message": "Trainer updated/deleted"} |
| Awards List | /api/awards/ | GET, POST | POST: {"employee_id": "EMP001", "award_type_id": 1, "associated_goals": "Sales target achieved", "gift_item": "Watch", "cash_price": 5000.00, "award_photo": "url_to_photo", "award_month_year": "January 2026", "award_information": "Best performer", "description": "Achieved 150% of target"} | GET: [{"award_id": 1, "company_id": 2, "employee_id": "EMP001", "employee_name": "John Doe", "award_type_id": 1, "award_type_name": "Best Performer", "associated_goals": "Sales target achieved", "gift_item": "Watch", "cash_price": 5000.00, "award_photo": "url", "award_month_year": "January 2026", "award_information": "Best performer", "description": "Achieved 150% of target", "created_at": "2026-01-31"}] |
| Award Detail | /api/awards/<int:pk>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Award updated/deleted"} |
| Employee Awards | /employee_awards/<str:employee_id>/ | GET | None | Employee awards list |
| Admin Assets List | /assets/ | GET, POST | POST (multipart/form-data): {"assets_name": "Dell Laptop", "assets_category_id": 1, "brand_id": 1, "product_id": 1, "employee_id": "EMP001", "purchase_date": "2026-01-15", "serial_number": "DELL123456", "manufacturer": "Dell Inc", "company_asset_code": "AST001", "quantity": 1, "is_working": "yes", "invoice_number": "INV2026001", "warranty_end_date": "2029-01-15", "asset_note": "Assigned to IT department", "asset_image": "file"} | GET: [Asset objects with all fields] |
| Admin Asset Detail | /assets/<int:pk>/ | PATCH, DELETE | PATCH: {"action": "return_yes"} or asset fields | {"message": "Asset updated/deleted"} |
| Employee Assets | /employee_assets/<str:employee_id>/ | GET | None | Employee assets list |
| Confirm Asset | /employee_confirm_asset/<str:pk>/ | PATCH | Confirmation data | {"message": "Asset confirmed"} |
| Asset Requisition List | /api/assets-requisition/ | GET, POST | POST: {"requisition_number": "REQ001", "asset_name": "Laptop", "assets_category_id": 1, "assets_type_id": 1, "assets_brand_id": 1, "specification": "16GB RAM, 512GB SSD", "quantity": 1, "expected_date": "2026-02-15", "status": "P"} | Asset requisition data |
| Asset Requisition Detail | /api/assets-requisition/<int:requisition_id>/ | PATCH | PATCH: Same as POST | {"message": "Requisition updated"} |
| HR Assets Dashboard | /hr-assets-dashboard/ | GET | None | Assets dashboard data |
| HR Assets Approval | /hr-return-approval/<int:pk>/ | PATCH | Approval data | {"message": "Approved"} |
| Resignations List | /resignations/ | GET, POST | POST: {"company_id": 2, "employee_id": "EMP001", "notice_date": "2026-02-01", "resignation_date": "2026-02-01", "reason": "Personal reasons", "added_by": 1, "status": "pending"} | GET: [{"resignation_id": 1, "company_id": 2, "employee_id": "EMP001", "resignation_date": "2026-02-01", "last_working_day": "2026-03-01", "reason": "Personal reasons", "added_by": 1, "status": "Pending", "created_at": "2026-02-01", "employee_name": "John Doe", "department_name": "IT"}] |
| Resignation Detail | /resignations/<int:resignation_id>/ | PATCH, DELETE | PATCH: {"status": "approved", "last_working_day": "2026-03-01"} | {"message": "Resignation updated/deleted"} |
| Employee Resignation | /employee_resignations/<str:employee_id>/ | GET, POST | POST: {"reason": "Career growth opportunity"} | POST: {"message": "Resignation submitted successfully.", "employee_id": "EMP001", "employee_name": "John Doe", "department_id": 1, "resignation_date": "2026-01-31", "reason": "Career growth opportunity", "status": "Pending"} |
| Approve Resignation Email | /approve_resignation_through_mail/<int:resignation_id>/ | GET | None | Approval confirmation |
| Reject Resignation Email | /reject_resignation_through_mail/<int:resignation_id>/ | GET | None | Rejection confirmation |
| Employee Exits List | /employee-exits/ | GET, POST | POST: {"employee_id": "EMP001", "exit_date": "2026-03-01", "exit_type_id": 1, "sub_exit_type_id": 1, "reason": "Resignation", "added_by": 1} | GET: [{"exit_id": 1, "company_id": 2, "employee_id": "EMP001", "employee_name": "John Doe", "exit_date": "2026-03-01", "exit_type_id": 1, "exit_type_name": "Resignation", "sub_exit_type_id": 1, "exit_interview": "yes", "is_inactivate_account": "no", "reason": "Career growth", "accountability_to": "Manager", "added_by": 1, "created_at": "2026-01-31"}] |
| Employee Exit Detail | /employee-exits/<int:exit_id>/ | PATCH, DELETE | PATCH: Exit fields | {"message": "Exit updated/deleted"} |
| Exit Employee Table 1 | /exit-employee-table1/ | GET | None | Exit table data |
| Update Exit Table 1 | /update-exit-employee-table1/<str:employee_id>/ | PATCH | Table fields | {"message": "Updated"} |
| Exit Employee Table 2 | /exit-employee-table2/ | GET | None | Exit table data |
| Update Exit Table 2 | /update-exit-employee-table2/<str:employee_id>/ | PATCH | Table fields | {"message": "Updated"} |
| Exit Employee Table 3 | /exit-employee-table3/ | GET | None | Exit table data |
| Update Exit Table 3 | /update-exit-employee-table3/<str:employee_id>/ | PATCH | Table fields | {"message": "Updated"} |
| Exit Employee Final Table | /exit-employee-finaltable/ | GET | None | Final exit table data |
| Exit Questionnaire | /exit-questionnaire/ | GET, POST | POST: Questionnaire fields | Questionnaire data |
| Exit Questionnaire Detail | /exit-questionnaire/<int:ques_id>/ | PATCH, DELETE | PATCH: Questionnaire fields | {"message": "Updated/deleted"} |
| Submit Exit Feedback | /post_exit_procedure_feedback/ | POST | Feedback data | {"message": "Submitted"} |
| View Employee Feedback | /view_employeewise_feedback_form/ | GET | None | Employee feedback |
| View All Feedback | /view_all_employee_feedback_form/ | GET | None | All feedback data |
| Get Terminations | /get-terminations/ | GET | None | Terminations list |
| Post Termination | /post-terminations/ | POST | Termination data | {"message": "Created"} |
| Update Termination | /update-terminations/<int:pk>/ | PATCH | Termination data | {"message": "Updated"} |
| Pending Terminations | /pending-terminations/ | GET | None | Pending terminations |
| Send Terminations | /send-terminations/ | GET | None | Sent terminations |
| Upload Clearance Form | /Upload-Clearance-Form/<str:employee_id>/ | PATCH | {"clearance_form": "file"} | {"message": "Uploaded"} |
| Admin Projects List | /api/projects/ | GET, POST | POST: {"client_id": "Client Name", "title": "Project Alpha", "start_date": "2026-02-01", "end_date": "2026-06-30", "assigned_to": "EMP001,EMP002,EMP003", "priority": "High", "budget_hours": 500.00, "project_progress": 0, "summary": "New development project", "description": "Detailed project description", "project_note": "Important notes", "associated_goals": "Q1 Goals"} | GET: [{"id": 1, "title": "Project Alpha", "client_name": "Client Name", "start_date": "2026-02-01", "end_date": "2026-06-30", "assigned_to": "John Doe, Jane Smith", "priority": "High", "budget_hours": 500.00, "project_progress": 25, "summary": "New development project", "description": "Detailed description", "project_note": "Important notes", "associated_goals": "Q1 Goals", "status": 1, "created_at": "2026-01-31"}] |
| Admin Project Detail | /api/projects/<int:project_id>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Project updated/deleted"} |
| Employee Projects | /api/employee_projects/<str:employee_id>/ | GET | None | Assigned projects |
| Project Progress Summary | /api/projects/progress-summary/ | GET | None | Progress summary |
| Project Discussion | /api/employee_projects/discussions/<int:project_id>/ | POST | Discussion data | {"message": "Discussion added"} |
| Project Attachment | /api/employee_projects/attachment/<int:project_id>/ | POST | {"attachment": "file"} | {"message": "Attachment uploaded"} |
| Tasks List | /api/tasks/ | GET, POST | POST: Task fields | Tasks data |
| Task Detail | /api/tasks/<int:task_id>/ | PATCH, DELETE | PATCH: Task fields | {"message": "Task updated/deleted"} |
| Employee Tasks | /employee/tasks/<str:employee_id>/ | GET | None | Employee tasks |
| Add Task Discussion | /employee/task/discussion/<int:task_id>/ | POST | Discussion data | {"message": "Discussion added"} |
| Add Task Note | /employee/task/note/<int:task_id>/ | POST | Note data | {"message": "Note added"} |
| Add Task Attachment | /employee/task/attachment/<int:task_id>/ | POST | {"attachment": "file"} | {"message": "Attachment added"} |
| Task Discussions | /task-discussions/ | GET, POST | POST: Discussion data | Discussion list |
| Task Files List | /task-files/ | GET, POST | POST: {"file": "file", "task_id": 1} | File list |
| Task File Detail | /task-files/<int:task_file_id>/ | GET, PATCH, DELETE | PATCH: File data | {"message": "File updated/deleted"} |
| Task Notes List | /task-notes/ | GET, POST | POST: Note data | Notes list |
| Task Note Detail | /task-notes/<int:task_note_id>/ | GET, PATCH, DELETE | PATCH: Note data | {"message": "Note updated/deleted"} |
| Assigned Task Detail | /assigned_tasks/<int:task_id>/ | GET, PUT, DELETE | PUT: Task data | Task details |
| Project Bugs List | /ci_projects_bugs/ | GET, POST | POST: Bug data | Bugs list |
| Project Bug Detail | /ci_projects_bugs/<int:project_bug_id>/ | PATCH, DELETE | PATCH: Bug data | {"message": "Bug updated/deleted"} |
| Employee Support Tickets | /api/employee_support_tickets/<str:employee_id>/ | GET, POST | POST: Ticket data | Tickets list |
| Admin Support Tickets | /admin_support_tickets/ | GET, POST | POST: Ticket data | Tickets list |
| Admin Support Ticket Detail | /admin_support_tickets/<int:ticket_id>/ | GET, PATCH, DELETE | PATCH: Ticket data | {"message": "Ticket updated/deleted"} |
| Visitors List | /visitors/ | GET, POST | POST: {"company_id": 2, "department": 1, "visit_purpose": "Meeting", "visitor_name": "John Smith", "phone": "9876543210", "email": "john@example.com", "visit_date": "2026-02-01", "check_in": "10:00:00", "address": "123 Main Street", "description": "Client meeting", "created_by": 1} | Visitors list |
| Visitor Detail | /visitors/<int:pk>/ | GET, PATCH, DELETE | PATCH: Same as POST | {"message": "Visitor updated/deleted"} |
| Visitors Raw List | /visitors/raw/ | GET | None | Raw visitors list |
| Disciplinary Cases List | /api/disciplinary-cases/ | GET, POST | POST: {"company_id": 2, "Warning_to": "EMP001", "Warning_by": 1, "warning_date": "2026-01-31", "attachment": "url", "subject": "Policy Violation", "description": "Details", "warning_type_id": 1} | Cases list |
| Disciplinary Case Detail | /api/disciplinary-cases/<int:pk>/ | PATCH, DELETE | PATCH: Same as POST | {"message": "Case updated/deleted"} |
| Clients List | /api/clients/ | GET, POST | POST (multipart/form-data): {"full_name": "Client Company", "company_name": "Client Corp", "contact_number": "9876543210", "gender": "Male", "email_address": "client@example.com", "profile_picture": "file"} | Clients list |
| Client Detail | /api/clients/<int:client_id>/ | GET, PATCH, DELETE | PATCH: Same as POST | {"message": "Client updated/deleted"} |
| Admin Dashboard | /admin_dashboard/ | GET, POST | None | {"status": "success", "emp_count": 100, "emp_count_active": 95, "emp_count_inactive": 5, "month_wise_data": [], "resignation_data": {}, "department_wise_count": [], "designation_wise_count": [], "division_wise_count": [], "active_employees": []} |
| Employee Dashboard | /api/employee-dashboard/ | GET | None | Dashboard data |
| Emp Dashboard | /empdashboard/<str:employee_id>/ | GET | None | Dashboard data |
| Company Setup Dashboard | /api/company-setup-dashboard/ | GET | None | [{"department_id": 1, "department_name": "IT", "active_employee_count": 25}] |
| Todos List | /api/todos/ | GET, POST | POST: Todo data | Todos list |
| Todo Detail | /api/todos/<int:todo_id>/ | PATCH, DELETE | PATCH: Todo data | {"message": "Todo updated/deleted"} |
| Global Notifications | /notifications/global/<str:employee_id>/ | GET | None | Notifications list |
| Biometric List | /biometric/ | GET, POST | POST: Biometric data | Biometric list |
| Biometric Detail | /biometric/<int:ci_biomatric_id>/ | GET, PUT, PATCH, DELETE | PUT/PATCH: Biometric data | {"message": "Biometric updated/deleted"} |
| Employee Confirmation | /EmpConfirmation/<str:employee_id>/ | GET, POST, PATCH | POST/PATCH: Confirmation data | Confirmation data |
| Policy Acknowledgement Status | /policy_ack/<str:emp_id>/ | GET | None | Acknowledgement status |
| Company Details | /api/company-details/ | GET, POST, PATCH | POST: {"company_name": "Company Name", "register_address": "Address", "manufacturing_address": "Address", "phone_number": "9876543210", "pan_number": "ABCDE1234F", "company_stamp": "url"} | Company details |
| Payroll | /payroll/<int:user_id>/<int:type>/ | GET | None | Payroll data (type=1: employee info, type=2: salary) |
| States Dropdown | /api/states/ | GET | None | States list |
| Countries Dropdown | /api/countries/ | GET | None | Countries list |
| Employee Dropdown | /employee-dropdown/ | GET | None | Employees list |
| Case Types Dropdown | /api/case-types/ | GET, POST | POST: Case type data | Case types list |
| Religion Dropdown | /api/religion-dropdown/ | GET | None | Religions list |
| Leave Type Dropdown | /api/leavetype-dropdown/ | GET | None | Leave types list |
| Citizenship Dropdown | /api/citizenship-dropdown/ | GET | None | Citizenships list |
| Nationality Dropdown | /api/nationality-dropdowns/ | GET | None | Nationalities list |
| Staff Role Dropdown | /api/staffrole-dropdown/ | GET | None | Staff roles list |
| Department Employee Count | /api/department-employee-count/ | GET | None | Department counts |
| Designation Employee Count | /api/designation-employee-count/ | GET | None | Designation counts |
| Award Types | /api/award-types/ | GET, POST | POST: Award type data | Award types list |
| Award Type Delete | /api/award-types/<int:award_type_id>/ | DELETE | None | {"message": "Deleted"} |
| Training Skills | /api/training-skills/ | GET, POST | POST: Skill data | Skills list |
| Assets Category | /api/assets-category/ | GET, POST | POST: Category data | Categories list |
| Assets Category Detail | /api/assets-category/<int:constants_id>/ | PATCH, DELETE | PATCH: Category data | {"message": "Updated/deleted"} |
| Assets Type | /api/assets-type/ | GET, POST | POST: Type data | Types list |
| Assets Type Detail | /api/assets-type/<int:constants_id>/ | PATCH, DELETE | PATCH: Type data | {"message": "Updated/deleted"} |
| Assets Brand | /api/assets-brand/ | GET, POST | POST: Brand data | Brands list |
| Assets Brand Detail | /api/assets-brand/<int:constants_id>/ | PATCH, DELETE | PATCH: Brand data | {"message": "Updated/deleted"} |
| Arrangement Type | /api/arrangement-type/ | GET, POST | POST: Arrangement data | Arrangements list |
| Arrangement Type Detail | /api/arrangement-type/<int:constants_id>/ | PATCH, DELETE | PATCH: Arrangement data | {"message": "Updated/deleted"} |
| Exit Type | /api/exit-type/ | GET, POST | POST: Exit type data | Exit types list |
| Exit Type Detail | /api/exit-type/<int:id>/ | PATCH, DELETE | PATCH: Exit type data | {"message": "Updated/deleted"} |
| Travel Mood Dropdown | /api/travel-mood/ | GET | None | Travel moods list |
| Departments Dropdown | /api/departments/dropdown/ | GET | None | Departments list |
| Designations Dropdown | /api/designations/dropdown/ | GET | None | Designations list |
| Employee Role Dropdown | /api/dropdown/employee-role/ | GET | None | Employee roles list |
| Resigned Employees Dropdown | /resigned-employees-dropdown/ | GET | None | Resigned employees list |
| Confirmation Employees Dropdown | /confirmation-employees-dropdown/ | GET | None | Confirmation employees list |
| Emp Name Dropdown | /dropdown/<str:empid>/ | GET | None | Manager-wise employees |
| Designation-wise Count | /get_designationwise_count/ | GET | None | Designation counts |
| Grade-wise Count | /get_gradewise_count/ | GET | None | Grade counts |
| Get Exit Date | /get-exit-date/<str:employee_id>/ | GET | None | Exit date |
| Check Asset Status | /check-asset-status/<str:employee_id>/ | GET | None | Asset status |
| Get Letters | /get-letters/<str:employee_id>/ | GET | None | Employee letters |
| Get Letters All | /get-letters/ | GET | None | All letters |
| HR Exit Employee | /hr-exit-employee/ | GET | None | HR exit data |
| Upload HR Sign | /upload-sign/<str:employee_id>/ | PATCH | {"sign": "file"} | {"message": "Uploaded"} |
| Upload Company Stamp | /upload-stamp/<int:company_detail_id>/ | PATCH | {"stamp": "file"} | {"message": "Uploaded"} |
| Data For Letters | /data-for-letters/<str:employee_id>/ | GET | None | Letter data |
| Get Employee Exit | /get-exit-employee/ | GET | None | Exit employees |
| Add Employee Exit | /add-new-exit-employee/ | POST | Exit employee data | {"message": "Created"} |
| Update Employee Exit | /exit-employee/<int:exit_id>/ | PATCH, DELETE | PATCH: Exit employee data | {"message": "Updated/deleted"} |

---

## HRMS App Module APIs (Base URL: `/api/`)

| Name | API URL | Method | Request Payload | Response |
|------|---------|--------|-----------------|----------|
| Employee Manager Dropdown | /api/emp_manager_dropdown/ | GET | None | Employees and managers list |
| Designation Department Dropdown | /api/desig_dept_dropdown/ | GET | None | Designations and departments |
| Designation Dept Dropdown Detail | /api/desig_dept_dropdown/<int:dept_id>/ | GET | None | Department-wise designations |
| Employees By Designation | /api/employees_by_designation/ | GET | None | Designation-wise employees |
| Designation Dropdown Filter Line Manager | /api/designation_dropdown_filter_by_line_manager/ | GET | None | Filtered designations |
| State Dropdown | /api/state_dropdown/ | GET | None | States list |
| Employee Hub Dropdown | /api/employee_hub_dropdown/<int:state_id>/ | GET | None | State-wise hubs |
| Office Shift Dropdown | /api/office_shift_dropdown/<int:employee_hub_id>/<int:state_id>/ | GET | None | Hub and state-wise shifts |
| Contract Details | /api/contract_details/ | GET | None | Contract details |
| Employee Basic Information | /api/emp_basic_info/ | GET | None | Employee basic info |
| Personal Information | /api/personal_info/ | GET | None | Personal info |
| Get Profile Photo | /api/get_profile_photo/<str:employee_id>/ | GET | None | Profile photo |
| Update Profile Photo | /api/update_profile_photo/ | POST | {"photo": "file"} | {"message": "Photo updated"} |
| Account Information | /api/account_info/ | GET | None | Account info |
| Document Details | /api/document_details/ | GET | None | Documents list |
| Change Password | /api/change_password/ | POST | {"old_password": "string", "new_password": "string"} | {"message": "Password changed"} |
| Timesheet Agenda | /api/timesheet_agenda/ | GET | None | Timesheet data |
| Leave Statistics | /api/leave_statistics/ | GET | None | Leave statistics |
| Dashboard Attendance | /api/dashboard_attendance/<str:employee_id>/ | GET | None | Dashboard attendance |
| Employee Attendance | /api/employee_attendance/ | GET | None | Employee attendance |
| Basic Info | /api/basic_info/ | GET | None | Basic info |
| Holiday List | /api/holiday_list/ | GET | None | Holidays list |
| Project List | /api/project_list/<int:user_id>/<int:type>/ | GET | None | Projects list |
| Project Details | /api/project_details/<int:user_id>/ | GET | None | Project details |
| Project Discussion | /api/project_discussion/ | POST | Discussion data | {"message": "Discussion added"} |
| Project Attach File | /api/project_attach_file/ | POST | {"file": "file"} | {"message": "File attached"} |
| Payroll | /api/payroll/<int:user_id>/<int:type>/ | GET | None | Payroll data |
| Policies | /api/policies/ | GET | None | Policies list |
| Employee Details | /api/employee_details/ | GET | None | All employees details |
| Edit Employee Get | /api/edit_employee/<int:user_id>/ | GET | None | Employee details |
| Edit Employee | /api/edit_employee/ | PUT, DELETE | PUT: Employee data | {"message": "Employee updated/deleted"} |
| Change Manager | /api/change_manager/ | POST | {"employee_id": "EMP001", "new_manager_id": 2} | {"message": "Manager changed"} |
| Get Max Employee ID | /api/get_max_employee_id/ | GET | None | {"max_id": "EMP099"} |
| Fetch Documents | /api/fetch_documents/ | GET | None | Documents list |
| Check Existing Email | /api/check_existing_email/ | POST | {"email": "user@example.com"} | {"exists": true} |
| Add Employee | /api/add_employee/ | POST | Employee data | {"message": "Employee added"} |
| Role List | /api/role_list/ | GET, PUT | PUT: Role data | Roles list |
| Role Delete | /api/role_list/<int:role_id>/ | DELETE | None | {"message": "Role deleted"} |
| Add Role | /api/add_role/ | POST | {"role_name": "string", "permissions": []} | {"message": "Role added"} |
| Office Shift | /api/office_shift/ | GET, POST, PUT | POST: Shift data | Shifts list |
| Office Shift Delete | /api/office_shift/<int:shift_id>/ | DELETE | None | {"message": "Shift deleted"} |
| Attendance Overview | /api/attendance_overview/ | GET | None | Attendance overview |
| Manual Attendance | /api/manual_attendance/ | GET, POST | POST: Attendance data | {"message": "Attendance marked"} |
| Employee Hub | /api/employee_hub/ | GET, POST, PUT, DELETE | POST: Hub data | Hub data |
| Monthly Report | /api/monthly_report/ | GET | None | Monthly report |
| Holiday | /api/holiday/ | GET, POST | POST: Holiday data | Holidays list |
| Payroll Setup Configuration | /api/payroll_setup_configuration/ | GET, POST | POST: Config data | Config data |
| Payroll Employee TDS | /api/payroll_employee_tds/ | GET, POST | POST: TDS data | TDS data |
| Payroll Report | /api/payroll_report/<int:month>/<int:year>/ | GET | None | Payroll report |
| Pre-Saved Payroll Report | /api/pre_saved_payroll_report/ | GET | None | Saved reports |
| Save Payroll Report | /api/save_payroll_report/ | POST | Report data | {"message": "Saved"} |
| Payment Info | /api/payment_info/ | GET | None | Payment info |
| Update Payment Info | /api/update_payment_info/ | PUT | Payment data | {"message": "Updated"} |
| Salary Structure | /api/salary_structure/ | GET | None | Salary structure |
| Payslip History | /api/payslip_history/ | GET | None | Payslip history |
| Payslip | /api/payslip/ | GET | None | Payslip |
| View Employee Salary Slip | /api/view_employee_salary_slip/<str:employee_id>/ | GET | None | Salary slip |
| Assets Inventory | /api/assets_inventory/ | GET, POST | POST: Asset data | Assets list |
| Monthly Attendance Report | /api/attendance/monthly-report/ | GET | None | Monthly report |
| Monthly Leave Report | /api/leave/monthly-report/ | GET | None | Monthly leave report |
| Leave Balance Report | /api/leave/balance-report/ | GET | None | Leave balance report |
| New Joiner Report | /api/new-joiner-report/ | GET | None | New joiners report |
| Manpower Report | /api/manpower-report/ | GET | None | Manpower report |
| Employee Attrition Report | /api/employee-attrition-report/ | GET | None | Attrition report |
| Employee Master Report | /api/employee_master_report/ | GET | None | Master report |
| HR Master Data | /api/hr-master-data/ | GET | None | HR master data |
| Employee Exit Report | /api/employee-exit-report/ | GET | None | Exit report |
| Performance Management Report | /api/performance-management-report/ | GET | None | Performance report |
| Annual Appraisal Report | /api/annual-appraisal-report/ | GET | None | Appraisal report |
| Salary Report | /api/salary-report/ | GET | None | Salary report |
| PT Report | /api/pt-report/ | GET | None | PT report |
| Holiday Calendar View | /api/holidays/calendar/<int:country_id>/<int:state_id>/<int:employee_hub>/ | GET | None | Holiday calendar |
| View Notification | /api/view_notification/ | GET | None | Notifications |
| Save HR Revenue Expense | /api/save_hr_revenue_expense/ | GET, POST | POST: {"revenue": 100000, "expense": 50000, "month": 1, "year": 2026} | Revenue/expense data |
| Save HR Revenue Expense Update | /api/save_hr_revenue_expense/<int:hr_rev_exp_id>/ | PATCH | Same as POST | {"message": "Updated"} |
| Send OTP | /api/send_otp/ | POST | {"email": "user@example.com"} | {"message": "OTP sent"} |
| Verify OTP | /api/verify_otp/ | POST | {"email": "user@example.com", "otp": "123456"} | {"message": "OTP verified"} |
| Reset Password | /api/reset_password/ | POST | {"email": "user@example.com", "new_password": "newpass123"} | {"message": "Password reset"} |
| HR Dashboard Metrics | /api/hr_dashboard_metrics/ | GET | None | Dashboard metrics |
| HR Dashboard Metrics By Month | /api/hr_dashboard_metrics_by_month/ | GET | None | Monthly metrics |
| HR Dashboard Graphs | /api/hr_dashboard_graphs/ | GET | None | Dashboard graphs |
| User Role Permissions | /api/roles/user-permissions/ | GET | None | User permissions |
| User Role Permissions By ID | /api/roles/user-permissions/<int:user_id>/ | GET | None | User-specific permissions |
| Check Permission | /api/roles/check-permission/ | POST | {"user_id": 1, "permission": "view_employee"} | {"has_permission": true} |
| Check Multiple Permissions | /api/roles/check-multiple-permissions/ | POST | {"user_id": 1, "permissions": ["view_employee", "edit_employee"]} | {"permissions": {"view_employee": true, "edit_employee": false}} |
| Role Create | /api/roles/create/ | POST | {"role_name": "string", "permissions": []} | {"message": "Role created"} |
| Role Update | /api/roles/update/ | PUT | {"role_id": 1, "role_name": "string", "permissions": []} | {"message": "Role updated"} |
| Role Delete | /api/roles/delete/<int:role_id>/ | DELETE | None | {"message": "Role deleted"} |
| Role List | /api/roles/list/ | GET | None | Roles list |
| Training Create | /api/training/create/ | POST | Training data | {"message": "Training created"} |
| Training Update | /api/training/update/ | PUT | Training data | {"message": "Training updated"} |
| Training Delete | /api/training/delete/<int:training_id>/ | DELETE | None | {"message": "Training deleted"} |
| Training List | /api/training/list/ | GET | None | Trainings list |
| Training Details | /api/training/details/<int:training_id>/ | GET | None | Training details |
| Training Update Status | /api/training/update-status/ | PATCH | {"training_id": 1, "status": "completed"} | {"message": "Status updated"} |
| Search By Email Vet Talent | /api/search_by_email_vet_talent/ | GET | Query params: email | Search results |
| Employee Leave Pattern | /api/employee_leave_pattern/ | GET | None | Leave patterns |
| Check Phasewise Parameters | /api/check_phasewise_parameters/ | GET | None | Phase parameters |
| Get Employee Details Clearance Form | /api/get_employee_details_clearance_form/ | GET | None | Clearance form data |

---

## M_App Module APIs (Base URL: `/apps/`)

| Name | API URL | Method | Request Payload | Response |
|------|---------|--------|-----------------|----------|
| Announcements List | /apps/announcements/ | GET, POST | POST: {"title": "string", "department_id": 1, "start_date": "2026-02-01", "end_date": "2026-02-28", "summary": "string", "description": "string"} | GET: [{"announcement_id": 1, "department_id": 1, "title": "Company Update", "department_name": "All", "start_date": "2026-02-01", "end_date": "2026-02-28", "summary": "Brief summary", "description": "Full description"}] |
| Announcement Details | /apps/announcements_details/<int:announcement_id>/ | GET, PUT, DELETE | PUT: Same as POST | Announcement details |
| Policies List | /apps/policies/ | GET, POST | POST (multipart/form-data): {"title": "string", "description": "string", "attachment": "file"} | Policies list |
| Policy Details | /apps/policies_details/<int:policy_id>/ | GET, PUT, DELETE | PUT: Same as POST | Policy details |
| Policy Acknowledgements | /apps/policies_acknowledgements/ | GET | None | Acknowledgements list |
| Policy Dashboard | /apps/policies_dashboard/ | GET | None | Policy dashboard |
| Create Ticket | /apps/create_tickets/ | POST, PUT | POST: {"subject": "string", "department_id": 1, "ticket_priority": 1, "description": "string", "employee_id": "EMP001"} | {"message": "Ticket created", "ticket_id": 1, "ticket_code": "TC1000"} |
| Ticket Details | /apps/ticket_view/<int:ticket_id>/ | GET, POST, DELETE | POST: {"status": 1, "remarks": "string", "employee_id": "EMP001"} | Ticket details |
| Department Wise Employees | /apps/department_wise_employee/ | GET | Query param: department_id | [{"employee_id": "EMP001", "employee_name": "John Doe"}] |

---

## New HRMS Module APIs (Base URL: `/apis/`)

| Name | API URL | Method | Request Payload | Response |
|------|---------|--------|-----------------|----------|
| Get Confirmation Parameters | /apis/confirmation_parameter/ | GET | None | [{"parameter_id": 1, "para_name": "string"}] |
| Create Confirmation Parameter | /apis/confirmation_parameter/ | POST | {"para_name": "string"} | {"message": "Parameter created"} |
| Update Confirmation Parameter | /apis/confirmation_parameter/ | PUT | {"parameter_id": 1, "para_name": "string"} | {"message": "Parameter updated"} |
| Delete Confirmation Parameter | /apis/confirmation_parameter/ | DELETE | {"parameter_id": 1} | {"message": "Parameter deleted"} |
| Save Phase-wise Data | /apis/save_phasewise_data/ | POST | {"entries": [{"emp_id": 1, "parameter_id": 1, "phase": 1, "points_by_lm": 8, "comment_by_lm": "Good", "points_by_head": 9, "comment_by_head": "Excellent", "points_by_hr": 8, "comment_by_hr": "Meets expectations"}], "role_id": 13} | {"message": "Data saved", "skipped_entries": []} |
| Final Confirmation Action | /apis/final_confirmation_action/ | PATCH | {"user_id": 1, "action": "confirm", "comment_by_lm": "Recommended", "comment_by_head": "Approved", "comment_by_hr": "Confirmed"} | {"message": "Action completed", "employee_id": "EMP001"} |
| Employee Confirmation Dashboard | /apis/employee_confirmation_dashboard/ | GET | None | {"data": [Employee confirmation data]} |
| Save Designation-wise Parameters | /apis/save_Desigwise_parameters/ | POST | {"parameter_id": 1, "designation_id": 1, "phase": 1, "created_by": 1} | {"message": "Parameters saved"} |
| Get Designation-wise Table Data | /apis/get_desigwise_tabledata/ | GET | Query params: phase, designation_id | {"data": [Designation parameters]} |
| Delete Designation-wise Parameter | /apis/delete_desigwise_para/<int:pk>/ | DELETE | None | {"message": "Parameter deleted"} |
| Get Employee Performance | /apis/get_employee_performance/<int:role_id>/<int:user_id>/ | GET | None | [Employee performance data] |
| Get Employee Overall Phase-wise Marks | /apis/get_employee_overall_phasewise/ | GET | Query param: user_id | {"status": "success", "data": {Phase-wise marks}} |
| Save Employee Overall Analysis | /apis/save_employee_overall_analysis/ | POST | {"user_id": 1, "emp_id": "EMP001", "performance_analysis": "Excellent", "kra_kpi_total": 85.5, "average": 80.0, "percent_achievement": 90.0, "comment_by_lm": "Good", "comment_by_hr": "Approved", "comment_by_head": "Confirmed"} | {"status": "success", "message": "Analysis saved"} |
| Get Phase-wise Data | /apis/get_phasewise_data/<int:user_id>/ | GET | None | {"status": "success", "data": [Phase data]} |
| Employee Leave Request Report | /apis/get_employee_leave_request_report/ | GET | Query params: year, month | [Leave request report] |
| Employee Type Five Details | /apis/get_employee_type_five_details/ | POST | {"type": 5, "user_id": 1} | {"pan_number": "string", "esic_number": "string", "pf_number": "string", "aadhar_no": "string"} |
| Employee Daily Attendance Report | /apis/get_employee_daily_attendence_get_report/ | GET | Query param: date | [Daily attendance report] |
| Monthly Check-In/Out Report | /apis/get_employee_monthly_check_in_check_out_get_report/ | GET | Query params: month, year | [Monthly attendance report] |
| All Employee Leave Summary Report | /apis/get_all_employee_leave_summary_get_report/ | GET | Query param: year | {"status": "success", "data": [Leave summary]} |
| Employee Confirmation Report | /apis/get_employee_confirmation_get_report/ | GET | Query param: year | {"year": "2026", "data": [Confirmation report]} |
| Employee PIP Report | /apis/get_employee_pip_report_get_report/ | GET | Query params: year, division_id | {"year": "2026", "division_id": "1", "count": 5, "results": [PIP report]} |
| Employee Promotion Report | /apis/get_employee_promotion_get_report/ | GET | Query param: employee_id | [Promotion report] |
| Gratuity Eligibility Report | /apis/get_employee_gratuity_eligibility_get_report/ | GET | None | [Gratuity eligibility report] |
| PF Report | /apis/get_employee_pf_get_report/ | POST | {"from_date": "2026-01-01", "to_date": "2026-01-31"} | [PF report] |
| Employee Payroll Salary Report | /apis/get_employee_payroll_salary_report/ | POST | {"month": 1, "year": 2026} | [Payroll salary report] |
| Get Employees by Dept & Designation | /apis/get_promotion_report_employee_drop/ | GET | Query params: dept, desig | {"status": "success", "data": [Employees list]} |
| Save and Freeze Leave Setup | /apis/save_and_freeze_leave_setup/ | POST | [{"constants_id": 1, "leave_type": "CL", "days_per_year": 12, "current_leave_name": "Casual Leave", "current_leave_days": 12, "year": 2026}] | {"message": "Leave setup saved"} |
| Add New Assets to Stock | /apis/add_new_asset_to_stock/ | POST | {"brand_id": 1, "category_id": 1, "product_id": 1, "quantity": 10, "price": 50000.00, "invoice_number": "INV2026001", "purchase_date": "2026-01-15", "warranty_end_date": "2029-01-15"} | {"message": "Asset added to stock"} |
| Update Category | /apis/update_delete_category/ | PUT | Query param: constants_id, Body: {"category_name": "string"} | {"message": "Category updated"} |
| Delete Category | /apis/update_delete_category/ | DELETE | Query param: constants_id | {"message": "Category deleted"} |
| Get All Products | /apis/create_edit_product/ | GET | None | [Products list] |
| Create Product | /apis/create_edit_product/ | POST | {"product_name": "string"} | {"message": "Product created"} |
| Update Product | /apis/create_edit_product/ | PUT | Query param: product_id, Body: {"product_name": "string"} | {"message": "Product updated"} |
| Delete Product | /apis/create_edit_product/ | DELETE | Query param: product_id | {"message": "Product deleted"} |
| Get Available Product Quantity | /apis/get_available_qty/ | GET | Query params: category_id, brand_id | [{"product_id": 1, "product_name": "string", "total_purchased": 100, "assigned": 50, "returned": 10, "in_stock": 40}] |
| Get Metrics Form Data | /apis/get_metrics_form_data/ | GET | Query params: month, year | {"data": [Revenue data]} |
| Get Assets In Stock Table | /apis/get_assets_instock_data/ | GET | None | {"status": "success", "data": [Assets in stock]} |

---

## VetHR Module APIs (Base URL: `/api/`)

| Name | API URL | Method | Request Payload | Response |
|------|---------|--------|-----------------|----------|
| Get Employee Leave Balance | /api/leave-balance/ | GET | Query param: employee_id | [{"leave_type_id": 1, "type": "leave_type", "category_name": "Casual Leave", "days_per_year": "12", "balance_leave": 10.5, "year": "2026"}] |
| Get Leave Applications | /api/apply-leave/ | GET | Query param: employee_id | [{"leave_id": 1, "employee_id": "EMP001", "employee_name": "John Doe", "leave_type": "Casual Leave", "from_date": "2026-02-01", "to_date": "2026-02-03", "no_of_days": 3.0, "reason": "Personal work", "line_manager_status": "Pending"}] |
| Apply Leave | /api/apply-leave/ | POST | {"employee_id": "EMP001", "user_id": 1, "company_id": 2, "leave_type_id": 1, "from_date": "2026-02-01", "to_date": "2026-02-03", "reason": "Personal work", "remarks": "Optional remarks", "is_half_day": false, "leave_attachment": "url"} | {"message": "Leave application submitted successfully", "leave_id": 1, "no_of_days": 3.0, "leave_type": "Casual Leave", "note": "Sandwich rule info"} |
| Employee Leaves List | /api/employee-leaves-list/ | GET | Query param: employee_id | {"leave_applications": [{"employee_name": "John Doe", "email": "john@example.com", "leave_type": "Casual Leave", "from_date": "2026-02-01", "to_date": "2026-02-03", "days_applied": 3.0, "status": "Pending"}]} |
| Employee Leave History | /api/leave-details/ | GET | Query param: employee_id | [{"leave_type": "Casual Leave", "days_per_year": 12, "approved_leave_days": 3.0, "balance": 9.0}] |
| Get Leave Requests for Approval | /api/line-manager-approval/ | GET | None | [{"leave_id": 1, "employee_id": "EMP001", "employee_name": "John Doe", "leave_type": "Casual Leave", "from_date": "2026-02-01", "to_date": "2026-02-03", "no_of_days": 3.0, "reason": "Personal work", "line_manager_status": "Pending"}] |
| Update Leave Request Status | /api/line-manager-approval/<int:leave_id>/ | PATCH | {"line_manager_status": "approved"} | {"message": "Leave status updated successfully", "new_status": "Approved"} |
| Sandwich Rule Check | /api/sandwich-rule-check/ | POST | {"employee_id": "EMP001", "from_date": "2026-02-01", "to_date": "2026-02-03"} | {"from_date": "2026-02-01", "to_date": "2026-02-03", "sandwich_applied": 0} |

---

## Summary

| Module | Total APIs |
|--------|------------|
| App Module (/) | 140+ |
| HRMS App Module (/api/) | 94 |
| M_App Module (/apps/) | 16 |
| New HRMS Module (/apis/) | 30 |
| VetHR Module (/api/) | 7 |
| **Total** | **287+** |

---

## Notes

1. **Authentication**: All APIs require JWT Bearer token except Login and Registration
2. **Date Format**: YYYY-MM-DD
3. **Time Format**: HH:MM:SS
4. **File Uploads**: Use multipart/form-data
5. **Status Codes**: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Server Error)

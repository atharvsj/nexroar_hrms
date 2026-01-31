from django.urls import path
from django.conf.urls.static import static

from .views import *
from .views import CIProjectBugListView ,TaskDiscussionAPIView, TaskNoteView, TaskFileView, CiStaffRoleView, OfficeShiftView
from .views import BasicInfo, ChangePassword, LoginView,  OnDutyInRequest, RegistrationView, TodayAttendance, ErpUserCreateView
from .views import DepartmentView, CIPolicyView
from .views import CiBiomatricDataListCreateView, CiBiomatricDataRetrieveUpdateDeleteView, CIPunchReportView, ContractOptionAPIView, BasicInformationListAPIView
from .views import CITrainingDetailView, CITrainingView, VisitorListCreateAPIView, VisitorDetailAPIView
from .views import VisitorRawListAPIView, EmployeeDropdownView, CaseTypeDropdownView,  DesignationWiseEmployeeCountView
from .views import CompanyDetailsAPI,DivisionAPI , GradeAPI , CompanySetupDashboardAPI, HeadquarterAPI, ClientAPI, ProjectProgressCountAPI, TaskAPI
from .exit_employee_module import *
urlpatterns = [

path('login/', LoginView.as_view(), name='login'),
path('register/', RegistrationView.as_view(), name='register'),
#path('add_leave/', ApplyLeave.as_view(),name = 'add_leave'),
path('basic-info/',BasicInfo.as_view(),name = "basic_info"),
path('change-password/',ChangePassword.as_view(),name="change_password"),
path('today-attendence/',TodayAttendance.as_view(),name='Today_Attendence'),
#path('monthly-attendence/',MonthlyAttendance.as_view(),name="monthly_attendence"),
path('on-duty-request/',OnDutyInRequest.as_view(),name="on_duty_request"),
path('compoff/', CompOffView.as_view(), name='compoff-list-create'),   # GET all and POST new records
path('compoff/<int:compoff_id>/', CompOffView.as_view(), name='compoff-detail'),   #PATCH AND DELETE
path('api/leave-applications-dashboard/', LeaveApplicationDashboardAPI.as_view(), name='leave-applications'),
path('api/leave-pending-current-month/', LeavePendingCurrentMonthView.as_view(), name='leave-pending-current-month'),
# path('api/leave-types/', LeaveTypeAPIView.as_view(), name='leave-types'),
# path('api/leave-types/<int:constants_id>/', LeaveTypeAPIView.as_view(), name='leave-type-detail'),
path('api/leave-setup/', LeaveSetupAPI.as_view()),              # GET, POST
path('api/leave-setup/<int:id>/', LeaveSetupAPI.as_view()),     # PATCH, DELETE
#path('api/sandwich-check/', SandwichRuleCheckAPI.as_view(), name='sandwich-check'),



path('ci_projects_bugs/', CIProjectBugListView.as_view(), name='project_bugs'),
path('ci_projects_bugs/<int:project_bug_id>/', CIProjectBugListView.as_view(), name='project_bug_detail'),

# Employee Tasks Section
path('employee/tasks/<str:employee_id>/', EmployeeTasksView.as_view(), name='employee-tasks'),    # Get all tasks
path('employee/task/discussion/<int:task_id>/', AddTaskDiscussion.as_view()),   # Post task discussion
path('employee/task/note/<int:task_id>/', AddTaskNote.as_view()), # Post task note
path('employee/task/attachment/<int:task_id>/', AddTaskAttachment.as_view()), # Post task attachment
path('task-discussions/',TaskDiscussionAPIView.as_view(), name='task_discussions'),
path('task-files/', TaskFileView.as_view(), name='task_files_list'),  # For POST and GET (all task files)
path('task-files/<int:task_file_id>/', TaskFileView.as_view(), name='task_file_detail'),  # For GET (specific task file), PATCH, and DELETE
path('task-notes/', TaskNoteView.as_view(), name='task-note-list-create'),  # List all or create new
path('task-notes/<int:task_note_id>/', TaskNoteView.as_view(), name='task-note-detail'), 
path('assigned_tasks/<int:task_id>/', AssignedTaskDetailView.as_view(), name='assigned-task-detail'),
  
path('create_user/', ErpUserCreateView.as_view(), name='create_user'),


   # roles& privileges  ,Shifts, ExitEmployee 

path('roles/', CiStaffRoleView.as_view(), name='ci_staff_roles'),
path('roles/<int:role_id>/', CiStaffRoleView.as_view(), name='ci_staff_roles'),
path('shifts/', OfficeShiftView.as_view(), name='ci_office_shifts'),  # For GET and POST
path('shifts/<int:office_shift_id>/', OfficeShiftView.as_view(), name='delete_office_shift'),  # For DELETE
path("employee-exits/", CiEmployeeExitView.as_view()),             # GET & POST
path("employee-exits/<int:exit_id>/", CiEmployeeExitView.as_view()),  # DELETE
 
path('departments/', DepartmentView.as_view(), name='department_list'),
path('departments/<int:pk>/', DepartmentView.as_view(), name='department-detail'),
path("biometric/", CiBiomatricDataListCreateView.as_view(), name="biometric-list-create"),
path("biometric/<int:ci_biomatric_id>/", CiBiomatricDataRetrieveUpdateDeleteView.as_view(), name="biometric-detail"),

# Designation - Core HR
path('ci_designations/', CiDesignationViewSet.as_view(), name='ci_designations_list'),
path('ci_designations/<int:pk>/', CiDesignationViewSet.as_view(), name='ci_designations_detail'),

#POLICY
path('policies/', CIPolicyView.as_view(), name='get_create_policy'), #GET , POST
path('policies/<int:pk>/', CIPolicyView.as_view(), name='update_delete_policy'), #PATCH, DELETE
path('acknowledge_policy/', AcknowledgePolicyView.as_view(), name='acknowledge_policy'),  # GET all policies
path('acknowledge_policy/<int:policy_id>/', AcknowledgePolicyView.as_view(), name='acknowledge_policy'), # Get id wise policy
path('policy-dashboard/', PolicyDashboardView.as_view()),
path('policy-dashboard/<str:employee_id>/', PolicyAcknowledgementDetailView.as_view(), name='policy-detail'),
# Admin policy section
path('api/policy-allocation/', PolicyAllocationAPIView.as_view(), name="policy-allocation"),  #GET, POST
path('api/policy-allocation/<int:policy_allocation_id>/', PolicyAllocationAPIView.as_view(), name="policy-allocation"), #PATCH
path('api/policy-allocation/<str:employee_id>/', PolicyAllocationAPIView.as_view(), name="policy-allocation"),  #DELETE
# Employee policy section
path('policies/assigned/<str:emp_id>/', EmployeePolicyAcknowledgeView.as_view(), name='assigned-policies'),
path('policies/acknowledge/<str:emp_id>/', EmployeePolicyAcknowledgeView.as_view(), name='acknowledge-policy'),

# Policy Signed Acknowledgement Document - NEW
path('policies/download-acknowledgement-template/<str:emp_id>/', DownloadPolicyAcknowledgementTemplateView.as_view(), name='download-acknowledgement-template'),
path('policies/upload-signed-document/<str:emp_id>/', UploadSignedPolicyDocumentView.as_view(), name='upload-signed-document'),
path('policies/signed-document-status/<str:emp_id>/', SignedPolicyDocumentStatusView.as_view(), name='signed-document-status'),
path('policies/view-signed-document/<str:emp_id>/', ViewSignedPolicyDocumentView.as_view(), name='view-signed-document'),
path('policies/all-signed-documents/', AllSignedPolicyDocumentsView.as_view(), name='all-signed-documents'),


#employee
path('employee-contracts/', ContractOptionAPIView.as_view(), name='employee-contracts'),
path('basic-info/', BasicInformationListAPIView.as_view(), name='basic-info-list'),  # GET all
path('basic-info/<str:id>/', BasicInformationListAPIView.as_view(), name='basic-info-detail'),   # GET/UPDATE one


path("basic_info/", BasicInformation.as_view(), name="basic-info"),
#path("personal_info/", PersonalInformation.as_view(), name="personal-info"),
path('punch_reports/', CIPunchReportView.as_view(), name="punch-in"),



path('events/', EventViewSet.as_view(), name='events'),
path('events/<int:event_id>/', EventViewSet.as_view(), name='event_delete'),
path('Empholidays/<str:employee_id>/', NewHolidayView.as_view(), name='employee-holidays'),


# Travel
path('travels/', CITravelAPIView.as_view(), name='travel-list'),
path('travels/<int:travel_id>/', CITravelAPIView.as_view(), name='travel-detail'),


path('announcements/', AnnouncementListCreateView.as_view(), name='announcement-list-create'),
path('announcements/<int:announcement_id>/', AnnouncementListCreateView.as_view(), name='announcement-detail'),



# Employee Panel
path("basic_info/", BasicInformation.as_view(), name="basic-info"),
path("payroll/<int:user_id>/<int:type>/", Payroll.as_view(), name="payroll"),


path('trainings/', CITrainingView.as_view(), name='training_list_create'),
path('trainings/<int:pk>/', CITrainingDetailView.as_view(), name='training_update_delete'),

path("admin_dashboard/", AdminDashboard.as_view(), name="admin-dashboard"),


path('trainers/', CITrainerView.as_view(), name='get_post_trainers'),
path('trainers/<int:pk>/', CITrainerView.as_view(), name='patch_delete_trainer'),


path('api/awards/', AwardsView.as_view(), name='awards-list-create'),
path('api/awards/<int:pk>/', AwardsView.as_view(), name='awards-update-delete'),
path('assets/', AdminAssetsView.as_view(), name='assets-list-create'),
path('assets/<int:pk>/', AdminAssetsView.as_view(), name='assets-list-create-update-delete'),

path('api/assets-requisition/', AssetRequisitionView.as_view(), name='assets-requisition-list-create'),  # POST, GET
path('api/assets-requisition/<int:requisition_id>/', AssetRequisitionView.as_view(), name='assets-requisition-update'),  # PATCH


path('visitors/', VisitorListCreateAPIView.as_view(), name='visitor-list-create'),
path('visitors/<int:pk>/', VisitorDetailAPIView.as_view(), name='visitor-detail'),
path('visitors/raw/', VisitorRawListAPIView.as_view(), name='visitor-raw-list'),



##DROPDOWN

path("api/states/", StateDropdown.as_view(), name='state-dropdown'),
path("api/countries/", CountryDropdown.as_view(), name='country-dropdown'),
path('employee-dropdown/', EmployeeDropdownView.as_view(), name='employee-dropdown'),
path('api/case-types/', CaseTypeDropdownView.as_view(), name='case-type-dropdown'),
path('api/religion-dropdown/', ReligionDropdownView.as_view(), name='religion-dropdown'),
path('api/leavetype-dropdown/', LeaveTypeDropdownView.as_view(), name='religion-dropdown'),
path('api/citizenship-dropdown/', CitizenshipDropdownView.as_view(), name='citizenship-dropdown'),
path('api/nationality-dropdowns/', NationalityDropdownView.as_view(), name='nationality-dropdown'),
path('api/staffrole-dropdown/', StaffRoleDropdownView.as_view(), name='staffrole-dropdown'),
path('api/department-employee-count/', DepartmentWiseEmployeeCountView.as_view(), name='department-employee-count'),
path('api/designation-employee-count/', DesignationWiseEmployeeCountView.as_view(), name='designation-employee-count'),
path('api/award-types/', AwardTypeDropdownView.as_view(), name='award-type-dropdown'),
path('api/award-types/<int:award_type_id>/', AwardTypeDropdownView.as_view(), name='award-type-delete'),
path('api/training-skills/', TrainingSkillDropdownView.as_view(), name='training-skill-dropdown'),
path('api/assets-category/', AssetsCategoryDropdownView.as_view(), name='assets-category'),
path('api/assets-category/<int:constants_id>/', AssetsCategoryDropdownView.as_view(), name='assets-category'),
path('api/assets-type/', AssetsTypeDropdownView.as_view(), name='assets-type'),
path('api/assets-type/<int:constants_id>/', AssetsTypeDropdownView.as_view(), name='assets-type'),
path('api/assets-brand/', AssetsBrandDropdownView.as_view(), name='assets-brand'),
path('api/assets-brand/<int:constants_id>/', AssetsBrandDropdownView.as_view(), name='assets-brand'),
path('api/arrangement-type/', ArrangementTypeDropdownView.as_view()),
path('api/arrangement-type/<int:constants_id>/', ArrangementTypeDetailView.as_view(), name='arrangement-type-detail'),
path('api/exit-type/', ExitEmployeeTypeDropdownView.as_view()),
path('api/travel-mood/', TravelMoodDropdownView.as_view(), name='travel-mood-dropdown'),
path('api/departments/dropdown/', DepartmentDropdownAPI.as_view()),
path('api/designations/dropdown/', DesignationDropdownAPI.as_view()),


path('resignations/', ResignationListCreateView.as_view(), name='resignation-list-create'),
path('resignations/<int:resignation_id>/', ResignationDetailView.as_view(), name='resignation-detail'),
path('employee_resignations/<str:employee_id>/', EmployeeResignationClass.as_view(), name='employee-resignation'),


path('attendance/today/', TodaysAttendanceReportView.as_view(), name='todays-attendance-report'),
path('attendance/by-date/', AttendanceByDateReportView.as_view(), name='attendance-by-date'),
####ADMIN PANEL
path('admin-holidays/', HolidayView.as_view()),            # GET, POST
path('admin-holidays/<int:holiday_id>/', HolidayView.as_view()),   # PATCH, DELETE
path('employee/holidays/<str:employee_id>/', EmployeeHolidayAPIView.as_view(), name='employee-holidays'), # GET HOLIDAYS


path('api/disciplinary-cases/', DisciplinaryCasesView.as_view(), name='disciplinary_cases_list'),  #GET,POST
path('api/disciplinary-cases/<int:pk>/', DisciplinaryCasesView.as_view(), name='disciplinary_case_detail'), #UPDATE, DELETE

path('api/leave-applications/', LeaveApplicationAPI.as_view(), name='leave-applications'),
path('api/leave-applications/<int:leave_id>/', LeaveApplicationAPI.as_view(), name='leave-application-detail'),
path('api/leave-types/', LeaveTypeListAPI.as_view(), name='leave-types'),

#### aditya
path('api/division/', DivisionAPI.as_view(), name='division-api'),
path('api/division/<int:division_id>/', DivisionAPI.as_view(), name='division-update-delete'),
# path('api/grade/', GradeAPI.as_view(), name='grade_api'),
# path('api/grade/<int:grade_id>/', GradeAPI.as_view(), name='grade-update-delete'),  # PATCH, DELETE
path('api/grade/', GradeAPI.as_view(), name='grade_api'),
path('api/grade/<int:id>/', GradeAPI.as_view(), name='grade-update-delete'),  # PATCH, DELETE
path('api/company-setup-dashboard/', CompanySetupDashboardAPI.as_view(), name='company_setup_dashboard'),
path('api/headquarters/', HeadquarterAPI.as_view(), name='headquarters_api'),
path('api/headquarters/<int:headquarter_id>/', HeadquarterAPI.as_view(), name='headquarters_detail_api'),
path('api/company-details/', CompanyDetailsAPI.as_view()),
path('api/clients/', ClientAPI.as_view()),
path('api/clients/<int:client_id>/', ClientAPI.as_view()),

####PROJECTS
##ADMIN PROJECT
path('api/projects/', AdminProjectAPI.as_view()),              # GET all or POST new project
path('api/projects/<int:project_id>/', AdminProjectAPI.as_view()),  # PUT & DELETE
path('api/projects/progress-summary/', ProjectProgressCountAPI.as_view()),  # Data of completed , in progress

# Employee  assigned project list
path('api/employee_projects/<str:employee_id>/', EmployeeAssignedProjects.as_view()),
path('api/employee_projects/discussions/<int:project_id>/', AddProjectDiscussion.as_view()),
path('api/employee_projects/attachment/<int:project_id>/', ProjectAttachmentAPI.as_view(), name='upload-attachment'),

####TASK 
path('api/tasks/', TaskAPI.as_view(), name='task_api'),
path('api/tasks/<int:task_id>/', TaskAPI.as_view(), name='task-update-delete'),

path('api/employee_support_tickets/<str:employee_id>/', EmployeeSupportTicketView.as_view(), name='support-tickets'),
path('admin_support_tickets/', AdminSupportTicketView.as_view(), name='admin-support-tickets'),
path('admin_support_tickets/<int:ticket_id>/', AdminSupportTicketView.as_view(), name='admin-support-ticket-detail'),
 

#employee dashboard
path('api/employee-dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
path('api/todos/', TodoAPIView.as_view(), name='employee_todo_dashboard'), # GET all todos or POST new todo
path('api/todos/<int:todo_id>/', TodoAPIView.as_view(), name='todo_update_delete'), #PATCH, 
path('api/dropdown/employee-role/', EmployeeRoleDropdownAPI.as_view(), name='employee-role-dropdown'),

path("empdashboard/<str:employee_id>/", EmpDashApi.as_view(), name="Emp-dash"),


# Employee Event View
path('employee_events/<str:employee_id>/', EmployeeEventView.as_view(), name='employee-events'),
 
# Employee Award view
path('employee_awards/<str:employee_id>/', EmployeeAwardsView.as_view(), name='employee-awards'),
 


path('employee_assets/<str:employee_id>/', EmployeeAssetsView.as_view()),  # GET
path('employee_confirm_asset/<str:pk>/', EmployeeAssetsView.as_view()),  # PATCH  # Confirm a specific asset by asset ID

path('employee-policies/<str:employee_id>/', EmployeePolicyView.as_view(), name='employee-policy-view'),
# Admin My Account
path('my_account/<str:pk>', AdminMyAccountView.as_view(), name='admin-my-account'),

###attendance for  employee
path('my_attendance/<str:empid>/', MyAttendanceAPIView.as_view(), name='my-attendance'),
###employee dropdown---manager wise employee
path('dropdown/<str:empid>/', EmpNameDropdownAPIView.as_view(), name='dropdown-names'),
###monthly report manager wise employee
path('emp_monthly_report/', MonthlyReportView.as_view(), name='monthly-report'),
path('notifications/global/<str:employee_id>/', GlobalNotificationAPIView.as_view(), name='global-notifications'),

####Emp confirmation
path("EmpConfirmation/<str:employee_id>/", EmpConfirmationAPI.as_view(), name="employee-confirmation"),
path('api/exit-type/<int:id>/', ExitEmployeeTypeDropdownView.as_view()),
  
#### Policy Acknowledgement Status
path("policy_ack/<str:emp_id>/", PolicyAcknowledgementStatusView.as_view()),
### Department wise leave report
path('department_leave_report/', DepartmentLeaveReportView.as_view(), name='department-leave-report'),
path("api/employee/<int:user_id>/", EmployeeDetailsAPIView.as_view(), name="employee-details"),
path('api/staffrole/', StaffRoleAPIView.as_view(), name='staffrole'),
path('api/staffrole/<int:role_id>/', StaffRoleAPIView.as_view(), name='staffrole'),

path("api/family-members-user/<int:user_id>/", FamilyMembersAPIView.as_view(), name="family-members-list-create"),# GET, POST
path("api/family-members/<int:family_member_id>/", FamilyMembersAPIView.as_view(), name="family-members-update-delete"), # PATCH, DELETE

path("api/employee/shift/<int:user_id>/", GetEmployeeShiftAPIView.as_view(), name="employee-shift"),

path('approve_resignation_through_mail/<int:resignation_id>/',ApproveResignationThroughMail.as_view()),
path('reject_resignation_through_mail/<int:resignation_id>/',RejectResignationThroughMail.as_view()),

#Employee-Exit------17-09-2025

# path('create_exit_questionneair/', CreateExitQuestionnaire.as_view(),name='create_exit_questionneair'),
# path('get_exit_procedure_feedback/', GetEmployeeExitQuestionneair.as_view(),name='get_exit_procedure_feedback'),
# path('post_exit_procedure_feedback/', SubmitEmployeeFeedbackForm.as_view(),name='post_exit_procedure_feedback'),
# path('view_employeewise_feedback_form/', ViewCompletedFeedbackForm.as_view(),name='view_employeewise_feedback_form'),

path('exit-questionnaire/', ExitQuestionnaireAPIView.as_view(), name='exit-questionnaire'), # GET EMPLOYEE AND HR, POST
path('exit-questionnaire/<int:ques_id>/', ExitQuestionnaireAPIView.as_view(), name='exit-questionnaire-detail'), # DELETE, PATCH
path('post_exit_procedure_feedback/', SubmitEmployeeExitFeedbackForm.as_view(),name='post_exit_procedure_feedback'),# POST
path('view_employeewise_feedback_form/', ViewCompletedFeedbackForm.as_view(),name='view_employeewise_feedback_form'),
path('view_all_employee_feedback_form/', ViewAllCompletedFeedbackForm.as_view(),name='view_allemployee_feedback_form'),

path('hr-assets-dashboard/',HRAssetsDashboard.as_view()),
path('hr-return-approval/<int:pk>/', HRAssetsApprovalDashboard.as_view()),
path('get-exit-date/<str:employee_id>/',GetExitDate.as_view()),
path('resigned-employees-dropdown/', ResignedEmployeesDropdownAPIView.as_view(), name="resigned-employees-dropdown"),
path('confirmation-employees-dropdown/', ConfirmationEmployeesDropdownAPIView.as_view(), name="comfirmation-employee-dropdown"),
path('get-letters/<str:employee_id>/',getletters.as_view()),
path('get-letters/',getletters.as_view()),

# path('exit-questionnaire/', ExitQuestionnaireAPIView.as_view(), name='exit-questionnaire'), # GET EMPLOYEE AND HR, POST
# path('exit-questionnaire/<int:ques_id>/', ExitQuestionnaireAPIView.as_view(), name='exit-questionnaire-detail'), # DELETE, PATCH
# path('post_exit_procedure_feedback/', SubmitEmployeeExitFeedbackForm.as_view(),name='post_exit_procedure_feedback'),# POST
# path('view_employeewise_feedback_form/', ViewCompletedFeedbackForm.as_view(),name='view_employeewise_feedback_form'),
 
# path('hr-assets-dashboard/',HRAssetsDashboard.as_view()),
# path('hr-return-approval/<int:pk>/', HRAssetsApprovalDashboard.as_view()),
# path('get-exit-date/<str:employee_id>/',GetExitDate.as_view()),
# path('resigned-employees-dropdown/', ResignedEmployeesDropdownAPIView.as_view(), name="resigned-employees-dropdown"),
# path('confirmation-employees-dropdown/', ConfirmationEmployeesDropdownAPIView.as_view(), name="comfirmation-employee-dropdown"),
# path('get-letters/<str:employee_id>/',getletters.as_view()),
# path('get-letters/',getletters.as_view()),
path('check-asset-status/<str:employee_id>/',CheckAssetStatus.as_view()),
 
path('get-terminations/', TerminationDashboard.as_view()),# GET ALL
path('post-terminations/', TerminationDashboard.as_view()),#POST
path('update-terminations/<int:pk>/', TerminationDashboard.as_view()),#PATCH
path('pending-terminations/', PendingTerminationList.as_view(), name="pending-terminations"),#GET PENDING
path('send-terminations/', SendTerminationList.as_view(), name="sent-terminations"),# GET SEND
path('Upload-Clearance-Form/<str:employee_id>/', UploadClearanceForm.as_view()),# PATCH
 
path('exit-employee-table1/', ExitEmployeeTable1.as_view()),# GET
path('update-exit-employee-table1/<str:employee_id>/', ExitEmployeeTable1.as_view()),# PATCH
path('exit-employee-table2/', ExitEmployeeTable2.as_view()),# GET
path('update-exit-employee-table2/<str:employee_id>/', ExitEmployeeTable2.as_view()),# PATCH
path('exit-employee-table3/', ExitEmployeeTable3.as_view()),# GET
path('update-exit-employee-table3/<str:employee_id>/', ExitEmployeeTable3.as_view()),# PATCH
path('exit-employee-finaltable/', ExitEmployeeDashboardFinalTable.as_view()),# GET ALL FINAL TABLE DATA
path('hr-exit-employee/', HRExitEmployee.as_view()),
path('upload-sign/<str:employee_id>/', UploadHRSignAPIView.as_view(), name='upload-hr-sign'),#PATCH
path('upload-stamp/<int:company_detail_id>/', UploadCompanyStampAPIView.as_view()), #PATCH
path('data-for-letters/<str:employee_id>/', DataForLetterAPIView.as_view()), #GET
path('get-exit-employee/', GetEmployeeExitView.as_view()), #GET
path('add-new-exit-employee/', AddEmployeeExitView.as_view()), #POST
path('exit-employee/<int:exit_id>/', UpdateEmployeeExitView.as_view()), #UPDATE, DELETE
path('get_designationwise_count/', EmployeeDesignationWiseCount.as_view(), name="get_designationwise_count"),
path('get_gradewise_count/', GradeWiseCount.as_view(), name="get_gradewise_count"),

##### FORGOT PASSWORD
   path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
   path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


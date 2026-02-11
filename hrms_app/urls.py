from django.urls import path, include
from .views.AdminPanel_views import *
from .views.EmployeePanel_views import *
from .views.Dropdown_views import *
# from .views.SQLChatBot import *
from .views.AccountDetails_views import *
from django.conf.urls.static import static
from .views.leave_reports import *
from .views.attendance_report import MonthlyAttendanceReport
from .views.reports import *
from .views.otp_views import SendOTP, VerifyOTP, ResetPassword
from .views.dashboard_views import HRDashboardMetrics, HRDashboardMetricsByMonth
from .views.graph_views import HRDashboardGraphs
from .views.role_views_django import *
from .views.training_views_django import *


# New Joiner Report
# Monthly leave reportpay
urlpatterns = [
    # Chatbot
    # path("sql_chatbot/", SQLChatbotView.as_view(), name="sql_chatbot"),
    # Dropdowns
    path(
        "emp_manager_dropdown/",
        EmployeeManagerDropdown.as_view(),
        name="employee-manger-dropdown",
    ),
    path(
        "desig_dept_dropdown/",
        DesignationDepartmentDropdown.as_view(),
        name="desig-dept-dropdown",
    ),
    path(
        "desig_dept_dropdown/<int:dept_id>/",
        DesignationDepartmentDropdown.as_view(),
        name="desig-dept-dropdown",
    ),
    path(
        "employees_by_designation/",
        EmployeesByDesignation.as_view(),
        name="employees-by-designation",
    ),
    path("designation_dropdown_filter_by_line_manager/", DesignationDropdownFilterByLineManager.as_view(), name="designation-dropdown-filter-by-line-manager"),
    path("ekach_line_manager/", EkachLineManager.as_view(), name="ekach-line-manager"),
    # Account Details
    path("contract_details/", ContractDetails.as_view(), name="contract-details"),
    path(
        "emp_basic_info/",
        EmployeeBasicInformation.as_view(),
        name="employee-basic-info",
    ),
    path("personal_info/", PersonalInformation.as_view(), name="personal-info"),
    path(
        "get_profile_photo/<str:employee_id>/",
        GetProfilePhoto.as_view(),
        name="get-profile-photo",
    ),
    path(
        "update_profile_photo/",
        UpdateProfilePhoto.as_view(),
        name="update-profile-photo",
    ),
    path("account_info/", AccountInformation.as_view(), name="account-info"),
    path("document_details/", DocumentDetails.as_view(), name="document-details"),
    path("change_password/", ChangePassword.as_view(), name="change-password"),
    path("timesheet_agenda/", TimesheetAgenda.as_view(), name="timesheet-agenda"),
    path("leave_statistics/", LeaveStatistics.as_view(), name="leave-statistics"),
    # Employee Panel
    path(
        "dashboard_attendance/<str:employee_id>/",
        DashboardAttendance.as_view(),
        name="dashboard-attendance",
    ),
    path(
        "employee_attendance/", EmployeeAttendance.as_view(), name="employee-attendance"
    ),
    # path("my_attendance/<str:empid>/", MyAttendanceAPIView.as_view(), name="my-attendance"),
    # path("emp_monthly_report/", MonthlyReportView.as_view(), name="emp-monthly-report"),
    path("basic_info/", BasicInformation.as_view(), name="basic-info"),
    path("holiday_list/", HolidayList.as_view(), name="holiday-list"),
    path(
        "project_list/<int:user_id>/<int:type>/",
        ProjectList.as_view(),
        name="project-list",
    ),
    path(
        "project_details/<int:user_id>/",
        ProjectDetails.as_view(),
        name="project-details",
    ),
    path("project_discussion/", ProjectDiscussion.as_view(), name="project-discussion"),
    path(
        "project_attach_file/", ProjectAttachFile.as_view(), name="project-attach-file"
    ),
    path("payroll/<int:user_id>/<int:type>/", Payroll.as_view(), name="payroll"),
    path("policies/", Policies.as_view(), name="policies"),
    # Admin Panel
    # Employees
    path("employee_details/", EmployeeDetails.as_view(), name="employee-details"),
    path(
        "edit_employee/<int:user_id>/", EditEmployee.as_view(), name="edit-employee-get"
    ),
    path("edit_employee/", EditEmployee.as_view(), name="edit-employee-put"),
    path("edit_employee/", EditEmployee.as_view(), name="edit-employee-delete"),
    path("change_manager/", ChangeManager.as_view(), name="change-manager"),
    path(
        "get_max_employee_id/", GetMaxEmployeeId.as_view(), name="get-max-employee-id"
    ),
    path("fetch_documents/", FetchDocuments.as_view(), name="fetch-documents"),
    path(
        "check_existing_email/",
        CheckExistingEmail.as_view(),
        name="check-existing-email",
    ),
    path("add_employee/", AddEmployee.as_view(), name="add-employee"),
    # Roles & privileges
    path("role_list/", RoleList.as_view(), name="role-list-get"),  # GET
    path("role_list/", RoleList.as_view(), name="role-list-put"),  # PUT
    path(
        "role_list/<int:role_id>/", RoleList.as_view(), name="role-list-delete"
    ),  # DELETE
    path("add_role/", AddRole.as_view(), name="add-role"),
    # Shift & Scheduling
    path("office_shift/", OfficeShiftList.as_view(), name="office-shift-get"),
    path("office_shift/", OfficeShiftList.as_view(), name="office-shift-put"),
    path(
        "office_shift/<int:shift_id>/",
        OfficeShiftList.as_view(),
        name="office-shift-delete",
    ),
    path("office_shift/", OfficeShiftList.as_view(), name="office-shift-post"),
    # Attendance Overview
    path(
        "attendance_overview/", AttendanceOverview.as_view(), name="attendance-overview"
    ),
    path(
        "manual_attendance/",
        ManualAttendance.as_view(),
        name="manual-attendance-get/post",
    ),
    path("state_dropdown/", StateDropdown.as_view(), name="state-dropdown"),
    path(
        "employee_hub_dropdown/<int:state_id>/",
        EmployeeHubDropdown.as_view(),
        name="employee-hub-dropdown",
    ),
    path(
        "office_shift_dropdown/<int:employee_hub_id>/<int:state_id>/",
        OfficeShiftDropdown.as_view(),
        name="office-shift-dropdown",
    ),
    # path(
    #     "line_manager_dropdown/",
    #     LineManagerDropdown.as_view(),
    #     name="line-manager-dropdown",
    # ),
    path(
        "employee_hub/", EmployeeHub.as_view(), name="employee-hub-get/post/edit/delete"
    ),
    path("monthly_report/", AttendanceMonthlyReport.as_view(), name="monthly-report"),
    path("holiday/", Holiday.as_view(), name="holiday"),
    path(
        "payroll_setup_configuration/",
        PayrollSetupConfiguration.as_view(),
        name="payroll-setup-configuration",
    ),
    path(
        "payroll_employee_tds/",
        PayrollEmployeeTds.as_view(),
        name="payroll-employee-tds",
    ),
    path(
        "payroll_report/<int:month>/<int:year>/",
        PayrollReport.as_view(),
        name="payroll-report",
    ),
    path(
        "pre_saved_payroll_report/",
        PreSavedPayrollReport.as_view(),
        name="pre-saved-payroll-report",
    ),
    path(
        "save_payroll_report/", SavePayrollReport.as_view(), name="save-payroll-report"
    ),
    path("payment_info/", PaymentInfo.as_view(), name="payment-info"),
    path(
        "update_payment_info/", UpdatePaymentInfo.as_view(), name="update-payment-info"
    ),
    path("salary_structure/", SalaryStructure.as_view(), name="salary_structure"),
    path("payslip_history/", PayslipHistory.as_view(), name="payslip-history"),
    path("payslip/", Payslip.as_view(), name="payslip"),
    # Assets
    path("assets_inventory/", AssetsInventory.as_view(), name="assets-inventory"),
    # RAAS
    path(
        "search_by_email_vet_talent/",
        SearchByEmailVetTalent.as_view(),
        name="search-by-email-vet-talent",
    ),
    path(
        "employee_leave_pattern/",
        EmployeeLeavePattern.as_view(),
        name="employee_leave_pattern",
    ),
    path(
        "attendance/monthly-report/",
        MonthlyAttendanceReport.as_view(),
        name="monthly-report",
    ),
    # Monthly leave report
    path(
        "leave/monthly-report/",
        MonthlyLeaveReport.as_view(),
        name="monthly_leave_report",
    ),
    # Leave balance report
    path(
        "leave/balance-report/",
        LeaveBalanceReport.as_view(),
        name="leave-balance-report",
    ),
    # New Joiner Report
    path("new-joiner-report/", NewJoinerReport.as_view(), name="new-joiner-report"),
    path(
        "manpower-report/",
        AnnualManpowerReportAPIView.as_view(),
        name="annual_manpower_report",
    ),
    path(
        "employee-attrition-report/",
        EmployeeAttritionRateReportAPIView.as_view(),
        name="employee_attrition_report",
    ),
    path(
        "employee_master_report/",
        EmployeeMasterReportAPIView.as_view(),
        name="employee-details",
    ),
    # HR Master Data
    path("hr-master-data/", HRMasterDataAPIView.as_view(), name="hr_master_data"),
    # Employee Exit Report
    path(
        "employee-exit-report/",
        EmployeeExitReportAPIView.as_view(),
        name="employee-exit-report",
    ),
    # Performance Management Report
    path(
        "performance-management-report/",
        PerformanceManagementReportAPIView.as_view(),
        name="performance-management-report",
    ),
    # annual-appraisal-report
    path(
        "annual-appraisal-report/",
        AnnualAppraisalReportAPIView.as_view(),
        name="annual-appraisal-report",
    ),
    path("salary-report/", SalaryReportAPIView.as_view(), name="salary-report"),
    path("pt-report/", PTReportAPIView.as_view(), name="pt_salary_report"),
    # Holiday calendar
    path(
        "holidays/calendar/<int:country_id>/<int:state_id>/<int:employee_hub>/",
        HolidayCalendarView.as_view(),
        name="holiday-calendar",
    ),
    # Notifications
    path("view_notification/", ViewNotification.as_view(), name="view-notification"),
    path("check_phasewise_parameters/", CheckPhasewiseParameter.as_view(), name="check-phasewise-parameters"),
    path("get_employee_details_clearance_form/", GetEmployeeDetailsClearanceForm.as_view(), name="get-employee-details-clearance-form"),

    #Bugs
    path("view_employee_salary_slip/<str:employee_id>/", ViewEmployeeSalarySlip.as_view(), name="view-employee-salary-slip"),
    path("save_hr_revenue_expense/", SaveHrRevenueExpense.as_view(), name="save-hr-revenue-expense"),                   # post, get
    path("save_hr_revenue_expense/<int:hr_rev_exp_id>/", SaveHrRevenueExpense.as_view(), name="save-hr-revenue-expense"),                   # patch
    
    # OTP and Forgot Password APIs
    path("send_otp/", SendOTP.as_view(), name="send-otp"),
    path("verify_otp/", VerifyOTP.as_view(), name="verify-otp"),
    path("reset_password/", ResetPassword.as_view(), name="reset-password"),
    
    # HR Dashboard Metrics APIs
    path("hr_dashboard_metrics/", HRDashboardMetrics.as_view(), name="hr-dashboard-metrics"),
    path("hr_dashboard_metrics_by_month/", HRDashboardMetricsByMonth.as_view(), name="hr-dashboard-metrics-by-month"),
    
    # HR Dashboard Graphs API
    path("hr_dashboard_graphs/", HRDashboardGraphs.as_view(), name="hr-dashboard-graphs"),




    ###  From the PHP HRMS ###

    # ==========================================
    # ROLE MANAGEMENT APIs
    # ==========================================
    
    # Permission Check APIs (GET methods)
    path('roles/user-permissions/', UserRolePermissionsAPIView.as_view(), name='user-permissions'),
    path('roles/user-permissions/<int:user_id>/', UserRolePermissionsAPIView.as_view(), name='user-permissions-by-id'),
    path('roles/check-permission/', CheckPermissionAPIView.as_view(), name='check-permission'),
    path('roles/check-multiple-permissions/', CheckMultiplePermissionsAPIView.as_view(), name='check-multiple-permissions'),
    
    # Role CRUD APIs
    path('roles/create/', RoleCreateAPIView.as_view(), name='role-create'),
    path('roles/update/', RoleUpdateAPIView.as_view(), name='role-update'),
    path('roles/delete/<int:role_id>/', RoleDeleteAPIView.as_view(), name='role-delete'),
    path('roles/list/', RoleListAPIView.as_view(), name='role-list'),
    
    # ==========================================
    # TRAINING MANAGEMENT APIs
    # ==========================================
    
    # Training CRUD APIs
    path('training/create/', TrainingCreateAPIView.as_view(), name='training-create'),
    path('training/update/', TrainingUpdateAPIView.as_view(), name='training-update'),
    path('training/delete/<int:training_id>/', TrainingDeleteAPIView.as_view(), name='training-delete'),
    path('training/list/', TrainingListAPIView.as_view(), name='training-list'),
    path('training/details/<int:training_id>/', TrainingDetailsAPIView.as_view(), name='training-details'),
    path('training/update-status/', TrainingUpdateStatusAPIView.as_view(), name='training-update-status'),
    
    # ==========================================
    # MALAYSIAN STATUTORY COMPLIANCE & PAYROLL
    # ==========================================
    path('my/', include('hrms_app.malaysia.urls', namespace='malaysia')),
]

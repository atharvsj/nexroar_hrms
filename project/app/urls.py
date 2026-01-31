from django.urls import path
from .views import *
from .views import (
    CIProjectFileListView,
    CIProjectBugListView,
    TaskDiscussionAPIView,
    TaskView,
    TaskNoteView,
    TaskFileView,
    CiStaffRoleView,
    OfficeShiftView,
)
from .views import (
    ApplyLeave,
    BasicInfo,
    ChangePassword,
    LoginView,
    MonthlyAttendence,
    OnDutyInRequest,
    RegistrationView,
    TodayAttendance,
    ErpUserCreateView,
    CiEmployeeExitView,
)
from .views import (
    DepartmentView,
    AnnouncementListCreateView,
    AnnouncementDetailView,
    CiDesignationViewSet,
    CIPolicyView,
)
from .views import (
    CiBiomatricDataListCreateView,
    CiBiomatricDataRetrieveUpdateDeleteView,
    CIPunchReportView,
    ContractOptionAPIView,
    BasicInformationListAPIView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("add_leave/", ApplyLeave.as_view(), name="add_leave"),
    path("basic-info/", BasicInfo.as_view(), name="basic_info"),
    path("change-password/", ChangePassword.as_view(), name="change_password"),
    path("today-attendence/", TodayAttendance.as_view(), name="Today_Attendence"),
    path("monthly-attendence/", MonthlyAttendence.as_view(), name="monthly_attendence"),
    path("on-duty-request/", OnDutyInRequest.as_view(), name="on_duty_request"),
    path(
        "ci_projects_files/", CIProjectFileListView.as_view(), name="ci-projects-files"
    ),
    path(
        "ci_projects_files/<int:project_file_id>/",
        CIProjectFileListView.as_view(),
        name="ci-project-files",
    ),
    path("ci_projects_bugs/", CIProjectBugListView.as_view(), name="project_bugs"),
    path(
        "ci_projects_bugs/<int:project_bug_id>/",
        CIProjectBugListView.as_view(),
        name="project_bug_detail",
    ),
    path(
        "tasks/", TaskView.as_view(), name="task-list-create"
    ),  # For GET (list all tasks) and POST (create task)
    path(
        "tasks/<int:task_id>/", TaskView.as_view(), name="task-detail"
    ),  # For GET, PATCH, DELETE specific task
    path("task-discussions/", TaskDiscussionAPIView.as_view(), name="task_discussions"),
    path(
        "task-files/", TaskFileView.as_view(), name="task_files_list"
    ),  # For POST and GET (all task files)
    path(
        "task-files/<int:task_file_id>/",
        TaskFileView.as_view(),
        name="task_file_detail",
    ),  # For GET (specific task file), PATCH, and DELETE
    path(
        "task-notes/", TaskNoteView.as_view(), name="task-note-list-create"
    ),  # List all or create new
    path(
        "task-notes/<int:task_note_id>/",
        TaskNoteView.as_view(),
        name="task-note-detail",
    ),  # Get, update, delete
    path("create_user/", ErpUserCreateView.as_view(), name="create_user"),
    # roles& privileges  ,Shifts, ExitEmployee
    path("roles/", CiStaffRoleView.as_view(), name="ci_staff_roles"),
    path("roles/<int:role_id>/", CiStaffRoleView.as_view(), name="ci_staff_roles"),
    path(
        "shifts/", OfficeShiftView.as_view(), name="ci_office_shifts"
    ),  # For GET and POST
    path(
        "shifts/<int:office_shift_id>/",
        OfficeShiftView.as_view(),
        name="delete_office_shift",
    ),  # For DELETE
    path(
        "employee-exit/", CiEmployeeExitView.as_view(), name="employee_exit_list_create"
    ),
    path(
        "employee-exit/<int:pk>/",
        CiEmployeeExitView.as_view(),
        name="employee_exit_delete",
    ),
    path(
        "announcements/",
        AnnouncementListCreateView.as_view(),
        name="announcement-list-create",
    ),
    path(
        "announcements/<int:announcement_id>/",
        AnnouncementDetailView.as_view(),
        name="announcement-detail",
    ),
    path("departments/", DepartmentView.as_view(), name="department_list"),
    path("departments/<int:pk>/", DepartmentView.as_view(), name="department-detail"),
    path(
        "biometric/",
        CiBiomatricDataListCreateView.as_view(),
        name="biometric-list-create",
    ),
    path(
        "biometric/<int:ci_biomatric_id>/",
        CiBiomatricDataRetrieveUpdateDeleteView.as_view(),
        name="biometric-detail",
    ),
    # Designation - Core HR
    # path('ci_designations/', CiDesignationViewSet.as_view(), name='ci_designations_list'),
    # path('ci_designations/<int:pk>/', CiDesignationViewSet.as_view(), name='ci_designations_detail'),
    path("policies/", CIPolicyView.as_view(), name="get_create_policy"),
    path("policies/<int:pk>/", CIPolicyView.as_view(), name="update_delete_policy"),
    # employee
    path(
        "employee-contracts/",
        ContractOptionAPIView.as_view(),
        name="employee-contracts",
    ),
    path(
        "basic-info/", BasicInformationListAPIView.as_view(), name="basic-info-list"
    ),  # GET all
    path(
        "basic-info/<int:id>/",
        BasicInformationListAPIView.as_view(),
        name="basic-info-detail",
    ),  # GET/UPDATE one
    path("basic_info/", BasicInformation.as_view(), name="basic-info"),
    # path("personal_info/", PersonalInformation.as_view(), name="personal-info"),
    path("punch_reports/", CIPunchReportView.as_view(), name="punch-in"),
    path("my_projects/", My_projectView.as_view(), name="my-project"),  # get
    path(
        "my_projects/<int:project_file_id>/",
        My_projectView.as_view(),
        name="my-project-detail",
    ),  # del & patch
    path("assigned_tasks/", AssignedTaskListView.as_view(), name="assigned-task-list"),
    path(
        "assigned_tasks/<int:task_id>/",
        AssignedTaskDetailView.as_view(),
        name="assigned-task-detail",
    ),
    path("events/", EventViewSet.as_view(), name="events"),
    path("events/<int:event_id>/", EventViewSet.as_view(), name="event_delete"),
    path("holidays/", HolidayViewSet.as_view(), name="holiday_list"),
    path("holidays/<int:holiday_id>/", HolidayViewSet.as_view(), name="holiday_detail"),
    # Travel
    path("travels/", CITravelAPIView.as_view(), name="travel-list"),
    path("travels/<int:travel_id>/", CITravelAPIView.as_view(), name="travel-detail"),
    path(
        "announcements/",
        AnnouncementListCreateView.as_view(),
        name="announcement-list-create",
    ),
    path(
        "announcements/<int:announcement_id>/",
        AnnouncementDetailView.as_view(),
        name="announcement-detail",
    ),
    path("policies/", CIPolicyView.as_view(), name="get_create_policy"),
    path("policies/<int:pk>/", CIPolicyView.as_view(), name="update_delete_policy"),
]

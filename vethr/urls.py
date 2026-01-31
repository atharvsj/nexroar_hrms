from django.urls import path
 
from vethr.views import ApplyLeaveAPIView, EmployeeLeaveBalanceAPIView, EmployeeLeavehistoryAPIView, SandwichRuleCheckAPIView, LeaveListByEmployeeAPIView,LineManagerApprovalAPIView
 
urlpatterns = [
   
        path('leave-balance/', EmployeeLeaveBalanceAPIView.as_view(), name='leave-balance'),
        path('apply-leave/', ApplyLeaveAPIView.as_view(), name='apply-leave'),
        path('employee-leaves-list/', LeaveListByEmployeeAPIView.as_view(), name='employee-leave-list'),
        path('leave-details/', EmployeeLeavehistoryAPIView.as_view(), name='leave-balance'),
        path('line-manager-approval/', LineManagerApprovalAPIView.as_view(), name="line-manager-approval"),   # GET all requests
        path('line-manager-approval/<int:leave_id>/', LineManagerApprovalAPIView.as_view(), name="line-manager-approval-update"),  # PATCH specific leave
        path('sandwich-rule-check/', SandwichRuleCheckAPIView.as_view(), name='sandwich-rule-check'),
 
 
 
 
]
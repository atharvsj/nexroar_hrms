from django.urls import path
from .views import *

urlpatterns = [
    path('confirmation_parameter/', ConfirmationParameter.as_view(),name='confirmation_parameter'),
    # path('save_phaseone_data/', SavePhase1APIView.as_view(),name='save_phaseone_data'),
    path('save_phasewise_data/', SavePhasewiseAPIView.as_view(),name='save_phasewise_data'),
    path('final_confirmation_action/', EmployeeConfirmationUpdate.as_view(),name='final_confirmation_action'),
    path('employee_confirmation_dashboard/', GetEmployeeConfimationDash.as_view(),name='employee_confirmation_dashboard'),
    
    # 10-07-2025
    path('save_Desigwise_parameters/', SavedesignationwiseParameters.as_view(),name='save_Desigwise_parameters'),
    path('get_desigwise_tabledata/', GetDesignationwiseTableData.as_view(),name='get_desigwise_tabledata'),
    path('delete_desigwise_para/<int:pk>/', DeleteDesigwiseParameter.as_view(),name='delete_desigwise_para'),
    path('get_employee_performance/<int:role_id>/<int:user_id>/', GetEmployeePerformanceTable.as_view(),name='get_employee_performance'),
    
# Live Done 
    
   


    path('get_employee_overall_phasewise/', GetEmployeeOverAllPhaseWiseMarks.as_view(),name='get_employee_overall_phasewise'),
    path('save_employee_overall_analysis/', SaveEmployeeOverallAnalysis.as_view(),name='save_employee_overall_analysis'),
    path('get_employee_leave_request_report/', EmployeeLeaveRequestGetReport.as_view(),name='get_employee_leave_request_report'),
    path('get_employee_type_five_details/', GetEmployeeTypeFiveDetails.as_view(),name='get_employee_type_five_details'),
    path('get_employee_daily_attendence_get_report/', EmployeeDailyAttendanceGetReport.as_view(),name='get_employee_daily_attendence_get_report'),
    path('get_employee_monthly_check_in_check_out_get_report/', EmployeeMonthlycheckINCheckOUTGetReport.as_view(),name='get_employee_monthly_check_in_check_out_get_report'),
    path('get_all_employee_leave_summary_get_report/', AllEmployeeLeaveSummaryReportGetReport.as_view(),name='get_all_employee_leave_summary_get_report'),
    path('get_employee_confirmation_get_report/', EmployeeConfirmationReportGetReport.as_view(),name='get_employee_confirmation_get_report'),
 
    path('get_employee_pip_report_get_report/', EmployeePIPReportGetReport.as_view(),name='get_employee_pip_report_get_report'),
 
    path('get_employee_promotion_get_report/', EmployeePromotionGetReport.as_view(),name='get_employee_promotion_get_report'),
    path('get_employee_gratuity_eligibility_get_report/', GratuityEligibilityGetReport.as_view(),name='get_employee_promotion_get_report'),
    path('get_employee_pf_get_report/', PFReportEmployeeGetReport.as_view(),name='get_employee_pf_get_report'),
    path('get_employee_payroll_salary_report/', EmployeePayrollSalaryGetReport.as_view(),name='get_employee_payroll_salary_report'),
    path('get_promotion_report_employee_drop/', GetEmployeesByDeptAndDesigPromotionReport.as_view(),name='get_promotion_report_employee_drop'),
    path('save_and_freeze_leave_setup/', SaveFreezeLeaveSetupYearWise.as_view(),name='save_and_freeze_leave_setup'),
    
    path('add_new_asset_to_stock/', AddNewAssetsToStock.as_view(),name='add_new_asset_to_stock'),
    path('update_delete_category/', UpdateDeleteCategoryAPIView.as_view(),name='update_delete_category'),
    
    path('create_edit_product/', CreateProductAPI.as_view(),name='create_edit_product'),
    path('create_edit_product/', CreateProductAPI.as_view(),name='create_edit_product'),
    path("get_phasewise_data/<int:user_id>/", GetPhasewiseData.as_view(), name="get-phase-wise-data"),
    
    path('get_available_qty/', GetAvailableProQty.as_view(),name='get_available_qty'),
    path('get_metrics_form_data/', GetMetricsFormData.as_view(),name='get_metrics_form_data'),
    path('get_assets_instock_data/', GetAssetsInstockTableAPI.as_view(),name='get_assets_instock_data'),

    
    
]

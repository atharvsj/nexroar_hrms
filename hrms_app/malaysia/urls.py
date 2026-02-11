"""
Malaysian Payroll URL Configuration
====================================
URL patterns for Malaysian statutory compliance APIs.
"""

from django.urls import path
from .views import (
    # Company Configuration
    CompanyStatutoryConfigView,
    
    # Employee Details
    EmployeeMalaysianDetailsView,
    EmployeeMalaysianDetailsListView,
    EmployeeTaxProfileView,
    
    # Allowance & Deduction Types
    AllowanceTypesView,
    DeductionTypesView,
    
    # Employee Allowances & Deductions
    EmployeeAllowancesView,
    EmployeeDeductionsView,
    
    # Payroll Processing
    PayrollProcessView,
    PayrollReportView,
    PayrollApproveView,
    PayslipView,
    
    # Statutory Files
    EPFFormAView,
    EPFGIROView,
    SOCSO8AView,
    EISFileView,
    CP39View,
    EAFormView,
    CP8DView,
    CP38View,
    HRDFLevyView,
    BankGIROView,
    StatutoryFileLogView,
    
    # CP38 Orders & TP3 Records
    CP38OrdersView,
    TP3RecordsView,
    
    # Foreign Workers
    ForeignWorkerExpiryView,
    ForeignWorkerListView,
    
    # Statutory Rates
    EPFRatesView,
    SOCSORatesView,
    EISRatesView,
    PCBTaxBracketsView,
)

app_name = 'malaysia'

urlpatterns = [
    # ==========================================================================
    # COMPANY STATUTORY CONFIGURATION
    # ==========================================================================
    path('company-config/<int:company_id>/', CompanyStatutoryConfigView.as_view(), name='company_config_detail'),
    path('company-config/', CompanyStatutoryConfigView.as_view(), name='company_config_save'),
    
    # ==========================================================================
    # EMPLOYEE MALAYSIAN DETAILS
    # ==========================================================================
    path('employee-details/<int:employee_id>/', EmployeeMalaysianDetailsView.as_view(), name='employee_details'),
    path('employee-details/', EmployeeMalaysianDetailsView.as_view(), name='employee_details_save'),
    path('employees/<int:company_id>/', EmployeeMalaysianDetailsListView.as_view(), name='employees_list'),
    
    # ==========================================================================
    # EMPLOYEE TAX PROFILE
    # ==========================================================================
    path('tax-profile/<int:employee_id>/<int:tax_year>/', EmployeeTaxProfileView.as_view(), name='tax_profile'),
    path('tax-profile/', EmployeeTaxProfileView.as_view(), name='tax_profile_save'),
    
    # ==========================================================================
    # ALLOWANCE & DEDUCTION TYPES
    # ==========================================================================
    path('allowance-types/', AllowanceTypesView.as_view(), name='allowance_types'),
    path('deduction-types/', DeductionTypesView.as_view(), name='deduction_types'),
    
    # ==========================================================================
    # EMPLOYEE ALLOWANCES & DEDUCTIONS
    # ==========================================================================
    path('employee-allowances/<int:employee_id>/<int:month>/<int:year>/', EmployeeAllowancesView.as_view(), name='employee_allowances'),
    path('employee-allowances/', EmployeeAllowancesView.as_view(), name='employee_allowances_save'),
    path('employee-deductions/<int:employee_id>/<int:month>/<int:year>/', EmployeeDeductionsView.as_view(), name='employee_deductions'),
    path('employee-deductions/', EmployeeDeductionsView.as_view(), name='employee_deductions_save'),
    
    # ==========================================================================
    # PAYROLL PROCESSING
    # ==========================================================================
    path('payroll/process/<int:company_id>/<int:month>/<int:year>/', PayrollProcessView.as_view(), name='payroll_process'),
    path('payroll/save/', PayrollProcessView.as_view(), name='payroll_save'),
    path('payroll/report/<int:company_id>/<int:month>/<int:year>/', PayrollReportView.as_view(), name='payroll_report'),
    path('payroll/approve/<int:company_id>/<int:month>/<int:year>/', PayrollApproveView.as_view(), name='payroll_approve'),
    path('payslip/<int:employee_id>/<int:month>/<int:year>/', PayslipView.as_view(), name='payslip'),
    
    # ==========================================================================
    # STATUTORY FILE GENERATION
    # ==========================================================================
    # EPF Files
    path('statutory/epf-form-a/', EPFFormAView.as_view(), name='epf_form_a'),
    path('statutory/epf-giro/', EPFGIROView.as_view(), name='epf_giro'),
    
    # SOCSO Files
    path('statutory/socso-8a/', SOCSO8AView.as_view(), name='socso_8a'),
    
    # EIS Files
    path('statutory/eis/', EISFileView.as_view(), name='eis_file'),
    
    # LHDN (Tax) Files
    path('statutory/cp39/', CP39View.as_view(), name='cp39'),
    path('statutory/ea-form/<int:employee_id>/<int:year>/', EAFormView.as_view(), name='ea_form'),
    path('statutory/cp8d/', CP8DView.as_view(), name='cp8d'),
    path('statutory/cp38/', CP38View.as_view(), name='cp38'),
    
    # HRDF Files
    path('statutory/hrdf-levy/', HRDFLevyView.as_view(), name='hrdf_levy'),
    
    # Bank GIRO
    path('statutory/bank-giro/', BankGIROView.as_view(), name='bank_giro'),
    
    # File Generation Log
    path('statutory/file-log/<int:company_id>/', StatutoryFileLogView.as_view(), name='file_log'),
    
    # ==========================================================================
    # CP38 ORDERS & TP3 RECORDS
    # ==========================================================================
    path('cp38-orders/<int:employee_id>/', CP38OrdersView.as_view(), name='cp38_orders'),
    path('cp38-orders/', CP38OrdersView.as_view(), name='cp38_orders_save'),
    path('tp3-records/<int:employee_id>/<int:tax_year>/', TP3RecordsView.as_view(), name='tp3_records'),
    path('tp3-records/', TP3RecordsView.as_view(), name='tp3_records_save'),
    
    # ==========================================================================
    # FOREIGN WORKER MANAGEMENT
    # ==========================================================================
    path('foreign-workers/expiry/<int:company_id>/', ForeignWorkerExpiryView.as_view(), name='foreign_worker_expiry'),
    path('foreign-workers/<int:company_id>/', ForeignWorkerListView.as_view(), name='foreign_workers_list'),
    
    # ==========================================================================
    # STATUTORY RATES MANAGEMENT
    # ==========================================================================
    path('rates/epf/', EPFRatesView.as_view(), name='epf_rates'),
    path('rates/epf/<int:rate_id>/', EPFRatesView.as_view(), name='epf_rates_delete'),
    path('rates/socso/', SOCSORatesView.as_view(), name='socso_rates'),
    path('rates/eis/', EISRatesView.as_view(), name='eis_rates'),
    path('rates/pcb/<int:tax_year>/', PCBTaxBracketsView.as_view(), name='pcb_tax_brackets'),
    path('rates/pcb/', PCBTaxBracketsView.as_view(), name='pcb_tax_brackets_save'),
]

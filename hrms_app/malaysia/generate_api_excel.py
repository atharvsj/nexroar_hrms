"""
Generate Excel documentation for Malaysian Payroll APIs
"""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Malaysian Payroll APIs"

# Define styles
header_font = Font(bold=True, color="FFFFFF", size=11)
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
cell_alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

# Headers
headers = ["Sr.No", "Purpose of API", "API Name", "URL", "Method", "Request Payload", "Response"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_alignment
    cell.border = thin_border

# API Data
apis = [
    # Company Configuration
    {
        "purpose": "Get company statutory configuration (EPF/SOCSO/EIS/LHDN registration numbers)",
        "name": "CompanyStatutoryConfigView (GET)",
        "url": "/hrms/my/company-config/{company_id}/",
        "method": "GET",
        "payload": "None (Path parameter: company_id)",
        "response": '{"status": "success", "data": {"config_id": 1, "company_id": 1, "epf_enabled": true, "epf_employer_no": "12345678901234", "socso_enabled": true, "socso_employer_no": "B3902056910M", "eis_enabled": true, "lhdn_enabled": true, "lhdn_e_number": "E9152876608", "hrdf_enabled": true, "hrdf_registration_no": "123456", "hrdf_levy_rate": 0.01}}'
    },
    {
        "purpose": "Create or update company statutory configuration",
        "name": "CompanyStatutoryConfigView (POST)",
        "url": "/hrms/my/company-config/",
        "method": "POST",
        "payload": '{"company_id": 1, "epf_enabled": true, "epf_employer_no": "12345678901234", "socso_enabled": true, "socso_employer_no": "B3902056910M", "eis_enabled": true, "lhdn_enabled": true, "lhdn_e_number": "E9152876608", "hrdf_enabled": true, "hrdf_registration_no": "123456", "hrdf_levy_rate": 0.01}',
        "response": '{"status": "success", "message": "Configuration saved successfully"}'
    },
    
    # Employee Details
    {
        "purpose": "Get Malaysian employee details (IC, EPF/SOCSO numbers, bank info)",
        "name": "EmployeeMalaysianDetailsView (GET)",
        "url": "/hrms/my/employee-details/{employee_id}/",
        "method": "GET",
        "payload": "None (Path parameter: employee_id)",
        "response": '{"status": "success", "data": {"my_employee_id": 1, "employee_id": 123, "ic_number": "901231145678", "epf_member_no": "12345678", "socso_member_no": "12345678901234", "tax_reference_no": "SG12345678901", "worker_type": "local", "nationality": "Malaysian", "bank_code": "MBB", "bank_account_no": "164012345678"}}'
    },
    {
        "purpose": "Create or update Malaysian employee details",
        "name": "EmployeeMalaysianDetailsView (POST)",
        "url": "/hrms/my/employee-details/",
        "method": "POST",
        "payload": '{"employee_id": 123, "user_id": 456, "ic_number": "901231145678", "tax_reference_no": "SG12345678901", "epf_member_no": "12345678", "socso_member_no": "12345678901234", "worker_type": "local", "nationality": "Malaysian", "residency_status": "resident", "epf_contribution_type": "full", "socso_category": "category_1", "bank_code": "MBB", "bank_name": "Maybank", "bank_account_no": "164012345678"}',
        "response": '{"status": "success", "message": "Employee details saved successfully"}'
    },
    {
        "purpose": "List all employees with Malaysian details for a company",
        "name": "EmployeeMalaysianDetailsListView",
        "url": "/hrms/my/employees/{company_id}/",
        "method": "GET",
        "payload": "None (Path parameter: company_id)",
        "response": '{"status": "success", "data": [{"my_employee_id": 1, "employee_id": 123, "employee_name": "John Doe", "ic_number": "901231145678", "epf_member_no": "12345678", "worker_type": "local", "is_active": 1}]}'
    },
    
    # Tax Profile
    {
        "purpose": "Get employee tax profile for PCB calculation (reliefs, deductions)",
        "name": "EmployeeTaxProfileView (GET)",
        "url": "/hrms/my/tax-profile/{employee_id}/{tax_year}/",
        "method": "GET",
        "payload": "None (Path parameters: employee_id, tax_year)",
        "response": '{"status": "success", "data": {"profile_id": 1, "employee_id": 123, "tax_year": 2026, "marital_status": "married", "spouse_working": false, "number_of_children": 2, "children_studying_higher": 1, "life_insurance": 3000, "medical_insurance": 2500}}'
    },
    {
        "purpose": "Create or update employee tax profile",
        "name": "EmployeeTaxProfileView (POST)",
        "url": "/hrms/my/tax-profile/",
        "method": "POST",
        "payload": '{"employee_id": 123, "tax_year": 2026, "marital_status": "married", "spouse_working": false, "number_of_children": 2, "children_studying_higher": 1, "disabled_self": false, "life_insurance": 3000, "medical_insurance": 2500, "sspn_deposit": 1000, "zakat_paid": 500}',
        "response": '{"status": "success", "message": "Tax profile saved successfully"}'
    },
    
    # Allowance & Deduction Types
    {
        "purpose": "List all allowance types (with taxable/EPF/SOCSO flags)",
        "name": "AllowanceTypesView (GET)",
        "url": "/hrms/my/allowance-types/?company_id=1",
        "method": "GET",
        "payload": "Query param: company_id (optional)",
        "response": '{"status": "success", "data": [{"allowance_type_id": 1, "allowance_code": "TRVL", "allowance_name": "Travel Allowance", "is_taxable": true, "epf_applicable": true, "socso_applicable": true, "eis_applicable": true}]}'
    },
    {
        "purpose": "Create new allowance type",
        "name": "AllowanceTypesView (POST)",
        "url": "/hrms/my/allowance-types/",
        "method": "POST",
        "payload": '{"company_id": 1, "allowance_code": "PARK", "allowance_name": "Parking Allowance", "is_taxable": true, "epf_applicable": true, "socso_applicable": true, "eis_applicable": true, "description": "Monthly parking allowance"}',
        "response": '{"status": "success", "message": "Allowance type created successfully"}'
    },
    {
        "purpose": "List all deduction types",
        "name": "DeductionTypesView (GET)",
        "url": "/hrms/my/deduction-types/?company_id=1",
        "method": "GET",
        "payload": "Query param: company_id (optional)",
        "response": '{"status": "success", "data": [{"deduction_type_id": 1, "deduction_code": "ZKAT", "deduction_name": "Zakat", "is_statutory": false, "affects_pcb": true}]}'
    },
    {
        "purpose": "Create new deduction type",
        "name": "DeductionTypesView (POST)",
        "url": "/hrms/my/deduction-types/",
        "method": "POST",
        "payload": '{"company_id": 1, "deduction_code": "UNON", "deduction_name": "Union Fees", "is_statutory": false, "affects_pcb": false, "description": "Monthly union membership fees"}',
        "response": '{"status": "success", "message": "Deduction type created successfully"}'
    },
    
    # Employee Allowances & Deductions
    {
        "purpose": "Get employee allowances for a specific month",
        "name": "EmployeeAllowancesView (GET)",
        "url": "/hrms/my/employee-allowances/{employee_id}/{month}/{year}/",
        "method": "GET",
        "payload": "None (Path parameters: employee_id, month, year)",
        "response": '{"status": "success", "data": [{"allowance_id": 1, "allowance_type_id": 1, "allowance_name": "Travel Allowance", "amount": 500.00, "remarks": "Monthly travel"}]}'
    },
    {
        "purpose": "Save employee allowance for a month",
        "name": "EmployeeAllowancesView (POST)",
        "url": "/hrms/my/employee-allowances/",
        "method": "POST",
        "payload": '{"employee_id": 123, "allowance_type_id": 1, "month": 2, "year": 2026, "amount": 500.00, "remarks": "Monthly travel allowance"}',
        "response": '{"status": "success", "message": "Allowance saved successfully"}'
    },
    {
        "purpose": "Get employee deductions for a specific month",
        "name": "EmployeeDeductionsView (GET)",
        "url": "/hrms/my/employee-deductions/{employee_id}/{month}/{year}/",
        "method": "GET",
        "payload": "None (Path parameters: employee_id, month, year)",
        "response": '{"status": "success", "data": [{"deduction_id": 1, "deduction_type_id": 1, "deduction_name": "Zakat", "amount": 100.00, "remarks": "Monthly zakat"}]}'
    },
    {
        "purpose": "Save employee deduction for a month",
        "name": "EmployeeDeductionsView (POST)",
        "url": "/hrms/my/employee-deductions/",
        "method": "POST",
        "payload": '{"employee_id": 123, "deduction_type_id": 1, "month": 2, "year": 2026, "amount": 100.00, "remarks": "Monthly zakat deduction"}',
        "response": '{"status": "success", "message": "Deduction saved successfully"}'
    },
    
    # Payroll Processing
    {
        "purpose": "Calculate payroll for all employees (preview mode - not saved)",
        "name": "PayrollProcessView (GET)",
        "url": "/hrms/my/payroll/process/{company_id}/{month}/{year}/",
        "method": "GET",
        "payload": "None (Path parameters: company_id, month, year)",
        "response": '{"status": "success", "data": [{"employee_id": 123, "employee_name": "John Doe", "basic_salary": 5000, "gross_salary": 5500, "epf_employee": 550, "epf_employer": 715, "socso_employee": 19.75, "socso_employer": 69.05, "eis_employee": 9.90, "eis_employer": 9.90, "pcb_amount": 120, "net_pay": 4800.35}], "summary": {"total_employees": 10, "total_gross": 55000, "total_net_pay": 48000}}'
    },
    {
        "purpose": "Save calculated payroll to database",
        "name": "PayrollProcessView (POST)",
        "url": "/hrms/my/payroll/save/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026, "status": "calculated", "payroll_data": [{"employee_id": 123, "employee_name": "John Doe", "basic_salary": 5000, "gross_salary": 5500, "epf_employee": 550, "epf_employer": 715, "socso_employee": 19.75, "socso_employer": 69.05, "eis_employee": 9.90, "eis_employer": 9.90, "pcb_amount": 120, "net_pay": 4800.35}]}',
        "response": '{"status": "success", "message": "Payroll saved for 10 employees"}'
    },
    {
        "purpose": "Get saved payroll report for a period",
        "name": "PayrollReportView",
        "url": "/hrms/my/payroll/report/{company_id}/{month}/{year}/",
        "method": "GET",
        "payload": "None (Path parameters: company_id, month, year)",
        "response": '{"status": "success", "data": [...], "summary": {"total_employees": 10, "total_gross": 55000, "total_net_pay": 48000, "total_epf_employee": 5500, "total_epf_employer": 7150, "total_pcb": 1200}}'
    },
    {
        "purpose": "Approve payroll for a period (changes status to approved)",
        "name": "PayrollApproveView",
        "url": "/hrms/my/payroll/approve/{company_id}/{month}/{year}/",
        "method": "POST",
        "payload": "None (Path parameters: company_id, month, year)",
        "response": '{"status": "success", "message": "Approved payroll for 10 employees"}'
    },
    {
        "purpose": "Get individual employee payslip with breakdown",
        "name": "PayslipView",
        "url": "/hrms/my/payslip/{employee_id}/{month}/{year}/",
        "method": "GET",
        "payload": "None (Path parameters: employee_id, month, year)",
        "response": '{"status": "success", "data": {"employee_name": "John Doe", "ic_number": "901231145678", "earnings": [{"description": "Basic Salary", "amount": 5000}], "deductions": [{"description": "EPF (11%)", "amount": 550}], "total_earnings": 5500, "total_deductions": 699.65, "net_pay": 4800.35, "ytd_gross": 11000, "ytd_epf": 1100, "ytd_pcb": 240}}'
    },
    
    # Statutory Files - EPF
    {
        "purpose": "Generate EPF Form A text file for upload to i-Akaun",
        "name": "EPFFormAView",
        "url": "/hrms/my/statutory/epf-form-a/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026}',
        "response": "File download: EPF_FORMA_202602.txt (pipe-delimited text file)"
    },
    {
        "purpose": "Generate EPF GIRO bank payment file",
        "name": "EPFGIROView",
        "url": "/hrms/my/statutory/epf-giro/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026, "bank_code": "MBB", "payment_date": "2026-02-15"}',
        "response": "File download: EPF_GIRO_202602.txt"
    },
    
    # Statutory Files - SOCSO
    {
        "purpose": "Generate SOCSO Form 8A text file for ASSIST portal",
        "name": "SOCSO8AView",
        "url": "/hrms/my/statutory/socso-8a/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026}',
        "response": "File download: SOCSO_8A_202602.txt (pipe-delimited text file)"
    },
    
    # Statutory Files - EIS
    {
        "purpose": "Generate EIS contribution file for ASSIST portal",
        "name": "EISFileView",
        "url": "/hrms/my/statutory/eis/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026}',
        "response": "File download: EIS_202602.txt (pipe-delimited text file)"
    },
    
    # Statutory Files - LHDN
    {
        "purpose": "Generate CP39 PCB deduction file for e-PCB portal",
        "name": "CP39View",
        "url": "/hrms/my/statutory/cp39/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026}',
        "response": "File download: CP39_202602.txt (pipe-delimited text file)"
    },
    {
        "purpose": "Generate EA Form PDF for individual employee",
        "name": "EAFormView",
        "url": "/hrms/my/statutory/ea-form/{employee_id}/{year}/",
        "method": "GET",
        "payload": "None (Path parameters: employee_id, year)",
        "response": "File download: EA_FORM_123_2025.pdf (PDF file)"
    },
    {
        "purpose": "Generate CP8D annual submission file for e-Filing",
        "name": "CP8DView",
        "url": "/hrms/my/statutory/cp8d/",
        "method": "POST",
        "payload": '{"company_id": 1, "year": 2025}',
        "response": "File download: CP8D_2025.txt (pipe-delimited text file)"
    },
    {
        "purpose": "Generate CP38 salary deduction order file",
        "name": "CP38View",
        "url": "/hrms/my/statutory/cp38/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026}',
        "response": "File download: CP38_202602.txt"
    },
    
    # Statutory Files - HRDF
    {
        "purpose": "Generate HRDF levy file",
        "name": "HRDFLevyView",
        "url": "/hrms/my/statutory/hrdf-levy/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026}',
        "response": "File download: HRDF_LEVY_202602.txt"
    },
    
    # Bank GIRO
    {
        "purpose": "Generate Bank GIRO salary payment file",
        "name": "BankGIROView",
        "url": "/hrms/my/statutory/bank-giro/",
        "method": "POST",
        "payload": '{"company_id": 1, "month": 2, "year": 2026, "bank_code": "MBB", "payment_date": "2026-02-25", "source_account": "164012345678"}',
        "response": "File download: BANK_GIRO_MBB_202602.txt"
    },
    
    # File Log
    {
        "purpose": "View statutory file generation history/audit log",
        "name": "StatutoryFileLogView",
        "url": "/hrms/my/statutory/file-log/{company_id}/?file_type=EPF_FORM_A&year=2026",
        "method": "GET",
        "payload": "Query params: file_type (optional), year (optional)",
        "response": '{"status": "success", "data": [{"log_id": 1, "file_type": "EPF_FORM_A", "file_name": "EPF_FORMA_202602.txt", "record_count": 50, "status": "generated", "created_at": "2026-02-10 10:30:00"}]}'
    },
    
    # CP38 Orders & TP3 Records
    {
        "purpose": "Get CP38 salary deduction orders for employee",
        "name": "CP38OrdersView (GET)",
        "url": "/hrms/my/cp38-orders/{employee_id}/",
        "method": "GET",
        "payload": "None (Path parameter: employee_id)",
        "response": '{"status": "success", "data": [{"order_id": 1, "lhdn_reference": "CP38/2026/001", "order_date": "2026-01-15", "monthly_amount": 200.00, "balance_amount": 2400.00}]}'
    },
    {
        "purpose": "Create CP38 salary deduction order",
        "name": "CP38OrdersView (POST)",
        "url": "/hrms/my/cp38-orders/",
        "method": "POST",
        "payload": '{"employee_id": 123, "lhdn_reference": "CP38/2026/001", "order_date": "2026-01-15", "start_month": 2, "start_year": 2026, "monthly_amount": 200.00, "total_amount": 2400.00, "remarks": "Tax arrears"}',
        "response": '{"status": "success", "message": "CP38 order created successfully"}'
    },
    {
        "purpose": "Get TP3 previous employment records for PCB calculation",
        "name": "TP3RecordsView (GET)",
        "url": "/hrms/my/tp3-records/{employee_id}/{tax_year}/",
        "method": "GET",
        "payload": "None (Path parameters: employee_id, tax_year)",
        "response": '{"status": "success", "data": [{"record_id": 1, "previous_employer_name": "ABC Sdn Bhd", "gross_remuneration": 25000.00, "epf_contribution": 2750.00, "pcb_deducted": 500.00}]}'
    },
    {
        "purpose": "Create TP3 previous employment record",
        "name": "TP3RecordsView (POST)",
        "url": "/hrms/my/tp3-records/",
        "method": "POST",
        "payload": '{"employee_id": 123, "tax_year": 2026, "previous_employer_name": "ABC Sdn Bhd", "previous_employer_e_number": "E1234567890", "employment_start_date": "2025-01-01", "employment_end_date": "2025-12-31", "gross_remuneration": 25000.00, "epf_contribution": 2750.00, "pcb_deducted": 500.00, "zakat_paid": 100.00}',
        "response": '{"status": "success", "message": "TP3 record created successfully"}'
    },
    
    # Foreign Workers
    {
        "purpose": "Get expiring foreign worker documents (work permit, visa, FOMEMA)",
        "name": "ForeignWorkerExpiryView",
        "url": "/hrms/my/foreign-workers/expiry/{company_id}/?days=30",
        "method": "GET",
        "payload": "Query param: days (threshold for expiry alert, default 30)",
        "response": '{"status": "success", "data": [{"employee_id": 123, "employee_name": "Worker Name", "worker_type": "foreign", "work_permit_expiry": "2026-03-15", "days_to_work_permit_expiry": 32, "visa_expiry": "2026-04-01", "days_to_visa_expiry": 49}], "threshold_days": 30}'
    },
    {
        "purpose": "List all foreign workers with their details",
        "name": "ForeignWorkerListView",
        "url": "/hrms/my/foreign-workers/{company_id}/",
        "method": "GET",
        "payload": "None (Path parameter: company_id)",
        "response": '{"status": "success", "data": [{"employee_id": 123, "employee_name": "Worker Name", "worker_type": "foreign", "nationality": "Indonesian", "passport_number": "A12345678", "work_permit_number": "WP123456", "work_permit_expiry": "2026-12-31"}]}'
    },
    
    # Statutory Rates
    {
        "purpose": "Get all EPF contribution rates",
        "name": "EPFRatesView (GET)",
        "url": "/hrms/my/rates/epf/",
        "method": "GET",
        "payload": "None",
        "response": '{"status": "success", "data": [{"rate_id": 1, "wage_from": 0, "wage_to": 30, "employee_rate": 11, "employer_rate_below_5k": 13, "employer_rate_above_5k": 12, "is_active": 1}]}'
    },
    {
        "purpose": "Add or update EPF contribution rate",
        "name": "EPFRatesView (POST)",
        "url": "/hrms/my/rates/epf/",
        "method": "POST",
        "payload": '{"wage_from": 0, "wage_to": 30, "employee_rate": 11, "employer_rate_below_5k": 13, "employer_rate_above_5k": 12, "is_active": true}',
        "response": '{"status": "success", "message": "EPF rate saved successfully"}'
    },
    {
        "purpose": "Deactivate EPF rate",
        "name": "EPFRatesView (DELETE)",
        "url": "/hrms/my/rates/epf/{rate_id}/",
        "method": "DELETE",
        "payload": "None (Path parameter: rate_id)",
        "response": '{"status": "success", "message": "Rate deactivated"}'
    },
    {
        "purpose": "Get all SOCSO contribution rates",
        "name": "SOCSORatesView (GET)",
        "url": "/hrms/my/rates/socso/",
        "method": "GET",
        "payload": "None",
        "response": '{"status": "success", "data": [{"rate_id": 1, "category": "category_1", "wage_from": 30, "wage_to": 50, "employee_rate": 0.10, "employer_rate": 0.20, "is_active": 1}]}'
    },
    {
        "purpose": "Add or update SOCSO contribution rate",
        "name": "SOCSORatesView (POST)",
        "url": "/hrms/my/rates/socso/",
        "method": "POST",
        "payload": '{"category": "category_1", "wage_from": 30, "wage_to": 50, "employee_rate": 0.10, "employer_rate": 0.20, "is_active": true}',
        "response": '{"status": "success", "message": "SOCSO rate saved successfully"}'
    },
    {
        "purpose": "Get all EIS contribution rates",
        "name": "EISRatesView (GET)",
        "url": "/hrms/my/rates/eis/",
        "method": "GET",
        "payload": "None",
        "response": '{"status": "success", "data": [{"rate_id": 1, "wage_from": 0, "wage_to": 30, "employee_rate": 0.2, "employer_rate": 0.2, "is_active": 1}]}'
    },
    {
        "purpose": "Add or update EIS contribution rate",
        "name": "EISRatesView (POST)",
        "url": "/hrms/my/rates/eis/",
        "method": "POST",
        "payload": '{"wage_from": 0, "wage_to": 30, "employee_rate": 0.2, "employer_rate": 0.2, "is_active": true}',
        "response": '{"status": "success", "message": "EIS rate saved successfully"}'
    },
    {
        "purpose": "Get PCB tax brackets for a specific year",
        "name": "PCBTaxBracketsView (GET)",
        "url": "/hrms/my/rates/pcb/{tax_year}/",
        "method": "GET",
        "payload": "None (Path parameter: tax_year)",
        "response": '{"status": "success", "data": [{"bracket_id": 1, "tax_year": 2026, "income_from": 0, "income_to": 5000, "tax_rate": 0, "cumulative_tax": 0}]}'
    },
    {
        "purpose": "Add or update PCB tax bracket",
        "name": "PCBTaxBracketsView (POST)",
        "url": "/hrms/my/rates/pcb/",
        "method": "POST",
        "payload": '{"tax_year": 2026, "income_from": 0, "income_to": 5000, "tax_rate": 0, "cumulative_tax": 0, "is_active": true}',
        "response": '{"status": "success", "message": "Tax bracket saved successfully"}'
    },
    
    # Bulk Import
    {
        "purpose": "Bulk import multiple employees with Malaysian details",
        "name": "BulkEmployeeImportView",
        "url": "/hrms/my/bulk-import/employees/",
        "method": "POST",
        "payload": '{"employees": [{"employee_id": 123, "user_id": 456, "ic_number": "901231145678", "epf_member_no": "12345678", "socso_member_no": "12345678901234", "worker_type": "local", "bank_code": "MBB", "bank_account_no": "164012345678"}, {"employee_id": 124, "user_id": 457, "ic_number": "851015086542", "worker_type": "foreign", "passport_number": "A12345678", "work_permit_expiry": "2026-12-31"}]}',
        "response": '{"status": "success", "message": "Processed 2 of 2 employees", "results": {"success": [{"index": 0, "employee_id": 123, "action": "created"}], "failed": [], "total": 2}}'
    },
    {
        "purpose": "Bulk import employee tax profiles for a year",
        "name": "BulkTaxProfileImportView",
        "url": "/hrms/my/bulk-import/tax-profiles/",
        "method": "POST",
        "payload": '{"tax_year": 2026, "profiles": [{"employee_id": 123, "marital_status": "married", "spouse_working": false, "number_of_children": 2, "life_insurance": 3000}, {"employee_id": 124, "marital_status": "single", "number_of_children": 0}]}',
        "response": '{"status": "success", "message": "Processed 2 of 2 profiles", "results": {"success": [{"index": 0, "employee_id": 123}, {"index": 1, "employee_id": 124}], "failed": [], "total": 2}}'
    },
    {
        "purpose": "Bulk import statutory rates (EPF/SOCSO/EIS/PCB)",
        "name": "BulkRatesImportView",
        "url": "/hrms/my/bulk-import/rates/",
        "method": "POST",
        "payload": '{"rate_type": "pcb", "tax_year": 2027, "rates": [{"income_from": 0, "income_to": 5000, "tax_rate": 0, "cumulative_tax": 0}, {"income_from": 5001, "income_to": 20000, "tax_rate": 1, "cumulative_tax": 0}, {"income_from": 20001, "income_to": 35000, "tax_rate": 3, "cumulative_tax": 150}]}',
        "response": '{"status": "success", "message": "Imported 3 of 3 PCB rates", "results": {"success": 3, "failed": [], "total": 3}}'
    },
    
    # Email Alerts
    {
        "purpose": "Preview expiring foreign worker documents (without sending email)",
        "name": "DocumentExpiryEmailAlertView (GET)",
        "url": "/hrms/my/alerts/document-expiry/{company_id}/?days=30",
        "method": "GET",
        "payload": "Query param: days (threshold, default 30)",
        "response": '{"status": "success", "threshold_days": 30, "summary": {"total_expiring": 5, "expired": 1, "critical_7_days": 2, "warning_14_days": 2}, "hr_recipients": [{"email": "hr@company.com", "name": "HR Manager"}], "expiring_documents": [...]}'
    },
    {
        "purpose": "Send email alerts for expiring documents to HR",
        "name": "DocumentExpiryEmailAlertView (POST)",
        "url": "/hrms/my/alerts/document-expiry/{company_id}/",
        "method": "POST",
        "payload": '{"days": 30, "send_to_employees": false, "custom_recipients": ["manager@company.com"]}',
        "response": '{"status": "success", "message": "Sent 3 email alerts", "emails_sent": 3, "recipients": ["hr@company.com", "admin@company.com", "manager@company.com"], "documents_flagged": 5}'
    },
    {
        "purpose": "Scheduled alert for all companies (for cron job)",
        "name": "ScheduledExpiryAlertView",
        "url": "/hrms/my/alerts/scheduled-expiry/",
        "method": "POST",
        "payload": "None (processes all companies)",
        "response": '{"status": "success", "message": "Processed 3 companies", "results": [{"company_id": 1, "status": "success", "emails_sent": 2}]}'
    },
]

# Write data
for idx, api in enumerate(apis, 1):
    row = idx + 1
    ws.cell(row=row, column=1, value=idx).alignment = cell_alignment
    ws.cell(row=row, column=1).border = thin_border
    
    ws.cell(row=row, column=2, value=api["purpose"]).alignment = cell_alignment
    ws.cell(row=row, column=2).border = thin_border
    
    ws.cell(row=row, column=3, value=api["name"]).alignment = cell_alignment
    ws.cell(row=row, column=3).border = thin_border
    
    ws.cell(row=row, column=4, value=api["url"]).alignment = cell_alignment
    ws.cell(row=row, column=4).border = thin_border
    
    ws.cell(row=row, column=5, value=api["method"]).alignment = cell_alignment
    ws.cell(row=row, column=5).border = thin_border
    
    ws.cell(row=row, column=6, value=api["payload"]).alignment = cell_alignment
    ws.cell(row=row, column=6).border = thin_border
    
    ws.cell(row=row, column=7, value=api["response"]).alignment = cell_alignment
    ws.cell(row=row, column=7).border = thin_border

# Set column widths
column_widths = [8, 50, 35, 55, 10, 80, 100]
for col, width in enumerate(column_widths, 1):
    ws.column_dimensions[get_column_letter(col)].width = width

# Set row height for header
ws.row_dimensions[1].height = 30

# Freeze header row
ws.freeze_panes = 'A2'

# Save workbook
output_path = r"d:\nexroar_hrms_new\hrms_app\malaysia\MALAYSIAN_PAYROLL_API_DOCUMENTATION.xlsx"
wb.save(output_path)
print(f"Excel file created successfully: {output_path}")
print(f"Total APIs documented: {len(apis)}")

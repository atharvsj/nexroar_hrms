"""
Malaysian Payroll Serializers
=============================
Serializers for request/response validation
"""

from rest_framework import serializers
from decimal import Decimal


class CompanyStatutoryConfigSerializer(serializers.Serializer):
    """Serializer for company statutory configuration"""
    company_id = serializers.IntegerField(required=True)
    epf_enabled = serializers.BooleanField(default=True)
    epf_employer_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
    socso_enabled = serializers.BooleanField(default=True)
    socso_employer_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
    eis_enabled = serializers.BooleanField(default=True)
    lhdn_enabled = serializers.BooleanField(default=True)
    lhdn_e_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    hrdf_enabled = serializers.BooleanField(default=False)
    hrdf_registration_no = serializers.CharField(max_length=50, required=False, allow_blank=True)
    hrdf_levy_rate = serializers.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0100'))


class EmployeeMalaysianDetailsSerializer(serializers.Serializer):
    """Serializer for Malaysian employee details"""
    employee_id = serializers.CharField(max_length=20, required=True)
    user_id = serializers.IntegerField(required=True)
    ic_number = serializers.CharField(max_length=14, required=False, allow_blank=True)
    passport_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    passport_expiry = serializers.DateField(required=False, allow_null=True)
    tax_reference_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
    epf_member_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
    socso_member_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
    eis_member_no = serializers.CharField(max_length=20, required=False, allow_blank=True)
    nationality = serializers.CharField(max_length=50, default='Malaysian')
    residency_status = serializers.ChoiceField(choices=['resident', 'non_resident'], default='resident')
    worker_type = serializers.ChoiceField(choices=['local', 'foreign', 'expat', 'pr'], default='local')
    epf_contribution_type = serializers.ChoiceField(choices=['full', 'optional', 'exempt'], default='full')
    socso_category = serializers.ChoiceField(choices=['category_1', 'category_2'], default='category_1')
    
    # Foreign worker fields
    work_permit_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    work_permit_expiry = serializers.DateField(required=False, allow_null=True)
    visa_type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    visa_expiry = serializers.DateField(required=False, allow_null=True)
    fomema_date = serializers.DateField(required=False, allow_null=True)
    fomema_expiry = serializers.DateField(required=False, allow_null=True)
    levy_payment_type = serializers.ChoiceField(choices=['company', 'employee', 'shared'], default='company')
    levy_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    
    # Bank details
    bank_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    bank_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    bank_account_no = serializers.CharField(max_length=30, required=False, allow_blank=True)
    bank_swift_code = serializers.CharField(max_length=20, required=False, allow_blank=True)


class EmployeeTaxProfileSerializer(serializers.Serializer):
    """Serializer for employee tax profile (PCB reliefs)"""
    employee_id = serializers.CharField(max_length=20, required=True)
    tax_year = serializers.IntegerField(required=True)
    marital_status = serializers.ChoiceField(choices=['single', 'married'], default='single')
    spouse_working = serializers.BooleanField(default=False)
    spouse_disabled = serializers.BooleanField(default=False)
    number_of_children = serializers.IntegerField(default=0, min_value=0)
    children_studying_higher = serializers.IntegerField(default=0, min_value=0)
    children_disabled = serializers.IntegerField(default=0, min_value=0)
    disabled_self = serializers.BooleanField(default=False)
    epf_additional = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    life_insurance = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    education_insurance = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    medical_insurance = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    sspn_deposit = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    zakat_paid = serializers.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))


class AllowanceTypeSerializer(serializers.Serializer):
    """Serializer for allowance type configuration"""
    allowance_type_id = serializers.IntegerField(read_only=True)
    company_id = serializers.IntegerField(required=False, allow_null=True)
    allowance_code = serializers.CharField(max_length=10, required=True)
    allowance_name = serializers.CharField(max_length=100, required=True)
    is_taxable = serializers.BooleanField(default=True)
    epf_applicable = serializers.BooleanField(default=True)
    socso_applicable = serializers.BooleanField(default=True)
    eis_applicable = serializers.BooleanField(default=True)
    description = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)


class DeductionTypeSerializer(serializers.Serializer):
    """Serializer for deduction type configuration"""
    deduction_type_id = serializers.IntegerField(read_only=True)
    company_id = serializers.IntegerField(required=False, allow_null=True)
    deduction_code = serializers.CharField(max_length=10, required=True)
    deduction_name = serializers.CharField(max_length=100, required=True)
    is_statutory = serializers.BooleanField(default=False)
    affects_pcb = serializers.BooleanField(default=False)
    description = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)


class EmployeeAllowanceSerializer(serializers.Serializer):
    """Serializer for employee monthly allowance"""
    allowance_id = serializers.IntegerField(read_only=True)
    employee_id = serializers.CharField(max_length=20, required=True)
    allowance_type_id = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


class EmployeeDeductionSerializer(serializers.Serializer):
    """Serializer for employee monthly deduction"""
    deduction_id = serializers.IntegerField(read_only=True)
    employee_id = serializers.CharField(max_length=20, required=True)
    deduction_type_id = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


class PayrollProcessRequestSerializer(serializers.Serializer):
    """Serializer for payroll processing request"""
    company_id = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True)
    employee_ids = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=False,
        allow_empty=True
    )


class PayrollSaveRequestSerializer(serializers.Serializer):
    """Serializer for saving processed payroll"""
    company_id = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True)
    payroll_data = serializers.ListField(required=True)
    status = serializers.ChoiceField(choices=['draft', 'calculated', 'approved', 'paid'], default='calculated')


class StatutoryFileRequestSerializer(serializers.Serializer):
    """Serializer for statutory file generation request"""
    company_id = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True)


class EPFGIRORequestSerializer(serializers.Serializer):
    """Serializer for EPF GIRO file request"""
    company_id = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True)
    bank_code = serializers.CharField(max_length=20, required=True)
    payment_date = serializers.CharField(max_length=8, required=True)  # YYYYMMDD


class BankGIRORequestSerializer(serializers.Serializer):
    """Serializer for Bank GIRO salary payment file"""
    company_id = serializers.IntegerField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True)
    bank_code = serializers.CharField(max_length=20, required=True)
    payment_date = serializers.CharField(max_length=8, required=True)
    source_account = serializers.CharField(max_length=20, required=True)


class EAFormRequestSerializer(serializers.Serializer):
    """Serializer for EA Form generation request"""
    employee_id = serializers.CharField(max_length=20, required=True)
    year = serializers.IntegerField(required=True)


class CP38OrderSerializer(serializers.Serializer):
    """Serializer for CP38 salary deduction order"""
    employee_id = serializers.CharField(max_length=20, required=True)
    lhdn_reference = serializers.CharField(max_length=50, required=True)
    order_date = serializers.DateField(required=True)
    start_month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    start_year = serializers.IntegerField(required=True)
    end_month = serializers.IntegerField(required=False, allow_null=True)
    end_year = serializers.IntegerField(required=False, allow_null=True)
    monthly_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


class TP3RecordSerializer(serializers.Serializer):
    """Serializer for TP3 (previous employment) record"""
    employee_id = serializers.CharField(max_length=20, required=True)
    tax_year = serializers.IntegerField(required=True)
    previous_employer_name = serializers.CharField(max_length=200, required=True)
    previous_employer_e_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    employment_start_date = serializers.DateField(required=False, allow_null=True)
    employment_end_date = serializers.DateField(required=False, allow_null=True)
    gross_remuneration = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)
    epf_contribution = serializers.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    pcb_deducted = serializers.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    zakat_paid = serializers.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    cp38_deducted = serializers.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))


class ForeignWorkerExpirySerializer(serializers.Serializer):
    """Serializer for foreign worker document expiry tracking"""
    employee_id = serializers.CharField(max_length=20)
    employee_name = serializers.CharField(max_length=200)
    worker_type = serializers.CharField(max_length=20)
    work_permit_expiry = serializers.DateField(allow_null=True)
    visa_expiry = serializers.DateField(allow_null=True)
    fomema_expiry = serializers.DateField(allow_null=True)
    days_to_work_permit_expiry = serializers.IntegerField(allow_null=True)
    days_to_visa_expiry = serializers.IntegerField(allow_null=True)
    days_to_fomema_expiry = serializers.IntegerField(allow_null=True)


class StatutoryRateSerializer(serializers.Serializer):
    """Generic serializer for statutory rate table entries"""
    rate_id = serializers.IntegerField(read_only=True)
    wage_from = serializers.DecimalField(max_digits=12, decimal_places=2)
    wage_to = serializers.DecimalField(max_digits=12, decimal_places=2)
    employee_share = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    employer_share = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(required=False, allow_null=True)
    is_active = serializers.BooleanField(default=True)


class PCBTaxBracketSerializer(serializers.Serializer):
    """Serializer for PCB tax brackets"""
    bracket_id = serializers.IntegerField(read_only=True)
    tax_year = serializers.IntegerField(required=True)
    income_from = serializers.DecimalField(max_digits=15, decimal_places=2)
    income_to = serializers.DecimalField(max_digits=15, decimal_places=2)
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    cumulative_tax = serializers.DecimalField(max_digits=15, decimal_places=2)
    is_active = serializers.BooleanField(default=True)


class StatutoryFileLogSerializer(serializers.Serializer):
    """Serializer for statutory file generation log"""
    log_id = serializers.IntegerField(read_only=True)
    file_type = serializers.CharField(max_length=50)
    company_id = serializers.IntegerField()
    month = serializers.IntegerField(allow_null=True)
    year = serializers.IntegerField()
    file_name = serializers.CharField(max_length=255)
    record_count = serializers.IntegerField()
    total_employee_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_employer_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField(max_length=20)
    created_at = serializers.DateTimeField()


class PayrollReportResponseSerializer(serializers.Serializer):
    """Serializer for payroll report response"""
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    ic_number = serializers.CharField(allow_blank=True, allow_null=True)
    department_name = serializers.CharField(allow_blank=True, allow_null=True)
    designation_name = serializers.CharField(allow_blank=True, allow_null=True)
    
    # Earnings
    basic_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    fixed_allowances = serializers.DecimalField(max_digits=12, decimal_places=2)
    variable_allowances = serializers.DecimalField(max_digits=12, decimal_places=2)
    overtime_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    bonus = serializers.DecimalField(max_digits=12, decimal_places=2)
    gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Statutory Deductions
    epf_employee = serializers.DecimalField(max_digits=12, decimal_places=2)
    epf_employer = serializers.DecimalField(max_digits=12, decimal_places=2)
    socso_employee = serializers.DecimalField(max_digits=12, decimal_places=2)
    socso_employer = serializers.DecimalField(max_digits=12, decimal_places=2)
    eis_employee = serializers.DecimalField(max_digits=12, decimal_places=2)
    eis_employer = serializers.DecimalField(max_digits=12, decimal_places=2)
    pcb_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    pcb_bonus = serializers.DecimalField(max_digits=12, decimal_places=2)
    hrdf_levy = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Other Deductions
    zakat = serializers.DecimalField(max_digits=12, decimal_places=2)
    loan_deduction = serializers.DecimalField(max_digits=12, decimal_places=2)
    other_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Totals
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_employer_contribution = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_pay = serializers.DecimalField(max_digits=12, decimal_places=2)


class PayslipResponseSerializer(serializers.Serializer):
    """Serializer for payslip response"""
    # Company Info
    company_name = serializers.CharField()
    company_address = serializers.CharField(allow_blank=True)
    epf_employer_no = serializers.CharField(allow_blank=True)
    socso_employer_no = serializers.CharField(allow_blank=True)
    
    # Employee Info
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    ic_number = serializers.CharField(allow_blank=True)
    epf_member_no = serializers.CharField(allow_blank=True)
    socso_member_no = serializers.CharField(allow_blank=True)
    tax_reference_no = serializers.CharField(allow_blank=True)
    department = serializers.CharField(allow_blank=True)
    designation = serializers.CharField(allow_blank=True)
    bank_name = serializers.CharField(allow_blank=True)
    bank_account_no = serializers.CharField(allow_blank=True)
    
    # Pay Period
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    pay_date = serializers.DateField(allow_null=True)
    
    # Earnings
    earnings = serializers.ListField(child=serializers.DictField())
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Deductions
    deductions = serializers.ListField(child=serializers.DictField())
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Employer Contributions
    employer_contributions = serializers.ListField(child=serializers.DictField())
    total_employer_contributions = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Net Pay
    net_pay = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # YTD
    ytd_gross = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    ytd_epf = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    ytd_pcb = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)

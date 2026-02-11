"""
Malaysian Statutory Constants and Rate Tables
==============================================
Contains EPF, SOCSO, EIS rates and PCB tax brackets as per 2024/2025 regulations.
These rates should be updated when statutory bodies announce changes.
"""

from decimal import Decimal

# =============================================================================
# STATUTORY BODY CODES
# =============================================================================

STATUTORY_BODIES = {
    'EPF': 'KWSP',      # Employees Provident Fund
    'SOCSO': 'PERKESO', # Social Security Organization
    'EIS': 'EIS',       # Employment Insurance System
    'LHDN': 'LHDN',     # Inland Revenue Board (PCB/MTD)
    'HRDF': 'PSMB',     # Human Resources Development Fund
}

# =============================================================================
# EPF (KWSP) RATES - Effective 2024
# =============================================================================

EPF_RATES = {
    # Employee contribution rates
    'employee_below_60': Decimal('11.00'),      # 11% for employees below 60
    'employee_60_and_above': Decimal('5.50'),   # 5.5% for employees 60 and above (optional)
    
    # Employer contribution rates
    'employer_wages_5000_below': Decimal('13.00'),  # 13% for wages <= RM5,000
    'employer_wages_above_5000': Decimal('12.00'),  # 12% for wages > RM5,000
    
    # Wage ceiling
    'wage_ceiling': Decimal('20000.00'),  # Maximum wages subject to EPF
    'threshold_5000': Decimal('5000.00'),  # Threshold for employer rate differentiation
}

# EPF Contribution Table (Third Schedule) - Selected ranges
# Full table should be loaded from database
EPF_CONTRIBUTION_TABLE = [
    # (wage_from, wage_to, employee_contribution, employer_contribution_below_5k, employer_contribution_above_5k)
    (Decimal('10.00'), Decimal('20.00'), Decimal('2.00'), Decimal('3.00'), Decimal('2.00')),
    (Decimal('20.01'), Decimal('40.00'), Decimal('4.00'), Decimal('5.00'), Decimal('5.00')),
    (Decimal('40.01'), Decimal('60.00'), Decimal('7.00'), Decimal('8.00'), Decimal('7.00')),
    (Decimal('60.01'), Decimal('80.00'), Decimal('9.00'), Decimal('10.00'), Decimal('10.00')),
    (Decimal('80.01'), Decimal('100.00'), Decimal('11.00'), Decimal('13.00'), Decimal('12.00')),
    # ... continues - Full table loaded from database
]

# =============================================================================
# SOCSO (PERKESO) RATES - 2024
# =============================================================================

SOCSO_CATEGORIES = {
    'CATEGORY_1': 'Employment Injury & Invalidity',  # Below 60 years
    'CATEGORY_2': 'Employment Injury Only',           # 60 years and above
}

# SOCSO wage ceiling
SOCSO_WAGE_CEILING = Decimal('5000.00')

# SOCSO Contribution Table - First Category (Employment Injury & Invalidity Pension)
# Full table should be loaded from database
SOCSO_CONTRIBUTION_TABLE_CAT1 = [
    # (wage_from, wage_to, employee_contribution, employer_contribution)
    (Decimal('30.00'), Decimal('50.00'), Decimal('0.10'), Decimal('0.20')),
    (Decimal('50.01'), Decimal('70.00'), Decimal('0.15'), Decimal('0.30')),
    (Decimal('70.01'), Decimal('100.00'), Decimal('0.25'), Decimal('0.45')),
    (Decimal('100.01'), Decimal('140.00'), Decimal('0.35'), Decimal('0.65')),
    (Decimal('140.01'), Decimal('200.00'), Decimal('0.50'), Decimal('0.90')),
    (Decimal('200.01'), Decimal('300.00'), Decimal('0.70'), Decimal('1.25')),
    (Decimal('300.01'), Decimal('400.00'), Decimal('0.95'), Decimal('1.65')),
    (Decimal('400.01'), Decimal('500.00'), Decimal('1.15'), Decimal('2.05')),
    (Decimal('500.01'), Decimal('600.00'), Decimal('1.35'), Decimal('2.45')),
    (Decimal('600.01'), Decimal('700.00'), Decimal('1.55'), Decimal('2.85')),
    (Decimal('700.01'), Decimal('800.00'), Decimal('1.75'), Decimal('3.25')),
    (Decimal('800.01'), Decimal('900.00'), Decimal('1.95'), Decimal('3.65')),
    (Decimal('900.01'), Decimal('1000.00'), Decimal('2.15'), Decimal('4.05')),
    (Decimal('1000.01'), Decimal('1100.00'), Decimal('2.35'), Decimal('4.45')),
    (Decimal('1100.01'), Decimal('1200.00'), Decimal('2.55'), Decimal('4.85')),
    (Decimal('1200.01'), Decimal('1300.00'), Decimal('2.75'), Decimal('5.25')),
    (Decimal('1300.01'), Decimal('1400.00'), Decimal('2.95'), Decimal('5.65')),
    (Decimal('1400.01'), Decimal('1500.00'), Decimal('3.15'), Decimal('6.05')),
    (Decimal('1500.01'), Decimal('1600.00'), Decimal('3.35'), Decimal('6.45')),
    (Decimal('1600.01'), Decimal('1700.00'), Decimal('3.55'), Decimal('6.85')),
    (Decimal('1700.01'), Decimal('1800.00'), Decimal('3.75'), Decimal('7.25')),
    (Decimal('1800.01'), Decimal('1900.00'), Decimal('3.95'), Decimal('7.65')),
    (Decimal('1900.01'), Decimal('2000.00'), Decimal('4.15'), Decimal('8.05')),
    (Decimal('2000.01'), Decimal('2100.00'), Decimal('4.35'), Decimal('8.45')),
    (Decimal('2100.01'), Decimal('2200.00'), Decimal('4.55'), Decimal('8.85')),
    (Decimal('2200.01'), Decimal('2300.00'), Decimal('4.75'), Decimal('9.25')),
    (Decimal('2300.01'), Decimal('2400.00'), Decimal('4.95'), Decimal('9.65')),
    (Decimal('2400.01'), Decimal('2500.00'), Decimal('5.15'), Decimal('10.05')),
    (Decimal('2500.01'), Decimal('2600.00'), Decimal('5.35'), Decimal('10.45')),
    (Decimal('2600.01'), Decimal('2700.00'), Decimal('5.55'), Decimal('10.85')),
    (Decimal('2700.01'), Decimal('2800.00'), Decimal('5.75'), Decimal('11.25')),
    (Decimal('2800.01'), Decimal('2900.00'), Decimal('5.95'), Decimal('11.65')),
    (Decimal('2900.01'), Decimal('3000.00'), Decimal('6.15'), Decimal('12.05')),
    (Decimal('3000.01'), Decimal('3100.00'), Decimal('6.35'), Decimal('12.45')),
    (Decimal('3100.01'), Decimal('3200.00'), Decimal('6.55'), Decimal('12.85')),
    (Decimal('3200.01'), Decimal('3300.00'), Decimal('6.75'), Decimal('13.25')),
    (Decimal('3300.01'), Decimal('3400.00'), Decimal('6.95'), Decimal('13.65')),
    (Decimal('3400.01'), Decimal('3500.00'), Decimal('7.15'), Decimal('14.05')),
    (Decimal('3500.01'), Decimal('3600.00'), Decimal('7.35'), Decimal('14.45')),
    (Decimal('3600.01'), Decimal('3700.00'), Decimal('7.55'), Decimal('14.85')),
    (Decimal('3700.01'), Decimal('3800.00'), Decimal('7.75'), Decimal('15.25')),
    (Decimal('3800.01'), Decimal('3900.00'), Decimal('7.95'), Decimal('15.65')),
    (Decimal('3900.01'), Decimal('4000.00'), Decimal('8.15'), Decimal('16.05')),
    (Decimal('4000.01'), Decimal('5000.00'), Decimal('9.75'), Decimal('19.25')),
]

# SOCSO Contribution Table - Second Category (Employment Injury Only - Age 60+)
SOCSO_CONTRIBUTION_TABLE_CAT2 = [
    # (wage_from, wage_to, employer_contribution_only)
    (Decimal('30.00'), Decimal('50.00'), Decimal('0.10')),
    (Decimal('50.01'), Decimal('70.00'), Decimal('0.15')),
    (Decimal('70.01'), Decimal('100.00'), Decimal('0.20')),
    # ... continues
]

# =============================================================================
# EIS RATES - 2024
# =============================================================================

EIS_RATES = {
    'employee_rate': Decimal('0.20'),  # 0.2%
    'employer_rate': Decimal('0.20'),  # 0.2%
    'wage_ceiling': Decimal('5000.00'),  # Maximum insurable earnings
    'max_age': 57,  # Not applicable for 57+ (can register up to 60 if started before 57)
}

# EIS Contribution Table
EIS_CONTRIBUTION_TABLE = [
    # (wage_from, wage_to, employee_contribution, employer_contribution)
    (Decimal('30.00'), Decimal('50.00'), Decimal('0.10'), Decimal('0.10')),
    (Decimal('50.01'), Decimal('70.00'), Decimal('0.10'), Decimal('0.10')),
    (Decimal('70.01'), Decimal('100.00'), Decimal('0.20'), Decimal('0.20')),
    (Decimal('100.01'), Decimal('140.00'), Decimal('0.25'), Decimal('0.25')),
    (Decimal('140.01'), Decimal('200.00'), Decimal('0.35'), Decimal('0.35')),
    (Decimal('200.01'), Decimal('300.00'), Decimal('0.50'), Decimal('0.50')),
    (Decimal('300.01'), Decimal('400.00'), Decimal('0.70'), Decimal('0.70')),
    (Decimal('400.01'), Decimal('500.00'), Decimal('0.90'), Decimal('0.90')),
    (Decimal('500.01'), Decimal('600.00'), Decimal('1.10'), Decimal('1.10')),
    (Decimal('600.01'), Decimal('700.00'), Decimal('1.30'), Decimal('1.30')),
    (Decimal('700.01'), Decimal('800.00'), Decimal('1.50'), Decimal('1.50')),
    (Decimal('800.01'), Decimal('900.00'), Decimal('1.70'), Decimal('1.70')),
    (Decimal('900.01'), Decimal('1000.00'), Decimal('1.90'), Decimal('1.90')),
    (Decimal('1000.01'), Decimal('1100.00'), Decimal('2.10'), Decimal('2.10')),
    (Decimal('1100.01'), Decimal('1200.00'), Decimal('2.30'), Decimal('2.30')),
    (Decimal('1200.01'), Decimal('1300.00'), Decimal('2.50'), Decimal('2.50')),
    (Decimal('1300.01'), Decimal('1400.00'), Decimal('2.70'), Decimal('2.70')),
    (Decimal('1400.01'), Decimal('1500.00'), Decimal('2.90'), Decimal('2.90')),
    (Decimal('1500.01'), Decimal('1600.00'), Decimal('3.10'), Decimal('3.10')),
    (Decimal('1600.01'), Decimal('1700.00'), Decimal('3.30'), Decimal('3.30')),
    (Decimal('1700.01'), Decimal('1800.00'), Decimal('3.50'), Decimal('3.50')),
    (Decimal('1800.01'), Decimal('1900.00'), Decimal('3.70'), Decimal('3.70')),
    (Decimal('1900.01'), Decimal('2000.00'), Decimal('3.90'), Decimal('3.90')),
    (Decimal('2000.01'), Decimal('2100.00'), Decimal('4.10'), Decimal('4.10')),
    (Decimal('2100.01'), Decimal('2200.00'), Decimal('4.30'), Decimal('4.30')),
    (Decimal('2200.01'), Decimal('2300.00'), Decimal('4.50'), Decimal('4.50')),
    (Decimal('2300.01'), Decimal('2400.00'), Decimal('4.70'), Decimal('4.70')),
    (Decimal('2400.01'), Decimal('2500.00'), Decimal('4.90'), Decimal('4.90')),
    (Decimal('2500.01'), Decimal('2600.00'), Decimal('5.10'), Decimal('5.10')),
    (Decimal('2600.01'), Decimal('2700.00'), Decimal('5.30'), Decimal('5.30')),
    (Decimal('2700.01'), Decimal('2800.00'), Decimal('5.50'), Decimal('5.50')),
    (Decimal('2800.01'), Decimal('2900.00'), Decimal('5.70'), Decimal('5.70')),
    (Decimal('2900.01'), Decimal('3000.00'), Decimal('5.90'), Decimal('5.90')),
    (Decimal('3000.01'), Decimal('3100.00'), Decimal('6.10'), Decimal('6.10')),
    (Decimal('3100.01'), Decimal('3200.00'), Decimal('6.30'), Decimal('6.30')),
    (Decimal('3200.01'), Decimal('3300.00'), Decimal('6.50'), Decimal('6.50')),
    (Decimal('3300.01'), Decimal('3400.00'), Decimal('6.70'), Decimal('6.70')),
    (Decimal('3400.01'), Decimal('3500.00'), Decimal('6.90'), Decimal('6.90')),
    (Decimal('3500.01'), Decimal('3600.00'), Decimal('7.10'), Decimal('7.10')),
    (Decimal('3600.01'), Decimal('3700.00'), Decimal('7.30'), Decimal('7.30')),
    (Decimal('3700.01'), Decimal('3800.00'), Decimal('7.50'), Decimal('7.50')),
    (Decimal('3800.01'), Decimal('3900.00'), Decimal('7.70'), Decimal('7.70')),
    (Decimal('3900.01'), Decimal('4000.00'), Decimal('7.90'), Decimal('7.90')),
    (Decimal('4000.01'), Decimal('5000.00'), Decimal('9.90'), Decimal('9.90')),
]

# =============================================================================
# PCB (LHDN) TAX RATES - Year of Assessment 2024
# =============================================================================

# Resident Individual Tax Rates
PCB_TAX_BRACKETS_2024 = [
    # (income_from, income_to, tax_rate_percent, cumulative_tax_on_previous)
    (Decimal('0'), Decimal('5000'), Decimal('0'), Decimal('0')),
    (Decimal('5001'), Decimal('20000'), Decimal('1'), Decimal('0')),
    (Decimal('20001'), Decimal('35000'), Decimal('3'), Decimal('150')),
    (Decimal('35001'), Decimal('50000'), Decimal('6'), Decimal('600')),
    (Decimal('50001'), Decimal('70000'), Decimal('11'), Decimal('1500')),
    (Decimal('70001'), Decimal('100000'), Decimal('19'), Decimal('3700')),
    (Decimal('100001'), Decimal('400000'), Decimal('25'), Decimal('9400')),
    (Decimal('400001'), Decimal('600000'), Decimal('26'), Decimal('84400')),
    (Decimal('600001'), Decimal('2000000'), Decimal('28'), Decimal('136400')),
    (Decimal('2000001'), Decimal('999999999'), Decimal('30'), Decimal('528400')),
]

# Non-Resident Tax Rate
NON_RESIDENT_TAX_RATE = Decimal('30')  # Flat 30%

# PCB Relief Categories (2024)
PCB_RELIEFS = {
    'individual': Decimal('9000'),
    'spouse': Decimal('4000'),          # Non-working spouse
    'child_under_18': Decimal('2000'),
    'child_18_plus_studying': Decimal('8000'),
    'child_disabled': Decimal('6000'),
    'disabled_individual': Decimal('6000'),
    'disabled_spouse': Decimal('5000'),
    'epf_max': Decimal('4000'),         # EPF relief max
    'life_insurance_max': Decimal('3000'),
    'education_insurance_max': Decimal('3000'),
    'medical_insurance_max': Decimal('3000'),
    'sspn_max': Decimal('8000'),        # SSPN deposit
    'lifestyle_max': Decimal('2500'),
    'parent_medical_max': Decimal('8000'),
    'complete_medical_max': Decimal('10000'),
}

# =============================================================================
# HRDF (PSMB) RATES
# =============================================================================

HRDF_RATES = {
    'levy_rate_10_plus': Decimal('1.00'),  # 1% for companies with 10+ employees
    'levy_rate_optional': Decimal('0.50'),  # 0.5% for 5-9 employees (optional)
    'threshold_mandatory': 10,  # Mandatory for 10+ Malaysian employees
}

# =============================================================================
# ALLOWANCE CATEGORIES - Statutory Applicability
# =============================================================================

ALLOWANCE_TYPES = {
    'TRAVEL': {
        'name': 'Travel Allowance',
        'code': 'TRVL',
        'epf_applicable': False,  # Generally exempt if for official duties
        'socso_applicable': False,
        'eis_applicable': False,
        'taxable': True,  # Unless for official duties
    },
    'MEAL': {
        'name': 'Meal Allowance',
        'code': 'MEAL',
        'epf_applicable': True,
        'socso_applicable': True,
        'eis_applicable': True,
        'taxable': True,
    },
    'HANDPHONE': {
        'name': 'Handphone Allowance',
        'code': 'HPHN',
        'epf_applicable': True,
        'socso_applicable': True,
        'eis_applicable': True,
        'taxable': True,
    },
    'HOUSING': {
        'name': 'Housing Allowance',
        'code': 'HOUS',
        'epf_applicable': True,
        'socso_applicable': True,
        'eis_applicable': True,
        'taxable': True,
    },
    'COMMISSION': {
        'name': 'Commission',
        'code': 'COMM',
        'epf_applicable': True,
        'socso_applicable': True,
        'eis_applicable': True,
        'taxable': True,
    },
    'INCENTIVE': {
        'name': 'Incentive',
        'code': 'INCV',
        'epf_applicable': True,
        'socso_applicable': True,
        'eis_applicable': True,
        'taxable': True,
    },
    'OVERTIME': {
        'name': 'Overtime',
        'code': 'OT',
        'epf_applicable': True,
        'socso_applicable': True,
        'eis_applicable': True,
        'taxable': True,
    },
    'SHIFT': {
        'name': 'Shift Allowance',
        'code': 'SHFT',
        'epf_applicable': True,
        'socso_applicable': True,
        'eis_applicable': True,
        'taxable': True,
    },
    'BONUS': {
        'name': 'Bonus',
        'code': 'BONS',
        'epf_applicable': True,
        'socso_applicable': False,  # Not subject to SOCSO
        'eis_applicable': False,     # Not subject to EIS
        'taxable': True,
    },
}

# =============================================================================
# DEDUCTION CATEGORIES
# =============================================================================

DEDUCTION_TYPES = {
    'ZAKAT': {
        'name': 'Zakat',
        'code': 'ZKAT',
        'is_statutory': True,
        'affects_pcb': True,  # Reduces PCB
    },
    'LOAN': {
        'name': 'Loan Repayment',
        'code': 'LOAN',
        'is_statutory': False,
        'affects_pcb': False,
    },
    'ADVANCE_SALARY': {
        'name': 'Advance Salary',
        'code': 'ADVS',
        'is_statutory': False,
        'affects_pcb': False,
    },
    'FINES': {
        'name': 'Fines & Penalties',
        'code': 'FINE',
        'is_statutory': False,
        'affects_pcb': False,
    },
    'UNION_FEES': {
        'name': 'Union Fees',
        'code': 'UNFEE',
        'is_statutory': False,
        'affects_pcb': False,
    },
    'CP38': {
        'name': 'CP38 Deduction',
        'code': 'CP38',
        'is_statutory': True,
        'affects_pcb': True,  # Additional tax deduction ordered by LHDN
    },
}

# =============================================================================
# BANK CODES - Bank Negara Malaysia Listed Banks
# =============================================================================

MALAYSIAN_BANKS = {
    'MBBEMYKL': {'name': 'Maybank', 'code': 'MBB'},
    'CIABORJ': {'name': 'CIMB Bank', 'code': 'CIMB'},
    'PABORJ': {'name': 'Public Bank', 'code': 'PBB'},
    'RHBB': {'name': 'RHB Bank', 'code': 'RHB'},
    'HLBB': {'name': 'Hong Leong Bank', 'code': 'HLB'},
    'AMBB': {'name': 'AmBank', 'code': 'AMB'},
    'BIMB': {'name': 'Bank Islam', 'code': 'BIMB'},
    'BMMB': {'name': 'Bank Muamalat', 'code': 'BMMB'},
    'AFFI': {'name': 'Affin Bank', 'code': 'AFFI'},
    'ALLA': {'name': 'Alliance Bank', 'code': 'ALLN'},
    'AGRO': {'name': 'Agrobank', 'code': 'AGRO'},
    'BSN': {'name': 'Bank Simpanan Nasional', 'code': 'BSN'},
    'BSNB': {'name': 'Bank Rakyat', 'code': 'BKRM'},
    'OCBC': {'name': 'OCBC Bank', 'code': 'OCBC'},
    'HSBC': {'name': 'HSBC Bank', 'code': 'HSBC'},
    'UOB': {'name': 'UOB Bank', 'code': 'UOB'},
    'SCB': {'name': 'Standard Chartered', 'code': 'SCB'},
}

# =============================================================================
# FILE FORMAT SPECIFICATIONS
# =============================================================================

FILE_FORMATS = {
    'EPF_FORM_A': {
        'extension': '.txt',
        'delimiter': '|',
        'encoding': 'utf-8',
    },
    'SOCSO_8A': {
        'extension': '.txt',
        'delimiter': '|',
        'encoding': 'utf-8',
    },
    'EIS': {
        'extension': '.txt',
        'delimiter': '|',
        'encoding': 'utf-8',
    },
    'CP39': {
        'extension': '.txt',
        'delimiter': '|',
        'encoding': 'utf-8',
    },
    'HRDF': {
        'extension': '.txt',
        'delimiter': '|',
        'encoding': 'utf-8',
    },
    'GIRO': {
        'extension': '.txt',
        'delimiter': '',  # Fixed width
        'encoding': 'utf-8',
    },
}

# =============================================================================
# FOREIGN WORKER CATEGORIES
# =============================================================================

FOREIGN_WORKER_TYPES = {
    'EXPAT': 'Expatriate',
    'FOREIGN': 'Foreign Worker',
    'PR': 'Permanent Resident',
}

LEVY_PAYMENT_TYPES = {
    'COMPANY': 'Company Paid',
    'EMPLOYEE': 'Employee Paid',
    'SHARED': 'Shared',
}

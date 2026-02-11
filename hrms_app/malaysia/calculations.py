"""
Malaysian Statutory Calculation Engines
========================================
EPF (KWSP), SOCSO (PERKESO), EIS, PCB (LHDN), HRDF calculation engines.
All calculations use raw SQL queries with connection.cursor().
"""

from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from datetime import date, datetime
from django.db import connection
from typing import Dict, Optional, Tuple, List
import calendar


class BaseCalculator:
    """Base class with common utility methods"""
    
    @staticmethod
    def safe_decimal(value, default="0.00") -> Decimal:
        """Safely convert value to Decimal"""
        try:
            if value is None:
                return Decimal(default)
            return Decimal(str(value))
        except:
            return Decimal(default)
    
    @staticmethod
    def round_sen(amount: Decimal) -> Decimal:
        """Round to nearest sen (2 decimal places)"""
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_age(ic_number: str = None, dob: date = None) -> int:
        """Calculate age from IC number or date of birth"""
        today = date.today()
        
        if ic_number and len(ic_number) >= 6:
            # Extract DOB from Malaysian IC (YYMMDD-XX-XXXX)
            ic_clean = ic_number.replace('-', '').replace(' ', '')
            year = int(ic_clean[:2])
            month = int(ic_clean[2:4])
            day = int(ic_clean[4:6])
            
            # Determine century
            current_year_short = today.year % 100
            if year > current_year_short:
                year += 1900
            else:
                year += 2000
            
            birth_date = date(year, month, day)
        elif dob:
            birth_date = dob
        else:
            return 0
        
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age


class EPFCalculator(BaseCalculator):
    """
    EPF (KWSP) Contribution Calculator
    Uses Third Schedule contribution table from database
    """
    
    def __init__(self, employee_id: str):
        self.employee_id = employee_id
        self.employee_info = self._get_employee_info()
    
    def _get_employee_info(self) -> Dict:
        """Get employee EPF-related information"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    med.ic_number,
                    med.epf_member_no,
                    med.epf_contribution_type,
                    med.worker_type,
                    ud.date_of_birth,
                    ud.gross_salary
                FROM ci_my_employee_details med
                LEFT JOIN ci_erp_users_details ud ON med.employee_id = ud.employee_id
                WHERE med.employee_id = %s
            """, [self.employee_id])
            row = cursor.fetchone()
            
        if row:
            return {
                'ic_number': row[0],
                'epf_member_no': row[1],
                'contribution_type': row[2] or 'full',
                'worker_type': row[3] or 'local',
                'dob': row[4],
                'gross_salary': self.safe_decimal(row[5])
            }
        return {}
    
    def calculate(self, epf_wages: Decimal, month: int = None, year: int = None) -> Dict:
        """
        Calculate EPF contributions based on wage table
        
        Args:
            epf_wages: Wages subject to EPF contribution
            
        Returns:
            Dict with employee_share, employer_share, total
        """
        if not self.employee_info:
            return self._empty_result()
        
        # Check if exempt
        if self.employee_info.get('contribution_type') == 'exempt':
            return self._empty_result()
        
        # Calculate age
        age = self.calculate_age(
            self.employee_info.get('ic_number'),
            self.employee_info.get('dob')
        )
        
        # Get contribution from rate table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT employee_share, employer_share_below_5k, employer_share_above_5k
                FROM ci_my_epf_rates
                WHERE %s >= wage_from AND %s <= wage_to
                AND is_active = 1
                AND (effective_to IS NULL OR effective_to >= CURDATE())
                ORDER BY effective_from DESC
                LIMIT 1
            """, [epf_wages, epf_wages])
            rate_row = cursor.fetchone()
        
        if rate_row:
            employee_share = self.safe_decimal(rate_row[0])
            
            # Employer rate depends on wage level
            if epf_wages <= Decimal('5000'):
                employer_share = self.safe_decimal(rate_row[1])
            else:
                employer_share = self.safe_decimal(rate_row[2])
        else:
            # Fallback to percentage calculation if no rate table entry
            if age >= 60:
                employee_rate = Decimal('5.5')  # Optional rate for 60+
            else:
                employee_rate = Decimal('11')
            
            if epf_wages <= Decimal('5000'):
                employer_rate = Decimal('13')
            else:
                employer_rate = Decimal('12')
            
            employee_share = self.round_sen(epf_wages * employee_rate / 100)
            employer_share = self.round_sen(epf_wages * employer_rate / 100)
        
        # Foreign worker handling
        if self.employee_info.get('worker_type') == 'foreign':
            # Foreign workers: Employer contribution is RM5 flat
            employer_share = Decimal('5.00')
            # Employee contribution is optional
            if self.employee_info.get('contribution_type') != 'full':
                employee_share = Decimal('0.00')
        
        return {
            'epf_wages': epf_wages,
            'employee_share': employee_share,
            'employer_share': employer_share,
            'total': employee_share + employer_share,
            'age': age,
            'epf_member_no': self.employee_info.get('epf_member_no', '')
        }
    
    def _empty_result(self) -> Dict:
        return {
            'epf_wages': Decimal('0'),
            'employee_share': Decimal('0'),
            'employer_share': Decimal('0'),
            'total': Decimal('0'),
            'age': 0,
            'epf_member_no': ''
        }


class SOCSOCalculator(BaseCalculator):
    """
    SOCSO (PERKESO) Contribution Calculator
    Category 1: Employment Injury & Invalidity (below 60)
    Category 2: Employment Injury Only (60 and above)
    """
    
    WAGE_CEILING = Decimal('5000.00')
    
    def __init__(self, employee_id: str):
        self.employee_id = employee_id
        self.employee_info = self._get_employee_info()
    
    def _get_employee_info(self) -> Dict:
        """Get employee SOCSO-related information"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    med.ic_number,
                    med.socso_member_no,
                    med.socso_category,
                    med.worker_type,
                    ud.date_of_birth
                FROM ci_my_employee_details med
                LEFT JOIN ci_erp_users_details ud ON med.employee_id = ud.employee_id
                WHERE med.employee_id = %s
            """, [self.employee_id])
            row = cursor.fetchone()
            
        if row:
            return {
                'ic_number': row[0],
                'socso_member_no': row[1],
                'socso_category': row[2] or 'category_1',
                'worker_type': row[3] or 'local',
                'dob': row[4]
            }
        return {}
    
    def calculate(self, socso_wages: Decimal) -> Dict:
        """
        Calculate SOCSO contributions based on wage table
        
        Args:
            socso_wages: Wages subject to SOCSO (max RM5,000)
            
        Returns:
            Dict with employee_share, employer_share
        """
        if not self.employee_info:
            return self._empty_result()
        
        # Calculate age to determine category
        age = self.calculate_age(
            self.employee_info.get('ic_number'),
            self.employee_info.get('dob')
        )
        
        # Determine category
        if age >= 60:
            category = 'category_2'
        else:
            category = self.employee_info.get('socso_category', 'category_1')
        
        # Cap wages at ceiling
        capped_wages = min(socso_wages, self.WAGE_CEILING)
        
        # Get contribution from rate table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT employee_share_cat1, employer_share_cat1, employer_share_cat2
                FROM ci_my_socso_rates
                WHERE %s >= wage_from AND %s <= wage_to
                AND is_active = 1
                ORDER BY effective_from DESC
                LIMIT 1
            """, [capped_wages, capped_wages])
            rate_row = cursor.fetchone()
        
        if rate_row:
            if category == 'category_2':
                # Age 60+: Employer only, Employment Injury Scheme
                employee_share = Decimal('0')
                employer_share = self.safe_decimal(rate_row[2])
            else:
                # Category 1: Both contribute
                employee_share = self.safe_decimal(rate_row[0])
                employer_share = self.safe_decimal(rate_row[1])
        else:
            # Fallback if no rate table
            employee_share = Decimal('0')
            employer_share = Decimal('0')
        
        # SOCSO Number: For locals, same as IC. For foreigners, use SSN
        socso_no = self.employee_info.get('socso_member_no')
        if not socso_no and self.employee_info.get('worker_type') == 'local':
            socso_no = self.employee_info.get('ic_number', '').replace('-', '')
        
        return {
            'socso_wages': capped_wages,
            'employee_share': employee_share,
            'employer_share': employer_share,
            'total': employee_share + employer_share,
            'category': category,
            'socso_member_no': socso_no or '',
            'age': age
        }
    
    def _empty_result(self) -> Dict:
        return {
            'socso_wages': Decimal('0'),
            'employee_share': Decimal('0'),
            'employer_share': Decimal('0'),
            'total': Decimal('0'),
            'category': 'category_1',
            'socso_member_no': '',
            'age': 0
        }


class EISCalculator(BaseCalculator):
    """
    EIS (Employment Insurance System) Calculator
    Not applicable for employees aged 57 and above
    """
    
    WAGE_CEILING = Decimal('5000.00')
    MAX_AGE = 57
    
    def __init__(self, employee_id: str):
        self.employee_id = employee_id
        self.employee_info = self._get_employee_info()
    
    def _get_employee_info(self) -> Dict:
        """Get employee EIS-related information"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    med.ic_number,
                    med.eis_member_no,
                    med.worker_type,
                    ud.date_of_birth
                FROM ci_my_employee_details med
                LEFT JOIN ci_erp_users_details ud ON med.employee_id = ud.employee_id
                WHERE med.employee_id = %s
            """, [self.employee_id])
            row = cursor.fetchone()
            
        if row:
            return {
                'ic_number': row[0],
                'eis_member_no': row[1],
                'worker_type': row[2] or 'local',
                'dob': row[3]
            }
        return {}
    
    def calculate(self, eis_wages: Decimal) -> Dict:
        """
        Calculate EIS contributions
        
        Args:
            eis_wages: Wages subject to EIS (max RM5,000)
            
        Returns:
            Dict with employee_share, employer_share
        """
        if not self.employee_info:
            return self._empty_result()
        
        # Calculate age
        age = self.calculate_age(
            self.employee_info.get('ic_number'),
            self.employee_info.get('dob')
        )
        
        # EIS not applicable for age 57+
        if age >= self.MAX_AGE:
            return self._empty_result()
        
        # Foreign workers are not covered by EIS
        if self.employee_info.get('worker_type') == 'foreign':
            return self._empty_result()
        
        # Cap wages at ceiling
        capped_wages = min(eis_wages, self.WAGE_CEILING)
        
        # Get contribution from rate table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT employee_share, employer_share
                FROM ci_my_eis_rates
                WHERE %s >= wage_from AND %s <= wage_to
                AND is_active = 1
                ORDER BY effective_from DESC
                LIMIT 1
            """, [capped_wages, capped_wages])
            rate_row = cursor.fetchone()
        
        if rate_row:
            employee_share = self.safe_decimal(rate_row[0])
            employer_share = self.safe_decimal(rate_row[1])
        else:
            # Fallback: 0.2% each
            employee_share = self.round_sen(capped_wages * Decimal('0.002'))
            employer_share = self.round_sen(capped_wages * Decimal('0.002'))
        
        return {
            'eis_wages': capped_wages,
            'employee_share': employee_share,
            'employer_share': employer_share,
            'total': employee_share + employer_share,
            'age': age
        }
    
    def _empty_result(self) -> Dict:
        return {
            'eis_wages': Decimal('0'),
            'employee_share': Decimal('0'),
            'employer_share': Decimal('0'),
            'total': Decimal('0'),
            'age': 0
        }


class PCBCalculator(BaseCalculator):
    """
    PCB (LHDN) Monthly Tax Deduction Calculator
    Implements MTD (Monthly Tax Deduction) Schedule
    """
    
    def __init__(self, employee_id: str, tax_year: int):
        self.employee_id = employee_id
        self.tax_year = tax_year
        self.employee_info = self._get_employee_info()
        self.tax_profile = self._get_tax_profile()
    
    def _get_employee_info(self) -> Dict:
        """Get employee tax-related information"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    med.ic_number,
                    med.tax_reference_no,
                    med.residency_status,
                    med.worker_type
                FROM ci_my_employee_details med
                WHERE med.employee_id = %s
            """, [self.employee_id])
            row = cursor.fetchone()
            
        if row:
            return {
                'ic_number': row[0],
                'tax_reference_no': row[1],
                'residency_status': row[2] or 'resident',
                'worker_type': row[3] or 'local'
            }
        return {}
    
    def _get_tax_profile(self) -> Dict:
        """Get employee tax relief profile"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    marital_status,
                    spouse_working,
                    spouse_disabled,
                    number_of_children,
                    children_studying_higher,
                    children_disabled,
                    disabled_self,
                    epf_additional,
                    life_insurance,
                    medical_insurance,
                    zakat_paid
                FROM ci_my_employee_tax_profile
                WHERE employee_id = %s AND tax_year = %s
            """, [self.employee_id, self.tax_year])
            row = cursor.fetchone()
            
        if row:
            return {
                'marital_status': row[0] or 'single',
                'spouse_working': bool(row[1]),
                'spouse_disabled': bool(row[2]),
                'number_of_children': row[3] or 0,
                'children_higher': row[4] or 0,
                'children_disabled': row[5] or 0,
                'disabled_self': bool(row[6]),
                'epf_additional': self.safe_decimal(row[7]),
                'life_insurance': self.safe_decimal(row[8]),
                'medical_insurance': self.safe_decimal(row[9]),
                'zakat_paid': self.safe_decimal(row[10])
            }
        return {'marital_status': 'single'}
    
    def _get_ytd_data(self, current_month: int) -> Dict:
        """Get year-to-date earnings and PCB"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(gross_salary), 0) as ytd_gross,
                    COALESCE(SUM(bonus), 0) as ytd_bonus,
                    COALESCE(SUM(epf_employee), 0) as ytd_epf,
                    COALESCE(SUM(pcb_amount + pcb_bonus), 0) as ytd_pcb,
                    COALESCE(SUM(zakat), 0) as ytd_zakat
                FROM ci_my_payroll_report
                WHERE employee_id = %s 
                AND year = %s 
                AND month < %s
                AND status IN ('approved', 'paid')
            """, [self.employee_id, self.tax_year, current_month])
            row = cursor.fetchone()
            
        if row:
            return {
                'ytd_gross': self.safe_decimal(row[0]),
                'ytd_bonus': self.safe_decimal(row[1]),
                'ytd_epf': self.safe_decimal(row[2]),
                'ytd_pcb': self.safe_decimal(row[3]),
                'ytd_zakat': self.safe_decimal(row[4])
            }
        return {
            'ytd_gross': Decimal('0'),
            'ytd_bonus': Decimal('0'),
            'ytd_epf': Decimal('0'),
            'ytd_pcb': Decimal('0'),
            'ytd_zakat': Decimal('0')
        }
    
    def _get_tp3_data(self) -> Dict:
        """Get TP3 (previous employment) data"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(gross_remuneration), 0),
                    COALESCE(SUM(epf_contribution), 0),
                    COALESCE(SUM(pcb_deducted), 0),
                    COALESCE(SUM(zakat_paid), 0)
                FROM ci_my_tp3_records
                WHERE employee_id = %s AND tax_year = %s
            """, [self.employee_id, self.tax_year])
            row = cursor.fetchone()
            
        if row:
            return {
                'tp3_gross': self.safe_decimal(row[0]),
                'tp3_epf': self.safe_decimal(row[1]),
                'tp3_pcb': self.safe_decimal(row[2]),
                'tp3_zakat': self.safe_decimal(row[3])
            }
        return {
            'tp3_gross': Decimal('0'),
            'tp3_epf': Decimal('0'),
            'tp3_pcb': Decimal('0'),
            'tp3_zakat': Decimal('0')
        }
    
    def calculate_annual_relief(self, annual_epf: Decimal) -> Decimal:
        """Calculate total annual tax reliefs"""
        relief = Decimal('9000')  # Individual relief
        
        profile = self.tax_profile
        
        # Self disability
        if profile.get('disabled_self'):
            relief += Decimal('6000')
        
        # Spouse relief
        if profile.get('marital_status') == 'married':
            if not profile.get('spouse_working'):
                relief += Decimal('4000')
            if profile.get('spouse_disabled'):
                relief += Decimal('5000')
        
        # Children relief
        children = profile.get('number_of_children', 0)
        children_higher = profile.get('children_higher', 0)
        children_disabled = profile.get('children_disabled', 0)
        
        relief += Decimal(str(children)) * Decimal('2000')
        relief += Decimal(str(children_higher)) * Decimal('8000')
        relief += Decimal(str(children_disabled)) * Decimal('6000')
        
        # EPF relief (max RM4,000)
        epf_relief = min(annual_epf, Decimal('4000'))
        relief += epf_relief
        
        # Life insurance (max RM3,000)
        life_ins = min(profile.get('life_insurance', Decimal('0')), Decimal('3000'))
        relief += life_ins
        
        # Medical insurance (max RM3,000)
        med_ins = min(profile.get('medical_insurance', Decimal('0')), Decimal('3000'))
        relief += med_ins
        
        return relief
    
    def calculate_tax(self, taxable_income: Decimal) -> Decimal:
        """Calculate annual tax based on tax brackets"""
        # Non-resident: flat 30%
        if self.employee_info.get('residency_status') == 'non_resident':
            return self.round_sen(taxable_income * Decimal('0.30'))
        
        # Resident: Progressive tax
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT income_from, income_to, tax_rate, cumulative_tax
                FROM ci_my_pcb_tax_brackets
                WHERE tax_year = %s AND is_active = 1
                ORDER BY income_from
            """, [self.tax_year])
            brackets = cursor.fetchall()
        
        if not brackets:
            return Decimal('0')
        
        tax = Decimal('0')
        remaining_income = taxable_income
        
        for bracket in brackets:
            bracket_from = self.safe_decimal(bracket[0])
            bracket_to = self.safe_decimal(bracket[1])
            rate = self.safe_decimal(bracket[2])
            
            if remaining_income <= 0:
                break
            
            if taxable_income <= bracket_from:
                continue
            
            taxable_in_bracket = min(
                remaining_income,
                bracket_to - bracket_from
            )
            
            if taxable_income > bracket_from:
                tax += taxable_in_bracket * rate / 100
                remaining_income -= taxable_in_bracket
        
        return self.round_sen(tax)
    
    def calculate(self, monthly_gross: Decimal, epf_employee: Decimal,
                  current_month: int, bonus: Decimal = Decimal('0'),
                  zakat_current: Decimal = Decimal('0')) -> Dict:
        """
        Calculate monthly PCB using MTD formula
        
        Args:
            monthly_gross: Current month gross salary
            epf_employee: Current month EPF employee contribution
            current_month: Current processing month (1-12)
            bonus: Bonus amount (if any)
            zakat_current: Zakat deduction for current month
            
        Returns:
            Dict with pcb_normal, pcb_bonus, total_pcb
        """
        if not self.employee_info:
            return self._empty_result()
        
        # Get YTD and TP3 data
        ytd = self._get_ytd_data(current_month)
        tp3 = self._get_tp3_data()
        
        # Calculate months remaining in year
        months_remaining = 13 - current_month
        
        # Annual projection
        ytd_gross = ytd['ytd_gross'] + tp3['tp3_gross']
        ytd_epf = ytd['ytd_epf'] + tp3['tp3_epf']
        ytd_pcb = ytd['ytd_pcb'] + tp3['tp3_pcb']
        ytd_zakat = ytd['ytd_zakat'] + tp3['tp3_zakat']
        
        # Project annual income (excluding bonus)
        projected_annual = ytd_gross + (monthly_gross * months_remaining)
        
        # Project annual EPF
        projected_epf = ytd_epf + (epf_employee * months_remaining)
        
        # Calculate reliefs
        annual_relief = self.calculate_annual_relief(projected_epf)
        
        # Project annual zakat
        projected_zakat = ytd_zakat + (zakat_current * months_remaining)
        
        # Taxable income (excluding bonus for normal PCB)
        taxable_income = projected_annual - annual_relief
        taxable_income = max(taxable_income, Decimal('0'))
        
        # Calculate annual tax
        annual_tax = self.calculate_tax(taxable_income)
        
        # Deduct zakat from tax (zakat is deductible from tax payable)
        annual_tax = max(annual_tax - projected_zakat, Decimal('0'))
        
        # Monthly PCB
        if months_remaining > 0:
            monthly_pcb = (annual_tax - ytd_pcb) / months_remaining
        else:
            monthly_pcb = annual_tax - ytd_pcb
        
        monthly_pcb = max(self.round_sen(monthly_pcb), Decimal('0'))
        
        # Calculate bonus PCB separately
        bonus_pcb = Decimal('0')
        if bonus > Decimal('0'):
            # Add bonus to projection and recalculate
            projected_with_bonus = projected_annual + bonus
            taxable_with_bonus = projected_with_bonus - annual_relief
            taxable_with_bonus = max(taxable_with_bonus, Decimal('0'))
            annual_tax_with_bonus = self.calculate_tax(taxable_with_bonus)
            annual_tax_with_bonus = max(annual_tax_with_bonus - projected_zakat, Decimal('0'))
            
            # Bonus PCB is the difference
            bonus_pcb = annual_tax_with_bonus - annual_tax
            bonus_pcb = max(self.round_sen(bonus_pcb), Decimal('0'))
        
        return {
            'pcb_normal': monthly_pcb,
            'pcb_bonus': bonus_pcb,
            'total_pcb': monthly_pcb + bonus_pcb,
            'taxable_income_projected': taxable_income,
            'annual_relief': annual_relief,
            'tax_reference_no': self.employee_info.get('tax_reference_no', ''),
            'residency_status': self.employee_info.get('residency_status', 'resident')
        }
    
    def _empty_result(self) -> Dict:
        return {
            'pcb_normal': Decimal('0'),
            'pcb_bonus': Decimal('0'),
            'total_pcb': Decimal('0'),
            'taxable_income_projected': Decimal('0'),
            'annual_relief': Decimal('0'),
            'tax_reference_no': '',
            'residency_status': ''
        }


class HRDFCalculator(BaseCalculator):
    """
    HRDF (PSMB) Levy Calculator
    1% of monthly wages for employers with 10+ Malaysian employees
    """
    
    def __init__(self, company_id: int):
        self.company_id = company_id
        self.config = self._get_config()
    
    def _get_config(self) -> Dict:
        """Get company HRDF configuration"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT hrdf_enabled, hrdf_levy_rate
                FROM ci_my_company_statutory_config
                WHERE company_id = %s
            """, [self.company_id])
            row = cursor.fetchone()
            
        if row:
            return {
                'enabled': bool(row[0]),
                'levy_rate': self.safe_decimal(row[1])
            }
        return {'enabled': False, 'levy_rate': Decimal('0')}
    
    def calculate(self, total_wages: Decimal) -> Dict:
        """
        Calculate HRDF levy
        
        Args:
            total_wages: Total monthly wages
            
        Returns:
            Dict with levy_amount
        """
        if not self.config.get('enabled'):
            return {'levy_amount': Decimal('0'), 'rate': Decimal('0')}
        
        rate = self.config.get('levy_rate', Decimal('0.01'))
        levy = self.round_sen(total_wages * rate)
        
        return {
            'levy_amount': levy,
            'rate': rate
        }


class WagesCalculator(BaseCalculator):
    """
    Calculate statutory wages (EPF, SOCSO, EIS wages)
    Based on allowance configurations
    """
    
    def __init__(self, employee_id: str, company_id: int):
        self.employee_id = employee_id
        self.company_id = company_id
    
    def calculate_statutory_wages(self, basic_salary: Decimal, 
                                    allowances: List[Dict],
                                    bonus: Decimal = Decimal('0'),
                                    overtime: Decimal = Decimal('0')) -> Dict:
        """
        Calculate wages subject to each statutory body
        
        Args:
            basic_salary: Basic salary
            allowances: List of allowance dicts with type_id and amount
            bonus: Bonus amount
            overtime: Overtime amount
            
        Returns:
            Dict with epf_wages, socso_wages, eis_wages, taxable_income
        """
        epf_wages = basic_salary + overtime
        socso_wages = basic_salary + overtime
        eis_wages = basic_salary + overtime
        taxable_income = basic_salary + overtime + bonus
        
        # Get allowance type configurations
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT allowance_type_id, is_taxable, epf_applicable, 
                       socso_applicable, eis_applicable
                FROM ci_my_allowance_types
                WHERE (company_id = %s OR company_id IS NULL)
                AND is_active = 1
            """, [self.company_id])
            rows = cursor.fetchall()
        
        allowance_config = {row[0]: {
            'taxable': bool(row[1]),
            'epf': bool(row[2]),
            'socso': bool(row[3]),
            'eis': bool(row[4])
        } for row in rows}
        
        # Process each allowance
        for allowance in allowances:
            type_id = allowance.get('type_id')
            amount = self.safe_decimal(allowance.get('amount', 0))
            
            config = allowance_config.get(type_id, {
                'taxable': True, 'epf': True, 'socso': True, 'eis': True
            })
            
            if config.get('epf'):
                epf_wages += amount
            if config.get('socso'):
                socso_wages += amount
            if config.get('eis'):
                eis_wages += amount
            if config.get('taxable'):
                taxable_income += amount
        
        # Bonus is EPF-applicable but not SOCSO/EIS
        epf_wages += bonus
        
        return {
            'epf_wages': epf_wages,
            'socso_wages': min(socso_wages, Decimal('5000')),
            'eis_wages': min(eis_wages, Decimal('5000')),
            'taxable_income': taxable_income,
            'gross_salary': basic_salary + overtime + bonus + sum(
                self.safe_decimal(a.get('amount', 0)) for a in allowances
            )
        }


class PayrollProcessor(BaseCalculator):
    """
    Main payroll processor that combines all calculators
    """
    
    def __init__(self, company_id: int, month: int, year: int):
        self.company_id = company_id
        self.month = month
        self.year = year
        self.config = self._get_company_config()
    
    def _get_company_config(self) -> Dict:
        """Get company statutory configuration"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    epf_enabled, epf_employer_no,
                    socso_enabled, socso_employer_no,
                    eis_enabled,
                    lhdn_enabled, lhdn_e_number,
                    hrdf_enabled, hrdf_levy_rate
                FROM ci_my_company_statutory_config
                WHERE company_id = %s
            """, [self.company_id])
            row = cursor.fetchone()
            
        if row:
            return {
                'epf_enabled': bool(row[0]),
                'epf_employer_no': row[1],
                'socso_enabled': bool(row[2]),
                'socso_employer_no': row[3],
                'eis_enabled': bool(row[4]),
                'lhdn_enabled': bool(row[5]),
                'lhdn_e_number': row[6],
                'hrdf_enabled': bool(row[7]),
                'hrdf_levy_rate': self.safe_decimal(row[8])
            }
        return {}
    
    def process_employee(self, employee_id: str, basic_salary: Decimal,
                         allowances: List[Dict] = None,
                         overtime: Decimal = Decimal('0'),
                         bonus: Decimal = Decimal('0'),
                         payable_days: Decimal = Decimal('0'),
                         other_deductions: Dict = None) -> Dict:
        """
        Process payroll for a single employee
        
        Returns complete payroll calculation including all statutory deductions
        """
        allowances = allowances or []
        other_deductions = other_deductions or {}
        
        # Calculate statutory wages
        wages_calc = WagesCalculator(employee_id, self.company_id)
        wages = wages_calc.calculate_statutory_wages(
            basic_salary, allowances, bonus, overtime
        )
        
        result = {
            'employee_id': employee_id,
            'month': self.month,
            'year': self.year,
            'payable_days': payable_days,
            'basic_salary': basic_salary,
            'overtime_amount': overtime,
            'bonus': bonus,
            'gross_salary': wages['gross_salary'],
            'epf_wages': wages['epf_wages'],
            'socso_wages': wages['socso_wages'],
            'eis_wages': wages['eis_wages'],
        }
        
        # EPF Calculation
        if self.config.get('epf_enabled', True):
            epf_calc = EPFCalculator(employee_id)
            epf = epf_calc.calculate(wages['epf_wages'])
            result.update({
                'epf_employee': epf['employee_share'],
                'epf_employer': epf['employer_share'],
                'epf_member_no': epf['epf_member_no']
            })
        else:
            result.update({
                'epf_employee': Decimal('0'),
                'epf_employer': Decimal('0'),
                'epf_member_no': ''
            })
        
        # SOCSO Calculation
        if self.config.get('socso_enabled', True):
            socso_calc = SOCSOCalculator(employee_id)
            socso = socso_calc.calculate(wages['socso_wages'])
            result.update({
                'socso_employee': socso['employee_share'],
                'socso_employer': socso['employer_share'],
                'socso_member_no': socso['socso_member_no'],
                'socso_category': socso['category']
            })
        else:
            result.update({
                'socso_employee': Decimal('0'),
                'socso_employer': Decimal('0'),
                'socso_member_no': '',
                'socso_category': ''
            })
        
        # EIS Calculation
        if self.config.get('eis_enabled', True):
            eis_calc = EISCalculator(employee_id)
            eis = eis_calc.calculate(wages['eis_wages'])
            result.update({
                'eis_employee': eis['employee_share'],
                'eis_employer': eis['employer_share']
            })
        else:
            result.update({
                'eis_employee': Decimal('0'),
                'eis_employer': Decimal('0')
            })
        
        # PCB Calculation
        zakat = self.safe_decimal(other_deductions.get('zakat', 0))
        if self.config.get('lhdn_enabled', True):
            pcb_calc = PCBCalculator(employee_id, self.year)
            pcb = pcb_calc.calculate(
                wages['taxable_income'],
                result['epf_employee'],
                self.month,
                bonus,
                zakat
            )
            result.update({
                'pcb_amount': pcb['pcb_normal'],
                'pcb_bonus': pcb['pcb_bonus'],
                'tax_reference_no': pcb['tax_reference_no']
            })
        else:
            result.update({
                'pcb_amount': Decimal('0'),
                'pcb_bonus': Decimal('0'),
                'tax_reference_no': ''
            })
        
        # HRDF Calculation (Employer only)
        if self.config.get('hrdf_enabled', False):
            hrdf_calc = HRDFCalculator(self.company_id)
            hrdf = hrdf_calc.calculate(wages['gross_salary'])
            result['hrdf_levy'] = hrdf['levy_amount']
        else:
            result['hrdf_levy'] = Decimal('0')
        
        # Other deductions
        result.update({
            'zakat': zakat,
            'loan_deduction': self.safe_decimal(other_deductions.get('loan', 0)),
            'advance_salary': self.safe_decimal(other_deductions.get('advance', 0)),
            'cp38_deduction': self.safe_decimal(other_deductions.get('cp38', 0)),
            'other_deductions': self.safe_decimal(other_deductions.get('other', 0))
        })
        
        # Calculate totals
        total_employee_statutory = (
            result['epf_employee'] + 
            result['socso_employee'] + 
            result['eis_employee'] + 
            result['pcb_amount'] + 
            result['pcb_bonus']
        )
        
        total_employer_statutory = (
            result['epf_employer'] + 
            result['socso_employer'] + 
            result['eis_employer'] + 
            result['hrdf_levy']
        )
        
        total_deductions = (
            total_employee_statutory +
            result['zakat'] +
            result['loan_deduction'] +
            result['advance_salary'] +
            result['cp38_deduction'] +
            result['other_deductions']
        )
        
        net_pay = wages['gross_salary'] - total_deductions
        
        result.update({
            'total_employee_statutory': total_employee_statutory,
            'total_employer_statutory': total_employer_statutory,
            'total_deductions': total_deductions,
            'total_earnings': wages['gross_salary'],
            'net_pay': net_pay
        })
        
        return result

"""
Malaysian Payroll API Views
============================
Class-based views using raw SQL queries for Malaysian statutory compliance.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import connection, transaction
from django.http import HttpResponse
from decimal import Decimal
from datetime import date, datetime
from typing import Dict, List
import calendar

from .serializers import (
    CompanyStatutoryConfigSerializer,
    EmployeeMalaysianDetailsSerializer,
    EmployeeTaxProfileSerializer,
    AllowanceTypeSerializer,
    DeductionTypeSerializer,
    EmployeeAllowanceSerializer,
    EmployeeDeductionSerializer,
    PayrollProcessRequestSerializer,
    PayrollSaveRequestSerializer,
    StatutoryFileRequestSerializer,
    EPFGIRORequestSerializer,
    BankGIRORequestSerializer,
    EAFormRequestSerializer,
    CP38OrderSerializer,
    TP3RecordSerializer,
)
from .calculations import PayrollProcessor, EPFCalculator, SOCSOCalculator, EISCalculator, PCBCalculator
from .file_generators import (
    EPFFormAGenerator, EPFGIROGenerator,
    SOCSO8AGenerator, EISFileGenerator,
    CP39Generator, EAFormGenerator, CP8DGenerator,
    CP38Generator, HRDFLevyGenerator, BankGIROGenerator,
    FileValidationService
)


class BaseAPIView(APIView):
    """Base API view with common utilities"""
    
    @staticmethod
    def safe_decimal(value, default="0.00") -> Decimal:
        try:
            if value is None:
                return Decimal(default)
            return Decimal(str(value))
        except:
            return Decimal(default)
    
    @staticmethod
    def dictfetchall(cursor):
        """Return all rows from a cursor as a dict"""
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @staticmethod
    def dictfetchone(cursor):
        """Return one row from a cursor as a dict"""
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return None


# =============================================================================
# COMPANY STATUTORY CONFIGURATION
# =============================================================================

class CompanyStatutoryConfigView(BaseAPIView):
    """
    GET: Get company statutory configuration
    POST: Create or update company statutory configuration
    """
    
    def get(self, request, company_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        config_id, company_id,
                        epf_enabled, epf_employer_no,
                        socso_enabled, socso_employer_no,
                        eis_enabled,
                        lhdn_enabled, lhdn_e_number,
                        hrdf_enabled, hrdf_registration_no, hrdf_levy_rate,
                        created_at, updated_at
                    FROM ci_my_company_statutory_config
                    WHERE company_id = %s
                """, [company_id])
                result = self.dictfetchone(cursor)
            
            if not result:
                return Response({
                    "status": "error",
                    "message": "Configuration not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                "status": "success",
                "data": result
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = CompanyStatutoryConfigSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                # Check if exists
                cursor.execute("""
                    SELECT config_id FROM ci_my_company_statutory_config
                    WHERE company_id = %s
                """, [data['company_id']])
                exists = cursor.fetchone()
                
                if exists:
                    # Update
                    cursor.execute("""
                        UPDATE ci_my_company_statutory_config SET
                            epf_enabled = %s, epf_employer_no = %s,
                            socso_enabled = %s, socso_employer_no = %s,
                            eis_enabled = %s,
                            lhdn_enabled = %s, lhdn_e_number = %s,
                            hrdf_enabled = %s, hrdf_registration_no = %s, hrdf_levy_rate = %s,
                            updated_at = NOW()
                        WHERE company_id = %s
                    """, [
                        data.get('epf_enabled', True), data.get('epf_employer_no', ''),
                        data.get('socso_enabled', True), data.get('socso_employer_no', ''),
                        data.get('eis_enabled', True),
                        data.get('lhdn_enabled', True), data.get('lhdn_e_number', ''),
                        data.get('hrdf_enabled', False), data.get('hrdf_registration_no', ''),
                        float(data.get('hrdf_levy_rate', 0.01)),
                        data['company_id']
                    ])
                else:
                    # Insert
                    cursor.execute("""
                        INSERT INTO ci_my_company_statutory_config
                        (company_id, epf_enabled, epf_employer_no, socso_enabled, socso_employer_no,
                         eis_enabled, lhdn_enabled, lhdn_e_number, hrdf_enabled, hrdf_registration_no, hrdf_levy_rate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        data['company_id'],
                        data.get('epf_enabled', True), data.get('epf_employer_no', ''),
                        data.get('socso_enabled', True), data.get('socso_employer_no', ''),
                        data.get('eis_enabled', True),
                        data.get('lhdn_enabled', True), data.get('lhdn_e_number', ''),
                        data.get('hrdf_enabled', False), data.get('hrdf_registration_no', ''),
                        float(data.get('hrdf_levy_rate', 0.01))
                    ])
            
            return Response({
                "status": "success",
                "message": "Configuration saved successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# EMPLOYEE MALAYSIAN DETAILS
# =============================================================================

class EmployeeMalaysianDetailsView(BaseAPIView):
    """
    GET: Get Malaysian details for an employee
    POST: Create or update Malaysian details
    """
    
    def get(self, request, employee_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        my_employee_id, employee_id, user_id,
                        ic_number, passport_number, passport_expiry,
                        tax_reference_no, epf_member_no, socso_member_no, eis_member_no,
                        nationality, residency_status, worker_type,
                        epf_contribution_type, socso_category,
                        work_permit_number, work_permit_expiry,
                        visa_type, visa_expiry,
                        fomema_date, fomema_expiry,
                        levy_payment_type, levy_amount,
                        bank_code, bank_name, bank_account_no, bank_swift_code,
                        is_active, created_at, updated_at
                    FROM ci_my_employee_details
                    WHERE employee_id = %s
                """, [employee_id])
                result = self.dictfetchone(cursor)
            
            if not result:
                return Response({
                    "status": "error",
                    "message": "Employee details not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                "status": "success",
                "data": result
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = EmployeeMalaysianDetailsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                # Check if exists
                cursor.execute("""
                    SELECT my_employee_id FROM ci_my_employee_details
                    WHERE employee_id = %s
                """, [data['employee_id']])
                exists = cursor.fetchone()
                
                if exists:
                    # Update
                    cursor.execute("""
                        UPDATE ci_my_employee_details SET
                            user_id = %s,
                            ic_number = %s, passport_number = %s, passport_expiry = %s,
                            tax_reference_no = %s, epf_member_no = %s, socso_member_no = %s, eis_member_no = %s,
                            nationality = %s, residency_status = %s, worker_type = %s,
                            epf_contribution_type = %s, socso_category = %s,
                            work_permit_number = %s, work_permit_expiry = %s,
                            visa_type = %s, visa_expiry = %s,
                            fomema_date = %s, fomema_expiry = %s,
                            levy_payment_type = %s, levy_amount = %s,
                            bank_code = %s, bank_name = %s, bank_account_no = %s, bank_swift_code = %s,
                            updated_at = NOW()
                        WHERE employee_id = %s
                    """, [
                        data['user_id'],
                        data.get('ic_number'), data.get('passport_number'), data.get('passport_expiry'),
                        data.get('tax_reference_no'), data.get('epf_member_no'), data.get('socso_member_no'), data.get('eis_member_no'),
                        data.get('nationality', 'Malaysian'), data.get('residency_status', 'resident'), data.get('worker_type', 'local'),
                        data.get('epf_contribution_type', 'full'), data.get('socso_category', 'category_1'),
                        data.get('work_permit_number'), data.get('work_permit_expiry'),
                        data.get('visa_type'), data.get('visa_expiry'),
                        data.get('fomema_date'), data.get('fomema_expiry'),
                        data.get('levy_payment_type', 'company'), float(data.get('levy_amount', 0)),
                        data.get('bank_code'), data.get('bank_name'), data.get('bank_account_no'), data.get('bank_swift_code'),
                        data['employee_id']
                    ])
                else:
                    # Insert
                    cursor.execute("""
                        INSERT INTO ci_my_employee_details
                        (employee_id, user_id, ic_number, passport_number, passport_expiry,
                         tax_reference_no, epf_member_no, socso_member_no, eis_member_no,
                         nationality, residency_status, worker_type,
                         epf_contribution_type, socso_category,
                         work_permit_number, work_permit_expiry, visa_type, visa_expiry,
                         fomema_date, fomema_expiry, levy_payment_type, levy_amount,
                         bank_code, bank_name, bank_account_no, bank_swift_code)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        data['employee_id'], data['user_id'],
                        data.get('ic_number'), data.get('passport_number'), data.get('passport_expiry'),
                        data.get('tax_reference_no'), data.get('epf_member_no'), data.get('socso_member_no'), data.get('eis_member_no'),
                        data.get('nationality', 'Malaysian'), data.get('residency_status', 'resident'), data.get('worker_type', 'local'),
                        data.get('epf_contribution_type', 'full'), data.get('socso_category', 'category_1'),
                        data.get('work_permit_number'), data.get('work_permit_expiry'),
                        data.get('visa_type'), data.get('visa_expiry'),
                        data.get('fomema_date'), data.get('fomema_expiry'),
                        data.get('levy_payment_type', 'company'), float(data.get('levy_amount', 0)),
                        data.get('bank_code'), data.get('bank_name'), data.get('bank_account_no'), data.get('bank_swift_code')
                    ])
            
            return Response({
                "status": "success",
                "message": "Employee details saved successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeMalaysianDetailsListView(BaseAPIView):
    """
    GET: Get all Malaysian employee details for a company
    """
    
    def get(self, request, company_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        med.my_employee_id, med.employee_id, med.user_id,
                        CONCAT(u.first_name, ' ', u.last_name) as employee_name,
                        med.ic_number, med.tax_reference_no,
                        med.epf_member_no, med.socso_member_no,
                        med.worker_type, med.nationality, med.residency_status,
                        med.bank_name, med.bank_account_no,
                        med.is_active
                    FROM ci_my_employee_details med
                    INNER JOIN ci_erp_users_details ud ON med.employee_id = ud.employee_id
                    INNER JOIN ci_erp_users u ON ud.user_id = u.id
                    WHERE ud.company_id = %s
                    ORDER BY u.first_name, u.last_name
                """, [company_id])
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# EMPLOYEE TAX PROFILE
# =============================================================================

class EmployeeTaxProfileView(BaseAPIView):
    """
    GET: Get employee tax profile for PCB calculation
    POST: Create or update tax profile
    """
    
    def get(self, request, employee_id, tax_year):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM ci_my_employee_tax_profile
                    WHERE employee_id = %s AND tax_year = %s
                """, [employee_id, tax_year])
                result = self.dictfetchone(cursor)
            
            if not result:
                return Response({
                    "status": "error",
                    "message": "Tax profile not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                "status": "success",
                "data": result
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = EmployeeTaxProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                # Check if exists
                cursor.execute("""
                    SELECT profile_id FROM ci_my_employee_tax_profile
                    WHERE employee_id = %s AND tax_year = %s
                """, [data['employee_id'], data['tax_year']])
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE ci_my_employee_tax_profile SET
                            marital_status = %s, spouse_working = %s, spouse_disabled = %s,
                            number_of_children = %s, children_studying_higher = %s, children_disabled = %s,
                            disabled_self = %s,
                            epf_additional = %s, life_insurance = %s, education_insurance = %s,
                            medical_insurance = %s, sspn_deposit = %s, zakat_paid = %s,
                            updated_at = NOW()
                        WHERE employee_id = %s AND tax_year = %s
                    """, [
                        data.get('marital_status', 'single'), data.get('spouse_working', False), data.get('spouse_disabled', False),
                        data.get('number_of_children', 0), data.get('children_studying_higher', 0), data.get('children_disabled', 0),
                        data.get('disabled_self', False),
                        float(data.get('epf_additional', 0)), float(data.get('life_insurance', 0)), float(data.get('education_insurance', 0)),
                        float(data.get('medical_insurance', 0)), float(data.get('sspn_deposit', 0)), float(data.get('zakat_paid', 0)),
                        data['employee_id'], data['tax_year']
                    ])
                else:
                    cursor.execute("""
                        INSERT INTO ci_my_employee_tax_profile
                        (employee_id, tax_year, marital_status, spouse_working, spouse_disabled,
                         number_of_children, children_studying_higher, children_disabled, disabled_self,
                         epf_additional, life_insurance, education_insurance, medical_insurance, sspn_deposit, zakat_paid)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        data['employee_id'], data['tax_year'],
                        data.get('marital_status', 'single'), data.get('spouse_working', False), data.get('spouse_disabled', False),
                        data.get('number_of_children', 0), data.get('children_studying_higher', 0), data.get('children_disabled', 0),
                        data.get('disabled_self', False),
                        float(data.get('epf_additional', 0)), float(data.get('life_insurance', 0)), float(data.get('education_insurance', 0)),
                        float(data.get('medical_insurance', 0)), float(data.get('sspn_deposit', 0)), float(data.get('zakat_paid', 0))
                    ])
            
            return Response({
                "status": "success",
                "message": "Tax profile saved successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# ALLOWANCE & DEDUCTION TYPES
# =============================================================================

class AllowanceTypesView(BaseAPIView):
    """Manage allowance types configuration"""
    
    def get(self, request):
        company_id = request.query_params.get('company_id')
        
        try:
            with connection.cursor() as cursor:
                if company_id:
                    cursor.execute("""
                        SELECT * FROM ci_my_allowance_types
                        WHERE (company_id = %s OR company_id IS NULL)
                        AND is_active = 1
                        ORDER BY allowance_name
                    """, [company_id])
                else:
                    cursor.execute("""
                        SELECT * FROM ci_my_allowance_types
                        WHERE company_id IS NULL AND is_active = 1
                        ORDER BY allowance_name
                    """)
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = AllowanceTypeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_my_allowance_types
                    (company_id, allowance_code, allowance_name, is_taxable, epf_applicable,
                     socso_applicable, eis_applicable, description, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data.get('company_id'), data['allowance_code'], data['allowance_name'],
                    data.get('is_taxable', True), data.get('epf_applicable', True),
                    data.get('socso_applicable', True), data.get('eis_applicable', True),
                    data.get('description', ''), data.get('is_active', True)
                ])
            
            return Response({
                "status": "success",
                "message": "Allowance type created successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeductionTypesView(BaseAPIView):
    """Manage deduction types configuration"""
    
    def get(self, request):
        company_id = request.query_params.get('company_id')
        
        try:
            with connection.cursor() as cursor:
                if company_id:
                    cursor.execute("""
                        SELECT * FROM ci_my_deduction_types
                        WHERE (company_id = %s OR company_id IS NULL)
                        AND is_active = 1
                        ORDER BY deduction_name
                    """, [company_id])
                else:
                    cursor.execute("""
                        SELECT * FROM ci_my_deduction_types
                        WHERE company_id IS NULL AND is_active = 1
                        ORDER BY deduction_name
                    """)
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = DeductionTypeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_my_deduction_types
                    (company_id, deduction_code, deduction_name, is_statutory, affects_pcb, description, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [
                    data.get('company_id'), data['deduction_code'], data['deduction_name'],
                    data.get('is_statutory', False), data.get('affects_pcb', False),
                    data.get('description', ''), data.get('is_active', True)
                ])
            
            return Response({
                "status": "success",
                "message": "Deduction type created successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# EMPLOYEE ALLOWANCES & DEDUCTIONS
# =============================================================================

class EmployeeAllowancesView(BaseAPIView):
    """Manage employee monthly allowances"""
    
    def get(self, request, employee_id, month, year):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ea.*, at.allowance_name, at.allowance_code
                    FROM ci_my_employee_allowances ea
                    INNER JOIN ci_my_allowance_types at ON ea.allowance_type_id = at.allowance_type_id
                    WHERE ea.employee_id = %s AND ea.month = %s AND ea.year = %s
                """, [employee_id, month, year])
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = EmployeeAllowanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_my_employee_allowances
                    (employee_id, allowance_type_id, month, year, amount, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE amount = VALUES(amount), remarks = VALUES(remarks)
                """, [
                    data['employee_id'], data['allowance_type_id'],
                    data['month'], data['year'],
                    float(data['amount']), data.get('remarks', '')
                ])
            
            return Response({
                "status": "success",
                "message": "Allowance saved successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeDeductionsView(BaseAPIView):
    """Manage employee monthly deductions"""
    
    def get(self, request, employee_id, month, year):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ed.*, dt.deduction_name, dt.deduction_code
                    FROM ci_my_employee_deductions ed
                    INNER JOIN ci_my_deduction_types dt ON ed.deduction_type_id = dt.deduction_type_id
                    WHERE ed.employee_id = %s AND ed.month = %s AND ed.year = %s
                """, [employee_id, month, year])
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = EmployeeDeductionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_my_employee_deductions
                    (employee_id, deduction_type_id, month, year, amount, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE amount = VALUES(amount), remarks = VALUES(remarks)
                """, [
                    data['employee_id'], data['deduction_type_id'],
                    data['month'], data['year'],
                    float(data['amount']), data.get('remarks', '')
                ])
            
            return Response({
                "status": "success",
                "message": "Deduction saved successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# PAYROLL PROCESSING
# =============================================================================

class PayrollProcessView(BaseAPIView):
    """
    Process Malaysian payroll for a given period
    GET: Calculate payroll (preview)
    POST: Save processed payroll
    """
    
    def get(self, request, company_id, month, year):
        """Calculate payroll for all employees (preview mode)"""
        try:
            # Get employees
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        ud.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) as employee_name,
                        ud.gross_salary,
                        d.department_name,
                        ds.designation_name,
                        med.ic_number,
                        med.epf_member_no,
                        med.socso_member_no,
                        med.tax_reference_no,
                        med.worker_type
                    FROM ci_erp_users_details ud
                    INNER JOIN ci_erp_users u ON ud.user_id = u.id
                    LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                    LEFT JOIN ci_designations ds ON ud.designation_id = ds.designation_id
                    LEFT JOIN ci_my_employee_details med ON ud.employee_id = med.employee_id
                    WHERE ud.company_id = %s AND u.is_active = 1
                    ORDER BY u.first_name, u.last_name
                """, [company_id])
                employees = self.dictfetchall(cursor)
            
            processor = PayrollProcessor(company_id, month, year)
            results = []
            
            for emp in employees:
                basic_salary = self.safe_decimal(emp.get('gross_salary', 0))
                
                # Get allowances
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT allowance_type_id, amount
                        FROM ci_my_employee_allowances
                        WHERE employee_id = %s AND month = %s AND year = %s
                    """, [emp['employee_id'], month, year])
                    allowances = [{'type_id': r[0], 'amount': r[1]} for r in cursor.fetchall()]
                
                # Get deductions
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT dt.deduction_code, ed.amount
                        FROM ci_my_employee_deductions ed
                        INNER JOIN ci_my_deduction_types dt ON ed.deduction_type_id = dt.deduction_type_id
                        WHERE ed.employee_id = %s AND ed.month = %s AND ed.year = %s
                    """, [emp['employee_id'], month, year])
                    deductions_raw = cursor.fetchall()
                
                other_deductions = {}
                for ded in deductions_raw:
                    code = ded[0].lower()
                    if code == 'zkat':
                        other_deductions['zakat'] = float(ded[1])
                    elif code == 'loan':
                        other_deductions['loan'] = float(ded[1])
                    elif code == 'advs':
                        other_deductions['advance'] = float(ded[1])
                    elif code == 'cp38':
                        other_deductions['cp38'] = float(ded[1])
                    else:
                        other_deductions['other'] = other_deductions.get('other', 0) + float(ded[1])
                
                # Calculate payroll
                payroll = processor.process_employee(
                    emp['employee_id'],
                    basic_salary,
                    allowances=allowances,
                    other_deductions=other_deductions
                )
                
                # Add employee info
                payroll['employee_name'] = emp['employee_name']
                payroll['department_name'] = emp['department_name']
                payroll['designation_name'] = emp['designation_name']
                payroll['ic_number'] = emp.get('ic_number', '')
                
                # Convert Decimals to float for JSON
                for key in payroll:
                    if isinstance(payroll[key], Decimal):
                        payroll[key] = float(payroll[key])
                
                results.append(payroll)
            
            return Response({
                "status": "success",
                "data": results,
                "summary": {
                    "total_employees": len(results),
                    "total_gross": sum(r['gross_salary'] for r in results),
                    "total_net_pay": sum(r['net_pay'] for r in results),
                    "total_epf_employee": sum(r['epf_employee'] for r in results),
                    "total_epf_employer": sum(r['epf_employer'] for r in results),
                    "total_socso_employee": sum(r['socso_employee'] for r in results),
                    "total_socso_employer": sum(r['socso_employer'] for r in results),
                    "total_eis_employee": sum(r['eis_employee'] for r in results),
                    "total_eis_employer": sum(r['eis_employer'] for r in results),
                    "total_pcb": sum(r['pcb_amount'] + r.get('pcb_bonus', 0) for r in results),
                }
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Save processed payroll to database"""
        serializer = PayrollSaveRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        payroll_data = data['payroll_data']
        
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    for emp in payroll_data:
                        # Check if exists
                        cursor.execute("""
                            SELECT payroll_id FROM ci_my_payroll_report
                            WHERE employee_id = %s AND month = %s AND year = %s
                        """, [emp['employee_id'], data['month'], data['year']])
                        exists = cursor.fetchone()
                        
                        if exists:
                            # Update
                            cursor.execute("""
                                UPDATE ci_my_payroll_report SET
                                    employee_name = %s, ic_number = %s, tax_reference_no = %s,
                                    epf_member_no = %s, socso_member_no = %s,
                                    basic_salary = %s, fixed_allowances = %s, variable_allowances = %s,
                                    overtime_amount = %s, bonus = %s, commission = %s, incentives = %s,
                                    gross_salary = %s, epf_wages = %s, socso_wages = %s, eis_wages = %s,
                                    epf_employee = %s, epf_employer = %s,
                                    socso_employee = %s, socso_employer = %s,
                                    eis_employee = %s, eis_employer = %s,
                                    pcb_amount = %s, pcb_bonus = %s, hrdf_levy = %s,
                                    zakat = %s, loan_deduction = %s, advance_salary = %s,
                                    cp38_deduction = %s, other_deductions = %s,
                                    total_employee_statutory = %s, total_employer_statutory = %s,
                                    total_deductions = %s, total_earnings = %s, net_pay = %s,
                                    status = %s, updated_at = NOW()
                                WHERE employee_id = %s AND month = %s AND year = %s
                            """, [
                                emp.get('employee_name', ''), emp.get('ic_number', ''), emp.get('tax_reference_no', ''),
                                emp.get('epf_member_no', ''), emp.get('socso_member_no', ''),
                                emp.get('basic_salary', 0), emp.get('fixed_allowances', 0), emp.get('variable_allowances', 0),
                                emp.get('overtime_amount', 0), emp.get('bonus', 0), emp.get('commission', 0), emp.get('incentives', 0),
                                emp.get('gross_salary', 0), emp.get('epf_wages', 0), emp.get('socso_wages', 0), emp.get('eis_wages', 0),
                                emp.get('epf_employee', 0), emp.get('epf_employer', 0),
                                emp.get('socso_employee', 0), emp.get('socso_employer', 0),
                                emp.get('eis_employee', 0), emp.get('eis_employer', 0),
                                emp.get('pcb_amount', 0), emp.get('pcb_bonus', 0), emp.get('hrdf_levy', 0),
                                emp.get('zakat', 0), emp.get('loan_deduction', 0), emp.get('advance_salary', 0),
                                emp.get('cp38_deduction', 0), emp.get('other_deductions', 0),
                                emp.get('total_employee_statutory', 0), emp.get('total_employer_statutory', 0),
                                emp.get('total_deductions', 0), emp.get('total_earnings', 0), emp.get('net_pay', 0),
                                data.get('status', 'calculated'),
                                emp['employee_id'], data['month'], data['year']
                            ])
                        else:
                            # Insert
                            cursor.execute("""
                                INSERT INTO ci_my_payroll_report
                                (employee_id, employee_name, ic_number, tax_reference_no,
                                 epf_member_no, socso_member_no, month, year,
                                 basic_salary, fixed_allowances, variable_allowances,
                                 overtime_amount, bonus, commission, incentives,
                                 gross_salary, epf_wages, socso_wages, eis_wages,
                                 epf_employee, epf_employer, socso_employee, socso_employer,
                                 eis_employee, eis_employer, pcb_amount, pcb_bonus, hrdf_levy,
                                 zakat, loan_deduction, advance_salary, cp38_deduction, other_deductions,
                                 total_employee_statutory, total_employer_statutory,
                                 total_deductions, total_earnings, net_pay, status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, [
                                emp['employee_id'], emp.get('employee_name', ''), emp.get('ic_number', ''), emp.get('tax_reference_no', ''),
                                emp.get('epf_member_no', ''), emp.get('socso_member_no', ''), data['month'], data['year'],
                                emp.get('basic_salary', 0), emp.get('fixed_allowances', 0), emp.get('variable_allowances', 0),
                                emp.get('overtime_amount', 0), emp.get('bonus', 0), emp.get('commission', 0), emp.get('incentives', 0),
                                emp.get('gross_salary', 0), emp.get('epf_wages', 0), emp.get('socso_wages', 0), emp.get('eis_wages', 0),
                                emp.get('epf_employee', 0), emp.get('epf_employer', 0),
                                emp.get('socso_employee', 0), emp.get('socso_employer', 0),
                                emp.get('eis_employee', 0), emp.get('eis_employer', 0),
                                emp.get('pcb_amount', 0), emp.get('pcb_bonus', 0), emp.get('hrdf_levy', 0),
                                emp.get('zakat', 0), emp.get('loan_deduction', 0), emp.get('advance_salary', 0),
                                emp.get('cp38_deduction', 0), emp.get('other_deductions', 0),
                                emp.get('total_employee_statutory', 0), emp.get('total_employer_statutory', 0),
                                emp.get('total_deductions', 0), emp.get('total_earnings', 0), emp.get('net_pay', 0),
                                data.get('status', 'calculated')
                            ])
            
            return Response({
                "status": "success",
                "message": f"Payroll saved for {len(payroll_data)} employees"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PayrollReportView(BaseAPIView):
    """Get saved payroll report for a period"""
    
    def get(self, request, company_id, month, year):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        pr.*,
                        d.department_name,
                        ds.designation_name
                    FROM ci_my_payroll_report pr
                    LEFT JOIN ci_erp_users_details ud ON pr.employee_id = ud.employee_id
                    LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                    LEFT JOIN ci_designations ds ON ud.designation_id = ds.designation_id
                    WHERE ud.company_id = %s AND pr.month = %s AND pr.year = %s
                    ORDER BY pr.employee_name
                """, [company_id, month, year])
                results = self.dictfetchall(cursor)
            
            # Calculate summary
            summary = {
                "total_employees": len(results),
                "total_gross": sum(float(r.get('gross_salary', 0) or 0) for r in results),
                "total_net_pay": sum(float(r.get('net_pay', 0) or 0) for r in results),
                "total_epf_employee": sum(float(r.get('epf_employee', 0) or 0) for r in results),
                "total_epf_employer": sum(float(r.get('epf_employer', 0) or 0) for r in results),
                "total_socso_employee": sum(float(r.get('socso_employee', 0) or 0) for r in results),
                "total_socso_employer": sum(float(r.get('socso_employer', 0) or 0) for r in results),
                "total_eis_employee": sum(float(r.get('eis_employee', 0) or 0) for r in results),
                "total_eis_employer": sum(float(r.get('eis_employer', 0) or 0) for r in results),
                "total_pcb": sum(float(r.get('pcb_amount', 0) or 0) + float(r.get('pcb_bonus', 0) or 0) for r in results),
                "total_hrdf": sum(float(r.get('hrdf_levy', 0) or 0) for r in results),
            }
            
            return Response({
                "status": "success",
                "data": results,
                "summary": summary
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PayrollApproveView(BaseAPIView):
    """Approve payroll for a period"""
    
    def post(self, request, company_id, month, year):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_my_payroll_report pr
                    INNER JOIN ci_erp_users_details ud ON pr.employee_id = ud.employee_id
                    SET pr.status = 'approved', pr.updated_at = NOW()
                    WHERE ud.company_id = %s AND pr.month = %s AND pr.year = %s
                    AND pr.status = 'calculated'
                """, [company_id, month, year])
                affected = cursor.rowcount
            
            return Response({
                "status": "success",
                "message": f"Approved payroll for {affected} employees"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# PAYSLIP
# =============================================================================

class PayslipView(BaseAPIView):
    """Generate payslip for an employee"""
    
    def get(self, request, employee_id, month, year):
        try:
            with connection.cursor() as cursor:
                # Get payroll data
                cursor.execute("""
                    SELECT pr.*, 
                           d.department_name, ds.designation_name,
                           med.bank_name, med.bank_account_no
                    FROM ci_my_payroll_report pr
                    LEFT JOIN ci_erp_users_details ud ON pr.employee_id = ud.employee_id
                    LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                    LEFT JOIN ci_designations ds ON ud.designation_id = ds.designation_id
                    LEFT JOIN ci_my_employee_details med ON pr.employee_id = med.employee_id
                    WHERE pr.employee_id = %s AND pr.month = %s AND pr.year = %s
                """, [employee_id, month, year])
                payroll = self.dictfetchone(cursor)
                
                if not payroll:
                    return Response({
                        "status": "error",
                        "message": "Payroll record not found"
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Get company config
                cursor.execute("""
                    SELECT epf_employer_no, socso_employer_no
                    FROM ci_my_company_statutory_config csc
                    INNER JOIN ci_erp_users_details ud ON csc.company_id = ud.company_id
                    WHERE ud.employee_id = %s
                    LIMIT 1
                """, [employee_id])
                company = self.dictfetchone(cursor)
                
                # Get YTD data
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(gross_salary), 0) as ytd_gross,
                        COALESCE(SUM(epf_employee), 0) as ytd_epf,
                        COALESCE(SUM(pcb_amount + pcb_bonus), 0) as ytd_pcb
                    FROM ci_my_payroll_report
                    WHERE employee_id = %s AND year = %s AND month <= %s
                    AND status IN ('approved', 'paid')
                """, [employee_id, year, month])
                ytd = self.dictfetchone(cursor)
            
            # Build payslip response
            earnings = [
                {"description": "Basic Salary", "amount": float(payroll.get('basic_salary', 0) or 0)},
            ]
            if float(payroll.get('fixed_allowances', 0) or 0) > 0:
                earnings.append({"description": "Fixed Allowances", "amount": float(payroll['fixed_allowances'])})
            if float(payroll.get('variable_allowances', 0) or 0) > 0:
                earnings.append({"description": "Variable Allowances", "amount": float(payroll['variable_allowances'])})
            if float(payroll.get('overtime_amount', 0) or 0) > 0:
                earnings.append({"description": "Overtime", "amount": float(payroll['overtime_amount'])})
            if float(payroll.get('bonus', 0) or 0) > 0:
                earnings.append({"description": "Bonus", "amount": float(payroll['bonus'])})
            if float(payroll.get('commission', 0) or 0) > 0:
                earnings.append({"description": "Commission", "amount": float(payroll['commission'])})
            
            deductions = [
                {"description": "EPF (11%)", "amount": float(payroll.get('epf_employee', 0) or 0)},
                {"description": "SOCSO", "amount": float(payroll.get('socso_employee', 0) or 0)},
                {"description": "EIS", "amount": float(payroll.get('eis_employee', 0) or 0)},
                {"description": "PCB (Tax)", "amount": float(payroll.get('pcb_amount', 0) or 0) + float(payroll.get('pcb_bonus', 0) or 0)},
            ]
            if float(payroll.get('zakat', 0) or 0) > 0:
                deductions.append({"description": "Zakat", "amount": float(payroll['zakat'])})
            if float(payroll.get('loan_deduction', 0) or 0) > 0:
                deductions.append({"description": "Loan Repayment", "amount": float(payroll['loan_deduction'])})
            if float(payroll.get('other_deductions', 0) or 0) > 0:
                deductions.append({"description": "Other Deductions", "amount": float(payroll['other_deductions'])})
            
            employer_contributions = [
                {"description": "EPF Employer", "amount": float(payroll.get('epf_employer', 0) or 0)},
                {"description": "SOCSO Employer", "amount": float(payroll.get('socso_employer', 0) or 0)},
                {"description": "EIS Employer", "amount": float(payroll.get('eis_employer', 0) or 0)},
            ]
            if float(payroll.get('hrdf_levy', 0) or 0) > 0:
                employer_contributions.append({"description": "HRDF Levy", "amount": float(payroll['hrdf_levy'])})
            
            response = {
                "epf_employer_no": company.get('epf_employer_no', '') if company else '',
                "socso_employer_no": company.get('socso_employer_no', '') if company else '',
                "employee_id": employee_id,
                "employee_name": payroll.get('employee_name', ''),
                "ic_number": payroll.get('ic_number', ''),
                "epf_member_no": payroll.get('epf_member_no', ''),
                "socso_member_no": payroll.get('socso_member_no', ''),
                "tax_reference_no": payroll.get('tax_reference_no', ''),
                "department": payroll.get('department_name', ''),
                "designation": payroll.get('designation_name', ''),
                "bank_name": payroll.get('bank_name', ''),
                "bank_account_no": payroll.get('bank_account_no', ''),
                "month": month,
                "year": year,
                "earnings": earnings,
                "total_earnings": float(payroll.get('gross_salary', 0) or 0),
                "deductions": deductions,
                "total_deductions": float(payroll.get('total_deductions', 0) or 0),
                "employer_contributions": employer_contributions,
                "total_employer_contributions": float(payroll.get('total_employer_statutory', 0) or 0),
                "net_pay": float(payroll.get('net_pay', 0) or 0),
                "ytd_gross": float(ytd.get('ytd_gross', 0) or 0) if ytd else 0,
                "ytd_epf": float(ytd.get('ytd_epf', 0) or 0) if ytd else 0,
                "ytd_pcb": float(ytd.get('ytd_pcb', 0) or 0) if ytd else 0,
            }
            
            return Response({
                "status": "success",
                "data": response
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# STATUTORY FILE GENERATION
# =============================================================================

class EPFFormAView(BaseAPIView):
    """Generate EPF Form A text file"""
    
    def post(self, request):
        serializer = StatutoryFileRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # Validate first
            validation = FileValidationService.validate_epf_data(
                data['company_id'], data['month'], data['year']
            )
            
            if not validation['valid']:
                return Response({
                    "status": "error",
                    "message": "Validation failed",
                    "errors": validation['errors'],
                    "warnings": validation['warnings']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            generator = EPFFormAGenerator(data['company_id'], data['month'], data['year'])
            file_content, file_name, summary = generator.generate()
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EPFGIROView(BaseAPIView):
    """Generate EPF GIRO bank file"""
    
    def post(self, request):
        serializer = EPFGIRORequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            generator = EPFGIROGenerator(data['company_id'], data['month'], data['year'])
            file_content, file_name, summary = generator.generate(
                data['bank_code'], data['payment_date']
            )
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SOCSO8AView(BaseAPIView):
    """Generate SOCSO Form 8A text file"""
    
    def post(self, request):
        serializer = StatutoryFileRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            validation = FileValidationService.validate_socso_data(
                data['company_id'], data['month'], data['year']
            )
            
            if not validation['valid']:
                return Response({
                    "status": "error",
                    "message": "Validation failed",
                    "errors": validation['errors']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            generator = SOCSO8AGenerator(data['company_id'], data['month'], data['year'])
            file_content, file_name, summary = generator.generate()
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EISFileView(BaseAPIView):
    """Generate EIS contribution text file"""
    
    def post(self, request):
        serializer = StatutoryFileRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            generator = EISFileGenerator(data['company_id'], data['month'], data['year'])
            file_content, file_name, summary = generator.generate()
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CP39View(BaseAPIView):
    """Generate CP39 PCB deduction text file"""
    
    def post(self, request):
        serializer = StatutoryFileRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            validation = FileValidationService.validate_pcb_data(
                data['company_id'], data['month'], data['year']
            )
            
            if not validation['valid']:
                return Response({
                    "status": "error",
                    "message": "Validation failed",
                    "errors": validation['errors'],
                    "warnings": validation['warnings']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            generator = CP39Generator(data['company_id'], data['month'], data['year'])
            file_content, file_name, summary = generator.generate()
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EAFormView(BaseAPIView):
    """Generate EA Form PDF"""
    
    def get(self, request, employee_id, year):
        try:
            # Get company_id from employee
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ud.company_id FROM ci_erp_users_details ud
                    WHERE ud.employee_id = %s
                """, [employee_id])
                row = cursor.fetchone()
                
            if not row:
                return Response({
                    "status": "error",
                    "message": "Employee not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            generator = EAFormGenerator(row[0], None, year)
            pdf_bytes, file_name, summary = generator.generate(employee_id)
            
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except ImportError as e:
            return Response({
                "status": "error",
                "message": "PDF generation requires ReportLab library. Install with: pip install reportlab"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CP8DView(BaseAPIView):
    """Generate CP8D annual submission file"""
    
    def post(self, request):
        company_id = request.data.get('company_id')
        year = request.data.get('year')
        
        if not company_id or not year:
            return Response({
                "status": "error",
                "message": "company_id and year are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            generator = CP8DGenerator(company_id, None, year)
            file_content, file_name, summary = generator.generate()
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CP38View(BaseAPIView):
    """Generate CP38 salary deduction file"""
    
    def post(self, request):
        serializer = StatutoryFileRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            generator = CP38Generator(data['company_id'], data['month'], data['year'])
            file_content, file_name, summary = generator.generate()
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HRDFLevyView(BaseAPIView):
    """Generate HRDF levy file"""
    
    def post(self, request):
        serializer = StatutoryFileRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            generator = HRDFLevyGenerator(data['company_id'], data['month'], data['year'])
            file_content, file_name, summary = generator.generate()
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BankGIROView(BaseAPIView):
    """Generate Bank GIRO salary payment file"""
    
    def post(self, request):
        serializer = BankGIRORequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            generator = BankGIROGenerator(data['company_id'], data['month'], data['year'])
            file_content, file_name, summary = generator.generate(
                data['bank_code'], data['payment_date'], data['source_account']
            )
            
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatutoryFileLogView(BaseAPIView):
    """View statutory file generation history"""
    
    def get(self, request, company_id):
        file_type = request.query_params.get('file_type')
        year = request.query_params.get('year')
        
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT * FROM ci_my_statutory_file_log
                    WHERE company_id = %s
                """
                params = [company_id]
                
                if file_type:
                    query += " AND file_type = %s"
                    params.append(file_type)
                
                if year:
                    query += " AND year = %s"
                    params.append(year)
                
                query += " ORDER BY created_at DESC LIMIT 100"
                
                cursor.execute(query, params)
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# CP38 ORDERS & TP3 RECORDS
# =============================================================================

class CP38OrdersView(BaseAPIView):
    """Manage CP38 salary deduction orders"""
    
    def get(self, request, employee_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM ci_my_cp38_orders
                    WHERE employee_id = %s
                    ORDER BY start_year DESC, start_month DESC
                """, [employee_id])
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = CP38OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_my_cp38_orders
                    (employee_id, lhdn_reference, order_date, start_month, start_year,
                     end_month, end_year, monthly_amount, total_amount, balance_amount, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data['employee_id'], data['lhdn_reference'], data['order_date'],
                    data['start_month'], data['start_year'],
                    data.get('end_month'), data.get('end_year'),
                    float(data['monthly_amount']), float(data.get('total_amount', 0) or 0),
                    float(data.get('total_amount', 0) or 0), data.get('remarks', '')
                ])
            
            return Response({
                "status": "success",
                "message": "CP38 order created successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TP3RecordsView(BaseAPIView):
    """Manage TP3 previous employment records"""
    
    def get(self, request, employee_id, tax_year):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM ci_my_tp3_records
                    WHERE employee_id = %s AND tax_year = %s
                """, [employee_id, tax_year])
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = TP3RecordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ci_my_tp3_records
                    (employee_id, tax_year, previous_employer_name, previous_employer_e_number,
                     employment_start_date, employment_end_date, gross_remuneration,
                     epf_contribution, pcb_deducted, zakat_paid, cp38_deducted)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    data['employee_id'], data['tax_year'],
                    data['previous_employer_name'], data.get('previous_employer_e_number', ''),
                    data.get('employment_start_date'), data.get('employment_end_date'),
                    float(data['gross_remuneration']),
                    float(data.get('epf_contribution', 0)), float(data.get('pcb_deducted', 0)),
                    float(data.get('zakat_paid', 0)), float(data.get('cp38_deducted', 0))
                ])
            
            return Response({
                "status": "success",
                "message": "TP3 record created successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# FOREIGN WORKER MANAGEMENT
# =============================================================================

class ForeignWorkerExpiryView(BaseAPIView):
    """Track foreign worker document expiries"""
    
    def get(self, request, company_id):
        days_threshold = int(request.query_params.get('days', 30))
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        med.employee_id,
                        CONCAT(u.first_name, ' ', u.last_name) as employee_name,
                        med.worker_type,
                        med.work_permit_expiry,
                        med.visa_expiry,
                        med.fomema_expiry,
                        DATEDIFF(med.work_permit_expiry, CURDATE()) as days_to_work_permit_expiry,
                        DATEDIFF(med.visa_expiry, CURDATE()) as days_to_visa_expiry,
                        DATEDIFF(med.fomema_expiry, CURDATE()) as days_to_fomema_expiry
                    FROM ci_my_employee_details med
                    INNER JOIN ci_erp_users_details ud ON med.employee_id = ud.employee_id
                    INNER JOIN ci_erp_users u ON ud.user_id = u.id
                    WHERE ud.company_id = %s
                    AND med.worker_type IN ('foreign', 'expat')
                    AND med.is_active = 1
                    AND (
                        DATEDIFF(med.work_permit_expiry, CURDATE()) <= %s
                        OR DATEDIFF(med.visa_expiry, CURDATE()) <= %s
                        OR DATEDIFF(med.fomema_expiry, CURDATE()) <= %s
                    )
                    ORDER BY 
                        LEAST(
                            COALESCE(DATEDIFF(med.work_permit_expiry, CURDATE()), 999999),
                            COALESCE(DATEDIFF(med.visa_expiry, CURDATE()), 999999),
                            COALESCE(DATEDIFF(med.fomema_expiry, CURDATE()), 999999)
                        )
                """, [company_id, days_threshold, days_threshold, days_threshold])
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results,
                "threshold_days": days_threshold
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForeignWorkerListView(BaseAPIView):
    """List all foreign workers"""
    
    def get(self, request, company_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        med.*,
                        CONCAT(u.first_name, ' ', u.last_name) as employee_name,
                        d.department_name,
                        ds.designation_name
                    FROM ci_my_employee_details med
                    INNER JOIN ci_erp_users_details ud ON med.employee_id = ud.employee_id
                    INNER JOIN ci_erp_users u ON ud.user_id = u.id
                    LEFT JOIN ci_departments d ON ud.department_id = d.department_id
                    LEFT JOIN ci_designations ds ON ud.designation_id = ds.designation_id
                    WHERE ud.company_id = %s
                    AND med.worker_type IN ('foreign', 'expat', 'pr')
                    AND med.is_active = 1
                    ORDER BY u.first_name, u.last_name
                """, [company_id])
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# STATUTORY RATES MANAGEMENT
# =============================================================================

class EPFRatesView(BaseAPIView):
    """View/manage EPF contribution rates"""
    
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM ci_my_epf_rates
                    WHERE is_active = 1
                    ORDER BY wage_from
                """)
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create or update EPF rate entry"""
        data = request.data
        
        if not data.get('wage_from') or not data.get('wage_to'):
            return Response({
                "status": "error",
                "message": "wage_from and wage_to are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with connection.cursor() as cursor:
                # Check if exists
                cursor.execute("""
                    SELECT rate_id FROM ci_my_epf_rates
                    WHERE wage_from = %s AND wage_to = %s
                """, [data['wage_from'], data['wage_to']])
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE ci_my_epf_rates SET
                            employee_rate = %s, employer_rate_below_5k = %s, employer_rate_above_5k = %s,
                            is_active = %s
                        WHERE rate_id = %s
                    """, [
                        float(data.get('employee_rate', 11)), float(data.get('employer_rate_below_5k', 13)),
                        float(data.get('employer_rate_above_5k', 12)), data.get('is_active', True),
                        exists[0]
                    ])
                else:
                    cursor.execute("""
                        INSERT INTO ci_my_epf_rates
                        (wage_from, wage_to, employee_rate, employer_rate_below_5k, employer_rate_above_5k, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [
                        float(data['wage_from']), float(data['wage_to']),
                        float(data.get('employee_rate', 11)), float(data.get('employer_rate_below_5k', 13)),
                        float(data.get('employer_rate_above_5k', 12)), data.get('is_active', True)
                    ])
            
            return Response({
                "status": "success",
                "message": "EPF rate saved successfully"
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, rate_id):
        """Deactivate EPF rate"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ci_my_epf_rates SET is_active = 0 WHERE rate_id = %s
                """, [rate_id])
            
            return Response({"status": "success", "message": "Rate deactivated"})
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SOCSORatesView(BaseAPIView):
    """View/manage SOCSO contribution rates"""
    
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM ci_my_socso_rates
                    WHERE is_active = 1
                    ORDER BY wage_from
                """)
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create or update SOCSO rate entry"""
        data = request.data
        
        if not data.get('wage_from') or not data.get('wage_to'):
            return Response({
                "status": "error",
                "message": "wage_from and wage_to are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rate_id FROM ci_my_socso_rates
                    WHERE wage_from = %s AND wage_to = %s AND category = %s
                """, [data['wage_from'], data['wage_to'], data.get('category', 'category_1')])
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE ci_my_socso_rates SET
                            employee_rate = %s, employer_rate = %s, is_active = %s
                        WHERE rate_id = %s
                    """, [
                        float(data.get('employee_rate', 0)), float(data.get('employer_rate', 0)),
                        data.get('is_active', True), exists[0]
                    ])
                else:
                    cursor.execute("""
                        INSERT INTO ci_my_socso_rates
                        (category, wage_from, wage_to, employee_rate, employer_rate, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [
                        data.get('category', 'category_1'),
                        float(data['wage_from']), float(data['wage_to']),
                        float(data.get('employee_rate', 0)), float(data.get('employer_rate', 0)),
                        data.get('is_active', True)
                    ])
            
            return Response({"status": "success", "message": "SOCSO rate saved successfully"})
            
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EISRatesView(BaseAPIView):
    """View/manage EIS contribution rates"""
    
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM ci_my_eis_rates
                    WHERE is_active = 1
                    ORDER BY wage_from
                """)
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create or update EIS rate entry"""
        data = request.data
        
        if not data.get('wage_from') or not data.get('wage_to'):
            return Response({
                "status": "error",
                "message": "wage_from and wage_to are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rate_id FROM ci_my_eis_rates
                    WHERE wage_from = %s AND wage_to = %s
                """, [data['wage_from'], data['wage_to']])
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE ci_my_eis_rates SET
                            employee_rate = %s, employer_rate = %s, is_active = %s
                        WHERE rate_id = %s
                    """, [
                        float(data.get('employee_rate', 0.2)), float(data.get('employer_rate', 0.2)),
                        data.get('is_active', True), exists[0]
                    ])
                else:
                    cursor.execute("""
                        INSERT INTO ci_my_eis_rates
                        (wage_from, wage_to, employee_rate, employer_rate, is_active)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [
                        float(data['wage_from']), float(data['wage_to']),
                        float(data.get('employee_rate', 0.2)), float(data.get('employer_rate', 0.2)),
                        data.get('is_active', True)
                    ])
            
            return Response({"status": "success", "message": "EIS rate saved successfully"})
            
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PCBTaxBracketsView(BaseAPIView):
    """View/manage PCB tax brackets"""
    
    def get(self, request, tax_year):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM ci_my_pcb_tax_brackets
                    WHERE tax_year = %s AND is_active = 1
                    ORDER BY income_from
                """, [tax_year])
                results = self.dictfetchall(cursor)
            
            return Response({
                "status": "success",
                "data": results
            })
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create or update PCB tax bracket"""
        data = request.data
        
        required = ['tax_year', 'income_from', 'income_to', 'tax_rate']
        for field in required:
            if field not in data:
                return Response({
                    "status": "error",
                    "message": f"{field} is required"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT bracket_id FROM ci_my_pcb_tax_brackets
                    WHERE tax_year = %s AND income_from = %s AND income_to = %s
                """, [data['tax_year'], data['income_from'], data['income_to']])
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE ci_my_pcb_tax_brackets SET
                            tax_rate = %s, cumulative_tax = %s, is_active = %s
                        WHERE bracket_id = %s
                    """, [
                        float(data['tax_rate']), float(data.get('cumulative_tax', 0)),
                        data.get('is_active', True), exists[0]
                    ])
                else:
                    cursor.execute("""
                        INSERT INTO ci_my_pcb_tax_brackets
                        (tax_year, income_from, income_to, tax_rate, cumulative_tax, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [
                        data['tax_year'], float(data['income_from']), float(data['income_to']),
                        float(data['tax_rate']), float(data.get('cumulative_tax', 0)),
                        data.get('is_active', True)
                    ])
            
            return Response({"status": "success", "message": "Tax bracket saved successfully"})
            
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

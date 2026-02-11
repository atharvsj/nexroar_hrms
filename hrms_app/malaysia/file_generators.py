"""
Malaysian Statutory File Generators
====================================
Generates files for EPF, SOCSO, EIS, LHDN (CP39, EA Form, CP8D, etc.), HRDF, and Bank GIRO.
All file formats follow official specifications from respective statutory bodies.
"""

from decimal import Decimal
from datetime import date, datetime
from django.db import connection
from django.conf import settings
from typing import Dict, List, Optional, Tuple
import os
import io
import json

# For PDF generation (EA Form)
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch, cm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class BaseFileGenerator:
    """Base class for file generators"""
    
    def __init__(self, company_id: int, month: int = None, year: int = None):
        self.company_id = company_id
        self.month = month
        self.year = year
        self.company_config = self._get_company_config()
    
    def _get_company_config(self) -> Dict:
        """Get company statutory configuration"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    epf_employer_no,
                    socso_employer_no,
                    lhdn_e_number,
                    hrdf_registration_no
                FROM ci_my_company_statutory_config
                WHERE company_id = %s
            """, [self.company_id])
            row = cursor.fetchone()
            
        if row:
            return {
                'epf_employer_no': row[0] or '',
                'socso_employer_no': row[1] or '',
                'lhdn_e_number': row[2] or '',
                'hrdf_registration_no': row[3] or ''
            }
        return {}
    
    @staticmethod
    def safe_decimal(value, default="0.00") -> Decimal:
        try:
            if value is None:
                return Decimal(default)
            return Decimal(str(value))
        except:
            return Decimal(default)
    
    @staticmethod
    def format_amount(amount: Decimal, width: int = 10) -> str:
        """Format amount with leading zeros, no decimal point"""
        cents = int(amount * 100)
        return str(cents).zfill(width)
    
    @staticmethod
    def format_amount_decimal(amount: Decimal) -> str:
        """Format amount with 2 decimal places"""
        return f"{amount:.2f}"
    
    @staticmethod
    def pad_string(value: str, width: int, align: str = 'left') -> str:
        """Pad string to fixed width"""
        if align == 'left':
            return value[:width].ljust(width)
        return value[:width].rjust(width)
    
    def _log_generation(self, file_type: str, file_name: str, file_path: str,
                        record_count: int, employee_total: Decimal,
                        employer_total: Decimal, status: str = 'generated') -> int:
        """Log file generation to database"""
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ci_my_statutory_file_log 
                (file_type, company_id, month, year, file_name, file_path,
                 record_count, total_employee_amount, total_employer_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                file_type, self.company_id, self.month, self.year,
                file_name, file_path, record_count,
                float(employee_total), float(employer_total), status
            ])
            return cursor.lastrowid
    
    def _get_payroll_data(self) -> List[Dict]:
        """Get approved payroll data for the period"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pr.employee_id,
                    pr.employee_name,
                    pr.ic_number,
                    pr.tax_reference_no,
                    pr.epf_member_no,
                    pr.socso_member_no,
                    pr.epf_wages,
                    pr.socso_wages,
                    pr.eis_wages,
                    pr.epf_employee,
                    pr.epf_employer,
                    pr.socso_employee,
                    pr.socso_employer,
                    pr.eis_employee,
                    pr.eis_employer,
                    pr.pcb_amount,
                    pr.pcb_bonus,
                    pr.gross_salary,
                    med.nationality,
                    med.worker_type,
                    med.bank_code,
                    med.bank_account_no
                FROM ci_my_payroll_report pr
                LEFT JOIN ci_my_employee_details med ON pr.employee_id = med.employee_id
                WHERE pr.month = %s AND pr.year = %s
                AND pr.status IN ('approved', 'paid')
                ORDER BY pr.employee_name
            """, [self.month, self.year])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


class EPFFormAGenerator(BaseFileGenerator):
    """
    EPF Form A Text File Generator
    Format: Pipe-delimited text file as per KWSP specifications
    """
    
    FILE_TYPE = 'EPF_FORM_A'
    
    def generate(self) -> Tuple[str, str, Dict]:
        """
        Generate EPF Form A text file
        
        Returns:
            Tuple of (file_content, file_name, summary_dict)
        """
        payroll_data = self._get_payroll_data()
        
        output = io.StringIO()
        total_employee = Decimal('0')
        total_employer = Decimal('0')
        record_count = 0
        
        employer_no = self.company_config.get('epf_employer_no', '')
        contribution_month = f"{self.year}{self.month:02d}"
        
        # Header Record
        # Format: H|Employer No|Contribution Month|Record Count|Total Contribution
        # (Header written after processing to get totals)
        
        detail_lines = []
        
        for emp in payroll_data:
            epf_employee = self.safe_decimal(emp.get('epf_employee'))
            epf_employer = self.safe_decimal(emp.get('epf_employer'))
            
            if epf_employee <= 0 and epf_employer <= 0:
                continue
            
            total_employee += epf_employee
            total_employer += epf_employer
            record_count += 1
            
            # Detail Record Format:
            # D|EPF No|IC No|Employee Name|Wages|Employee Share|Employer Share
            epf_no = emp.get('epf_member_no', '') or ''
            ic_no = (emp.get('ic_number', '') or '').replace('-', '')
            emp_name = (emp.get('employee_name', '') or '').upper()[:60]
            wages = self.safe_decimal(emp.get('epf_wages'))
            
            detail_line = '|'.join([
                'D',
                epf_no[:12],
                ic_no[:12],
                emp_name,
                self.format_amount_decimal(wages),
                self.format_amount_decimal(epf_employee),
                self.format_amount_decimal(epf_employer)
            ])
            detail_lines.append(detail_line)
        
        # Write Header
        total_contribution = total_employee + total_employer
        header = '|'.join([
            'H',
            employer_no,
            contribution_month,
            str(record_count),
            self.format_amount_decimal(total_contribution)
        ])
        output.write(header + '\n')
        
        # Write Detail Records
        for line in detail_lines:
            output.write(line + '\n')
        
        # Write Trailer
        trailer = '|'.join([
            'T',
            str(record_count),
            self.format_amount_decimal(total_employee),
            self.format_amount_decimal(total_employer),
            self.format_amount_decimal(total_contribution)
        ])
        output.write(trailer)
        
        file_content = output.getvalue()
        file_name = f"EPF_FORMA_{employer_no}_{self.year}{self.month:02d}.txt"
        
        # Log generation
        self._log_generation(
            self.FILE_TYPE, file_name, '', record_count,
            total_employee, total_employer
        )
        
        return file_content, file_name, {
            'record_count': record_count,
            'total_employee': float(total_employee),
            'total_employer': float(total_employer),
            'total_contribution': float(total_contribution)
        }


class EPFGIROGenerator(BaseFileGenerator):
    """
    EPF GIRO Bank File Generator
    For bank payment of EPF contributions
    """
    
    FILE_TYPE = 'EPF_GIRO'
    
    def generate(self, bank_code: str, payment_date: str) -> Tuple[str, str, Dict]:
        """
        Generate EPF GIRO bank file
        
        Args:
            bank_code: Bank code for GIRO
            payment_date: Payment date (YYYYMMDD)
        """
        payroll_data = self._get_payroll_data()
        
        output = io.StringIO()
        total_amount = Decimal('0')
        record_count = 0
        
        employer_no = self.company_config.get('epf_employer_no', '')
        
        for emp in payroll_data:
            epf_total = self.safe_decimal(emp.get('epf_employee')) + \
                        self.safe_decimal(emp.get('epf_employer'))
            
            if epf_total <= 0:
                continue
            
            total_amount += epf_total
            record_count += 1
        
        # GIRO Header
        header = '|'.join([
            'EPF',
            employer_no,
            payment_date,
            self.format_amount_decimal(total_amount),
            str(record_count)
        ])
        output.write(header + '\n')
        
        file_content = output.getvalue()
        file_name = f"EPF_GIRO_{employer_no}_{payment_date}.txt"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', record_count,
            total_amount, Decimal('0')
        )
        
        return file_content, file_name, {
            'record_count': record_count,
            'total_amount': float(total_amount)
        }


class SOCSO8AGenerator(BaseFileGenerator):
    """
    SOCSO Form 8A Text File Generator
    Format: As per PERKESO specifications
    """
    
    FILE_TYPE = 'SOCSO_8A'
    
    def generate(self) -> Tuple[str, str, Dict]:
        """Generate SOCSO 8A text file"""
        payroll_data = self._get_payroll_data()
        
        output = io.StringIO()
        total_employee = Decimal('0')
        total_employer = Decimal('0')
        record_count = 0
        
        employer_no = self.company_config.get('socso_employer_no', '')
        contribution_period = f"{self.year}{self.month:02d}"
        
        detail_lines = []
        
        for emp in payroll_data:
            socso_employee = self.safe_decimal(emp.get('socso_employee'))
            socso_employer = self.safe_decimal(emp.get('socso_employer'))
            
            if socso_employee <= 0 and socso_employer <= 0:
                continue
            
            total_employee += socso_employee
            total_employer += socso_employer
            record_count += 1
            
            # SOCSO Number: For locals, IC number. For foreigners, SSN
            worker_type = emp.get('worker_type', 'local')
            if worker_type == 'local':
                socso_no = (emp.get('ic_number', '') or '').replace('-', '')
            else:
                socso_no = emp.get('socso_member_no', '') or ''
            
            ic_no = (emp.get('ic_number', '') or '').replace('-', '')
            emp_name = (emp.get('employee_name', '') or '').upper()[:60]
            wages = self.safe_decimal(emp.get('socso_wages'))
            
            # Determine category (1 = Both, 2 = Employer only)
            category = '1' if socso_employee > 0 else '2'
            
            detail_line = '|'.join([
                'D',
                socso_no[:12],
                ic_no[:12],
                emp_name,
                category,
                self.format_amount_decimal(wages),
                self.format_amount_decimal(socso_employee),
                self.format_amount_decimal(socso_employer)
            ])
            detail_lines.append(detail_line)
        
        # Header
        total_contribution = total_employee + total_employer
        header = '|'.join([
            'H',
            employer_no,
            contribution_period,
            str(record_count),
            self.format_amount_decimal(total_contribution)
        ])
        output.write(header + '\n')
        
        # Details
        for line in detail_lines:
            output.write(line + '\n')
        
        # Trailer
        trailer = '|'.join([
            'T',
            str(record_count),
            self.format_amount_decimal(total_employee),
            self.format_amount_decimal(total_employer),
            self.format_amount_decimal(total_contribution)
        ])
        output.write(trailer)
        
        file_content = output.getvalue()
        file_name = f"SOCSO_8A_{employer_no}_{self.year}{self.month:02d}.txt"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', record_count,
            total_employee, total_employer
        )
        
        return file_content, file_name, {
            'record_count': record_count,
            'total_employee': float(total_employee),
            'total_employer': float(total_employer),
            'total_contribution': float(total_contribution)
        }


class EISFileGenerator(BaseFileGenerator):
    """
    EIS Contribution File Generator
    Format: As per PERKESO EIS specifications
    """
    
    FILE_TYPE = 'EIS'
    
    def generate(self) -> Tuple[str, str, Dict]:
        """Generate EIS contribution text file"""
        payroll_data = self._get_payroll_data()
        
        output = io.StringIO()
        total_employee = Decimal('0')
        total_employer = Decimal('0')
        record_count = 0
        
        employer_no = self.company_config.get('socso_employer_no', '')
        contribution_period = f"{self.year}{self.month:02d}"
        
        detail_lines = []
        
        for emp in payroll_data:
            # Skip foreign workers (EIS not applicable)
            if emp.get('worker_type') == 'foreign':
                continue
            
            eis_employee = self.safe_decimal(emp.get('eis_employee'))
            eis_employer = self.safe_decimal(emp.get('eis_employer'))
            
            if eis_employee <= 0 and eis_employer <= 0:
                continue
            
            total_employee += eis_employee
            total_employer += eis_employer
            record_count += 1
            
            ic_no = (emp.get('ic_number', '') or '').replace('-', '')
            emp_name = (emp.get('employee_name', '') or '').upper()[:60]
            wages = self.safe_decimal(emp.get('eis_wages'))
            
            detail_line = '|'.join([
                'D',
                ic_no[:12],
                emp_name,
                self.format_amount_decimal(wages),
                self.format_amount_decimal(eis_employee),
                self.format_amount_decimal(eis_employer)
            ])
            detail_lines.append(detail_line)
        
        # Header
        total_contribution = total_employee + total_employer
        header = '|'.join([
            'H',
            employer_no,
            contribution_period,
            str(record_count),
            self.format_amount_decimal(total_contribution)
        ])
        output.write(header + '\n')
        
        # Details
        for line in detail_lines:
            output.write(line + '\n')
        
        # Trailer
        trailer = '|'.join([
            'T',
            str(record_count),
            self.format_amount_decimal(total_employee),
            self.format_amount_decimal(total_employer),
            self.format_amount_decimal(total_contribution)
        ])
        output.write(trailer)
        
        file_content = output.getvalue()
        file_name = f"EIS_{employer_no}_{self.year}{self.month:02d}.txt"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', record_count,
            total_employee, total_employer
        )
        
        return file_content, file_name, {
            'record_count': record_count,
            'total_employee': float(total_employee),
            'total_employer': float(total_employer),
            'total_contribution': float(total_contribution)
        }


class CP39Generator(BaseFileGenerator):
    """
    LHDN CP39 Monthly PCB Deduction File Generator
    """
    
    FILE_TYPE = 'CP39'
    
    def generate(self) -> Tuple[str, str, Dict]:
        """Generate CP39 PCB deduction text file"""
        payroll_data = self._get_payroll_data()
        
        output = io.StringIO()
        total_pcb = Decimal('0')
        record_count = 0
        
        e_number = self.company_config.get('lhdn_e_number', '')
        deduction_period = f"{self.year}{self.month:02d}"
        
        detail_lines = []
        
        for emp in payroll_data:
            pcb_amount = self.safe_decimal(emp.get('pcb_amount'))
            pcb_bonus = self.safe_decimal(emp.get('pcb_bonus'))
            total_emp_pcb = pcb_amount + pcb_bonus
            
            if total_emp_pcb <= 0:
                continue
            
            total_pcb += total_emp_pcb
            record_count += 1
            
            tax_file_no = emp.get('tax_reference_no', '') or ''
            ic_no = (emp.get('ic_number', '') or '').replace('-', '')
            emp_name = (emp.get('employee_name', '') or '').upper()[:60]
            
            # CP39 Detail Format
            # Tax File No | IC No | Name | PCB Amount | CP38 (if any)
            cp38 = Decimal('0')  # Would be fetched if applicable
            
            detail_line = '|'.join([
                'D',
                tax_file_no[:15],
                ic_no[:12],
                emp_name,
                self.format_amount_decimal(total_emp_pcb),
                self.format_amount_decimal(cp38)
            ])
            detail_lines.append(detail_line)
        
        # Header
        header = '|'.join([
            'H',
            e_number,
            deduction_period,
            str(record_count),
            self.format_amount_decimal(total_pcb)
        ])
        output.write(header + '\n')
        
        # Details
        for line in detail_lines:
            output.write(line + '\n')
        
        # Trailer
        trailer = '|'.join([
            'T',
            str(record_count),
            self.format_amount_decimal(total_pcb)
        ])
        output.write(trailer)
        
        file_content = output.getvalue()
        file_name = f"CP39_{e_number}_{self.year}{self.month:02d}.txt"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', record_count,
            total_pcb, Decimal('0')
        )
        
        return file_content, file_name, {
            'record_count': record_count,
            'total_pcb': float(total_pcb)
        }


class EAFormGenerator(BaseFileGenerator):
    """
    EA Form (Annual Tax Statement) Generator
    Generates PDF output
    """
    
    FILE_TYPE = 'EA_FORM'
    
    def _get_annual_data(self, employee_id: str) -> Dict:
        """Get annual cumulative data for an employee"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(gross_salary), 0) as total_gross,
                    COALESCE(SUM(basic_salary), 0) as total_basic,
                    COALESCE(SUM(bonus), 0) as total_bonus,
                    COALESCE(SUM(commission), 0) as total_commission,
                    COALESCE(SUM(fixed_allowances + variable_allowances), 0) as total_allowances,
                    COALESCE(SUM(epf_employee), 0) as total_epf_employee,
                    COALESCE(SUM(pcb_amount + pcb_bonus), 0) as total_pcb,
                    COALESCE(SUM(zakat), 0) as total_zakat,
                    COALESCE(SUM(cp38_deduction), 0) as total_cp38
                FROM ci_my_payroll_report
                WHERE employee_id = %s AND year = %s
                AND status IN ('approved', 'paid')
            """, [employee_id, self.year])
            row = cursor.fetchone()
            
        if row:
            return {
                'total_gross': self.safe_decimal(row[0]),
                'total_basic': self.safe_decimal(row[1]),
                'total_bonus': self.safe_decimal(row[2]),
                'total_commission': self.safe_decimal(row[3]),
                'total_allowances': self.safe_decimal(row[4]),
                'total_epf_employee': self.safe_decimal(row[5]),
                'total_pcb': self.safe_decimal(row[6]),
                'total_zakat': self.safe_decimal(row[7]),
                'total_cp38': self.safe_decimal(row[8])
            }
        return {}
    
    def _get_employee_details(self, employee_id: str) -> Dict:
        """Get employee details for EA form"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    med.ic_number,
                    med.tax_reference_no,
                    med.passport_number,
                    CONCAT(u.first_name, ' ', u.last_name) as full_name,
                    u.address_1,
                    u.address_2,
                    u.city,
                    u.state,
                    u.zipcode,
                    ud.date_of_joining
                FROM ci_my_employee_details med
                LEFT JOIN ci_erp_users_details ud ON med.employee_id = ud.employee_id
                LEFT JOIN ci_erp_users u ON ud.user_id = u.id
                WHERE med.employee_id = %s
            """, [employee_id])
            row = cursor.fetchone()
            
        if row:
            return {
                'ic_number': row[0] or '',
                'tax_reference_no': row[1] or '',
                'passport_number': row[2] or '',
                'full_name': row[3] or '',
                'address_1': row[4] or '',
                'address_2': row[5] or '',
                'city': row[6] or '',
                'state': row[7] or '',
                'zipcode': row[8] or '',
                'date_of_joining': row[9]
            }
        return {}
    
    def generate(self, employee_id: str) -> Tuple[bytes, str, Dict]:
        """
        Generate EA Form PDF for a single employee
        
        Returns:
            Tuple of (pdf_bytes, file_name, summary_dict)
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
        
        emp_details = self._get_employee_details(employee_id)
        annual_data = self._get_annual_data(employee_id)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                rightMargin=1*cm, leftMargin=1*cm,
                                topMargin=1*cm, bottomMargin=1*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            alignment=1
        )
        elements.append(Paragraph("STATEMENT OF REMUNERATION FROM EMPLOYMENT", title_style))
        elements.append(Paragraph("PENYATA SARAAN DARIPADA PENGGAJIAN", title_style))
        elements.append(Paragraph(f"(YEAR/TAHUN: {self.year})", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Employer Details
        e_number = self.company_config.get('lhdn_e_number', '')
        employer_data = [
            ['Employer\'s E Number / E Number Majikan:', e_number],
        ]
        employer_table = Table(employer_data, colWidths=[8*cm, 10*cm])
        employer_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(employer_table)
        elements.append(Spacer(1, 0.3*cm))
        
        # Employee Details
        employee_data = [
            ['Employee Name / Nama Pekerja:', emp_details.get('full_name', '')],
            ['IC Number / No. K/P:', emp_details.get('ic_number', '')],
            ['Tax Reference No. / No. Cukai Pendapatan:', emp_details.get('tax_reference_no', '')],
            ['Address / Alamat:', emp_details.get('address_1', '')],
            ['', f"{emp_details.get('city', '')} {emp_details.get('zipcode', '')} {emp_details.get('state', '')}"],
        ]
        emp_table = Table(employee_data, colWidths=[8*cm, 10*cm])
        emp_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(emp_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Remuneration Details
        elements.append(Paragraph("A. REMUNERATION / SARAAN", styles['Heading2']))
        
        remuneration_data = [
            ['Description / Butiran', 'Amount (RM) / Amaun (RM)'],
            ['1. Salary / Gaji', f"{annual_data.get('total_basic', 0):,.2f}"],
            ['2. Bonus / Bonus', f"{annual_data.get('total_bonus', 0):,.2f}"],
            ['3. Commission / Komisyen', f"{annual_data.get('total_commission', 0):,.2f}"],
            ['4. Allowances / Elaun', f"{annual_data.get('total_allowances', 0):,.2f}"],
            ['5. Total Gross Remuneration / Jumlah Saraan Kasar', 
             f"{annual_data.get('total_gross', 0):,.2f}"],
        ]
        rem_table = Table(remuneration_data, colWidths=[12*cm, 6*cm])
        rem_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        elements.append(rem_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Deductions
        elements.append(Paragraph("B. DEDUCTIONS / POTONGAN", styles['Heading2']))
        
        deduction_data = [
            ['Description / Butiran', 'Amount (RM) / Amaun (RM)'],
            ['1. EPF / KWSP', f"{annual_data.get('total_epf_employee', 0):,.2f}"],
            ['2. PCB / MTD Deducted / PCB Dipotong', f"{annual_data.get('total_pcb', 0):,.2f}"],
            ['3. Zakat Deducted / Zakat Dipotong', f"{annual_data.get('total_zakat', 0):,.2f}"],
            ['4. CP38 Deducted / CP38 Dipotong', f"{annual_data.get('total_cp38', 0):,.2f}"],
        ]
        ded_table = Table(deduction_data, colWidths=[12*cm, 6*cm])
        ded_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        elements.append(ded_table)
        
        # Build PDF
        doc.build(elements)
        
        pdf_bytes = buffer.getvalue()
        file_name = f"EA_FORM_{employee_id}_{self.year}.pdf"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', 1,
            annual_data.get('total_gross', Decimal('0')), Decimal('0')
        )
        
        return pdf_bytes, file_name, {
            'employee_id': employee_id,
            'year': self.year,
            'total_gross': float(annual_data.get('total_gross', 0)),
            'total_pcb': float(annual_data.get('total_pcb', 0))
        }


class CP8DGenerator(BaseFileGenerator):
    """
    CP8D Annual Submission File Generator
    Annual return of remuneration paid to employees
    """
    
    FILE_TYPE = 'CP8D'
    
    def generate(self) -> Tuple[str, str, Dict]:
        """Generate CP8D annual submission file"""
        e_number = self.company_config.get('lhdn_e_number', '')
        
        # Get all employees with payroll data for the year
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pr.employee_id,
                    MAX(med.ic_number) as ic_number,
                    MAX(med.tax_reference_no) as tax_file_no,
                    MAX(CONCAT(u.first_name, ' ', u.last_name)) as emp_name,
                    SUM(pr.gross_salary) as total_gross,
                    SUM(pr.epf_employee) as total_epf,
                    SUM(pr.pcb_amount + pr.pcb_bonus) as total_pcb,
                    SUM(pr.zakat) as total_zakat,
                    SUM(pr.cp38_deduction) as total_cp38,
                    MIN(ud.date_of_joining) as joining_date
                FROM ci_my_payroll_report pr
                LEFT JOIN ci_my_employee_details med ON pr.employee_id = med.employee_id
                LEFT JOIN ci_erp_users_details ud ON pr.employee_id = ud.employee_id
                LEFT JOIN ci_erp_users u ON ud.user_id = u.id
                WHERE pr.year = %s AND pr.status IN ('approved', 'paid')
                GROUP BY pr.employee_id
                ORDER BY emp_name
            """, [self.year])
            
            columns = [col[0] for col in cursor.description]
            employees = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        output = io.StringIO()
        total_gross = Decimal('0')
        total_pcb = Decimal('0')
        record_count = 0
        
        detail_lines = []
        
        for emp in employees:
            gross = self.safe_decimal(emp.get('total_gross'))
            total_gross += gross
            total_pcb += self.safe_decimal(emp.get('total_pcb'))
            record_count += 1
            
            ic_no = (emp.get('ic_number', '') or '').replace('-', '')
            tax_file = emp.get('tax_file_no', '') or ''
            emp_name = (emp.get('emp_name', '') or '').upper()[:60]
            
            # Format joining date
            joining_date = emp.get('joining_date')
            if joining_date:
                if isinstance(joining_date, str):
                    join_str = joining_date.replace('-', '')[:8]
                else:
                    join_str = joining_date.strftime('%Y%m%d')
            else:
                join_str = ''
            
            detail_line = '|'.join([
                'D',
                tax_file[:15],
                ic_no[:12],
                emp_name,
                self.format_amount_decimal(gross),
                self.format_amount_decimal(self.safe_decimal(emp.get('total_epf'))),
                self.format_amount_decimal(self.safe_decimal(emp.get('total_pcb'))),
                self.format_amount_decimal(self.safe_decimal(emp.get('total_zakat'))),
                self.format_amount_decimal(self.safe_decimal(emp.get('total_cp38'))),
                join_str
            ])
            detail_lines.append(detail_line)
        
        # Header
        header = '|'.join([
            'H',
            e_number,
            str(self.year),
            str(record_count),
            self.format_amount_decimal(total_gross),
            self.format_amount_decimal(total_pcb)
        ])
        output.write(header + '\n')
        
        # Details
        for line in detail_lines:
            output.write(line + '\n')
        
        # Trailer
        trailer = '|'.join([
            'T',
            str(record_count),
            self.format_amount_decimal(total_gross),
            self.format_amount_decimal(total_pcb)
        ])
        output.write(trailer)
        
        file_content = output.getvalue()
        file_name = f"CP8D_{e_number}_{self.year}.txt"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', record_count,
            total_gross, Decimal('0')
        )
        
        return file_content, file_name, {
            'record_count': record_count,
            'total_gross': float(total_gross),
            'total_pcb': float(total_pcb)
        }


class CP21Generator(BaseFileGenerator):
    """CP21 - Notification of Departure from Malaysia (for employees leaving)"""
    FILE_TYPE = 'CP21'
    # Implementation follows similar pattern


class CP22Generator(BaseFileGenerator):
    """CP22 - Notification of New Employee"""
    FILE_TYPE = 'CP22'
    # Implementation follows similar pattern


class CP22AGenerator(BaseFileGenerator):
    """CP22A - Notification of Cessation of Employment"""
    FILE_TYPE = 'CP22A'
    # Implementation follows similar pattern


class CP38Generator(BaseFileGenerator):
    """
    CP38 - Salary Deduction Order File
    For employees with LHDN deduction orders
    """
    
    FILE_TYPE = 'CP38'
    
    def generate(self) -> Tuple[str, str, Dict]:
        """Generate CP38 deduction file"""
        # Get active CP38 orders for employees
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    cp.employee_id,
                    cp.lhdn_reference,
                    cp.monthly_amount,
                    med.ic_number,
                    med.tax_reference_no,
                    CONCAT(u.first_name, ' ', u.last_name) as emp_name
                FROM ci_my_cp38_orders cp
                LEFT JOIN ci_my_employee_details med ON cp.employee_id = med.employee_id
                LEFT JOIN ci_erp_users_details ud ON cp.employee_id = ud.employee_id
                LEFT JOIN ci_erp_users u ON ud.user_id = u.id
                WHERE cp.status = 'active'
                AND (
                    (cp.start_year < %s) OR 
                    (cp.start_year = %s AND cp.start_month <= %s)
                )
                AND (
                    cp.end_year IS NULL OR cp.end_year > %s OR
                    (cp.end_year = %s AND cp.end_month >= %s)
                )
                ORDER BY emp_name
            """, [self.year, self.year, self.month, self.year, self.year, self.month])
            
            columns = [col[0] for col in cursor.description]
            orders = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        output = io.StringIO()
        total_amount = Decimal('0')
        record_count = len(orders)
        
        e_number = self.company_config.get('lhdn_e_number', '')
        
        detail_lines = []
        
        for order in orders:
            amount = self.safe_decimal(order.get('monthly_amount'))
            total_amount += amount
            
            ic_no = (order.get('ic_number', '') or '').replace('-', '')
            tax_file = order.get('tax_reference_no', '') or ''
            lhdn_ref = order.get('lhdn_reference', '') or ''
            emp_name = (order.get('emp_name', '') or '').upper()[:60]
            
            detail_line = '|'.join([
                'D',
                lhdn_ref,
                tax_file[:15],
                ic_no[:12],
                emp_name,
                self.format_amount_decimal(amount)
            ])
            detail_lines.append(detail_line)
        
        # Header
        header = '|'.join([
            'H',
            e_number,
            f"{self.year}{self.month:02d}",
            str(record_count),
            self.format_amount_decimal(total_amount)
        ])
        output.write(header + '\n')
        
        # Details
        for line in detail_lines:
            output.write(line + '\n')
        
        # Trailer
        trailer = '|'.join([
            'T',
            str(record_count),
            self.format_amount_decimal(total_amount)
        ])
        output.write(trailer)
        
        file_content = output.getvalue()
        file_name = f"CP38_{e_number}_{self.year}{self.month:02d}.txt"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', record_count,
            total_amount, Decimal('0')
        )
        
        return file_content, file_name, {
            'record_count': record_count,
            'total_amount': float(total_amount)
        }


class TP3Generator(BaseFileGenerator):
    """TP3 - Previous Employment Information Form"""
    FILE_TYPE = 'TP3'
    # Implementation for TP3 form generation


class HRDFLevyGenerator(BaseFileGenerator):
    """
    HRDF Levy File Generator
    """
    
    FILE_TYPE = 'HRDF'
    
    def generate(self) -> Tuple[str, str, Dict]:
        """Generate HRDF levy contribution file"""
        # Get total wages for HRDF calculation
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as emp_count,
                    SUM(gross_salary) as total_wages,
                    SUM(hrdf_levy) as total_levy
                FROM ci_my_payroll_report
                WHERE month = %s AND year = %s
                AND status IN ('approved', 'paid')
            """, [self.month, self.year])
            row = cursor.fetchone()
        
        emp_count = row[0] or 0
        total_wages = self.safe_decimal(row[1])
        total_levy = self.safe_decimal(row[2])
        
        output = io.StringIO()
        
        hrdf_reg_no = self.company_config.get('hrdf_registration_no', '')
        
        # HRDF File Format
        header = '|'.join([
            'H',
            hrdf_reg_no,
            f"{self.year}{self.month:02d}",
            str(emp_count),
            self.format_amount_decimal(total_wages),
            self.format_amount_decimal(total_levy)
        ])
        output.write(header)
        
        file_content = output.getvalue()
        file_name = f"HRDF_{hrdf_reg_no}_{self.year}{self.month:02d}.txt"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', emp_count,
            Decimal('0'), total_levy
        )
        
        return file_content, file_name, {
            'employee_count': emp_count,
            'total_wages': float(total_wages),
            'total_levy': float(total_levy)
        }


class BankGIROGenerator(BaseFileGenerator):
    """
    Bank GIRO File Generator for Salary Payment
    Supports multiple Malaysian banks as per Bank Negara list
    """
    
    FILE_TYPE = 'BANK_GIRO'
    
    def generate(self, bank_code: str, payment_date: str, 
                 source_account: str) -> Tuple[str, str, Dict]:
        """
        Generate Bank GIRO file for salary payment
        
        Args:
            bank_code: Bank code (e.g., MBBEMYKL for Maybank)
            payment_date: Payment date (YYYYMMDD)
            source_account: Source bank account number
        """
        payroll_data = self._get_payroll_data()
        
        output = io.StringIO()
        total_amount = Decimal('0')
        record_count = 0
        
        detail_lines = []
        
        for emp in payroll_data:
            net_pay = self.safe_decimal(emp.get('net_pay', 0))
            
            if net_pay <= 0:
                continue
            
            bank_account = emp.get('bank_account_no', '') or ''
            emp_bank_code = emp.get('bank_code', '') or ''
            emp_name = (emp.get('employee_name', '') or '').upper()[:40]
            
            if not bank_account:
                continue
            
            total_amount += net_pay
            record_count += 1
            
            # GIRO Detail Format (fixed width)
            # Account No (16) | Amount (15) | Name (40) | Bank Code (8) | Reference (20)
            reference = f"SAL{self.year}{self.month:02d}{emp.get('employee_id', '')}"
            
            detail_line = '|'.join([
                bank_account[:16].ljust(16),
                self.format_amount_decimal(net_pay).rjust(15),
                emp_name.ljust(40),
                emp_bank_code[:8].ljust(8),
                reference[:20].ljust(20)
            ])
            detail_lines.append(detail_line)
        
        # GIRO Header
        header = '|'.join([
            'H',
            bank_code,
            source_account[:16],
            payment_date,
            str(record_count),
            self.format_amount_decimal(total_amount)
        ])
        output.write(header + '\n')
        
        # Details
        for line in detail_lines:
            output.write(line + '\n')
        
        # Trailer
        trailer = '|'.join([
            'T',
            str(record_count),
            self.format_amount_decimal(total_amount)
        ])
        output.write(trailer)
        
        file_content = output.getvalue()
        file_name = f"GIRO_{bank_code}_{payment_date}.txt"
        
        self._log_generation(
            self.FILE_TYPE, file_name, '', record_count,
            total_amount, Decimal('0')
        )
        
        return file_content, file_name, {
            'record_count': record_count,
            'total_amount': float(total_amount),
            'payment_date': payment_date
        }


class FileValidationService:
    """
    Pre-validation service for statutory files
    Validates data before file generation
    """
    
    @staticmethod
    def validate_epf_data(company_id: int, month: int, year: int) -> Dict:
        """Validate data for EPF Form A generation"""
        errors = []
        warnings = []
        
        with connection.cursor() as cursor:
            # Check company EPF config
            cursor.execute("""
                SELECT epf_employer_no FROM ci_my_company_statutory_config
                WHERE company_id = %s
            """, [company_id])
            row = cursor.fetchone()
            
            if not row or not row[0]:
                errors.append("EPF Employer Number not configured")
            
            # Check employees without EPF numbers
            cursor.execute("""
                SELECT COUNT(*) FROM ci_my_payroll_report pr
                LEFT JOIN ci_my_employee_details med ON pr.employee_id = med.employee_id
                WHERE pr.month = %s AND pr.year = %s
                AND pr.status IN ('approved', 'paid')
                AND pr.epf_employee > 0
                AND (med.epf_member_no IS NULL OR med.epf_member_no = '')
            """, [month, year])
            count = cursor.fetchone()[0]
            
            if count > 0:
                warnings.append(f"{count} employee(s) have EPF contributions but no EPF member number")
            
            # Check employees without IC numbers
            cursor.execute("""
                SELECT COUNT(*) FROM ci_my_payroll_report pr
                LEFT JOIN ci_my_employee_details med ON pr.employee_id = med.employee_id
                WHERE pr.month = %s AND pr.year = %s
                AND pr.status IN ('approved', 'paid')
                AND pr.epf_employee > 0
                AND (med.ic_number IS NULL OR med.ic_number = '')
            """, [month, year])
            count = cursor.fetchone()[0]
            
            if count > 0:
                errors.append(f"{count} employee(s) have EPF contributions but no IC number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_socso_data(company_id: int, month: int, year: int) -> Dict:
        """Validate data for SOCSO 8A generation"""
        errors = []
        warnings = []
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT socso_employer_no FROM ci_my_company_statutory_config
                WHERE company_id = %s
            """, [company_id])
            row = cursor.fetchone()
            
            if not row or not row[0]:
                errors.append("SOCSO Employer Number not configured")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_pcb_data(company_id: int, month: int, year: int) -> Dict:
        """Validate data for CP39 generation"""
        errors = []
        warnings = []
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT lhdn_e_number FROM ci_my_company_statutory_config
                WHERE company_id = %s
            """, [company_id])
            row = cursor.fetchone()
            
            if not row or not row[0]:
                errors.append("LHDN E Number not configured")
            
            # Check employees without tax file numbers
            cursor.execute("""
                SELECT COUNT(*) FROM ci_my_payroll_report pr
                LEFT JOIN ci_my_employee_details med ON pr.employee_id = med.employee_id
                WHERE pr.month = %s AND pr.year = %s
                AND pr.status IN ('approved', 'paid')
                AND (pr.pcb_amount > 0 OR pr.pcb_bonus > 0)
                AND (med.tax_reference_no IS NULL OR med.tax_reference_no = '')
            """, [month, year])
            count = cursor.fetchone()[0]
            
            if count > 0:
                warnings.append(f"{count} employee(s) have PCB deductions but no Tax File Number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

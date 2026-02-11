# Malaysian Statutory Compliance & Payroll Module

Complete Malaysian payroll module for HRMS with statutory compliance for EPF (KWSP), SOCSO (PERKESO), EIS, LHDN (PCB/MTD), and HRDF (PSMB).

## Table of Contents
1. [Installation](#installation)
2. [Database Setup](#database-setup)
3. [API Endpoints](#api-endpoints)
4. [Statutory File Generation](#statutory-file-generation)
5. [Foreign Worker Management](#foreign-worker-management)

---

## Installation

The module is located at `hrms_app/malaysia/` and integrated with the main `hrms_app` URLs.

**Base URL:** `/hrms/my/`

---

## Database Setup

Execute the SQL statements in `DATABASE_TABLES.sql` to create the required tables:

```bash
mysql -u username -p database_name < DATABASE_TABLES.sql
```

**Tables Created:**
- `ci_my_company_statutory_config` - Company statutory registration numbers
- `ci_my_employee_details` - Malaysian employee details (IC, EPF/SOCSO numbers, bank info)
- `ci_my_employee_tax_profile` - PCB tax reliefs and deductions
- `ci_my_epf_rates` - EPF contribution table
- `ci_my_socso_rates` - SOCSO contribution table
- `ci_my_eis_rates` - EIS contribution table
- `ci_my_pcb_tax_brackets` - PCB tax brackets
- `ci_my_allowance_types` - Configured allowance types
- `ci_my_deduction_types` - Configured deduction types
- `ci_my_employee_allowances` - Monthly employee allowances
- `ci_my_employee_deductions` - Monthly employee deductions
- `ci_my_payroll_report` - Processed payroll records
- `ci_my_statutory_file_log` - File generation audit log
- `ci_my_employee_ytd` - Year-to-date balances
- `ci_my_cp38_orders` - LHDN CP38 salary deduction orders
- `ci_my_tp3_records` - TP3 previous employment records

---

## API Endpoints

### Company Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/company-config/{company_id}/` | Get company statutory config |
| POST | `/hrms/my/company-config/` | Create/Update company config |

**Request Body (POST):**
```json
{
  "company_id": 1,
  "epf_enabled": true,
  "epf_employer_no": "12345678901234",
  "socso_enabled": true,
  "socso_employer_no": "B3902056910M",
  "eis_enabled": true,
  "lhdn_enabled": true,
  "lhdn_e_number": "E9152876608",
  "hrdf_enabled": true,
  "hrdf_registration_no": "123456",
  "hrdf_levy_rate": 0.01
}
```

### Employee Details

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/employee-details/{employee_id}/` | Get Malaysian employee details |
| POST | `/hrms/my/employee-details/` | Create/Update employee details |
| GET | `/hrms/my/employees/{company_id}/` | List all employees with MY details |

**Request Body (POST):**
```json
{
  "employee_id": 123,
  "user_id": 456,
  "ic_number": "901231145678",
  "tax_reference_no": "SG12345678901",
  "epf_member_no": "12345678",
  "socso_member_no": "12345678901234",
  "worker_type": "local",
  "nationality": "Malaysian",
  "residency_status": "resident",
  "epf_contribution_type": "full",
  "socso_category": "category_1",
  "bank_code": "MBB",
  "bank_name": "Maybank",
  "bank_account_no": "164012345678"
}
```

### Employee Tax Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/tax-profile/{employee_id}/{tax_year}/` | Get employee tax profile |
| POST | `/hrms/my/tax-profile/` | Create/Update tax profile |

**Request Body (POST):**
```json
{
  "employee_id": 123,
  "tax_year": 2024,
  "marital_status": "married",
  "spouse_working": false,
  "number_of_children": 2,
  "children_studying_higher": 1,
  "disabled_self": false,
  "epf_additional": 0,
  "life_insurance": 3000,
  "medical_insurance": 2500,
  "sspn_deposit": 1000,
  "zakat_paid": 500
}
```

### Allowance & Deduction Types

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/allowance-types/?company_id=1` | List allowance types |
| POST | `/hrms/my/allowance-types/` | Create allowance type |
| GET | `/hrms/my/deduction-types/?company_id=1` | List deduction types |
| POST | `/hrms/my/deduction-types/` | Create deduction type |

### Employee Allowances & Deductions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/employee-allowances/{employee_id}/{month}/{year}/` | Get employee allowances |
| POST | `/hrms/my/employee-allowances/` | Save employee allowance |
| GET | `/hrms/my/employee-deductions/{employee_id}/{month}/{year}/` | Get employee deductions |
| POST | `/hrms/my/employee-deductions/` | Save employee deduction |

### Payroll Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/payroll/process/{company_id}/{month}/{year}/` | Calculate payroll (preview) |
| POST | `/hrms/my/payroll/save/` | Save calculated payroll |
| GET | `/hrms/my/payroll/report/{company_id}/{month}/{year}/` | Get payroll report |
| POST | `/hrms/my/payroll/approve/{company_id}/{month}/{year}/` | Approve payroll |
| GET | `/hrms/my/payslip/{employee_id}/{month}/{year}/` | Get employee payslip |

**Payroll Save Request:**
```json
{
  "company_id": 1,
  "month": 1,
  "year": 2024,
  "status": "calculated",
  "payroll_data": [
    {
      "employee_id": 123,
      "employee_name": "John Doe",
      "basic_salary": 5000,
      "gross_salary": 5500,
      "epf_employee": 550,
      "epf_employer": 715,
      "socso_employee": 19.75,
      "socso_employer": 69.05,
      "eis_employee": 9.90,
      "eis_employer": 9.90,
      "pcb_amount": 120,
      "net_pay": 4800.35
    }
  ]
}
```

---

## Statutory File Generation

### EPF Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hrms/my/statutory/epf-form-a/` | Generate EPF Form A text file |
| POST | `/hrms/my/statutory/epf-giro/` | Generate EPF GIRO bank file |

**EPF Form A Request:**
```json
{
  "company_id": 1,
  "month": 1,
  "year": 2024
}
```

**EPF GIRO Request:**
```json
{
  "company_id": 1,
  "month": 1,
  "year": 2024,
  "bank_code": "MBB",
  "payment_date": "2024-01-15"
}
```

### SOCSO Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hrms/my/statutory/socso-8a/` | Generate SOCSO Form 8A text file |

### EIS Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hrms/my/statutory/eis/` | Generate EIS contribution file |

### LHDN Tax Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hrms/my/statutory/cp39/` | Generate CP39 PCB deduction file |
| GET | `/hrms/my/statutory/ea-form/{employee_id}/{year}/` | Generate EA Form PDF |
| POST | `/hrms/my/statutory/cp8d/` | Generate CP8D annual submission |
| POST | `/hrms/my/statutory/cp38/` | Generate CP38 salary deduction file |

### HRDF Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hrms/my/statutory/hrdf-levy/` | Generate HRDF levy file |

### Bank GIRO

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hrms/my/statutory/bank-giro/` | Generate bank salary payment file |

**Bank GIRO Request:**
```json
{
  "company_id": 1,
  "month": 1,
  "year": 2024,
  "bank_code": "MBB",
  "payment_date": "2024-01-25",
  "source_account": "164012345678"
}
```

### File Generation Log

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/statutory/file-log/{company_id}/?file_type=EPF_FORM_A&year=2024` | View file generation history |

---

## Foreign Worker Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/foreign-workers/{company_id}/` | List all foreign workers |
| GET | `/hrms/my/foreign-workers/expiry/{company_id}/?days=30` | Get expiring documents alert |

**Expiry Alert Response:**
```json
{
  "status": "success",
  "data": [
    {
      "employee_id": 123,
      "employee_name": "Worker Name",
      "worker_type": "foreign",
      "work_permit_expiry": "2024-02-15",
      "visa_expiry": "2024-03-01",
      "fomema_expiry": "2024-01-31",
      "days_to_work_permit_expiry": 15,
      "days_to_visa_expiry": 30,
      "days_to_fomema_expiry": 1
    }
  ],
  "threshold_days": 30
}
```

---

## CP38 Orders & TP3 Records

### CP38 Orders (LHDN Salary Deduction Orders)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/cp38-orders/{employee_id}/` | List CP38 orders |
| POST | `/hrms/my/cp38-orders/` | Create CP38 order |

### TP3 Records (Previous Employment)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/tp3-records/{employee_id}/{tax_year}/` | Get TP3 records |
| POST | `/hrms/my/tp3-records/` | Create TP3 record |

---

## Statutory Rates Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/rates/epf/` | Get EPF contribution rates |
| GET | `/hrms/my/rates/socso/` | Get SOCSO contribution rates |
| GET | `/hrms/my/rates/eis/` | Get EIS contribution rates |
| GET | `/hrms/my/rates/pcb/{tax_year}/` | Get PCB tax brackets |

---

## Calculation Logic

### EPF (KWSP) Calculation
- **Employee Rate:** 11% (or 5.5% for <60 years old and >5000 monthly wage option)
- **Employer Rate:** 13% (if wages ≤ RM5,000), 12% (if wages > RM5,000)
- **Foreign Workers:** Optional, employer portion only
- **Age 60+:** Reduced rates apply

### SOCSO (PERKESO) Calculation
- **Category 1:** Employment Injury + Invalidity (age < 60)
- **Category 2:** Employment Injury only (age ≥ 60)
- **Ceiling:** RM5,000 per month
- **Foreign Workers:** Not applicable

### EIS Calculation
- **Rate:** 0.2% employee, 0.2% employer
- **Ceiling:** RM5,000 per month
- **Age 57+:** Not applicable
- **Foreign Workers:** Not applicable

### PCB (MTD) Calculation
- Follows LHDN MTD Schedule
- Considers tax reliefs (personal, spouse, children)
- YTD balancing mechanism
- TP3 support for mid-year joiners
- CP38 orders integration

### HRDF (PSMB) Levy
- **Rate:** 1% of monthly wages
- Employer contribution only
- Applicable to companies with 10+ employees

---

## File Formats

| File | Format | Specification |
|------|--------|--------------|
| EPF Form A | Pipe-delimited text | KWSP i-Akaun |
| SOCSO 8A | Pipe-delimited text | PERKESO ASSIST |
| EIS | Pipe-delimited text | PERKESO ASSIST |
| CP39 | Pipe-delimited text | e-PCB |
| CP8D | Pipe-delimited text | e-Filing |
| EA Form | PDF | LHDN specification |
| Bank GIRO | Pipe-delimited text | Bank-specific |

---

## Dependencies

- Django REST Framework
- Python Decimal (for financial calculations)
- ReportLab (for EA Form PDF generation) - Optional

```bash
pip install reportlab
```

---

## Notes

1. All APIs use raw SQL with `connection.cursor()` for database operations
2. Financial calculations use Python `Decimal` for precision
3. YTD tracking is automatic through the payroll processing
4. Statutory file formats follow official specifications
5. Foreign worker document expiry tracking is built-in

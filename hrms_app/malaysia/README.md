# Malaysian Statutory Compliance & Payroll Module

Complete Malaysian payroll module for HRMS with statutory compliance for EPF (KWSP), SOCSO (PERKESO), EIS, LHDN (PCB/MTD), and HRDF (PSMB).

## Table of Contents
1. [Installation](#installation)
2. [Database Setup](#database-setup)
3. [API Endpoints](#api-endpoints)
4. [Rate Management](#rate-management)
5. [Bulk Import](#bulk-import)
6. [Statutory File Generation](#statutory-file-generation)
7. [Email Alerts](#email-alerts)
8. [Foreign Worker Management](#foreign-worker-management)

---

## Installation

The module is located at `hrms_app/malaysia/` and integrated with the main `hrms_app` URLs.

**Base URL:** `/hrms/my/`

**Dependencies:**
```bash
pip install reportlab  # For EA Form PDF generation
```

---

## Database Setup

Execute the SQL statements in `DATABASE_TABLES.sql` to create the required tables:

```bash
mysql -u username -p database_name < hrms_app/malaysia/DATABASE_TABLES.sql
```

**Tables Created:**
| Table | Description |
|-------|-------------|
| `ci_my_company_statutory_config` | Company statutory registration numbers |
| `ci_my_employee_details` | Malaysian employee details (IC, EPF/SOCSO numbers, bank info) |
| `ci_my_employee_tax_profile` | PCB tax reliefs and deductions per employee |
| `ci_my_epf_rates` | EPF contribution table (updatable by HR) |
| `ci_my_socso_rates` | SOCSO contribution table (updatable by HR) |
| `ci_my_eis_rates` | EIS contribution table (updatable by HR) |
| `ci_my_pcb_tax_brackets` | PCB tax brackets by year (updatable by HR) |
| `ci_my_allowance_types` | Configured allowance types |
| `ci_my_deduction_types` | Configured deduction types |
| `ci_my_employee_allowances` | Monthly employee allowances |
| `ci_my_employee_deductions` | Monthly employee deductions |
| `ci_my_payroll_report` | Processed payroll records |
| `ci_my_statutory_file_log` | File generation audit log |
| `ci_my_employee_ytd` | Year-to-date balances |
| `ci_my_cp38_orders` | LHDN CP38 salary deduction orders |
| `ci_my_tp3_records` | TP3 previous employment records |

---

## Where Rate Values Come From

### Important Notes on Rate Data:

1. **No Government APIs Exist:** KWSP (EPF), PERKESO (SOCSO), and LHDN do NOT provide public APIs for contribution rates. They publish rates as PDF/Excel files that must be entered manually.

2. **Default Values:** The `DATABASE_TABLES.sql` file includes 2024 rates as INSERT statements. These are loaded when you run the SQL.

3. **HR Can Update Rates:** All rates are stored in database tables and can be updated by HR via API when government announces changes (usually annually in Budget).

### Rate Update Flow:
```
Government Announces New Rates (Budget/Gazette)
    ↓
HR Downloads PDF from Government Website
    ↓
HR Uses API to Update Rates in System
    ↓
System Uses Updated Rates for Calculations
```

---

## Rate Management

### View & Update Statutory Rates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/rates/epf/` | Get all EPF contribution rates |
| POST | `/hrms/my/rates/epf/` | Add/Update EPF rate |
| DELETE | `/hrms/my/rates/epf/{rate_id}/` | Deactivate EPF rate |
| GET | `/hrms/my/rates/socso/` | Get all SOCSO contribution rates |
| POST | `/hrms/my/rates/socso/` | Add/Update SOCSO rate |
| GET | `/hrms/my/rates/eis/` | Get all EIS contribution rates |
| POST | `/hrms/my/rates/eis/` | Add/Update EIS rate |
| GET | `/hrms/my/rates/pcb/{tax_year}/` | Get PCB tax brackets for year |
| POST | `/hrms/my/rates/pcb/` | Add/Update PCB tax bracket |

### EPF Rate Update Example:
```json
POST /hrms/my/rates/epf/
{
  "wage_from": 0,
  "wage_to": 30,
  "employee_rate": 11,
  "employer_rate_below_5k": 13,
  "employer_rate_above_5k": 12,
  "is_active": true
}
```

### PCB Tax Bracket Update Example:
```json
POST /hrms/my/rates/pcb/
{
  "tax_year": 2026,
  "income_from": 0,
  "income_to": 5000,
  "tax_rate": 0,
  "cumulative_tax": 0
}
```

---

## Bulk Import

### Bulk Employee Import
```json
POST /hrms/my/bulk-import/employees/
{
  "employees": [
    {
      "employee_id": 123,
      "user_id": 456,
      "ic_number": "901231145678",
      "epf_member_no": "12345678",
      "socso_member_no": "12345678901234",
      "tax_reference_no": "SG12345678901",
      "worker_type": "local",
      "nationality": "Malaysian",
      "bank_code": "MBB",
      "bank_account_no": "164012345678"
    },
    {
      "employee_id": 124,
      "user_id": 457,
      "ic_number": "851015086542",
      "worker_type": "foreign",
      "nationality": "Indonesian",
      "passport_number": "A12345678",
      "work_permit_number": "WP123456",
      "work_permit_expiry": "2026-12-31"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Processed 2 of 2 employees",
  "results": {
    "success": [
      {"index": 0, "employee_id": 123, "action": "created"},
      {"index": 1, "employee_id": 124, "action": "created"}
    ],
    "failed": [],
    "total": 2
  }
}
```

### Bulk Tax Profile Import
```json
POST /hrms/my/bulk-import/tax-profiles/
{
  "tax_year": 2026,
  "profiles": [
    {
      "employee_id": 123,
      "marital_status": "married",
      "spouse_working": false,
      "number_of_children": 2,
      "children_studying_higher": 1,
      "life_insurance": 3000,
      "medical_insurance": 2500
    }
  ]
}
```

### Bulk Rates Import
Import entire contribution tables at once:

```json
POST /hrms/my/bulk-import/rates/
{
  "rate_type": "pcb",
  "tax_year": 2027,
  "rates": [
    {"income_from": 0, "income_to": 5000, "tax_rate": 0, "cumulative_tax": 0},
    {"income_from": 5001, "income_to": 20000, "tax_rate": 1, "cumulative_tax": 0},
    {"income_from": 20001, "income_to": 35000, "tax_rate": 3, "cumulative_tax": 150},
    {"income_from": 35001, "income_to": 50000, "tax_rate": 6, "cumulative_tax": 600},
    {"income_from": 50001, "income_to": 70000, "tax_rate": 11, "cumulative_tax": 1500},
    {"income_from": 70001, "income_to": 100000, "tax_rate": 19, "cumulative_tax": 3700},
    {"income_from": 100001, "income_to": 400000, "tax_rate": 25, "cumulative_tax": 9400},
    {"income_from": 400001, "income_to": 600000, "tax_rate": 26, "cumulative_tax": 84400},
    {"income_from": 600001, "income_to": 2000000, "tax_rate": 28, "cumulative_tax": 136400},
    {"income_from": 2000001, "income_to": 999999999, "tax_rate": 30, "cumulative_tax": 528400}
  ]
}
```

---

## API Endpoints

### Company Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/company-config/{company_id}/` | Get company statutory config |
| POST | `/hrms/my/company-config/` | Create/Update company config |

### Employee Details

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/employee-details/{employee_id}/` | Get Malaysian employee details |
| POST | `/hrms/my/employee-details/` | Create/Update employee details |
| GET | `/hrms/my/employees/{company_id}/` | List all employees with MY details |

### Payroll Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/payroll/process/{company_id}/{month}/{year}/` | Calculate payroll (preview) |
| POST | `/hrms/my/payroll/save/` | Save calculated payroll |
| GET | `/hrms/my/payroll/report/{company_id}/{month}/{year}/` | Get payroll report |
| POST | `/hrms/my/payroll/approve/{company_id}/{month}/{year}/` | Approve payroll |
| GET | `/hrms/my/payslip/{employee_id}/{month}/{year}/` | Get employee payslip |

---

## Statutory File Generation

### EPF Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hrms/my/statutory/epf-form-a/` | Generate EPF Form A text file |
| POST | `/hrms/my/statutory/epf-giro/` | Generate EPF GIRO bank file |

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

### Other Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hrms/my/statutory/hrdf-levy/` | Generate HRDF levy file |
| POST | `/hrms/my/statutory/bank-giro/` | Generate bank salary payment file |

### File Formats

| File | Format | Portal |
|------|--------|--------|
| EPF Form A | Pipe-delimited `.txt` | i-Akaun (KWSP) |
| SOCSO 8A | Pipe-delimited `.txt` | ASSIST (PERKESO) |
| EIS | Pipe-delimited `.txt` | ASSIST (PERKESO) |
| CP39 | Pipe-delimited `.txt` | e-PCB (LHDN) |
| CP8D | Pipe-delimited `.txt` | e-Filing (LHDN) |
| EA Form | PDF | Manual/e-Filing |
| Bank GIRO | Pipe-delimited `.txt` | Bank Internet Banking |

---

## Email Alerts

### Document Expiry Alerts

Send email notifications to HR when foreign worker documents are expiring.

**Preview Expiring Documents:**
```
GET /hrms/my/alerts/document-expiry/{company_id}/?days=30
```

**Response:**
```json
{
  "status": "success",
  "threshold_days": 30,
  "summary": {
    "total_expiring": 5,
    "expired": 1,
    "critical_7_days": 2,
    "warning_14_days": 2
  },
  "hr_recipients": [
    {"email": "hr@company.com", "name": "HR Manager"}
  ],
  "expiring_documents": [...]
}
```

**Send Email Alerts:**
```json
POST /hrms/my/alerts/document-expiry/{company_id}/
{
  "days": 30,
  "send_to_employees": false,
  "custom_recipients": ["manager@company.com"]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Sent 3 email alerts",
  "emails_sent": 3,
  "recipients": ["hr@company.com", "admin@company.com", "manager@company.com"],
  "documents_flagged": 5
}
```

### Scheduled Alerts (Cron Job)

For automated daily alerts, call:
```
POST /hrms/my/alerts/scheduled-expiry/
```

This processes all companies and sends alerts. Add to crontab:
```bash
0 8 * * * curl -X POST http://your-server/hrms/my/alerts/scheduled-expiry/
```

---

## Foreign Worker Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hrms/my/foreign-workers/{company_id}/` | List all foreign workers |
| GET | `/hrms/my/foreign-workers/expiry/{company_id}/?days=30` | Get expiring documents |

---

## Default Values Summary

| Setting | Default Value | How to Change |
|---------|---------------|---------------|
| EPF Employee Rate | 11% | `POST /hrms/my/rates/epf/` |
| EPF Employer Rate (≤RM5000) | 13% | `POST /hrms/my/rates/epf/` |
| EPF Employer Rate (>RM5000) | 12% | `POST /hrms/my/rates/epf/` |
| SOCSO Ceiling | RM5,000 | Update `ci_my_socso_rates` table |
| EIS Rate | 0.2% each | `POST /hrms/my/rates/eis/` |
| HRDF Levy | 1% | `POST /hrms/my/company-config/` |
| PCB Tax Brackets | 2024 rates | `POST /hrms/my/rates/pcb/` or bulk import |
| Allowance Types | 10 default types | `POST /hrms/my/allowance-types/` |
| Deduction Types | 8 default types | `POST /hrms/my/deduction-types/` |

---

## Calculation Logic

### EPF (KWSP)
- **Employee:** 11% (5.5% optional for age 60+)
- **Employer:** 13% (if wages ≤ RM5,000), 12% (if wages > RM5,000)
- Uses contribution table lookup for exact amounts

### SOCSO (PERKESO)
- **Category 1:** Employment Injury + Invalidity (age < 60)
- **Category 2:** Employment Injury only (age ≥ 60)
- **Ceiling:** RM5,000/month

### EIS
- **Rate:** 0.2% employee + 0.2% employer
- **Ceiling:** RM5,000/month
- **Exclusions:** Age 57+, foreign workers

### PCB (MTD)
- Follows LHDN Schedule
- Considers reliefs: personal, spouse, children, EPF, insurance
- YTD balancing mechanism
- TP3 support for mid-year joiners

---

## Quick Start

1. **Create Tables:**
   ```bash
   mysql -u username -p database < hrms_app/malaysia/DATABASE_TABLES.sql
   ```

2. **Configure Company:**
   ```bash
   POST /hrms/my/company-config/
   {"company_id": 1, "epf_employer_no": "12345678901234", ...}
   ```

3. **Add Employee Details:**
   ```bash
   POST /hrms/my/bulk-import/employees/
   {"employees": [...]}
   ```

4. **Process Payroll:**
   ```bash
   GET /hrms/my/payroll/process/1/2/2026/
   ```

5. **Generate Files:**
   ```bash
   POST /hrms/my/statutory/epf-form-a/
   {"company_id": 1, "month": 2, "year": 2026}
   ```

---

## Notes

- All APIs use raw SQL with `connection.cursor()` for database operations
- Financial calculations use Python `Decimal` for precision
- Files follow official statutory format specifications
- Email alerts require Django email settings to be configured

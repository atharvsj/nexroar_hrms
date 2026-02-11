import random
from datetime import datetime, timedelta
import mysql.connector
from faker import Faker

fake = Faker("en_IN")

# ---------------- DB CONFIG ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",      # update if needed
    database="social_welfare"
)
cursor = conn.cursor()
NOW = datetime.now()

# ---------------- HELPERS ----------------
def rand_date(days_back=180):
    return NOW - timedelta(days=random.randint(0, days_back))

ai_flag_reasons = [
    "Missing documents",
    "High benefit amount",
    "Multiple active applications",
    "Age eligibility verification",
    "Category mismatch",
    "Income threshold exceeded"
]

# ---------------- ROLES ----------------
roles = ["Citizen", "Employee", "Leadership"]

for role in roles:
    cursor.execute(
        "INSERT INTO role (role_name, created_at) VALUES (%s, %s)",
        (role, NOW)
    )

ROLE_CITIZEN = 1
ROLE_EMPLOYEE = 2
ROLE_LEADERSHIP = 3

# ---------------- WARDS ----------------
zones = ["North", "South", "East", "West"]

for i in range(1, 11):
    cursor.execute(
        """
        INSERT INTO ward (ward_name, zone, eligible_population)
        VALUES (%s, %s, %s)
        """,
        (f"Ward-{i}", random.choice(zones), random.randint(8000, 16000))
    )

# ---------------- USERS ----------------
citizen_user_ids = []

# Employees
for _ in range(12):
    cursor.execute(
        """
        INSERT INTO user (name, role, ward_id, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (fake.name(), ROLE_EMPLOYEE, random.randint(1, 10), rand_date())
    )

# Leadership
for _ in range(4):
    cursor.execute(
        """
        INSERT INTO user (name, role, ward_id, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (fake.name(), ROLE_LEADERSHIP, random.randint(1, 10), rand_date())
    )

# Citizens
for _ in range(100):
    name = fake.name()
    ward_id = random.randint(1, 10)

    cursor.execute(
        """
        INSERT INTO user (name, role, ward_id, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (name, ROLE_CITIZEN, ward_id, rand_date())
    )

    user_id = cursor.lastrowid
    citizen_user_ids.append(user_id)

    cursor.execute(
        """
        INSERT INTO citizen
        (citizen_id, name, ward_id, age, gender, category,
         is_vulnerable, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            user_id,
            name,
            ward_id,
            random.randint(18, 80),
            random.choice([0, 1]),
            random.choice(["General", "SC", "ST", "OBC"]),
            random.choice([0, 0, 1]),
            rand_date()
        )
    )

# ---------------- SCHEMES (INDIAN GOVT) ----------------
schemes = [
    ("PM Jan Dhan Yojana", "finance", 20),
    ("PM Awas Yojana", "housing", 60),
    ("Ayushman Bharat", "health", 30),
    ("Mid Day Meal Scheme", "nutrition", 15),
    ("PM Kisan Samman Nidhi", "agriculture", 25),
    ("Beti Bachao Beti Padhao", "education", 35),
]

for s in schemes:
    cursor.execute(
        """
        INSERT INTO scheme (scheme_name, category, sla_days, is_active)
        VALUES (%s, %s, %s, 1)
        """,
        s
    )

# ---------------- APPLICATIONS ----------------
application_ids = []
statuses = ["Submitted", "In-Review", "Approved", "Rejected"]

for citizen_id in citizen_user_ids:
    for _ in range(random.randint(2, 3)):
        scheme_id = random.randint(1, len(schemes))
        status = random.choice(statuses)

        submitted_at = rand_date(120)
        sla_days = random.randint(15, 60)
        sla_due_date = submitted_at + timedelta(days=sla_days)

        is_breached = 1 if (NOW > sla_due_date and status != "Approved") else 0
        is_flagged = random.choice([0, 0, 0, 1])

        cursor.execute(
            """
            INSERT INTO application
            (citizen_id, scheme_id, status, submitted_at,
             last_updated_at, sla_due_date,
             flagged_by_ai, is_sla_breached, ai_flag_reason)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                citizen_id,
                scheme_id,
                status,
                submitted_at,
                submitted_at + timedelta(days=random.randint(2, 8)),
                sla_due_date,
                is_flagged,
                is_breached,
                random.choice(ai_flag_reasons) if is_flagged else None
            )
        )

        application_ids.append(cursor.lastrowid)

# ---------------- BENEFITS ----------------
for app_id in application_ids:
    if random.random() < 0.55:
        cursor.execute(
            """
            INSERT INTO benefit
            (application_id, amount, status, disbursed_at)
            VALUES (%s,%s,%s,%s)
            """,
            (
                app_id,
                random.randint(2000, 30000),
                random.choice(["Pending", "Disbursed", "Failed"]),
                str(rand_date(30))
            )
        )

# ---------------- GRIEVANCES ----------------
grievance_categories = ["Delay", "Rejection", "Payment"]
grievance_status = ["Open", "In-progress", "Resolved"]

for _ in range(50):
    created = rand_date(90)
    resolved = created + timedelta(days=random.randint(3, 20))

    cursor.execute(
        """
        INSERT INTO grievance
        (citizen_id, related_application_id, category,
         status, created_at, resolved_at)
        VALUES (%s,%s,%s,%s,%s,%s)
        """,
        (
            random.choice(citizen_user_ids),
            random.choice(application_ids),
            random.choice(grievance_categories),
            random.choice(grievance_status),
            created,
            resolved
        )
    )

conn.commit()
cursor.close()
conn.close()

print("✅ Social welfare database seeded with analytics-ready data.")

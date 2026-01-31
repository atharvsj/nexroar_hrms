import pymysql

# Database connection configuration
db_config = {
    "host": "ls-f8259bafe38561c18d0d411f37aefbfabc0ff7bf.citdgny2wnek.ap-south-1.rds.amazonaws.com",
    "user": "dbmasteruser",
    "password": "database9014",
    "database": "new_hrms"
}

# String to search (column name or data value)
search_string = "client"  # e.g., "email", "user_id", or any keyword

try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"\n🔍 Searching for '{search_string}' in the database '{db_config['database']}'...\n")

    for table in tables:

        if table == 'ci_activity_data':
            continue

        # Check if search_string is in column names
        cursor.execute(f"SHOW COLUMNS FROM `{table}`")
        columns = cursor.fetchall()
        for column in columns:
            if search_string.lower() in column[0].lower():
                print(f"✅ Column match: Table `{table}`, Column `{column[0]}`")

        # Optional: Search inside text columns (like VARCHAR, TEXT)
        for column in columns:
            col_name = column[0]
            col_type = column[1]

            if any(t in col_type.lower() for t in ['char', 'text']):
                try:
                    cursor.execute(f"SELECT `{col_name}` FROM `{table}` WHERE `{col_name}` LIKE %s LIMIT 1", ('%' + search_string + '%',))
                    result = cursor.fetchone()
                    if result:
                        print(f"🔎 Value match in table `{table}`, column `{col_name}` → Value: {result[0]}")
                except Exception as e:
                    pass  # Skip any column that throws error (e.g., binary/blob)

except Exception as e:
    print(f"❌ Error: {str(e)}")

finally:
    if 'conn' in locals():
        conn.close()

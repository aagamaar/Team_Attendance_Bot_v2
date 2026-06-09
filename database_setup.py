import sqlite3

# Create database connection
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Drop existing tables to start fresh (WARNING: This deletes all data)
print("🗑️ Dropping existing tables...")
cursor.execute("DROP TABLE IF EXISTS attendance")
cursor.execute("DROP TABLE IF EXISTS employees")
cursor.execute("DROP TABLE IF EXISTS organizations")
cursor.execute("DROP TABLE IF EXISTS monthly_summary")

print("📦 Creating new tables with proper structure...")

# Create organizations table
cursor.execute('''
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    join_code TEXT UNIQUE,
    owner_telegram_id INTEGER,
    created_at TEXT DEFAULT CURRENT_DATE
)
''')

# Create employees table - WITH ALL COLUMNS INCLUDED
cursor.execute('''
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    org_id INTEGER,
    telegram_id INTEGER,
    name TEXT,
    email TEXT,
    department TEXT,
    join_date TEXT DEFAULT CURRENT_DATE,
    joined_at TEXT DEFAULT CURRENT_DATE,
    leave_balance INTEGER DEFAULT 4,
    total_present INTEGER DEFAULT 0,
    total_leaves_taken INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    is_admin INTEGER DEFAULT 0,
    FOREIGN KEY (org_id) REFERENCES organizations(id)
)
''')

# Create attendance table
cursor.execute('''
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    date TEXT,
    status TEXT,
    marked_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    UNIQUE(employee_id, date)
)
''')

# Create monthly_summary table for quick reporting
cursor.execute('''
CREATE TABLE monthly_summary (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER,
    year INTEGER,
    month INTEGER,
    present_count INTEGER DEFAULT 0,
    leave_count INTEGER DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    UNIQUE(employee_id, year, month)
)
''')

# Added after creating tables
cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_org ON employees(org_id)')

print("✅ Database setup complete!")
print("\n📊 Tables created with ALL columns:")
print("- organizations (companies)")
print("- employees (team members with joined_at, email, department, etc.)")
print("- attendance (daily records)")
print("- monthly_summary (quick reports)")

conn.commit()
conn.close()

print("\n🎯 You can now run: python bot.py")
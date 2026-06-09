# database.py
import sqlite3
from datetime import date
import secrets
import string

# Database connection (global so all functions can use it)
conn = sqlite3.connect('attendance.db', check_same_thread=False)
cursor = conn.cursor()

def generate_join_code():
    """Generate a random 6-character join code"""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(6))

def get_employee(telegram_id):
    """Get employee record by Telegram ID
    Returns: (id, org_id, name, leave_balance, is_admin, org_name, join_code, department, email)
    """
    cursor.execute('''
        SELECT e.id, e.org_id, e.name, e.leave_balance, e.is_admin, 
               o.name, o.join_code, e.department, e.email
        FROM employees e
        JOIN organizations o ON e.org_id = o.id
        WHERE e.telegram_id = ?
    ''', (telegram_id,))
    return cursor.fetchone()

def get_organization(org_id):
    """Get organization details
    Returns: (id, name, join_code, owner_telegram_id)
    """
    cursor.execute('''
        SELECT id, name, join_code, owner_telegram_id 
        FROM organizations 
        WHERE id = ?
    ''', (org_id,))
    return cursor.fetchone()

def get_employees_by_org(org_id):
    """Get all employees in an organization
    Returns: List of (id, name, is_admin, leave_balance, department, email)
    """
    cursor.execute('''
        SELECT id, name, is_admin, leave_balance, department, email
        FROM employees 
        WHERE org_id = ? AND is_active = 1
        ORDER BY is_admin DESC, name
    ''', (org_id,))
    return cursor.fetchall()

def is_weekend(dt):
    """Check if date is weekend (Saturday=5, Sunday=6)"""
    return dt.weekday() >= 5

def reset_balance_if_needed(employee_id):
    """Reset leave balance on the 1st of each month"""
    today = date.today()
    if today.day == 1:
        cursor.execute("UPDATE employees SET leave_balance = 4 WHERE id = ?", (employee_id,))
        conn.commit()
        return True
    return False

def update_employee_stats(employee_id):
    """Update total_present and total_leaves_taken for an employee"""
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
            SUM(CASE WHEN status = 'leave' THEN 1 ELSE 0 END) as leave_count
        FROM attendance
        WHERE employee_id = ?
    ''', (employee_id,))
    result = cursor.fetchone()
    present = result[0] if result[0] else 0
    leaves = result[1] if result[1] else 0
    
    cursor.execute('''
        UPDATE employees 
        SET total_present = ?, total_leaves_taken = ?
        WHERE id = ?
    ''', (present, leaves, employee_id))
    conn.commit()

def mark_attendance(employee_id, status):
    """Mark attendance for an employee
    Returns: (success, message)
    """
    today_str = date.today().isoformat()
    
    # Check if already marked
    cursor.execute("SELECT * FROM attendance WHERE employee_id = ? AND date = ?", (employee_id, today_str))
    if cursor.fetchone():
        return False, "Already marked today!"
    
    # Insert attendance record
    cursor.execute('''
        INSERT INTO attendance (employee_id, date, status)
        VALUES (?, ?, ?)
    ''', (employee_id, today_str, status))
    conn.commit()
    
    # Update employee stats
    update_employee_stats(employee_id)
    
    return True, "Success"

def take_leave(employee_id):
    """Process leave request
    Returns: (success, message)
    """
    # Get current balance
    cursor.execute("SELECT leave_balance FROM employees WHERE id = ?", (employee_id,))
    result = cursor.fetchone()
    balance = result[0] if result else 0
    
    if balance <= 0:
        return False, "No leaves left this month!"
    
    # Mark leave (this also updates stats)
    success, message = mark_attendance(employee_id, 'leave')
    if not success:
        return False, message
    
    # Reduce balance
    cursor.execute("UPDATE employees SET leave_balance = leave_balance - 1 WHERE id = ?", (employee_id,))
    conn.commit()
    
    new_balance = balance - 1
    return True, f"Leave marked! {new_balance} leaves remaining."

def get_today_stats(org_id):
    """Get today's attendance statistics for an organization
    Returns: (stats_list, present_count, leave_count, absent_count)
    """
    today_str = date.today().isoformat()
    
    cursor.execute("SELECT id, name FROM employees WHERE org_id = ? AND is_active = 1", (org_id,))
    employees = cursor.fetchall()
    
    stats = []
    present_count = 0
    leave_count = 0
    absent_count = 0
    
    for emp_id, emp_name in employees:
        cursor.execute("SELECT status FROM attendance WHERE employee_id = ? AND date = ?", (emp_id, today_str))
        result = cursor.fetchone()
        status = result[0] if result else "absent"
        
        stats.append((emp_name, status))
        
        if status == 'present':
            present_count += 1
        elif status == 'leave':
            leave_count += 1
        else:
            absent_count += 1
    
    return stats, present_count, leave_count, absent_count

def get_monthly_stats(org_id):
    """Get monthly statistics for an organization
    Returns: List of (name, present_count, leave_count, balance)
    """
    current_month = date.today().strftime("%Y-%m")
    
    cursor.execute("SELECT id, name FROM employees WHERE org_id = ? AND is_active = 1", (org_id,))
    employees = cursor.fetchall()
    
    monthly_stats = []
    
    for emp_id, emp_name in employees:
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN status = 'leave' THEN 1 ELSE 0 END) as leave_count
            FROM attendance
            WHERE employee_id = ? AND strftime('%Y-%m', date) = ?
        ''', (emp_id, current_month))
        result = cursor.fetchone()
        present = result[0] if result[0] else 0
        leaves = result[1] if result[1] else 0
        
        cursor.execute("SELECT leave_balance FROM employees WHERE id = ?", (emp_id,))
        balance_result = cursor.fetchone()
        balance = balance_result[0] if balance_result else 4
        
        monthly_stats.append((emp_name, present, leaves, balance))
    
    return monthly_stats

def delete_employee_record(employee_id):
    """Delete employee and all related records"""
    cursor.execute("DELETE FROM attendance WHERE employee_id = ?", (employee_id,))
    cursor.execute("DELETE FROM monthly_summary WHERE employee_id = ?", (employee_id,))
    cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()

# Helper function to get employee by ID (not Telegram ID)
def get_employee_by_id(employee_id):
    """Get employee record by internal ID"""
    cursor.execute('''
        SELECT e.id, e.org_id, e.name, e.leave_balance, e.is_admin, 
               o.name, e.department, e.email
        FROM employees e
        JOIN organizations o ON e.org_id = o.id
        WHERE e.id = ?
    ''', (employee_id,))
    return cursor.fetchone()
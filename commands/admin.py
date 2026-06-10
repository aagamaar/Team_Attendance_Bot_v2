# commands/admin.py
from telegram import Update
from telegram.ext import ContextTypes
from utils import is_rate_limited
from database import cursor, conn, get_employee, today_ist
from datetime import date

async def admin_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee or not employee[4]:
        await update.message.reply_text("👑 Admin access required.")
        return
    
    employee_id, org_id, name, balance, is_admin, org_name, join_code, dept, email = employee
    today_str = today_ist().isoformat()
    
    cursor.execute("SELECT id, name FROM employees WHERE org_id = ?", (org_id,))
    all_employees = cursor.fetchall()
    
    report = f"📋 {org_name} - Today's Attendance\n\n"
    present_count = leave_count = absent_count = 0
    
    for emp_id, emp_name in all_employees:
        cursor.execute("SELECT status FROM attendance WHERE employee_id = ? AND date = ?", (emp_id, today_str))
        result = cursor.fetchone()
        status = result[0] if result else "absent"
        
        emoji = "✅" if status == "present" else "📤" if status == "leave" else "❌"
        report += f"{emoji} {emp_name}: {status}\n"
        
        if status == "present": present_count += 1
        elif status == "leave": leave_count += 1
        else: absent_count += 1
    
    report += f"\n✅ Present: {present_count} | 📤 Leave: {leave_count} | ❌ Absent: {absent_count}"
    await update.message.reply_text(report)

async def admin_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee or not employee[4]:
        await update.message.reply_text("👑 Admin access required.")
        return
    
    employee_id, org_id, name, balance, is_admin, org_name, join_code, dept, email = employee
    
    # FIX: Define current_month here
    current_month = today_ist().strftime("%Y-%m")
    
    cursor.execute("SELECT id, name FROM employees WHERE org_id = ?", (org_id,))
    all_employees = cursor.fetchall()
    
    report = f"📆 {org_name} - {today_ist().strftime('%B %Y')}\n\n"
    
    for emp_id, emp_name in all_employees:
        cursor.execute('''
            SELECT status, COUNT(*) FROM attendance 
            WHERE employee_id = ? AND strftime('%Y-%m', date) = ? 
            GROUP BY status
        ''', (emp_id, current_month))
        results = cursor.fetchall()
        
        present = sum(r[1] for r in results if r[0] == 'present')
        leaves = sum(r[1] for r in results if r[0] == 'leave')
        
        cursor.execute("SELECT leave_balance FROM employees WHERE id = ?", (emp_id,))
        balance_left = cursor.fetchone()[0]
        
        report += f"👤 {emp_name}: ✅ {present} | 📤 {leaves} | 🎫 {balance_left}/4\n"
    
    await update.message.reply_text(report)

async def reset_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee or not employee[4]:
        await update.message.reply_text("👑 Admin access required.")
        return
    
    employee_id, org_id, name, balance, is_admin, org_name, join_code, dept, email = employee
    
    cursor.execute("UPDATE employees SET leave_balance = 4 WHERE org_id = ?", (org_id,))
    conn.commit()
    
    await update.message.reply_text(f"✅ Leave balances reset for {org_name}!")
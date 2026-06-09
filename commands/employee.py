# commands/employee.py
from telegram import Update
from telegram.ext import ContextTypes
from utils import is_rate_limited
from database import (
    conn, cursor, get_employee, is_weekend, reset_balance_if_needed,
    mark_attendance, take_leave
)
from datetime import date

async def present(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee:
        await update.message.reply_text("❌ You're not part of any organization. Use /start")
        return
    
    employee_id, org_id, name, balance, is_admin, org_name, join_code, dept, email = employee
    today_obj = date.today()
    
    if is_weekend(today_obj):
        await update.message.reply_text("🏖️ It's the weekend! No need to mark attendance.")
        return
    
    reset_balance_if_needed(employee_id)
    success, message = mark_attendance(employee_id, 'present')
    
    if success:
        await update.message.reply_text(f"✅ Marked present!\n📅 {today_obj.strftime('%A, %B %d, %Y')}\n🏢 {org_name}")
    else:
        await update.message.reply_text(f"⚠️ {message}")

async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee:
        await update.message.reply_text("❌ You're not part of any organization. Use /start")
        return
    
    employee_id, org_id, name, balance, is_admin, org_name, join_code, dept, email = employee
    today_obj = date.today()
    
    if is_weekend(today_obj):
        await update.message.reply_text("🏖️ Weekends are already off!")
        return
    
    reset_balance_if_needed(employee_id)
    success, message = take_leave(employee_id)
    
    await update.message.reply_text(f"✅ {message}" if success else f"❌ {message}")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee:
        await update.message.reply_text("❌ You're not part of any organization. Use /start")
        return
    
    employee_id, org_id, name, balance, is_admin, org_name, join_code, dept, email = employee
    reset_balance_if_needed(employee_id)
    
    # Refresh balance after potential reset
    cursor.execute("SELECT leave_balance FROM employees WHERE id = ?", (employee_id,))
    current_balance = cursor.fetchone()[0]
    
    await update.message.reply_text(f"📊 {name}: {current_balance}/4 leaves remaining this month")

async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee:
        await update.message.reply_text("❌ You're not part of any organization.")
        return
    
    employee_id, org_id, name, balance, is_admin, org_name, join_code, dept, email = employee
    
    from database import get_employees_by_org
    employees_list = get_employees_by_org(org_id)
    
    if not employees_list:
        await update.message.reply_text("No members found.")
        return
    
    report = f"👥 {org_name} - Team Members\n\n"
    for emp_id, emp_name, emp_is_admin, emp_balance, emp_dept, emp_email in employees_list:
        role = "👑 Admin" if emp_is_admin else "👤 Member"
        dept_str = f" ({emp_dept})" if emp_dept else ""
        report += f"{role} {emp_name}{dept_str}\n"
    
    report += f"\n📊 Total: {len(employees_list)} members"
    await update.message.reply_text(report)
# commands/management.py
from telegram import Update
from telegram.ext import ContextTypes
from utils import is_rate_limited
from database import cursor, conn, get_employee

async def delete_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if not context.args:
        await update.message.reply_text("Usage: /delete_employee <name>\nExample: /delete_employee John")
        return
    
    employee_to_delete = " ".join(context.args).lower()
    
    cursor.execute('''
        SELECT id, name FROM employees 
        WHERE org_id = ? AND LOWER(name) LIKE ? AND is_admin = 0
    ''', (org_id, f'%{employee_to_delete}%'))
    
    target = cursor.fetchone()
    
    if not target:
        await update.message.reply_text(f"❌ Employee not found.")
        return
    
    target_id, target_name = target
    
    cursor.execute("DELETE FROM attendance WHERE employee_id = ?", (target_id,))
    cursor.execute("DELETE FROM employees WHERE id = ?", (target_id,))
    cursor.execute("DELETE FROM monthly_summary WHERE employee_id = ?", (target_id,))
    conn.commit()
    
    await update.message.reply_text(f"✅ Employee '{target_name}' removed.")

async def make_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if not context.args:
        await update.message.reply_text("Usage: /make_admin <employee_name>")
        return
    
    employee_name = " ".join(context.args).lower()
    
    cursor.execute('''
        SELECT id, name FROM employees 
        WHERE org_id = ? AND LOWER(name) LIKE ? AND is_admin = 0
    ''', (org_id, f'%{employee_name}%'))
    
    target = cursor.fetchone()
    
    if not target:
        await update.message.reply_text(f"❌ Employee not found.")
        return
    
    target_id, target_name = target
    
    cursor.execute("UPDATE employees SET is_admin = 1 WHERE id = ?", (target_id,))
    conn.commit()
    
    await update.message.reply_text(f"✅ {target_name} is now an admin!")

async def set_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin or employee can set their own department"""
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee:
        await update.message.reply_text("❌ You're not part of any organization.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /set_department <department_name>\nExample: /set_department Engineering")
        return
    
    department = " ".join(context.args)
    employee_id = employee[0]  # First value is id
    
    cursor.execute("UPDATE employees SET department = ? WHERE id = ?", (department, employee_id))
    conn.commit()
    
    await update.message.reply_text(f"✅ Department set to: {department}")

async def set_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin or employee can set their own email"""
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    employee = get_employee(user_id)
    
    if not employee:
        await update.message.reply_text("❌ You're not part of any organization.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /set_email <email>\nExample: /set_email john@company.com")
        return
    
    email = context.args[0]
    
    # Basic email validation
    if '@' not in email or '.' not in email:
        await update.message.reply_text("❌ Invalid email format.")
        return
    
    employee_id = employee[0]
    
    cursor.execute("UPDATE employees SET email = ? WHERE id = ?", (email, employee_id))
    conn.commit()
    
    await update.message.reply_text(f"✅ Email set to: {email}")

async def view_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View your own profile including department and email"""
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
    
    profile = f"📋 **Your Profile**\n\n"
    profile += f"👤 Name: {name}\n"
    profile += f"🏢 Organization: {org_name}\n"
    profile += f"👑 Role: {'Admin' if is_admin else 'Employee'}\n"
    profile += f"🎫 Leave Balance: {balance}/4\n"
    profile += f"🏷️ Department: {dept or 'Not set'}\n"
    profile += f"📧 Email: {email or 'Not set'}"
    
    await update.message.reply_text(profile)

async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    if not context.args:
        await update.message.reply_text("Usage: /remove_admin <admin_name>")
        return
    
    admin_name = " ".join(context.args).lower()
    
    cursor.execute('''
        SELECT id, name FROM employees 
        WHERE org_id = ? AND LOWER(name) LIKE ? AND is_admin = 1 AND telegram_id != ?
    ''', (org_id, f'%{admin_name}%', user_id))
    
    target = cursor.fetchone()
    
    if not target:
        await update.message.reply_text(f"❌ Admin not found.")
        return
    
    target_id, target_name = target
    
    cursor.execute("UPDATE employees SET is_admin = 0 WHERE id = ?", (target_id,))
    conn.commit()
    
    await update.message.reply_text(f"✅ {target_name} is no longer an admin.")
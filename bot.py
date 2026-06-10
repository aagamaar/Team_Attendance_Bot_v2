import os
from flask import Flask
import threading

# Create Flask app for health checks (keeps bot alive)
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "✅ Attendance Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# Start Flask in background thread
threading.Thread(target=run_flask, daemon=True).start()

# bot.py - Main entry point
from telegram.ext import Application, CommandHandler
from database import conn, cursor  # This initializes the database
from commands.employee import present, leave, balance, members
from commands.admin import admin_today, admin_month, reset_balance
from commands.management import delete_employee, make_admin, remove_admin
from commands.export import export_csv
from commands.management import set_department, set_email, view_profile
from utils import is_rate_limited

# Import the start and create_company functions (keep these in main bot.py for simplicity)
from telegram import Update
from telegram.ext import ContextTypes
from database import cursor, conn, get_employee, generate_join_code, today_ist

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    name = update.effective_user.first_name
    employee = get_employee(user_id)
    
    if employee:
        employee_id, org_id, emp_name, balance, is_admin, org_name, join_code, dept, email = employee
        if is_admin:
            await update.message.reply_text(
                f"✅ Welcome back {name}!\n🏢 {org_name} (Admin)\n\n"
                f"Employee: /present, /leave, /balance, /members\n"
                f"Admin: /admin_today, /admin_month, /reset_balance\n"
                f"Management: /delete_employee, /make_admin, /remove_admin\n"
                f"Profile: /set_department, /set_email, /profile\n"
                f"Export: /export_csv\n\n"
                f"🔑 Join Code: {join_code}"
            )
        else:
            await update.message.reply_text(
                f"✅ Welcome {emp_name}!\n🏢 {org_name}\n\n"
                f"/present - Mark present\n/leave - Take leave\n"
                f"/balance - Check leaves\n/members - See team\n"
                f"/profile - View your profile"
            )
    else:
        await update.message.reply_text(
            f"👋 Welcome {name}!\n\n"
            "Create company: /create_company <name>\n"
            "Join company: /join <code>"
        )

async def create_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    name = update.effective_user.first_name
    
    if get_employee(user_id):
        await update.message.reply_text("❌ You're already in an organization!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /create_company <Company Name>")
        return
    
    company_name = " ".join(context.args)
    join_code = generate_join_code()
    
    cursor.execute('INSERT INTO organizations (name, join_code, owner_telegram_id) VALUES (?, ?, ?)',
                   (company_name, join_code, user_id))
    org_id = cursor.lastrowid
    
    cursor.execute('INSERT INTO employees (org_id, telegram_id, name, leave_balance, is_admin, last_reset_month) VALUES (?, ?, ?, 4, 1, ?)',
                   (org_id, user_id, name, today_ist().strftime("%Y-%m")))
    conn.commit()
    
    await update.message.reply_text(f"✅ '{company_name}' created!\nJoin code: {join_code}\nShare with employees.")

async def join_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Rate limit check
    if is_rate_limited(user_id):
        await update.message.reply_text("⏰ Too many requests. Please wait a moment.")
        return
    
    name = update.effective_user.first_name
    
    if get_employee(user_id):
        await update.message.reply_text("❌ You're already in an organization!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /join <code>")
        return
    
    join_code = context.args[0].upper()
    cursor.execute("SELECT id, name FROM organizations WHERE join_code = ?", (join_code,))
    org = cursor.fetchone()
    
    if not org:
        await update.message.reply_text("❌ Invalid join code.")
        return
    
    org_id, org_name = org
    
    cursor.execute('INSERT INTO employees (org_id, telegram_id, name, leave_balance, is_admin, last_reset_month) VALUES (?, ?, ?, 4, 0, ?)',
                   (org_id, user_id, name, today_ist().strftime("%Y-%m")))
    conn.commit()
    
    await update.message.reply_text(f"✅ Joined '{org_name}'!\nUse /present to mark attendance.")

# Main function
def main():
    TOKEN =  os.environ.get("TELEGRAM_TOKEN","YOUR_BOT_TOKEN_HERE")  # Replace with your token
    
    app = Application.builder().token(TOKEN).build()
    
    # Core commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_company", create_company))
    app.add_handler(CommandHandler("join", join_company))
    
    # Employee commands
    app.add_handler(CommandHandler("present", present))
    app.add_handler(CommandHandler("leave", leave))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("members", members))
    
    # Admin commands
    app.add_handler(CommandHandler("admin_today", admin_today))
    app.add_handler(CommandHandler("admin_month", admin_month))
    app.add_handler(CommandHandler("reset_balance", reset_balance))
    
    # Management commands
    app.add_handler(CommandHandler("delete_employee", delete_employee))
    app.add_handler(CommandHandler("make_admin", make_admin))
    app.add_handler(CommandHandler("remove_admin", remove_admin))
    
    # Export
    app.add_handler(CommandHandler("export_csv", export_csv))
    
    # Email and department
    app.add_handler(CommandHandler("set_department", set_department))
    app.add_handler(CommandHandler("set_email", set_email))
    app.add_handler(CommandHandler("profile", view_profile))

    print("🤖 Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
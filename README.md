
---

# 📊 Team Attendance Bot

[![Python](https://img.shields.io/badge/Python-3.14%2B-blue.svg)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-0088cc.svg)](https://t.me/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **A multi-tenant attendance and leave management system for small teams — built as a Telegram Bot**

---

## 📋 Problem Statement

Small organizations (10-50 employees) track daily attendance through WhatsApp polls. Every morning, employees respond with "Present" or "Leave". At month-end, admins manually count responses and update spreadsheets.

### ❌ Problems:

| Employee Side | Admin Side |
|---------------|------------|
| Notification fatigue from daily polls | 200+ manual checks per month |
| No privacy (everyone sees who's on leave) | Error-prone manual counting |
| No visibility into leave balance | No real-time attendance view |
| Easy to forget responding | Separate spreadsheet for leave tracking |

---

## 🚀 Solution

A **Telegram Bot** that makes attendance tracking effortless:

- ⚡ **2 seconds** to mark attendance
- 📱 **No new apps** — uses existing Telegram
- 👁️ **Real-time visibility** for employees & admins
- 📊 **Automatic leave tracking** (4 leaves/month)
- 🏖️ **Weekends ignored** automatically
- 🏢 **Multi-tenant** — supports multiple organizations

---

## 🎯 Features

### For Employees

| Command | Description |
|---------|-------------|
| `/start` | Welcome message & available commands |
| `/present` | Mark yourself present (Mon-Fri only) |
| `/leave` | Request leave (deducts from 4/month quota) |
| `/balance` | Check remaining leave balance |
| `/members` | See all team members |
| `/profile` | View your profile (department, email) |

### For Administrators

| Command | Description |
|---------|-------------|
| `/admin_today` | View complete team attendance for today |
| `/admin_month` | View monthly summary with present/leave counts |
| `/reset_balance` | Reset all team members' leave balances |
| `/export_csv` | Export attendance data as CSV report |

### Management Commands

| Command | Description |
|---------|-------------|
| `/delete_employee` | Remove an employee from the organization |
| `/make_admin` | Promote an employee to admin (co-founder) |
| `/remove_admin` | Demote an admin to regular employee |
| `/set_department` | Set your department |
| `/set_email` | Set your email address |

### Organization Setup

| Command | Description |
|---------|-------------|
| `/create_company <name>` | Create a new organization (you become admin) |
| `/join <code>` | Join an existing organization using join code |

---

## 📊 CSV Export Example

The `/export_csv` command generates a comprehensive report including:

- **Employee Summary** — names, departments, leave balances, attendance stats
- **Monthly Attendance** — present days, leave days, attendance rate (%)
- **Recent Records** — last 30 days of attendance
- **Leave Balance Summary** — team-wide leave statistics

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.14+** | Core programming language |
| **python-telegram-bot** | Telegram Bot API wrapper |
| **SQLite** | Local database for storage |
| **Render** | 24/7 cloud hosting (optional) |

---

## 📂 Project Structure

```
Team_Attendance_Bot/
├── bot.py                 # Main entry point
├── database.py            # Database operations
├── database_setup.py      # Table creation script
├── utils.py               # Rate limiting utilities
├── requirements.txt       # Python dependencies
├── commands/
│   ├── __init__.py
│   ├── admin.py           # Admin commands
│   ├── employee.py        # Employee commands
│   ├── export.py          # CSV export
│   └── management.py      # Management commands
└── attendance.db          # SQLite database (auto-generated)
```

---

## 🚦 Getting Started

### Prerequisites

- Python 3.14+
- Telegram account
- Bot token from [@BotFather](https://t.me/BotFather)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Team_Attendance_Bot.git
cd Team_Attendance_Bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create a Telegram bot**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot`
   - Follow instructions to get your bot token

4. **Add your bot token**
```python
# In bot.py, replace:
TOKEN = "YOUR_BOT_TOKEN_HERE"
```

5. **Setup the database**
```bash
python database_setup.py
```

6. **Run the bot**
```bash
python bot.py
```

7. **Test on Telegram**
   - Search for your bot by username
   - Send `/start`
   - Create a company: `/create_company MyCompany`
   - Mark attendance: `/present`

---

## ☁️ Deployment (24/7 Hosting)

### Deploy on Render (Free)

1. Push your code to GitHub
2. Go to [render.com](https://render.com)
3. Create a new **Web Service**
4. Connect your GitHub repository
5. Add environment variable: `TELEGRAM_TOKEN` = your bot token
6. Click **Deploy**

Your bot will run 24/7 — even when your computer is off!

---

## 📈 Business Rules Enforced

```
📅 4 leaves per employee per month
🔄 Unused leaves do NOT carry over
🎉 Weekends automatically ignored (no marking needed)
📆 Leaves reset on the 1st of every month
👑 Multiple admins per organization supported
```

---

## 🔒 Security Features

| Feature | Description |
|---------|-------------|
| **Data isolation** | Each organization sees ONLY their data |
| **Rate limiting** | Prevents spam (20 commands per minute) |
| **Admin verification** | Sensitive commands require admin role |
| **Join codes** | 6-character random codes for secure joining |

---

## 📝 Commands Quick Reference

```
Command               Description
─────────────────────────────────────────────────────────
/start                Welcome message
/create_company       Create new organization (become admin)
/join                 Join existing organization

/present              Mark attendance (Mon-Fri only)
/leave                Request leave (4/month limit)
/balance              Check remaining leaves
/members              See team members
/profile              View your profile

/admin_today          Today's team attendance (Admin)
/admin_month          Monthly summary report (Admin)
/reset_balance        Reset all team leaves (Admin)
/export_csv           Export CSV report (Admin)

/delete_employee      Remove an employee (Admin)
/make_admin           Promote to admin (Admin)
/remove_admin         Demote from admin (Admin)
/set_department       Set your department
/set_email            Set your email
```

---

## 📊 Impact Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Time to mark attendance | 30 seconds | 2 seconds | **93% faster** |
| Admin monthly reporting | Hours | Instant | **99% reduction** |
| Manual counting errors | High | Zero | **100% elimination** |

---

## 🤝 Contributing

Issues and pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License — free for personal and commercial use.

---

## 👩‍💻 Author

**Aagama A R**

---

## 🙏 Acknowledgments

- [@BotFather](https://t.me/BotFather) for Telegram Bot API
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library
- [Render](https://render.com) for free hosting

---

<div align="center">

**⭐ Star this repo if you found it useful!**

*Built with ❤️ for small teams*

</div>

---

# database_setup.py
# Tables are now created automatically when the bot starts (see init_db in database.py).
# Running this file manually is optional and safe — it never deletes existing data.
import database  # importing runs init_db()

print("✅ Database ready! Tables created (existing data untouched).")
print("🎯 You can now run: python bot.py")

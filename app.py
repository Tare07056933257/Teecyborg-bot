# TeeCyborg AI Telegram Bot (Render Deploy Version)

from flask import Flask, request
import requests
import time
import threading
import datetime
import os

# === Configuration ===
BOT_TOKEN = "7931353636:AAFJizCRMnlxGtiU6HOXh9mXTu1PqMzNaxU"
CHAT_ID = "1689538681"
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

app = Flask(__name__)
journal_entries = []
reminder_interval = 300  # 5 minutes

# === Reminder Thread ===
def send_reminder():
    while True:
        time.sleep(reminder_interval)
        requests.post(BOT_URL, json={
            "chat_id": CHAT_ID,
            "text": "⏰ Reminder: Stay sharp, monitor your charts or update your journal."
        })

# === Telegram Webhook Receiver ===
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            send_text(chat_id, "🤖 TeeCyborg active! Use /remindme, /journal, or /log.")

        elif text.startswith("/remindme"):
            send_text(chat_id, "🔔 Reminder set every 5 minutes. Use /journal <note> to log a thought.")

        elif text.startswith("/journal"):
            entry = text.replace("/journal", "").strip()
            if entry:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                journal_entries.append(f"📝 {timestamp}: {entry}")
                send_text(chat_id, "✅ Journal entry saved.")
            else:
                send_text(chat_id, "✍️ Use it like this: /journal Sold V75 on HA reversal")

        elif text.startswith("/chart"):
            send_text(chat_id, "📊 Chart image feature coming soon!")

        elif text.startswith("/log"):
            if journal_entries:
                log_text = "\n".join(journal_entries[-10:])
                send_text(chat_id, f"🗂 Last 10 entries:\n{log_text}")
            else:
                send_text(chat_id, "📭 No journal entries yet.")

    return "ok"

# === Helper to Send Messages ===
def send_text(chat_id, message):
    requests.post(BOT_URL, json={"chat_id": chat_id, "text": message})

# === Launch Reminder Thread ===
threading.Thread(target=send_reminder, daemon=True).start()

# === Health Check ===
@app.route("/")
def index():
    return "TeeCyborg bot is running."

# === Run App (Render uses PORT env) ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

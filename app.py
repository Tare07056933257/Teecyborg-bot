from flask import Flask, request
import requests
import time
import threading
import datetime
import os

BOT_TOKEN = "7931353636:AAFJizCRMnlxGtiU6HOXh9mXTu1PqMzNaxU"
CHAT_ID = "1689538681"
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

app = Flask(__name__)
journal_entries = []
reminder_enabled = True
reminder_interval = 300  # 5 minutes

# === Reminder System ===
def reminder_loop():
    while True:
        if reminder_enabled:
            requests.post(BOT_URL, json={
                "chat_id": CHAT_ID,
                "text": "⏰ Reminder: Keep logging or check the charts!"
            })
        time.sleep(reminder_interval)

# === Start reminder thread ===
threading.Thread(target=reminder_loop, daemon=True).start()

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").lower()

        # Chat-like responses
        if "remind me" in text:
            send_text(chat_id, "🔔 I’ll remind you every 5 mins. Stay focused!")
        elif "stop reminder" in text:
            global reminder_enabled
            reminder_enabled = False
            send_text(chat_id, "✅ Reminder turned off.")
        elif "start reminder" in text:
            reminder_enabled = True
            send_text(chat_id, "🔔 Reminder re-enabled.")
        elif "log that" in text or "journal" in text:
            entry = text.replace("log that", "").replace("journal", "").strip()
            if entry:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                journal_entries.append(f"📝 {timestamp}: {entry}")
                send_text(chat_id, "🗂️ Got it. Entry saved.")
            else:
                send_text(chat_id, "✍️ What would you like me to log?")
        elif "show" in text and ("log" in text or "note" in text or "journal" in text):
            if journal_entries:
                entries = "\n".join(journal_entries[-10:])
                send_text(chat_id, f"📜 Last entries:\n{entries}")
            else:
                send_text(chat_id, "📭 No entries yet.")
        elif "chart" in text:
            send_text(chat_id, "📊 Chart feature coming soon, Cyborg Commander.")
        else:
            send_text(chat_id, f"🤖 I’m listening, Tare. Try saying 'log that I saw HA reversal' or 'remind me'.")

    return "ok"

@app.route("/")
def home():
    return "TeeCyborg is awake. Ready to serve."

def send_text(chat_id, message):
    requests.post(BOT_URL, json={"chat_id": chat_id, "text": message})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

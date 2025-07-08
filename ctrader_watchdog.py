import requests
import time
import datetime
import os

# === Load secure env variables from Render ===
CLIENT_ID = os.environ.get("CTRADER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("CTRADER_CLIENT_SECRET")
ACCOUNT_ID = os.environ.get("CTRADER_ACCOUNT_ID")
SYMBOL = "DEMO.DERIV.VOLATILITY75INDEX"

# === Telegram Config ===
TELEGRAM_TOKEN = "7931353636:AAFJizCRMnlxGtiU6HOXh9mXTu1PqMzNaxU"
TELEGRAM_CHAT_ID = "1689538681"

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        print("Telegram failed:", e)

# === Auth with cTrader ===
def get_access_token():
    url = "https://demo.ctraderapi.com/connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        if response.status_code != 200:
            send_telegram(f"❌ Auth failed: {response.status_code}\n{response.text}")
            return None
        return response.json().get("access_token")
    except Exception as e:
        send_telegram(f"💥 Auth error: {e}")
        return None

# === Check Open Positions ===
def check_open_positions(token):
    url = f"https://api.spotware.com/connect/trading/accounts/{ACCOUNT_ID}/positions"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            positions = r.json().get("positions", [])
            if positions:
                for pos in positions:
                    msg = f"📊 Open Trade:\nSymbol: {pos['symbolName']}\nSide: {pos['direction']}\nEntry: {pos['entryPrice']}"
                    send_telegram(msg)
            else:
                send_telegram("✅ No open trades found.")
        else:
            send_telegram(f"⚠️ Failed to get positions: {r.status_code}")
    except Exception as e:
        send_telegram(f"💥 Error checking positions: {e}")

# === Check New Candle ===
def check_latest_candle(token):
    url = f"https://api.spotware.com/connect/trading/accounts/{ACCOUNT_ID}/symbols/{SYMBOL}/candles?timeframe=5m&count=1"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            candle = r.json()["candles"][0]
            t = datetime.datetime.fromtimestamp(candle["timestamp"] / 1000)
            msg = f"🕐 New 5m Candle:\nTime: {t}\nOpen: {candle['open']}\nClose: {candle['close']}"
            send_telegram(msg)
        else:
            send_telegram(f"⚠️ Candle fetch failed: {r.status_code}")
    except Exception as e:
        send_telegram(f"💥 Candle check error: {e}")

# === Main loop ===
if __name__ == "__main__":
    send_telegram("🚀 TeeCyborg Watchdog started.")
    while True:
        token = get_access_token()
        if token:
            check_open_positions(token)
            check_latest_candle(token)
        else:
            send_telegram("❌ No access token. Skipping checks.")
        time.sleep(300)  # check every 5 minutes

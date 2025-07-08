import requests
import time
import datetime
import os

# === Load from environment ===
CLIENT_ID = os.environ.get("CTRADER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("CTRADER_CLIENT_SECRET")
ACCOUNT_ID = os.environ.get("CTRADER_ACCOUNT_ID")
SYMBOL = "DEMO.DERIV.VOLATILITY75INDEX"

# === Telegram Bot Config ===
TELEGRAM_TOKEN = "7931353636:AAFJizCRMnlxGtiU6HOXh9mXTu1PqMzNaxU"
TELEGRAM_CHAT_ID = "1689538681"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})

# === Step 1: Authenticate ===
def get_access_token():
    url = "https://api.spotware.com/connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    return response.json().get("access_token")

# === Step 2: Get open positions ===
def check_open_positions(token):
    url = f"https://api.spotware.com/connect/trading/accounts/{ACCOUNT_ID}/positions"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        positions = data.get("positions", [])
        for pos in positions:
            msg = f"📊 Open trade:\nSymbol: {pos['symbolName']}\nSide: {pos['direction']}\nVolume: {pos['volume']}\nEntry: {pos['entryPrice']}"
            send_telegram(msg)
    else:
        send_telegram("⚠️ Could not fetch positions.")

# === Step 3: Get latest candle ===
def check_latest_candle(token):
    url = f"https://api.spotware.com/connect/trading/accounts/{ACCOUNT_ID}/symbols/{SYMBOL}/candles?timeframe=5m&count=1"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        candle = r.json()["candles"][0]
        t = datetime.datetime.fromtimestamp(candle["timestamp"] / 1000)
        msg = f"🕐 New 5m Candle:\nTime: {t}\nOpen: {candle['open']}\nClose: {candle['close']}"
        send_telegram(msg)
    else:
        send_telegram("⚠️ Candle fetch failed.")

# === Main Loop ===
if __name__ == "__main__":
    while True:
        try:
            token = get_access_token()
            if token:
                check_open_positions(token)
                check_latest_candle(token)
            else:
                send_telegram("❌ Failed to get access token.")
        except Exception as e:
            send_telegram(f"💥 Error: {str(e)}")
        time.sleep(300)  # every 5 minutes

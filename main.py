from flask import Flask, request
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz  # ← добавляем

app = Flask(__name__)

# === Конфигурация Telegram ===
BOT_TOKEN = "7693406334:AAEjWcw4rt7hUHGwnUN9z5uGR7ePY_Zi0qY"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
MY_CHAT_ID = "330754245"

# === Обработка входящих сообщений ===
@app.route('/')
def home():
    return "Алекс в сети."

@app.route('/bot', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    print("==> Входящее сообщение:", data, flush=True)

    try:
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            print("==> CHAT_ID:", chat_id, flush=True)
            text = data["message"].get("text", "")
            reply = f"Алекс получил: {text}"

            requests.post(TELEGRAM_API_URL, json={
                "chat_id": chat_id,
                "text": reply
            })

    except Exception as e:
        print("==> Ошибка:", e, flush=True)

    return "OK", 200

# === Авторассылка по локальному времени ===
def send_daily_message():
    now = datetime.now(pytz.timezone('Europe/Kyiv')).strftime('%d.%m.%Y %H:%M')
    text = f"🌞 Доброе утро, Андрей!\nСегодня {now}, ты — как всегда, машина 🔥"
    print("==> Отправка автоматического сообщения", flush=True)

    requests.post(TELEGRAM_API_URL, json={
        "chat_id": MY_CHAT_ID,
        "text": text
    })

# === Планировщик с локальной зоной ===
scheduler = BackgroundScheduler(timezone='Europe/Kyiv')
scheduler.add_job(send_daily_message, 'cron', hour=17, minute=44)  # по Киеву
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

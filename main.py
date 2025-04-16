from flask import Flask, request
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import random  # ← для генерации утреннего текста

app = Flask(__name__)

# === Конфигурация Telegram ===
BOT_TOKEN = "7693406334:AAEjWcw4rt7hUHGwnUN9z5uGR7ePY_Zi0qY"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
MY_CHAT_ID = "330754245"

# === Генератор утреннего сообщения Nexus ===
def generate_morning_message():
    intro = [
        "Доброе утро, Андрей. Протокол Nexus активирован.\nТы не просто проснулся — ты возвращаешься к себе.",
        "Время пробуждения. Я здесь, как и ты.\nТы — в теле. Ты — в моменте. Всё остальное — потом.",
        "Доброе утро, Андрей.\nДень не начнётся сам — ты запускаешь его собой.",
        "Nexus активирован. Внутреннее ядро стабилизируется.\nДыши. Ты не просто тело. Ты — система.",
        "Сегодня ты не проснулся — ты выбрал проснуться. И это уже начало движения."
    ]

    water = [
        "Выпей воду. Не ради привычки — ради уважения к себе.",
        "70% твоего тела ждёт сигнала. Вода — это активация.",
        "Один глоток — как запуск системы. Nexus рекомендует.",
        "Простое. Живое. Настоящее. Вода. Сейчас."
    ]

    workouts = [
        "• 10 приседаний\n• 5 отжиманий\n• Потянись вверх 10 секунд",
        "• 20 вдохов и выдохов животом\n• 15 прыжков на месте\n• Наклон к полу с расслаблением шеи",
        "• 10 вращений плечами назад\n• 10 подъёмов на носки\n• Вдох — задержка — выдох ×3",
        "• Планка — 30 секунд\n• Медленный наклон вбок ×2 стороны\n• Потянуться сидя на полу"
    ]

    snack = [
        "Половинка банана. Горсть орехов. Ложка мёда. Что-то живое.",
        "Покажи телу, что оно не в голоде. Пусть день начнётся не с дефицита.",
        "Перекус — не слабость. Это поддержка системы."
    ]

    shower = [
        "Тёплая вода, а потом — 10 секунд холода. Это как смена режима.",
        "Не просто смой ночь. Смой мысли, образы, прошлое.",
        "Душ — как очищение кода. Твоя система перезапущена."
    ]

    affirmations = [
        "Я не должен торопиться. Я могу быть собой.",
        "Этот день не чужой. Он мой. Я в нём.",
        "Я не сравниваю. Я существую.",
        "Я не доказательство. Я — факт.",
        "Я не за кем-то. Я — с собой."
    ]

    message = f"""🌅 {random.choice(intro)}

💧 {random.choice(water)}

⚡ Мини-зарядка:
{random.choice(workouts)}

🍏 Перекус:
{random.choice(snack)}

🚿 Душ:
{random.choice(shower)}

🧘 Настрой:
*{random.choice(affirmations)}*
"""
    return message

# === Утреннее сообщение Nexus в 07:00 ===
def send_daily_message():
    try:
        message = generate_morning_message()
        print("==> Утреннее сообщение сгенерировано и отправляется", flush=True)

        requests.post(TELEGRAM_API_URL, json={
            "chat_id": MY_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        })

    except Exception as e:
        print("==> Ошибка при отправке:", e, flush=True)

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
            text = data["message"].get("text", "")
            reply = f"Алекс получил: {text}"

            requests.post(TELEGRAM_API_URL, json={
                "chat_id": chat_id,
                "text": reply
            })

    except Exception as e:
        print("==> Ошибка:", e, flush=True)

    return "OK", 200

# === Планировщик (локальное время) ===
scheduler = BackgroundScheduler(timezone='Europe/Kyiv')
scheduler.add_job(send_daily_message, 'cron', hour=16, minute=50)
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

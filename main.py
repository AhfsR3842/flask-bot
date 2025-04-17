from flask import Flask, request
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
import random
import json

app = Flask(__name__)

# === Конфигурация Telegram ===
BOT_TOKEN = "7693406334:AAEjWcw4rt7hUHGwnUN9z5uGR7ePY_Zi0qY"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
MY_CHAT_ID = "330754245"

# === Утреннее сообщение ===
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

# === Вечерняя логика ===
def load_goals():
    with open("evening_goals.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_stats():
    if os.path.exists("evening_stats.json"):
        with open("evening_stats.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_stats(stats):
    with open("evening_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def choose_random_goal(goals, completed_goals):
    available = {
        block: [
            g for g in items if g["repeatable"] or g["text"] not in completed_goals
        ]
        for block, items in goals.items()
    }
    available = {k: v for k, v in available.items() if v}
    if not available:
        return None, None
    block = random.choice(list(available.keys()))
    goal = random.choice(available[block])
    return block, goal

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

def send_evening_goal():
    try:
        goals = load_goals()
        stats = load_stats()
        today = datetime.now(pytz.timezone("Europe/Kyiv")).strftime("%Y-%m-%d")

        completed = [g["goal"] for g in stats.values() if g.get("done")]
        block, goal = choose_random_goal(goals, completed)

        if not goal:
            message = "Все цели выполнены. Сегодня просто отдыхай 😌"
        else:
            message = f"""🌙 Вечерняя цель: *{block}*

🎯 *{goal['text']}*

⏳ Время: 1–1.5 часа  
Когда закончишь — просто напиши:  
✅ Сделал или ❌ Нет
"""
            stats[today] = {
                "block": block,
                "goal": goal["text"],
                "done": False
            }
            save_stats(stats)

        requests.post(TELEGRAM_API_URL, json={
            "chat_id": MY_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        })

    except Exception as e:
        print("==> Ошибка при отправке вечерней цели:", e, flush=True)

@app.route('/bot', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    print("==> Входящее сообщение:", data, flush=True)

    try:
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            if text.strip().lower() == "/утро":
                send_daily_message()
                return "OK", 200

            if text.strip().lower() == "/вечер":
                send_evening_goal()
                return "OK", 200

            # Остальная логика (✅ / ❌ и т.д.)
            reply = f"Алекс получил: {text}"
            requests.post(TELEGRAM_API_URL, json={
                "chat_id": chat_id,
                "text": reply
            })

    except Exception as e:
        print("==> Ошибка:", e, flush=True)

    return "OK", 200
      
            stats = load_stats()
            today = datetime.now(pytz.timezone("Europe/Kyiv")).strftime("%Y-%m-%d")

            if today in stats and text.strip() in ["✅", "❌"]:
                stats[today]["done"] = text.strip() == "✅"
                save_stats(stats)
                reply = "Отлично, цель выполнена! 🔥" if text.strip() == "✅" else "Хорошо, предложу снова позже ✌️"
            else:
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
scheduler.add_job(send_daily_message, 'cron', hour=7, minute=0)
scheduler.add_job(send_evening_goal, 'cron', hour=21, minute=0)
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

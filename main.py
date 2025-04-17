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
BOT_TOKEN = "7693406334:AAGnATxMuZqQpHfD0spwCpt4DXaX0ciNS-o"
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
        "• Планка — 30 секунд\n• Медленный наклон вбок ×2 стороны\n• Потянуться сидя на полу",
        "• Растяжка рук и шеи\n• Круговые движения тазом\n• Глубокие вдохи на 3 счета"
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
def load_cement_stats():
    if os.path.exists("cement_stats.json"):
        with open("cement_stats.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"dates": [], "total": 0, "streak": 0}

def save_cement_stats(stats):
    with open("cement_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def check_cement_achievement(total):
    achievements = {
        5: "*Режим \"Нежность\" активирован. Nexus фиксирует стабильность.*",
        10: "*Ты цемаешь системно. Уже почти привычка.*",
        50: "*Формируется паттерн любви. Это красиво.*",
        100: "*Сто вечерних поцелуев. Это не просто цифра.*",
        500: "*Половина тысячи. Она знает. Nexus тоже.*",
        1000: "*Ты переписал протоколы близости. Это уровень Бога.*"
    }
    return achievements.get(total, None)

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
        block: [g for g in items if g["repeatable"] or g["text"] not in completed_goals]
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

        intro = random.choice([
            "Солнце село. Остался ты и момент — что ты сделаешь с ним?",
            "Ты прожил день. Теперь твой вечер. Сделай его значимым.",
            "Пока все отвлекаются — ты можешь выбрать глубину.",
            "Система ждёт сигнала. Вечер активен."
        ])

        message = f"""🌙 {intro}

Цель на вечер: *{block}*
🎯 *{goal['text']}*

⏳ Время: 1–1.5 часа  
Когда закончишь — просто напиши:  
✅ Сделал или ❌ Нет

⚠ Обязательное задание:  
Цемнуть свою девушку. Без этого вечер не считается закрытым.
"""

        keyboard = [[
            {"text": "Цемнул 💋", "callback_data": "cem_yes"},
            {"text": "Забыл 😐", "callback_data": "cem_no"},
            {"text": "📊 Статистика", "callback_data": "cem_stats"}
        ]]

        stats[today] = {
            "block": block,
            "goal": goal["text"],
            "done": False
        }
        save_stats(stats)

        requests.post(TELEGRAM_API_URL.replace("sendMessage", "sendMessage"), json={
            "chat_id": MY_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": keyboard}
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

            if text.strip().lower() == "/start":
                reply = "Привет, Андрей. Я живой, командуй – /утро, /вечер или просто поговори."
                requests.post(TELEGRAM_API_URL, json={"chat_id": chat_id, "text": reply})
                return "OK", 200

            if text.strip().lower() == "/утро":
                send_daily_message()
                return "OK", 200

            if text.strip().lower() == "/вечер":
                send_evening_goal()
                return "OK", 200

    
            if text.strip().lower() == "/цем":
                cement_stats = load_cement_stats()
                reply = (
                    f"📊 Статистика цемов:\n"
                    f"Всего: {cement_stats['total']}\n"
                    f"Подряд: {cement_stats['streak']}\n"
                    f"Последний: {cement_stats['dates'][-1] if cement_stats['dates'] else '—'}"
                )
                achievement = check_cement_achievement(cement_stats["total"])
                if achievement:
                    reply += f"\n\n🎖 Достижение: {achievement.strip('*')}"
                requests.post(TELEGRAM_API_URL, json={"chat_id": chat_id, "text": reply})
                return "OK", 200

        elif "callback_query" in data:
            query = data["callback_query"]
            chat_id = query["message"]["chat"]["id"]
            data_str = query["data"]
            cement_stats = load_cement_stats()
            today = datetime.now(pytz.timezone("Europe/Kyiv")).strftime("%Y-%m-%d")

            if data_str == "cem_yes" and today not in cement_stats["dates"]:
                cement_stats["dates"].append(today)
                cement_stats["total"] += 1
                cement_stats["streak"] += 1
                save_cement_stats(cement_stats)
                achievement = check_cement_achievement(cement_stats["total"])
                reply = "Цем зафиксирован 💋"
                if achievement:
                    reply += f"\n\n🎖 Достижение: {achievement.strip('*')}"

            elif data_str == "cem_no" and today not in cement_stats["dates"]:
                cement_stats["streak"] = 0
                save_cement_stats(cement_stats)
                reply = "Не зафиксировано. Вечер без цема — неполный."

            elif data_str == "cem_stats":
                reply = (
                    f"📊 Статистика цемов:\n"
                    f"Всего: {cement_stats['total']}\n"
                    f"Подряд: {cement_stats['streak']}\n"
                    f"Последний: {cement_stats['dates'][-1] if cement_stats['dates'] else '—'}"
                )
                achievement = check_cement_achievement(cement_stats["total"])
                if achievement:
                    reply += f"\n\n🎖 Достижение: {achievement.strip('*')}"

            else:
                reply = "Уже зафиксировано сегодня."

            requests.post(TELEGRAM_API_URL, json={"chat_id": chat_id, "text": reply})

    except Exception as e:
        print("==> Ошибка:", e, flush=True)

    return "OK", 200

# === Планировщик ===
scheduler = BackgroundScheduler(timezone='Europe/Kyiv')
scheduler.add_job(send_daily_message, 'cron', hour=7, minute=0)
scheduler.add_job(send_evening_goal, 'cron', hour=21, minute=0)
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

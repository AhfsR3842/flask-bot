from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "7693406334:AAEjWcw4rt7hUHGwnUN9z5uGR7ePY_Zi0qY"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route('/')
def home():
    return "Бот подключен к Telegram!"

@app.route('/bot', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    print("==> Получено сообщение:", data)

    try:
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            reply = f"Ты написал: {text}"

            print(f"==> Отправка в чат {chat_id}: {reply}")

            resp = requests.post(TELEGRAM_API_URL, json={
                "chat_id": chat_id,
                "text": reply
            })

            print("==> Ответ Telegram API:", resp.text)

    except Exception as e:
        print("==> Ошибка обработки:", e)

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

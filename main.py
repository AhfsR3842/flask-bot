from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "7693406334:AAEjWcw4rt7hUHGwnUN9z5uGR7ePY_Zi0qY"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.route('/')
def home():
    return "Ассистент Алекс на связи."

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

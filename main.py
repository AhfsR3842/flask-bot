from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот жив!"

@app.route('/bot', methods=['POST'])
def bot():
    data = request.get_json()
    print("Получено сообщение:", data)
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request

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
    app.run()

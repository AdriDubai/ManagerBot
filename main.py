from flask import Flask, request
import telebot
import os

# Получение токена из переменных окружения
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Устанавливаем webhook при запуске
@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    return "Webhook установлен!", 200

# Получение сообщений от Telegram
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200

# Обработчик команды /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот на базе GPT.")

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Ты написал: {message.text}")

# Запуск Flask-приложения
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


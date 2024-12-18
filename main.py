from flask import Flask, request
import telebot
import os
import openai
import time

# Получение токенов из переменных окружения
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
openai.api_key = OPENAI_API_KEY

# Устанавливаем webhook один раз при запуске
def setup_webhook():
    webhook_info = bot.get_webhook_info()
    if not webhook_info.url or webhook_info.url != f"{RENDER_URL}/{TOKEN}":
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print("Webhook установлен!")

setup_webhook()  # Явно вызываем функцию при старте

# Получение сообщений от Telegram
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def gpt_reply(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = response['choices'][0]['message']['content']
        time.sleep(2)  # Задержка между ответами
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке запроса.")

# Запуск Flask-приложения
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


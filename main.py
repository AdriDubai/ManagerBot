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

# Устанавливаем webhook при старте
@app.route("/", methods=["GET"])
def home():
    return "Webhook сервер запущен!", 200

@app.route("/" + TOKEN, methods=["POST"])
def get_message():
    try:
        json_data = request.stream.read().decode("utf-8")
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        print(f"Ошибка в обработке запроса: {e}")
        return "Internal Server Error", 500

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def gpt_reply(message):
print(f"Получено сообщение от пользователя: {message.chat.username}: {message.text}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = response['choices'][0]['message']['content']
        print(f"Ответ от OpenAI: {reply}")
        time.sleep(2)  # Задержка между ответами
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке запроса.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


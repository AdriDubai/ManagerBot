from flask import Flask, request
import telebot
import os
import openai

# Получение токенов из переменных окружения
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
openai.api_key = OPENAI_API_KEY

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

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def gpt_reply(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = response['choices'][0]['message']['content']
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обработке запроса.")
        print(f"Error: {e}")

# Запуск Flask-приложения
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


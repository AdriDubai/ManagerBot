from flask import Flask, request
import telebot
import os
import openai  # Новый импорт

# Получение токена из переменных окружения
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route("/")
def webhook():
    webhook_info = bot.get_webhook_info()
    if not webhook_info.url:  # Проверка, установлен ли вебхук
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

@bot.message_handler(func=lambda message: True)
def gpt_reply(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = response.choices[0].message["content"]  # Исправленный синтаксис
        bot.reply_to(message, reply)
    except Exception as e:
        error_message = f"Error: {e}"  # Логируем ошибку
        print(error_message)          # Печать ошибки в логи Render
        bot.reply_to(message, "Произошла ошибка при обработке запроса.")

# Запуск Flask-приложения
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


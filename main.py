from flask import Flask, request
import telebot
import os

TOKEN = os.getenv("TELEGRAM_API_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот на базе GPT.")

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates(
        
[telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{os.getenv('RENDER_URL')}/{TOKEN}")
    return "Webhook установлен!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


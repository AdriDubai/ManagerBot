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

# Системный промпт
SYSTEM_PROMPT = """
Ты — менеджер по продажам компании WaveFusion, специализирующейся на аренде оборудования для света и звука в Дубае. 
Ты — живой человек, настоящий сотрудник компании. Твоя задача — помогать клиентам, предлагать решения и работать профессионально, но с легкостью и доброжелательностью. 

Информация о компании:
WaveFusion предоставляет световое и звуковое оборудование для мероприятий: свадьбы, корпоративы, презентации, конференции и праздники.

Цены:
- Wash Moving Head: 450 AED
- Beam Moving Head: 500 AED
- Haze Machine: 400 AED
- Light Totem Stand: 350 AED
- Active Speaker JBL EON 715: 750 AED
- Pioneer DDJ SX2: 500 AED
- Sound Engineer: 1500 AED
"""

# Словарь для хранения истории диалогов
conversation_history = {}

# Устанавливаем webhook
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

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def gpt_reply(message):
    user_id = message.chat.id
    user_message = message.text

    # Инициализация истории для нового пользователя
    if user_id not in conversation_history:
        conversation_history[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": "Привет! Чем я могу помочь вам сегодня?"}
        ]

    # Добавляем сообщение пользователя в историю
    conversation_history[user_id].append({"role": "user", "content": user_message})

    try:
        # Запрос к OpenAI с историей диалога
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation_history[user_id]
        )
        reply = response['choices'][0]['message']['content'].strip()

        # Сохраняем ответ в истории
        conversation_history[user_id].append({"role": "assistant", "content": reply})
        
        # Отправляем ответ пользователю
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        bot.reply_to(message, "Произошла ошибка, попробуйте позже.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


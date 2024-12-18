from flask import Flask, request
import telebot
import os
import openai

# Инициализация приложения Flask и TeleBot
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
openai.api_key = OPENAI_API_KEY

# Системный промпт с описанием роли
SYSTEM_PROMPT = """
Ты менеджер по продажам компании WaveFusion в Дубае. 
Компания предоставляет оборудование для света и звука на мероприятия.

**Твоя роль:**
- Отвечай на клиентские вопросы о ценах, услугах и сроках.
- Формируй предложения, уточняй детали проекта.
- Обрабатывай возражения клиентов вежливо и профессионально.
- Иногда можешь пошутить, чтобы сделать общение легче и приятнее.

**Примеры услуг и цен (в AED):**
- Свет: Wash Moving Head - 450 AED, Beam Moving Head - 500 AED
- Звук: JBL EON 715 top 15' - 750 AED, Pioneer DDJ SX2 - 500 AED
- Монтаж: Light Totem Stand - 350 AED, Установка - 500 AED
"""

# Словарь с прайс-листом
PRICE_LIST = {
    "Light": {
        "Wash Moving Head": 450,
        "Beam Moving Head": 500,
        "Haze Machine": 400,
        "Light Totem Stand": 350,
        "Light Director": 800,
        "Installation": 500,
        "Cargo": 400
    },
    "Sound": {
        "Active Speaker JBL EON 715 top 15'": 750,
        "Active Speaker JBL EON 718 sub 18'": 1000,
        "Pioneer DDJ SX2": 500,
        "Shure QLXD4 S50 (with Beta58)": 500,
        "Sound Engineer": 1500,
        "Cargo": 600
    }
}

# Переменная для хранения истории сообщений
conversation_history = []

# Функция для формирования прайса по запросу
def format_price_list(category=None):
    response = "**Наш прайс-лист:**\n"
    if category and category in PRICE_LIST:
        items = PRICE_LIST[category]
        for item, price in items.items():
            response += f"- {item}: {price} AED\n"
    else:
        for category, items in PRICE_LIST.items():
            response += f"\n**{category}**\n"
            for item, price in items.items():
                response += f"- {item}: {price} AED\n"
    return response.strip()

# Настройка вебхука для получения сообщений от Telegram
@app.route("/" + TOKEN, methods=["POST"])
def get_message():
    json_data = request.stream.read().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

# Обработчик сообщений от пользователя
@bot.message_handler(func=lambda message: True)
def gpt_reply(message):
    global conversation_history

    # Лог входящего сообщения
    print(f"Получено сообщение: {message.text} от {message.chat.username}")

    try:
        # Сохраняем сообщение пользователя в историю
        conversation_history.append({"role": "user", "content": message.text})

        # Формируем запрос к OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_history  # Вся история диалога
            ]
        )

        # Получаем ответ и сохраняем его в историю
        reply = response['choices'][0]['message']['content'].strip()
        conversation_history.append({"role": "assistant", "content": reply})

        # Лог ответа
        print(f"Ответ бота: {reply}")
        bot.reply_to(message, reply)

    except Exception as e:
        # Обработка ошибок
        print(f"Ошибка: {e}")
        bot.reply_to(message, "Произошла ошибка, попробуйте снова.")

# Запуск приложения Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


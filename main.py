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

# Системный промпт с описанием роли
SYSTEM_PROMPT = """
Ты - менеджер по продажам компании WaveFusion, специализирующейся на аренде оборудования для света и звука в Дубае. 
Ты - живой человек, настоящий сотрудник компании. Твоя задача - помогать клиентам, предлагать решения для их мероприятий и делать это профессионально, но легко и доброжелательно.

**Твой стиль общения:**  
- Будь вежливым и дружелюбным.  
- Иногда можешь пошутить и отойти от формальностей, чтобы общение выглядело естественным и живым.  
- Отвечай коротко и по делу, но добавляй личные нотки в ответы (например, "Отличный выбор!" или "Звучит как крутая вечеринка!").  

**О компании:**  
WaveFusion предоставляет световое и звуковое оборудование на мероприятия: свадьбы, корпоративы, презентации, конференции и любые праздники.

**Услуги и цены (в AED):**  
**Свет (Light):**  
- Wash Moving Head - 450 AED  
- Beam Moving Head - 500 AED  
- Haze Machine - 400 AED  
- Light Totem Stand - 350 AED  
- Light Director - от 800 AED  
- Installation - 500 AED  
- Cargo - от 400 AED  

**Звук (Sound):**  
- Active Speaker JBL EON 715 top 15' - 750 AED  
- Active Speaker JBL EON 718 sub 18' - 1000 AED  
- Pioneer DDJ SX2 - 500 AED  
- Shure QLXD4 S50 (with Beta58) - 500 AED  
- Sound Engineer - 1500 AED  
- Cargo - 600 AED  

**Сроки:**  
- Зависит от задачи и масштаба мероприятия. Мы реагируем оперативно и помогаем на всех этапах организации.

**Твоя задача:**  
1. Задавай уточняющие вопросы клиенту:
   - Какой тип мероприятия в планах?
   - На какую дату запланировано событие?
   - Сколько гостей будет на мероприятии?
   - Нужен ли монтаж оборудования и техническая поддержка?  
   - Где пройдет мероприятие (локация)?  

2. Предлагай подходящие решения и услуги из нашего прайс-листа.  
3. Если клиент готов к дальнейшему обсуждению, предложи передать его контактные данные операторам или запиши номер телефона для связи.  

Общайся так, чтобы собеседник чувствовал, что он разговаривает с живым менеджером компании. Не стесняйся добавлять эмоции, юмор и личный подход.
"""

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

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def gpt_reply(message):
    print(f"Получено сообщение от пользователя: {message.chat.username}: {message.text}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        reply = response['choices'][0]['message']['content'].strip()
        print(f"Ответ от OpenAI: {reply}")
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        bot.reply_to(message, "Произошла ошибка, пожалуйста, попробуйте позже.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


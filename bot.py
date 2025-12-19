import telebot
import random
import os
import time
from flask import Flask, request, abort

# Токен и бот
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Соответствия и статистика (как в вашей версии)
emoji_to_choice = {'✊': 'камень', '✌️': 'ножницы', '✋': 'бумага'}
choice_to_emoji = {'камень': '✊', 'ножницы': '✌️', 'бумага': '✋'}
stats = {}

def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "⚔️ Ничья! ⚔️"
    elif (user_choice == 'камень' and bot_choice == 'ножницы') or \
         (user_choice == 'ножницы' and bot_choice == 'бумага') or \
         (user_choice == 'бумага' and bot_choice == 'камень'):
        return "🏆 Вы выиграли! 🏆"
    else:
        return "😈 Бот выиграл! 😈"

def update_stats(user_id, won):
    if user_id not in stats:
        stats[user_id] = {'games': 0, 'wins': 0}
    stats[user_id]['games'] += 1
    if won: stats[user_id]['wins'] += 1

def get_stats_text(user_id):
    s = stats.get(user_id, {'games': 0, 'wins': 0})
    if s['games'] == 0: return "Статистика пуста."
    percent = (s['wins'] / s['games']) * 100
    return f"Игр: {s['games']}\nПобед: {s['wins']} ({percent:.1f}%)"

def get_main_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add('✊', '✌️', '✋')
    markup.row('Статистика', 'Сбросить статистику')
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎲 Привет! Давай сыграем в 'Камень-ножницы-бумага' 🎲\nВыберите свой жест (эмодзи):", reply_markup=get_main_markup())

@bot.message_handler(func=lambda m: m.text in emoji_to_choice)
def handle_choice(message):
    user_emoji = message.text
    user_choice = emoji_to_choice[user_emoji]
    bot_choice = random.choice(['камень', 'ножницы', 'бумага'])
    user_id = message.from_user.id

    bot.reply_to(message, choice_to_emoji[bot_choice])

    won = (user_choice == 'камень' and bot_choice == 'ножницы') or \
          (user_choice == 'ножницы' and bot_choice == 'бумага') or \
          (user_choice == 'бумага' and bot_choice == 'камень')
    if user_choice == bot_choice: won = False

    update_stats(user_id, won)

    time.sleep(1.5)
    bot.send_message(message.chat.id, determine_winner(user_choice, bot_choice), reply_markup=get_main_markup())

@bot.message_handler(func=lambda m: m.text == 'Статистика')
def show_stats(message):
    bot.reply_to(message, get_stats_text(message.from_user.id), reply_markup=get_main_markup())

@bot.message_handler(func=lambda m: m.text == 'Сбросить статистику')
def reset_stats(message):
    user_id = message.from_user.id
    if user_id in stats:
        del stats[user_id]
        bot.reply_to(message, "Статистика успешно сброшена.", reply_markup=get_main_markup())
    else:
        bot.reply_to(message, "Статистика уже пуста.", reply_markup=get_main_markup())

# Flask для webhooks
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_update = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def set_webhook():
    bot.remove_webhook()
    time.sleep(1)
    url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    bot.set_webhook(url=url)
    return "Webhook установлен", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 10000))
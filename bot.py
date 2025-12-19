import telebot
import random
import os
import time
import threading

# Токен из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Варианты для пользователя (стандартные эмодзи)
user_choices = ['✊', '✌️', '✋']

# Варианты для бота (с тёмным тоном кожи)
bot_choices = ['✊🏿', '✌🏿', '✋🏿']  # 0 — камень, 1 — ножницы, 2 — бумага

# Глобальная статистика по пользователям
stats = {}

# Определение победителя по индексам
def determine_winner(user_idx, bot_idx):
    if user_idx == bot_idx:
        return "⚔️ Ничья! ⚔️", False
    elif (user_idx + 1) % 3 == bot_idx:  # бот побеждает
        return "😈 Бот выиграл! 😈", False
    else:  # пользователь побеждает
        return "🏆 Вы выиграли! 🏆", True

# Обновление статистики
def update_stats(user_id, won):
    if user_id not in stats:
        stats[user_id] = {'games': 0, 'wins': 0}
    stats[user_id]['games'] += 1
    if won:
        stats[user_id]['wins'] += 1

# Текст статистики
def get_stats_text(user_id):
    s = stats.get(user_id, {'games': 0, 'wins': 0})
    if s['games'] == 0:
        return "Статистика пуста."
    percent = (s['wins'] / s['games']) * 100
    return f"Игр: {s['games']}\nПобед: {s['wins']} ({percent:.1f}%)"

# Основная клавиатура (стандартные эмодзи для пользователя)
def get_main_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add('✊', '✌️', '✋')
    markup.row('Статистика', 'Сбросить статистику')
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "🎲 Привет! Сыграем в 'Камень-ножницы-бумага' 🎲\n"
                 "Выберите свой жест:",
                 reply_markup=get_main_markup())

# Обработка выбора пользователя
@bot.message_handler(func=lambda m: m.text in user_choices)
def handle_choice(message):
    user_emoji = message.text
    user_idx = user_choices.index(user_emoji)
    bot_idx = random.randint(0, 2)
    bot_emoji = bot_choices[bot_idx]
    user_id = message.from_user.id

    # Задержка 1 секунда перед отправкой выбора бота
    def send_bot_choice_and_result():
        time.sleep(1)  # Задержка перед эмодзи бота
        bot.reply_to(message, bot_emoji)

        # Определяем результат
        result_text, won = determine_winner(user_idx, bot_idx)
        update_stats(user_id, won)

        time.sleep(1.5)  # Задержка перед результатом
        bot.send_message(message.chat.id, result_text, reply_markup=get_main_markup())

    threading.Thread(target=send_bot_choice_and_result).start()

# Статистика
@bot.message_handler(func=lambda m: m.text == 'Статистика')
def show_stats(message):
    bot.reply_to(message, get_stats_text(message.from_user.id), reply_markup=get_main_markup())

# Сброс статистики
@bot.message_handler(func=lambda m: m.text == 'Сбросить статистику')
def reset_stats(message):
    user_id = message.from_user.id
    if user_id in stats:
        del stats[user_id]
        bot.reply_to(message, "Статистика успешно сброшена.", reply_markup=get_main_markup())
    else:
        bot.reply_to(message, "Статистика уже пуста.", reply_markup=get_main_markup())

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
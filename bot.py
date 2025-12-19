import telebot
import random
import os
import time
import threading

# Токен из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Единый список вариантов (эмодзи)
choices = ['✊', '✌️', '✋']  # индекс: 0 — камень, 1 — ножницы, 2 — бумага

# Глобальная статистика по пользователям
stats = {}

# Определение победителя по индексам (возвращает текст результата и флаг победы пользователя)
def determine_winner(user_idx, bot_idx):
    if user_idx == bot_idx:
        return "⚔️ Ничья! ⚔️", False
    elif (user_idx + 1) % 3 == bot_idx:  # бот побеждает (следующий выигрывает)
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

# Основная клавиатура
def get_main_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add('✊', '✌️', '✋')
    markup.row('Статистика', 'Сбросить статистику')
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "🎲 Привет! Давай сыграем в 'Камень-ножницы-бумага' 🎲\n"
                 "Выберите свой жест:",
                 reply_markup=get_main_markup())

# Обработка выбора пользователя (эмодзи)
@bot.message_handler(func=lambda m: m.text in choices)
def handle_choice(message):
    user_emoji = message.text
    user_idx = choices.index(user_emoji)
    bot_emoji = random.choice(choices)
    bot_idx = choices.index(bot_emoji)
    user_id = message.from_user.id

    # Немедленно отправляем выбор бота (только эмодзи)
    bot.reply_to(message, bot_emoji)

    # Определяем результат
    result_text, won = determine_winner(user_idx, bot_idx)
    update_stats(user_id, won)

    # Через 1.5 секунды отправляем только результат
    def send_result():
        time.sleep(1.5)
        bot.send_message(message.chat.id, result_text, reply_markup=get_main_markup())

    threading.Thread(target=send_result).start()

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
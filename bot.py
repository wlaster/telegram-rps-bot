import telebot
import random
import os
import time
import threading

# Токен из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Эмодзи для отображения
choice_to_emoji = {
    'камень': '✊',
    'ножницы': '✌️',
    'бумага': '✋'
}

# Глобальная статистика (по пользователям)
stats = {}  # Ключ: user_id, значение: {'games': int, 'wins': int}

# Функция определения победителя (только текст результата)
def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "⚔️ Ничья! ⚔️"
    elif (user_choice == 'камень' and bot_choice == 'ножницы') or \
         (user_choice == 'ножницы' and bot_choice == 'бумага') or \
         (user_choice == 'бумага' and bot_choice == 'камень'):
        return "🏆 Вы выиграли! 🏆"
    else:
        return "😈 Бот выиграл! 😈"

# Обновление статистики
def update_stats(user_id, won):
    if user_id not in stats:
        stats[user_id] = {'games': 0, 'wins': 0}
    stats[user_id]['games'] += 1
    if won:
        stats[user_id]['wins'] += 1

# Получение строки статистики
def get_stats_text(user_id):
    s = stats.get(user_id, {'games': 0, 'wins': 0})
    if s['games'] == 0:
        return "Статистика пуста."
    percent = (s['wins'] / s['games']) * 100
    return f"Игр: {s['games']}\nПобед: {s['wins']} ({percent:.1f}%)"

# Основная клавиатура
def get_main_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add('Камень', 'Ножницы', 'Бумага')
    markup.row('Статистика', 'Сбросить статистику')
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "🎲 Привет! Давай сыграем в 'Камень-ножницы-бумага' 🎲\n"
                 "Выберите свой вариант:",
                 reply_markup=get_main_markup())

# Обработка игрового выбора
@bot.message_handler(func=lambda m: m.text in ['Камень', 'Ножницы', 'Бумага'])
def handle_choice(message):
    user_text = message.text
    user_choice = user_text.lower()  # 'камень', 'ножницы', 'бумага'
    bot_choice = random.choice(['камень', 'ножницы', 'бумага'])
    user_id = message.from_user.id

    # Немедленно отправляем только эмодзи бота
    bot.reply_to(message, choice_to_emoji[bot_choice])

    # Определяем результат и обновляем статистику
    if user_choice == bot_choice:
        result_text = determine_winner(user_choice, bot_choice)
        won = False
    elif (user_choice == 'камень' and bot_choice == 'ножницы') or \
         (user_choice == 'ножницы' and bot_choice == 'бумага') or \
         (user_choice == 'бумага' and bot_choice == 'камень'):
        result_text = determine_winner(user_choice, bot_choice)
        won = True
    else:
        result_text = determine_winner(user_choice, bot_choice)
        won = False

    update_stats(user_id, won)

    # Через 1.5 секунды отправляем только результат
    def send_result():
        time.sleep(1.5)
        bot.send_message(message.chat.id, result_text, reply_markup=get_main_markup())

    threading.Thread(target=send_result).start()

# Кнопка Статистика
@bot.message_handler(func=lambda m: m.text == 'Статистика')
def show_stats(message):
    user_id = message.from_user.id
    bot.reply_to(message, get_stats_text(user_id), reply_markup=get_main_markup())

# Кнопка Сбросить статистику
@bot.message_handler(func=lambda m: m.text == 'Сбросить статистику')
def reset_stats(message):
    user_id = message.from_user.id
    if user_id in stats:
        del stats[user_id]
        bot.reply_to(message, "Статистика успешно сброшена.", reply_markup=get_main_markup())
    else:
        bot.reply_to(message, "Статистика уже пуста.", reply_markup=get_main_markup())

# Запуск бота (polling)
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
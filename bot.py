import telebot
import random
import os

# Получаем токен из переменных окружения (безопасно)
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Создаём объект бота
bot = telebot.TeleBot(TOKEN)

# Возможные варианты выбора
choices = ['камень', 'ножницы', 'бумага']

# Функция определения победителя
def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "Ничья!"
    elif (user_choice == 'камень' and bot_choice == 'ножницы') or \
         (user_choice == 'ножницы' and bot_choice == 'бумага') or \
         (user_choice == 'бумага' and bot_choice == 'камень'):
        return "Вы выиграли!"
    else:
        return "Бот выиграл!"

# Команда /start — приветствие и клавиатура
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Камень', 'Ножницы', 'Бумага')
    
    bot.reply_to(message, 
                 "Привет! Давай сыграем в 'Камень-ножницы-бумага'.\n"
                 "Выбери свой вариант:", 
                 reply_markup=markup)

# Обработка выбора пользователя
@bot.message_handler(func=lambda message: message.text.lower() in choices)
def handle_choice(message):
    user_choice = message.text.lower()
    bot_choice = random.choice(choices)
    
    result = determine_winner(user_choice, bot_choice)
    
    response = (f"Вы выбрали: {user_choice.capitalize()}\n"
                f"Бот выбрал: {bot_choice.capitalize()}\n\n"
                f"{result}")
    
    bot.reply_to(message, response)

# Запуск бота в режиме постоянного опроса (polling)
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
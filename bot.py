import telebot
import random
import os
import time
import threading

# Получаем токен из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Создаём объект бота
bot = telebot.TeleBot(TOKEN)

# Соответствие: эмодзи → внутренний выбор
emoji_to_choice = {
    '✊': 'камень',
    '✌️': 'ножницы',
    '✋': 'бумага'
}

# Эмодзи для отображения
choice_to_emoji = {
    'камень': '✊',
    'ножницы': '✌️',
    'бумага': '✋'
}

# Функция определения победителя
def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "⚔️ Ничья! ⚔️"
    elif (user_choice == 'камень' and bot_choice == 'ножницы') or \
         (user_choice == 'ножницы' and bot_choice == 'бумага') or \
         (user_choice == 'бумага' and bot_choice == 'камень'):
        return "🏆 Вы выиграли! 🏆"
    else:
        return "😈 Бот выиграл! 😈"

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add('✊', '✌️', '✋')
    
    bot.reply_to(message, 
                 "🎲 Привет! Давай сыграем в 'Камень-ножницы-бумага' 🎲\n"
                 "Выбери свой жест:", 
                 reply_markup=markup)

# Обработка выбора (по эмодзи)
@bot.message_handler(func=lambda message: message.text in emoji_to_choice)
def handle_choice(message):
    user_emoji = message.text
    user_choice = emoji_to_choice[user_emoji]
    bot_choice = random.choice(['камень', 'ножницы', 'бумага'])
    
    # Анимация в отдельном потоке
    def play_animation():
        # Отправляем GIF-анимацию (динамичные кулаки)
        animation_url = "https://cdn.dribbble.com/userupload/23306378/file/original-715b01478a663e164717ffa7305240ae.gif"
        bot.send_animation(message.chat.id, animation_url, caption="Раз... Два... Три!")
        
        time.sleep(3)  # Пауса для просмотра анимации
        
        # Отправка результата
        result = determine_winner(user_choice, bot_choice)
        response = (f"Вы: {user_emoji}\n"
                    f"Бот: {choice_to_emoji[bot_choice]}\n\n"
                    f"{result}")
        bot.send_message(message.chat.id, response)
    
    threading.Thread(target=play_animation).start()

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
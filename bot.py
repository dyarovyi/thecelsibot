import telebot
import requests
import schedule
import config
import time
import threading
from telebot.types import KeyboardButton, Message
from threading import Thread

bot = telebot.TeleBot(config.BOT_TOKEN)
flag = False


# BOT HANDLERS

@bot.message_handler(commands = ['start', 'welcome'])
def welcome_handler(message):
    global chat_id
    chat_id = message
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
    markup.add(KeyboardButton('Get weather'), KeyboardButton('Help'))
    bot.send_message(message.chat.id, config.HELP_STR, reply_markup = markup)


@bot.message_handler(commands = ['checkweather'])
def get_weather_handler(message):
    city = bot.send_message(message.chat.id, "Enter the city:")
    global last_message
    last_message = message
    global last_city
    last_city = city
    flag = True
    bot.register_next_step_handler(city, send_weather)


@bot.message_handler(commands = ['help'])
def help_handler(message):
    bot.send_message(message.chat.id, config.HELP_STR)


@bot.message_handler(content_types = ['text'])
def echo_handler(message):
    if message.text.lower() in ('hey', 'hi', 'hello'):
        welcome_handler(message)
    elif message.text == 'Get weather':
        get_weather_handler(message)
    elif message.text == 'Help':
        help_handler(message)
    else:
        bot.send_message(message.chat.id, 'Sorry, I dont understand this😢')


# PROGRAM FUNCTIONS

def get_weather(city):
    '''This function returns the weather requested'''

    url = config.URL
    parameters = {'APPID': config.WEATHER_API_KEY, 'q': city, 'units': 'metric'}
    response = requests.get(url, parameters)
    weather = response.json()
    return format_response(weather)


def format_response(weather):
    '''This function returns a formatted string of the weather request'''

    try:
        city = weather['name']
        id = int(weather['weather'][0]['id'])
        conditions = weather['weather'][0]['description']
        temperature = int(weather['main']['temp'])
        return 'It is {}ºC and {} in {}{}.'.format(temperature, conditions, city, get_emoji(int(id)))
    except:
        return 'There was a problem with retrieving the information.'


def get_emoji(id: int):
    if 200 <= id < 300:
        return '⚡️'
    elif 300 <= id < 400:
        return '🌧'
    elif id in range(500, 600):
        return '☔️'
    elif id in range(600, 700):
        return '❄️'
    elif id in range(700, 800):
        return '💨'
    elif id == 800:
        return '☀️'
    elif id in range(801, 900):
        return '☁️'
    else:
        return ''


def send_weather(message):
    '''This function sends a message to the user containing weather'''

    try:
        get_weather(message.text)
    except Exception as ex:
        bot.send_message(message.chat.id, 'ex')

    weather = get_weather(message.text)
    bot.send_message(message.chat.id, weather)


def send_scheduled():
    # bot.send_message(chat_id, 'hey')
    weather = get_weather(last_city)
    bot.send_message(chat_id, weather)


def scheduler():
    while not flag:
        continue
    while flag:
        print('scheduler works')
        schedule.every(1).seconds.do(send_scheduled)
        while True:
            schedule.run_pending()
            time.sleep(1)


def main():
    print('main works')
    bot.polling(non_stop = True)


if __name__ == '__main__':
    t2 = threading.Thread(target = scheduler)
    t1 = threading.Thread(target = main)

    # lambda: bot.polling(non_stop = True)

    t2.start()
    t1.start()
import telebot
import requests
import config
import time
import threading
from telebot.types import KeyboardButton
from threading import Thread

UPDATE_TIME = 60 * 60 * 6 # - every 6 hours

bot = telebot.TeleBot(config.BOT_TOKEN)
scheduler_thread = threading.Thread(target = lambda: None)
running = False


# BOT HANDLERS

@bot.message_handler(commands = ['start', 'welcome'])
def welcome_handler(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
    markup.add(KeyboardButton('Weather now'), 
        KeyboardButton('Weather today'),
        KeyboardButton('Set scheduled'), 
        KeyboardButton('Stop scheduled'))
    bot.send_message(message.chat.id, config.INFO_STR, reply_markup = markup)


@bot.message_handler(commands = ['getweathernow', 'getweathertoday'])
def get_weather_handler(message):
    city_message = bot.send_message(message.chat.id, "Enter the city:")

    if message.text == '/getweathertoday' or message.text == 'Weather today':
        bot.register_next_step_handler(city_message, send_weather_today)
    else:
        bot.register_next_step_handler(city_message, send_weather_now)


@bot.message_handler(commands = ['setscheduled'])
def set_scheduled_handler(message):
    city_message = bot.send_message(message.chat.id, "Enter the city:")
    bot.register_next_step_handler(city_message, thread_handler)


@bot.message_handler(commands = ['stopscheduled'])
def stop_scheduled_handler(message):
    global running
    global scheduler_thread

    if running:
        running = False
        scheduler_thread.join()

    bot.send_message(message.chat.id, 'You will no longer get scheduled forecasts.')


@bot.message_handler(commands = ['help'])
def help_handler(message):
    bot.send_message(message.chat.id, config.INFO_STR)


@bot.message_handler(content_types = ['text'])
def echo_handler(message):
    if message.text.lower() in ('hey', 'hi', 'hello'):
        welcome_handler(message)
    elif message.text in ('Weather now', 'Weather today'):
        get_weather_handler(message)
    elif message.text == 'Set scheduled':
        set_scheduled_handler(message)
    elif message.text == 'Stop scheduled':
        stop_scheduled_handler(message)
    elif message.text == 'Help':
        help_handler(message)
    else:
        bot.send_message(message.chat.id, 'Sorry, I dont understand this😢')


# PROGRAM FUNCTIONS

def send_weather_now(message):
    send_weather(message, False)


def send_weather_today(message):
    send_weather(message, True)


def send_weather(message, full):
    '''This function sends a message to the user containing weather'''

    try:
        get_weather(message.text, full)
    except Exception as ex:
        bot.send_message(message.chat.id, 'ex')

    weather = get_weather(message.text, full)
    bot.send_message(message.chat.id, weather)


def get_weather(city, full = False):
    '''This function returns the weather requested'''

    url = config.URL
    parameters = {'APPID': config.WEATHER_API_KEY, 'q': city, 'units': 'metric'}
    response = requests.get(url, parameters)
    weather = response.json()
    return format_response(weather, full)


def format_response(weather, full = False):
    '''This function returns a formatted string of the weather request'''

    try:
        city = weather['name']
        id = int(weather['weather'][0]['id'])
        conditions = weather['weather'][0]['description']
        temperature = int(weather['main']['temp'])

        if full:
            temperature_min = int(weather['main']['temp_min'])
            temperature_max = int(weather['main']['temp_max'])
            wind = weather['wind']['speed']
            pressure = weather['main']['pressure']
            humidity = weather['main']['humidity']
            sunrise = time.strftime("%I:%M", time.localtime(weather['sys']['sunrise']))
            sunset = time.strftime("%I:%M", time.localtime(weather['sys']['sunset']))

            return config.FULL_FORECAST_STR.format(get_emoji(int(id)), temperature_min, temperature_max, conditions, city, sunrise, sunset, wind, pressure, humidity)
        else:
            return 'It is {}ºC and {} in {} {}.'.format(temperature, conditions, city, get_emoji(int(id)))
    except:
        return 'There is a problem with getting the information😢'


def get_emoji(id: int):
    '''This function returns proper emoji for weather conditions'''

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


def thread_handler(message):
    global running
    global scheduler_thread

    if running:
        running = False
        scheduler_thread.join()

    if not running:
        running = True
        scheduler_thread = threading.Thread(target = lambda: scheduler(message))
        scheduler_thread.start()


def scheduler(message):
    '''This function sets scheduled forecasts'''

    while running:
        send_weather(message, True)
        time.sleep(UPDATE_TIME)


if __name__ == '__main__':
    bot.polling(non_stop = True)
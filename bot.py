import telebot
import requests
from telebot.types import KeyboardButton
import config

bot = telebot.TeleBot(config.BOT_TOKEN)


# BOT HANDLERS

@bot.message_handler(commands = ['start'])
def welcome_handler(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
    markup.add(KeyboardButton('Get weather'), KeyboardButton('Help'))
    bot.send_message(message.chat.id, 'Wecome to the Celsi bot!', reply_markup = markup)


@bot.message_handler(commands = ['checkweather'])
def get_weather_handler(message):
    sent = bot.send_message(message.chat.id, "Enter the city:")
    bot.register_next_step_handler(sent, send_weather)


@bot.message_handler(commands = ['help'])
def help_handler(message):
    bot.send_message(message.chat.id, config.HELP_STR)


@bot.message_handler(content_types = ['text'])
def echo_handler(message):
    if message.text == 'Get weather':
        get_weather_handler(message)
    elif message.text == 'Help':
        help_handler(message)
    else:
        bot.send_message(message.chat.id, message.text)


# PROGRAM FUNCTIONS

def format_response(weather):
    '''This function returns a formatted string of the weather request'''

    try:
        city = weather['name']
        conditions = weather['weather'][0]['description']
        temperature = int(weather['main']['temp'])
        return 'It is {}ºC and {} in {}.'.format(temperature, conditions, city)
    except:
        return 'There was a problem with retrieving the information.'


def get_weather(city):
    '''This function returns the weather requested'''

    url = config.URL
    parameters = {'APPID': config.WEATHER_API_KEY, 'q': city, 'units': 'metric'}
    response = requests.get(url, parameters)
    weather = response.json()
    return format_response(weather)


def send_weather(message):
    '''This function sends a message to the user containing weather'''

    try:
        get_weather(message.text)
    except Exception as ex:
        bot.send_message(message.chat.id, 'ex')

    weather = get_weather(message.text)
    bot.send_message(message.chat.id, weather)


def main():
    bot.infinity_polling()


if __name__ == '__main__':
    main()
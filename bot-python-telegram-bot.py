import requests
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Bot
from telegram.ext import Updater, CallbackContext, Filters, MessageHandler
from telegram.utils.request import Request

BOT_TOKEN = '5084440734:AAHBDVwKnourIu6EmEoYq3Z8_Y-j6iUPCok'
WEATHER_API_KEY = 'cc996131a1939fd9766f768090a0b5ea'
URL = 'https://api.openweathermap.org/data/2.5/weather'

KEYBOARD = [
    [KeyboardButton('Get weather at specific place')],
    [KeyboardButton('Get weather at my location')]
]

WAITING_FOR_CITY = False

def format_response(weather):
    '''This function returns a formatted string of the weather request'''

    try:
        city = weather['name']
        conditions = weather['weather'][0]['description']
        temperature = int(weather['main']['temp'])
        return 'It is {} degrees and {} in {}.'.format(temperature, conditions, city)
    except:
        return 'There was a problem with retrieving the information.'


def get_weather(city):
    '''This function returns the weather requested'''

    url = URL
    parameters = {'APPID': WEATHER_API_KEY, 'q': city, 'units': 'metric'}
    response = requests.get(url, parameters)
    weather = response.json()
    return format_response(weather)


def get_weather_button_handler(update: Update, context: CallbackContext):
    '''This is a handler for getting weather.'''
    
    city = update.message.text
    print('City: {}'.format(city))
    update.message.reply_text(text = get_weather(city),reply_markup = ReplyKeyboardRemove())


def message_handler(update: Update, context: CallbackContext):
    '''This is a handler for incoming messages.'''

    text = update.message.text
    if WAITING_FOR_CITY:
        waiting_for_city = False
        return get_weather_button_handler(update, context)

    elif WAITING_FOR_CITY == False and text == 'Get weather at specific place':
        waiting_for_city = True

    reply_markup = ReplyKeyboardMarkup(keyboard = KEYBOARD, resize_keyboard = True)
    update.message.reply_text(text = 'Hey you!', reply_markup = reply_markup)


def main():
    request = Request(connect_timeout = 0.5)
    bot = Bot(request = request, token = BOT_TOKEN)

    updater = Updater(bot = bot, use_context = True)
    updater.dispatcher.add_handler(MessageHandler(filters = Filters.text, callback = message_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
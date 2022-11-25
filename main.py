import keyboard as keyboard
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, update, ForceReply
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, \
    ConversationHandler
from telegram.update import Update
from telegram.ext.updater import Updater
import requests
import json

EXPECT_LATITUDE, EXPECT_LONGITUDE, EXPECT_BUTTON = range(3)
updater = Updater("5574538838:AAHlBF1UeXD1Whyr-Tpe8sR09TY0qctoS7Y", use_context=True)


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the weatherBot")


def help(update: Update, context: CallbackContext):
    update.message.reply_text("use /setll command to start input first latitude and then longitude")


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")
    if query.data == "latitude":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Input Latitude', reply_markup=ForceReply())
        return EXPECT_LATITUDE
    elif query.data == "longitude":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Input Longitude', reply_markup=ForceReply())
        return EXPECT_LONGITUDE


def setll(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("lat", callback_data="latitude"),
            InlineKeyboardButton("long", callback_data="longitude"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("choose smth", reply_markup=reply_markup)
    return EXPECT_BUTTON


def latitude_input(update: Update, context: CallbackContext):
    latitude = update.message.text
    context.chat_data['latitude'] = latitude
    update.message.reply_text(f"Latitude is saved as {latitude}")
    if 'longitude' in context.chat_data:
        say_weather(update, context)
        return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Input Longitude', reply_markup=ForceReply())
        return EXPECT_LONGITUDE


def longitude_input(update: Update, context: CallbackContext):
    longitude = update.message.text
    context.chat_data['longitude'] = longitude
    update.message.reply_text(f'Longitude is saved as {longitude}')
    if 'latitude' in context.chat_data:
        say_weather(update, context)
        return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Input Latitude', reply_markup=ForceReply())
        return EXPECT_LATITUDE


def say_weather(update: Update, context: CallbackContext):
    latitude = context.chat_data['latitude']
    longitude = context.chat_data['longitude']
    context.chat_data['latitude'] = None
    context.chat_data['longitude'] = None
    result = {}

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=a3553685387f0897d9242cb6bc5eb359"
    response = requests.get(url)

    data = response.json()
    print(data)
    lat = data['coord']['lat']
    long = data['coord']['lon']
    current_data = data['main']
    current_temp = (float(current_data['temp']) - 273.15)
    current_hum = current_data['humidity']
    current_cloud = data['clouds']['all']
    current_wind = data['wind']['speed']
    reply_message = f'По координатам {lat} широты и {long} долготы обнаружены следующие погодные данные: ' \
                        '\n Температура: {:.2f}градусов Цельсия'.format(current_temp) +   f'\n Влажность: {current_hum} процентов' \
                        f'\n Скорость ветра: {current_wind}' \
                        f'\n Облачность: {current_cloud}%'
    update.message.reply_text(reply_message)

    #update.message.reply_text("There was a problem. Try again later!")


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Name Conversation cancelled by user. Bye. Send /set_name to start again')
    return ConversationHandler.END


if __name__ == '__main__':
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    conv_handler = ConversationHandler(entry_points=[CommandHandler('setll', setll)],
                                       states={
                                           EXPECT_BUTTON: [CallbackQueryHandler(button)],
                                           EXPECT_LATITUDE: [
                                               MessageHandler(Filters.text, latitude_input)],
                                           EXPECT_LONGITUDE: [
                                               MessageHandler(Filters.text, longitude_input)],

                                       },
                                       fallbacks=[CommandHandler('cancel', cancel)])
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()

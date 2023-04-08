import telebot
from telebot import types
import re

bot = telebot.TeleBot("5946939423:AAHjqwfBDMWDjd4xK_T2yGiSsT-mkir_7pk", parse_mode=None)
user_action = None

@bot.message_handler(commands=['start'])
def start_handler(message):
    global user_action
    user_action = None
    markup = types.ReplyKeyboardMarkup()
    alert_button = types.KeyboardButton("Nowe zgloszenie")
    list_button = types.KeyboardButton("Lista zgloszen")
    search_button = types.KeyboardButton("Szukaj zgloszenia")
    markup.add(alert_button, list_button, search_button)
    bot.send_message(message.chat.id, "Zaczynamy!!!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Nowe zgloszenie")
def add_alert_handler(message):
    global user_action
    user_action = "add"
    bot.send_message(message.chat.id, "Wpisz dane zgłoszenia:")



@bot.message_handler(func=lambda message: message.text == "Lista zgloszen")
def list_alert_handler(message):
    with open("address.txt", "r") as f:
        addresses = f.readlines()
    bot.send_message(message.chat.id, "Lista zgłoszeń:\n" + "\n".join(addresses))


@bot.message_handler(func=lambda message: message.text == "Szukaj zgloszenia")
def search_handler(message):
    global user_action
    user_action = "search"
    bot.send_message(message.chat.id, "Wpisz frazę do wyszukania:")


@bot.message_handler(func=lambda
        message: message.text != "Szukaj zgloszenia" and message.text != "Nowe zgloszenie" and message.text != "Lista zgloszen")
def save_or_search_handler(message):
    global user_action
    if user_action == "add":
        with open("address.txt", "a") as f:
            f.write(message.text + '\n')
        bot.send_message(message.chat.id, "Zgłoszenie zapisano.")
        user_action = None
        start_handler(message)
    elif user_action == "search":
        with open("address.txt", "r") as f:
            addresses = f.readlines()
        search_term = message.text
        results = [address for address in addresses if re.search(search_term, address, re.IGNORECASE)]
        if results:
            bot.send_message(message.chat.id, "Znalezione zgłoszenia:\n" + "\n".join(results))
        else:
            bot.send_message(message.chat.id, "Nie znaleziono zgłoszenia.")
        user_action = None
        start_handler(message)


bot.polling(none_stop=True)


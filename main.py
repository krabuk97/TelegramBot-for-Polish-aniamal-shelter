import telebot
from telebot import types
import sqlite3
import threading
from mytoken import EXACT_TOKEN_TYPES

bot = telebot.TeleBot(EXACT_TOKEN_TYPES, parse_mode=None)
user_action = None

# Połączenie z bazą danych
conn = sqlite3.connect("address.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS address (address_text TEXT)")

# Blokada do synchronizacji dostępu do bazy danych
db_lock = threading.Lock()


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
    with db_lock:
        cur.execute("SELECT address_text FROM address")
        results = cur.fetchall()

    if results:
        formatted_results = "\n".join([result[0] for result in results])
        bot.send_message(message.chat.id, "Lista zgłoszeń:\n" + formatted_results)
    else:
        bot.send_message(message.chat.id, "Brak zgłoszeń.")


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
        address_text = message.text

        with db_lock:
            # Zapisywanie adresu do bazy danych
            cur.execute('INSERT INTO address (address_text) VALUES (?)', (address_text,))
            conn.commit()

        bot.send_message(message.chat.id, "Zgłoszenie zapisano.")
        user_action = None
        start_handler(message)

    elif user_action == "search":
        search_term = message.text

        with db_lock:
            # Wyszukiwanie zgłoszeń w bazie danych
            cur.execute('SELECT address_text FROM address WHERE address_text LIKE ?', ('%' + search_term + '%',))
            results = cur.fetchall()

            if results:
                formatted_results = "\n".join([result[0] for result in results])
                bot.send_message(message.chat.id, "Znalezione zgłoszenia:\n" + formatted_results)
            else:
                bot.send_message(message.chat.id, "Nie znaleziono zgłoszenia.")

            user_action = None
            start_handler(message)


bot.polling(none_stop=True)

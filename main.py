import telebot
from telebot import types
import sqlite3
import threading
from mytoken import EXACT_TOKEN_TYPES


class StartHandler:
    def __init__(self, bot):
        self.bot = bot

    def handle(self, message):
        markup = types.ReplyKeyboardMarkup()
        alert_button = types.KeyboardButton("Nowe zgłoszenie")
        list_button = types.KeyboardButton("Lista zgłoszeń")
        search_button = types.KeyboardButton("Szukaj zgłoszenia")
        markup.add(alert_button, list_button, search_button)
        self.bot.send_message(message.chat.id, "Zaczynamy!!!", reply_markup=markup)


class AddAlertHandler:
    def __init__(self, bot, db_lock, cur, conn):
        self.bot = bot
        self.db_lock = db_lock
        self.cur = cur
        self.conn = conn

    def handle(self, message):
        self.bot.send_message(message.chat.id, "Wpisz dane zgłoszenia:")

        @self.bot.message_handler(func=lambda m: True)
        def save_alert(message):
            address_text = message.text

            with self.db_lock:
                self.cur.execute('INSERT INTO address (address_text) VALUES (?)', (address_text,))
                self.conn.commit()

            self.bot.send_message(message.chat.id, "Zgłoszenie zapisano.")

        self.bot.register_next_step_handler(message, save_alert)


class ListAlertHandler:
    def __init__(self, bot, db_lock, cur):
        self.bot = bot
        self.db_lock = db_lock
        self.cur = cur

    def handle(self, message):
        with self.db_lock:
            self.cur.execute("SELECT address_text FROM address")
            results = self.cur.fetchall()

        if results:
            formatted_results = "\n".join([result[0] for result in results])
            self.bot.send_message(message.chat.id, "Lista zgłoszeń:\n" + formatted_results)
        else:
            self.bot.send_message(message.chat.id, "Brak zgłoszeń.")


class SearchHandler:
    def __init__(self, bot, db_lock, cur):
        self.bot = bot
        self.db_lock = db_lock
        self.cur = cur

    def handle(self, message):
        self.bot.send_message(message.chat.id, "Wpisz frazę do wyszukania:")

        @self.bot.message_handler(func=lambda m: True)
        def search_alert(message):
            search_term = message.text
            with self.db_lock:
                self.cur.execute('SELECT address_text FROM address WHERE address_text LIKE ?', ('%' + search_term + '%',))
                results = self.cur.fetchall()

            if results:
                formatted_results = "\n".join([result[0] for result in results])
                self.bot.send_message(message.chat.id, "Znalezione zgłoszenia:\n" + formatted_results)
            else:
                self.bot.send_message(message.chat.id, "Nie znaleziono zgłoszenia.")

        self.bot.register_next_step_handler(message, search_alert)


class AddressBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token, parse_mode=None)

        # Połączenie z bazą danych
        self.conn = sqlite3.connect("address.db", check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS address (address_text TEXT)")

        # Blokada do synchronizacji dostępu do bazy danych
        self.db_lock = threading.Lock()

        self.start_handler = StartHandler(self.bot)
        self.add_alert_handler = AddAlertHandler(self.bot, self.db_lock, self.cur, self.conn)
        self.list_alert_handler = ListAlertHandler(self.bot, self.db_lock, self.cur)
        self.search_handler = SearchHandler(self.bot, self.db_lock, self.cur)

        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            self.start_handler.handle(message)

        @self.bot.message_handler(func=lambda message: message.text == "Nowe zgłoszenie")
        def add_alert(message):
            self.add_alert_handler.handle(message)

        @self.bot.message_handler(func=lambda message: message.text == "Lista zgłoszeń")
        def list_alert(message):
            self.list_alert_handler.handle(message)

        @self.bot.message_handler(func=lambda message: message.text == "Szukaj zgłoszenia")
        def search(message):
            self.search_handler.handle(message)

    def run(self):
        self.bot.polling(none_stop=True)


TOKEN = EXACT_TOKEN_TYPES

bot = AddressBot(TOKEN)
bot.run()

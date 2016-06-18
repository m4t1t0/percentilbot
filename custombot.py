import telebot
from telebot import types

class CustomBot(telebot.TeleBot):
    def send_html_message(self, chat_id, text):
        return super(CustomBot, self).send_message(chat_id, text, None, None, None, "HTML")

    def reply_markup(self, options):
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        for option in options:
            markup.add(option)

        return markup

    def hide_markup(self):
        markup = types.ReplyKeyboardHide(selective=False)

        return markup


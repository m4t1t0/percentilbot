#!/usr/bin/env python

import telebot

class CustomBot(telebot.TeleBot):
    def send_html_message(self, chat_id, text):
        return super(CustomBot, self).send_message(chat_id, text, None, None, None, "HTML")

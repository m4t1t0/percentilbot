#!/usr/bin/env python

import telebot

class CustomBot(telebot.TeleBot):
    def send_message(self, chat_id, text, parse_mode=None):
        return super(CustomBot, self).send_message(chat_id, text, None, None, None, parse_mode)

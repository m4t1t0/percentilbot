#!/usr/bin/env python

from daemonize import Daemonize
import emoji
import config
import custombot
import db
import query_manager

pid = "/tmp/percentil_telegram.pid"

hubs = [
    {
        'name': 'madrid',
        'db': db.Db(host=config.mad_db_host, user=config.mad_db_user, passwd=config.mad_db_pass, dbname=config.mad_db_name)
    },
    {
        'name': 'berlin',
        'db': db.Db(host=config.ber_db_host, user=config.ber_db_user, passwd=config.ber_db_pass, dbname=config.ber_db_name)
    }
]

default_grouped_data = [
    {
        'name': 'Num',
        'key': 'num',
        'postfix': None,
        'format': '{:1.0f}'
    },
    {
        'name': 'Money',
        'key': 'money',
        'postfix': u"\u20AC",
        'format': '{:1.2f}'
    }
]

def main():
    bot = custombot.CustomBot(config.token)



    manager = query_manager.Manager(hubs)

    ## /start, /help
    @bot.message_handler(commands=['start', 'help'])
    def response_welcome(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
        	print_help(bot, message)

    ## /orders
    @bot.message_handler(commands=['orders', 'o'])
    def response_orders(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            data = manager.get_orders_data()
            message_text = format_message_grouped_data(data, default_grouped_data)
            bot.send_html_message(message.chat.id, message_text)

    ## /purchases
    @bot.message_handler(commands=['purchases', 'p'])
    def response_bought_items(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            data = manager.get_purchases_data()
            message_text = format_message_grouped_data(data, default_grouped_data)
            bot.send_html_message(message.chat.id, message_text)

    ## default handler for every other text
    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def command_default(m):
        bot.reply_to(m, "I don't understand what you say. Maybe try the /help command")

    bot.polling()

def check_auth(message):
    return message.from_user.id in config.auth_users

def response_no_access(bot, message):
    bot.send_message(message.chat.id, "Access denied! try to contact tech manager with id: {}".format(message.from_user.id))

def print_help(bot, message):
    commands = {
        'start': 'Get used to the bot',
        'help': 'Gives you information about the available commands',
        'orders, /o': 'Get data about the correct orders in both hubs',
        'purchases, /p': 'Get data about items bought in both hubs',
    }

    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += "/" + key + " " + u"\u2192" + " "
        help_text += commands[key] + "\n"
    bot.send_message(message.chat.id, help_text)

def format_message_grouped_data(data, grouped_data):
    message_text = ''
    for hub in hubs:
        message_text += '\n\n<b>{}</b>'.format(hub['name'].upper())

        for gd in grouped_data:
            message_text += "\n\t\t" + u"\u2192".format(gd['name'])
            if data[hub['name']]['data'] is None:
                message_text += ' -'
            else:
                for value in data[hub['name']]['data']:
                    message_text += ' {}: <code>{}</code>' \
                    .format(
                        value['subtype'],
                        format_result(value[gd['key']], gd['postfix'], gd['format'])
                    )

        for gd in grouped_data:
            if data[hub['name']]['data'] is not None:
                message_text += '\n<b>{}:</b> <code>{}</code>' \
                    .format(
                        gd['name'],
                        format_result(data[hub['name']]['subtotal'][gd['key']], gd['postfix'], gd['format'])
                    )
    
    return message_text

def format_result(value, postfix=None, _format='{:1.0f}'):
    if value == "-":
        return value
    else:
        _str = _format.format(value)
        if postfix is not None:
            return _str + postfix
        else:
            return _str

main()

#daemon = Daemonize(app="percentil_telegram", pid=pid, action=main)
#daemon.start()

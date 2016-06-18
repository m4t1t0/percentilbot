#!/usr/bin/env python

from daemonize import Daemonize
import emoji
import config
import custombot
from telebot import types
import db
import time
import datetime
from dateutil.parser import parse
import collections
import query_manager
import step_manager

pid = "/tmp/percentil_telegram.pid"

hubs = collections.OrderedDict()
hubs['madrid'] = {'name': 'Madrid', 'db': db.Db(host=config.mad_db_host, user=config.mad_db_user, 
    passwd=config.mad_db_pass, dbname=config.mad_db_name)}
hubs['berlin'] = {'name': 'Berlín', 'db': db.Db(host=config.ber_db_host, user=config.ber_db_user, 
    passwd=config.ber_db_pass, dbname=config.ber_db_name)}

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

user_steps = {}

def main():
    bot = custombot.CustomBot(config.token)
    manager = query_manager.Manager()

    ## /start, /help
    @bot.message_handler(commands=['start', 'help'])
    def response_welcome(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            uid = message.chat.id
            step = step_manager.UserStep(uid)
            user_steps[uid] = step
            print_help(bot, message)

    ## /help
    @bot.message_handler(commands=['help'])
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
            uid = message.chat.id
            markup = bot.reply_markup(hubs)
            bot.send_message(uid, 'Please choose hub', reply_markup=markup)
            user_steps[uid].set_step(1)
            user_steps[uid].set_command('orders')

    ## /orders step 1
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 1
        and user_steps[message.chat.id].get_command() == 'orders')
    def response_orders_step_1(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            selected_hub = message.text
            if selected_hub not in hubs:
                bot.send_html_message(message.chat.id, selected_hub + ' is not a valid hub')
            else:
                uid = message.chat.id
                markup = bot.reply_markup(['today', 'yesterday'])
                bot.send_message(uid, 'Please choose date', reply_markup=markup)
                user_steps[uid].set_step(2)
                user_steps[uid].set_command('orders')
                user_steps[uid].save_response(1, selected_hub)

    ## /orders step 2
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 2
        and user_steps[message.chat.id].get_command() == 'orders')
    def response_orders_step_2(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            selected_date = validate_date(message.text)

            if not selected_date:
                bot.send_html_message(message.chat.id, 'Wrong date, correct format: YYYY-MM-DD')
            else:
                uid = message.chat.id
                markup = bot.reply_markup(manager.get_orders_available_grouping())
                bot.send_message(uid, 'Please choose grouping', reply_markup=markup)
                user_steps[uid].set_step(3)
                user_steps[uid].set_command('orders')
                user_steps[uid].save_response(2, selected_date)

    ## /orders step 3
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 3
        and user_steps[message.chat.id].get_command() == 'orders')
    def response_orders_step_3(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            selected_grouping = validate_grouping(manager, user_steps[message.chat.id].get_command(), message.text)

            if not selected_grouping:
                bot.send_html_message(message.chat.id, 'Wrong grouping method')
            else:
                uid = message.chat.id
                markup = bot.hide_markup()
                bot.send_message(uid, selected_grouping, reply_markup=markup)

                selected_hub = user_steps[uid].get_response(1)
                selected_date = user_steps[uid].get_response(2)
                data = manager.get_orders_data(hubs[selected_hub], selected_grouping, selected_date)
                header = [hubs[selected_hub], str(selected_date), message.text]
                message_text = format_message_grouped_data(data, header, default_grouped_data)
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
    auth = message.from_user.id in config.auth_users
    if auth == True:
        uid = message.chat.id
        if uid not in user_steps:
            step = step_manager.UserStep(uid)
            user_steps[uid] = step
        return True
    else:
        return False
        
def response_no_access(bot, message):
    bot.send_message(message.chat.id, "Access denied! try to contact tech manager with id: {}".format(message.from_user.id))

def print_help(bot, message):
    commands = collections.OrderedDict()
    commands['start'] = 'Get used to the bot'
    commands['help'] = 'Gives you information about the available commands'
    commands['orders, /o'] = 'Get data about the correct orders in both hubs'
    commands['purchases, /p'] = 'Get data about items bought in both hubs'

    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += "/" + key + " " + u"\u2192" + " "
        help_text += commands[key] + "\n"
    bot.send_message(message.chat.id, help_text)

def format_message_grouped_data(data, header, grouped_data):
    message_text = ''
    message_text += '\n\n<b>{}</b>'.format(header[0]['name'].upper())
    header.pop(0)
    for head in header:
        message_text += ' <i>{}</i>'.format(head)

    for gd in grouped_data:
        message_text += "\n\t\t" + u"\u2192".format(gd['name'])
        if data['data'] is None:
            message_text += ' -'
        else:
            for value in data['data']:
                message_text += ' {}: <code>{}</code>' \
                .format(
                    value['grouping_type'],
                    format_result(value[gd['key']], gd['postfix'], gd['format'])
                )

    for gd in grouped_data:
        if data['data'] is not None:
            message_text += '\n<b>{}:</b> <code>{}</code>' \
                .format(
                    gd['name'],
                    format_result(data['total'][gd['key']], gd['postfix'], gd['format'])
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

def validate_date(text_date):
    if text_date == 'today':
        return datetime.date.today()

    if text_date == 'yesterday':
        return datetime.date.today() - datetime.timedelta(days=1)

    try:
        return parse(text_date).date()
    except ValueError:
        return None

def validate_grouping(manager, type, grouping):
    if (type == 'orders'):
        available = manager.get_orders_available_grouping()
        if grouping not in available:
            return None
        else:
            return available[grouping]

main()

#daemon = Daemonize(app="percentil_telegram", pid=pid, action=main)
#daemon.start()

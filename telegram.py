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
from query_manager import Manager
import step_manager

pid = "/tmp/percentil_telegram.pid"

hubs = collections.OrderedDict()
hubs['madrid'] = {'name': 'Madrid', 'db': db.Db(host=config.mad_db_host, user=config.mad_db_user, 
    passwd=config.mad_db_pass, dbname=config.mad_db_name)}
hubs['berlin'] = {'name': 'Berlín', 'db': db.Db(host=config.ber_db_host, user=config.ber_db_user, 
    passwd=config.ber_db_pass, dbname=config.ber_db_name)}

user_steps = {}

def main():
    bot = custombot.CustomBot(config.token)
    manager = Manager()

    initialize()

    ## /start, /help
    @bot.message_handler(commands=['start', 'help'])
    def response_welcome(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
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
        response_step_0(message, 'orders')

    ## /orders step 1
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 1
        and user_steps[message.chat.id].get_command() == 'orders')
    def response_orders_step_1(message):
        response_step_1(message, user_steps[message.chat.id].get_command())

    ## /orders step 2
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 2
        and user_steps[message.chat.id].get_command() == 'orders')
    def response_orders_step_2(message):
        response_step_2(message, user_steps[message.chat.id].get_command())

    ## /orders step 3
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 3
        and user_steps[message.chat.id].get_command() == 'orders')
    def response_orders_step_3(message):
        response_step_3(message, user_steps[message.chat.id].get_command())

    ## /purchases
    @bot.message_handler(commands=['purchases', 'p'])
    def response_purchases(message):
        response_step_0(message, 'purchases')

    ## /purchases step 1
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 1
        and user_steps[message.chat.id].get_command() == 'purchases')
    def response_purchases_step_1(message):
        response_step_1(message, user_steps[message.chat.id].get_command())

    ## /purchases step 2
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 2
        and user_steps[message.chat.id].get_command() == 'purchases')
    def response_purchases_step_2(message):
        response_step_2(message, user_steps[message.chat.id].get_command())

    ## /purchases step 3
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 3
        and user_steps[message.chat.id].get_command() == 'purchases')
    def response_purchases_step_3(message):
        response_step_3(message, user_steps[message.chat.id].get_command())

    ## /items_sold
    @bot.message_handler(commands=['items_sold', 'is'])
    def response_items_sold(message):
        response_step_0(message, 'items_sold')

    ## /items_sold step 1
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 1
        and user_steps[message.chat.id].get_command() == 'items_sold')
    def response_items_sold_step_1(message):
        response_step_1(message, user_steps[message.chat.id].get_command())

    ## /items_sold step 2
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 2
        and user_steps[message.chat.id].get_command() == 'items_sold')
    def response_items_sold_step_2(message):
        response_step_2(message, user_steps[message.chat.id].get_command())

    ## /items_sold step 3
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 3
        and user_steps[message.chat.id].get_command() == 'items_sold')
    def response_items_sold_step_3(message):
        response_step_3(message, user_steps[message.chat.id].get_command())

    def response_step_0(message, command):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            uid = message.chat.id
            markup = bot.reply_markup(hubs)
            bot.send_message(uid, 'Please choose hub', reply_markup=markup)
            user_steps[uid].set_step(1)
            user_steps[uid].set_command(command)

    def response_step_1(message, command):
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
                user_steps[uid].save_response(1, selected_hub)

    def response_step_2(message, command):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            selected_date = validate_date(message.text)

            if not selected_date:
                bot.send_html_message(message.chat.id, 'Wrong date, correct format: YYYY-MM-DD')
            else:
                uid = message.chat.id
                available_grouping = getattr(globals()['Manager'](), 'get_' + command + '_available_grouping')()
                markup = bot.reply_markup(available_grouping)
                bot.send_message(uid, 'Please choose grouping', reply_markup=markup)
                user_steps[uid].set_step(3)
                user_steps[uid].save_response(2, selected_date)

    def response_step_3(message, command):
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
                data = getattr(globals()['Manager'](), 'get_' + command + '_data')(hubs[selected_hub], selected_grouping, selected_date)
                header = [hubs[selected_hub], u"\u2021", command, u"\u2021", str(selected_date), u"\u2021", message.text]
                grouped_data = getattr(globals()['Manager'](), 'get_' + command + '_grouped_data_format')()
                message_text = format_message_grouped_data(data, header, grouped_data)
                bot.send_html_message(message.chat.id, message_text)
                user_steps[uid].reset()

    ## default handler for every other text
    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def command_default(m):
        bot.reply_to(m, "I don't understand what you say. Maybe try the /help command")

    bot.polling()

def initialize():
    for uid in config.auth_users:
        step = step_manager.UserStep(uid)
        user_steps[uid] = step

def check_auth(message):
    return message.from_user.id in config.auth_users
        
def response_no_access(bot, message):
    bot.send_message(message.chat.id, "Access denied! try to contact tech manager with id: {}".format(message.from_user.id))

def print_help(bot, message):
    commands = collections.OrderedDict()
    commands['/start'] = 'Get used to the bot'
    commands['/help'] = 'Gives you information about the available commands'
    commands['/orders, /o'] = 'Get data about the correct orders in both hubs'
    commands['/purchases, /p'] = 'Get data about items bought in both hubs'
    commands['/items_sold, /is'] = 'Get data about items sold in both hubs'

    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += key + " " + u"\u2192" + " "
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

def validate_grouping(manager, command, grouping):
    available = getattr(globals()['Manager'](), 'get_' + command + '_available_grouping')()
    if grouping not in available:
        return None
    else:
        return available[grouping]

main()

#daemon = Daemonize(app="percentil_telegram", pid=pid, action=main)
#daemon.start()

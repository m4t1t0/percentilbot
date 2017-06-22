#!/usr/bin/env python

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

mainDb = db.Db(host=config.db_host, user=config.db_user, passwd=config.db_pass, dbname=config.db_name)
user_steps = {}
user_auths = []

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

    ## /orders step 1
    @bot.message_handler(commands=['orders'])
    def response_orders_step_1(message):
        response_step_1(message, 'orders')

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

    ## /purchases step 1
    @bot.message_handler(commands=['purchases'])
    def response_purchases_step_1(message):
        response_step_1(message, 'purchases')

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

    ## /items_sold step 1
    @bot.message_handler(commands=['items_sold'])
    def response_items_sold_step_1(message):
        response_step_1(message, 'items_sold')

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

    ## /bags_requested step 1
    @bot.message_handler(commands=['bags_requested'])
    def response_bags_requested_step_1(message):
        response_step_1(message, 'bags_requested')

    ## /bags_requested step 2
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 2
        and user_steps[message.chat.id].get_command() == 'bags_requested')
    def response_bags_requested_step_2(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            selected_date = validate_date(message.text)

            if not selected_date:
                bot.send_html_message(message.chat.id, 'Wrong date, correct format: YYYY-MM-DD')
            else:
                uid = message.chat.id
                markup = bot.hide_markup()
                bot.send_message(uid, selected_date, reply_markup=markup)

                data = manager.get_bags_requested_data(mainDb, selected_date)
                header = [u"\u2021", 'bags_requested', u"\u2021", str(selected_date)]
                grouped_data = manager.get_bag_request_grouped_data_format()
                message_text = format_message_grouped_data(data, header, grouped_data)
                bot.send_html_message(message.chat.id, message_text)
                user_steps[uid].reset()

    ## /bags_in step 1
    @bot.message_handler(commands=['bags_in'])
    def response_bags_in_step_1(message):
        response_step_1(message, 'bags_in')

    ## /bags_in step 2
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 2
        and user_steps[message.chat.id].get_command() == 'bags_in')
    def response_bags_in_step_2(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            selected_date = validate_date(message.text)

            if not selected_date:
                bot.send_html_message(message.chat.id, 'Wrong date, correct format: YYYY-MM-DD')
            else:
                uid = message.chat.id
                markup = bot.hide_markup()
                bot.send_message(uid, selected_date, reply_markup=markup)

                data = manager.get_bags_in_data(mainDb, selected_date)
                header = [u"\u2021", 'bags_in', u"\u2021", str(selected_date)]
                grouped_data = manager.get_bag_request_grouped_data_format()
                message_text = format_message_grouped_data(data, header, grouped_data)
                bot.send_html_message(message.chat.id, message_text)
                user_steps[uid].reset()

    ## /missing_items step 1
    @bot.message_handler(commands=['missing_items'])
    def response_missing_items_step_1(message):
        response_step_1(message, 'missing_items')

    ## /missing_items step 2
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 2
        and user_steps[message.chat.id].get_command() == 'missing_items')
    def response_missing_items_step_2(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            selected_date = validate_date(message.text)

            if not selected_date:
                bot.send_html_message(message.chat.id, 'Wrong date, correct format: YYYY-MM-DD')
            else:
                uid = message.chat.id
                markup = bot.hide_markup()
                bot.send_message(uid, selected_date, reply_markup=markup)

                data = manager.get_missing_items_data(mainDb, selected_date)
                header = [u"\u2021", 'missing_items', u"\u2021", str(selected_date)]
                message_text = format_message_simple_data(data, header, ['hold', 'missing'])
                bot.send_html_message(message.chat.id, message_text)
                user_steps[uid].reset()

    ## /new_shoppers step 1
    @bot.message_handler(commands=['new_shoppers'])
    def response_new_shoppers_step_1(message):
        response_step_1(message, 'new_shoppers')

    ## /new_shoppers step 2
    @bot.message_handler(func=lambda message: user_steps[message.chat.id].get_step() == 2
        and user_steps[message.chat.id].get_command() == 'new_shoppers')
    def response_new_shoppers_step_2(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            selected_date = validate_date(message.text)

            if not selected_date:
                bot.send_html_message(message.chat.id, 'Wrong date, correct format: YYYY-MM-DD')
            else:
                uid = message.chat.id
                markup = bot.hide_markup()
                bot.send_message(uid, selected_date, reply_markup=markup)

                data = manager.get_new_shoppers_data(mainDb, selected_date)
                header = [u"\u2021", 'new_shoppers', u"\u2021", str(selected_date)]
                grouped_data = manager.get_bag_request_grouped_data_format()
                message_text = format_message_grouped_data(data, header, grouped_data)
                bot.send_html_message(message.chat.id, message_text)
                user_steps[uid].reset()

    def response_step_1(message, command):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            uid = message.chat.id
            markup = bot.reply_markup(['today', 'yesterday'])
            bot.send_message(uid, 'Please choose date', reply_markup=markup)
            user_steps[uid].set_step(2)
            user_steps[uid].set_command(command)

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

                selected_date = user_steps[uid].get_response(2)
                data = getattr(globals()['Manager'](), 'get_' + command + '_data')(mainDb, selected_grouping, selected_date)
                header = [u"\u2021", command, u"\u2021", str(selected_date), u"\u2021", message.text]
                grouped_data = getattr(globals()['Manager'](), 'get_' + command + '_grouped_data_format')()
                message_text = format_message_grouped_data(data, header, grouped_data)
                bot.send_html_message(message.chat.id, message_text)
                user_steps[uid].reset()

    ## default handler for every other text
    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def command_default(message):
        bot.reply_to(message, "I don't understand what you say. Maybe try the /help command")

    ## Notification handler based on severity
    @bot.notification_handler(severity=['error'])
    def notification_error(notification):
        for auth in config.auth_users:
            if ('admin' in auth['roles']):
                bot.send_html_message(auth['uid'], notification['text'])

    @bot.notification_handler(func=lambda notification: True)
    def notification_default(notification):
        for auth in config.auth_users:
            if (notification['role'] in auth['roles']):
                bot.send_html_message(auth['uid'], notification['text'])

    bot.polling()

def initialize():
    for auth in config.auth_users:
        uid = auth['uid']
        step = step_manager.UserStep(uid)
        user_steps[uid] = step
        user_auths.append(uid)

def check_auth(message):
    return message.from_user.id in user_auths

def response_no_access(bot, message):
    bot.send_message(message.chat.id, "Access denied! try to contact tech manager with id: {}".format(message.from_user.id))

def print_help(bot, message):
    # Commands to send to botfather
    # start - Get used to the bot
    # help - Gives you information about the available commands
    # orders - Get data about the correct orders
    # purchases - Get data about items processed
    # items_sold - Get data about items sold
    # bags_requested - Get data about the bags requested
    # bags_in - Get data about the bags
    # missing_items - Get information about hold items and picking misses
    # new_shoppers - Get information about new shoppers

    commands = collections.OrderedDict()
    commands['/start'] = 'Get used to the bot'
    commands['/help'] = 'Gives you information about the available commands'
    commands['/orders'] = 'Get data about the correct orders'
    commands['/purchases'] = 'Get data about items processed'
    commands['/items_sold'] = 'Get data about items sold'
    commands['/bags_requested'] = 'Get data about the bags requested'
    commands['/bags_in'] = 'Get data about the bags'
    commands['/missing_items'] = 'Get information about hold items and picking misses'
    commands['/new_shoppers'] = 'Get information about new shoppers'

    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += key + " " + u"\u2192" + " "
        help_text += commands[key] + "\n"
    bot.send_message(message.chat.id, help_text)

def format_message_simple_data(data, header, keys):
    message_text = ''
    for head in header:
        message_text += ' <i>{}</i>'.format(head)

    for dt in data:
        for key in keys:
            message_text += "\n\t\t" + u"\u2192 {}: ".format(key)
            if dt[key] is None:
                message_text += '-'
            else:
                message_text += str(dt[key])

    return message_text

def format_message_grouped_data(data, header, grouped_data):
    message_text = ''
    for head in header:
        message_text += ' <i>{}</i>'.format(head)

    for gd in grouped_data:
        message_text += "\n\t\t" + u"\u2192"
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

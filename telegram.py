#!/usr/bin/env python

from time import sleep
from daemonize import Daemonize
import time
import config
import custombot
import _mysql

pid = "/tmp/percentil_telegram.pid"

def main():
    bot = custombot.CustomBot(config.token)

    db_pct = _mysql.connect(host=config.pct_db_host, user=config.pct_db_user, passwd=config.pct_db_pass, db=config.pct_db_name)
    db_krd = _mysql.connect(host=config.krd_db_host, user=config.krd_db_user, passwd=config.krd_db_pass, db=config.krd_db_name)

    ## /start, /help
    @bot.message_handler(commands=['start', 'help'])
    def response_welcome(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
        	print_help(bot, message)
    
    ## /orders
    @bot.message_handler(commands=['orders'])
    def response_orders(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            try:
                num_orders_pct = int(get_num_orders(db_pct))
            except ValueError:
                num_orders_pct = '-'

            try:
                num_orders_krd = int(get_num_orders(db_krd))
            except ValueError:
                num_orders_krd = '-'

            total = get_total(num_orders_pct, num_orders_krd)
            
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>" \
                .format(format_result(num_orders_pct), format_result(num_orders_krd), format_result(total))
            bot.send_html_message(message.chat.id, message_text)

    ## /money
    @bot.message_handler(commands=['money'])
    def response_orders(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            try:
                money_pct = float(get_money(db_pct))
            except ValueError:
                money_pct = '-'

            try:
                money_krd = float(get_money(db_krd))
            except ValueError:
                money_krd = '-'

            total = get_total(money_pct, money_krd)
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>" \
                .format(format_result(money_pct, "€", "{:1.2f}"), format_result(money_krd, "€", "{:1.2f}"), format_result(total, "€", "{:1.2f}"))
            bot.send_html_message(message.chat.id, message_text)

    ## /wrong_orders
    @bot.message_handler(commands=['wrong_orders'])
    def response_wrong_orders(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            try:
                wrong_orders_pct = int(get_num_wrong_orders(db_pct))
            except ValueError:
                wrong_orders_pct = '-'

            try:
                wrong_orders_krd = int(get_num_wrong_orders(db_krd))
            except ValueError:
                wrong_orders_krd = '-'

            total = get_total(wrong_orders_pct, wrong_orders_krd)
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>" \
                .format(format_result(wrong_orders_pct), format_result(wrong_orders_krd), format_result(total))
            bot.send_html_message(message.chat.id, message_text)

    ## /buyed_items
    @bot.message_handler(commands=['buyed_items'])
    def response_buyed_items(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            try:
                buyed_items_pct = int(get_buyed_items(db_pct))
            except ValueError:
                buyed_items_pct = '-'

            try:
                buyed_items_krd = int(get_buyed_items(db_krd))
            except ValueError:
                buyed_items_krd = '-'

            total = get_total(buyed_items_pct, buyed_items_krd)
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>" \
                .format(format_result(buyed_items_pct), format_result(buyed_items_krd), format_result(total))
            bot.send_html_message(message.chat.id, message_text)

    ## /buyed_money
    @bot.message_handler(commands=['buyed_money'])
    def response_buyed_items(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            try:
                buyed_money_pct = float(get_buyed_money(db_pct))
            except ValueError:
                buyed_money_pct = '-'

            try:
                buyed_money_krd = float(get_buyed_money(db_krd))
            except ValueError:
                buyed_money_krd = '-'

            total = get_total(buyed_money_pct, buyed_money_krd)
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>" \
                .format(format_result(buyed_money_pct, "€", "{:1.2f}"), format_result(buyed_money_krd, "€", "{:1.2f}"), format_result(total, "€", "{:1.2f}"))
            bot.send_html_message(message.chat.id, message_text)

    ## filter on a greeting
    @bot.message_handler(func=lambda message: message.text.lower() == "hi".lower() or message.text.lower() == "hello".lower())
    def command_text_hi(m):
        bot.send_message(m.chat.id, "I'm not allowed to socialize, if you want conversation try to speak with another human!")

    ## filter on a insult
    @bot.message_handler(func=lambda message: message.text.lower() == "fuck you".lower() or message.text.lower() == "fuck you!".lower())
    def command_text_hi(m):
        bot.send_message(m.chat.id, "Fuck you too!")

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
        'orders': 'Get the number of correct orders in both hubs',
        'money': 'Get the amount of money from correct orders in both hubs',
        'wrong_orders': 'Get the number of wrong orders in both hubs',
        'buyed_items': 'Get the number of items buyed in both hubs',
        'buyed_money': 'Get the fiscal price of the items buyed in both hubs'
    }

    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += "/" + key + " " + u"\u2192" + " "
        help_text += commands[key] + "\n"
    bot.send_message(message.chat.id, help_text)

def get_num_orders(db):
    today = time.strftime("%Y-%m-%d") + ' 00:00:00'
    try: 
        db.query("""
            SELECT COUNT(*) AS num
            FROM ps_orders o
            INNER JOIN PercentilOrder po
            ON o.id_order = po.id_order
            WHERE o.date_add >= '{}'
            AND po.id_order_state IN ({})
            """.format(today, config.valid_order_states))
        r = db.store_result()
        data = r.fetch_row()
        return data[0][0]
    except:
        return '-'

def get_money(db):
    today = time.strftime("%Y-%m-%d") + ' 00:00:00'
    try:
        db.query("""
            SELECT SUM(total_paid_real) AS num
            FROM ps_orders o
            INNER JOIN PercentilOrder po
            ON o.id_order = po.id_order
            WHERE o.date_add >= '{}'
            AND po.id_order_state IN ({})
            """.format(today, config.valid_order_states))
        r = db.store_result()
        data = r.fetch_row()
        result = data[0][0]
        if result is None:
            return 0
        else:
            return result
    except:
        return '-'

def get_num_wrong_orders(db):
    today = time.strftime("%Y-%m-%d") + ' 00:00:00'
    try:
        db.query("""
            SELECT COUNT(*) AS num
            FROM ps_orders o
            LEFT JOIN PercentilOrder po
            ON o.id_order = po.id_order
            WHERE o.date_add >= '{}'
            AND (po.id_order IS NULL OR po.id_order_state IN ({}))
            """.format(today, config.wrong_order_states))
        r = db.store_result()
        data = r.fetch_row()
        return data[0][0]
    except:
        return '-'

def get_buyed_items(db):
    today = time.strftime("%Y-%m-%d") + ' 00:00:00'
    try:
        db.query("""
            SELECT COUNT(*) AS num
            FROM PercentilProduct pp
            WHERE pp.processedOn >= '{}'
            AND pp.status NOT IN ('Lost', 'Discarded', 'Discarded_Hiper')
            """.format(today))
        r = db.store_result()
        data = r.fetch_row()
        return data[0][0]
    except:
        return '-'

def get_buyed_money(db):
    today = time.strftime("%Y-%m-%d") + ' 00:00:00'
    try:
        db.query("""
            SELECT SUM(pp.fiscal_price) AS num
            FROM PercentilProduct pp
            WHERE pp.processedOn >= '{}'
            AND pp.status NOT IN ('Lost', 'Discarded', 'Discarded_Hiper')
            """.format(today))
        r = db.store_result()
        data = r.fetch_row()
        result = data[0][0]
        if result is None:
            return 0
        else:
            return result
    except:
        return '-'

def get_total(value1, value2):
    if value1 == '-' or value2 == '-':
        return '-'
    else:
        return value1 + value2

def format_result(value, prefix=None, _format="{:1.0f}"):
    if value == "-":
        return value
    else:
        _str = _format.format(value)
        if prefix is not None:
            return _str + prefix
        else:
            return _str

main()

daemon = Daemonize(app="percentil_telegram", pid=pid, action=main)
daemon.start()

#!/usr/bin/env python

from time import sleep
from daemonize import Daemonize
import time
import config
import custombot
import _mysql

#pid = "/tmp/percentil_telegram.pid"

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
            num_orders_pct = get_num_orders(db_pct)
            num_orders_krd = get_num_orders(db_krd)
            total = int(num_orders_pct) + int(num_orders_krd)
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>".format(num_orders_pct, num_orders_krd, total)
            bot.send_html_message(message.chat.id, message_text)

    ## /money
    @bot.message_handler(commands=['money'])
    def response_orders(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            money_pct = get_money(db_pct)
            money_krd = get_money(db_krd)
            total = float(money_pct) + float(money_krd)
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>".format(money_pct + "€", money_krd + "€", str(total) + "€")
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
        'orders': 'Get the amount of correct orders in both hubs',
        'money': 'Get the amount of money from correct orders in both hubs'
    }

    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += "/" + key + " " + u"\u2192" + " "
        help_text += commands[key] + "\n"
    bot.send_message(message.chat.id, help_text)

def get_num_orders(db):
    today = time.strftime("%Y-%m-%d") + ' 00:00:00'
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

def get_money(db):
    today = time.strftime("%Y-%m-%d") + ' 00:00:00'
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
    return data[0][0]

main()

#daemon = Daemonize(app="percentil_telegram", pid=pid, action=main)
#daemon.start()

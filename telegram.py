#!/usr/bin/env python

from time import sleep
from daemonize import Daemonize
import time
import config
import telebot
import _mysql

#pid = "/tmp/percentil_telegram.pid"

def main():
    bot = telebot.TeleBot(config.token)
    db_pct = _mysql.connect(host=config.pct_db_host, user=config.pct_db_user, passwd=config.pct_db_pass, db=config.pct_db_name)
    db_krd = _mysql.connect(host=config.krd_db_host, user=config.krd_db_user, passwd=config.krd_db_pass, db=config.krd_db_name)

    ## START, HELP
    @bot.message_handler(commands=['start', 'help'])
    def response_welcome(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
        	print_help(bot, message)
    
    ## ORDERS
    @bot.message_handler(commands=['orders'])
    def response_orders(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            num_orders_pct = get_num_orders(db_pct)
            num_orders_krd = get_num_orders(db_krd)
            message_text = "MADRID: {}\nBERLIN: {}".format(num_orders_pct, num_orders_krd)
            bot.send_message(message.chat.id, message_text)
    
    bot.polling()

def check_auth(message):
    return message.from_user.id in config.auth_users

def response_no_access(bot, message):
    bot.send_message(message.chat.id, "Access denied! try to contact tech manager with id: {}".format(message.from_user.id))

def print_help(bot, message):
    message_text = """
    Available commands:
    /orders
    /money
    """
    bot.send_message(message.chat.id, message_text)

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

main()

#daemon = Daemonize(app="percentil_telegram", pid=pid, action=main)
#daemon.start()


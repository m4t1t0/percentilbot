#!/usr/bin/env python

from daemonize import Daemonize
import config
import custombot
import db
import query_manager

pid = "/tmp/percentil_telegram.pid"

def main():
    bot = custombot.CustomBot(config.token)

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
    @bot.message_handler(commands=['orders'])
    def response_orders(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            data = manager.get_orders_data()
            message_text = "<b>MADRID:</b>\n<b>Num:</b> K: <code>{}</code> | W: <code>{}</code> | M: <code>{}</code> | T: <code>{}</code>\n" \
                "<b>Money:</b> K: <code>{}</code> | W: <code>{}</code> | M: <code>{}</code> | T: <code>{}</code>\n\n" \
                "<b>BERLIN:</b>\n<b>Num:</b> K: <code>{}</code> | W: <code>{}</code> | M: <code>{}</code> | T: <code>{}</code>\n" \
                "<b>Money:</b> K: <code>{}</code> | W: <code>{}</code> | M: <code>{}</code> | T: <code>{}</code>" \
                .format(
                    format_result(data['madrid']['data'][0]['num']),
                    format_result(data['madrid']['data'][1]['num']),
                    format_result(data['madrid']['data'][2]['num']),
                    format_result(data['madrid']['subtotal']['num']),
                    format_result(data['madrid']['data'][0]['money'], u"\u20AC", "{:1.2f}"),
                    format_result(data['madrid']['data'][1]['money'], u"\u20AC", "{:1.2f}"),
                    format_result(data['madrid']['data'][2]['money'], u"\u20AC", "{:1.2f}"),
                    format_result(data['madrid']['subtotal']['money'], u"\u20AC", "{:1.2f}"),
                    format_result(data['berlin']['data'][0]['num']),
                    format_result(data['berlin']['data'][1]['num']),
                    format_result(data['berlin']['data'][2]['num']),
                    format_result(data['berlin']['subtotal']['num']),
                    format_result(data['berlin']['data'][0]['money'], u"\u20AC", "{:1.2f}"),
                    format_result(data['berlin']['data'][1]['money'], u"\u20AC", "{:1.2f}"),
                    format_result(data['berlin']['data'][2]['money'], u"\u20AC", "{:1.2f}"),
                    format_result(data['berlin']['subtotal']['money'], u"\u20AC", "{:1.2f}")
                    )
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
                .format(format_result(money_pct, u"\u20AC", "{:1.2f}"), format_result(money_krd, u"\u20AC", "{:1.2f}"), format_result(total, u"\u20AC", "{:1.2f}"))
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

    ## /bought_items
    @bot.message_handler(commands=['bought_items'])
    def response_bought_items(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            try:
                bought_items_pct = int(get_bought_items(db_pct))
            except ValueError:
                bought_items_pct = '-'

            try:
                bought_items_krd = int(get_bought_items(db_krd))
            except ValueError:
                bought_items_krd = '-'

            total = get_total(bought_items_pct, bought_items_krd)
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>" \
                .format(format_result(bought_items_pct), format_result(bought_items_krd), format_result(total))
            bot.send_html_message(message.chat.id, message_text)

    ## /bought_money
    @bot.message_handler(commands=['bought_money'])
    def response_bought_items(message):
        if not check_auth(message):
            response_no_access(bot, message);
            return
        else:
            try:
                bought_money_pct = float(get_bought_money(db_pct))
            except ValueError:
                bought_money_pct = '-'

            try:
                bought_money_krd = float(get_bought_money(db_krd))
            except ValueError:
                bought_money_krd = '-'

            total = get_total(bought_money_pct, bought_money_krd)
            message_text = "<b>MADRID:</b> <code>{}</code>\n<b>BERLIN:</b> <code>{}</code>\n<b>TOTAL:</b> <code>{}</code>" \
                .format(format_result(bought_money_pct, u"\u20AC", "{:1.2f}"), format_result(bought_money_krd, u"\u20AC", "{:1.2f}"), format_result(total, u"\u20AC", "{:1.2f}"))
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
        'orders': 'Get the number of correct orders in both hubs',
        'wrong_orders': 'Get the number of wrong orders in both hubs',
        'bought_items': 'Get the number of items bought in both hubs',
        'bought_money': 'Get the fiscal price of the items bought in both hubs',
        'dev_option': 'This indicates that we are are in dev mode. Delete, please'
    }

    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += "/" + key + " " + u"\u2192" + " "
        help_text += commands[key] + "\n"
    bot.send_message(message.chat.id, help_text)

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

def get_bought_items(db):
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

def get_bought_money(db):
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

def format_result(value, postfix=None, _format="{:1.0f}"):
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

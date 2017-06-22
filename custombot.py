import config
import redis
import json
import telebot
from telebot import types

class CustomBot(telebot.TeleBot):

    def __init__(self, token, threaded=True, skip_pending=False):
        self.__redis_cliented = False
        self.redis_client = None
        self.notification_handlers = []
        super().__init__(token, threaded, skip_pending)

    def create_redis_client(self):
        self.redis_client = redis.StrictRedis(host=config.redis_host, port=config.redis_port,
            db=config.redis_db)

    def send_html_message(self, chat_id, text):
        return super().send_message(chat_id, text, None, None, None, "HTML")

    def reply_markup(self, options):
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        for option in options:
            markup.add(option)

        return markup

    def hide_markup(self):
        markup = types.ReplyKeyboardRemove(selective=False)

        return markup

    def get_updates(self, offset=None, limit=None, timeout=20):
        self.get_notifications(timeout)
        return super().get_updates(offset, limit, timeout)

    def _exec_task(self, task, *args, **kwargs):
        if self.threaded:
            self.worker_pool.put(task, *args, **kwargs)
        else:
            task(*args, **kwargs)

    def _build_handler_dict(self, handler, **filters):
        return {
            'function': handler,
            'filters': filters
        }

    def _test_notification_handler(self, handler, notification):
        for filter, filter_value in handler['filters'].items():
            if filter_value is None:
                continue

            if not self._test_notification_filter(filter, filter_value, notification):
                return False

        return True

    def _test_notification_filter(self, filter, filter_value, notification):
        test_cases = {
            'severity': lambda notif: notif['severity'] in filter_value,
            'func': lambda notif: filter_value(notif)
        }

        return test_cases.get(filter, lambda notif: False)(notification)

    def _notify_notification_handlers(self, handlers, notification):
        for handler in handlers:
            if self._test_notification_handler(handler, notification):
                self._exec_task(handler['function'], notification)
                break

    def notification_handler(self, **kwargs):
        def decorator(handler):
            handler_dict = self._build_handler_dict(handler, **kwargs)
            self.add_notification_handler(handler_dict)

            return handler

        return decorator

    def add_notification_handler(self, handler_dict):
        self.notification_handlers.append(handler_dict)

    def get_notifications(self, timeout=20):
        if not self.__redis_cliented:
            self.create_redis_client()
            self.__redis_cliented = True

        while self.redis_client.llen(config.redis_queue) > 0:
            data = self.redis_client.lpop(config.redis_queue)
            decoded_data = data.decode('utf-8')
            notification = json.loads(decoded_data)
            if ('severity' not in notification):
                notification['severity'] = 'message'

            if ('role' not in notification):
                notification['role'] = 'admin'

            self._notify_notification_handlers(self.notification_handlers, notification)

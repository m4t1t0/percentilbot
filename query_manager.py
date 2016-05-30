import time
import config

class Manager():

    def __init__(self, hubs):
        self.hubs = hubs;

    def get_orders_data(self):
        result = {}

        for hub in self.hubs:
            today_morning = time.strftime("%Y-%m-%d") + ' 00:00:00'
            today_night = time.strftime("%Y-%m-%d") + ' 23:59:59'
            sql = """
                SELECT COUNT(*) AS num, sum(total_paid_real) as money
                FROM ps_orders o
                INNER JOIN PercentilOrder po
                ON o.id_order = po.id_order
                WHERE o.date_add >= '{}'
                AND o.date_add <= '{}'
                AND po.id_order_state IN ({})
                GROUP BY po.clothes_subtype
                ORDER BY clothes_subtype ASC
                """.format(today_morning, today_night, config.valid_order_states)
        
            data = hub['db'].run_query(sql)
            if data == None:
                subtotal = {'num': '-', 'money': '-'}
            else:
                num = data[0]['num'] + data[1]['num'] + data[2]['num']
                money = data[0]['money'] + data[1]['money'] + data[2]['money']
                subtotal = {'num': num, 'money': money}

            result[hub['name']] = {'data': data, 'subtotal': subtotal}

        return result

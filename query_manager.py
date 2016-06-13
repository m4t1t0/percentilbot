import time
import config

class Manager():

    def get_orders_data(self, hub, grouping, time_start, time_end):
        result = {}
        sql = getattr(globals()['Manager'](), 'sql_' + grouping)()
        data = hub['db'].run_query(sql.format(time_start, time_end, config.valid_order_states))

        return self.totalize(data, ['num', 'money'])

    def totalize(self, data, keys):
        total = {}
        for key in keys:
            total[key] = 0

        if data == None:
            for key in keys:
                total[key] = '-'
        else:
            for value in data:
                for key in keys:
                    total[key] += value[key]

        return {'data': data, 'total': total}

    def sql_orders_by_clothes_subtype(self):
        return """
            SELECT po.clothes_subtype AS subtype, 
            COUNT(*) AS num, sum(total_paid_real) as money
            FROM ps_orders o
            INNER JOIN PercentilOrder po
            ON o.id_order = po.id_order
            WHERE o.date_add >= '{}'
            AND o.date_add <= '{}'
            AND po.id_order_state IN ({})
            GROUP BY po.clothes_subtype
            ORDER BY clothes_subtype ASC
            """

    # def get_purchases_data(self):
    #     result = {}

    #     for hub in self.hubs:
    #         #time_start = time.strftime("%Y-%m-%d") + ' 00:00:00'
    #         #time_end = time.strftime("%Y-%m-%d") + ' 23:59:59'
    #         time_start = '2016-06-03 00:00:00'
    #         time_end = '2016-06-03 23:59:59'
    #         sql = """
    #             SELECT IF(pp.id_subproductType IN (1, 2, 3), 'K', 'W') AS subtype, COUNT(*) AS num, SUM(pp.fiscal_price) AS money
    #             FROM PercentilProduct pp
    #             WHERE pp.processedOn >= '{}'
    #             AND pp.processedOn <= '{}'
    #             AND pp.status NOT IN ('Lost', 'Discarded', 'Discarded_Hiper')
    #             GROUP BY subtype
    #             """.format(time_start, time_end)
        
    #         data = hub['db'].run_query(sql)
    #         if data == None:
    #             subtotal = {'num': '-', 'money': '-'}
    #         else:
    #             num = money = 0
    #             for value in data:
    #                 num += value['num']
    #                 money += value['money']

    #             subtotal = {'num': num, 'money': money}

    #         result[hub['name']] = {'data': data, 'subtotal': subtotal}

    #     return result

    # def get_num_wrong_orders(db):
    #     today = time.strftime("%Y-%m-%d") + ' 00:00:00'
    #     try:
    #         db.query("""
    #             SELECT COUNT(*) AS num
    #             FROM ps_orders o
    #             LEFT JOIN PercentilOrder po
    #             ON o.id_order = po.id_order
    #             WHERE o.date_add >= '{}'
    #             AND (po.id_order IS NULL OR po.id_order_state IN ({}))
    #             """.format(today, config.wrong_order_states))
    #         r = db.store_result()
    #         data = r.fetch_row()
    #         return data[0][0]
    #     except:
    #         return '-'

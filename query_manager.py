import time
import collections
import config

class Manager():

    def get_orders_data(self, db, grouping, date_text):
        time_start = str(date_text) + ' 00:00:00'
        time_end = str(date_text) + ' 23:59:59'
        sql = getattr(globals()['Manager'](), 'sql_' + grouping)()
        data = db.run_query(sql.format(time_start, time_end, config.valid_order_states))

        return self.totalize(data, ['num', 'money'])

    def get_orders_available_grouping(self):
        grouping = collections.OrderedDict()
        grouping['by cloth type'] = 'orders_by_clothes_subtype'
        grouping['by site'] = 'orders_by_site'
        grouping['by payment method'] = 'orders_by_payment_method'

        return grouping

    def get_purchases_data(self, db, grouping, date_text):
        time_start = str(date_text) + ' 00:00:00'
        time_end = str(date_text) + ' 23:59:59'
        sql = getattr(globals()['Manager'](), 'sql_' + grouping)()
        data = db.run_query(sql.format(time_start, time_end))

        return self.totalize(data, ['num', 'money'])

    def get_purchases_available_grouping(self):
        grouping = collections.OrderedDict()
        grouping['by cloth type'] = 'purchases_by_cloth_type'
        grouping['by site'] = 'purchases_by_site'

        return grouping

    def get_items_sold_data(self, db, grouping, date_text):
        result = {}
        time_start = str(date_text) + ' 00:00:00'
        time_end = str(date_text) + ' 23:59:59'
        sql = getattr(globals()['Manager'](), 'sql_' + grouping)()
        data = db.run_query(sql.format(time_start, time_end, config.valid_order_states))

        return self.totalize(data, ['num', 'buy_price', 'sell_price'])

    def get_items_sold_available_grouping(self):
        grouping = collections.OrderedDict()
        grouping['by cloth type'] = 'items_sold_by_cloth_type'
        grouping['by site'] = 'items_sold_by_site'

        return grouping

    def get_bags_requested_data(self, db, date_text):
        time_start = str(date_text) + ' 00:00:00'
        time_end = str(date_text) + ' 23:59:59'
        sql = self.sql_bags_requested_by_site()
        data = db.run_query(sql.format(time_start, time_end))

        return self.totalize(data, ['num'])

    def get_bags_in_data(self, db, date_text):
        time_start = str(date_text) + ' 00:00:00'
        time_end = str(date_text) + ' 23:59:59'
        sql = self.sql_bags_in_by_site()
        data = db.run_query(sql.format(time_start, time_end))

        return self.totalize(data, ['num'])

    def get_missing_items_data(self, db, date_text):
        time_start = str(date_text) + ' 00:00:00'
        time_end = str(date_text) + ' 23:59:59'
        sql = self.sql_missing_items()
        data = db.run_query(sql.format(time_start, time_end))

        return data

    def get_new_shoppers_data(self, db, date_text):
        time_start = str(date_text) + ' 00:00:00'
        time_end = str(date_text) + ' 23:59:59'
        sql = self.sql_new_shoppers_by_site()
        data = db.run_query(sql.format(config.new_shopper_order_states, time_start, time_end))

        return self.totalize(data, ['num'])

    def _get_default_grouped_data_format(self):
        return [
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

    def get_orders_grouped_data_format(self):
        return self._get_default_grouped_data_format()

    def get_purchases_grouped_data_format(self):
        return self._get_default_grouped_data_format()

    def get_items_sold_grouped_data_format(self):
        return [
            {
                'name': 'Num',
                'key': 'num',
                'postfix': None,
                'format': '{:1.0f}'
            },
            {
                'name': 'Buy price',
                'key': 'buy_price',
                'postfix': u"\u20AC",
                'format': '{:1.2f}'
            },
            {
                'name': 'Sell price',
                'key': 'sell_price',
                'postfix': u"\u20AC",
                'format': '{:1.2f}'
            }
        ]

    def get_bag_request_grouped_data_format(self):
        return [
            {
                'name': 'Num',
                'key': 'num',
                'postfix': None,
                'format': '{:1.0f}'
            }
        ]

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
            SELECT po.clothes_subtype AS grouping_type, COUNT(*) AS num, sum(total_paid_real) as money
            FROM ps_orders o
            INNER JOIN PercentilOrder po ON o.id_order = po.id_order
            WHERE o.date_add >= '{}'
            AND o.date_add <= '{}'
            AND po.id_order_state IN ({})
            GROUP BY po.clothes_subtype
            ORDER BY clothes_subtype ASC
            """

    def sql_orders_by_site(self):
        return """
            SELECT w.shortName AS grouping_type, COUNT(*) AS num, sum(total_paid_real) as money
            FROM ps_orders o
            INNER JOIN PercentilOrder po ON o.id_order = po.id_order
            INNER JOIN ps_customer c ON c.id_customer = o.id_customer
            INNER JOIN customer_extra_info cei ON cei.id_customer = c.id_customer
            INNER JOIN Websites w on w.id_website = cei.id_site
            WHERE o.date_add >= '{}'
            AND o.date_add <= '{}'
            AND po.id_order_state IN ({})
            GROUP BY cei.id_site
            ORDER BY cei.id_site ASC
            """

    def sql_orders_by_payment_method(self):
        return """
            SELECT IF(pm.shortName IS NULL, 'W', pm.shortName) AS grouping_type, 
            COUNT(*) AS num, sum(total_paid_real) as money
            FROM ps_orders o
            INNER JOIN PercentilOrder po ON o.id_order = po.id_order
            LEFT JOIN PaymentMethods pm ON pm.tagName = o.module
            WHERE o.date_add >= '{}'
            AND o.date_add <= '{}'
            AND po.id_order_state IN ({})
            GROUP BY o.module
            ORDER BY pm.id_paymentMethod ASC
            """

    def sql_purchases_by_cloth_type(self):
        return """
            SELECT IF(pp.id_subproductType IN (1, 2, 3), 'K', 'W') AS grouping_type,
            COUNT(*) AS num, SUM(pp.fiscal_price) AS money
            FROM PercentilProduct pp
            WHERE pp.processedOn >= '{}'
            AND pp.processedOn <= '{}'
            AND pp.status NOT IN ('Lost', 'Discarded', 'Discarded_Hiper')
            GROUP BY grouping_type
            ORDER BY grouping_type ASC
            """

    def sql_purchases_by_site(self):
        return """
            SELECT w.shortName AS grouping_type, COUNT(*) AS num, SUM(pp.fiscal_price) AS money
            FROM PercentilProduct pp
            INNER JOIN bag b ON pp.id_bag = b.id_bag
            INNER JOIN bag_request br ON b.id_bag_request = br.id_bag_request
            INNER JOIN ps_customer c ON c.id_customer = br.id_customer
            INNER JOIN customer_extra_info cei ON c.id_customer = cei.id_customer
            INNER JOIN Websites w on w.id_website = cei.id_site
            WHERE pp.processedOn >= '{}'
            AND pp.processedOn <= '{}'
            AND pp.status NOT IN ('Lost', 'Discarded', 'Discarded_Hiper')
            GROUP BY cei.id_site
            ORDER BY cei.id_site ASC
            """

    def sql_items_sold_by_cloth_type(self):
        return """
            SELECT IF(pp.id_subproductType IN (1, 2, 3), 'K', 'W') AS grouping_type, 
            COUNT(*) AS num, SUM(pp.fiscal_price) AS buy_price,
            SUM(od.product_price) AS sell_price 
            FROM ps_orders o
            INNER JOIN PercentilOrder po ON o.id_order = po.id_order
            INNER JOIN ps_order_detail od ON od.id_order = o.id_order
            INNER JOIN ps_product p ON p.id_product = od.product_id
            INNER JOIN PercentilProduct pp ON p.id_product = pp.id_product
            WHERE o.date_add >= '{}'
            AND o.date_add <= '{}'
            AND po.id_order_state IN ({})
            GROUP BY grouping_type
            ORDER BY grouping_type ASC
            """

    def sql_items_sold_by_site(self):
        return """
            SELECT w.shortName AS grouping_type,
            COUNT(*) AS num, SUM(pp.fiscal_price) AS buy_price,
            SUM(od.product_price) AS sell_price 
            FROM ps_orders o
            INNER JOIN PercentilOrder po ON o.id_order = po.id_order
            INNER JOIN ps_order_detail od ON o.id_order = od.id_order
            INNER JOIN ps_product p ON p.id_product = od.product_id
            INNER JOIN PercentilProduct pp ON p.id_product = pp.id_product
            INNER JOIN ps_customer c ON c.id_customer = o.id_customer
            INNER JOIN customer_extra_info cei ON c.id_customer = cei.id_customer
            INNER JOIN Websites w on w.id_website = cei.id_site
            WHERE o.date_add >= '{}'
            AND o.date_add <= '{}'
            AND po.id_order_state IN ({})
            GROUP BY cei.id_site
            ORDER BY cei.id_site ASC
            """

    def sql_bags_requested_by_site(self):
        return """
            SELECT w.shortName AS grouping_type, COUNT(*) AS num
            FROM bag_request br
            INNER JOIN ps_customer c ON c.id_customer = br.id_customer
            INNER JOIN customer_extra_info cei ON c.id_customer = cei.id_customer
            INNER JOIN Websites w ON w.id_website = cei.id_site
            WHERE br.request_date >= '{}'
            AND br.request_date <= '{}'
            GROUP BY cei.id_site
            ORDER BY cei.id_site ASC
            """

    def sql_bags_in_by_site(self):
        return """
            SELECT w.shortName AS grouping_type, COUNT(*) AS num
            FROM bag b
            INNER JOIN bag_request br ON br.id_bag_request = b.id_bag_request
            INNER JOIN ps_customer c ON c.id_customer = br.id_customer
            INNER JOIN customer_extra_info cei ON c.id_customer = cei.id_customer
            INNER JOIN Websites w ON w.id_website = cei.id_site
            WHERE b.receivedOn >= '{}'
            AND b.receivedOn <= '{}'
            GROUP BY cei.id_site
            ORDER BY cei.id_site ASC
            """

    def sql_missing_items(self):
        return """
            SELECT SUM(IF(plc.status = 'none', 1, 0)) AS 'hold', SUM(IF(plc.status = 'missing', 1, 0)) AS 'missing'
            FROM PickingList pl
            INNER JOIN PickingListContents plc ON pl.id_pickingList = plc.id_pickingList
            WHERE pl.creationDate >= '{}'
            AND pl.creationDate <= '{}'
            """

    def sql_new_shoppers_by_site(self):
        return """
            SELECT w.shortName AS grouping_type, SUM(IF(cn.ncompras = 1, 1, 0)) AS num
            FROM
            (
                SELECT id_customer, COUNT(*) AS ncompras
                FROM ps_orders o
                INNER JOIN PercentilOrder po ON o.id_order = po.id_order
                WHERE po.id_order_state IN ({})
                GROUP BY id_customer
            ) cn, ps_orders o
            INNER JOIN ps_customer c ON o.id_customer=c.id_customer
            INNER JOIN PercentilOrder po ON o.id_order=po.id_order
            INNER JOIN customer_extra_info AS cei ON c.id_customer=cei.id_customer
            INNER JOIN Websites w ON w.id_website = cei.id_site
            WHERE cn.id_customer=o.id_customer
            AND o.date_add >= '{}'
            AND o.date_add <= '{}'
            GROUP BY w.shortName
            """

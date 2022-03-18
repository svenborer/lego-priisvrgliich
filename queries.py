import timeit

from datetime import datetime, timedelta
from random import randint
from collections import Counter

from database import MySQLDatabase

class Queries():
    def __init__(self):
        self.db = MySQLDatabase()
    
    def _select_query(self, query, data=()):
        if self.db.cnx:
            cursor = self.db.cnx.cursor(dictionary=True)
            cursor.execute(query, data)
            result = cursor.fetchall()
            cursor.close()
            records = []
            for row in result:
                records.append(row)
            return records

    def _execute_query(self, query):
        if self.db.cnx:
            cursor = self.db.cnx.cursor()
            cursor.execute(query)
            cursor.close()
            self.db.cnx.commit()

    def get_auction_by_url(self, url):
        query = """
            SELECT
                *
            FROM 
                tbl_auction_scans 
            WHERE
                url = %s
        """
        return self._select_query(query, (url, ))

    def get_latest_scan_ids(self):
        query = "SELECT * FROM tmp_latest_scan_ids"
        return [d['scan_id'] for d in self._select_query(query)]

    def get_all_running_auctions(self):
        query = "SELECT * FROM tbl_auction_scans WHERE end_date > NOW()"
        return self._select_query(query)

    def get_lowest_price_in_history_by_set_number(self, set_number):
        query = """
            SELECT *, MIN(price) AS low_price
            FROM tbl_wanted_history
            WHERE set_number = %s
        """
        return self._select_query(query, (set_number, ))

    def get_all_wanted_sets(self):
        query = """
            SELECT *
            FROM tbl_sets
            WHERE i_want = 1
        """
        return self._select_query(query)

    def get_subscriptions(self):
        query = """
            SELECT
                *
            FROM
                tbl_subscriptions
            WHERE
                notified = 0
        """
        return self._select_query(query)

    def get_subscriptions_theme(self):
        query = """
            SELECT
                *
            FROM
                tbl_subscriptions_theme
            WHERE
                notified = 0
        """
        return self._select_query(query)

    def get_current_prices_for_set(self, set_number='%'):
        query = """
            SELECT
                *,
                (
                    100 -(
                        tbl_provider_scans.price /(tbl_sets.ch_price / 100)
                    )
                ) AS save_in_percentage_lp,
                tbl_provider_scans.id
            FROM
                tbl_provider_scans
            LEFT JOIN
                tbl_sets USING(set_number)
            JOIN
                tmp_latest_scan_ids USING(scan_id)
            WHERE
                set_number LIKE %s
        """
        return self._select_query(query, (set_number, ))

    def get_subscriptions_theme_history(self):
        query = """
            SELECT
                *
            FROM
                tbl_subscriptions_theme_history
            JOIN
                tbl_provider_scans
            ON
                tbl_provider_scans.id = tbl_subscriptions_theme_history.deal_id
            JOIN
                tbl_subscriptions_theme
            ON
                tbl_subscriptions_theme.id = tbl_subscriptions_theme_history.subscriptions_theme_id
        """
        return self._select_query(query)

    def get_buy_now_deals(self, after=datetime.now()+timedelta(hours=-296)):
        query = """
            SELECT
                tbl_sets.subtheme,
                tbl_sets.theme,
                tbl_sets.year,
                tbl_sets.ch_price,
                tbl_auction_scans.url,
                tbl_auction_scans.set_number,
                tbl_auction_scans.product_condition,
                tbl_auction_scans.title,
                tbl_auction_scans.end_date,
                (
                    tbl_auction_scans.buy_now_price + tbl_auction_scans.shipping_price
                ) AS price,
                blp.qty_avg_price,
                (
                    100 -(
                        tbl_auction_scans.buy_now_price + tbl_auction_scans.shipping_price
                    ) /(blp.qty_avg_price / 100)
                ) AS save_in_percentage,
                tbl_auction_scans.scan_date
            FROM
                tbl_auction_scans
            JOIN tbl_sets USING(set_number)
            JOIN tmp_newest_bricklink_prices AS blp
            ON
                tbl_auction_scans.set_number = blp.set_number AND blp.product_condition = tbl_auction_scans.product_condition
            WHERE
                tbl_auction_scans.buy_now_price IS NOT NULL AND
                blp.qty_avg_price > 0 AND
                tbl_auction_scans.has_buy_now = 1 AND
                tbl_auction_scans.end_date > NOW() AND
                tbl_auction_scans.scan_date > %s
            GROUP BY
                tbl_auction_scans.url
            ORDER BY
                save_in_percentage
            DESC
        """
        return self._select_query(query, (after, ))

    def get_auction_deals(self):
        query = """
            SELECT
                tbl_sets.subtheme,
                tbl_sets.theme,
                tbl_sets.year,
                tbl_sets.ch_price,
                tbl_auction_scans.url,
                tbl_auction_scans.set_number,
                tbl_auction_scans.product_condition,
                tbl_auction_scans.title,
                tbl_auction_scans.end_date,
                (
                    tbl_auction_scans.auction_price + tbl_auction_scans.shipping_price
                ) AS price,
                tbl_auction_scans.scan_date
            FROM
                tbl_auction_scans
            JOIN tbl_sets USING(set_number)
            WHERE
                tbl_auction_scans.has_auction = 1 AND
                tbl_auction_scans.end_date < DATE_ADD(NOW(), INTERVAL 12 HOUR) AND
                tbl_auction_scans.end_date > NOW()
        """
        return self._select_query(query)

    def get_bricklink_price_for_set(self, set_number, condition='new', age=999):
        query = """
            SELECT
                *
            FROM
                tbl_bricklink_prices
            WHERE
                set_number = %s AND
                product_condition = %s AND
                DATEDIFF(NOW(), scan_date) < %s
            ORDER BY
                scan_date DESC
            LIMIT 1
            """
        return self._select_query(query, (set_number, condition, age))

    def get_bricklink_pov_price_for_set(self, set_number, condition='new', age=999):
        query = """
            SELECT
                *
            FROM
                tbl_part_out_value
            WHERE
                set_number = %s AND
                DATEDIFF(NOW(), scan_date) < %s
            ORDER BY
                scan_date DESC
            LIMIT 1
            """
        return self._select_query(query, (set_number, age))

    def get_random_sets(self, limit=100):
        query = """
            SELECT
                *
            FROM
                tmp_newest_bricklink_prices
            RIGHT JOIN tbl_sets USING(set_number)
            WHERE
            	(DATEDIFF(NOW(), scan_date) > 10 OR
                scan_date IS NULL) AND set_number != 0
            ORDER BY
                RAND()
            LIMIT %s
        """
        return self._select_query(query, (limit, ))
    
    def get_sets(self, id='%'):
        query = """
            SELECT
                *
            FROM
                tbl_sets
            WHERE
                id = %s
            """
        return self._select_query(query, (id, ))

    def _create_tmp_newest_bricklink_prices(self):
        self._execute_query("DELETE FROM tmp_newest_bricklink_prices")
        query = """
        INSERT INTO tmp_newest_bricklink_prices (id, set_number, product_condition, times_sold, total_qty, min_price, avg_price, qty_avg_price, max_price, scan_date)
            SELECT
                id, set_number, product_condition, times_sold, total_qty, min_price, avg_price, qty_avg_price, max_price, scan_date
            FROM
                tbl_bricklink_prices
            INNER JOIN(
                SELECT
                    set_number,
                    MAX(scan_date) AS scan_date
                FROM
                    tbl_bricklink_prices
                GROUP BY
                    set_number
            ) AS MAX USING(set_number, scan_date)
        """
        self._execute_query(query)

    def _create_tmp_newest_pov_prices(self):
        self._execute_query("DELETE FROM tmp_part_out_value")
        query = """
        INSERT INTO tmp_part_out_value (set_number, last_6m_average, scan_date)
            SELECT
                set_number, last_6m_average, scan_date
            FROM
                tbl_part_out_value
            INNER JOIN(
                SELECT
                    set_number,
                    MAX(scan_date) AS scan_date
                FROM
                    tbl_part_out_value
                GROUP BY
                    set_number
            ) AS MAX USING(set_number, scan_date)
        """
        self._execute_query(query)

    def _create_new_listings_tbl(self):
        self._execute_query("DELETE FROM tmp_new_listings_tmp")
        query = """
        INSERT INTO tmp_new_listings_tmp (id, set_number, title, url, price, currency, provider, availability, scan_date, scan_id)
            SELECT
                id, set_number, title, url, price, currency, provider, availability, scan_date, scan_id
            FROM
                tbl_provider_scans
            INNER JOIN(
                SELECT
                    set_number,
                    MIN(scan_date) AS scan_date
                FROM
                    tbl_provider_scans
                GROUP BY
                    set_number
            ) AS MAX USING(set_number, scan_date)
            WHERE
                scan_date > NOW() - INTERVAL 2 WEEK
            ORDER BY
                scan_date
            DESC
        """
        self._execute_query(query)
        self._execute_query("DELETE FROM tmp_new_listings")
        self._execute_query("INSERT INTO tmp_new_listings SELECT * FROM tmp_new_listings_tmp")


    def _create_tmp_latest_scan_ids(self):
        self._execute_query("DELETE FROM tmp_latest_scan_ids_tmp")
        query = """
        INSERT INTO tmp_latest_scan_ids_tmp (scan_id)
            SELECT
                scan_id
            FROM
                (
                SELECT
                    *
                FROM
                    tbl_provider_scans
                WHERE
                    DATEDIFF(NOW(), scan_date) < 2
                GROUP BY
                    provider, scan_id
                ORDER BY
                    scan_date
                DESC
                    ) AS t
                GROUP BY
                    provider
        """
        self._execute_query(query)
        self._execute_query("DELETE FROM tmp_latest_scan_ids")
        self._execute_query("INSERT INTO tmp_latest_scan_ids (scan_id) SELECT scan_id FROM tmp_latest_scan_ids_tmp")

    def _calc_tmp_provider_tbl(self):
        query = """
            SELECT * FROM `tbl_provider_scans` WHERE DATEDIFF(NOW(), scan_date) < 5 ORDER BY `scan_date` ASC 
        """
        tmp_deals_l7d = self._select_query(query)
        deals = []
        for tmp_deal in self._select_query("SELECT * FROM `tbl_provider_scans` JOIN tmp_latest_scan_ids USING(scan_id)"):
            deal = dict(tmp_deal)
            price_range = [_['price'] for _ in tmp_deals_l7d if _['provider'] == deal['provider'] and _['set_number'] == deal['set_number']]
            print(tmp_deal)
            max_count_price = max(set(price_range), key = price_range.count)
            price_change_l7d = int(tmp_deal['price']-max_count_price)
            # print('{} has a price change of {} CHF.'.format(tmp_deal['set_number'], price_change_l7d))
            deal.update({'price_change_l7d' : price_change_l7d})
            deals.append(deal)
        db = MySQLDatabase()
        self._execute_query("DELETE FROM tmp_deals_tmp")
        for deal in deals:
            payload = {
                'table_name' : 'tmp_deals_tmp',
                'data' : {
                    'set_number' : deal['set_number'],
                    'title' : deal['title'],
                    'url' : deal['url'],
                    'price' : deal['price'],
                    'currency' : deal['currency'],
                    'provider' : deal['provider'],
                    'availability' : deal['availability'],
                    'scan_date' : deal['scan_date'],
                    'scan_id' : deal['scan_id'],
                    'price_change_l7d' : deal['price_change_l7d']
                }
            }
            db._insert_query(payload)
        self._execute_query("DELETE FROM tmp_deals")
        self._execute_query("INSERT INTO tmp_deals SELECT * FROM tmp_deals_tmp")

if __name__=='__main__':
    q = Queries()
    q._calc_tmp_provider_tbl()
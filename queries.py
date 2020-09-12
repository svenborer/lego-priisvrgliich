import timeit

from datetime import datetime, timedelta

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

    def get_random_sets(self, limit=100):
        query = """
            SELECT
                *
            FROM
                tbl_sets
            JOIN tmp_newest_bricklink_prices USING(set_number)
            WHERE
                DATEDIFF(NOW(), scan_date) > 10
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
    
    def _create_tmp_latest_scan_ids(self):
        self._execute_query("DELETE FROM tmp_latest_scan_ids")
        query = """
        INSERT INTO tmp_latest_scan_ids (scan_id)
            SELECT
                scan_id
            FROM (
                SELECT
                    *
                FROM
                    tbl_provider_scans
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

if __name__=='__main__':
    starttime = timeit.default_timer()
    q = Queries()
    q._create_tmp_latest_scan_ids()
    q._create_tmp_newest_bricklink_prices()
    print("Time elapsed :", timeit.default_timer() - starttime)
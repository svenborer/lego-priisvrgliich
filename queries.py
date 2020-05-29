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

    def get_scans_by_date(self, age=14):
        query = """
            SELECT
                COUNT(*) as count, provider, DATE(scan_date) AS date
            FROM
                tbl_provider_scans
            WHERE
                DATEDIFF(NOW(), scan_date) < %s
            GROUP BY
                date, provider
            ORDER BY
                date
        """
        return self._select_query(query, (age, ))

    def get_providers(self):
        query = """
            SELECT
                *
            FROM
                tbl_provider_scans
            GROUP BY
                provider
        """
        return self._select_query(query)

    def get_latest_scan_ids(self):
        query = "SELECT scan_id FROM (SELECT * FROM tbl_provider_scans GROUP BY provider, scan_id ORDER BY scan_date DESC) AS t GROUP BY provider"
        data = self._select_query(query)
        scan_ids = [d['scan_id'] for d in data]
        return scan_ids

    def get_latest_offers(self, set_number):
        scan_ids = self.get_latest_scan_ids()
        query = """
            SELECT
                tbl_provider_scans.provider,
                tbl_provider_scans.url,
                tbl_provider_scans.scan_id,
                tbl_provider_scans.price,
                (
                    100 -(
                        tbl_provider_scans.price
                    ) /(blp.qty_avg_price / 100)
                ) AS save_in_percentage_bl,
                (
                    100 -(
                        tbl_provider_scans.price
                    ) /(tbl_sets.ch_price / 100)
                ) AS save_in_percentage_lp
            FROM
                tbl_provider_scans
            JOIN tbl_sets ON tbl_sets.set_number = tbl_provider_scans.set_number
            JOIN(
                SELECT
                    *
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
            ) AS blp ON blp.set_number = tbl_provider_scans.set_number AND blp.product_condition = 'new'
            WHERE 
                tbl_provider_scans.scan_id IN('{}') AND
                tbl_provider_scans.set_number = %s
            ORDER BY
                save_in_percentage_bl
            DESC
        """
        return self._select_query(query.format("', '".join(scan_ids)), (set_number, ))

    def get_sets_currently_on_market(self):
        scan_ids = self.get_latest_scan_ids()
        query = """
            SELECT
                tbl_sets.name,
                tbl_sets.year,
                tbl_sets.theme,
                tbl_sets.subtheme,
                tbl_sets.pieces,
                tbl_sets.minifigs,
                tbl_sets.ch_price,
                blp.qty_avg_price,
                tbl_provider_scans.set_number,
                blp.qty_avg_price,
                (
                    (
                        blp.qty_avg_price /(tbl_sets.ch_price / 100)
                    ) - 100
                ) AS difference
            FROM
                tbl_provider_scans
            RIGHT JOIN tbl_sets ON tbl_sets.set_number = tbl_provider_scans.set_number
            JOIN(
                SELECT
                    *
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
            ) AS blp ON blp.set_number = tbl_provider_scans.set_number AND blp.product_condition = 'new'
            WHERE
                tbl_provider_scans.scan_id IN('{}')
            GROUP BY
                tbl_provider_scans.set_number
            ORDER BY
                tbl_sets.theme, tbl_sets.year
        """
        return self._select_query(query.format("', '".join(scan_ids)))

    def get_set_information(self, set_number='%'):
        scan_ids = self.get_latest_scan_ids()
        query = """
            SELECT
                tbl_sets.name,
                tbl_sets.year,
                tbl_sets.theme,
                tbl_sets.subtheme,
                tbl_sets.pieces,
                tbl_sets.minifigs,
                tbl_sets.ch_price,
                tbl_provider_scans.set_number,
                blp.qty_avg_price,
                (
                    (
                        blp.qty_avg_price /(tbl_sets.ch_price / 100)
                    ) - 100
                ) AS difference
            FROM
                tbl_provider_scans
            LEFT JOIN tbl_sets ON tbl_sets.set_number = tbl_provider_scans.set_number
            JOIN(
                SELECT
                    *
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
            ) AS blp ON blp.set_number = tbl_provider_scans.set_number AND blp.product_condition = 'new'
            WHERE
                tbl_provider_scans.scan_id IN('{}') AND
                tbl_provider_scans.set_number LIKE %s
            GROUP BY
                tbl_provider_scans.set_number
            ORDER BY
                tbl_provider_scans.set_number
            DESC
        """
        return self._select_query(query.format("', '".join(scan_ids)), (set_number, ))

    def get_all_running_auctions(self):
        query = "SELECT * FROM tbl_auction_scans WHERE end_date > NOW()"
        return self._select_query(query)

    def get_new_listings(self):
        query = """
            SELECT
                *
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
            LEFT JOIN tbl_sets USING(set_number)
            WHERE
                scan_date > NOW() - INTERVAL 4 WEEK
            ORDER BY
                `tbl_provider_scans`.`scan_date`
            DESC
        """
        return self._select_query(query)         

    def get_subscriptions(self):
        query = """
            SELECT
                *,
                IF(price_treshold IS NULL,0,price_treshold) AS price_treshold,
                IF(save_lp_treshold IS NULL,100,save_lp_treshold) AS save_lp_treshold,
                IF(save_bl_treshold IS NULL,100,save_bl_treshold) AS save_bl_treshold
            FROM
                tbl_subscriptions
            WHERE
                notified = 0
        """
        return self._select_query(query)

    def get_current_prices_for_set(self, set_number):
        scan_ids = self.get_latest_scan_ids()
        query = """
            SELECT
                *,
                (
                    100 -(
                        tbl_provider_scans.price /(tbl_sets.ch_price / 100)
                    )
                ) AS save_in_percentage_lp
            FROM
                tbl_provider_scans
            LEFT JOIN
                tbl_sets USING(set_number)
            WHERE
                set_number = %s AND
                scan_id IN ('{}')
        """
        return self._select_query(query.format("', '".join(scan_ids)), (set_number, ))

    def get_provider_deals(self, bl_treshold=0, lp_treshold=40):
        query = "SELECT scan_id FROM (SELECT * FROM tbl_provider_scans GROUP BY provider, scan_id ORDER BY scan_date DESC) AS t GROUP BY provider"
        data = self._select_query(query)
        scan_ids = [d['scan_id'] for d in data]
        query = """
            SELECT
                tbl_sets.name,
                tbl_sets.year,
                tbl_sets.theme,
                tbl_sets.subtheme,
                tbl_sets.ch_price,
                tbl_provider_scans.set_number,
                tbl_provider_scans.scan_date,
                tbl_provider_scans.url,
                tbl_provider_scans.provider,
                tbl_provider_scans.price,
                tbl_provider_scans.availability,
                blp.qty_avg_price,
                (
                    100 -(
                        tbl_provider_scans.price /(blp.qty_avg_price / 100)
                    )
                ) AS save_in_percentage_bl,
                (
                    100 -(
                        tbl_provider_scans.price /(tbl_sets.ch_price / 100)
                    )
                ) AS save_in_percentage_lp
            FROM
                tbl_provider_scans
            JOIN(
                SELECT
                    *
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
            ) AS blp ON blp.set_number = tbl_provider_scans.set_number AND blp.product_condition = 'new'
            LEFT JOIN tbl_sets ON tbl_sets.set_number = tbl_provider_scans.set_number
            WHERE
                blp.qty_avg_price > 0 AND
                tbl_provider_scans.scan_id IN('{}') AND
                tbl_sets.name IS NOT NULL AND 
                (
                    (
                        100 -(
                            tbl_provider_scans.price /(blp.qty_avg_price / 100)
                        )
                    ) > %s OR
                    (
                        100 -(
                            tbl_provider_scans.price /(tbl_sets.ch_price / 100)
                        )
                    ) > %s
                )
            GROUP BY
                tbl_provider_scans.set_number,
                tbl_provider_scans.provider
            ORDER BY
                save_in_percentage_bl
            DESC
        """
        return self._select_query(query.format("', '".join(scan_ids)), (bl_treshold, lp_treshold))
    
    def get_auction_deals(self):
        query = """
            SELECT
                tbl_sets.theme,
                tbl_sets.subtheme,
                tbl_auction_scans.url,
                tbl_auction_scans.set_number,
                tbl_auction_scans.product_condition,
                tbl_auction_scans.title,
                tbl_auction_scans.end_date,
                (
                    tbl_auction_scans.auction_price + tbl_auction_scans.shipping_price
                ) AS price,
                blp.qty_avg_price,
                (
                    100 -(
                        tbl_auction_scans.auction_price + tbl_auction_scans.shipping_price
                    ) /(blp.qty_avg_price / 100)
                ) AS save_in_percentage
            FROM
                tbl_auction_scans
            JOIN tbl_sets USING(set_number)
            JOIN(
                SELECT
                    *
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
            ) AS blp
            ON
                tbl_auction_scans.set_number = blp.set_number AND blp.product_condition = tbl_auction_scans.product_condition
            WHERE
                blp.qty_avg_price > 0 AND
                tbl_auction_scans.has_auction = 1 AND
                tbl_auction_scans.end_date > NOW() AND
                DATEDIFF(tbl_auction_scans.end_date,NOW()) < 1
            ORDER BY
                save_in_percentage
            DESC
        """
        return self._select_query(query)

    def get_buy_now_deals(self, after=datetime.now()+timedelta(hours=-296)):
        query = """
            SELECT
                tbl_sets.subtheme,
                tbl_sets.theme,
                tbl_sets.year,
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
            JOIN(
                SELECT
                    *
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
            ) AS blp
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
            WHERE
                set_number != 0
            ORDER BY
                RAND()
            LIMIT %s
        """
        return self._select_query(query, (limit, ))

    def get_themes(self, theme='%', subtheme='%'):
        query = "SELECT * FROM tbl_sets WHERE theme LIKE %s AND subtheme LIKE %s GROUP BY theme"
        return self._select_query(query, (theme, subtheme))

    def get_subthemes(self, theme='%', subtheme='%'):
        query = "SELECT * FROM tbl_sets WHERE theme LIKE %s AND (subtheme LIKE %s OR subtheme IS NULL) GROUP BY subtheme"
        return self._select_query(query, (theme, subtheme))
    
    def get_sets(self, id='%', set_number='%', theme='%', subtheme='%'):
        query = """
            SELECT
                *
            FROM
                tbl_sets
            WHERE
                id LIKE %s AND
                set_number LIKE %s AND
                theme LIKE %s AND
                subtheme LIKE %s
            """
        return self._select_query(query, (id, set_number, theme, subtheme))

    def get_latest_bricklink_prices(self, set_number='%'):
        query = """
            SELECT
                *
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
            WHERE set_number LIKE %s
        """
        return self._select_query(query, (set_number, ))

    def get_market_statistics_by_theme(self, theme='%'):
        query = """
            SELECT
                tbl_sets.theme,
                tbl_sets.subtheme,
                AVG(tbl_sets.us_price) AS avg_us_price,
                AVG(blp.qty_avg_price) AS qty_avg_price,
                (
                    (
                        AVG(blp.qty_avg_price) /(AVG(tbl_sets.us_price) / 100)
                    ) -100
                ) AS difference_in_percent
            FROM
                tbl_sets
            JOIN(
                SELECT
                    *
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
            ) AS blp
            ON
                tbl_sets.set_number = blp.set_number AND product_condition = 'new'
            WHERE
                tbl_sets.theme LIKE %s AND
                tbl_sets.us_price IS NOT NULL AND
                blp.qty_avg_price > 0
            GROUP BY
                tbl_sets.theme,
                tbl_sets.subtheme
            ORDER BY
                difference_in_percent
            DESC
        """
        return self._select_query(query, (theme, ))

    def get_market_statistics_by_subtheme(self, theme='%', subtheme='%'):
        query = """
            SELECT
                tbl_sets.set_number,
                tbl_sets.theme,
                tbl_sets.subtheme,
                tbl_sets.name,
                tbl_sets.year,
                tbl_sets.us_price,
                blp.qty_avg_price,
                (
                    (
                        blp.qty_avg_price /(tbl_sets.us_price / 100)
                    ) -100
                ) AS difference_in_percent
            FROM
                tbl_sets
            JOIN(
                SELECT
                    *
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
            ) AS blp
            ON
                tbl_sets.set_number = blp.set_number AND product_condition = 'new'
            WHERE
                tbl_sets.theme LIKE %s AND
                tbl_sets.subtheme __TO_REPLACE_HERE__ AND
                tbl_sets.us_price IS NOT NULL AND
                blp.qty_avg_price > 0
            ORDER BY
                difference_in_percent
            DESC
        """
        if subtheme is None:
            return self._select_query(query.replace('__TO_REPLACE_HERE__', 'IS NULL'), (theme, ))
        return self._select_query(query.replace('__TO_REPLACE_HERE__', 'LIKE %s'), (theme, subtheme))

if __name__=='__main__':
    starttime = timeit.default_timer()
    q = Queries()
    data = q._select_query('SELECT * FROM `sergej_lego-priisvrgliich`.tbl_provider_scans WHERE scan_id = "CYMPVKUNMD" AND set_number = "70424"')
    print(data)
    print("The time difference is :", timeit.default_timer() - starttime)
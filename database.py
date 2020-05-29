import logging

import mysql.connector
from mysql.connector import errorcode
from datetime import datetime

from config import _config

class MySQLDatabase():
    def __init__(self):
        self.cnx = None
        try:
            self.cnx = mysql.connector.connect(**_config['mysql'])
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error("[MySQL|CONNECT] Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("[MySQL|CONNECT] Database does not exist")
            else:
                logging.error("[MySQL|CONNECT] {}".format(err))
    
    def _insert_query(self, payload):
        if self.cnx:
            if isinstance(payload['table_name'], str) and isinstance(payload['data'], dict):
                query_template = 'INSERT INTO {} ({}) VALUES ({})'
                insert_values = tuple(payload['data'].values())
                query = query_template.format(payload['table_name'], ', '.join(payload['data'].keys()), ', '.join('%s' for _ in payload['data'].values()))
                try:
                    logging.debug('[MySQL|{}] Keys: {}, Values: {}'.format(payload['table_name'], payload['data'].keys(), payload['data'].values()))
                    cursor = self.cnx.cursor()
                    cursor.execute(query, insert_values)
                    self.cnx.commit()
                    cursor.close()
                    return True
                except Exception as e:
                    logging.error('[MySQL] {}'.format(e))
            return False

    def _update_query(self, payload):
        if self.cnx:
            if isinstance(payload['table_name'], str) and isinstance(payload['data'], dict) and isinstance(payload['condition'], dict):
                query_template = 'UPDATE {} SET {} WHERE {}'
                query_update_str = ', '.join('{} = %s'.format(k) for k in payload['data'].keys())
                query_condition_str = ' AND '.join('{} = %s'.format(k) for k in payload['condition'].keys())
                query = query_template.format(payload['table_name'], query_update_str, query_condition_str)
                query_payload = tuple(payload['data'].values()) + tuple(payload['condition'].values())
                try:
                    logging.debug('[MySQL] {}'.format(payload))
                    cursor = self.cnx.cursor()
                    cursor.execute(query, query_payload)
                    self.cnx.commit()
                    cursor.close()
                    return True
                except Exception as e:
                    logging.error('[MySQL] {}'.format(e))
            return False

    def close(self):
        self.cnx.close()

if __name__ == '__main__':
    db = MySQLDatabase()
    db._update_query({'table_name' : 'tbl_sets', 'data' : {'set_number' : 75000, 'name' : 'SW BS', 'ch_price' : 45.90}, 'condition' : {'id' : 1}})
    db._update_query({'table_name' : 'tbl_auction_scans', 'data' : {'auction_price' : 655}, 'condition' : {'id' : 1}})
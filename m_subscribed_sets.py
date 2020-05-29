from config import _config
from queries import Queries
from database import MySQLDatabase

if __name__ == '__main__':
    q = Queries()
    db = MySQLDatabase()
    for row in q.get_subscriptions():
        entries = q.get_current_prices_for_set(row['set_number'])
        low_prices = [r for r in entries if r['price'] < row['price_treshold'] or r['save_in_percentage_lp'] > row['save_lp_treshold']]
        if low_prices:
            for d in low_prices:
                print('SetNumber: {}'.format(d['set_number']))
                print('URL: {}'.format(d['url']))
                print('Price: {} CHF (Treshold: {})'.format(d['price'], row['price_treshold']))
                print('Save LP: {:.2f}% (Treshold: {}%)'.format(d['save_in_percentage_lp'], row['save_lp_treshold']))
                print('Mail Address: {}'.format(row['email']))
            payload = {
                'table_name' : 'tbl_subscriptions',
                'data' : {
                    'notified' : 1
                },
                'condition' : {
                    'id' : row['id']
                }
            }
            db._update_query(payload)
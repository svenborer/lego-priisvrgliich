from config import _config
from queries import Queries
from database import MySQLDatabase
from send_mail import send_mail

q = Queries()
db = MySQLDatabase()

for row in q.get_all_wanted_sets():
    entries = q.get_current_prices_for_set(row['set_number'])
    low_price = q.get_lowest_price_in_history_by_set_number(row['set_number'])
    price_to_beat = 9999999 if low_price[0]['low_price'] is None else low_price[0]['low_price']
    low_prices = [r for r in entries if r['price'] < price_to_beat]
    if low_prices:
        for d in low_prices:
            mail_body = "Set: https://svenborer.ch/lego-priisvrgliich/set/{} {}\nThema: {}/{}\nStei/Minifigure: {}/{}\nPriis: {} CHF\nUVP: {} CHF\nRabatt: {}%\nAhbieter: {}\nURL: {}"
            body = mail_body.format(d['set_number'], d['name'], d['theme'], d['subtheme'], d['pieces'], d['minifigs'], d['price'], d['ch_price'], round(d['save_in_percentage_lp'], 1), d['provider'], d['url'])
            subject = '[L-PVG-P-S] {}|{}'.format(d['set_number'], d['name'])
            to = 'borer.sven@gmail.com'
            send_mail(to, subject, body)
            payload = {
                'table_name' : 'tbl_wanted_history',
                'data' : {
                    'set_number' : d['set_number'],
                    'price' : d['price']
                }
            }
            db._insert_query(payload)
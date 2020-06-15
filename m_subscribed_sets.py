from config import _config
from queries import Queries
from database import MySQLDatabase
from send_mail import send_mail

q = Queries()
db = MySQLDatabase()

for row in q.get_subscriptions():
    entries = q.get_current_prices_for_set(row['set_number'])
    low_prices = [r for r in entries if r['price'] < row['price_treshold']]
    if low_prices:
        for d in low_prices:
            mail_body = """
Set: {} {}
Thema: {}/{}
Stei/Minifigure: {}/{}
Priis: {} CHF
UVP: {} CHF
Treshold: {} CHF
Rabatt: {}%
Ahbieter: {}
URL: {}
            """
            body = mail_body.format(d['set_number'], d['name'], d['theme'], d['subtheme'], d['pieces'], d['minifigs'], d['price'], d['ch_price'], row['price_treshold'], round(d['save_in_percentage_lp'], 1), d['provider'], d['url'])
            subject = 'LEGO-Priisvrgliich|Alarm'
            to = row['email']
            send_mail(to, subject, body)
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
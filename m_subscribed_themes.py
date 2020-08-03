from config import _config
from queries import Queries
from database import MySQLDatabase
from send_mail import send_mail

q = Queries()
db = MySQLDatabase()

all_sets = q.get_current_prices_for_set()
subscription_history = q.get_subscriptions_theme_history()

for row in q.get_subscriptions_theme():
    low_prices = [_ for _ in all_sets if _['theme'] == row['theme'] and _['save_in_percentage_lp'] and _['save_in_percentage_lp'] >= row['save_treshold']]
    low_prices_sorted = reversed(sorted(low_prices, key=lambda k: k['save_in_percentage_lp']))
    if low_prices_sorted:
        for d in low_prices_sorted:
            sent = [h for h in subscription_history if row['id'] == h['subscriptions_theme_id'] and d['url'] == h['url'] and d['price'] >= h['price']]
            if not sent:
                mail_body = """
Set: {} {}
Thema: {}/{}
Stei/Minifigure: {}/{}
Priis: {} CHF
UVP: {} CHF
Rabatt: {}%
Ahbieter: {}
URL: {}
                """
                body = mail_body.format(d['set_number'], d['name'], d['theme'], d['subtheme'], d['pieces'], d['minifigs'], d['price'], d['ch_price'], round(d['save_in_percentage_lp'], 1), d['provider'], d['url'])
                subject = '[LEGO-PVG-P-T] {}|{}'.format(d['set_number'], d['name'])
                to = row['email']
                send_mail(to, subject, body)
                payload = {
                    'table_name' : 'tbl_subscriptions_theme_history',
                    'data' : {
                        'deal_id' : d['id'],
                        'subscriptions_theme_id' : row['id']
                    }
                }
                db._insert_query(payload)
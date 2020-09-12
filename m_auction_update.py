import logging
from datetime import datetime

from auction import Ricardo
from queries import Queries
from send_mail import send_mail

logging.basicConfig(filename='logs/{}_auction_update.log'.format(datetime.now().strftime('%Y%m%d')), filemode='a', format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

try:
    r = Ricardo()
    r.init_update_scan()
except Exception as e:
    logging.error("[RICARDO] Problems scanning, Err: {} ...".format(e))

q = Queries()
auction_deals = q.get_auction_deals()
active_subscriptions = q.get_subscriptions()

mail_body = "Titel: {}\nSet: https://svenborer.ch/lego-priisvrgliich/set/{} {}\nThema: {}/{}\nCondition: {}\nURL: {}\nPriis: {} CHF\nTreshold: {} CHF\nUVP: {} CHF\nBL: {} CHF / {}%\nAendet am: {}"

if auction_deals:
    for d in auction_deals:
        subscriptions = [_ for _ in active_subscriptions if _['set_number'] == d['set_number'] and d['product_condition'] == 'new' and d['price'] < _['price_treshold']]
        for s in subscriptions:
            body = mail_body.format(d['title'], d['set_number'], d['name'], d['theme'], d['subtheme'], d['product_condition'], d['url'], round(d['price'], 2), s['price_treshold'], d['ch_price'], 'N/A', 'N/A', d['end_date'])
            subject = '[L-PVG-A-A] {}|{}'.format(d['set_number'], d['title'])
            to = s['email']
            send_mail(to, subject, body)
import logging
from datetime import datetime

from config import _config
from queries import Queries
from auction import Ricardo
from send_mail import send_mail

wl_set_number = _config['scanner']['wishlist']['set_number']
wl_theme = _config['scanner']['wishlist']['theme']
wl_subtheme = _config['scanner']['wishlist']['subtheme']

logging.basicConfig(filename='logs/{}_auction.log'.format(datetime.now().strftime('%Y%m%d')), filemode='a', format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

timestamp = datetime.now()
q = Queries()

try:
    r = Ricardo()
    r.init_base_scan()
except Exception as e:
    logging.error("[RICARDO] Problems scanning, Err: {} ...".format(e))

mail_body = "Titel: {}\nSet: {}\nThema: {}/{}\nCondition: {}\nURL: {}\nPriis: {} CHF\nTreshold: {} CHF\nUVP: {} CHF\nBL: {} CHF / {}%\nAendet am: {}"

buy_now_deals = q.get_buy_now_deals(after=timestamp)
buy_now_deals_filtered = [_ for _ in buy_now_deals if (_['set_number'] in wl_set_number or _['subtheme'] in wl_subtheme or _['theme'] in wl_theme) and _['save_in_percentage'] > -10]
active_subscriptions = q.get_subscriptions()

if buy_now_deals_filtered:
    for d in buy_now_deals_filtered:
        body = mail_body.format(d['title'], d['set_number'], d['theme'], d['subtheme'], d['product_condition'], d['url'], d['price'], 'N/A', d['ch_price'], round(d['qty_avg_price'], 2), round(d['save_in_percentage'], 1), d['end_date'])
        subject = '[L-PVG-A-SK] {}|{}'.format(d['set_number'], d['title'])
        to = 'borer.sven@gmail.com'
        send_mail(to, subject, body)

if buy_now_deals:
    for d in buy_now_deals:
        subscriptions = [_ for _ in active_subscriptions if _['set_number'] == d['set_number'] and d['product_condition'] == 'new' and d['price'] < _['price_treshold']]
        for s in subscriptions:
            body = mail_body.format(d['title'], d['set_number'], d['theme'], d['subtheme'], d['product_condition'], d['url'], round(d['price'], 2), s['price_treshold'], d['ch_price'], round(d['qty_avg_price'], 2), round(d['save_in_percentage'], 1), d['end_date'])
            subject = '[L-PVG-A-SK] {}|{}'.format(d['set_number'], d['title'])
            to = s['email']
            send_mail(to, subject, body)
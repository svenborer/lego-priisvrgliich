import logging
from datetime import datetime

from config import _config
from queries import Queries
from auction import Ricardo
from send_mail import send_email

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

buy_now_deals = q.get_buy_now_deals(after=timestamp)
buy_now_deals = [d for d in buy_now_deals if (str(d['set_number']) in wl_set_number or d['subtheme'] in wl_subtheme or d['theme'] in wl_theme) and d['save_in_percentage'] > -10]

# if buy_now_deals:
#     body = ''
#     for d in buy_now_deals:
#         body += 'Title: {}\n'.format(d['title'])
#         body += 'Theme: {}\n'.format(d['theme'])
#         body += 'Subtheme: {}\n'.format(d['subtheme'])
#         body += 'SetNumber: {}\n'.format(d['set_number'])
#         body += 'Condition: {}\n'.format(d['product_condition'])
#         body += 'URL: {}\n'.format(d['url'])
#         body += 'Price: {} / {} / {}%\n'.format(d['price'], d['qty_avg_price'], d['save_in_percentage'])
#         body += 'Ends in: {}\n\n'.format(d['end_date'])
#     send_email('Ricardo BuyNow Deals', body)

if buy_now_deals:
    for d in buy_now_deals:
        print('Title: {}'.format(d['title']))
        print('Theme: {}/{}'.format(d['theme'], d['subtheme']))
        print('SetNumber: {}'.format(d['set_number']))
        print('Condition: {}'.format(d['product_condition']))
        print('URL: {}'.format(d['url']))
        print('Price: {} / {} / {} %'.format(d['price'], d['qty_avg_price'], d['save_in_percentage']))
        print('Ends in: {}\n'.format(d['end_date']))
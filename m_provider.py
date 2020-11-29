import logging
from datetime import datetime

from provider import Galaxus, LEGO, Manor, MeinSpielzeug, Smyth, Techmania, Alternate, Migros, Velis
from queries import Queries
from send_mail import send_mail
from config import _config

logging.basicConfig(filename='logs/{}_provider.log'.format(datetime.now().strftime('%Y%m%d')), filemode='a', format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

def send_error_mail(provider, errormsg):
    body = "Seht us als waer dr Scanner fuer {} dunde: {} ...".format(provider, errormsg)
    subject = '[L-PVG] {}|Scanning Error ...'.format(provider)
    to = _config['notification']['email']
    send_mail(to, subject, body)

try:
    s = Smyth()
    s.init_scan()
except Exception as e:
    logging.error("[SMYTH] Problems scanning, Err: {} ...".format(e))
    send_error_mail('SMYTH', e)

try:
    g = Galaxus()
    g.init_scan()
except Exception as e:
    logging.error("[GALAXUS] Problems scanning, Err: {} ...".format(e))
    send_error_mail('GALAXUS', e)

try:
    l = LEGO()
    l.init_scan()
except Exception as e:
    logging.error("[LEGO] Problems scanning, Err: {} ...".format(e))
    send_error_mail('LEGO', e)

try:
    ms = MeinSpielzeug()
    ms.init_scan()
except Exception as e:
    logging.error("[MEINSPIELZEUG] Problems scanning, Err: {} ...".format(e))
    send_error_mail('MEINSPIELZEUG', e)

try:
    m = Migros()
    m.init_scan()
except Exception as e:
    logging.error("[MIGROS] Problems scanning, Err: {} ...".format(e))
    send_error_mail('MIGROS', e)

try:
    a = Alternate()
    a.init_scan()
except Exception as e:
    logging.error("[ALTERNATE] Problems scanning, Err: {} ...".format(e))
    send_error_mail('ALTERNATE', e)

try:
    t = Techmania()
    t.init_scan()
except Exception as e:
    logging.error("[TECHMANIA] Problems scanning, Err: {} ...".format(e))
    send_error_mail('TECHMANIA', e)

try:
    ma = Manor()
    ma.init_scan()
except Exception as e:
    logging.error("[MANOR] Problems scanning, Err: {} ...".format(e))
    send_error_mail('MANOR', e)

try:
    v = Velis()
    v.init_scan()
except Exception as e:
    logging.error("[VELIS] Problems scanning, Err: {} ...".format(e))
    send_error_mail('VELIS', e)

q = Queries()
q._create_tmp_latest_scan_ids()
q._create_tmp_newest_bricklink_prices()
q._calc_tmp_provider_tbl()
q._create_new_listings_tbl()
import logging
from datetime import datetime

from provider import Galaxus, LEGO, Manor, MeinSpielzeug, Techmania, Alternate, Migros, Velis
from queries import Queries

logging.basicConfig(filename='logs/{}_provider.log'.format(datetime.now().strftime('%Y%m%d')), filemode='a', format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

try:
    g = Galaxus()
    g.init_scan()
except Exception as e:
    logging.error("[GALAXUS] Problems scanning, Err: {} ...".format(e))

try:
    l = LEGO()
    l.init_scan()
except Exception as e:
    logging.error("[LEGO] Problems scanning, Err: {} ...".format(e))

try:
    ms = MeinSpielzeug()
    ms.init_scan()
except Exception as e:
    logging.error("[MEINSPIELZEUG] Problems scanning, Err: {} ...".format(e))

try:
    m = Migros()
    m.init_scan()
except Exception as e:
    logging.error("[MIGROS] Problems scanning, Err: {} ...".format(e))

try:
    a = Alternate()
    a.init_scan()
except Exception as e:
    logging.error("[ALTERNATE] Problems scanning, Err: {} ...".format(e))

try:
    t = Techmania()
    t.init_scan()
except Exception as e:
    logging.error("[TECHMANIA] Problems scanning, Err: {} ...".format(e))

try:
    ma = Manor()
    ma.init_scan()
except Exception as e:
    logging.error("[MANOR] Problems scanning, Err: {} ...".format(e))

try:
    v = Velis()
    v.init_scan()
except Exception as e:
    logging.error("[VELIS] Problems scanning, Err: {} ...".format(e))

q = Queries()
q._create_tmp_latest_scan_ids()
q._create_tmp_newest_bricklink_prices()
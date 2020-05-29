import logging
from datetime import datetime

from auction import Ricardo

logging.basicConfig(filename='logs/{}_auction_update.log'.format(datetime.now().strftime('%Y%m%d')), filemode='a', format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

try:
    r = Ricardo()
    r.init_update_scan()
except Exception as e:
    logging.error("[RICARDO] Problems scanning, Err: {} ...".format(e))
import logging
from datetime import datetime

from queries import Queries
from bricklink import Bricklink

logging.basicConfig(filename=datetime.now().strftime('logs/%Y%m%d_bricklink.log'), filemode='a', format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.DEBUG)

q = Queries()

sets = q.get_random_sets(limit=5)

for s in sets:
    Bricklink(s['set_number'])
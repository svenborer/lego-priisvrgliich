import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup

from scanner import ProductScanner
from database import MySQLDatabase

logging.basicConfig(filename='logs/{}_eol_sets.log'.format(datetime.now().strftime('%Y%m%d')), filemode='a', format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

def _get_set_numbers_from_string(string):
    set_numbers = re.findall(r'([0-9]{7}|[0-9]{4,5})', string)
    set_numbers = list(dict.fromkeys(set_numbers))
    return set_numbers

db = MySQLDatabase()
ps = ProductScanner()

set_number = 0

eol_url = 'https://www.stonewars.de/news/lego-eol-end-of-life-2021/'

soup = ps._get_soup(eol_url, headers={})
eol_sets_raw = [_get_set_numbers_from_string(_.text) for _ in soup.find_all('td', {'class' : 'column-2'})]
eol_sets = [item for sublist in eol_sets_raw for item in sublist]

for set_number in eol_sets:
    logging.info("[EOL] {} has been defined as end of life ...".format(set_number))
    update_data = {
        'table_name' : 'tbl_sets',
        'data' : {
            'is_eol' : True
        },
        'condition' : {
            'set_number' : set_number
        }
    }
    db._update_query(update_data)
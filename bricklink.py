import logging
import requests
import re

from queries import Queries
from database import MySQLDatabase
from datetime import datetime
from bs4 import BeautifulSoup

class Bricklink():
    def __init__(self, set_number, condition='new'):
        self._url = 'http://www.bricklink.com/catalogPG.asp?S={}-1&ColorID=0'.format(set_number)
        self._headers = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
        self.condition = condition
        self.prices = {}
        self.set_number = set_number
        self.scan_date = datetime.now()
        self.exchange_rates = {}
        self.toCurrency = 'CHF'
        self.result = {}
        self.db = MySQLDatabase()
        self.q = Queries()
        self._parse_prices()

    def _get_soup(self):
        while True:
            try:
                logging.debug("[BLP|{}] Requesting prices ...".format(self.set_number))
                r = requests.get("http://www.bricklink.com/catalogPG.asp?S={}-1&viewExclude=Y&ColorID=0".format(self.set_number),
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0"
                    }
                )
                soup = BeautifulSoup(r.content, "html.parser")
                return soup
            except Exception as e:
                logging.error("[BLP|{}] {} ...".format(self.set_number, e))
                return False

    def _parse_prices(self):
        if not self.in_database:
            logging.debug("[BLP|{}] Not found in database ...".format(self.set_number))
            if self.is_valid:
                logging.debug("[BLP|{}] Is valid, parsing prices ...".format(self.set_number))
                try:
                    price_table = self._soup.find('tr', {'bgcolor' : '#C0C0C0'}).find_all('td', {'valign' : 'TOP'})
                    if len(price_table) == 4:
                        self.prices['new'] = self._prices(price_table[0])
                        self.prices['used'] = self._prices(price_table[1])
                        self._deploy_to_database()
                        self.result['status'] = 'success'
                        self.result['source'] = 'bricklink'
                        self.result['data'] = self.prices
                except Exception as e:
                    logging.warning('[BLP|{}] {}'.format(self.set_number, e))
                    self.result['status'] = 'error'
                    self.result['msg'] = e
        else:
            logging.debug("[BLP|{}] Found in database ...".format(self.set_number))
            for c in ['new', 'used']:
                data = self.q.get_bricklink_price_for_set(self.set_number, c, age=7)
                p = [p for p in data]
                self.prices[c] = p[0]
            self.result['status'] = 'success'
            self.result['source'] = 'database'
            self.result['data'] = self.prices

    def _prices(self, table):
        prices = {}
        prices['times_sold'] = -1
        prices['total_qty'] = -1
        prices['min_price'] = -1
        prices['avg_price'] = -1
        prices['qty_avg_price'] = -1
        prices['max_price'] = -1
        try:
            prices['times_sold'] = table.find('td', text = re.compile('^Times Sold:.*')).find_next('td').text
            prices['total_qty'] = table.find('td', text = re.compile('^Total Qty:.*')).find_next('td').text
            prices['min_price'] = self._clean_and_convert_price(table.find('td', text = re.compile('^Min Price:')).find_next('td').text)
            prices['avg_price'] = self._clean_and_convert_price(table.find('td', text = re.compile('^Avg Price:')).find_next('td').text)
            prices['qty_avg_price'] = self._clean_and_convert_price(table.find('td', text = re.compile('^Qty Avg Price:')).find_next('td').text)
            prices['max_price'] = self._clean_and_convert_price(table.find('td', text = re.compile('^Max Price:')).find_next('td').text)
        except Exception as e:
            logging.debug("[BLP|PARSE_PRICE_TABLES|{}] {}".format(self.set_number, e))
            return prices
        return prices
    
    def _deploy_to_database(self):
        for c in ['new', 'used']:
            # set_number, product_condition, times_sold, total_qty, min_price, avg_price, qty_avg_price, max_price, scan_date
            payload = {
                'table_name' : 'tbl_bricklink_prices',
                'data' : {
                    'set_number' : self.set_number, 
                    'product_condition' : c, 
                    'times_sold' : self.prices[c]['times_sold'], 
                    'total_qty' : self.prices[c]['total_qty'], 
                    'min_price' : self.prices[c]['min_price'], 
                    'avg_price' : self.prices[c]['avg_price'], 
                    'qty_avg_price' : self.prices[c]['qty_avg_price'], 
                    'max_price' : self.prices[c]['max_price'], 
                    'scan_date' : self.scan_date
                }
            }
            self.db._insert_query(payload)

    def _clean_and_convert_price(self, price):
        currency = ''.join(re.findall(r'[A-Z]{3}', price))
        # exchangeRate = self._get_currency_exchange_rate(baseCurrency=currency)
        price = float(''.join(re.findall(r'[0-9,.]', price)).replace(',', ''))
        price = round(price*1.1, 2)
        return price
    
    # TWD not yet supported
    def _get_currency_exchange_rate(self, baseCurrency):
        if baseCurrency == 'TWD':
            logging.debug("[BLP|_GET_CURRENCY_EXCHANGE_RATE] Returning hardcoded TWD rate 0.031 ...")
            return 0.031
        if baseCurrency in self.exchange_rates:
            return self.exchange_rates[baseCurrency]
        else:
            url = "https://api.exchangeratesapi.io/latest?base={}"
            url = url.format(baseCurrency)
            r = requests.get(url, headers=self._headers)
            r_json = r.json()
            rate = r_json['rates'][self.toCurrency]
            self.exchange_rates[baseCurrency] = rate
            logging.debug("[BLP|_GET_CURRENCY_EXCHANGE_RATE] {} has rate {} ...".format(baseCurrency, self.exchange_rates[baseCurrency]))
            return rate

    @property
    def in_database(self):
        for c in ['new', 'used']:
            data = self.q.get_bricklink_price_for_set(self.set_number, c, age=3)
            data = [d for d in data]
            if not data:
                return False
        return True

    @property
    def is_valid(self):
        self._soup = self._get_soup()
        body = self._soup.find('body').text
        if 'No Item(s) were found.  Please try again!' in body:
            self.result['status'] = 'error'
            self.result['msg'] = 'NoItemsFound'
            logging.debug("[BLP|{}] {} ...".format(self.set_number, self.result['msg']))
            return False
        if 'Quota Exceeded' in body:
            self.result['status'] = 'error'
            self.result['msg'] = 'QuotaExceeded'
            logging.debug("[BLP|{}] {} ...".format(self.set_number, self.result['msg']))
            return False
        if 'HTTP Error 404' in body:
            self.result['status'] = 'error'
            self.result['msg'] = 'HTTP404'
            logging.debug("[BLP|{}] {} ...".format(self.set_number, self.result['msg']))
            return False
        if 'System Unavailable' in body:
            self.result['status'] = 'error'
            self.result['msg'] = 'SystemUnavailable'
            logging.debug("[BLP|{}] {} ...".format(self.set_number, self.result['msg']))
            return False
        if 'Qty Avg Price' not in body and 'Times Sold' not in body:
            self.result['status'] = 'error'
            self.result['msg'] = 'NoPriceChartAvailable'
            logging.debug("[BLP|{}] {} ...".format(self.set_number, self.result['msg']))
            return False
        logging.debug("[BLP|{}] Is a valid product ...".format(self.set_number))
        return True

if __name__=='__main__':
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.DEBUG)
    for set_number in ['7781']:
        bl = Bricklink(set_number)
        print(bl.result)
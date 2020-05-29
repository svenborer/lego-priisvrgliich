import random
import string
import logging
import requests
import re

from bs4 import BeautifulSoup
from datetime import datetime

from product import ProviderProduct, AuctionProduct

class BaseScanner():
    def __init__(self):
        self.start_time = datetime.now()
        self.products = []
        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}

    def _get_soup(self, url, headers):
        total_retries = 5
        for i in range(0, total_retries):
            try:
                r = requests.get(url=url, headers=headers, timeout=20)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.content, "html.parser")
                    return soup
            except Exception as e:
                logging.warning("Problems requesting {}. Retry ({}/{}); Err: {} ...".format(url, i, total_retries, e))
        logging.error("Requesting {} failed ...".format(url))
        return

    def _get_json(self, url, headers, data={}, request_type='post'):
        total_retries = 5
        for i in range(0, total_retries):
            try:
                if request_type == 'post':
                    r = requests.post(url=url, headers=headers, data=data, timeout=20)
                else:
                    r = requests.get(url=url, headers=headers, data=data, timeout=20)
                if r.status_code == 200:
                    return r.json()
            except Exception as e:
                logging.warning("Problems requesting {}. Retry ({}/{}); Err: {} ...".format(url, i, total_retries, e))
        logging.error("Requesting {} failed ...".format(url))
        return

    def _get_set_numbers_from_string(self, string):
        set_numbers = re.findall(r'([0-9]{7}|[0-9]{4,5})', string)
        set_numbers = list(dict.fromkeys(set_numbers))
        return set_numbers

class ProductScanner(BaseScanner):
    def __init__(self):
        BaseScanner.__init__(self)
        self.scan_id = self._generate_scan_id()
        self.p = ProviderProduct()

    def _generate_scan_id(self):
        return ''.join(random.choice(string.ascii_uppercase) for i in range(10))

class AuctionScanner(BaseScanner):
    def __init__(self):
        BaseScanner.__init__(self)
        self.p = AuctionProduct()
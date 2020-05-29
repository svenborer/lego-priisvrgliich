import re
import validators
import logging

from datetime import datetime

from database import MySQLDatabase
from config import _config

class ProviderProduct():
    def __init__(self):
        self.products = []

    def add_product(self, set_number, title, price, currency, url, availability, provider, scan_id):
        product = {
            'table_name' : 'tbl_provider_scans',
            'data' : {
                'set_number' : set_number,
                'title' : title,
                'url' : url,
                'price' : price,
                'currency' : currency,
                'provider' : provider,
                'availability' : availability,
                'scan_date' : datetime.now(),
                'scan_id' : scan_id
            }
        }
        if self._is_product_valid(product['data']):
            self.products.append(product)
            logging.debug('[ADD] {}'.format(product))
            return product
        return False

    def get_products(self):
        return self.products
    
    def get_product_count(self):
        return len(self.products)

    def deploy_to_database(self):
        db = MySQLDatabase()
        for product in self.products:
            logging.debug('[DEPLOY] {}'.format(product))
            db._insert_query(product)
        db.close()

    def _is_product_valid(self, product):
        if re.match(r'([0-9]{7}|[0-9]{4,5})', str(product['set_number'])) and \
            isinstance(product['title'], str) and \
            isinstance(float(product['price']), float) and \
            isinstance(product['currency'], str) and \
            isinstance(product['provider'], str) and \
            isinstance(product['scan_id'], str) and \
            validators.url(product['url']) and \
            product['set_number'] not in _config['scanner']['blacklist']:
            logging.debug('[VALID] {}'.format(product))
            return True
        logging.debug('[INVALID] {}'.format(product))
        return False

class AuctionProduct():
    def __init__(self):
        self.products = []
        self.updates = []

    def add_product(self, set_number, title, product_condition, url, has_auction, auction_price, has_buy_now, buy_now_price, shipping_price, bids_count, end_date):
        product = {
            'table_name' : 'tbl_auction_scans',
            'data' : {
                'set_number' : set_number,
                'title' : title,
                'product_condition' : product_condition,
                'url' : url,
                'has_auction' : has_auction,
                'auction_price' : auction_price,
                'has_buy_now' : has_buy_now,
                'buy_now_price' : buy_now_price,
                'shipping_price' : shipping_price,
                'bids_count' : bids_count,
                'end_date' : end_date,
                'scan_date' : datetime.now()
            }
        }
        if self._is_product_valid(product):
            self.products.append(product)
            logging.debug('[ADD] {}'.format(product))
            return product
        return False

    def add_update(self, id, auction_price, buy_now_price, bids_count):
        payload = {
            'table_name' : 'tbl_auction_scans', 
            'data' : {
                'auction_price' : auction_price,
                'buy_now_price' : buy_now_price,
                'bids_count' : bids_count
            }, 
            'condition' : {
                'id' : id
            }
        }
        if self._is_update_valid(payload) and payload not in self.updates:
            self.updates.append(payload)

    def get_products(self):
        return self.products
    
    def get_product_count(self):
        return len(self.products)

    def deploy_to_database(self):
        db = MySQLDatabase()
        for product in self.products:
            db._insert_query(product)
        for update in self.updates:
            db._update_query(update)
        db.close()

    def _is_product_valid(self, product):
        return True

    def _is_update_valid(self, update):
        return True

if __name__ == '__main__':
    p = ProviderProduct()
    p.add_product(75222, 'Cloud Fuck', 499.90, 'CHF', 'https://www.galaxus.ch/0981726519-cloud-fuck', None, 'Galaxus', 'HJKLOIUZTR')
    p.add_product(75192, 'Millenium Falcon', 949, 'CHF', 'https://www.galaxus.ch/9811234519-millenium-falcon', None, 'Galaxus', 'HJKLOIUZTR')
    p.add_product(70424, 'Hidden Side Train', 54.9, 'CHF', 'https://www.galaxus.ch/1982726322-hidden-train', None, 'Galaxus', 'HJKLOIUZTR')
    print(p.get_products())
    p.deploy_to_database()
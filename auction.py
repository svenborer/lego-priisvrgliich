import logging
import json
import re

from datetime import datetime

from product import AuctionProduct
from scanner import AuctionScanner
from queries import Queries
from config import _config

class Ricardo(AuctionScanner):
    def __init__(self):
        AuctionScanner.__init__(self)
        self.q = Queries()
        self.base_url = 'https://www.ricardo.ch/de/c/lego-41815/?page={}&sort=newest'

    def init_base_scan(self):
        logging.info('[RICARDO] Initialize base scan ...')
        for page in range(1, 3):
            url = self.base_url.format(page)
            logging.info("[RICARDO] Scanning {} ...".format(url))
            json = self._get_product_json(url)
            products = json['initialState']['srp']['results']
            logging.info('[RICARDO] Found {} products to scan ...'.format(len(products)))
            [self.products.append(product) for product in products]
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        self.p.deploy_to_database()

    def init_update_scan(self):
        logging.info('[RICARDO] Initialize update scan ...')
        all_auctions = self.q.get_all_running_auctions()
        total_pages = self._get_total_pages()
        for page in range(1, total_pages):
            url = self.base_url.format(page)
            logging.info("[RICARDO] Scanning {} ...".format(url))
            json = self._get_product_json(url)
            products = json['initialState']['srp']['results']
            logging.info("[RICARDO] Found {} potential products to update ...".format(len(products)))
            for product in products:
                product_url = "{}{}".format('https://www.ricardo.ch', product['url'])
                [self.p.add_update(auction['id'], product['bidPrice'], product['buyNowPrice'], product['bidsCount']) for auction in all_auctions if auction['url'] == product_url and (auction['auction_price'] != product['bidPrice'] or auction['buy_now_price'] != product['buyNowPrice'] or auction['bids_count'] != product['bidsCount'])]
        self.p.deploy_to_database()
                
    def _scan_product(self, product):
        url = "{}{}".format('https://www.ricardo.ch', product['url'])
        if not self.q.get_auction_by_url(url):
            logging.info("[RICARDO] Scanning {} ...".format(url))
            title = product['title']
            soup = self._get_soup(url, self.headers)
            description = soup.find('div', {'name' : 'description'}).text
            set_numbers = self._get_set_numbers_from_string(title) + self._get_set_numbers_from_string(description)
            set_numbers = list(dict.fromkeys(set_numbers))
            condition = 'new' if product['conditionKey'] == 'new' else 'used'
            has_auction = product['hasAuction']
            has_buy_now = product['hasBuyNow']
            auction_price = product['bidPrice']
            buy_now_price = product['buyNowPrice']
            shipping_price = product['shipping']['cost']
            bids_count = product['bidsCount']
            end_date = datetime.strptime(product['endDate'][:-4], '%Y-%m-%dT%H:%M:%S') if len(product['endDate']) == 23 else datetime.strptime(product['endDate'], '%Y-%m-%dT%H:%M:%SZ')
            for set_number in set_numbers:
                self.p.add_product(set_number, title, condition, url, has_auction, auction_price, has_buy_now, buy_now_price, shipping_price, bids_count, end_date)

    def _get_total_pages(self):
        first_page = self.base_url.format(1)
        json = self._get_product_json(first_page)
        total_products = json['initialState']['srp']['totalArticlesCount']
        page_size = json['initialState']['srp']['config']['pageSize']
        total_pages = int(total_products/page_size) + 2
        logging.info('[RICARDO] Total Products: {}, Page Size: {}, Total Pages: {}'.format(total_products, page_size, total_pages))
        return total_pages

    def _get_product_json(self, url):
        soup = self._get_soup(url, self.headers)
        json_string = soup.find('script', text = re.compile(r'window\.ricardo=.*')).contents[0].split('window.ricardo=')[1][:-1]
        json_o = json.loads(json_string)
        return json_o

    def _is_product_active(self, url):
        soup = self._get_soup(url, self.headers)
        active = False if soup.find('span', text = 'Der Artikel wurde erfolgreich verkauft.') else True
        return active

class Tutti(AuctionScanner):
    # curl 'https://www.tutti.ch/api/v10/list.json?aggregated=1&limit=30&o=2&q=lego&with_all_regions=true' 
    # -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0' 
    # -H 'Accept: application/json, text/plain, */*' 
    # -H 'Accept-Language: de' --compressed 
    # -H 'X-Tutti-Hash: 858521e7-f8d9-40ef-a534-6ae88d93165c' 
    # -H 'X-Tutti-Source: web LIVE-200803-89' 
    # -H 'Connection: keep-alive' 
    # -H 'Referer: https://www.tutti.ch/de/li/ganze-schweiz?o=2&q=lego' 
    # -H 'Cookie: tutti_xp=mZtaEl66QCSdEcIIX8kWrw.0.8020.a; lang=de; gr_reco=zeenkyfai9e-nzhtvml55sg-arowab2x8bk-snce3qk9stl; filters_ch=true' 
    # -H 'TE: Trailers'

    def __init__(self):
        AuctionScanner.__init__(self)
        self.q = Queries()
        self.base_url = 'https://www.tutti.ch/api/v10/list.json?aggregated=1&limit=50&o=1&q=lego&with_all_regions=true'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0',
            'Accept': 'application/json, text/plain, */*',
            'X-Tutti-Hash': '858521e7-f8d9-40ef-a534-6ae88d93165c'
        }

    def init_base_scan(self):
        logging.info('[TUTTI] Initialize base scan ...')
        url = self.base_url
        logging.info("[TUTTI] Scanning {} ...".format(url))
        json = self._get_json(url, self.headers, request_type='get')
        products = json['items']
        [self.products.append(product) for product in products]
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        #self.p.deploy_to_database()

    def _scan_product(self, product):
        url = "{}{}".format('https://www.ricardo.ch', product['url'])
        if not self.q.get_auction_by_url(url):
            logging.info("[RICARDO] Scanning {} ...".format(url))
            title = product['title']
            soup = self._get_soup(url, self.headers)
            description = soup.find('div', {'name' : 'description'}).text
            set_numbers = self._get_set_numbers_from_string(title) + self._get_set_numbers_from_string(description)
            set_numbers = list(dict.fromkeys(set_numbers))
            condition = 'new' if product['conditionKey'] == 'new' else 'used'
            has_auction = product['hasAuction']
            has_buy_now = product['hasBuyNow']
            auction_price = product['bidPrice']
            buy_now_price = product['buyNowPrice']
            shipping_price = product['shipping']['cost']
            bids_count = product['bidsCount']
            end_date = datetime.strptime(product['endDate'][:-4], '%Y-%m-%dT%H:%M:%S') if len(product['endDate']) == 23 else datetime.strptime(product['endDate'], '%Y-%m-%dT%H:%M:%SZ')
            for set_number in set_numbers:
                self.p.add_product(set_number, title, condition, url, has_auction, auction_price, has_buy_now, buy_now_price, shipping_price, bids_count, end_date)

if __name__ == '__main__':
    t = Tutti()
    t.init_base_scan()
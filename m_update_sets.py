import requests
import logging
from datetime import datetime

from database import MySQLDatabase
from queries import Queries

logging.basicConfig(filename='logs/{}_update_sets.log'.format(datetime.now().strftime('%Y%m%d')), filemode='a', format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.INFO)

db = MySQLDatabase()
q = Queries()

for year in range((datetime.now().year)-3, datetime.now().year):
    y = str(year)
    for page in range(1, 10):
        p = str(page)
        data = {'apiKey' : '3-icPn-cRhu-ZZJ3', 'userHash' : '', 'params' : "{ 'year':'"+y+"', 'orderBy':'Pieces', 'pageSize':200, 'pageNumber':"+p+" }" }
        r = requests.get('https://brickset.com/api/v3.asmx/getSets', params=data).json()
        if r['status'] == 'noRecords':
            break
        if r['status'] == 'success':
            print(r['sets'])
            for set in r['sets']:
                id = set['setID']
                set_number = set['number']
                variant = set['numberVariant']
                theme = set['theme']
                subtheme = set['subtheme'] if set.get('subtheme') else None
                year = set['year']
                name = set['name']
                minifigs = set['minifigs'] if set.get('minifigs') else None
                pieces = set['pieces'] if set.get('pieces') else None
                uk_price = None
                us_price = None
                ca_price = None
                eu_price = None
                ch_price = None
                if set['LEGOCom'].get('UK'):
                    if set['LEGOCom']['UK'].get('retailPrice'):
                        uk_price = set['LEGOCom']['UK']['retailPrice']
                if set['LEGOCom'].get('US'):
                    if set['LEGOCom']['US'].get('retailPrice'):
                        us_price = set['LEGOCom']['US']['retailPrice']
                if set['LEGOCom'].get('CA'):
                    if set['LEGOCom']['CA'].get('retailPrice'):
                        ca_price = set['LEGOCom']['CA']['retailPrice']
                if set['LEGOCom'].get('DE'):
                    if set['LEGOCom']['DE'].get('retailPrice'):
                        eu_price = set['LEGOCom']['DE']['retailPrice']
                image_url = set['image']['imageURL'] if set['image'].get('imageURL') else None
                owned_by = None
                wanted_by = None
                if set.get('collections') and set['collections'].get('ownedBy'):
                    owned_by = set['collections']['ownedBy']
                if set.get('collections') and set['collections'].get('wantedBy'):
                    wanted_by = set['collections']['wantedBy']
                data = (id, set_number, variant, theme, subtheme, year, name, minifigs, pieces, uk_price, us_price, ca_price, eu_price, ch_price, image_url, wanted_by, owned_by)
                if q.get_sets(id=id):
                    logging.info("[UPDATESET] {} has been found in database, updating ...".format(id))
                    update_data = {
                        'table_name' : 'tbl_sets',
                        'data' : {
                            'set_number' : set_number,
                            'variant' : variant,
                            'theme' : theme,
                            'subtheme' : subtheme,
                            'year' : year,
                            'name' : name,
                            'minifigs' : minifigs,
                            'pieces' : pieces,
                            'uk_price' : uk_price,
                            'us_price' : us_price,
                            'ca_price' : ca_price,
                            'eu_price' : eu_price,
                            'image_url' : image_url,
                            'owned_by' : owned_by,
                            'wanted_by' : wanted_by
                        },
                        'condition' : {
                            'id' : id
                        }
                    }
                    db._update_query(update_data)
                else:
                    logging.info("[UPDATESET] {} adding to database ...".format(set_number))
                    payload = {
                        'table_name' : 'tbl_sets',
                        'data' : {
                            'id' : id,
                            'set_number' : set_number,
                            'variant' : variant,
                            'theme' : theme,
                            'subtheme' : subtheme,
                            'year' : year,
                            'name' : name,
                            'minifigs' : minifigs,
                            'pieces' : pieces,
                            'uk_price' : uk_price,
                            'us_price' : us_price,
                            'ca_price' : ca_price,
                            'eu_price' : eu_price,
                            'ch_price' : ch_price,
                            'image_url' : image_url,
                            'owned_by' : owned_by,
                            'wanted_by' : wanted_by
                        }
                    }
                    db._insert_query(payload)
        else:
            logging.error(r)

q._create_tmp_newest_bricklink_prices()
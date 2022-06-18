from collections import defaultdict
import datetime

import requests
from xml.etree import ElementTree


exchange_rate_cache = defaultdict(dict)

def get_exchange_rate(currency_id, date):
    date_str = date.strftime('%d/%m/%Y')
    cached_exchange_rate = exchange_rate_cache[currency_id].get(date_str, None)
    if cached_exchange_rate is not None:
        return cached_exchange_rate
    response = requests.get(f'https://cbr.ru/scripts/XML_daily.asp?date_req={date_str}')
    tree = ElementTree.fromstring(response.content)
    for child in tree:
        if child.attrib['ID'] == currency_id:
            for value in child:
                if value.tag == 'Value':
                    exchange_rate = float(value.text.replace(',', '.'))
                    exchange_rate_cache[currency_id][date_str] = exchange_rate
                    return exchange_rate
    return None


def get_usd_exchange_rate(date):
    return get_exchange_rate('R01235', date)


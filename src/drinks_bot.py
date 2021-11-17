import logging
import requests
from bs4 import BeautifulSoup
import constants
import random

snappy_responses = ['. Is that cheap enough for ya?',
                    ', you cheapo!',
                    '. Run for your life, Jef Colruyt is chasing you!'
                    ]

def get_drinks_prices(words_received):
    """Command: drinks price <cola/cola-zero/ice-tea>. Retrieve price from Collect&Go website."""
    if any(drinks_trigger in words_received for drinks_trigger in constants.drinks_triggers):
        if 'ice-tea' in words_received or 'ice' in words_received or 'tea' in words_received:
            drink = 'ice-tea'
            url = 'https://www.collectandgo.be/colruyt/nl/assortiment/lipton-ice-tea-bruisend-33cl'
        elif 'cola' in words_received and 'zero' in words_received:
            drink = 'cola zero'
            url = 'https://www.collectandgo.be/colruyt/nl/assortiment/cola-zonder-suiker#pdp_3074457345616689399'
        elif 'cola' in words_received:
            drink = 'cola'
            url = 'https://www.collectandgo.be/colruyt/nl/assortiment/cola-met-suiker?#pdp_3074457345616677907'
        if drink and url:
            page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) '
                                                            'Gecko/20070725 Firefox/2.0.0.6'})
            if page.status_code == 200:
                soup = BeautifulSoup(page.content, 'html.parser')
                html_text = list(soup.children)[5].get_text()
                start_index = html_text.find('€')
                price = html_text[start_index:start_index+6]
                msg = f'The price of a {drink} is {price}. {random.choice(snappy_responses)}'
                return msg

    return None

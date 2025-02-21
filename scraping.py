import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import re
import requests


class CarItem:
    def __init__(self, id, brand, model, year, price, url):
        self.id = id
        self.url = url
        self.brand = brand
        self.model = model
        self.year = year
        self.price = price

    def to_database(self):
        """Save the item to the database"""


class Scraper:
    def _scrape_sibling(self, re_pattern, tag_type='p'):
        tag_element = self.soup.find(tag_type, string=re.compile(re_pattern))
        sibling_element = tag_element.next_sibling or tag_element.previous_sibling
        if sibling_element:
            return sibling_element.text
        return None

    def _scrape_css_selector(self,  css_selector, found_many='first'):
        if not found_many in ['first', 'last', 'all']:
            raise ValueError('found many most be in ["first", "last", "all"], but {} passed'.format(found_many))
        all_tags = self.soup.select(css_selector)
        if not all_tags:
            return None
        match found_many:
            case 'first':
                return all_tags[0].text
            case 'last':
                return all_tags[-1].text
            case 'all':
                return ''.join(all_tags)


class KavakItemScraper(Scraper):
    def __init__(self, url):
        self.url = url
        self.html = requests.get(url)
        self.soup = BeautifulSoup(self.html.content, 'html.parser')

    @property
    def item_id(self):
        text = self._scrape_sibling('Stock ID')
        return int(text)

    @property
    def brand(self):
        text = self._scrape_css_selector('ul.breadcrumb_breadcrumb__nPwIW li:nth-child(2) a')
        return text.capitalize()

    @property
    def model(self):
        text = self._scrape_css_selector('ul.breadcrumb_breadcrumb__nPwIW li:nth-child(3) a')
        return text.capitalize()

    @property
    def year(self):
        text = self._scrape_css_selector('ul.breadcrumb_breadcrumb__nPwIW li:nth-child(4) a')
        return int(text)

    @property
    def engine_displacement(self):
        disp_pattern = re.compile(r'(\d\.\d).*')
        text = self._scrape_css_selector('aside.buy-box_wrapper__jCjj4 h1.header_title__l7xVU') or ''
        displacement = disp_pattern.findall(text)
        if displacement:
            displacement = displacement[0]
            return float(displacement)
        return None



if __name__ == '__main__':
    car_item = KavakItemScraper('https://www.kavak.com/mx/usado/infiniti-qx60-35_sensory_auto_4wd-suv-2019')
    print(car_item.item_id)
    print(car_item.brand)
    print(car_item.model)
    print(car_item.year)
    print(car_item.engine_displacement)
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import re
import requests
import time

class CarItem:
    def __init__(self, car_id, brand, model, year, price, url):
        self.car_id = car_id
        self.url = url
        self.brand = brand
        self.model = model
        self.year = year
        self.price = price

    def __str__(self):
        return (
            f'Car ID: {self.car_id}\n'
            f'Brand: {self.brand}, Model: {self.model}, Year: {self.year}\n'
            f'Price: ${self.price}'
        )

    def to_database(self):
        """Save the item to the database"""


class Scraper:
    def _scrape_sibling(self, re_pattern, tag_type='p'):
        tag_element = self.soup.find(tag_type, string=re.compile(re_pattern))
        sibling_element = tag_element.next_sibling or tag_element.previous_sibling
        if sibling_element:
            return sibling_element.text
        return None

    def _scrape_css_selector(self,  css_selector, found_many='first', as_string=True, **kwargs):
        if not found_many in ['first', 'last', 'all']:
            raise ValueError('found many most be in ["first", "last", "all"], but {} passed'.format(found_many))
        all_tags = self.soup.select(css_selector, **kwargs)
        if not all_tags:
            return None
        if as_string:
            match found_many:
                case 'first':
                    return all_tags[0].text
                case 'last':
                    return all_tags[-1].text
                case 'all':
                    return ''.join(all_tags)
        else:
            match found_many:
                case 'first':
                    return all_tags[0]
                case 'last':
                    return all_tags[-1]
                case 'all':
                    return all_tags


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


class PageIterator(ABC):
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        """
        All classes must implement this method to iterate over the pages
        of the current website to extract the pages with the list of car
        items.
        :return:
        """
        pass


class KavakPageIterator(PageIterator):
    def __init__(self, base_url):
        self.base_url = base_url
        self.next_iteration = 0


    def __next__(self):
        req = requests.get(self.base_url, params={'page': self.next_iteration})
        self.next_iteration += 1
        if req.status_code != 200:
            raise StopIteration
        return KavakPageScraper(req)


class KavakPageScraper(Scraper):
    def __init__(self, req):
        self.url = req.request.url
        self.soup = BeautifulSoup(req.content, 'html.parser')

    def get_items(self):
        all_items = self._scrape_css_selector(
            '#main-content .results_results__container__tcF4_',
            as_string=False,
            found_many='first',
        ).children

        all_car_items = []
        for item in all_items:
            if item.find(string=re.compile('Vende tu auto y.*')):
                continue
            else:
                car_item = self._div_to_car_item(item)
                all_car_items.append(car_item)
        return all_car_items

    def _div_to_car_item(self, item):
        car_id = item.a.attrs['data-testid'].split('-')[-1]
        url = item.a['href']
        brand, model = item.find('h3', {'class': 'card-product_cardProduct__title__RR0CK'}).text.split(' • ')
        year = int(
            item.find('p', {'class': 'card-product_cardProduct__subtitle__hbN2a'}).text.strip(' • ')[0]
        )
        price = int(item.find(
            'span', {'class': 'amount_uki-amount__large__price__2NvVx'}
        ).text.replace(',', ''))
        return CarItem(car_id, brand, model, year, price, url)


    def __str__(self):
        return self.url


if __name__ == '__main__':
    lit = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
    for li in lit:
        car_item_1 = li.get_items()[0]
        print(car_item_1)
        break

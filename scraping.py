from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import re
import requests


class CarItem:
    def __init__(self, car_id, url, price, status='Disponible'):
        self.car_id = car_id
        self.url = url
        self.price = price
        self.status = status

    def __str__(self):
        return (
            f'Car ID: {self.car_id} [{self.status}]'
            f'price= ${self.price:,}\n'
            f'URL = {self.url}'
        )

    def to_database(self):
        """Save the item to the database"""


class Scraper:
    def __init__(self):
        self.soup = None # Each specific page should create a BeautifulSoup instance

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
        super().__init__()
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
    """
    This abstract base class provides a foundation for scraping paginated lists of items from webpages.
    Concrete subclasses must implement the iteration protocol (through the __iter__ magic method),
    yielding a PlatformWebScraper instance for each page of results.
    This PlatformPageScraper instance should be capable of scraping the individual items on that specific
    page.
    """
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        """
        All classes must implement this method to iterate over the pages
        of the current website to extract the pages with the list of car
        items.

        :return: PlatformWebScraper instance
        """
        pass


class KavakPageIterator(PageIterator):
    """
    This class implements the iteration protocol for scraping Kavak's paginated listings.
    Each iteration yields a KavakPageScraper instance, representing a single page of results,
    which can then be used to scrape individual vehicle listings.
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.next_iteration = 0


    def __next__(self):
        """
        Implementation of the iteration protocol for the paging listing the items.
        Each iteration, returns an instance of KavakPageScraper, which allows to scrap
        the specific page and extract individual vehicle listings.

        :return: KavakPageScraper instance
        """
        req = requests.get(self.base_url, params={'page': self.next_iteration})
        self.next_iteration += 1
        if req.status_code != 200:
            raise StopIteration
        return KavakPageScraper(req)


class KavakPageScraper(Scraper):
    def __init__(self, req):
        super().__init__()
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

    @staticmethod
    def _div_to_car_item(item):
        car_id = item.a.attrs['data-testid'].split('-')[-1]
        url = item.a['href']
        try:
            price = int(item.find(
                'span', {'class': 'amount_uki-amount__large__price__2NvVx'}
            ).text.replace(',', ''))
            status = 'Disponible'
        except AttributeError:
            price = None
            status = 'Apartado'

        return CarItem(car_id, url, price, status)


    def __str__(self):
        return self.url


if __name__ == '__main__':
    lit = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
    for li in lit:
        car_item_1 = li.get_items()[0]
        print(car_item_1)
        break

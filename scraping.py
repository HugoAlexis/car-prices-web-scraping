from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import re
import requests
from database import Database
from sqlite3 import IntegrityError
import time
import random


DB = Database()


class CarItem:
    """
    This class models a car item, providing methods to scrape its details
    from a listing and store the extracted information in a database."
    """
    def __init__(self, car_id, url, price, status='Disponible'):
        self.car_id = car_id
        self.url = url
        self.price = price
        self.status = status

    def __str__(self):
        """
        String representation of a car item.
        :return:
        """
        return (
            f'Car ID: {self.car_id} [{self.status}]'
            f'price= ${self.price:,}\n'
            f'URL = {self.url}'
        )

    def __bool__(self):
        """
        Returns true if the no-null attributes of the car item are available.
        :return: Boolean
        """
        conditions = [
            bool(self.car_id),
            bool(self.url)
        ]
        if all(conditions):
            return True
        return False

    def to_database(self):
        """Save the item to the database"""
        try:
            DB.query(
                """
                    INSERT INTO cars (id, url, price, status)
                    VALUES (?, ?, ?, ?)
                """,
                params=(self.car_id, self.url, self.price, self.status)
            )
        except IntegrityError:
            pass


class Scraper:
    """
    Class with different static methods for safe scraping.
    """
    def __init__(self):
        self.soup = None # Each specific page should create a BeautifulSoup instance

    def _scrape_sibling(self, re_pattern, tag_type='p'):
        """
        Find the html element which text contains a string with the given pattern. If
        the file exists in the page, returns the content of its sibling tag, otherwise
        return None.
        :param re_pattern: pattern to find the tag.
        :param tag_type: type of the tag to find.
        :return: text of the sibling tag found, or None if not found.
        """
        tag_element = self.soup.find(tag_type, string=re.compile(re_pattern))
        sibling_element = tag_element.next_sibling or tag_element.previous_sibling
        if sibling_element:
            return sibling_element.text
        return None

    def _scrape_css_selector(self,  css_selector, found_many='first', as_string=True, **kwargs):
        """
        Given a valid CSS selector, find the first element which matches the selector and
        returns its content (as a string, or as a list of tags matched).

        :param css_selector: string containing the CSS selector to find.
        :param found_many: action to perform if many tags are found to match the CSS selector.
        :param as_string: weather the method will return the tag or its tag.
        :param kwargs: additional parameters to pass to the CSS selector method.
        :return: all_tags (as a string if as_string is True, or a list of tags if as_string is False).
        """
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
    """
    Implementation for scraping and retrieving information about vehicles listed on Kavak.
    """
    def __init__(self, url):
        """
        Given the listing url of the Kavak car, makes a request to get the html from the
        car listing to extract information about the vehicle listed.
        :param url: URL of the Kavak car.
        """
        super().__init__()
        self.url = url
        self.html = requests.get(url)
        self.soup = BeautifulSoup(self.html.content, 'html.parser')

    @property
    def item_id(self):
        """Id of the listed car item."""
        text = self._scrape_sibling('Stock ID')
        return int(text)

    @property
    def brand(self):
        """Brand of the listed car item"""
        text = self._scrape_css_selector('ul.breadcrumb_breadcrumb__nPwIW li:nth-child(2) a')
        return text.capitalize()

    @property
    def model(self):
        """Model of the listed car item"""
        text = self._scrape_css_selector('ul.breadcrumb_breadcrumb__nPwIW li:nth-child(3) a')
        return text.capitalize()

    @property
    def year(self):
        """Year of the listed car item"""
        text = self._scrape_css_selector('ul.breadcrumb_breadcrumb__nPwIW li:nth-child(4) a')
        return int(text)

    @property
    def engine_displacement(self):
        """Engine displacement of the listed car item"""
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
        self.next_iteration = 0
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
        pagination_buttons = (
            BeautifulSoup(req.content, 'html.parser')
            .select('a.results_results__pagination-nav__Qcftr')
        )
        if len(pagination_buttons) < 2:
            raise StopIteration
        if req.status_code != 200:
            raise StopIteration
        return KavakPageScraper(req)


class KavakPageScraper(Scraper):
    """
    A class providing the functionality to scrap a Kavak page of results
    (from pages of the website's pagination).
    """
    def __init__(self, req):
        super().__init__()
        self.url = req.request.url
        self.soup = BeautifulSoup(req.content, 'html.parser')

    def get_items(self):
        """
        Return a list of CarIte instances found on the pagination page.

        :return: list of CarItem instances
        """
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
        """
        Given a (BeautifulSoup) tag containing the listing of a car item,
        return a CarItem instance.
        :param item: BeautifulSoup tag containing the listing of a car item
        :return CarItem instance: Instance containing the information of the car listing.
        """
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
    page_iterator = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
    for page in page_iterator:
        page_items = page.get_items()
        print(page.url, '\n', 'Found: ', len(page_items), end='\n'*2)
        for item in page_items:
            if item:
                item.to_database()
        time_to_sleep = 10 + random.random() * 10
        time.sleep(time_to_sleep)
    print('Done!')
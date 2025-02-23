import re

import requests
from bs4 import BeautifulSoup

from scraping import Scraper, PageIterator, CarItem


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


class KavakPageIterator(PageIterator):
    """
    This class implements the iteration protocol for scraping Kavak's paginated listings.
    Each iteration yields a KavakPageScraper instance, representing a single page of results,
    which can then be used to scrape individual vehicle listings.
    """
    def __init__(self, base_url):
        self.base_url = base_url


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

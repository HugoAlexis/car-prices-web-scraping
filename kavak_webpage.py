import requests
from bs4 import BeautifulSoup
from scraping import Scraper, PageIterator
from webpage_parsers import KavakItem
import time


class KavakPageIterator(PageIterator):
    """
    This class implements the iteration protocol for scraping Kavak's paginated listings.
    Each iteration yields a KavakPageScraper instance, representing a single page of results,
    which can then be used to scrape individual vehicle listings.
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.url = None


    def __next__(self):
        """
        Implementation of the iteration protocol for the paging listing the items.
        Each iteration, returns an instance of KavakPageScraper, which allows to scrap
        the specific page and extract individual vehicle listings.

        :return: KavakPageScraper instance
        """

        req = requests.get(self.base_url, params={'page': self.next_iteration})
        self.url = req.request.url
        self.next_iteration += 1
        pagination_buttons = (
            BeautifulSoup(req.content, 'html.parser')
            .select('a.results_results__pagination-nav__Qcftr')
        )

        if len(pagination_buttons) < 2 and self.next_iteration > 1:
            raise StopIteration
        if req.status_code != 200:
            raise StopIteration

        return KavakPageScraper(req.url)


class KavakPageScraper(Scraper):
    """
    A class providing the functionality to scrap a Kavak page of results
    (from pages of the website's pagination).
    """

    def __init__(self, url):
        super().__init__(url)
        self.div_items = self._scrape_css_selector(
            '#main-content .results_results__container__tcF4_',
            as_string=False,
            found_many='first',
        )

    def url_all_items(self):
        """
        Return a list of CarIte instances found on the pagination page.

        :return: list of CarItem instances
        """

        dict_all_items = {}
        for item in self.div_items.children:
            if 'Vende tu auto' in item.text:
                continue
            url = item.a.attrs['href']
            id = item.a.attrs['data-testid'].split('-')[-1]
            dict_all_items[id] = url
        return dict_all_items

    def labels_all_items(self):
        dict_all_items = {}
        for item in self.div_items.children:
            if 'Vende tu auto' in item.text:
                continue
            itme_id = item.a.attrs['data-testid'].split('-')[-1]
            div_labels = item.img.find_next_sibling('div')
            if div_labels:
                labels = div_labels.text
            else:
                labels = None

            dict_all_items[itme_id] = labels
        return dict_all_items

    def __str__(self):
        return self.url


if __name__ == '__main__':
    kavak_iterator = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
    for page in kavak_iterator:
        items = page.url_all_items()
        for id, url in items.items():
            item = KavakItem(url)
            print('Brand: {}'.format(item.brand))
            print('Model: {}'.format(item.model))
            print('Original_price: {}'.format(item.original_price))
            print('Price: {}'.format(item.price))
            print('Report: {}'.format(item.url_report))
            time.sleep(3)
        break
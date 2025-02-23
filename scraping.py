from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import re
import requests
from database import Database
from sqlite3 import IntegrityError


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

    def scrape_details(self, webpage_model):
        """
        Scrape the details from the webpage of a car item, following the model
        passed in the webpage model.
        :param webpage_model: CarItemWebpage with model to scrap the details.
        :return: dictionary with details extracted from the CarItem webpage.
        """
        pass


class CarItemWebpage:
    """
    This class serves as a model for extracting car item details from specific websites.

    Due to varying website structures, each website necessitates a unique CarItemWebpage
    model.
    Each desired data point (e.g., price, mileage) should be implemented as a
    class attribute, returning the scraped value as a string. If a data point is not
    found on the website, the attribute should return None. If an attribute is not implemented,
    it will return None.
    """
    def __init__(self, url):
        self.url = url
        self.req = requests.get(url)
        self.req_ok = (self.req.status_code == 200)
        if self.req_ok:
            self.soup = BeautifulSoup(self.req.content, 'html.parser')

    @property
    def brand(self):
        return None

    @property
    def model(self):
        return None

    @property
    def year(self):
        return None

    @property
    def engine_displacement(self):
        return None

    @property
    def version(self):
        return None

    @property
    def body_style(self):
        return None

    @property
    def fuel_economy(self):
        return None

    @property
    def city(self):
        return None

    @property
    def cylinders(self):
        return None
    @property
    def number_of_gears(self):
        return None

    @property
    def horsepower(self):
        return None

    @property
    def doors(self):
        return None

    @property
    def cruise_control(self):
        return None

    @property
    def distance_sensor(self):
        return None

    @property
    def start_button(self):
        return None

    @property
    def number_of_airbags(self):
        return None

    @property
    def abs(self):
        return None

    @property
    def passengers(self):
        return None

    @property
    def interior_material(self):
        return None

    def __getattr__(self, name):
        return None

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

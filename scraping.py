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
        self.base_url = url
        self.url = f'{self.base_url}?id={car_id}'
        self.price = price
        self.status = status
        self.details_scraped = False

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

    @property
    def exists_in_database(self):
        results = DB.select_query(f'SELECT * FROM car_info WHERE id = {self.car_id}')
        if results:
            return True
        return False

    def scrape_details(self, WebpageScraper):
        """
        Scrape the details from the webpage of a car item following the model
        passed in the webpage model, and saves it as an instance attribute.
        :param webpage_scraperl: CarItemWebpage class to scrap the details for CarItem listing.
        :return: dictionary with details extracted from the CarItem webpage.
        """
        item_scraper = WebpageScraper(self.url)
        details = {
            'brand': item_scraper.brand,
            'model': item_scraper.model,
            'year': item_scraper.year,
            'version': item_scraper.version,
            'engine_displacement' : item_scraper.engine_displacement,
            'odometer': item_scraper.odometer,
            'transmission': item_scraper.transmission,
            'body_style': item_scraper.body_style,
            'fuel_economy': item_scraper.fuel_economy,
            'city': item_scraper.city,
            'cylinders': item_scraper.cylinders,
            'number_of_gears': item_scraper.number_of_gears,
            'horsepower': item_scraper.horsepower,
            'doors': item_scraper.doors,
            'cruise_control': item_scraper.cruise_control,
            'distance_sensor': item_scraper.distance_sensor,
            'start_button': item_scraper.start_button,
            'number_of_airbags': item_scraper.number_of_airbags,
            'abs': item_scraper.abs,
            'passengers': item_scraper.passengers,
            'interior_materials' : item_scraper.interior_materials,
            'price': item_scraper.price,
            'price_without_discount': item_scraper.price_without_discount,
        }

        if self.car_id != item_scraper.item_id:
            print(type(self.car_id), type(item_scraper.item_id))
            raise IntegrityError(f'{self.car_id} - {item_scraper.item_id}: IDs do not match')

        self.item_details = details
        self.details_scraped = True

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

    def details_to_database(self):
        """Save the details of the car listing to the database"""
        if not self.details_scraped:
            raise Exception('Details not scraped yet.')

        DB.query(
                """
                INSERT INTO car_info 
                    (id, brand, model, version, year, body_style, engine_displacement, odometer, 
                     city, transmission, mileage, cylinders, horsepower, number_of_gears, doors,
                     number_of_airbags, abs, passengers, interior_materials, start_button, cruise_control, 
                     price, price_without_discount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (self.car_id, self.item_details['brand'], self.item_details['model'], self.item_details['version'],
                 self.item_details['year'], self.item_details['body_style'], self.item_details['engine_displacement'],
                 self.item_details['odometer'], self.item_details['city'], self.item_details['transmission'],
                 self.item_details['fuel_economy'], self.item_details['cylinders'], self.item_details['horsepower'],
                 self.item_details['number_of_gears'], self.item_details['doors'], self.item_details['number_of_airbags'],
                 self.item_details['abs'], self.item_details['passengers'], self.item_details['interior_materials'],
                 self.item_details['start_button'], self.item_details['cruise_control'],
                 self.item_details['price'], self.item_details['price_without_discount'])
            )



class Scraper:
    """
    Class with different static methods for safe scraping.
    """

    def __init__(self, url):
        self.url = url
        self.req = requests.get(url)
        self.req_ok = (self.req.status_code == 200)
        if self.req_ok:
            self.soup = BeautifulSoup(self.req.content, 'html.parser')


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
        if not tag_element:
            return None
        sibling_element = tag_element.next_sibling or tag_element.previous_sibling
        if sibling_element:
            return sibling_element.text
        return None

    def __getattr__(self, attr):
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

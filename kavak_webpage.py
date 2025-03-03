import re
import requests
from bs4 import BeautifulSoup
from scraping import Scraper, PageIterator, CarItem
from requests.exceptions import RequestException


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
        super().__init__(url)

    @property
    def item_id(self):
        """Id of the listed car item."""
        text = self._scrape_sibling('Stock ID')
        try:
            return int(text)
        except ValueError:
            return None

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

    @property
    def version(self):
        """Version of the listed car item"""
        text = self._scrape_css_selector('ul.breadcrumb_breadcrumb__nPwIW li:nth-child(5)')
        # Remove engine displacement from the text version
        if text:
            text_version = re.compile(r'\d+\.\d+\s(.*)').findall(text)
            if text_version:
                return text_version[0].capitalize()
        return None

    @property
    def body_style(self):
        """Body style of the listed car item"""
        text = self._scrape_sibling('Tipo de Carrocer')
        if text:
            return text.capitalize()

    @property
    def fuel_economy(self):
        """Fuel eco of the listed car item"""
        text = self._scrape_sibling('Consumo combinado')
        if text:
            return text.capitalize()

    @property
    def odometer(self):
        """Odometer of the listed car item"""
        text = self._scrape_css_selector('p.header_subtitle__y_nvg')
        if text:
            odometer_pattern = re.compile(r'([0-9,]+)\skm.*')
            odometer = odometer_pattern.findall(text)
            if odometer:
                return int(odometer[0].replace(',', ''))

    @property
    def transmission(self):
        """Type of transmission of the listed car item"""
        text = self._scrape_css_selector('aside .buy-box_extended__YcHd4 ul li:nth-child(3) .filters_info__WlDer span:nth-child(2)')
        if text:
            return text.strip().capitalize()



    @property
    def city(self):
        """City of the listed car item"""
        text = self._scrape_sibling('Ciudad$')
        if text:
            return text.capitalize()

    @property
    def cylinders(self):
        """Cylinders of the listed car item"""
        text = self._scrape_sibling('Cilindros')
        if text:
            return int(text)

    @property
    def number_of_gears(self):
        """Number of gears of the listed car item"""
        text = self._scrape_sibling('N.?mero de Velocidades')
        if text:
            return int(text)

    @property
    def horsepower(self):
        """Horsepower of the listed car item"""
        text = self._scrape_sibling('Caballos de Fuerza')
        if text:
            return int(text)

    @property
    def doors(self):
        """Doors of the listed car item"""
        text = self._scrape_sibling('N.?mero de Puertas')
        if text:
            return int(text)

    @property
    def cruise_control(self):
        """Wheather the listed car item has cruise control"""
        text = self._scrape_sibling('Control de Crucero')
        if text:
            if text.capitalize() in ['Sí', 'Si']:
                return True
            return False
        return False

    @property
    def distance_sensor(self):
        """Weather the listed car item has distance sensor"""
        text = self._scrape_sibling('Sensor de distancia')
        if text:
            if text.capitalize() in ['Sí', 'Si']:
                return True
            return False
        return False

    @property
    def start_button(self):
        """Weather the listed car item has start button"""
        text = self._scrape_sibling('Boton de Encendido')
        if text:
            if text.capitalize() in ['Sí', 'Si']:
                return True
            return False
        return False

    @property
    def number_of_airbags(self):
        """Number of airbags of the listed car item"""
        text = self._scrape_sibling('N.?mero total de Airbags')
        if text:
            return int(text)
        return False

    @property
    def abs(self):
        """Weather the  listed car item has ABS system"""
        text = self._scrape_sibling('Tipo Frenos ABS')
        if text:
            if text.capitalize() in ['Sí', 'Si']:
                return True
            return False
        return False

    @property
    def passengers(self):
        """Number of passengers of the listed car item"""
        text = self._scrape_sibling('N.?mero de Pasajeros')
        if text:
            return int(text)

    @property
    def interior_materials(self):
        """Material used for the interior in the listed car item"""
        text = self._scrape_sibling('Material Asientos')
        if text:
            return text.capitalize()

    @property
    def price_without_discount(self):
        """Price of the listed car item without discount"""
        text = self._scrape_css_selector('.price_amount__dRxZ8')
        if text:
            return int(text.replace(',', '').replace('$', ''))

    @property
    def price(self):
        text = self._scrape_css_selector('span.amount_uki-amount__extraLarge__price__ZMOLc')
        if text:
            return int(text.replace(',', '').replace('$', ''))

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
        car_id = int(item.a.attrs['data-testid'].split('-')[-1])
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

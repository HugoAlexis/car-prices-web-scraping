import time
import random
from webpage_parsers import KavakItem
from kavak_webpage import KavakPageIterator
import ORM
from database import Database


kavak_sleep_time = 5


class Main:
    def __init__(self):
        self.DB = Database(use_postgres=True)
        self.PageIterator = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
        self.identifier_items_scraped = []

    def parse_new_item(self, item_parser):
        car_version = ORM.Version.from_parser(item_parser)
        car = ORM.Car.from_parser(item_parser, version_object=car_version)
        version_details = ORM.VersionDetails.from_parser(item_parser, version_object=car_version)

        return car, car_version, version_details

    def parse_existing_item(self, db_item):
        car_version = ORM.Version.from_db(db_item['version_id'])
        car = ORM.Car.from_db(db_item['car_id'], version_object=car_version)
        version_details = ORM.VersionDetails.from_db(db_item['version_id'], version_object=car_version)
        return car, car_version, version_details

    def dump_item_objects(self, objects):
        for object in objects:
            object.dump()

    def run(self):
        with (ORM.Scrape() as scrape):
            for i, page in enumerate(self.PageIterator):
                page_urls = page.url_all_items()
                page_labels = page.labels_all_items()
                page_prices = page.prices_all_items()
                page_cities = page.cities_all_items()
                page_odometers = page.odometer_all_items()

                estimated_time = kavak_sleep_time * len(page_urls)
                print(f'f[{i}] Scraping data for {len(page_urls)} items ({estimated_time:.0f} s est).')

                for id, url in page_urls.items():
                    if id in self.identifier_items_scraped:
                        continue

                    db_item = self.DB.get_item_match('cars', {'identifier': id})
                    if not db_item:
                        item_parser = KavakItem(url + f'?id={id}')
                        car, car_version, version_details = self.parse_new_item(item_parser)
                        time.sleep(kavak_sleep_time)
                    else:
                        car, car_version, version_details = self.parse_existing_item(db_item)
                    scrape_history = ORM.ScrapeHistory(
                        car_object=car, scrape_object=scrape, labels=page_labels[id] or '',
                        price=int(page_prices[id]) if page_prices[id] else None)
                    car_info = ORM.CarInfo(car, city=page_cities[id], odometer=page_odometers[id])
                    self.dump_item_objects(
                        [car_version, car, version_details, scrape_history, car_info]
                    )

                    self.identifier_items_scraped.append(id)







if __name__ == '__main__':
    main = Main()
    main.run()
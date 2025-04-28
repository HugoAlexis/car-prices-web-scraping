import time
import random
from webpage_parsers import KavakItem
from kavak_webpage import KavakPageIterator
import ORM
from database import Database


class Main:
    def __init__(self):
        self.DB = Database(use_postgres=True)
        self.PageIterator = KavakPageIterator('https://www.kavak.com/mx/seminuevos')

    def run(self):
        with ORM.Scrape() as scrape:
            for page in self.PageIterator:
                page_urls = page.url_all_items()
                for id, url in page_urls.items():
                    item_parser = KavakItem(url + f'?id={id}')
                    car_version = ORM.Version.from_parser(item_parser)
                    car = ORM.Car.from_parser(item_parser, version_object=car_version)
                    version_details = ORM.VersionDetails.from_parser(item_parser, version_object=car_version)
                    scrape_history = ORM.ScrapeHistory(car_object=car, scrape_object=scrape, labels='')

                    car_version.dump()
                    car.dump()
                    version_details.dump()
                    scrape_history.dump()
                    #time.sleep(5)





if __name__ == '__main__':
    main = Main()
    main.run()
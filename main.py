import time
import random
from sqlite3 import IntegrityError

from kavak_webpage import KavakPageIterator, KavakItemScraper

def scrap_all_products():
    pass

if __name__ == '__main__':
    page_iterator = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
    for page in page_iterator:
        page_items = page.get_items()
        print(page_iterator.url)
        print('Found {} items'.format(len(page_items)))

        for i, item in enumerate(page_items):
            print(i, end=' - ')
            item.to_database()
            if item.exists_in_database:
                continue

            item.scrape_details(KavakItemScraper)
            item.details_to_database()

            time_to_sleep = random.randrange(18, 22)
            time.sleep(time_to_sleep)
        print('\n'*2)

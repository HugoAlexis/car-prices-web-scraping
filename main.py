import time
import random
from kavak_webpage import KavakPageIterator, KavakItemScraper

if __name__ == '__main__':
    page_iterator = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
    for page in page_iterator:
        page_items = page.get_items()
        print(page_iterator.url)
        print('Found {} items'.format(len(page_items)))

        for i, item in enumerate(page_items):
            if item:    # If the request is ok for the webpage of item
                print(i, end=' - ')
                item.to_database()
                if item.exists_in_database:
                    continue
                if item.status == 'Disponible':
                    item.scrape_details(KavakItemScraper)
                    item.details_to_database()
                    print(item.item_details)

                time_to_sleep = random.randrange(15, 25)
                time.sleep(time_to_sleep)
        print('\n'*2)
import time
import random
from kavak_webpage import KavakPageIterator, KavakItemScraper

if __name__ == '__main__':
    page_iterator = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
    for page in page_iterator:
        page_items = page.get_items()
        for item in page_items:
            if item:
                item.to_database()
                item.scrape_details(KavakItemScraper)
                item.details_to_database()
                time.sleep(5)
        break
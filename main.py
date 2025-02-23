import time
import random
from kavak_webpage import KavakPageIterator

if __name__ == '__main__':
    page_iterator = KavakPageIterator('https://www.kavak.com/mx/seminuevos')
    for page in page_iterator:
        page_items = page.get_items()
        print(page.url, '\n', 'Found: ', len(page_items), end='\n'*2)
        for item in page_items:
            if item:
                item.to_database()
        time_to_sleep = 10 + random.random() * 10
        time.sleep(time_to_sleep)
    print('Done!')
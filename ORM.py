import time
from database import Database

class Scrape:
    def __init__(self):
        self.scrape_id = self._get_id()
        self.datetime_start = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.datetime_end = None
        self.finish_ok = False
        self.error_type = ''

    def _get_id(self):
        scrape_ids = db.select(
            table='scrapes',
            columns=['scrape_id'],
        )
        if scrape_ids:
            scrape_id = max(scrape_ids, key=lambda x: x[0])[0] + 1
        else:
            scrape_id = 0
        return scrape_id


    def dump(self):
        db.insert(
            table='scrapes',
            values=self.__dict__
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.datetime_end = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if not exc_type:
            self.finish_ok = True
        else:
            self.finish_ok = False
            self.error_type = exc_type.__name__
            self.error_msg = str(exc_val)
        self.dump()


if __name__ == '__main__':
    db = Database(use_postgres=True)
    for i in range(0):
        try:
            with Scrape() as scrape:
                time.sleep(2)
                raise ValueError('Paso otro error')
        except ValueError:
            pass
    all_scrapes = db.select(
        table='scrapes'
    )
    for scrape_i in all_scrapes:
        print(scrape_i)

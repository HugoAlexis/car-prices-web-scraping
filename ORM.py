import time
from database import Database

db = Database(use_postgres=True)


class ObjectModelMixin:
    def dump(self):
        db.insert(
            table=self.table_name,
            values=self.__dict__
        )

class Scrape(ObjectModelMixin):
    table_name = 'scrapes'
    table_id = 'scrape_id'

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


class Version(ObjectModelMixin):
    table_name = 'versions'
    table_id = 'version_id'

    def __init__(self, brand, model, version_name, year_prod, body_style, engine_displacement, transmission_type):
        self.brand = brand.capitalize()
        self.model = model.capitalize()
        self.version_name = version_name.capitalize()
        self.year_prod = year_prod
        self.body_style = body_style.upper()
        self.engine_displacement = engine_displacement
        self.transmission_type = transmission_type.capitalize()
        self.version_id = self._get_id()

    def _get_id(self):
        ids = db.select(
            table='versions',
            columns=['version_id'],
            where_clause="""
                brand = ? 
                AND model = ? 
                AND version_name = ?
                AND year_prod = ? 
                AND body_style = ?
                AND engine_displacement = ?
                AND transmission_type = ?
            """,
            where_params=(self.brand, self.model, self.version_name, self.year_prod,
             self.body_style, self.engine_displacement, self.transmission_type)
        )
        if ids:
            id = ids[0][0]
            self._already_exists = True
        else:
            self._already_exists = False
            all_ids = db.select(
                table='versions',
                columns=['version_id'],
            )
            if all_ids:
                id = max(all_ids, key=lambda x: x[0])[0] + 1
            else:
                id = 0
        return id

    def dump(self):
        if not self._already_exists:
            super().dump()



if __name__ == '__main__':
    db = Database(use_postgres=True)
    for i in range(5):
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

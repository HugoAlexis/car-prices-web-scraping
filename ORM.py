import time
from dotenv import load_dotenv
from database import db
import os

load_dotenv('.env')
WEBSITE1 = os.getenv('WEBSITE1')

class ObjectModel:
    table_name = ''
    table_id = []
    table_columns = []

    """
    A base  class for Object-Relational Mapping (ORM) models.

    Functionality:
        - Insert (`dump`) and update (`update`) data in a database.
        - Create ORM instances from parser objects via `from_parser`.

    Constraints:
        - All database table columns must match an instance attribute or @property.
        - All extra instance attributes must start with _ or __ to be ignored by ORM methods.

    Expected in subclasses (as class attributes):
        - `table_name`: Name of the table (str).
        - `table_columns`: List of valid column names (str) for the table.
        - `table_id`: list of column names (str) that constitute the table id.

    Methods:
        - dump(): Inserts the object into the database.
        - update(): Updates the existing record using the primary key.
        - from_parser(): Factory method to create an ORM instance from a parser object.
    """

    def dump(self):
        """
           Inserts the object into the database.

           This method uses the `table_name` attribute to determine the target table
           and inserts the object's attributes (`__dict__`) as column values.
        """
        db.insert(
            table=self.table_name,
            values=self.__dict__
        )

    @classmethod
    def from_parser(cls, parser_obj, **kwargs):
        """ 
        Create an instance of the ORM class from a parser object.

        Args:
            parser_obj: An object with @property accessros for attributes matching
                        the expected `table_columns`
        :return:
            An instance of the ORM class with fields populated from the parser.
        """

        for field in cls.table_columns:
            kwargs[field] = getattr(parser_obj, field)

        return cls(**kwargs)

    @classmethod
    def from_db(cls, column_id, **kwargs):
        if not isinstance(column_id, list):
            column_id = [column_id]

        item_values = db.get_item_match(
            table_name=cls.table_name,
            item_values=dict(zip(cls.table_id, column_id)))

        return cls(**item_values, **kwargs)



class Scrape(ObjectModel):
    table_name = 'scrapes'
    table_id = ['scrape_id']
    table_columns = ['datetime_start', 'datetime_end', 'finish_ok', 'error_type', 'error_msg']

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
        self.dump()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.datetime_end = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if not exc_type:
            self.finish_ok = True
        else:
            self.finish_ok = False
            self.error_type = exc_type.__name__
            self.error_msg = str(exc_val)
            db.connection.rollback()
        self.dump_update()
        return True

    def dump_update(self):
        db.update(
            table=self.table_name,
            values=self.__dict__,
            where_clause='scrape_id = ?',
            where_params=[self.scrape_id]
        )


class Version(ObjectModel):
    table_name = 'versions'
    table_id = ['version_id']
    table_columns = [
        'brand', 'model', 'version_name', 'year_prod', 'body_style', 'engine_displacement',
        'transmission_type'
    ]

    def __init__(self, brand, model, version_name, year_prod, body_style, engine_displacement, transmission_type, **kwargs):
        self.brand = brand.capitalize()
        self.model = model.capitalize()
        self.version_name = version_name.capitalize()
        self.year_prod = year_prod
        self.body_style = body_style.upper() if body_style else None
        self.engine_displacement = engine_displacement if engine_displacement else None
        self.transmission_type = transmission_type.capitalize() if transmission_type else None
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


class VersionDetails(ObjectModel):
    table_name = 'version_details'
    table_id = ['version_id']
    table_columns = [
        'mileage', 'cylinders', 'num_of_gears', 'fuel_range', 'engine_type',
        'fuel_type', 'horsepower', 'rim_inches', 'rim_material', 'num_of_doors',
        'num_of_passengers', 'num_of_airbags', 'has_abs', 'interior_materials',
        'has_start_button', 'has_cruise_control', 'has_distance_sensor', 'has_bluetooth',
        'has_rain_sensor', 'has_automatic_emergency_breaking', 'has_gps', 'has_sunroof',
        'has_androidauto', 'has_applecarplay', 'weight_kg'
    ]

    def __init__(
            self,
            version_object,
            mileage=None,
            cylinders=None,
            num_of_gears=None,
            fuel_range=None,
            engine_type=None,
            fuel_type=None,
            horsepower=None,
            rim_inches=None,
            rim_material=None,
            num_of_doors=None,
            num_of_passengers=None,
            num_of_airbags=None,
            has_abs=None,
            interior_materials=None,
            has_start_button=None,
            has_cruise_control=None,
            has_distance_sensor=None,
            has_bluetooth=None,
            has_rain_sensor=None,
            has_automatic_emergency_breaking=None,
            has_gps=None,
            has_sunroof=None,
            has_androidauto=None,
            has_applecarplay=None,
            weight_kg=None,
            **kwargs
        ):
        self._version_object = version_object
        self.version_id = self._get_id(version_object.version_id)
        self.mileage = round(float(mileage), 1) if mileage else None
        self.cylinders = int(cylinders) if cylinders else None
        self.num_of_gears = int(num_of_gears) if num_of_gears else None
        self.fuel_range = int(fuel_range) if fuel_range else None
        self.engine_type = engine_type.capitalize() if engine_type else None
        self.fuel_type = fuel_type.capitalize() if fuel_type else None
        self.horsepower = int(horsepower) if horsepower else None
        self.rim_inches = int(rim_inches) if rim_inches else None
        self.rim_material = rim_material.capitalize() if rim_material else None
        self.num_of_doors = int(num_of_doors) if num_of_doors else None
        self.num_of_passengers = int(num_of_passengers) if num_of_passengers else None
        self.num_of_airbags = int(num_of_airbags) if num_of_airbags else None
        self.has_abs = bool(has_abs) if has_abs else False
        self.interior_materials = interior_materials.capitalize() if interior_materials else None
        self.has_start_button = bool(has_start_button) if has_start_button else False
        self.has_cruise_control = bool(has_cruise_control) if has_cruise_control else False
        self.has_distance_sensor = bool(has_distance_sensor) if has_distance_sensor else False
        self.has_bluetooth = bool(has_bluetooth) if has_bluetooth else False
        self.has_rain_sensor = bool(has_rain_sensor) if has_rain_sensor else False
        self.has_automatic_emergency_breaking = bool(has_automatic_emergency_breaking) if has_automatic_emergency_breaking else False
        self.has_gps = bool(has_gps) if has_gps else False
        self.has_sunroof = bool(has_sunroof) if has_sunroof else False
        self.has_androidauto = bool(has_androidauto) if has_androidauto else False
        self.has_applecarplay = bool(has_applecarplay) if has_applecarplay else False
        self.weight_kg = int(weight_kg) if weight_kg else None

    def _get_id(self, version_id):
        ids = db.select(
            table=self.table_name,
            columns=self.table_id,
            where_clause="""
                version_id = ?
            """,
            where_params=(version_id,)
        )
        if ids:
            self._already_exists = True
        else:
            self._already_exists = False

        return version_id

    def dump(self):
        if self._already_exists:
            return
        super().dump()



class Car(ObjectModel):
    table_name = 'cars'
    table_id = ['car_id']
    table_columns = [
        'url', 'image_url', 'report_url', 'website', 'identifier', 'car_id', 'version_id'
    ]

    def __init__(
            self,
            identifier,
            version_object,
            url,
            image_url,
            website=WEBSITE1,
            **kwargs,
        ):

        self._version_object = version_object
        self.url = url
        self.image_url = image_url
        self.website = website
        self.identifier = identifier
        self.car_id = self._get_id()
        self.version_id = version_object.version_id

    def _get_id(self):
        car_id = db.select(
            table=self.table_name,
            columns=self.table_id,
            where_clause="""
                identifier = ? AND website = ?
            """,
            where_params=(self.identifier, self.website),
        )

        if car_id:
            self._already_exists = True
            return car_id[0][0]
        else:
            self._already_exists = False
            all_ids = db.select(
                table=self.table_name,
                columns=self.table_id,
            )

            if all_ids:
                return max(all_ids, key=lambda x: x[0])[0] + 1
            else:
                return 0

    def dump(self):
        if not self._already_exists:
            super().dump()


class CarInfo(ObjectModel):
    table_name = 'car_info'
    table_id = ['car_id']
    table_columns = ['city', 'odometer', 'image_path', 'report_path']

    def __init__(
            self,
            car_object,
            city=None,
            odometer=None,
        ):
        self._car_object = car_object
        self.car_id = car_object.car_id
        self.city = city
        self.odometer = odometer
        image_format = self._car_object.image_url.split('.')[-1]
        if image_format not in ['jpg', 'jpeg', 'png']:
            image_format = 'webp'
        report_format = 'pdf'

        self.image_path = os.path.join(
            'data',
            'images',
            self._car_object.website,
            f'{self._car_object.identifier}.{image_format}'
        )
        self.report_path = os.path.join(
            'data',
            'reports',
            self._car_object.website,
            f'{self._car_object.identifier}.{report_format}'
        )

    def dump(self):
        id = db.select(
            table=self.table_name,
            columns=self.table_id,
            where_clause="""
                car_id = ?
            """,
            where_params=(self.car_id,)
        )
        if id:
            return
        else:
            super().dump()


class ScrapeHistory(ObjectModel):
    table_name = 'scrape_history'

    def __init__(
            self,
            car_object,
            scrape_object,
            labels,
            price
        ):
        self._car_object = car_object
        self._scrape_object = scrape_object
        self.car_id = car_object.car_id
        self.scrape_id = scrape_object.scrape_id
        self.labels = labels
        self.price = price


from scraping import Scraper
import re

class KavakItem(Scraper):

    @property
    def website(self): return 'kavak'

    @property
    def identifier(self): return self._scrape_sibling('Stock ID')

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def mileage(self): return r'(\d+)\s?Consumo combinado'

    @Scraper.css_extract_text()
    def original_price(self): return 'span.price_amount__dRxZ8'

    @Scraper.css_extract_text()
    def price(self): return 'span.amount_uki-amount__extraLarge__price__ZMOLc'

    @Scraper.css_extract_text()
    def brand(self): return 'ul.breadcrumb_breadcrumb__nPwIW li:nth-child(2) a'

    @Scraper.css_extract_text()
    def model(self): return 'ul.breadcrumb_breadcrumb__nPwIW li:nth-child(3) a'

    @Scraper.css_extract_text()
    def year_prod(self): return 'ul.breadcrumb_breadcrumb__nPwIW li:nth-child(4) a'

    @Scraper.css_extract_text()
    def version_name(self): return 'ul.breadcrumb_breadcrumb__nPwIW li:nth-child(5) span'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def engine_displacement(self): return '(\d+(?:\.\d+)?)\s?Litros'

    @Scraper.re_extract_text()
    def cylinders(self): return '(\d+)\s?Cilindros'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def mileage(self): return r'(\d+\.\d+)\s?Consumo'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def city(self): return r'([a-zA-Z\sáéíóú]+)\s?Ciudad'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def car_id(self): return r'(\d+)\s?Stock ID'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def horsepower(self): return r'(\d+)\s?Caballos de Fuerza'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def weight_kg(self): return r'(\d+)\s?Peso bruto'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def fuel_range(self): return r'(\d+)\s?Autonom.a combinada'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def num_of_gears(self): return r'(\d+)\s?N.mero de Velocidades'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def fuel_type(self): return r'([A-Z]{1}[a-z]+)\s?Combustible'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def engine_type(self): return r'([A-ZÁÉÍÓÚ][a-záéíóú]+)\s?Tipo de motor'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def num_of_doors(self): return r'(\d+)\s?N.mero de Puertas'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def num_of_airbags(self): return r'(\d+)N.mero.*Airbags'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def rim_inches(self): return r'(\d+)\s?Di.metro de Rin'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def rim_material(self): return r'([A-ZÁÉÍÓÚ][a-záéíóú]+)\s?Tipo de Rin'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_startstop_button(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})Start.Stop'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_gps(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?GPS'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_start_button(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Boton de Encendido'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_sunroof(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Techo Panor.mico'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_cruise_control(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Control de Crucero'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_heated_seats(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Asientos.*alefaccionados'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_distance_sensor(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Sensor de distancia'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_abs(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Tipo Frenos ABS'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_rain_sensor(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Sensor de lluvia'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_automatic_emergency_breaking(self):
        return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Asistencia de frenado'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_bluetooth(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Bluetooth'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def num_of_passengers(self): return r'(\d+)\s?N.mero de Pasajeros'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def interior_materials(self): return r'([A-ZÁÉÍÓÚ][a-záéíóú]+)\sMaterial Asientos?'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_touchscreen(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Pantalla T.ctil'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_androidauto(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Android Auto'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def has_androidauto(self): return r'([A-ZÁÉÍÓÚa-záéíóú]{2})\s?Apple CarPlay'

    @Scraper.re_extract_text(outer_tag='div.desktop_car-detail__start__BToHy')
    def body_style(self): return r'[^A-Z]([A-Z][a-zA-Z]*)Tipo de .arrocer.a'

    @property
    def body_style(self): return self._scrape_sibling('Tipo de Carrocería')

    @Scraper.re_extract_text(outer_tag='aside.buy-box_wrapper__jCjj4 ')
    def transmission_type(self): return r'Transmisión\s?(Automático|Manual)'

    @property
    def image_url(self):
        img_tag = self.soup.select('div.keen-slider__slide img')
        if img_tag:
            return  img_tag[0].attrs['src']
        return None

    @property
    def report_url(self): return None

class AutocosmosItem(Scraper):

    @property
    def combustible(self):
        return self._scrape_sibling('Combustible', 'td')

    @property
    def has_sunroof(self):
        has_x = self._scrape_sibling('Quemacocos', 'td') or ''
        return False if ('no tiene' in has_x.strip().lower()) else True


if __name__ == '__main__':
    item = KavakItem('https://www.kavak.com/mx/usado/nissan-frontier-25_platinum_le_auto-pickup-2022')
    print('brand: ', item.brand)
    print('model: ', item.model)
    print('year: ', item.year_prod)
    print('transmission_type: ', item.transmission_type)
    print('mileage: ', item.mileage)
    print('cylinders: ', item.cylinders)
    print('num_of_gears:', item.num_of_gears)
    print('fuel_type: ', item.fuel_type)
    print('fuel_range: ', item.fuel_range)
    print('engine_type: ', item.engine_type)
    print('horsepower: ', item.horsepower)
    print('rim_inches: ', item.rim_inches)
    print('rim_materials: ', item.rim_material)
    print('num_of_doors: ', item.num_of_doors)
    print('num_of_passengers: ', item.num_of_passengers)
    print('num_of_airbags: ', item.num_of_airbags)
    print('has_abs: ', item.has_abs or 'No')
    print('interior_materials: ', item.interior_materials or 'No')
    print('has_startstop_button: ', item.has_startstop_button or 'No')
    print('has_cruise_contro: ', item.has_cruise_control or 'No')
    print('has_distance_sensor: ', item.has_distance_sensor or 'No')
    print('has_bluetooth: ', item.has_bluetooth or 'No')
    print('has_rain_sensor: ', item.has_rain_sensor or 'No')
    print('has_emergency_breaking: ', item.has_automatic_emergency_breaking or 'No')
    print('has_gps: ', item.has_gps or 'No')
    print('has_sunroof: ', item.has_sunroof or 'No')
    print('has_androidauto: ', item.has_androidauto or 'No')
    print('weigth_kg: ', item.weight_kg)
    print(item.url_image)

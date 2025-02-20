import requests
from bs4 import BeautifulSoup


class CarItem:
    def __init__(self, id, brand, model, year, price, url):
        self.id = id
        self.url = url
        self.brand = brand
        self.model = model
        self.year = year
        self.price = price

    def to_database(self):
        """Save the item to the database"""

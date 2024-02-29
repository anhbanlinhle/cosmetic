from typing import Any
import scrapy
import json
import re
from ..db_connector import connector
from ..db_connector import constants
from ..items import Product, Ingredient

from scrapy.http import Request, Response

class BaseSpider(scrapy.Spider):
    def start_requests(self):
        pass

    def parse_link(self, response):
        pass

    def parse_product(self, response: Response, **kwargs: Any):
        pass

    def parse_ingredient(self, response: Response, **kwargs: Any):
        pass

    def generate_ingredient_id(self, name):
        result = ""

        for char in name:
            if 'A' <= char <= 'Z':
                result += chr(ord(char) + 32)
            elif char == ' ':
                result += '-'
            else:
                result += char
        
        return result
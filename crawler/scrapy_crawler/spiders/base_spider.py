from typing import Any
import scrapy
from scrapy_crawler.db_connector import connector
from scrapy_crawler.db_connector import constants
from scrapy_crawler.items import Product, Ingredient

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
    
    def check_exist_record(self, record: Ingredient | Product):
        if isinstance(record, Ingredient):
            return self.check_exist_ingredient(record)
        else:
            return self.check_exist_product(record)

    def check_exist_ingredient(self, ingredient: Ingredient) -> Ingredient:
        pass

    def check_exist_product(self, product: Product) -> Product:
        pass
    
    def make_product(self, id: str, name: str, description: str, url: str, ingredients: list[str], is_en: bool):
        scraped_product = Product()
        scraped_product['id'] = id
        scraped_product['name'] = name
        scraped_product['url'] = url
        scraped_product['ingredients'] = ingredients
        scraped_product['description'] = description
        scraped_product['is_en'] = is_en

        return scraped_product
    
    def make_ingredient(self, id: str, name: str, alias: list[str], document: list[str], safe_for_preg: int, description: str, url: str, is_en: bool):
        scraped_ingredient = Ingredient()
        scraped_ingredient["id"] = id
        scraped_ingredient["name"] = name
        scraped_ingredient["alias"] = alias
        scraped_ingredient["document"] = document
        scraped_ingredient["url"] = url
        scraped_ingredient["description"] = description
        scraped_ingredient["safe_for_preg"] = safe_for_preg
        scraped_ingredient['is_en'] = is_en

        return scraped_ingredient
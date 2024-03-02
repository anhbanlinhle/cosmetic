from typing import Any
from unidecode import unidecode
import scrapy
from scrapy_crawler.db_connector import connector
from scrapy_crawler.db_connector import constants
from scrapy_crawler.items import Product, Ingredient
from scrapy_crawler.es.es_service import ElasticsearchService

from scrapy.http import Request, Response

class BaseSpider(scrapy.Spider):

    es_service_instance = ElasticsearchService()
    INGREDIENT_INDEX = 'test-2'
    PRODUCT_INDEX = 'test-2'

    def start_requests(self):
        pass

    def parse_link(self, response):
        pass

    def parse_product(self, response: Response, **kwargs: Any):
        pass

    def parse_ingredient(self, response: Response, **kwargs: Any):
        pass

    def generate_record_id(self, name):

        normalized_name = unidecode(name, "utf-8")
        result = ""

        for char in normalized_name:
            if 'A' <= char <= 'Z':
                result += chr(ord(char) + 32)
            elif char == ' ':
                if result[len(result) - 1] != '-':
                    result += '-'
            else:
                result += char
        
        return result
    
    def make_final_result(self, record: Ingredient | Product):
        if isinstance(record, Ingredient):
            return self.check_exist_ingredient(record)
        else:
            return self.check_exist_product(record)

    def check_exist_ingredient(self, scraped_ingredient: Ingredient) -> Ingredient:
        full_list_name = scraped_ingredient["alias"]
        full_list_name.append(scraped_ingredient["name"])

        existing_ingre = self.es_service_instance.search_ingredient_in_index(name=full_list_name, index=self.INGREDIENT_INDEX)

        if existing_ingre != None:
            # handle name and alias
            existing_alias = set(existing_ingre["alias"])
            for name_item in full_list_name:
                if name_item != existing_ingre["name"]:
                    existing_alias.add(name_item)

            existing_ingre["alias"] = list(existing_alias)

            # handle document
            existing_ingre["document"] = existing_ingre["document"] + scraped_ingredient["document"]

            # handle description
            if scraped_ingredient.get("description") != None and existing_ingre.get("description") == None:
                existing_ingre["description"] = scraped_ingredient["description"]
            elif scraped_ingredient.get("description") != None and existing_ingre.get("description") != None:
                existing_ingre["description"].update(scraped_ingredient["description"])

            # handle url
            existing_ingre["url"] = existing_ingre["url"] + scraped_ingredient["url"]

            # handle safe_for_preg
            existing_ingre["safe_for_preg"].update(scraped_ingredient["safe_for_preg"])

            return existing_ingre
        
        else:
            return scraped_ingredient

    def check_exist_product(self, product: Product) -> Product:
        return product;
    
    def make_product(self, id: str, name: str, description: str | dict | None, url: str | list[str], ingredients: list[str], is_en: bool):
        scraped_product = Product()
        scraped_product['id'] = id
        scraped_product['name'] = name
        scraped_product['url'] = [url] if isinstance(url, str) else url
        scraped_product['ingredients'] = ingredients
        scraped_product['description'] = { f'{url}': description } if isinstance(description, str) else description
        scraped_product['is_en'] = is_en

        return scraped_product
    
    def make_ingredient(self, id: str, name: str, alias: list[str], document: list[str] | None, 
                        safe_for_preg: int | dict, description: str | dict | None, url: str | list[str], is_en: bool):
        scraped_ingredient = Ingredient()
        scraped_ingredient["id"] = id
        scraped_ingredient["name"] = name
        scraped_ingredient["alias"] = alias
        scraped_ingredient["document"] = document if document != None else []
        scraped_ingredient["url"] = [url] if isinstance(url, str) else url
        scraped_ingredient["description"] = { f'{url}': description } if isinstance(description, str) else description
        scraped_ingredient["safe_for_preg"] = { f'{url}': safe_for_preg } if isinstance(safe_for_preg, int) else safe_for_preg
        scraped_ingredient['is_en'] = is_en

        return scraped_ingredient
from typing import Any
import json
import scrapy
import re
from scrapy.http import Response, TextResponse

from scrapy_crawler.items import Product, Ingredient
from scrapy_crawler.spiders.base_spider import BaseSpider

class CallMeDuySpider(BaseSpider):
    name = 'callmeduy'

    ingredient_current_position = 0
    product_current_position = 0
    record_size = 100
    
    ingredient_api = "https://callmeduy.com/_api/chemicals/search"
    product_api = "https://callmeduy.com/_api/products"

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7,fr-FR;q=0.6,fr;q=0.5",
        "Host": "callmeduy.com",
        "Content-Type": "application/json;charset=UTF-8",
    }

    is_end_ingredient = False
    is_end_product = False

    def start_requests(self):
        while (not self.is_end_ingredient):
            yield scrapy.Request(url=self.ingredient_api, 
                                 method="POST",
                                 body=json.dumps(self.create_ingredient_post_body(start=self.ingredient_current_position, limit=self.record_size)),
                                 headers=self.header,
                                 callback=self.parse_ingredient)
            
            self.ingredient_current_position += self.record_size

        while (not self.is_end_product):
            yield scrapy.Request(url=self.make_product_api_with_param(self.product_current_position, self.record_size), 
                                 method="GET",
                                 headers=self.header,
                                 callback=self.parse_product)
            
            self.product_current_position += self.record_size

    def parse_ingredient(self, response: TextResponse, **kwargs: Any) -> Any:
        response_body = json.loads(response.text)

        if len(response_body) < 1:
            self.is_end_ingredient = True
            return

        for item in response_body:
            name_list = set()
            for name_item in item["names"]:
                if not ('/' in name_item["name"]):
                    name_list.update(self.ingredient_name_clean(name_item["name"].strip()))

            if len(name_list) < 1:
                continue

            name_list = list(name_list)

            scraped_ingredient = self.make_ingredient(id=self.generate_record_id(name_list[0]),
                                                      document=None,
                                                      name=name_list[0],
                                                      alias=name_list[1:],
                                                      url="https://callmeduy.com/thanh-phan",
                                                      description=self.convert_html_to_text(item["description"]) if item["description"] != None else item["description"],
                                                      safe_for_preg=item["safetyLevel"] if item["safetyLevel"] != None else -1,
                                                      spider_name=self.name,
                                                      is_en=False)

            yield self.make_final_result(scraped_ingredient)

    def parse_product(self, response: TextResponse, **kwargs: Any) -> Any:
        response_body = json.loads(response.text)

        if len(response_body) < 1:
            self.is_end_product = True
            return
        
        for item in response_body:
            ingredient_list = []
            for ingredient_item in item["ingredients"]:
                if len(ingredient_item["names"]) > 0:
                    ingredient_list.append(self.ingredient_name_clean_product(ingredient_item["names"][0]["name"]))

            stripped_name = item["name"].strip()
            scraped_product = self.make_product(id=self.generate_record_id(stripped_name),
                                                name=stripped_name,
                                                ingredients=ingredient_list,
                                                description=self.convert_html_to_text(item["description"]) if item["description"] != None else item["description"],
                                                url=response.url,
                                                spider_name=self.name,
                                                is_en=False)

            yield self.make_final_result(scraped_product)
    
    def create_ingredient_post_body(self, start: int, limit: int) -> dict:
        return {
            "_start": start,
            "_limit": limit
        }
    
    def convert_html_to_text(self, html: str) -> str:
        return re.sub(r"<[^>]*>", "", html)
    
    def ingredient_name_clean(self, name: str) -> set:
        name_without_brackets = ''
        name_in_brackets = ''
        in_bracket = False
        out_bracket_position = -2

        other_name = ''

        for index, char in enumerate(name):
            if char == '(':
                in_bracket = True

            if ((not in_bracket) and (out_bracket_position != index - 1)):
                name_without_brackets += char
            elif in_bracket and char != '(' and char != ')':
                name_in_brackets += char

            if char == ')':
                in_bracket = False
                out_bracket_position = index
                other_name += (name_in_brackets + name[(index + 1):]) if index < (len(name) - 1) else name_in_brackets

        result = set()
        result.add(name_without_brackets.strip())
        if other_name != '':
            result.add(other_name.strip())

        return result
    
    def make_product_api_with_param(self, start: int, limit: int) -> str:
        return self.product_api + f"?_start={start}&_limit={limit}&name_contains=&_sort=created_at:DESC"
    
    def ingredient_name_clean_product(self, name: str) -> str:
        name_without_brackets = ''
        in_bracket = False
        out_bracket_position = -2

        for index, char in enumerate(name):
            if char == '(':
                in_bracket = True
            
            if ((not in_bracket) and (out_bracket_position != index - 1)) or \
                ((out_bracket_position == index - 1) and char != ' '):
                name_without_brackets += char

            if char == ')':
                in_bracket = False
                out_bracket_position = index

        result_map = map(str.strip, name_without_brackets.split('/'))

        max_length_item = ''
        for item in result_map:
            if len(item) > len(max_length_item):
                max_length_item = item
        
        return max_length_item


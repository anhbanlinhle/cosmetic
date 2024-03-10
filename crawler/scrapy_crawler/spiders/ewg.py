from typing import Any
import json
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request, Response

from scrapy_crawler.db_connector import connector
from scrapy_crawler.db_connector import constants
from scrapy_crawler.items import Product, Ingredient
from scrapy_crawler.spiders.base_spider import BaseSpider

class EwgSpider(BaseSpider):
    name = 'ewg'

    custom_settings = {
        "DOWNLOAD_DELAY": 0.8
    }

    vowel_list = {'u', 'e', 'o', 'a', 'i', 'y'}

    end_of_product = False
    end_of_ingredient = False

    def start_requests(self):
        website = connector.get_website_with_name(self.name)
        product_url = website.url + website.product_suffix
        ingredient_url = website.url + website.ingredient_suffix

        product_list_x_path = connector.get_content_list_xpath(website_id=website.id, type=constants.PRODUCT)
        ingredient_list_x_path = connector.get_content_list_xpath(website_id=website.id, type=constants.INGREDIENT)

        for vowel in self.vowel_list:
            ingredient_page_num = 1 
            while (not self.end_of_ingredient):
                yield scrapy.Request(url=(ingredient_url + vowel + f'&page={ingredient_page_num}'), 
                                    callback=self.parse_link, 
                                    meta={"domain": website.url, 
                                        "website_id": website.id,
                                        "path": ingredient_list_x_path.path,
                                        "is_product": False})
                ingredient_page_num += 1
            self.end_of_ingredient = False
            
        product_page_num = 1
        while (not self.end_of_product):
            yield scrapy.Request(url=(product_url + str(product_page_num)), 
                                callback=self.parse_link, 
                                meta={"domain": website.url, 
                                    "website_id": website.id,
                                    "path": product_list_x_path.path,
                                    "is_product": True})
            product_page_num += 1

    def parse_link(self, response):
        href_list = response.xpath(response.meta.get("path") + '/@href').getall()
    
        if response.meta.get("is_product") == True:
            if len(href_list) == 0:
                self.end_of_product = True
                return
            
            path = connector.get_product(response.meta.get("website_id"))
            for href in href_list:
                product_url = (response.meta.get("domain") + str(href)) if not href.startswith('http') else href
                yield scrapy.Request(url=product_url, callback=self.parse_product, 
                                    meta={"domain": response.meta.get("domain"), 
                                        "website_id": response.meta.get("website_id"),
                                        "obj_xpath": path})
        else:
            if len(href_list) == 0:
                self.end_of_ingredient = True
                return
            
            path = connector.get_ingredient(response.meta.get("website_id"))
            for href in href_list:
                ingredient_url = (response.meta.get("domain") + str(href)) if not href.startswith('http') else href
                yield scrapy.Request(url=ingredient_url, callback=self.parse_ingredient, 
                                    meta={"domain": response.meta.get("domain"), 
                                        "website_id": response.meta.get("website_id"),
                                        "obj_xpath": path})

    def parse_product(self, response: Response, **kwargs: Any):
        product_xpath = response.meta.get("obj_xpath")

        product_name = response.xpath(product_xpath.name_xpath + "//text()").get().strip()

        description = None

        raw_ingredient_list = response.xpath(product_xpath.x_path_to_ingredient_list + "//text()").get().strip().split(", ")
        ingredient_list = [self.get_name_without_brackets(name=ingre) for ingre in raw_ingredient_list]

        scraped_product = self.make_product(id=self.generate_record_id(product_name),
                                                name=product_name,
                                                ingredients=ingredient_list,
                                                description=description,
                                                url=response.url,
                                                spider_name=self.name,
                                                is_en=True)

        yield self.make_final_result(scraped_product)
    
    def parse_ingredient(self, response: Response, **kwargs: Any):
        ingredient_xpath = response.meta.get("obj_xpath")

        name_dict = json.loads(ingredient_xpath.name_xpath)

        ingredient_name = response.xpath(name_dict["name"] + "//text()").get().strip()
        alias_list = response.xpath(name_dict["alias"] + "//text()").getall()
        aliases = [(alias_list[index].strip())[2:] for index in range(len(alias_list))]

        description = response.xpath(ingredient_xpath.description_xpath + "//text()").get()

        scraped_ingredient = self.make_ingredient(id=self.generate_record_id(ingredient_name),
                                                    document=None,
                                                    name=self.get_name_without_brackets(ingredient_name),
                                                    alias=aliases,
                                                    url=response.url,
                                                    description=description.strip() if description != None else None,
                                                    safe_for_preg=(-1),
                                                    spider_name=self.name,
                                                    is_en=True)

        yield self.make_final_result(scraped_ingredient)

    def get_name_without_brackets(self, name) -> str:
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

        return name_without_brackets.strip()
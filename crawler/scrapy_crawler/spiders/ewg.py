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

    vowel_list = {'u', 'e', 'o', 'a', 'i', 'y'}

    def start_requests(self):
        website = connector.get_website_with_name(self.name)
        product_url = website.url + website.product_suffix
        ingredient_url = website.url + website.ingredient_suffix
        preg_url = website.url + website.preg_suffix
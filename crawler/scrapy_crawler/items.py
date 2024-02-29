# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    ingredients = scrapy.Field()
    is_en = scrapy.Field()

class Ingredient(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    alias = scrapy.Field()
    description = scrapy.Field()
    document = scrapy.Field()
    safe_for_preg = scrapy.Field()
    url = scrapy.Field()
    is_en = scrapy.Field()
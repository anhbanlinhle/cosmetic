from typing import Any
import scrapy
import json
import re
from scrapy_crawler.db_connector import connector
from scrapy_crawler.db_connector import constants
from scrapy_crawler.items import Product, Ingredient
from scrapy_crawler.spiders.base_spider import BaseSpider

from scrapy.http import Request, Response

class IncidecoderSpider(BaseSpider):
    name = 'incidecoder'

    vowel_list = {'u', 'e', 'o', 'a', 'i', 'y'}
    end_of_prod = False

    def start_requests(self):

        website = connector.get_website_with_name(self.name)
        product_url = website.url + website.product_suffix

        product_xpath = connector.get_product(website.id)
        ingredient_xpath = connector.get_ingredient(website.id)

        for vowel in self.vowel_list:
            self.end_of_prod = False
            page_index = 1
            current_url = str(product_url) + vowel + '&page='

            while not self.end_of_prod:
                current_url_with_page = current_url + str(page_index)
                yield scrapy.Request(url=current_url_with_page, 
                                     callback=self.parse_link, 
                                     meta={"domain": website.url, 
                                           "website_id": website.id,
                                           "product_xpath": product_xpath,
                                           "ingredient_xpath": ingredient_xpath})
                page_index += 1
    
    def parse_link(self, response):
        product_list_x_path = connector.get_content_list_xpath(response.meta.get("website_id"), constants.PRODUCT)
        href_list = response.xpath(product_list_x_path.path + '/@href').getall()

        if len(href_list) < 1:
            self.end_of_prod = True
            return

        for href in href_list:
            product_url = response.meta.get("domain") + str(href)
            yield scrapy.Request(url=product_url, 
                                 callback=self.parse_product, 
                                 meta={"domain": response.meta.get("domain"), 
                                       "website_id": response.meta.get("website_id"),
                                       "product_xpath": response.meta.get("product_xpath"),
                                       "ingredient_xpath": response.meta.get("ingredient_xpath")})

    def parse_product(self, response: Response, **kwargs: Any):
        product_xpath = response.meta.get("product_xpath")

        description = response.xpath(product_xpath.description_xpath)
        description_expansion = description.xpath('.//child::*').getall()
        merged_description = ''
        if (len(description_expansion) > 0):
            description_children = description.xpath('.' + product_xpath.description_expand + "/text()").getall()
            for child in description_children:
                merged_description += child.strip()

        ingredient_list = response.xpath(product_xpath.x_path_to_ingredient_list)
        ingredient_list_name = ingredient_list.xpath('./text()').getall()
        ingredient_list_href = ingredient_list.xpath('./@href').getall()

        cleaned_ingredient_list = self.clean_ingredient_list_in_product(ingredient_list_name)

        product_name = response.xpath(product_xpath.brand_xpath + "//text()").get().strip() + " " + response.xpath(product_xpath.name_xpath + "//text()").get().strip()
        product_description = merged_description if len(description_expansion) > 0 else description.xpath('./text()').get().strip()
        product_description = re.sub(r"(?<=[a-zA-Z])[\n\t\r]", " ", product_description)

        scraped_product = self.make_product(id=self.generate_record_id(product_name),
                                                name=product_name,
                                                ingredients=cleaned_ingredient_list,
                                                description=(product_description if product_description != '' else None),
                                                url=response.url,
                                                is_en=True)

        yield self.make_final_result(scraped_product)

        for href in ingredient_list_href:
            yield scrapy.Request(url=(response.meta.get("domain") + href), 
                                 callback=self.parse_ingredient, 
                                 meta={"domain": response.meta.get("domain"),
                                       "website_id": response.meta.get("website_id"),
                                       "product_xpath": response.meta.get("product_xpath"),
                                       "ingredient_xpath": response.meta.get("ingredient_xpath")})


    def parse_ingredient(self, response: Response, **kwargs: Any):
        ingredient_xpath = response.meta.get("ingredient_xpath")

        name_dict = json.loads(ingredient_xpath.name_xpath)

        name_alias_list = set()
        aliases = response.xpath(name_dict["alias"] + "//text()").get()
        if aliases != None:
            alias_list = list(map(str.strip, aliases.split(', ')))
            name_alias_list.update(alias_list)

        description = response.xpath(ingredient_xpath.description_xpath + "//text()").getall()
        document = list(map(str.strip, response.xpath(ingredient_xpath.related_document + "//text()").getall()))

        description_paragraph = ''
        for content in description:
            description_paragraph += (content.strip() + '\n')

        ingredient_name = response.xpath(name_dict["name"] + "//text()").get().strip()
        ingredient_description = re.sub(r"(?<=[a-zA-Z])[\n\t\r]", " ", description_paragraph)

        scraped_ingredient = self.make_ingredient(id=self.generate_record_id(ingredient_name),
                                                    document=document,
                                                    name=ingredient_name,
                                                    alias=list(name_alias_list),
                                                    url=response.url,
                                                    description=(ingredient_description if ingredient_description != '' else None),
                                                    safe_for_preg=(-1),
                                                    is_en=True)

        yield self.make_final_result(scraped_ingredient)

        product_href_list = response.xpath(ingredient_xpath.xpath_to_product_list + '/@href').getall()
        if len(product_href_list) > 0:
            for href in product_href_list:
                yield scrapy.Request(url=(response.meta.get("domain") + href), 
                                     callback=self.parse_product, 
                                     meta={"domain": response.meta.get("domain"),
                                           "website_id": response.meta.get("website_id"),
                                           "product_xpath": response.meta.get("product_xpath"),
                                           "ingredient_xpath": response.meta.get("ingredient_xpath")})
                
            yield scrapy.Request(url=(response.meta.get("domain") + href + "?uoffset=1"), 
                                     callback=self.parse_product_list_from_ingredient, 
                                     meta={"domain": response.meta.get("domain"),
                                           "website_id": response.meta.get("website_id"),
                                           "path_to_products": ingredient_xpath.xpath_to_product_list,
                                           "product_xpath": response.meta.get("product_xpath"),
                                           "ingredient_xpath": response.meta.get("ingredient_xpath")})

    def parse_product_list_from_ingredient(self, response: Response, **kwargs: Any):

        product_href_list = response.xpath(response.meta.get("path_to_products") + '/@href').getall()
        for href in product_href_list:
            yield scrapy.Request(url=(response.meta.get("domain") + href), 
                                     callback=self.parse_product, 
                                     meta={"domain": response.meta.get("domain"),
                                           "website_id": response.meta.get("website_id"),
                                           "product_xpath": response.meta.get("product_xpath"),
                                           "ingredient_xpath": response.meta.get("ingredient_xpath")})

        next_page = response.xpath('//a[contains(text(), "Next page")]/@href').get()
        if next_page != None:
            yield scrapy.Request(url=(response.meta.get("domain") + next_page), 
                                     callback=self.parse_product_list_from_ingredient, 
                                     meta={"domain": response.meta.get("domain"),
                                           "website_id": response.meta.get("website_id"),
                                           "product_xpath": response.meta.get("product_xpath"),
                                           "ingredient_xpath": response.meta.get("ingredient_xpath")})
            
    def clean_ingredient_list_in_product(self, name_list: list):
        result = []

        for ingredient_name in name_list:
            name_without_brackets = ''
            in_bracket = False
            out_bracket_position = -2
            
            for index, char in enumerate(ingredient_name):
                if char == '(':
                    in_bracket = True
                
                if ((not in_bracket) and (out_bracket_position != index - 1)) or \
                    ((out_bracket_position == index - 1) and char != ' '):
                    name_without_brackets += char

                if char == ')':
                    in_bracket = False
                    out_bracket_position = index

            result.append(name_without_brackets)

        return result
from typing import Any
import json
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request, Response

from scrapy_crawler.db_connector import connector
from scrapy_crawler.db_connector import constants
from scrapy_crawler.items import Product, Ingredient
from scrapy_crawler.spiders.base_spider import BaseSpider

class GuoSpider(BaseSpider):
    name = 'guo'

    preg_safe_mapping = {
        "mức độ nguy hại (cao)": 3,
        "mức độ nguy hại (trung bình)": 2,
        "mức độ nguy hại (thấp)": 1,
        "tương đối an toàn": 0
    }

    def start_requests(self):
        website = connector.get_website_with_name(self.name)
        product_url = website.url + website.product_suffix
        ingredient_url = website.url + website.ingredient_suffix
        preg_url = website.url + website.preg_suffix
        
        preg_list_x_path = connector.get_content_list_xpath(website_id=website.id, type=constants.PREG)
        product_list_x_path = connector.get_content_list_xpath(website_id=website.id, type=constants.PRODUCT)
        ingredient_list_x_path = connector.get_content_list_xpath(website_id=website.id, type=constants.INGREDIENT)

        yield scrapy.Request(url=preg_url, 
                             callback=self.parse_ingredient_preg, 
                             meta={"domain": website.url, 
                                   "website_id": website.id,
                                   "path": preg_list_x_path.path})

        yield scrapy.Request(url=product_url, 
                             callback=self.parse_link, 
                             meta={"domain": website.url, 
                                   "website_id": website.id,
                                   "path": product_list_x_path.path,
                                   "is_product": True})

        yield scrapy.Request(url=ingredient_url, 
                             callback=self.parse_link, 
                             meta={"domain": website.url, 
                                   "website_id": website.id,
                                   "path": ingredient_list_x_path.path,
                                   "is_product": False})
    
    def parse_link(self, response):
        href_list = response.xpath(response.meta.get("path") + '/@href').getall()
        
        if response.meta.get("is_product") == True:
            path = connector.get_product(response.meta.get("website_id"))
            for href in href_list:
                product_url = (response.meta.get("domain") + str(href)) if not href.startswith('http') else href
                yield scrapy.Request(url=product_url, callback=self.parse_product, 
                                    meta={"domain": response.meta.get("domain"), 
                                        "website_id": response.meta.get("website_id"),
                                        "obj_xpath": path})
        else:
            path = connector.get_ingredient(response.meta.get("website_id"))
            for href in href_list:
                ingredient_url = (response.meta.get("domain") + str(href)) if not href.startswith('http') else href
                yield scrapy.Request(url=ingredient_url, callback=self.parse_ingredient, 
                                    meta={"domain": response.meta.get("domain"), 
                                        "website_id": response.meta.get("website_id"),
                                        "obj_xpath": path})
        
    def parse_ingredient_preg(self, response: Response, **kwargs: Any):
        preg_ingredient_list = response.xpath(response.meta.get("path")).getall()

        for index, html_str in enumerate(preg_ingredient_list) :
            selector = Selector(text=html_str)
            single_item_list = selector.xpath(".//text()").getall()
            
            preg_safe = 0
            if index == 0:
                preg_safe = 3
            elif index == 1:
                preg_safe = 2
            elif index == 2:
                preg_safe = 1

            for item in single_item_list:
                name = item.strip()
                if name == '':
                    continue

                name_list = self.preg_phase_name_clean(name)

                ingredient = Ingredient()
                ingredient['name'] = name_list[0]
                ingredient['alias'] = name_list[1:]
                ingredient['safe_for_preg'] = preg_safe
                yield ingredient

    def parse_product(self, response: Response, **kwargs: Any):
        product_xpath = response.meta.get("obj_xpath")
        description = response.xpath(product_xpath.description_xpath + "//text()").getall()

        merged_description = ''
        if len(description) > 0:
            for des in description:
                merged_description += des
            merged_description.strip()
        
        ingredient_list = response.xpath(product_xpath.x_path_to_ingredient_list + "//text()").get().strip()

        scraped_product = Product()
        scraped_product['name'] = response.xpath(product_xpath.name_xpath + "//text()").get().strip()
        scraped_product['url'] = response.url
        scraped_product['ingredients'] = ingredient_list.split(", ")
        scraped_product['ingredients'][len(scraped_product['ingredients']) - 1] = scraped_product['ingredients'][len(scraped_product['ingredients']) - 1].replace(".", "")
        scraped_product['description'] = merged_description
        scraped_product['is_en'] = False

        yield scraped_product

    def parse_ingredient(self, response: Response, **kwargs: Any):
        ingredient_xpath = response.meta.get("obj_xpath")

        name = response.xpath(ingredient_xpath.name_xpath + "//text()").get()
        if name == None:
            return
        
        description_json = json.loads(ingredient_xpath.description_xpath)
        safe_for_preg = response.xpath(description_json['safe_for_preg']).get()
        description = response.xpath(description_json['description']).get()

        safe_for_preg = self.preg_safe_mapping.get((safe_for_preg.strip()).lower()) if safe_for_preg != None else -1

        name_list = self.ingredient_phase_name_clean(name.strip())

        scraped_ingredient = Ingredient()
        scraped_ingredient["name"] = name_list[0]
        scraped_ingredient["id"] = self.generate_record_id(scraped_ingredient["name"])
        scraped_ingredient["alias"] = name_list[1:]
        scraped_ingredient["url"] = response.url
        scraped_ingredient["description"] = description if description != None else ""
        scraped_ingredient["safe_for_preg"] = safe_for_preg if safe_for_preg != None else -1
        scraped_ingredient['is_en'] = False
        
        yield scraped_ingredient

        ingredient_navigate = response.xpath('//body//*[contains(@id, "nav")]//a[contains(@href, "/thanh-phan")]/@href').getall()
        for href in ingredient_navigate:
            navigate_url = (response.meta.get("domain") + str(href)) if href.startswith('/thanh-phan') else href
            yield scrapy.Request(url=navigate_url, callback=self.parse_ingredient, 
                                meta={"domain": response.meta.get("domain"), 
                                    "website_id": response.meta.get("website_id"),
                                    "obj_xpath": response.meta.get("obj_xpath")})
    
    def ingredient_phase_name_clean(self, name: str) -> list[str]:
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

        return list(map(str.strip, name_without_brackets.split('/')))
    
    def preg_phase_name_clean(self, name: str) -> list[str]:
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

        result = [name_without_brackets.strip()]
        if other_name != '':
            result.append(other_name.strip())
        return result
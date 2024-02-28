class Website:
    def __init__(self, id: int, url: str, product_suffix: str, ingredient_suffix: str, preg_suffix: str):
        self.id = id
        self.url = url
        self.product_suffix = product_suffix
        self.ingredient_suffix = ingredient_suffix
        self.preg_suffix = preg_suffix

class ContentListXpath:
    def __init__(self, id: int, website_id: str, type: str, path: str):
        self.id = id
        self.website_id = website_id
        self.type = type
        self.path = path

class Product:
    def __init__(self, id: int, 
                 website_id: str, 
                 brand_xpath: str, 
                 name_xpath: str, 
                 description_xpath: str,
                 x_path_to_ingredient_list: str,
                 description_expand: str):
        self.id = id
        self.website_id = website_id
        self.brand_xpath = brand_xpath
        self.name_xpath = name_xpath
        self.description_xpath = description_xpath
        self.x_path_to_ingredient_list = x_path_to_ingredient_list
        self.description_expand = description_expand

class Ingredient:
    def __init__(self, id: int, website_id: str, name_xpath: str, description_xpath: str, related_document: str, xpath_to_product_list: str):
        self.id = id
        self.website_id = website_id
        self.name_xpath = name_xpath
        self.description_xpath = description_xpath
        self.related_document = related_document
        self.xpath_to_product_list = xpath_to_product_list
import mysql.connector
import os
from . import table
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')
PORT = os.getenv('PORT')

db = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE,
    port=PORT
)
cursor = db.cursor()

def get_website_with_name(name: str) -> table.Website:
    cursor.execute('SELECT * FROM website WHERE url LIKE %s', ('%' + name + '%',))
    result = cursor.fetchone()
    return table.Website(result[0], result[1], result[2], result[3], result[4])

def get_content_list_xpath(website_id: int, type: str) -> table.ContentListXpath:
    cursor.execute(f'SELECT * FROM content_list_xpath WHERE website_id = {website_id} AND type = {type}')
    result = cursor.fetchone()
    return table.ContentListXpath(result[0], result[1], result[2], result[3])

def get_product(website_id: int) -> table.Product:
    cursor.execute(f'SELECT * FROM product WHERE website_id = {website_id}')
    result = cursor.fetchone()
    return table.Product(result[0], result[1], result[2], result[3], result[4], result[5], result[6])

def get_ingredient(website_id: int) -> table.Ingredient:
    cursor.execute(f'SELECT * FROM ingredient WHERE website_id = {website_id}')
    result = cursor.fetchone()
    return table.Ingredient(result[0], result[1], result[2], result[3], result[4], result[5])

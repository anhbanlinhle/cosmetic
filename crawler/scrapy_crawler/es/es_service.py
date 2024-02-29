from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

from items import Product, Ingredient

load_dotenv()

ADDRESS = os.getenv('ELASTICSEARCH_ADDRESS')
USER = os.getenv('ELASTICSEARCH_USER')
PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')

class ElasticsearchService:

    client = Elasticsearch(
        ADDRESS,
        basic_auth=(USER, PASSWORD)
    )

    def search_ingredient_in_index(self, name: str | list[str], index: str) -> Ingredient:
        if name == None or index == None:
            raise Exception("name and index must not be null")

        query = {
            "bool": {
                "should": []
            }
        }

        if isinstance(name, str):
            query["bool"]["should"].append(self.generate_multi_match_query(name))
        else:
            for single_name in name:
                query["bool"]["should"].append(self.generate_multi_match_query(single_name))

        res = self.client.search(
            index=index, 
            query=query,
            source_excludes=[ "@version", "event", "@timestamp" ],
            sort=[{ "@timestamp" : "asc" }]
        )
        
        if len(res["hits"]["hits"]) > 0:
            return res["hits"]["hits"][0]["_source"]
        else:
            return None

    def generate_multi_match_query(self, name: str) -> dict:
        return {
            "multi_match": {
                "query": name,
                "fields": ["name", "alias"],
                "type": "phrase"
            }
        }

from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

from scrapy_crawler.items import Product, Ingredient

load_dotenv()

ADDRESS = os.getenv('ELASTICSEARCH_ADDRESS')
USER = os.getenv('ELASTICSEARCH_USER')
PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')

class ElasticsearchService:

    client = Elasticsearch(
        ADDRESS,
        basic_auth=(USER, PASSWORD)
    )

    def match_phrase_ingredient_in_index(self, name: str | list[str], index: str) -> Ingredient:
        if name == None or index == None:
            raise Exception("name and index must not be null")

        query = {
            "bool": {
                "should": []
            }
        }

        if isinstance(name, str):
            query["bool"]["should"].append(self._generate_ingredient_multi_match_query(name))
        else:
            for single_name in name:
                query["bool"]["should"].append(self._generate_ingredient_multi_match_query(single_name))

        res = self.client.search(
            index=index, 
            query=query,
            source_excludes=[ "@version", "event", "@timestamp" ],
            sort=[{ "_score": "desc", "@timestamp" : "asc" }]
        )
        
        if len(res["hits"]["hits"]) > 0:
            return res["hits"]["hits"][0]["_source"]
        else:
            return None

    def exact_match_ingredient_in_index(self, name: str | list[str], index: str) -> Ingredient:
        if name == None or index == None:
            raise Exception("name and index must not be null")

        query = {
            "bool": {
                "should": []
            }
        }

        query["bool"]["should"] = query["bool"]["should"] + self._generate_ingredient_keyword_query(name=name)
                
        res = self.client.search(
            index=index, 
            query=query,
            source_excludes=[ "@version", "event", "@timestamp" ],
            sort=[{ "_score": "desc", "@timestamp" : "asc" }]
        )
        
        if len(res["hits"]["hits"]) > 0:
            return res["hits"]["hits"][0]["_source"]
        else:
            return None

    def exact_match_product_in_index(self, name: str, index: str) -> Ingredient:
        if name == None or index == None:
            raise Exception("name and index must not be null")

        query = {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "alias.keyword": str.lower(name)
                        }
                    }
                ]
            }
        }
                
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

    def _generate_ingredient_multi_match_query(self, name: str) -> dict:
        return {
            "multi_match": {
                "query": name,
                "fields": ["name", "alias"],
                "type": "phrase"
            }
        }

    def _generate_ingredient_keyword_query(self, name: str | list[str]) -> list[dict]:
        if isinstance(name, str):
            return self._generate_keyword_term_name_alias(name=name)
        else:
            result = []
            for single_name in name:
                result = result + self._generate_keyword_term_name_alias(name=single_name)

            return result

    def _generate_keyword_term_name_alias(self, name: str):
        lowercased_name = str.lower(name)
        return [
            {
                "term": {
                    "alias.keyword": lowercased_name
                }
            },
            {
                "term": {
                    "name.keyword": lowercased_name
                }
            }
        ]
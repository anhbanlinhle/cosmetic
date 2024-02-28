# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from kafka import KafkaProducer
import json
from . import items

class CosmeticPipeline:

    def open_spider(self, spider):
            
        self.producer = KafkaProducer(bootstrap_servers=['localhost:29092'], 
                                      value_serializer=lambda x: json.dumps(x).encode('utf-8'))
        self.topic_product = 'product' 
        self.topic_ingredient = 'ingredient'

    def close_spider(self, spider):
        self.producer.close()

    def process_item(self, item, spider):
        msg = ItemAdapter(item).asdict()

        if isinstance(item, items.Product):
            self.producer.send(self.topic_product, value=msg)
        else:    
            self.producer.send(self.topic_ingredient, value=msg)

        self.producer.flush()
        return item

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JmggItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    project_code = scrapy.Field()
    price = scrapy.Field()
    deadline = scrapy.Field()
    client = scrapy.Field()
    agent = scrapy.Field()
    area = scrapy.Field()
    last_updated = scrapy.Field()

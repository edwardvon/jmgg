# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from main.models import Requestments


# class JmggItem(scrapy.Item):
#     # define the fields for your item here like:
#     name = scrapy.Field()
#     project_code = scrapy.Field()
#     price = scrapy.Field()
#     deadline = scrapy.Field()
#     client = scrapy.Field()
#     agent = scrapy.Field()
#     area = scrapy.Field()
#     pubdate = scrapy.Field()
#     url = scrapy.Field()
#     pdf = scrapy.Field()

class JmggItem(DjangoItem):
    django_model = Requestments

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PapercollectingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class PaperItem(scrapy.Item):
    title = scrapy.Field()
    authors = scrapy.Field()
    abstract = scrapy.Field()
    pdf_href = scrapy.Field()
    arxiv_id = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    subject = scrapy.Field()
    date_line = scrapy.Field()
    
    
class ACMProceeding(scrapy.Item):
    name = scrapy.Field()
    href = scrapy.Field()
    citation_id = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
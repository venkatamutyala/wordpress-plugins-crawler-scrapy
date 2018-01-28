# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class WordpressItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    active_versions = scrapy.Field()
    download_history = scrapy.Field()
    download_history_summary = scrapy.Field()
    active_installs_growth = scrapy.Field()
    various_details = scrapy.Field()
    reviews = scrapy.Field()
    scrapy_item_version = scrapy.Field()
    scrapy_item_creation_epoch_timestamp = scrapy.Field()
    scrapy_item_creation_epoch_date = scrapy.Field()
    scrapy_item_creation_date = scrapy.Field()
    pass

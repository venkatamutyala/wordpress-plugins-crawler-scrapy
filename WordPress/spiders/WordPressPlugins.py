# -*- coding: utf-8 -*-
import scrapy
from WordPress.items import WordpressItem
import re
import json
import datetime


class WordpresspluginsSpider(scrapy.Spider):
    name = 'WordPressPlugins'
    allowed_domains = ['wordpress.org']
    URI_SEARCH_PLUGIN = "https://wordpress.org/plugins/page/{}/?s"
    start_urls = [URI_SEARCH_PLUGIN.format(1)]

    URI_REVIEWS = "https://wordpress.org/support/plugin/{}/reviews/page/{}"
    URI_ACTIVE_VERSIONS = "https://api.wordpress.org/stats/plugin/1.0/?slug={}"
    URI_DOWNLOAD_HISTORY = "https://api.wordpress.org/stats/plugin/1.0/downloads.php?slug={}"
    URI_DOWNLOAD_SUMMARY = "https://api.wordpress.org/stats/plugin/1.0/downloads.php?slug={}&historical_summary=1"
    URI_ACTIVE_INSTALLS_GROWTH = "https://api.wordpress.org/stats/plugin/1.0/active-installs.php?slug={}"
    URI_HOME_PAGE_ADVANCED = "https://wordpress.org/plugins/{}/advanced/"

    def parse(self, response):
        get_next_page = response.css('#main > nav > div > a.next.page-numbers::attr(href)').extract_first()
        plugin_urls = response.css('article > div.entry > header > h2 > a::attr(href)').extract()

        for plugin_url in plugin_urls:
            slug = self.get_plugin_name(plugin_url)
            request = scrapy.Request(url=self.URI_ACTIVE_VERSIONS.format(slug), callback=self.parse_active_versions)
            current_time = datetime.datetime.utcnow()
            request = self.set_request_with_item(request, WordpressItem(name=slug, scrapy_item_version="0.1.0",
                                                                        scrapy_item_creation_epoch_timestamp=int((
                                                                                                                         current_time - datetime.datetime(
                                                                                                                     1970,
                                                                                                                     1,
                                                                                                                     1)).total_seconds()),
                                                                        scrapy_item_creation_epoch_date=int((
                                                                                                                    datetime.datetime(
                                                                                                                        current_time.year,
                                                                                                                        current_time.month,
                                                                                                                        current_time.day) - datetime.datetime(
                                                                                                                1970,
                                                                                                                1,
                                                                                                                1)).total_seconds()),
                                                                        scrapy_item_creation_date=current_time.strftime(
                                                                            '%Y-%m-%d')))
            yield request

        if get_next_page:
            yield scrapy.Request(url=get_next_page, callback=self.parse)

        pass

    def parse_active_versions(self, response):
        plugin_data = self.get_item(response)
        plugin_data['active_versions'] = self.get_json(response.text)
        request = scrapy.Request(url=self.URI_DOWNLOAD_SUMMARY.format(plugin_data['name']),
                                 callback=self.parse_download_summary)
        request = self.set_request_with_item(request, plugin_data)
        yield request

    def parse_active_installs_growth(self, response):
        plugin_data = self.get_item(response)
        plugin_data['active_installs_growth'] = self.get_json(response.text)
        request = scrapy.Request(url=self.URI_HOME_PAGE_ADVANCED.format(plugin_data['name']),
                                 callback=self.parse_advanced)
        request = self.set_request_with_item(request, plugin_data)
        yield request

    def parse_advanced(self, response):
        plugin_data = self.get_item(response)

        various_details = {}

        stats = response.css('div.widget.plugin-meta > ul > li')
        for stat in stats:
            key = re.sub('\s+', '', stat.css('li::text').extract_first()).replace(':', '').lower()
            value = stat.css('strong::text').extract_first()
            if "lastupdated" in key:
                value = stat.css('span::text').extract_first()
            if value:
                various_details[key] = value

        languages = response.css('#popover-languages > div.popover-inner > p:nth-child(1) > a::text').extract()
        tags = response.css(
            '#post-164 > div.entry-meta > div.widget.plugin-meta > ul > li.clear > div > a::text').extract()

        various_details['languages'] = languages
        various_details['tags'] = tags

        plugin_data['various_details'] = various_details

        request = scrapy.Request(url=self.URI_REVIEWS.format(plugin_data['name'], 1), callback=self.parse_reviews)
        request = self.set_request_with_item(request, plugin_data)

        yield request

    def parse_reviews(self, response):

        plugin_data = self.get_item(response)

        if 'reviews' not in plugin_data:
            plugin_data['reviews'] = []

        review_urls = response.css('.bbp-topic-permalink::attr(href)').extract()
        for review_url in review_urls:
            request = scrapy.Request(url=review_url, callback=self.parse_single_review)
            request = self.set_request_with_item(request, plugin_data)
            yield request

        get_next_page = response.css('a.next.page-numbers::attr(href)').extract_first()

        if get_next_page:
            request = scrapy.Request(url=get_next_page, callback=self.parse_reviews)
            request = self.set_request_with_item(request, plugin_data)
            yield request
        else:
            request = scrapy.Request(url=self.URI_DOWNLOAD_HISTORY.format(plugin_data['name']),
                                     callback=self.parse_downloads)
            request = self.set_request_with_item(request, plugin_data)
            yield request

    def parse_single_review(self, response):
        plugin_data = self.get_item(response)

        review_details = {}
        review_details['review_title'] = response.css('#main > div.entry-content > header > h1::text').extract_first()
        review_details['content'] = response.css('div.bbp-topic-content').extract_first()
        review_details['author'] = response.css('div.bbp-topic-author > a.bbp-author-name::text').extract_first()
        review_details['review_age'] = response.css('p.bbp-topic-post-date > a::text').extract_first()
        review_details['wordpress_version'] = response.xpath(
            '//*[@id="main"]/div[2]/div[2]/ul/li[6]/text()').extract_first()
        review_details['reply_count'] = response.css('li.reply-count::text').extract_first()
        review_details['participant_count'] = response.css('ul > li.voice-count::text').extract_first()
        review_details['rating'] = str(
            re.search('title=".*" ', response.css('#bbpress-forums > div.wporg-ratings').extract_first())).replace(
            'title="', '').replace('"', '').strip()
        review_details['replies'] = {}

        plugin_data['reviews'].append(review_details)

    def parse_downloads(self, response):
        plugin_data = self.get_item(response)
        plugin_data['download_history'] = self.get_json(response.text)

        yield plugin_data

    def parse_download_summary(self, response):
        plugin_data = self.get_item(response)
        plugin_data['download_history_summary'] = self.get_json(response.text)
        request = scrapy.Request(url=self.URI_ACTIVE_INSTALLS_GROWTH.format(plugin_data['name']),
                                 callback=self.parse_active_installs_growth)
        request = self.set_request_with_item(request, plugin_data)
        yield request

    def get_item(self, response):
        item = response.meta['item']
        return item

    def set_request_with_item(self, request, item):
        request.meta['item'] = item
        return request

    def get_plugin_name(self, plugin_url):
        # https://wordpress.org/plugins/wp-super-cache/
        slug = plugin_url.split('/')[4]  ##wp-super-cache
        return slug

    def get_json(self, string_payload):
        try:
            return json.loads(string_payload)
        except ValueError:
            return {}

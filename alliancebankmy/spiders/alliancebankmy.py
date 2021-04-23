import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from alliancebankmy.items import Article


class alliancebankmySpider(scrapy.Spider):
    name = 'alliancebankmy'
    start_urls = ['https://www.alliancebank.com.my/corporate/media-centre.aspx']

    def parse(self, response):
        links = response.xpath('//a[@class="primary-btn btn-details after-icon-arrow"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="NewsBody"]//strong/text()').get() or response.xpath(
            '//div[@class="has-padding news-body"]//b/text()').get()
        if date:
            date = " ".join(date.split()[-3:])

        content = response.xpath('//div[@class="NewsBody"]//text()').getall() or response.xpath(
            '//div[@class="has-padding news-body"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

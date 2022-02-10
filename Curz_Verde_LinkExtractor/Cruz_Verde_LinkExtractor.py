# In this example the links aren't inside "a tags", they are inside a
# class attribute. So it may be possible to explain the functionality
# of LinkExtractor()

from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess


class Pharmacy(Item):
    item = Field()
    price = Field()

class CruzVerde(CrawlSpider):
    name = 'Pharmacy'
    custom_settings = {'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/80.0.3987.132 Safari/537.36'}

    allowed_domains = ['cruzverde.cl']
    start_urls = ['https://www.cruzverde.cl/medicamentos/']
    download_delay = 1

    rules = (
        # Pharmacy Articles Paging (H)
        Rule(
            LinkExtractor(allow=r'start=',
                          tags=('a', 'button'),
                          attrs=('href', 'data-url')),
            # Note: Explaining LinkExtractor Functionality: It searches
            #       through the html tree, looking for a tags (that are
            #       commonly used for links.
            follow=True,
            callback='parse_pharmacy'),)

    def parse_pharmacy(self, response):
        sel = Selector(response)
        articles = sel.xpath('//div[@class="product product-wrapper"]')

        for article in articles:
            item = ItemLoader(Pharmacy(), article)

            item.add_xpath('item', './/a[@class="link"]/text()')
            item.add_xpath('price', './/span[contains(@class,"value")]/text()')

            yield item.load_item()


# To run without terminal
# This is equivalent to write in terminal:
# scrapy runspider file_name -o results.ext -t ext
process = CrawlerProcess(settings={
    "FEEDS": {"CruzVerde.json": {"format": "json"},
              },
})

process.crawl(CruzVerde)
process.start()  # the script will block here until the crawling is finished

# PENDING TASK: To clean data and gives a good structure
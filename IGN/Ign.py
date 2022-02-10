# Scraping through tabs
from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess

class News(Item):
    title = Field()
    content = Field()

class Reviews(Item):
    title = Field()
    ranking = Field()

class Videos(Item):
    title = Field()
    published_day = Field()

class IGNCrawler(CrawlSpider):
    name = 'ign'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/80.0.3987.132 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT': 30  # Number of pages to 'flip'
    }
    allowed_domains = ['latam.ign.com']
    download_delay = 1
    start_urls = ['https://latam.ign.com/se/?model=article&q=switch&order_by=-date']

    rules = (
        #   Switch tab
        Rule(
            LinkExtractor(
                allow=r'type='
            ), follow='True'
        ),
        #   Paging
        Rule(
            LinkExtractor(
                allow=r'&page=\d+'
            ), follow='True'
        ),

        #   One rule for each tab to parse
        #   Reviews
        Rule(
            LinkExtractor(
                allow=r'/review/'
            ), follow='True', callback='parse_reviews'
        ),
        #   Videos
        Rule(
            LinkExtractor(
                allow=r'/video/'
            ), follow='True', callback='parse_videos'
        ),
        #   News
        Rule(
            LinkExtractor(
                allow=r'/news/'
            ), follow='True', callback='parse_news'
        )
    )

    def limpiar_texto(self, texto):
        texto_nuevo = texto.replace('\n', '').replace('\t', '').replace('\r', '').strip()
        return texto_nuevo

    def parse_news(self, response):
        item = ItemLoader(News(), response)
        item.add_xpath('title', '//h1/text()')
        #                                           Perro trucazo
        item.add_xpath('content', '//div[@id="id_text"]//*/text()', MapCompose(self.limpiar_texto))
                                    # to access into anything inside div[@id="id_text"]
        yield item.load_item()

    def parse_reviews(self, response):
        item = ItemLoader(Reviews(), response)
        item.add_xpath('title', '//h1/text()')
        item.add_xpath('ranking', '(//span[@class="side-wrapper side-wrapper hexagon-content"])[1]' +
                                  '/text()')
                        # Note:
                        # @class="nameclass", It Searches for the
                        # exact name, if the found element has an
                        # extra character, it is not taken into account
        yield item.load_item()

    def parse_videos(self, response):
        item = ItemLoader(Videos(), response)
        item.add_xpath('title', '//h1/text()')
        item.add_xpath('published_day', '//span[@class="publish-date"]/text()')
        yield item.load_item()


# To run without terminal
# This is equivalent to write in terminal:
# scrapy runspider file_name -o results.ext -t ext
process = CrawlerProcess(settings={
    "FEEDS": {
        "Ign.json": {"format": "json"},
    },
})

process.crawl(IGNCrawler)
process.start()  # the script will block here until the crawling is finished

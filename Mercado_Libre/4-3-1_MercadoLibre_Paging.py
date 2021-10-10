# This excercise is for practicing paging with scrapy and
# to adding the paging rules

from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess


class Article(Item):
    title = Field()
    price = Field()
    specifications = Field()
    description = Field()
    image = Field()


class MercadoLibreCrawler(CrawlSpider):
    name = 'mercadoLibre'
    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/80.0.3987.132 Safari/537.36",
        'CLOSESPIDER_PAGECOUNT': 20  # Number of pages to 'flip'
    }

    download_delay = 1
    allowed_domains = ["listado.mercadolibre.com.mx",
                       "articulo.mercadolibre.com.mx",
                       "computacion.mercadolibre.com.mx"]
    start_urls = ["https://listado.mercadolibre.com.mx/"
                  "carcasa-toshiba-satellite-s855d"
                  "#D[A:carcasa%20toshiba%20satellite%20s855d]"]
    rules = (
        # Paging
        Rule(
            LinkExtractor(allow=r'_Desde_'),
            follow=True),
        # Product Details
        Rule(
            LinkExtractor(allow=r'/MLM-'),
            follow=True,
            callback='parse_items')
    )

    def cleanText(self, texto):
        resultado = texto.replace('\n', '').replace('\r', '').replace('\t', '').strip()
        # strip() delete spaces at the start of the text, and at the end of it.
        return resultado

    def parse_items(self, response):
        item = ItemLoader(Article(), response)
        # 'response' is used because there won't be there any iterations inside the parser

        item.add_xpath('title', '//h1/text()')
        # item.add_xpath('specifications', '')
        item.add_xpath('description',
                       "//p[contains(@class, 'description_')]/text()",
                       MapCompose(self.cleanText))
        item.add_xpath('price', '//span[@class="price-tag-fraction"]/text()')
        # item.add_value('image', response.xpath('//img[@srcset and @data-zoom]/@srcset/text()').extract)

        yield item.load_item()


# To run without terminal
# This is equivalent to write in terminal:
# scrapy runspider file_name -o results.ext -t ext

process = CrawlerProcess(settings={
    "FEEDS": {
        "4-3-1_MercadoLibre_Paging.json": {"format": "json"},
    },
})

process.crawl(MercadoLibreCrawler)
process.start()  # the script will block here until the crawling is finished

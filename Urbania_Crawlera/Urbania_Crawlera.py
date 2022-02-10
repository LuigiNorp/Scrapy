# Ejercicio incompleto: Crawlera ya no existe ahora es zyte y pide una tarjeta
#                       por adelantado, no conviene de momento

from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
from random import randint

class Departamento(Item):
    nombre = Field()
    direccion = Field()

class Urbaniape(CrawlSpider):
    name = "Departamentos"
    custom_settings = {'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/80.0.3987.132 Safari/537.36'}

    start_urls = ['https://urbania.pe/buscar/proyectos-departamentos?page=1',
                  'https://urbania.pe/buscar/proyectos-departamentos?page=2',
                  'https://urbania.pe/buscar/proyectos-departamentos?page=3',
                  'https://urbania.pe/buscar/proyectos-departamentos?page=4',
                  'https://urbania.pe/buscar/proyectos-departamentos?page=5']

    allowed_domains = ['urbania.pe']
    download_delay = randint(1, 3)

    rules = (
        Rule(
            LinkExtractor(allow=r'/proyecto-'),
            follow=True,
            callback='parse_depa'),)

    def parse_depa(self, response):
        sel = Selector(response)
        item = ItemLoader(Departamento(), sel)

        item.add_xpath('nombre', '(//h2)[1]/text()')
        item.add_xpath('direccion', '//h1/text()')

        yield item.load_item()


# To run without terminal
process = CrawlerProcess(settings={
    "FEEDS": {"Urbania_Crawlera.json": {"format": "json"},},})
process.crawl(Urbaniape)
process.start()  # the script will block here until the crawling is finished

# Deep Extraction (2 Lv). Extracting the Hotel, Opinions and [data of the
# people who made them.] <- Second level, because it means to go into the
# Extracting data opinions from users profiles

# Removing duplications

from scrapy.item import Field, Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess


class Opinion(Item):
    title = Field()
    ranking = Field()
    content = Field()
    autor = Field()


class TripAdvisor(CrawlSpider):
    name = 'OpinionsTripAdvisor'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.132 Safari/537.36',

        'CLOSESPIDER_PAGECOUNT': 100
    }
    allowed_domains = ['tripadvisor.com']
    start_urls = ['https://www.tripadvisor.com/'
                  'Hotels-g150800-Mexico_City_Central_Mexico_and_Gulf_Coast-Hotels.html']
    download_delay = 1

    rules = (
        # Hotel Paging (H)
        Rule(
            LinkExtractor(allow=r'-oa\d+-'),
            follow=True
            ),
        # Hotel Details (V)
        Rule(
            LinkExtractor(
                allow=r'/Hotel_Review-',
                restrict_xpaths=[
                    '//div[@id="taplc_hsx_hotel_list_lite_dusty_hotels_combined_sponsored_0"]'
                    '//a[@data-clicksource="HotelName"]']),
            follow=True
            ),
        # Hotel's Opinions Paging (H)
        Rule(
            LinkExtractor(allow=r'-or\d+-'),
            follow=True
            ),
        # User Profile Details (V)
        Rule(
            LinkExtractor(
                allow=r'/Profile/',
                restrict_xpaths=['//div[@data-test-target="reviews-tab"]'
                                 '//a[contains(@class,"ui_header_link")]']
                          ),
            follow=True,
            callback='parse_opinion'
            ),
            )

    def getRanking(self, texto):
        ranking = texto.split('_')[-1]
        return ranking

    def parse_opinion(self, response):
        sel = Selector(response)
        opinions = sel.xpath('//div[@id="content"]/div/div')
        autor = sel.xpath('(//h1/span)[1]/text()').get()  # .get() - Is used to obtain the
        #          value of the expression
        for opinion in opinions:
            item = ItemLoader(Opinion(), opinion)
            item.add_value('autor', autor)
            item.add_xpath('title', './/div[@class="_3IEJ3tAK _2K4zZcBv"]/text()')
            item.add_xpath('content', './/q/text()')
            item.add_xpath('ranking',
                           './/div[not(contains(@class,"ui_poi"))]'
                           '/span[contains(@class,"ui_bubble_rating")]'
                           '/@class',
                           MapCompose(self.getRanking)
                           )

            yield item.load_item()


# To run without terminal
# This is equivalent to write in terminal:
# scrapy runspider file_name -o results.ext -t ext
process = CrawlerProcess(settings={
    "FEEDS": {"4-5-1_Trip_Advisor_Restrict_Xpaths.json": {"format": "json"},
              },
})

process.crawl(TripAdvisor)
process.start()  # the script will block here until the crawling is finished
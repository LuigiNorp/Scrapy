import os
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.item import Field, Item
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule

# We are trying to clean the information, the "$" character and "MXN"
# string will be cleaned (pre-procesing) from data extraction

print(sys.path)
print(os.path)


class Hotel(Item):
    name = Field()
    price = Field()
    seller = Field()
    price_large = Field()
    seller_large = Field()
    description = Field()
    amenities = Field()


class TripAdvisor(CrawlSpider):
    name = "Hotels"
    custom_settings = {
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/80.0.3987.132 Safari/537.36"
    }
    start_urls = ['https://www.tripadvisor.com/'
                  'Hotels-g150800-Mexico_City_Central_Mexico_and_Gulf_Coast-Hotels.html']

    download_delay = 2  # Seconds

    # When the link of the website fits with the condition: (in this case)
    # "/Hotel-Review-", it'll call to run parse function and extract data.
    # Needed to use RegEx in: allow=r'pattern'

    rules = [Rule(LinkExtractor(allow=r'/Hotel_Review-'),
                  follow=True, callback="parse_item")]

    # Note:
    # [] Square braquets were mandatory for
    # TypeError: 'Rule' object is not iterable

    # This Method is Used inside MapCompose Fn
    def del_money_sign(self, price):
        new_price = price.replace("MX$", "")
        new_price = int(new_price.replace(",", "").replace("\n", "").replace("\r", "").replace("\t", ""))
        return new_price
    # ----------------------------------------------------

    def parse_item(self, response):
        sel = Selector(response)
        item = ItemLoader(Hotel(), sel)

        prices_div = '//div[@data-vendorname]'\
                     '//div[contains(text(),"$") and contains(@data-sizegroup,"prices")]'\
                     '/text()'

        prices_a = '//a[@data-vendorname]'\
                   '//div[contains(text(),"$")]'\
                   '/text()'

        prices_a2 = '//a[@data-vendorname]'\
                    '//div[contains(text(),"$")][2]'\
                    '/text()'

        prices_span = '//span[contains(text(),"$") and contains(@title,"$")]'\
                      '/text()'

        sellers_div = '//div[@data-vendorname]'\
                      '//img[@alt]'\
                      '/@alt'

        sellers_a = '//a[@data-vendorname]'\
                    '//img[@alt]'\
                    '/@alt'

        sellers_span = '//div[@data-vendorname]'\
                       '/span[@title and not(contains(@title,"$"))]'\
                       '/@title'  # /div/img/@alt /a /span

        item.add_xpath('name', '//h1[@id="HEADING"]'
                       '/text()')

        item.add_xpath('description', '//div[contains(@data-ssrev-handlers, "Description")]'
                       '/div/div[1]'
                       '/text()')

        item.add_xpath('amenities', '//div[@data-test-target="amenity_text"]'
                       '/text()')

        # Main Sellers and Prices

        # map compose is used into 'add_value()' and 'add_xpath()' functions, and its
        # functionality is to do a pre-processing of extracted data.

        if sellers_a is not None:
            item.add_value('seller',
                           response.xpath(sellers_a).extract())

        if sellers_div is not None:
            item.add_value('seller',
                           response.xpath(sellers_div).extract())

        # We use MapCompose() to activate del_money_sign method
        if prices_a2 is not None:
            item.add_xpath('price',
                            prices_a2,
                            MapCompose(self.del_money_sign))

        if prices_a is not None:
            item.add_xpath('price',
                            prices_a,
                            MapCompose(self.del_money_sign))

        if prices_div is not None:
            item.add_xpath('price',
                            prices_div,
                            MapCompose(self.del_money_sign))

        # Other Price Options
        item.add_xpath('price_large',
                       prices_span,
                       MapCompose(self.del_money_sign))

        item.add_xpath('seller_large',
                       sellers_span)

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

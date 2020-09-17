import scrapy


class RecipesSpider(scrapy.Spider):
    name = "lands"
    start_urls = [
        'https://www.lankapropertyweb.com/land/index.php',
    ]

    def parse(self, response):
        for inner_article in response.css('h4.listing-titles'):
            yield response.follow(inner_article.css('a::attr(href)').extract_first(), callback=self.parse_page)
        next_page = response.css('div ul.pagination li.pagination_arrows a::attr(href)').extract()[1]
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_page(self, response):

        yield {
            'title': response.css('div.details-heading.details-property')[0].xpath('./h1/text()').extract_first(),
            'location': response.css('div.col-md-9.col-sm-10.col-xs-12')[0].xpath('./span[@class="details-location"]/text()').extract_first(),
            'area': response.xpath('//div[@id="prop-keyfacts"]/div/div[1]/table/tr[2]/td[2]/text()').extract_first().replace('\xa0', ' '),
            'price': response.xpath('//div[@class="price-detail"]/text()').extract_first().replace('\n', ''),
            'description': "".join(response.css('div.col-lg-12.about-section')[0].xpath('./div/div/div/p/text()').extract()),
        }

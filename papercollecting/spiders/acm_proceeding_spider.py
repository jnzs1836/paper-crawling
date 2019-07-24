import scrapy
from papercollecting.items import ACMProceeding
import time
import re



class ACMProceedingSpider(scrapy.Spider):
    name = 'acm_proceedings'
    start_urls = ['https://dl.acm.org/proceedings.cfm']


    site_url = 'https://dl.acm.org'

    def start_requests(self):

        for url in self.start_urls:
            headers = {
                'referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            }
            yield scrapy.Request(url=url, callback=self.parse, headers=headers)
            time.sleep(9)

    def parse(self, response):
        content = response.xpath('//div[@class = "text12"]')
        proceeding_collections = content.css('ul')
        proceeding_collection_names = content.css('strong')

        assert len(proceeding_collections) == len(proceeding_collection_names)
        # procedding_collections = response.xpath('/html/body/div[2]/div[4]/ul/li')
        for i, proceeding_collection in enumerate(proceeding_collections):
            category = proceeding_collection_names[i].xpath('text()').get()
            for proceeding in proceeding_collection.css('a'):
                # Extracting citation id
                citation_id = re.search('citation.cfm\?id=(.*)', proceeding.attrib['href']).groups()[0]

                # Extract title and name
                title = proceeding.attrib['title']
                name = proceeding.xpath('text()').get()

                # Set the category

                # Initialize an Item
                item = ACMProceeding()
                item['citation_id'] = citation_id
                item['title'] = title
                item['name'] = name
                item['category'] = category
                yield item



import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from papercollecting.items import PaperItem
import os
import time
my_subjects = {
    'cs':[
        'AI', 'AR', 'CC', 'CG', 'CE', 'CL', 'CR', 'CV', 'CY', 'DB', 'DC', 'DL', 'DM', 'DS', 'ET', 'FL', 'GL', 'GR', 'GT'
    ]
}

select_subjects = {
    'cs':[
        'AI', 'CE', 'CL', 'CR', 'DL', 'GT'
    ]
}

begin = {
    'year': 2016,
    'month': 1,
}
end = {
    'year': 2019,
    'month': 1,
}


def generate_requests(begin, end, subjects):
    requests = []
    urls = []
    for subject, categories in subjects.items():
        for category in categories:
            year = begin['year']
            month = begin['month']

            while year < end['year'] or (year == end['year'] and month < end['month']):
                month_str = '0' * (2 - len(str(month))) + str(month)
                url = 'https://arxiv.org/list/' + subject + '.' + category + '/' + str(year)[-2:] + month_str + '?show=1000'
                requests.append({
                    'url': url,
                    'subject': subject,
                    'category': category,
                    'year': year,
                    'month': month
                })

                urls.append(url)
                month += 1
                if month > 12:
                    year += 1
                    month = 1
    print(requests[0])
    return requests


pdf_path = '/home/vidi/Work/text-vis/data/paper-scrapy/arxiv/'

def create_dirs(begin, end, subjects):
    for subject, categories in subjects.items():
        os.mkdir(pdf_path +subject)
        for category in categories:
            os.mkdir(pdf_path + subject + '/' + category)
            year = begin['year']
            month = begin['month']
            os.mkdir(pdf_path + subject + '/' + category + '/' + str(year)[-2:])
            while year < end['year'] or (year == end['year'] and month < end['month']):
                month_str = '0' * (2 - len(str(month))) + str(month)
                os.mkdir(pdf_path + subject + '/' + category + '/' + str(year)[-2:] + '/' + month_str)
                month += 1
                if month > 12:
                    year += 1
                    month = 1
                    os.mkdir(pdf_path + subject + '/' + category + '/' + str(year)[-2:])





# create_dirs(begin, end, select_subjects)
class ArxivCSSpider(scrapy.Spider):
    name = 'arxiv_cs'
    start_urls = ['https://arxiv.org/list/cs.CR/1712?show=8']
        # generate_requests(begin, end, select_subjects)
    pdf_path = '/home/vidi/Work/text-vis/data/paper-scrapy/arxiv/'
    # def start_requests(self):
    #     yield scrapy.Request(url='https://arxiv.org/list/cs.CV/1802?show=1000', callback=self.parse_form_page)
    #     pass

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('/abs/',)), callback='parse_item'),
    )
    site_url = 'https://arxiv.org'


    def start_requests(self):
        start_requests = generate_requests(begin, end, select_subjects)
        for r in start_requests:
            print(r)
            yield scrapy.Request(url=r['url'], callback=self.parse_index,meta=r)
            time.sleep(9)

        # for url in self.start_urls:
        #
        #     yield scrapy.Request(url=url, callback=self.parse_index)

    def parse_index(self, response):
        urls = []
        papers = response.xpath('//*[@id="dlpage"]/dl/dt/span/a[1]')
        for paper in papers:

            urls.append(self.site_url + paper.attrib['href'])
        for url in urls:
            if url.split("/")
            time.sleep(1)

            yield scrapy.Request(url=url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        url = response.url
        arxiv_id = url.split('/')[-1]

        title = response.selector.xpath('//*[@id="abs"]/h1/text()').extract()[0]
        abstract = response.xpath('//*[@id="abs"]/blockquote/text()[1]').extract()[0]
        authors = []
        for author in response.xpath('//*[@id="abs"]/div/a/text()'):
            authors.append(str(author))
        date_line = response.css('#abs > div.dateline').extract()
        pdf_href = response.xpath('//*[@id="abs"]/div[1]/div[1]/ul/li[1]/a').attrib['href']
        pdf_url = self.site_url + pdf_href


        paper = PaperItem()
        subject = response.meta['subject']
        category = response.meta['category']
        year = response.meta['year']
        month = response.meta['month']
        paper['subject'] = response.meta['subject']
        paper['category'] = response.meta['category']
        paper['arxiv_id'] = arxiv_id
        paper['authors'] = authors
        paper['abstract'] = abstract
        paper['date_line'] = str(date_line)
        paper['pdf_href'] = pdf_href
        paper['url'] = response.url
        paper['year'] = response.meta['year']
        paper['month'] = response.meta['month']
        paper['title'] = title
        yield paper
        yield scrapy.Request(url=pdf_url, callback=self.parse_pdf,
                             meta={
                                 'arxiv_id': arxiv_id,
                                 'year': year,
                                 'month': month,
                                 'subject': subject,
                                 'category': category
                             })
    def parse_pdf(self, response):
        arxiv_id = response.meta['arxiv_id']
        month = response.meta['month']
        month_str = '0' * (2 - len(str(month))) + str(month)
        file = self.pdf_path + response.meta['subject'] + '/' + response.meta['category'] + '/' + str(response.meta['year'])[-2:] + '/'+ month_str +'/' + arxiv_id + '.pdf'
        with open(file, 'wb') as f:
            f.write(response.body)

    def parse_paper_page(self, reponse):
        pass

import scrapy


# To collect papers from acm dl,you need to implement your filter function and use it in start_requests function.
# You could simply use do_not_filter function and the spider will crawl papers from all proceedings.
# I have implemented a filtering function to crawl selectively only ACM CHI papers.


def do_not_filter(text):
    return True


def filter_chi(text):
    return text['name'][:5] == 'CHI \''


def generate_urls(f):
    from pymongo import MongoClient

    client = MongoClient()
    db = client['papers']
    proceedings = db['acm_proceedings']
    proceedings = proceedings.find()
    # print(proceedings)
    proceedings = filter(f, proceedings)
    urls = []
    for proceeding in proceedings:
        citation_id = proceeding['citation_id']
        url = 'https://dl.acm.org/tab_about.cfm?id=' + citation_id+ '&type=proceeding&sellOnline=0&parent_id='+citation_id+'&parent_type=proceeding&title=Proceedings%20of%20the%202015%20CHI%20Conference%20on%20Human%20Factors%20in%20Computing%20Systems&toctitle=&tocissue_date=&notoc=0&usebody=tabbody&tocnext_id=&tocnext_str=&tocprev_id=&tocprev_str=&toctype=&_cf_containerId=cf_layoutareaprox&_cf_nodebug=true&_cf_nocache=true&_cf_clientid=EE9348C62C3D3D469D1813C8B332D467&_cf_rc=1'
        urls.append(url)
    return urls


class ACMPaperSpider(scrapy.Spider):
    name = 'acm_papers'
    pdf_path = '/home/jnzs1836/Code/'
    site_url = 'https://dl.acm.org/'
    def start_requests(self):
        # Modify here
        urls = generate_urls(filter_chi)
        for url in urls:
            headers = {
                'referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            }
            yield scrapy.Request(url=url, headers=headers)
            break

    def parse(self, response):
        content = response.xpath('//div[@class = "text12"]')
        refs = response.css('a')
        pdf_refs = list(filter(lambda x: 'title' in x.attrib.keys() and x.attrib['title']=='FullText PDF', refs))
        for pdf_ref in pdf_refs:
            print(pdf_ref)
            headers = {
                'referer': self.site_url + pdf_ref.attrib['href'],
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            }
            yield scrapy.Request(url=self.site_url + pdf_ref.attrib['href'], callback=self.parse_pdf, headers=headers)
            break

    def parse_pdf(self, response):
        file = self.pdf_path + 'sample' + '.pdf'
        with open(file, 'wb') as f:
            f.write(response.body)



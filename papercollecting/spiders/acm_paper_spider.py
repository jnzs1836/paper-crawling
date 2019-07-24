import scrapy
import time

pending_time = 1

# To collect papers from acm dl,you need to implement your filter function and use it in start_requests function.
# You could simply use do_not_filter function and the spider will crawl papers from all proceedings.
# I have implemented a filtering function to crawl selectively only ACM CHI papers.


def do_not_filter(proceeding):
    return True


def filter_chi(proceeding):

    if proceeding['name'][:5] == 'CHI \'' and (int(proceeding['name'][5:7]) > 19 or int(proceeding['name'][5:7]) < 16):
        print(proceeding)
        print(int(proceeding['name'][5:7]))
        return True
    else:
        return False


def generate_proceedings(f):
    from pymongo import MongoClient

    client = MongoClient()
    db = client['papers']
    proceedings = db['acm_proceedings']
    proceedings = proceedings.find()
    # print(proceedings)
    proceedings = filter(f, proceedings)
    result = []
    for proceeding in proceedings:
        citation_id = proceeding['citation_id']
        url = 'https://dl.acm.org/tab_about.cfm?id=' + citation_id+ '&type=proceeding&sellOnline=0&parent_id='+citation_id+'&parent_type=proceeding&title=Proceedings%20of%20the%202015%20CHI%20Conference%20on%20Human%20Factors%20in%20Computing%20Systems&toctitle=&tocissue_date=&notoc=0&usebody=tabbody&tocnext_id=&tocnext_str=&tocprev_id=&tocprev_str=&toctype=&_cf_containerId=cf_layoutareaprox&_cf_nodebug=true&_cf_nocache=true&_cf_clientid=EE9348C62C3D3D469D1813C8B332D467&_cf_rc=1'
        proceeding['url'] = url
        result.append(proceeding)
    return result


class ACMPaperSpider(scrapy.Spider):
    name = 'acm_papers'
    pdf_path = '/home/jnzs1836/Code/'
    site_url = 'https://dl.acm.org/'
    def start_requests(self):
        # Modify here
        proceedings = generate_proceedings(filter_chi)
        # print(proceedings)
        for i, proceeding in enumerate(proceedings):
            url = proceeding['url']
            title = proceeding['title']
            characters = list(filter(lambda c: c!='\'' and c!=' ', title))
            title = ''
            for c in characters:
                title = title + c
            headers = {
                'referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            }

            yield scrapy.Request(url=url, headers=headers,meta={
                'title': title
            })
            time.sleep(pending_time)

    def parse(self, response):
        content = response.xpath('//div[@class = "text12"]')
        rows = response.xpath('/html/body/div[1]/table/tbody/tr')
        # print(rows)
        # print("___________________________________________________")
        refs = response.css('a')
        pdf_refs = list(filter(lambda x: 'title' in x.attrib.keys() and x.attrib['title']=='FullText PDF', refs))
        for i, pdf_ref in enumerate(pdf_refs):
            headers = {
                'referer': self.site_url + pdf_ref.attrib['href'],
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            }
            yield scrapy.Request(url=self.site_url + pdf_ref.attrib['href'], callback=self.parse_pdf, headers=headers, meta={
                'proceeding': response.meta['title'],
                'id': i+1,
            })
            time.sleep(pending_time)

    def parse_pdf(self, response):
        id_str = (5 - len(str(response.meta['id']))) * '0' + str(response.meta['id'])
        file = self.pdf_path + response.meta['proceeding'] + '-' + id_str + '.pdf'
        with open(file, 'wb') as f:
            f.write(response.body)



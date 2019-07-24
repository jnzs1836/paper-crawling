# Paper Crawling

A collection of spiders to collect papers from websites like ACM DL, arXiv, IEEExplore and etc.


## ACM DL

ACM DL requires the spiders to specify user-agent and we could simply set
```
headers =  {
                'referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
            }
```


## arXiv

arXiv is extremely friendly to web crawling. However, you do not spiders to collect arXiv papers except the following reasons because it provides monthly collection of papers.

+ Hoping to have real-time updates of arXiv
+ Requiring papers categorized by the subjects
+ Other reasons
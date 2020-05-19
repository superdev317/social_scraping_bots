from bs4 import BeautifulSoup
import requests
import datetime
import re
import sys
sys.path.append("..")

from Crawlers.utils import get_substring, get_hash
from Crawlers.dbmanager import MongoDBManager
from Crawlers.config import ETH, OPINION_TIMESTAMP_LIMIT

dbmanager = MongoDBManager()


def do_crawl_ethiopia_addisfortune_opinion(debug=False):
    try:
        crawl_ethiopia_addisfortune_opinion(debug)
    except Exception as e:
        errMsg = "Failed in crawl_ethiopia_addisfortune_opinion! error={}".format(str(e))
        dbmanager.insertLog(errMsg)


def crawl_ethiopia_addisfortune_opinion(debug=False):
    start_url   = "https://addisfortune.news/commentary/"
    response = requests.get(start_url, timeout=10)
    if response.status_code != 200:
        return
    soup = BeautifulSoup(response.text, 'lxml')

    # get links from the home page
    article_links = []
    contents = soup.select("div.col-lg-12 > a")
    for content in contents:
        if content['href'].find('?') > 0:
            continue
        article_links.append(content['href'])        

    # remove the duplicated links
    article_links = list(dict.fromkeys(article_links))

    # crawl the article links up to 15
    count = 0
    for article_link in article_links:
        if count < 15:
            print ("article link ===>>> ", article_link)
            if crawl_article_page(article_link, debug) == True:            
                count = count + 1


def crawl_article_page(article_url, debug):
    response = requests.get(article_url, timeout=10)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    head = soup.head
    if head == None:
        return

    headline    = head.find("meta", attrs={"property": "og:title"})
    if headline:
        headline = headline['content']
    summary     = head.find("meta", attrs={"property": "og:description"})
    if summary:
        summary = summary['content']
    image       = head.find("meta", attrs={"property": "og:image"})
    if image:
        image   = image['content']
    url         = response.url
    article_id  = get_hash(url)

    # author & published
    author = None
    published = None
    data_tag = soup.find("p", attrs={"class": "font-11 adf_theme t-center"})
    if data_tag:
        data = data_tag.text.strip()
        published = get_substring(data, '', '. By').strip()
        date = datetime.datetime.strptime(published, '%B %d , %Y') - datetime.timedelta(hours=3)
        published = date.timestamp()        
        author = get_substring(data, '. By').strip()
    else:
        return

    # ignore this article if it was in previous 72 hours
    today = datetime.datetime.utcnow()
    timediff = today.timestamp() - published
    if timediff > OPINION_TIMESTAMP_LIMIT:
        return

    article_tags = soup.select("div.col-lg-8 > p.adf_post_body")
    if len(article_tags) == 0:
        return

    article_body = ""
    article_body_html = ""    
    for tag in article_tags:
        if tag.text == "" or tag.text == "\n":
            continue
        article_body += tag.text.strip() + '\n'
        article_body_html += str(tag)

    body = re.sub(r'\s\s+', ' ', article_body)
    if len(body) < 100:
        return

    today = datetime.datetime.utcnow()
    crawl_date = today.strftime("%Y-%m-%d")

    news = {
        "category": "Africa",
        "source": "Addis Fortune",
        "type": "Opinion",
        "state": ETH,
        "nid": article_id,
        "headline": headline,
        "author": author,
        "published": published,
        "summary": summary,
        "image": image,
        "url": url,
        "text": body,
        "html": article_body_html,
        "crawl_date": crawl_date,
        "translated": False
    }

    if debug:
        print ("News Article: ", news)
        # print ("text    ===>>> ", news['text'])
        # print ("html    ===>>> ", news['html'])
        # print ("summ    ===>>> ", news['summarized_text'])

    dbmanager.insertNews(news)

    return True
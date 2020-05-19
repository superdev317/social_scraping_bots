from bs4 import BeautifulSoup
import requests
import datetime
import re
import sys
import iso8601
sys.path.append("..")

from Crawlers.utils import get_hash
from Crawlers.dbmanager import MongoDBManager
from Crawlers.config import USA, OPINION_TIMESTAMP_LIMIT

dbmanager = MongoDBManager()


def do_crawl_usa_wsj_opinion(debug=False):
    try:
        crawl_wsj_opinion(debug)
    except Exception as e:
        errMsg = "Failed in crawl_wsj_opinion! error={}".format(str(e))
        dbmanager.insertLog(errMsg)


def crawl_wsj_opinion(debug=False):
    start_url   = "https://www.wsj.com/news/opinion"
    response = requests.get(start_url, timeout=10)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, 'lxml')

    # get links from the home page
    article_links = []
    contents = soup.findAll("a", {"data-referer": "/news/opinion"})
    for content in contents:
        article_links.append(content['href'])

    # remove the duplicated links
    article_links = list(dict.fromkeys(article_links))

    # crawl the article links up to 10
    for article_link in article_links:
        print ("article link ===>>> ", article_link)
        crawl_article_page(article_link, debug)


def crawl_article_page(article_url, debug):
    response = requests.get(article_url, timeout=10)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    head = soup.head
    if head == None:
        return

    headline    = head.find("meta", {"name": "article.headline"})
    if headline:
        headline = headline['content']

    summary     = head.find("meta", {"name": "article.summary"})
    if summary:
        summary = summary['content']
    author      = head.find("meta", {"name": "author"})
    if author:
        author  = author['content']
    published   = head.find("meta", {"name": "article.published"})
    if published:
        published = published['content']
        published = iso8601.parse_date(published).timestamp()
    else:
        return
    image       = head.find("meta", {"property": "og:image"})
    if image:
        image   = image['content']
    url         = response.url    
    article_id  = get_hash(url)

    # ignore this article if it was in previous 72 hours
    today = datetime.datetime.utcnow()
    timediff = today.timestamp() - published
    if timediff > OPINION_TIMESTAMP_LIMIT:
        return      

    article_tags = soup.select("div > .wsj-snippet-body > p")
    if len(article_tags) == 0:
        article_tags = soup.select("div > .article-content > p")
    if len(article_tags) == 0:
        return

    article_body = ""
    article_body_html = ""
    for tag in article_tags:
        if tag.text == "" or tag.text == "\n":
            continue
        article_body += tag.text.strip() + '\n'
        article_body_html += str(tag)

    body = re.sub('\s\s+', ' ', article_body)
    if len(body) < 100:
        return

    today = datetime.datetime.utcnow()
    crawl_date = today.strftime("%Y-%m-%d")

    news = {
        "category": "Anglosphere",
        "source": "Wall Street Journal",
        "type": "Opinion",
        "state": USA,
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
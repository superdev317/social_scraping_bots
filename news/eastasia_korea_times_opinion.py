from bs4 import BeautifulSoup
import requests
import datetime
import re
import sys
import iso8601
sys.path.append("..")

from Crawlers.utils import get_hash, get_substring
from Crawlers.dbmanager import MongoDBManager
from Crawlers.config import KOR, OPINION_TIMESTAMP_LIMIT

dbmanager = MongoDBManager()


def do_crawl_korea_koreatimes_opinion(debug=False):
    try:
        crawl_korea_koreatimes_opinion(debug)
    except Exception as e:
        errMsg = "Failed in crawl_korea_koreatimes_opinion! error={}".format(str(e))
        dbmanager.insertLog(errMsg)


def crawl_korea_koreatimes_opinion(debug=False):
    start_url   = "http://www.koreatimes.co.kr/www2/common/opinion.asp?category"
    response = requests.get(start_url, timeout=10)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, 'lxml')

    # get links from the home page
    article_links = []
    contents = soup.select("li.op2_OPED.HD > a")
    for content in contents:
        article_links.append(content['href'])

    # remove the duplicated links
    article_links = list(dict.fromkeys(article_links))

    # crawl the article links up to 15
    count = 0
    base_url = "http://www.koreatimes.co.kr"
    for article_link in article_links:
        article_link = base_url + article_link
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
        headline = headline['content'].strip()
    summary     = head.find("meta", attrs={"property": "og:description"})
    if summary:
        summary = summary['content']
    author      = head.find("meta", attrs={"name": "writer"})
    if author:
        author  = author['content']
    published   = head.find("meta", attrs={"property": "article:published_time"})
    if published:
        published = iso8601.parse_date(published['content']).timestamp()
    else:
        return
    image       = head.find("meta", attrs={"property": "og:image"})
    if image:
        image   = image['content']
    url         = response.url
    article_id  = get_hash(url)

    # ignore this article if it was in previous 72 hours
    today = datetime.datetime.utcnow()
    timediff = today.timestamp() - published
    if timediff > OPINION_TIMESTAMP_LIMIT:
        return      

    article_tags = soup.select("div#startts > span > span")
    if len(article_tags) == 0:
        return

    article_body = ""
    article_body_html = ""
    tag_index = 0
    for tag in article_tags:
        tag_index += 1
        if tag.text == "" or tag.text == "\n":
            continue
        if tag_index < 3 and tag.text.find('By') != -1:
            author = get_substring(tag.text, 'By')
            if author:
                author = author.strip()
                continue
        article_body += tag.text.strip() + '\n'
        article_body_html += str(tag)
    
    body = re.sub('\s\s+', ' ', article_body)
    if len(body) < 100:
        return

    today = datetime.datetime.utcnow()
    crawl_date = today.strftime("%Y-%m-%d")

    news = {
        "category": "East Asia",
        "source": "Korea Times",
        "type": "Opinion",
        "state": KOR,
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
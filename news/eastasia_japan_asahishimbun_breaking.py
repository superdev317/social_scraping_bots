from bs4 import BeautifulSoup
import requests
import datetime
import re
import sys
sys.path.append("..")

from Crawlers.utils import get_substring, replace_quote, get_hash
from Crawlers.dbmanager import MongoDBManager
from Crawlers.config import JPN, BREAKING_TIMESTAMP_LIMIT

dbmanager = MongoDBManager()


def do_crawl_japan_asahishimbun_breaking(debug=False):
    try:
        crawl_japan_asahishimbun_breaking(debug)
    except Exception as e:
        errMsg = "Failed in crawl_japan_asahishimbun_breaking! error={}".format(str(e))
        dbmanager.insertLog(errMsg)


def crawl_japan_asahishimbun_breaking(debug=False):
    start_url   = "http://www.asahi.com/ajw/"
    response = requests.get(start_url, timeout=10)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, 'lxml')

    # get links from the home page
    article_links = []
    contents = soup.select("ul.EnTopNewsL > li.Fst > a")
    for content in contents:
        article_links.append(content['href'])

    contents = soup.select("ul.EnTopNewsR > li.Fst > a")
    for content in contents:
        article_links.append(content['href'])

    base_url = "http://www.asahi.com"
    contents = soup.select("ul.EnList2ndLevel li.Fst > a")
    for content in contents:
        article_links.append(base_url + content['href'])                

    # remove the duplicated links
    article_links = list(dict.fromkeys(article_links))

    # crawl the article links up to 15
    count = 0
    for article_link in article_links:
        article_link = article_link
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

    headline    = soup.select("div.ArticleTitle > div.Title > h1")
    if headline:
        headline = headline[0].text.strip()
        headline = get_substring(headline, "", "：The Asahi")
        headline = replace_quote(headline)
    summary     = head.find("meta", attrs={"property": "og:description"})
    if summary:
        summary = summary['content']
        summary = replace_quote(summary)
    author      = soup.find("p", attrs={"class": "EnArticleName"})
    if author:
        temp = author.text.strip()
        if temp.find('By') == 0:
            author = get_substring(temp, 'By', '/').strip()
        else:
            author = None
    published   = soup.find("p", attrs={"class": "EnLastUpdated"})
    if published:
        published = published.text
        date = datetime.datetime.strptime(published, '%B %d, %Y at %H:%M JST') - datetime.timedelta(hours=9)
        published = date.timestamp()
    else:
        return
    image       = head.find("meta", attrs={"property": "og:image"})
    if image:
        image   = image['content']
    url         = response.url
    article_id  = get_hash(url)

    # ignore this article if it was in previous 24 hours
    today = datetime.datetime.utcnow()
    timediff = today.timestamp() - published
    if timediff > BREAKING_TIMESTAMP_LIMIT:
        return    

    body_items = soup.select("div.ArticleText > p")
    if len(body_items) == 0:
        return

    article_body = ""
    article_body_html = ""    
    for tag in body_items:
        if tag.text == "" or tag.text == "\n":
            continue
        article_body += tag.text.strip() + '\n'
        article_body_html += str(tag)
    
    body = re.sub('\s\s+', ' ', article_body)
    body = replace_quote(body)
    article_body_html = replace_quote(article_body_html)
    if len(body) < 100:
        return

    today = datetime.datetime.utcnow()
    crawl_date = today.strftime("%Y-%m-%d")

    news = {
        "category": "East Asia",
        "source": "Asahi Shimbun",
        "type": "Breaking",
        "state": JPN,
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
from bs4 import BeautifulSoup
import requests
import json
import datetime
import re
import sys
import iso8601
sys.path.append("..")

from Crawlers.utils import get_hash
from Crawlers.dbmanager import MongoDBManager
from Crawlers.config import GBR, BREAKING_TIMESTAMP_LIMIT

dbmanager = MongoDBManager()


def do_crawl_uk_economist_breaking(debug=False):
    try:
        crawl_uk_economist_breaking(debug)
    except Exception as e:
        errMsg = "Failed in crawl_uk_economist_breaking! error={}".format(str(e))
        dbmanager.insertLog(errMsg)


def crawl_uk_economist_breaking(debug=False):
    start_url   = "https://newsapi.org/v2/top-headlines?sources=the-economist&apiKey=c56f93c3484841b7b31e37fd7e2a2752"
    response = requests.get(start_url, timeout=10)
    if response.status_code != 200:
        return

    json_obj = json.loads(response.text)
    for article in json_obj['articles']:
        author      = article['author']
        published   = iso8601.parse_date(article['publishedAt']).timestamp()
        image       = article['urlToImage']
        url         = article['url']

        # ignore this article if it was in previous 24 hours
        today = datetime.datetime.utcnow()
        timediff = today.timestamp() - published
        if timediff > BREAKING_TIMESTAMP_LIMIT:
            continue          

        article_info = {
            "author": author,
            "published": published,
            "image": image,
            "url": url
        }

        print ("article link ===>>> ", url)
        crawl_article_page(url, article_info, debug)


def crawl_article_page(article_url, article_info, debug):
    response = requests.get(article_url, timeout=10)
    if response.status_code != 200:
        return

    soup = BeautifulSoup(response.text, 'lxml')

    try:
        bodyscript = soup.body.select('script#preloadedData')[0].text
        article_json_array = json.loads(bodyscript)
        article_json = article_json_array[len(article_json_array) - 1]

        if 'canonical' not in article_json['response'].keys():
            return

        economic_article = article_json['response']['canonical']
        if '_text1HYMMu' not in economic_article:
            return

        article_text = economic_article['_text1HYMMu']

        articleTexts = []
        for element in article_text:
            elementText = ""
            if 'children' in element:
                children = element['children']
                for child in children:
                    if ('children' in child):
                        sub_children = child['children']
                        for item in sub_children:
                            if 'data' in item.keys():
                                elementText += item['data']

                    else:
                        elementText += child['data'] + ' '

            if len(elementText) > 0:
                articleTexts.append(elementText)

        article_section = None
        if economic_article['articleSection']['internal']:
            article_section = economic_article['articleSection']['internal'][0]['hasPart']['parts'][0]
        elif economic_article['publication']:
            article_section = economic_article['publication'][0]['hasPart']['parts'][0]
        else:
            return

        headline = ""
        if 'headline' in article_section:
            headline = article_section['headline']
            summary = article_section['description']
        else:
            return

        article_body = ""
        article_body_html = ""  
        for text in articleTexts:
            article_body += text.strip() + '\n'
            article_body_html += '<p>' + text.strip() + '</p>\n'
    except:
        return

    article_body = re.sub('\s\s+', ' ', article_body)
    if len(article_body) < 100:
        return

    today = datetime.datetime.utcnow()
    crawl_date = today.strftime("%Y-%m-%d")

    article_id = get_hash(article_info['url'])

    news = {
        "category": "Anglosphere",
        "source": "Economist",
        "type": "Breaking",
        "state": GBR,
        "nid": article_id,
        "headline": headline,
        "author": article_info['author'],
        "published": article_info['published'],
        "summary": summary,
        "image": article_info['image'],
        "url": article_info['url'],
        "text": article_body,
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
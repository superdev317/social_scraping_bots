import requests
import json
import datetime
import sys
sys.path.append("..")

from Crawlers.config import HTTP_HEADERS
from Crawlers.dbmanager import MongoDBManager
# from Crawlers.utils import refine_text
# from Crawlers.profanity_check import profanity_check
# 

dbmanager = MongoDBManager()


lifestyles = [
    { "name": "getmotivated", "source": "GetMotivated", "ups": 100},
    { "name": "LifeProTips", "source": "LifeProTips", "ups": 80},
    { "name": "todayilearned", "source": "TodayILearned", "ups": 100},
    { "name": "upliftingnews", "source": "UpliftingNews", "ups": 100}
]


def do_crawl_reddit_lifestyle(debug=False):
    try:
        crawl_reddit_lifestyle(debug)
    except Exception as e:
        errMsg = "Failed in crawl_reddit_lifestyle! error={}".format(str(e))
        dbmanager.insertLog(errMsg)


def crawl_reddit_lifestyle(debug=False):
    start_url_format  = "https://www.reddit.com/r/{}/new.json?limit=30"

    for lifestyle in lifestyles:
        start_url = start_url_format.format(lifestyle['name'])
        print ("start url ===>>> ", lifestyle, start_url)
        response = requests.get(start_url, headers = HTTP_HEADERS, timeout=10)
        if response.status_code != 200:
            return

        article_count = 0
        json_obj = json.loads(response.text)
        for article in json_obj['data']['children']:
            if article_count == 10:
                break

            article_data = article['data']
            title   = article_data['title']
            author  = article_data['author']
            ups     = article_data['ups']
            prefix  = article_data['subreddit_name_prefixed']
            created = article_data['created_utc']
            rid     = article_data['id']
            num_comments = article_data['num_comments']
            selftext = article_data['selftext']
            selftext_html = article_data['selftext_html']
            thumbnail = article_data['thumbnail']
            url     = "https://www.reddit.com" + article_data['permalink']

            # If it contains media, save its url into the article
            media_url = None
            if article_data['media']:
                media_url = article_data['url']

            txtLength = len(title) + len(selftext)
            if (ups > lifestyle['ups']) and (num_comments >= 5) and (txtLength > 50):
                reddit = {
                    "rid": rid,
                    "title": title,
                    "author": author,
                    "text": selftext,
                    "html": selftext_html,
                    "image": thumbnail,
                    "media_url": media_url,
                    "upvotes": ups,
                    "prefix": prefix,
                    "created": created,
                    "url": url
                }

                comment_url = "https://www.reddit.com/r/{}/comments/{}/new.json?depth=1&limit=10".format(lifestyle['name'], rid)
                print ("comment_url ===>>> ", comment_url)
                if crawl_comment_page(comment_url, reddit, lifestyle, debug) == True:
                    article_count = article_count + 1


def crawl_comment_page(comment_url, reddit, lifestyle, debug):
    response = requests.get(comment_url, headers = HTTP_HEADERS, timeout=10)
    if response.status_code != 200:
        return

    json_obj = json.loads(response.text)

    # comment
    json_comments = json_obj[1]['data']['children']
    if len(json_comments) < 5:
        return

    comment_count = 0
    comments = []
    for comment in json_comments:
        if (comment_count == 3):
            break

        comment_data = comment['data']
        author  = ""
        if 'author' in comment_data:
            author = comment_data['author']
        body    = ""
        if 'body' in comment_data:
            body = comment_data['body']
            body_html = comment_data['body_html']

        c_url = "https://www.reddit.com" + comment_data['permalink']
        if (author != "" and body != "" and len(body) > 50):
            comments.append({
                "author": author,
                "body": body,
                "html": body_html,
                "created": comment_data['created_utc'],
                "url": c_url
            })
            comment_count = comment_count + 1

    if (len(comments) < 3):
        return

    reddit['comments'] = comments

    today = datetime.datetime.utcnow()
    crawl_date = today.strftime("%Y-%m-%d")

    reddit['category']    = "Lifestyle"
    reddit['source']      = lifestyle['source']
    reddit['crawl_date']  = crawl_date

    if debug == True:
        print ("Reddit Article: ", reddit)   

    dbmanager.insertReddit(reddit)

    return True
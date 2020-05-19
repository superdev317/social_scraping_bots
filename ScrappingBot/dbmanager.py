import pymongo
import datetime
import html
import re

from ScrappingBot.config.config import DB_URI, DB_NAME, DB_DEBUG, DB_NEWS_COLLECTION_NAME, DB_REDDIT_COLLECTION_NAME

class MongoDBManager:
    connuri = DB_URI
    dbname = DB_NAME

    def __init__(self):
        self.mgclient = pymongo.MongoClient(MongoDBManager.connuri)
        self.mgdb = self.mgclient[MongoDBManager.dbname]

        # news collection
        self.news_collection = self.mgdb[DB_NEWS_COLLECTION_NAME]
        if "crawl_date_1" not in self.news_collection.index_information():
            self.news_collection.create_index([("crawl_date", pymongo.DESCENDING),
                                                ("nid", pymongo.ASCENDING)])

        # reddit collection
        self.reddit_collection = self.mgdb[DB_REDDIT_COLLECTION_NAME]
        if "crawl_date_1" not in self.reddit_collection.index_information():
            self.reddit_collection.create_index([("crawl_date", pymongo.DESCENDING),
                                                ("rid", pymongo.ASCENDING)])

        # log collection
        self.log_collection = self.mgdb['log']
        if "date_1" not in self.log_collection.index_information():
            self.log_collection.create_index("date")

    def refineText(self, text):
        re_text = html.unescape(text)
        re_text = re.sub('\s\s+', ' ', re_text)
        return re_text

    def refineNews(self, news):
        if news['headline'] != None and news['headline'] != "":
            news['headline'] = self.refineText(news['headline'])

        if news['summary'] != None and news['summary'] != "":
            news['summary'] = self.refineText(news['summary'])

        if news['text'] != None and news['text'] != "":
            news['text'] = self.refineText(news['text'])

    def insertNews(self, newsInfo):
        self.refineNews(newsInfo)

        myquery = {"nid": newsInfo['nid']}
        news = self.news_collection.find_one(myquery)
        if news:
            myquery = {"_id": news['_id']}
            newvalue = { "$set": newsInfo }
            self.news_collection.update_one(myquery, newvalue)
            if DB_DEBUG == True:
                print ("News updated ->", newsInfo['headline'])
            return

        self.news_collection.insert_one(newsInfo)
        if DB_DEBUG == True:
            print ("News inserted ->", newsInfo['headline'])

    def getNewsByCrawlDate(self, datestring):
        myquery = {"crawl_date": datestring}
        news = self.news_collection.find(myquery)

        result = []
        for document in news:
            result.append(document)

        return result

    def refineReddit(self, reddit):
        if reddit['title'] != None and reddit['title'] != "":
            reddit['title'] = self.refineText(reddit['title'])

        if reddit['text'] != None and reddit['text'] != "":
            reddit['text'] = self.refineText(reddit['text'])
        
        for comment in reddit['comments']:
            if comment['body'] != None and comment['body'] != "":
                comment['body'] = self.refineText(comment['body'])        

    def insertReddit(self, redditInfo):
        self.refineReddit(redditInfo)

        myquery = {"rid": redditInfo['rid']}
        reddit = self.reddit_collection.find_one(myquery)
        if reddit:
            myquery = {"_id": reddit['_id']}
            newvalue = { "$set": redditInfo }
            self.reddit_collection.update_one(myquery, newvalue)
            if DB_DEBUG == True:
                print ("Reddit updated ->", redditInfo['title'])
            return

        self.reddit_collection.insert_one(redditInfo)
        if DB_DEBUG == True:
            print ("Reddit inserted ->", redditInfo['title'])

    def getRedditByCrawlDate(self, datestring):
        myquery = {"crawl_date": datestring}
        reddits = self.reddit_collection.find(myquery)

        result = []
        for document in reddits:
            result.append(document)
            
        return result

    def insertLog(self, logstring):
        today = datetime.datetime.utcnow()
        log_date = today.strftime("%Y-%m-%d %H:%M:%S")
        log_info = {
            "error": logstring,
            "date": log_date
        }

        self.log_collection.insert_one(log_info)
        if DB_DEBUG:
            print (log_info)
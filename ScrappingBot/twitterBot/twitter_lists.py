from bs4 import BeautifulSoup
import requests
import json
import datetime
import sys
import tweepy
sys.path.append("..")
from ScrappingBot.dbmanager import MongoDBManager
from ScrappingBot.config.firebaseManager import FirestoreManager
from ScrappingBot.config.config import HTTP_HEADERS
from ScrappingBot.config.config import TWITTER_CONSUMER_KEY, TWITTER_SECRET, TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET

# from Crawlers.utils import refine_text
# from Crawlers.profanity_check import profanity_check
#

dbmanager = MongoDBManager()
firestoremanager = FirestoreManager() 
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET)
twitterApi = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)

def do_crawl_twitter_lists(debug=False):
    try:
        listUrls = firestoremanager.getLists()
        for list_url in listUrls:
            crawl_twitter_discussion(list_url)
       
    except Exception as e:
        errMsg = "Failed in crawl_twitter_lists! error={}".format(str(e))
        dbmanager.insertLog(errMsg)


def crawl_twitter_discussion(start_url, debug=True):
    # start_url = "https://twitter.com/thenewsraven/lists/medical-educators"
    print("start_url =============+>", start_url)
    response = requests.get(start_url, headers=HTTP_HEADERS, timeout=10)
    print("response ============+++>", response)
    if response.status_code != 200:
        return
    
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.select("div.stream > ol.stream-items > li.stream-item")
    
    articleIds = []
    for article in articles:
        article_id = article['data-item-id']
        retweeter_profile_link = ""
        retweeter_name = ""
        tweet_adaptivePhotos = ""
        tweet_adaptive_photos = []
        if article_id:
            articleIds.append(article_id)
        retweet = article.find("span", {"class": "js-retweet-text"})
        if retweet:
            retweeter_profile_link = retweet.find("a", {"class": "js-user-profile-link"})
            retweeter_name = retweet.find("a", {"class": "js-user-profile-link"}).find("b")
            if retweeter_profile_link:
                retweeter_profile_link = retweeter_profile_link['href']
            if retweeter_name:
                retweeter_name = retweeter_name.get_text()
                
        content = article.find("div", {"class", "content"})
        header = content.find("div", {"class", "stream-item-header"})
        tweet_profile_link = header.find("a", "account-group")
        if tweet_profile_link:
            tweet_profile_link = tweet_profile_link['href']
        tweet_profile_avatar = header.find("a", "account-group").find("img", {"class", "avatar"})
        if tweet_profile_avatar:
            tweet_profile_avatar = tweet_profile_avatar['src']
        tweet_profile_fullname = header.find("a", "account-group").find("span", {"class", "FullNameGroup"}).find("strong")
        if tweet_profile_fullname:
            tweet_profile_fullname = tweet_profile_fullname.get_text()
        tweet_profile_username = header.find("a", "account-group").find("span", {"class", "username"}).find("b")
        if tweet_profile_username:
            tweet_profile_username = "@" + tweet_profile_username.get_text()
        tweet_time_group = header.find("small", {"class", "time"})
        tweet_original_link = tweet_time_group.find("a", {"class", "tweet-timestamp"})
        print ("tiwtter article link ===>>> ", tweet_original_link)
        if tweet_original_link:
            tweet_original_link = tweet_original_link['href']
        tweet_time_stamp = tweet_time_group.find("a", {"class", "tweet-timestamp"})
        if tweet_time_stamp:
            tweet_time_stamp = tweet_time_stamp['title']
        
        tweet_text_content = content.find("div", {"class", "js-tweet-text-container"}).find("p", {"class", "tweet-text"})
        tweet_AdaptiveMediaOuterContainer = content.find("div", {"class", "AdaptiveMediaOuterContainer"})
        if tweet_AdaptiveMediaOuterContainer:
            tweet_adaptivePhotos =  tweet_AdaptiveMediaOuterContainer.findAll("div", {"class", "js-adaptive-photo"})
            tweet_ataptiveMediaVideo = tweet_AdaptiveMediaOuterContainer.find("div", {"class", "AdaptiveMedia-video"})
            for tweet_adaptive_photo in tweet_adaptivePhotos:
                tweet_adaptive_photo = tweet_adaptive_photo.find("img")
                tweet_adaptive_photo = tweet_adaptive_photo['src']
                tweet_adaptive_photos.append(tweet_adaptive_photo)
                
        footer = content.find("div", {"class", "stream-item-footer"})
        tweet_footer_reply = footer.find("div", {"class", "ProfileTweet-action--reply"}).find("span", {"class", "ProfileTweet-actionCountForPresentation"})
        if tweet_footer_reply:
            tweet_footer_reply = tweet_footer_reply.get_text()
        tweet_footer_retweet = footer.find("div", {"class", "ProfileTweet-action--retweet"}).find("span", {"class", "ProfileTweet-actionCountForPresentation"})
        if tweet_footer_retweet:
            tweet_footer_retweet = tweet_footer_retweet.get_text()
        tweet_footer_favorite = footer.find("div", {"class", "ProfileTweet-action--favorite"}).find("span", {"class", "ProfileTweet-actionCountForPresentation"})
        if tweet_footer_favorite:
            tweet_footer_favorite = tweet_footer_favorite.get_text()
        
        tweet = {
            "article_object": {
                "article_id": article_id,
                "retweet": {
                    "retweeter_profile_link": retweeter_profile_link,
                    "retweeter_name": retweeter_name,
                },
                "content": {
                    "header": {
                        "tweet_profile_link": tweet_profile_link,
                        "tweet_profile_avatar": tweet_profile_avatar,
                        "tweet_profile_fullname": tweet_profile_fullname,
                        "tweet_profile_username": tweet_profile_username,
                        "tweet_original_link": tweet_original_link,
                        "tweet_time_stamp": tweet_time_stamp,
                    },
                    "tweet_text_content": tweet_text_content,
                    "tweet_AdaptiveMediaOuterContainer": tweet_AdaptiveMediaOuterContainer,
                    "tweet_adaptive_photos": tweet_adaptive_photos,
                    "tweet_ataptiveMediaVideo": tweet_ataptiveMediaVideo,
                    "footer": {
                        "tweet_footer_reply": tweet_footer_reply,
                        "tweet_footer_retweet": tweet_footer_retweet,
                        "tweet_footer_favorite": tweet_footer_favorite,
                    }
                }
            }
        }
        print ("Twitter Article: ", tweet)
        if debug == True:
            print ("Twitter Article: ", tweet)
            
        # dbmanager.insertNews(tweet)
        
        # return True



            
    

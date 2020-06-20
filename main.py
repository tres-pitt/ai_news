import tweepy
import sqlite3 as sql
import sys
import os
from const import consts

# simple twitter bot
# you'll need to generate your own consts.py file after getting a developer account
class tw_bot:
    # setup class vars
    def __init__(self):
        assert "TechTweets.db" in os.listdir('.')
        self.db = sql.connect("TechTweets.db")
        self.dbc = self.db.cursor()
        self.tw_consts = consts().const_dict()
        self.consumer_key = self.tw_consts["consumer"]
        self.consumer_secret = self.tw_consts["consumer_secret"]
        self.access_token = self.tw_consts["access"]
        self.access_secret = self.tw_consts["access_secret"]

    # given a tweet, setup the API and post the tweet
    def tweet(self, msg):
        assert isinstance(msg, str)
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        api = tweepy.API(auth)
        api.update_status(msg)

# TODO: setup a sensible pipeline
if __name__ == '__main__':
    twb = tw_bot()
    #tweet_info = twb.tweet("Microsoft pitched facial recognition to the DEA https://www.buzzfeednews.com/article/ryanmac/microsoft-pitched-facial-recognition-dea-drug-enforcement")
    #msg2 = "An enormous theorem: the classification of finite simple groups https://plus.maths.org/content/enormous-theorem-classification-finite-simple-groups"
    # maintain flexibility w.r.t. whether initialize tweeted bool-int to 0
    qry = "select *, max(ID) from (select * from tweets where tweeted is null or tweeted = 0)"
    #msg = twb.dbc.execute(qry).fetchall()
    #assert len(msg) == 1
    # unpack inelegantly due to max(id) fashion of select statement
    breakpoint()
    id, msg, link, tweeted, id2 = twb.dbc.execute(qry).fetchall()[0]
    assert id == id2
    try:
        tweet_info = twb.tweet(msg + " " + link)
        # we shouldnt need to cast ID but I see no harm
        qry2 = "update tweets set tweeted = 1 where id = " + str(id)
        twb.dbc.execute(qry2)
        twb.db.commit()
        print("tweet suceeded")
    except:
        print("tweet failed")
        pass

# [1] https://realpython.com/twitter-bot-python-tweepy/

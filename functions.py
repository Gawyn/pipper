import datetime
import pymongo
import time
import twitter
import yaml

import numpy as np
import matplotlib.pyplot as plt

from pymongo import MongoClient
from collections import Counter

client = MongoClient()
db = client.pipper

credentials = yaml.load(open("credentials.yml", "r"))
api = twitter.Api(consumer_key=credentials['consumer_key'],
        consumer_secret=credentials['consumer_secret'],
        access_token_key=credentials['access_token_key'],
        access_token_secret=credentials['access_token_secret'])

def checkTextInTweets(tweets, regex, conditions):
    regex_condition = {"text": {"$regex" : regex}}
    conditions.update(regex_condition)
    return tweets.find(conditions)


def filterTweetsMentioning(tweets, screen_name, conditions):
    conditions.update({"user_mentions": {"$exists": True}, "user_mentions.screen_name": screen_name})
    return tweets.find(conditions)

def mentionsByHalf(tweets, mentions, half, title=""):
    for mention in mentions:
        mentioning = filterTweetsMentioning(tweets, mention, {"game_half": half})
        cnt = getCounterfromCursor(mentioning, "minute_half")
        cnt = zeroSetter(cnt)
        plt.plot(cnt.keys(), cnt.values(), label=mention)

    legend = plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc="upper center", ncol=3, mode="expand", borderaxespad=0.)
    for handle in legend.legendHandles:
        handle.set_linewidth(5.0)

    plt.title(title, x=0.11, y=1.03, size="x-large", name="Helvetica")
    plt.show()

def getCreatedAt(tweet):
    return datetime.datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")

def setCreatedAt(tweets, tweet):
    date = getCreatedAt(tweet)
    tweets.update({"id": tweet["id"]}, {"$set": { "datetime": date }})

def zeroSetter(cnt):
    for x in range(1, 45):
        if cnt[x] == 0 :
            cnt[x] = 0
    return cnt

def getCounter(tweets, key, condition=None):
    return Counter(map(lambda x:x[key], tweets.find(condition)))

def getCounterfromCursor(cursor, key):
    return Counter(map(lambda x: x[key], cursor))

def printGraph(values, keys, width, np):
    indexes = np.arange(len(values))
    plt.bar(indexes, values, width)
    plt.xticks(indexes + width * 0.5, keys)
    plt.show()

def makePlot(tweets, plt, field1, field2):
    first_dim = map(lambda x: x[field1], tweets.find())
    second_dim = map(lambda x: x[field2], tweets.find())
    plt.plot(first_dim, second_dim)
    plt.show()

def makeGraph(cnt, np, plt, threshold=0.005, order=None):
    if(order == "most_common"):
        ordered = cnt.most_common()
    else:
        ordered = sorted(cnt.most_common())

    keys = map(lambda x: x[0], ordered)
    values = map(lambda x: x[1], ordered)

    printGraph(values, keys, 1, np)


def makePie(cnt, np, plt, title="", threshold=0.005):
    ordered = cnt.most_common()
    total_values = map(lambda x: x[1], ordered)
    min_value = threshold * sum(total_values)

    ordered = [v for v in ordered if v[1] >= min_value]
    labels = np.array(map(lambda x: x[0], ordered))
    values = np.array(map(lambda x: x[1], ordered))
    porcent = 100.*values/values.sum()

    plt.pie(values, shadow=True)
    labels = ['{0} - {1:1.1f} %'.format(i,j) for i,j in zip(labels, porcent)]

    plt.axis('equal')
    plt.legend(labels, loc="center left")
    plt.title(title, x=0.11, y=1.03, size="x-large", name="Helvetica")

    plt.show()

def get_tweets(api, tweets, query, final_tweet, begin_tweet):
    r = api.GetSearch(query + " -filter:retweets", count=100, result_type="recent", include_entities=True, max_id=final_tweet)

    for tweet in r:
        formattedTweet = tweet.AsDict()
        if not tweets.find_one( { "id": formattedTweet["id"] } ) :
            if formattedTweet["id"] >= begin_tweet:
                if formattedTweet.get("urls"):
                    formattedTweet["urls"] = formattedTweet["urls"].values()
                tweets.insert(formattedTweet)

def get_many_tweets(api, tweets, query, final_tweet, begin_tweet):
  while final_tweet > begin_tweet:
      for i in xrange(15):
          if final_tweet > begin_tweet:
              get_tweets(api, tweets, query, final_tweet, begin_tweet)
              final_tweet = tweets.find().sort("id", pymongo.ASCENDING)[0]["id"]
      time.sleep(910)

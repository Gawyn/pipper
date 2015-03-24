import pymongo
import twitter
import yaml

client = MongoClient()
db = client.pipper
tweets = db.tweets

credentials = yaml.load(open("credentials.yml", "r"))
api = twitter.Api(consumer_key=credentials['consumer_key'],
        consumer_secret=credentials['consumer_secret'],
        access_token_key=credentials['access_token_key'],
        access_token_secret=credentials['access_token_secret'])

final_tweet = 579762557763891200
r = api.GetSearch("#ElClasico -filter:retweets", count=100, result_type="recent", include_entities=True, max_id=final_tweet)

tweets.insert(tweet)

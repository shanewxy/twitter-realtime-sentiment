from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import couchdb
import argparse
import twitter_credentials


class TwitterStreamer:
    """
    streaming live tweets
    """

    def stream_tweets(self, locations):
        listener = MyStreamListener()
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)

        stream = Stream(auth, listener)
        stream.filter(locations=locations)


class MyStreamListener(StreamListener):

    def on_data(self, data):
        try:
            data_object = json.loads(data)
            # store_tweets_locally(filename, data_object)
            store_tweets_db(data_object)

        except BaseException as e:
            print("Error on data: %s " % str(e))

    def on_error(self, status_code):
        print(status_code)


def store_tweets_db(data_object):
    place = data_object['place']['name']

    # double check place here, no idea why Streaming API will return 'New South Wales' or 'Victoria'
    # even if already set the stream filter
    if str(place) != 'New South Wales' and str(place) != 'Victoria':
        doc_id, doc_rev = db.save({'text': data_object['text'],
                                   'coordinates': data_object['coordinates'],
                                   'created_at': data_object['created_at'],
                                   'place': data_object['place']['name'],
                                   'user_id': data_object['user']['id'],
                                   'user_location': data_object['user']['location'],
                                   'sentiment': sentiment_analyzer_scores(data_object['text'])})


def store_tweets_locally(filename, data_object):
    """
    Store json locally
    :param filename:
    :param data_object:
    :return:
    """
    db_tweets = dict()
    db_tweets['text'] = data_object['text']
    db_tweets['coordinates'] = data_object['coordinates']
    db_tweets['created_at'] = data_object['created_at']
    db_tweets['place'] = data_object['place']['name']
    db_tweets['user_id'] = data_object['user']['id']
    db_tweets['user_location'] = data_object['user']['location']
    # db_tweets['sentiment'] = TextBlob(data_object['text']).sentiment.polarity
    db_tweets['sentiment'] = sentiment_analyzer_scores(data_object['text'])

    print(db_tweets)
    with open(filename, 'a') as tf:
        if str(db_tweets['place']) != 'New South Wales' and str(db_tweets['place']) != 'Victoria':
            tf.write(json.dumps(db_tweets, indent=2))
        return True


def sentiment_analyzer_scores(text):
    """
    Get sentiment score using Vader, normalize sentiment score to [-1, 1]
    :param text: The sentence to be analyzed
    :return: The sentiment score
    """
    score = SentimentIntensityAnalyzer().polarity_scores(text)
    compound = score['compound']

    if -0.05 < compound < 0.05:
        sentiment = 0
    elif compound >= 0.05:
        sentiment = score['pos']
    elif compound <= -0.05:
        sentiment = -score['neu']

    return sentiment


if __name__ == "__main__":
    # coordinates of Melbourne
    locations = [144.9631, -37.8136, 145.9631, -36.8136]
    filename = "tweets.json"

    parser = argparse.ArgumentParser()
    # parser.add_argument("--user", default="admin", type=str, help="couchdb user")
    # parser.add_argument("--pwd", default="admin", type=str, help="couchdb password")
    parser.add_argument("--server", default="127.0.0.1:5984", type=str, help="couchdb server address")
    args = parser.parse_args()

    # db_server = couchdb.Server("http://%s:%s@%s/" % (args.user, args.pwd, args.server))
    db_server = couchdb.Server("http://%s/" % args.server)
    db_name = "twitter_realtime_sentiment"
    if db_name in db_server:
        db = db_server[db_name]
    else:
        db = db_server.create(db_name)

    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(locations)

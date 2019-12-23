from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json

import twitter_credentials

analyser = SentimentIntensityAnalyzer()


class TwitterStreamer:
    """
    streaming live tweets
    """

    def stream_tweets(self, filename, locations):
        listener = MyStreamListener(filename)
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)

        stream = Stream(auth, listener)
        stream.filter(locations=locations)


class MyStreamListener(StreamListener):

    def __init__(self, filename):
        self.filename = filename

    def on_data(self, data):
        try:
            data_object = json.loads(data)
            store_tweets_locally(filename, data_object)

        except BaseException as e:
            print("Error on data: %s " % str(e))

    def on_error(self, status_code):
        print(status_code)


def store_tweets_locally(filename, data_object):
    """
    Store json locally
    :param filename:
    :param data_object:
    :return:
    """
    db_tweets = dict()
    db_tweets['id'] = data_object['id']
    db_tweets['text'] = data_object['text']
    db_tweets['coordinates'] = data_object['coordinates']
    db_tweets['created_at'] = data_object['created_at']
    db_tweets['user_id'] = data_object['user']['id']
    db_tweets['place'] = data_object['place']['name']
    # db_tweets['sentiment'] = TextBlob(data_object['text']).sentiment.polarity
    db_tweets['sentiment'] = sentiment_analyzer_scores(data_object['text'])

    print(db_tweets)
    with open(filename, 'a') as tf:
        if str(db_tweets['place']) != 'New South Wales' and str(db_tweets['place']) != 'Victoria':
            tf.write(json.dumps(db_tweets, indent=2))
        return True


def sentiment_analyzer_scores(text):
    """
    Get sentiment score using Vader
    :param text:
    :return:
    """
    score = analyser.polarity_scores(text)

    # if score['compound'] >= 0.05:
    #     sentiment = score['pos']
    # elif score['compound'] <= -0.05:
    #     sentiment = -score['neg']
    # else:
    #     sentiment = score['neu']

    # print("{:-<40} {}".format(text, str(score)))
    return score


if __name__ == "__main__":
    # coordinates of Melbourne
    locations = [144.9631, -37.8136, 145.9631, -36.8136]
    filename = "tweets.json"

    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(filename, locations)

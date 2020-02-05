from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import requests
import couchdb
import argparse
import twitter_credentials
import shapefile
from shapely.geometry import Point, Polygon
from http.client import IncompleteRead

# coordinates of Melbourne
locations = [144.946457, -37.840935, 145.9631, -36.8136]
sf = shapefile.Reader("/home/ubuntu/project/1270055001_sa2_2016_aust_shape/SA2_2016_AUST")
records = sf.records()
shapes = sf.shapes()
length = len(records)


class TwitterStreamer:
    """
    streaming live tweets
    """

    def stream_tweets(self, locations):
        try:
            listener = MyStreamListener()
            auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
            auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)

            stream = Stream(auth, listener)
            stream.filter(locations=locations)
        except IncompleteRead:
            pass


class MyStreamListener(StreamListener):

    def on_data(self, data):
        try:
            print(data)
            data_object = json.loads(data)
            # store_tweets_locally(filename, data_object)
            store_tweets_db(data_object)

        except BaseException as e:
            print("Error on data: %s " % str(e))

    def on_error(self, status_code):
        print(status_code)


def store_tweets_db(data_object):
    place = data_object['place']['name']
    coord = data_object['coordinates']

    if coord is not None:
        sa2_name, sa2_code = get_sa2_info(coord[0], coord[1])
    elif str(place) != "Melbourne" and str(place) != 'New South Wales' and str(place) != 'Victoria':
        bbx = data_object['place']['bounding_box']['coordinates'][0][0]
        sa2_name, sa2_code = get_sa2_info(bbx[0], bbx[1])
    else:
        sa2_name = data_object['place']['name']
        sa2_code = ""

    # double check place here, no idea why Streaming API will return 'New South Wales' or 'Victoria'
    # even if already set the stream filter
    if str(place) != 'New South Wales' and str(place) != 'Victoria':
        r = requests.post("http://localhost:8080/tweet/upload",json={'text': data_object['text'],
                                   'coordinates': data_object['coordinates'],
                                   'created_at': data_object['created_at'],
                                   'sa2_name': sa2_name,
                                   'sa2_code': sa2_code,
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


def get_sa2_name(lat, lon):

    url = 'https://mappify.io/api/rpc/coordinates/classify/'
    payload = {"lat": lat, "lon": lon, "encoding": "sa2", "apiKey": "4934f296-ae11-4fe0-a0ca-69e528d10067"}
    response = requests.post(url, data=json.dumps(payload), headers={'content-type': 'application/json'})
    json_str = json.loads(response.text)
    if json_str['result'] is not None:
        sa2_name = json_str['result']['name']
        sa2_code = json_str['result']['code'][0] + json_str['result']['code'][-4:]
        return sa2_name, sa2_code
    else:
        return "Melbourne", ""

def get_sa2_info(lon, lat):
    """
    get SA2 name and code based on latitude and longtitude.
    :param lon:
    :param lat:
    :return:
    """
    p = Point(lon, lat)
    for i in range(length):
        poly = Polygon(shapes[i].points)
        if poly.contains(p):
            sa2_name = records[i][2]
            sa2_code = records[i][1]
            return sa2_name, sa2_code


if __name__ == "__main__":
    filename = "tweets.json"

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="127.0.0.1:5984", type=str, help="couchdb server address")
    args = parser.parse_args()

    # db_server = couchdb.Server("http://admin:admin@%s/" % (args.server))
    db_server = couchdb.Server("http://%s/" % args.server)
    args = parser.parse_args()

    db_name = "twitter_realtime_sentiment"
    if db_name in db_server:
        db = db_server[db_name]
    else:
        db = db_server.create(db_name)

    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(locations)

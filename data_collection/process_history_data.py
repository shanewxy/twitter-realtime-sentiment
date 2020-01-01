import json
import time
import couchdb
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from twitter_streaming import sentiment_analyzer_scores

locations = [144.9631, -37.8136, 145.9631, -36.8136]  # Melbourne's location


def store_tweet_db(json_obj):
    doc_id, doc_rev = db.save({'text': json_obj['json']['text'],
                               'coordinates': json_obj['json']['coordinates']['coordinates'],
                               'created_at': json_obj['json']['created_at'],
                               'place': json_obj['json']['place']['name'],
                               'user_id': json_obj['json']['user']['id'],
                               'user_location': json_obj['json']['user']['location'],
                               'sentiment': sentiment_analyzer_scores(json_obj['json']['text'])})


def process_data(json_obj):
    """
    Process json data, filter out required tweets
    :param json_obj:
    :return:
    """
    coordinates = json_obj['json']['coordinates']['coordinates']
    place = json_obj['json']['place']['name']
    if valid_coordinate(coordinates, place):
        store_tweet_db(json_obj)


def valid_coordinate(coordinates, place):
    """
    Return True if this coordinate is not null and inside Melbourne
    :param coordinates:
    :return:
    """
    if coordinates is not None and locations[0] <= coordinates[0] <= locations[2] \
            and locations[1] <= coordinates[1] <= locations[3]:
        return True
    elif place == 'Melbourne':
        return True
    return False


if __name__ == "__main__":

    db_server = couchdb.Server("http://127.0.0.1:5984/")
    db_name = "twitter_realtime_sentiment"
    if db_name in db_server:
        db = db_server[db_name]
    else:
        db = db_server.create(db_name)

    with open("~/project/test.json", 'r') as f:
        for cnt, line in enumerate(f):
            try:
                line = line.strip('\n').strip(',')
                json_obj = json.loads(line)
                process_data(json_obj)

                time.sleep(1)
            except Exception as e:
                print(e)
                continue



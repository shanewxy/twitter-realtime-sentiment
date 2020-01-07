import json
import time
import couchdb
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from twitter_streaming import sentiment_analyzer_scores, get_sa2_name
import requests

locations = [143.9631, -38.8136, 145.9631, -36.8136]  # Melbourne's location


def store_tweet_db(json_obj):
    coord = json_obj['json']['coordinates']['coordinates']

    if coord[0] != 0 and coord[1] != 0 and locations[0] <= coord[0] <= locations[2] \
            and locations[1] <= coord[1] <= locations[3]:
        sa2_name, sa2_code = get_sa2_name(coord[1], coord[0])
    else:
        sa2_name = json_obj['json']['place']['name']
        sa2_code = ""

    doc_id, doc_rev = requests.post("http://localhost:8080/tweet/upload", json={'text': data_object['json']['text'],
                               'coordinates': json_obj['json']['coordinates']['coordinates'],
                               'created_at': json_obj['json']['created_at'],
                               'sa2_name': sa2_name,
                               'sa2_code': sa2_code,
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
    # coord = json.load(coordinates)
    # print(coordinates[0])
    if coordinates is not None and locations[0] <= coordinates[0] <= locations[2] \
            and locations[1] <= coordinates[1] <= locations[3]:
        return True
    elif place == 'Melbourne':
        return True
    return False


if __name__ == "__main__":

    db_server = couchdb.Server("http://127.0.0.1:5984/")
    db_name = "history"
    if db_name in db_server:
        db = db_server[db_name]
    else:
        db = db_server.create(db_name)

    with open("/Users/pengkedi/Downloads/bigTwitter.json", 'r') as f:
        for cnt, line in enumerate(f):
            try:
                line = line.strip('\n').strip(',')
                json_obj = json.loads(line)
                process_data(json_obj)

            except Exception as e:
                print(e)
                continue



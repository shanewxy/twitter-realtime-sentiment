import argparse

from TwitterAPI import TwitterAPI
from TwitterAPI import TwitterPager
import couchdb
import json
from twitter_streaming import sentiment_analyzer_scores
from twitter_streaming import get_sa2_name

"""
Used for handing data which download from couchdb server. Run when everything settled down

"""

def process_data(data):
    print(data)

    sa2_name, sa2_code = "Melbourne", ""

    json_obj = json.loads(data)
    coord = json_obj['geometry']['coordinates']
    if coord is not None:
        sa2_name, sa2_code = get_sa2_name(coord[1], coord[0])


    db.save({'text': json_obj['properties']['text'],
             'coordinates': json_obj['geometry']['coordinates'],
             'created_at': json_obj['properties']['created_at'],
             'sa2_name': sa2_name,
             'sa2_code': sa2_code,
             'user_id': "",
             'user_location': "",
             'sentiment': sentiment_analyzer_scores(json_obj['properties']['text'])})


if __name__ == "__main__":

    db_server = couchdb.Server("http://127.0.0.1:5984/")
    db_name = "history"
    if db_name in db_server:
        db = db_server[db_name]
    else:
        db = db_server.create(db_name)

    filename = "/home/ubuntu/project/r1qb-r1qg.json"
    parser = argparse.ArgumentParser()
    parser.add_argument("--f", type=str, help="file to process")
    args = parser.parse_args()

    with open(args.f, 'r') as f:

        s = f.read()
        list = s.split("}, {", -1)
        for l in list:
            data = "{"+l+"}"
            process_data(data)



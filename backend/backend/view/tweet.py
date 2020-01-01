from backend.database.couchdb_connector import *
import ujson
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging
import datetime

logger = logging.getLogger('django')


@csrf_exempt
def tweet_upload(request):
    tweet = request.body
    logger.info("Received request: %s", tweet)

    tweet_json = ujson.loads(tweet)
    tweet_json['timestamp'] = datetime.datetime.timestamp(
        datetime.datetime.strptime(tweet_json['created_at'], '%a %b %d %H:%M:%S %z %Y'))
    print(tweet_json['timestamp'])
    tweet_json['score'] = tweet_json['sentiment']['compound']

    if request.method == "POST":
        logger.info("Saving tweet into database...")
        tweet_id, rev = tweet_db.save(tweet_json)

    return HttpResponse(ujson.dumps(tweet_json))


def historic_zones(request):
    result = tweet_db.view("statistics/zones_sentiment", group=True)
    resp = {}

    for row in result:
        resp[row.key[0]] = {'avg': row.value.get('sum') / row.value.get('count'), 'count': row.value.get('count')}
    logger.info("response: %s", resp)

    return HttpResponse(ujson.dumps(resp))


def realtime_zones(request):
    resp = {}

    now = datetime.datetime.now()
    now_timestamp = datetime.datetime.timestamp(now)

    start_time = now - datetime.timedelta(weeks=1)
    start_timestamp = datetime.datetime.timestamp(start_time)

    tweets = tweet_db.view("statistics/realtime_zone", start_key=start_timestamp, end_key=now_timestamp)

    for tweet in tweets:
        place, score = tweet.value
        if resp.get(place) is None:
            resp[place] = {}
            resp[place]['count'] = 0
            resp[place]['sum'] = 0
        resp[place]['count'] += 1
        resp[place]['sum'] += 1

    resp['start_time'] = start_time
    resp['end_time'] = now

    statistics_db.save(resp)
    return HttpResponse(ujson.dumps(resp))


if __name__ == '__main__':
    print()

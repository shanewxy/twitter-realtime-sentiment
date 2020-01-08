from backend.database.couchdb_connector import *
from backend.settings import *
# from shapely import *
from backend.topic_modeling.topic import common_topic
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging
import ujson
import datetime

logger = logging.getLogger('django')


@csrf_exempt
def tweet_upload(request):
    """
    An api to upload processed tweet into tweet database, added timestamp and score field
    :param request: a tweet json
    :return: the uploaded format
    """

    tweet = request.body
    logger.info("Received request: %s", tweet)

    tweet_json = ujson.loads(tweet)
    tweet_json['timestamp'] = datetime.datetime.timestamp(
        datetime.datetime.strptime(tweet_json['created_at'], '%a %b %d %H:%M:%S %z %Y'))
    print(tweet_json['timestamp'])
    tweet_json['sentiment'] = tweet_json['sentiment']

    if request.method == "POST":
        logger.info("Saving tweet into database...")
        tweet_id, rev = tweet_db.save(tweet_json)

    return HttpResponse(ujson.dumps(tweet_json))


def historic_zones(request):
    """
    An api returning the statistics of all of the tweets in the database historically,
    group by geo zones
    :param request:
    :return: json like: {"Melbourne":{"avg":-0.5423,"count":1}}
    """

    result = tweet_db.view("sentiment/zones_sentiment", group=True)
    resp = dict()

    for row in result:
        resp[(row.key[0], row.key[1])] = {'avg': row.value.get('sum') / row.value.get('count'),
                                          'count': row.value.get('count')}
    logger.info("response: %s", resp)

    return HttpResponse(ujson.dumps(resp))


def realtime_zones(request):
    """
    An api returning the realtime stats of tweets in the designated time period from now,
    and store the record into statistics database
    :param request:
    :return: json like: {"Melbourne":{"count":2,"sum":2.0,"avg":1.0}}
    """
    minute = request.GET.get('minute', default=5)
    resp = dict()
    now = datetime.datetime.now()
    now_timestamp = datetime.datetime.timestamp(now)

    start_time = now - datetime.timedelta(minutes=int(minute))
    start_timestamp = datetime.datetime.timestamp(start_time)

    tweets = tweet_db.view("sentiment/realtime_zone", start_key=start_timestamp, end_key=now_timestamp)

    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S%z')
    end_time = now.strftime('%Y-%m-%d %H:%M:%S%z')
    for tweet in tweets:
        name = tweet.value[0]
        code = tweet.value[1]
        score = tweet.value[2]
        user = tweet.value[3]
        key = (name, code)
        if resp.get(key) is None:
            resp[key] = {'count': 0, 'sum': 0.0, 'users': set()}
        resp[key]['count'] += 1
        resp[key]['sum'] += score
        resp[key]['users'].add(user)

    for place, score in resp.items():
        resp[place]['avg'] = score['sum'] / score['count']
        resp[place]['users_count'] = len(resp[place]['users'])
        resp[place].pop('users')
        stats = {'place': place, 'start_time': start_time, 'end_time': end_time, 'avg': resp[place]['avg'],
                 'count': score['count'], 'users_count': resp[place]['users_count']}
        statistics_db.save(stats)

    resp['start_time'] = start_time
    resp['end_time'] = end_time

    return HttpResponse(ujson.dumps(resp))


def stats_min_max(request):
    """
    An api returning the historic minimum and max in each zone
    :param request:
    :return:
    """
    stats = statistics_db.view("stats/historic_stats")
    min_stat = dict()
    max_stat = dict()
    for stat in stats:
        name = stat.key[0]
        code = stat.key[1]
        start_time = stat.key[2]
        end_time = stat.key[3]
        place = (name, code)
        count, score = stat.value
        if min_stat.get(place) is None or score < min_stat[place]["sentiment"]:
            min_stat[place] = dict()
            min_stat[place]["start_time"] = start_time
            min_stat[place]["end_time"] = end_time
            min_stat[place]["sentiment"] = score
            min_stat[place]["count"] = count

        if max_stat.get(place) is None or score > max_stat[place]["sentiment"]:
            max_stat[place] = dict()
            max_stat[place]["start_time"] = start_time
            max_stat[place]["end_time"] = end_time
            max_stat[place]["sentiment"] = score
            max_stat[place]["count"] = count

    resp = dict()
    resp["historic_min"] = min_stat
    resp["historic_max"] = max_stat
    return HttpResponse(ujson.dumps(resp))


def top_words(request):
    """
    An api used to query the top hot words
    :param request: contains end time and top limit
    :return: {start_time, end_time, words}
    """
    minute = request.GET.get('minute', default=5)
    limit = request.GET.get('limit', default=10)
    resp = dict()
    now = datetime.datetime.now()
    now_timestamp = datetime.datetime.timestamp(now)

    start_time = now - datetime.timedelta(minutes=int(minute))
    start_timestamp = datetime.datetime.timestamp(start_time)
    tweets = tweet_db.view("sentiment/tweets_content", start_key=start_timestamp, end_key=now_timestamp)

    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S%z')
    end_time = now.strftime('%Y-%m-%d %H:%M:%S%z')

    resp['start_time'] = start_time
    resp['end_time'] = end_time

    text = ""
    for tweet in tweets:
        text += tweet.value

    words = common_topic(text, limit)

    resp['top_words'] = words
    return HttpResponse(ujson.dumps(resp))


if __name__ == '__main__':
    melb_json = ujson.load(open(os.path.join(os.path.dirname(BASE_DIR), 'SA2boundary.json')))
    # print(os.path.join(os.path.dirname(BASE_DIR),'SA2boundary.json'))

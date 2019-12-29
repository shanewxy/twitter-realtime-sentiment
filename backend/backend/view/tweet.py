from backend.database.couchdb_connector import *
import ujson
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import logging

logger = logging.getLogger('django')


@csrf_exempt
def tweet_upload(request):
    tweet = request.body
    logger.info("Received request: %s", tweet)
    tweet_json = ujson.loads(tweet)
    tweet_json['score'] = tweet_json['sentiment']['compound']
    if request.method == "POST":
        logger.info("Saving tweet into database...")
        tweet_id, rev = tweet_db.save(tweet_json)
    return HttpResponse("rev:{}", rev)

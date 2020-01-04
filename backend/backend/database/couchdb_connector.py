import couchdb
import logging
from backend.config import *
from backend.database.design_docs import *

logger = logging.getLogger(__name__)


class CouchDBConnector:
    def __init__(self, url=COUCHDB_URL, domain=COUCHDB_DOMAIN, ports=COUCHDB_PORT):
        try:
            self.domain = domain
            self.ports = ports.__str__()
            self.server = couchdb.Server(url.format(domain, ports))
            self.server.create(TWEET_DB)
        except Exception as e:
            logger.error(e)

        try:
            self.server.create(STATISTICS_DB)
        except Exception as e:
            logger.error(e)

        try:
            self.tweet_db = self.server[TWEET_DB]
            self.statistics_db = self.server[STATISTICS_DB]
            self.tweet_db.save(DESIGN_DOCS_TWEETS)
        except Exception as e:
            logger.error(e)
        try:
            self.statistics_db.save(DESIGN_DOCS_STATS)
        except Exception as e:
            logger.error(e)


couchdbConnector = CouchDBConnector()
tweet_db = couchdbConnector.tweet_db
statistics_db = couchdbConnector.statistics_db

if __name__ == '__main__':
    for row in tweet_db.view("statistics/zones_sentiment", group=True):
        print(row)
    for row in tweet_db.view("statistics/all_tweets"):
        print(row)
    for row in tweet_db.view("statistics/realtime_zone"):
        print(row)

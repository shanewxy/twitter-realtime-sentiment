import couchdb
import logging
from backend.database.config import *
from backend.database.couchdb_view import *

logger = logging.getLogger(__name__)


class CouchDBConnector:
    def __init__(self, url=COUCHDB_URL, domain=COUCHDB_DOMAIN, ports=COUCHDB_PORT):
        self.domain = domain
        self.ports = ports.__str__()
        try:
            self.server = couchdb.Server(url.format(domain, ports))
            self.server.create('tweet')
        except Exception as e:
            logger.error(e)
        try:
            self.database = self.server['tweet']
            self.database.save(DESIGN_DOCS)
        except Exception as e:
            logger.error(e)


couchdbConnector = CouchDBConnector()
tweet_db = couchdbConnector.database
for tweet in tweet_db.view("statistics/zones_sentiment", group=True):
    print(tweet)

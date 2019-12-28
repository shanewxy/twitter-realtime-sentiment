import couchdb
import logging
from backend.database.config import *

logger = logging.getLogger(__name__)


class CouchDBConnector:
    def __init__(self, url=COUCHDB_URL, domain=COUCHDB_DOMAIN, ports=COUCHDB_PORT):
        self.domain = domain
        self.ports = ports.__str__()
        try:
            self.server = couchdb.Server(url.format(domain, ports))
        except Exception:
            logger.error("CouchDB connection failed")


couchdbConnector = CouchDBConnector()
couchdbServer = couchdbConnector.server
try:
    couchdbConnector.server.create('tweet')
except Exception:
    logger.error("Failed to create database")

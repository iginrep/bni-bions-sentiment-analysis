from __future__ import annotations

from functools import lru_cache
from pymongo import MongoClient
from pymongo.database import Database
from apps.api.app.config import settings


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    return MongoClient(settings.mongodb_uri)


def get_database() -> Database:
    return get_mongo_client()[settings.mongodb_database]

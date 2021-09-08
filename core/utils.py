from django.conf import settings

from pymongo import MongoClient


def connect_to_mongo():
    client = MongoClient(host=settings.MONGO_HOST)
    if settings.MONGO_PASS:
        client[settings.MONGO_DB].authenticate(settings.MONGO_USER, settings.MONGO_PASS)
    db = client[settings.MONGO_DB]
    return client, db

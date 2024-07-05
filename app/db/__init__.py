import os
from os.path import join, dirname
from pymongo import MongoClient
from dotenv import load_dotenv

import certifi

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

__all__ = ['get_db_client', 'get_database']
connection_string = os.getenv('CONNECTION_URL')


def get_db_client():
    return MongoClient(connection_string, tlsCAFile=certifi.where())


def get_database():
    client: MongoClient = get_db_client()
    return client.get_database()

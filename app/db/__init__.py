import os
from os.path import join, dirname
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.collection import Collection

from app.user.models import Users, AttemptedQuestions
from app.question.models import Topics, Questions, Answers

import certifi

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

__all__ = [
    'get_db_client',
    'get_database',
    'user_instance',
    'topics_instance',
    'answers_instance',
    'questions_instance',
    'attempted_questions_instance'
]
connection_string = os.getenv('CONNECTION_URL')


# @TODO convert this to a service
def get_db_client():
    return MongoClient(connection_string, tlsCAFile=certifi.where())


def get_database():
    client: MongoClient = get_db_client()
    return client.get_database()


def user_instance() -> Collection[Users]:
    db_connection = get_database()
    return db_connection.users


def questions_instance() -> Collection[Questions]:
    db_connection = get_database()
    return db_connection.questions


def topics_instance() -> Collection[Topics]:
    db_connection = get_database()
    return db_connection.topics


def answers_instance() -> Collection[Answers]:
    db_connection = get_database()
    return db_connection.answers


def attempted_questions_instance() -> Collection[AttemptedQuestions]:
    db_connection = get_database()
    return db_connection.attempted_questions

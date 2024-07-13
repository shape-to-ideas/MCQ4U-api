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
    'DatabaseService'
]
connection_string = os.getenv('CONNECTION_URL')


class DatabaseService:
    @staticmethod
    def get_db_client():
        return MongoClient(connection_string, tlsCAFile=certifi.where())

    def get_database(self):
        client: MongoClient = self.get_db_client()
        return client.get_database()

    def user_instance(self) -> Collection[Users]:
        db_connection = self.get_database()
        return db_connection.users

    def questions_instance(self) -> Collection[Questions]:
        db_connection = self.get_database()
        return db_connection.questions

    def topics_instance(self) -> Collection[Topics]:
        db_connection = self.get_database()
        return db_connection.topics

    def answers_instance(self) -> Collection[Answers]:
        db_connection = self.get_database()
        return db_connection.answers

    def attempted_questions_instance(self) -> Collection[AttemptedQuestions]:
        db_connection = self.get_database()
        return db_connection.attempted_questions

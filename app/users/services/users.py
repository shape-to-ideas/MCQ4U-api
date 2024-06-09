import json
from app.db import get_database
from app.users.domain.users import RegisterUser
from pprint import pprint

__all__ = ['UserService']


class UserService:

    @staticmethod
    def user_instance():
        db_connection = get_database()
        return db_connection.users

    def register_user(self, user_payload: RegisterUser):
        email = user_payload.email
        users_collection = self.user_instance()
        # user_data = users_collection.find_one(
        #     {'email': email}, {'_id': 0, '__v': 0, 'password': 0}
        # )

        # if user_data:
        #     return json.dumps({'error': 'Email Already Registered'})
        return "end"
        # return self.insert_user(email=user_email)

    def insert_user(self, email: str, username: str, firstname: str, lastname: str):
        return self.user_instance().insert_one({'email': email, })

import json
from typing import Dict, Any

from app.db import get_database
from app.user.domains import RegisterUserDto, LoginUserDto
import bcrypt
import os
from os.path import join, dirname
from dotenv import load_dotenv
from app.shared.constants import ENCODING_FORMAT, ErrorMessages, JWT_ENCODE
import jwt
from app.shared.utils import current_date, date_to_epoch, epoch_in_milliseconds
from litestar.exceptions import ValidationException

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

__all__ = ['UserService']


def encrypt_password(password: str):
    rounds = os.getenv('SALT_ROUNDS')
    salt = bcrypt.gensalt(
        rounds=int(rounds)
    )
    return bcrypt.hashpw(
        password=password.encode(ENCODING_FORMAT),
        salt=salt
    )


class UserService:

    @staticmethod
    def user_instance():
        db_connection = get_database()
        return db_connection.users

    def register_user(self, user_payload: RegisterUserDto):
        phone = user_payload.phone
        users_collection = self.user_instance()
        user_data = users_collection.find_one(
            {'phone': phone}, {'_id': 0, '__v': 0, 'password': 0}
        )

        if user_data:
            return json.dumps({'error': ErrorMessages.ACCOUNT_ALREADY_EXISTS.value})
        return self.insert_user(user_payload)

    def insert_user(self, user: RegisterUserDto):
        password_string = encrypt_password(user.password)
        self.user_instance().insert_one({
            'email': user.email,
            'firstname': user.first_name,
            'lastName': user.last_name,
            'phone': user.phone,
            'password': password_string.decode(ENCODING_FORMAT),
            'isAdmin': user.is_admin
        })
        return True

    def login(self, login_payload: LoginUserDto):
        jwt_secret = os.getenv('JWT_SECRET')

        users_collection = self.user_instance()
        agg_cursor = users_collection.aggregate(
            [
                {'$match': {'phone': login_payload.phone}},
                {'$project': {"id": {'$toString': "$_id"}, "_id": 0, "isAdmin": 1}},
                {'$limit': 1}
            ]
        )

        record_list = list(agg_cursor)
        if len(record_list) == 0:
            raise ValidationException(detail="User does not exist")

        user_data = record_list[0]

        current_epoch_date = date_to_epoch(current_date())
        encoded = jwt.encode(
            {"isAdmin": user_data["isAdmin"], "id": user_data["id"],
             "expiry": epoch_in_milliseconds(current_epoch_date)},
            jwt_secret, algorithm=JWT_ENCODE)
        if not encoded:
            raise ValidationException(detail="Invalid Token Generated")

        return {"token": encoded}

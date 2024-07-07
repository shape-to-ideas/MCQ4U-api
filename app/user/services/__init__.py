import bcrypt
import os
import jwt
from app.db import get_database
from app.user.domains import RegisterUserDto, LoginUserDto
from os.path import join, dirname
from dotenv import load_dotenv
from litestar.exceptions import ValidationException
from pymongo.collection import Collection

from app.shared.constants import ENCODING_FORMAT, ErrorMessages, JWT_ENCODE
from app.shared.utils import current_date, date_to_epoch, epoch_in_milliseconds
from app.user.models import Users

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


def validate_password(user_password: str, encrypted_pass: str) -> bool:
    pass_hash = encrypted_pass.encode(ENCODING_FORMAT)
    user_password_hash = user_password.encode(ENCODING_FORMAT)
    if bcrypt.checkpw(user_password_hash, pass_hash):
        return True
    else:
        raise ValidationException(detail=ErrorMessages.INVALID_LOGIN_PASSWORD.value)


class UserService:

    @staticmethod
    def user_instance() -> Collection[Users]:
        db_connection = get_database()
        return db_connection.users

    def register_user(self, user_payload: RegisterUserDto):
        users_collection = self.user_instance()
        user_data = users_collection.count_documents(
            {'$or': [
                {'phone': user_payload.phone},
                {'email': user_payload.email}
            ]}
        )

        if user_data:
            raise ValidationException(detail=ErrorMessages.ACCOUNT_ALREADY_EXISTS.value)
        inserted_user = self.insert_user(user_payload)
        print({'id': str(inserted_user.inserted_id)})
        return {'id': str(inserted_user.inserted_id)}

    def insert_user(self, user: RegisterUserDto):
        password_string = encrypt_password(user.password)
        return self.user_instance().insert_one({
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'password': password_string.decode(ENCODING_FORMAT),
            'is_admin': user.is_admin,
            'is_active': True
        })

    def login(self, login_payload: LoginUserDto):
        jwt_secret = os.getenv('JWT_SECRET')

        users_collection = self.user_instance()
        agg_cursor = users_collection.aggregate(
            [
                {'$match': {'phone': login_payload.phone}},
                {'$project': {"id": {'$toString': "$_id"}, "_id": 0, "is_admin": 1, 'password': 1}},
                {'$limit': 1}
            ]
        )

        record_list = list(agg_cursor)
        if len(record_list) == 0:
            raise ValidationException(detail="User does not exist")

        user_data = record_list[0]

        validate_password(login_payload.password, user_data['password'])

        current_epoch_date = date_to_epoch(current_date())
        encoded = jwt.encode(
            {"is_admin": user_data["is_admin"], "id": user_data["id"],
             "expiry": epoch_in_milliseconds(current_epoch_date)},
            jwt_secret, algorithm=JWT_ENCODE)
        if not encoded:
            raise ValidationException(detail="Invalid Token Generated")

        return {"token": encoded}

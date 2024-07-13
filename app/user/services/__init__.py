import bcrypt
import os
import jwt
from os.path import join, dirname
from dotenv import load_dotenv
from litestar.exceptions import ValidationException, NotAuthorizedException
from bson.objectid import ObjectId

from app.shared.constants import ENCODING_FORMAT, ErrorMessages, JWT_ENCODE
from app.shared.utils import current_timestamp, parse_token, token_expiry_time, current_time_string
from app.user.domains import AttemptQuestionDto
from app.db import user_instance, questions_instance, attempted_questions_instance
from app.user.domains import RegisterUserDto, LoginUserDto

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


def validate_auth_token(jwt_token: str):
    try:
        jwt_secret = os.getenv('JWT_SECRET')
        jwt_decode = jwt.decode(jwt_token, jwt_secret, algorithms=JWT_ENCODE)
        token_time = jwt_decode['expiry']
        if token_time > current_timestamp():
            return jwt_decode['id']
        else:
            raise ValidationException(detail=ErrorMessages.INVALID_TOKEN.value)
    except:
        raise ValidationException(detail=ErrorMessages.INVALID_TOKEN.value)


def validate_password(user_password: str, encrypted_pass: str) -> bool:
    pass_hash = encrypted_pass.encode(ENCODING_FORMAT)
    user_password_hash = user_password.encode(ENCODING_FORMAT)
    if bcrypt.checkpw(user_password_hash, pass_hash):
        return True
    else:
        raise ValidationException(detail=ErrorMessages.INVALID_LOGIN_PASSWORD.value)


class UserService:
    def register_user(self, user_payload: RegisterUserDto):
        users_collection = user_instance()
        user_data = users_collection.count_documents(
            {'$or': [
                {'phone': user_payload.phone},
                {'email': user_payload.email}
            ]}
        )

        if user_data:
            raise ValidationException(detail=ErrorMessages.ACCOUNT_ALREADY_EXISTS.value)
        inserted_user = self.insert_user(user_payload)
        return {'id': str(inserted_user.inserted_id)}

    @staticmethod
    def get_user_details(user_id: str):
        user_details = user_instance().find_one({"_id": ObjectId(user_id)})
        if not user_details:
            raise NotAuthorizedException(ErrorMessages.INVALID_USER)
        return user_details

    @staticmethod
    def insert_user(user: RegisterUserDto):
        password_string = encrypt_password(user.password)
        return user_instance().insert_one({
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'password': password_string.decode(ENCODING_FORMAT),
            'is_admin': user.is_admin,
            'is_active': True,
            'created_at': current_time_string(),
            'updated_at': current_time_string()
        })

    @staticmethod
    def login(login_payload: LoginUserDto):
        jwt_secret = os.getenv('JWT_SECRET')

        users_collection = user_instance()
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

        encoded = jwt.encode(
            {"is_admin": user_data["is_admin"], "id": user_data["id"],
             "expiry": token_expiry_time()},
            jwt_secret, algorithm=JWT_ENCODE)
        if not encoded:
            raise ValidationException(detail="Invalid Token Generated")

        return {"token": encoded}

    def attempt_question(self, token: str, attempt_question_payload: AttemptQuestionDto):
        token_str = parse_token(token)
        user_id = validate_auth_token(token_str)

        user_details = self.get_user_details(user_id)

        question_details = questions_instance().find_one({"_id": ObjectId(attempt_question_payload.question_id)})
        if not question_details:
            raise ValidationException(ErrorMessages.INVALID_QUESTION_ID.value)

        attempted_entry = attempted_questions_instance().insert_one({
            'user_id': user_details['_id'].__str__(),
            'question_id': question_details['_id'].__str__(),
            'option': attempt_question_payload.option.value,
            'created_at': current_time_string(),
            'updated_at': current_time_string()
        })
        return {'id': str(attempted_entry.inserted_id)}

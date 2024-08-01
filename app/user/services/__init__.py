import bcrypt
import os
import jwt
import json
from os.path import join, dirname
from dotenv import load_dotenv
from litestar.exceptions import ValidationException, NotAuthorizedException
from bson import ObjectId, json_util
from litestar.types import Scope

from app.shared.constants import ENCODING_FORMAT, ErrorMessages, JWT_ENCODE
from app.shared.utils import token_expiry_time, current_time_string
from app.user.domains import AttemptQuestionDto
from app.db import DatabaseService
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


def validate_password(user_password: str, encrypted_pass: str) -> bool:
    pass_hash = encrypted_pass.encode(ENCODING_FORMAT)
    user_password_hash = user_password.encode(ENCODING_FORMAT)
    if bcrypt.checkpw(user_password_hash, pass_hash):
        return True
    else:
        raise ValidationException(detail=ErrorMessages.INVALID_LOGIN_PASSWORD.value)


class UserService:
    database_service = DatabaseService()

    def register_user(self, user_payload: RegisterUserDto):
        users_collection = self.database_service.user_instance()
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

    def get_user_details(self, user_id: str):
        user_details = self.database_service.user_instance().find_one({"_id": ObjectId(user_id)})
        if not user_details:
            raise NotAuthorizedException(ErrorMessages.INVALID_USER)
        return user_details

    def insert_user(self, user: RegisterUserDto):
        password_string = encrypt_password(user.password)
        return self.database_service.user_instance().insert_one({
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

    def login(self, login_payload: LoginUserDto):
        jwt_secret = os.getenv('JWT_SECRET')

        users_collection = self.database_service.user_instance()
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

    def attempt_question(self, attempt_question_payload: AttemptQuestionDto, scope: Scope):
        user_id = scope['user_auth_data']['id']

        user_details = self.get_user_details(user_id)

        question_details = self.database_service.questions_instance().find_one(
            {"_id": ObjectId(attempt_question_payload.question_id)})
        if not question_details:
            raise ValidationException(ErrorMessages.INVALID_QUESTION_ID.value)

        existing_attempt = self.database_service.attempted_questions_instance().find_one({
            'question_id': attempt_question_payload.question_id,
            'user_id': user_id
        }, {'_id': True})
        print(existing_attempt)

        if existing_attempt:
            raise ValidationException(ErrorMessages.QUESTION_ALREADY_ATTEMPTED.value)

        attempted_entry = self.database_service.attempted_questions_instance().insert_one({
            'user_id': user_details['_id'].__str__(),
            'question_id': question_details['_id'].__str__(),
            'option': attempt_question_payload.option.value,
            'created_at': current_time_string(),
            'updated_at': current_time_string()
        })
        return {'id': str(attempted_entry.inserted_id)}

    def get_attempted_questions(self, topic_id: str, scope: Scope):
        user_id = scope['user_auth_data']['id']
        questions_instance = self.database_service.questions_instance()
        questions_cursor = questions_instance.aggregate([
            {
                "$lookup": {
                    "let": {"topicObjId": {"$toObjectId": "$topic_id"}},
                    "from": "topics",
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$_id", "$$topicObjId"]}}}
                    ],
                    "as": "topics"
                }
            }
            , {
                "$lookup": {
                    "let": {"question_id_str": {"$toString": "$_id"}},
                    "from": "attempted_questions",
                    "pipeline": [
                        {
                            "$match": {
                                "$and": [
                                    {"$expr": {"$eq": ["$question_id", "$$question_id_str"]}},
                                    {"user_id": user_id}
                                ]
                            }
                        }
                    ],
                    "as": "attempted_questions"
                }
            }
            , {
                "$lookup": {
                    "let": {"question_id_str": {"$toString": "$_id"}},
                    "from": "answers",
                    "pipeline": [
                        {
                            "$match": {
                                "$and": [
                                    {"$expr": {"$eq": ["$question_id", "$$question_id_str"]}},
                                ]
                            }
                        }
                    ],
                    "as": "correct_answer"
                }
            }
        ])

        questions_list = list(questions_cursor)
        json_result = json.loads(json_util.dumps(questions_list))
        return json_result

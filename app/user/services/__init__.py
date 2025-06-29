import bcrypt
import os
import jwt
import json
from os.path import join, dirname
from dotenv import load_dotenv
from litestar.exceptions import ValidationException, NotAuthorizedException
from bson import ObjectId, json_util
from litestar.types import Scope
from pymongo.collection import Collection

from app.shared.constants import ENCODING_FORMAT, ErrorMessages, JWT_ENCODE
from app.shared.utils import token_expiry_time, current_time_string
from app.user.domains import AttemptQuestionDto
from app.db import DatabaseService
from app.user.domains import RegisterUserDto, LoginUserDto
from app.shared.utils import find_in_list
from app.shared.logger import logger
from app.user.models import Users

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

__all__ = ['UserService']


def encrypt_password(password: str) -> bytes:
    rounds = os.getenv('SALT_ROUNDS').__str__()
    salt = bcrypt.gensalt(rounds=int(rounds))
    return bcrypt.hashpw(password=password.encode(ENCODING_FORMAT), salt=salt)


def validate_password(user_password: str, encrypted_pass: str) -> bool:
    pass_hash = encrypted_pass.encode(ENCODING_FORMAT)
    user_password_hash = user_password.encode(ENCODING_FORMAT)
    if bcrypt.checkpw(user_password_hash, pass_hash):
        return True
    else:
        raise ValidationException(detail=ErrorMessages.INVALID_LOGIN_PASSWORD.value)


class UserService:
    database_service = DatabaseService()

    def register_user(self, user_payload: RegisterUserDto) -> dict[str, str]:
        users_collection = self.database_service.user_instance()
        user_data = users_collection.count_documents(
            {'$or': [{'phone': user_payload.phone}, {'email': user_payload.email}]}
        )

        if user_data:
            raise ValidationException(detail=ErrorMessages.ACCOUNT_ALREADY_EXISTS.value)
        inserted_user = self.insert_user(user_payload)
        return {'id': str(inserted_user.inserted_id)}

    def get_user_details(self, user_id: str):
        user_details = self.database_service.user_instance().find_one(
            {'_id': ObjectId(user_id)}
        )
        if not user_details:
            raise NotAuthorizedException(ErrorMessages.INVALID_USER)
        return user_details

    def insert_user(self, user: RegisterUserDto):
        password_string = encrypt_password(user.password)
        return self.database_service.user_instance().insert_one(
            {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'password': password_string.decode(ENCODING_FORMAT),
                'is_admin': user.is_admin,
                'is_active': True,
                'created_at': current_time_string(),
                'updated_at': current_time_string(),
            }
        )

    def login(self, login_payload: LoginUserDto) -> dict[str, str]:
        jwt_secret = os.getenv('JWT_SECRET')

        users_collection = self.database_service.user_instance()
        agg_cursor = users_collection.aggregate(
            [
                {'$match': {'phone': login_payload.phone}},
                {
                    '$project': {
                        'id': {'$toString': '$_id'},
                        '_id': 0,
                        'is_admin': 1,
                        'password': 1,
                        'first_name': 1,
                        'last_name': 1,
                        'email': 1,
                    }
                },
                {'$limit': 1},
            ]
        )

        record_list = list(agg_cursor)
        if len(record_list) == 0:
            raise ValidationException(detail='User does not exist')

        user_data = record_list[0]

        validate_password(login_payload.password, user_data['password'])

        encoded = jwt.encode(
            {
                'is_admin': user_data['is_admin'],
                'id': user_data['id'],
                'expiry': token_expiry_time(),
                'first_name': user_data['first_name'],
                'email': user_data['email'],
                'last_name': user_data['last_name'],
            },
            jwt_secret,
            algorithm=JWT_ENCODE,
        )
        if not encoded:
            raise ValidationException(detail='Invalid Token Generated')

        return {'token': encoded}

    def attempt_questions(
            self, attempt_question_payload: list[AttemptQuestionDto], scope: Scope
    ):
        user_id = scope['user_auth_data']['id']
        user_details = self.get_user_details(user_id)

        questions_collection = self.database_service.questions_instance()
        question_attempt_details = self.get_attempted_question_by_question_ids(
            questions_collection=questions_collection,
            attempt_question_payload=attempt_question_payload,
            user_id=user_id,
        )

        attempts_to_insert = self.filter_unattempted_questions(
            attempt_question_payload, question_attempt_details, user_details
        )

        if len(attempts_to_insert):
            attempted_entry = self.database_service.attempted_questions_instance().insert_many(attempts_to_insert)
            return {'id': str(attempted_entry.inserted_ids)}
            # return attempts_to_insert
        else:
            return {}

    @staticmethod
    def filter_unattempted_questions(
            attempt_question_payload: list[AttemptQuestionDto],
            question_attempt_details,
            user_details: Users,
    ):
        filtered_unattempted_questions = []
        for attempt_input in attempt_question_payload:
            existing_question = find_in_list(
                question_attempt_details, 'id', attempt_input.question_id
            )
            logger.info(attempt_input.question_id)
            if not existing_question:
                logger.info(f'Invalid Question Payload: {attempt_input.question_id}')
                continue

            if existing_question['attempted_questions']:
                logger.info('Question Already Attempted')
                continue

            filtered_unattempted_questions.append(
                {
                    'user_id': user_details['_id'].__str__(),
                    'question_id': attempt_input.question_id,
                    'option': attempt_input.option.value,
                    'created_at': current_time_string(),
                    'updated_at': current_time_string(),
                }
            )
        return filtered_unattempted_questions

    @staticmethod
    def get_attempted_question_by_question_ids(
            questions_collection: Collection[any],
            attempt_question_payload: list[AttemptQuestionDto],
            user_id: str,
    ):
        question_object_ids = []
        for question in attempt_question_payload:
            question_object_ids.append(ObjectId(question.question_id))

        question_details = questions_collection.aggregate(
            [
                {
                    '$match': {'_id': {'$in': question_object_ids}, 'is_active': True},
                },
                {
                    '$lookup': {
                        'let': {'questionIdStr': {'$toString': '$_id'}},
                        'from': 'attempted_questions',
                        'pipeline': [
                            {
                                '$match': {
                                    '$and': [
                                        {
                                            '$expr': {
                                                '$eq': [
                                                    '$question_id',
                                                    '$$questionIdStr',
                                                ]
                                            }
                                        },
                                        {'$expr': {'$eq': ['$user_id', user_id]}},
                                    ],
                                },
                            },
                        ],
                        'as': 'attempted_questions',
                    },
                },
                {
                    '$project': {
                        '_id': False,
                        'id': {'$toString': '$_id'},
                        'attempted_questions': {
                            '$id': True,
                            'id': {'$toString': '$_id'},
                        },
                    },
                },
            ]
        )
        return list(question_details)

    def get_attempted_questions(self, topic_id: str, scope: Scope):
        user_id = scope['user_auth_data']['id']
        questions_instance = self.database_service.questions_instance()
        questions_cursor = questions_instance.aggregate(
            [
                {'$match': {'topic_id': topic_id, 'is_active': True}},
                {
                    '$lookup': {
                        'let': {'topicObjId': {'$toObjectId': '$topic_id'}},
                        'from': 'topics',
                        'pipeline': [
                            {'$match': {'$expr': {'$eq': ['$_id', '$$topicObjId']}}}
                        ],
                        'as': 'topics',
                    }
                },
                {
                    '$lookup': {
                        'let': {'question_id_str': {'$toString': '$_id'}},
                        'from': 'attempted_questions',
                        'pipeline': [
                            {
                                '$match': {
                                    '$and': [
                                        {
                                            '$expr': {
                                                '$eq': [
                                                    '$question_id',
                                                    '$$question_id_str',
                                                ]
                                            }
                                        },
                                        {'user_id': user_id},
                                    ]
                                }
                            }
                        ],
                        'as': 'attempted_questions',
                    }
                },
                {
                    '$lookup': {
                        'let': {'question_id_str': {'$toString': '$_id'}},
                        'from': 'answers',
                        'pipeline': [
                            {
                                '$match': {
                                    '$and': [
                                        {
                                            '$expr': {
                                                '$eq': [
                                                    '$question_id',
                                                    '$$question_id_str',
                                                ]
                                            }
                                        },
                                    ]
                                }
                            }
                        ],
                        'as': 'correct_answer',
                    }
                },
            ]
        )

        questions_list = list(questions_cursor)
        json_result = json.loads(json_util.dumps(questions_list))
        return json_result

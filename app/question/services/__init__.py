import json
from os.path import join, dirname
from dotenv import load_dotenv
from typing import List, Optional
from litestar.exceptions import HTTPException, ValidationException
from litestar.types import Scope
from bson import json_util, ObjectId, errors as bson_errors
from pymongo import errors as mongo_errors

from app.question.domains import (
    CreateQuestionsDto,
    CreateTopicsDto,
    Options,
    QuestionPayload,
)
from app.question.models import Topics
from app.shared.constants import ErrorMessages
from app.shared.utils import current_time_string
from app.db import DatabaseService

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

__all__ = ['QuestionService']


class TopicsResponseType:
    name: str


def prepare_topics_payload(topic_names: [str], user_id: str):
    topics_payload = []
    for name in topic_names:
        topics_payload.append({'name': name, 'created_by': user_id})
    return topics_payload


def filter_existing_topics(topics_dto: CreateTopicsDto, existing_topics: List[Topics]):
    existing_topic_names = []
    for topic_object in existing_topics:
        existing_topic_names.append(topic_object.get('name'))

    new_topics: [str] = []
    for topic in topics_dto.topic_names:
        if topic not in existing_topic_names:
            new_topics.append(topic)

    return new_topics


# @TODO need to be optimised
def generate_options_list(options: list[Options]):
    options_list = []
    for option in options:
        option_string = option.model_dump_json()
        option_json = json.loads(option_string)
        options_list.append(option_json)
    return options_list


class QuestionService:
    database_service = DatabaseService()

    def validate_topic_id(self, topic_id: str):
        topics_collection = self.database_service.topics_instance()
        try:
            topic_id_object = ObjectId(topic_id)
            topic = topics_collection.find_one({'_id': topic_id_object})
            if not topic:
                raise HTTPException(
                    detail=ErrorMessages.INVALID_TOPIC.value, status_code=400
                )
        except HTTPException:
            raise HTTPException(
                detail=ErrorMessages.INVALID_TOPIC.value, status_code=400
            )

    def create_question(self, question_dto: CreateQuestionsDto, scope: Scope):
        try:
            questions_collection = self.database_service.questions_instance()
            user_id = scope['user_auth_data']['id']

            questions_list = self.prepare_questions_list(question_dto, user_id)
            inserted_questions = questions_collection.insert_many(questions_list)
            newly_added_questions = questions_collection.find(
                {'_id': {'$in': inserted_questions.inserted_ids}}
            )
            self.insert_answers(list(newly_added_questions), question_dto.data)

            return 'done'
        except mongo_errors.BulkWriteError as e:
            print(e)
            raise ValidationException(ErrorMessages.QUESTIONS_BULK_CREATE_ERROR.value)

    def create_topics(
            self, topics_dto: CreateTopicsDto, scope: Scope
    ) -> [TopicsResponseType]:
        topics_collection = self.database_service.topics_instance()
        existing_topics = topics_collection.find({}, {'name': 1})
        topics_list: List[Topics] = list(existing_topics)
        user_id = scope['user_auth_data']['id']

        topics_to_insert = []
        if not len(topics_list):
            topics_to_insert = prepare_topics_payload(topics_dto.topic_names, user_id)
            topics_collection.insert_many(topics_to_insert)
        else:
            filtered_new_topics = filter_existing_topics(topics_dto, topics_list)
            if len(filtered_new_topics):
                topics_to_insert = prepare_topics_payload(filtered_new_topics, user_id)
                topics_collection.insert_many(topics_to_insert)

        json_result = json.loads(json_util.dumps(topics_to_insert))
        return json_result

    def get_questions(
            self, topic_id: str, is_active: str, question_id: Optional[str],
    ) -> [CreateQuestionsDto]:
        questions_instance = self.database_service.questions_instance()

        if question_id:
            question_cursor = questions_instance.find(
                {
                    '_id': ObjectId(question_id),
                    'is_active': False if is_active == 'false' else True,
                }
            )
            json_result = json.loads(json_util.dumps(question_cursor))
            return json_result

        if topic_id:
            question_cursor = questions_instance.find(
                {
                    'topic_id': topic_id,
                    'is_active': False if is_active == 'false' else True,
                }
            )
            questions_list = list(question_cursor)
            json_result = json.loads(json_util.dumps(questions_list))
            return json_result

    def get_topics_list(self):
        topics_instance = self.database_service.topics_instance()
        topics_cursor = topics_instance.find()
        topics = json.loads(json_util.dumps(topics_cursor))
        return topics

    def insert_answers(self, created_questions, questions_dto: List[QuestionPayload]):
        answers_payload = []
        for question in created_questions:
            question_id = str(question['_id'])
            question_from_payload = [
                payload_question
                for payload_question in questions_dto
                if payload_question.title == question['title']
            ]
            current_question_from_payload = list(question_from_payload)[0]
            answers_payload.append(
                {
                    'question_id': question_id,
                    'answer': current_question_from_payload.answer.value,
                    'created_at': current_time_string(),
                    'updated_at': current_time_string(),
                }
            )

        answers_collection = self.database_service.answers_instance()
        answers_collection.insert_many(answers_payload)

    def prepare_questions_list(self, questions_dto: CreateQuestionsDto, user_id: str):
        topics_payload = []
        for question in questions_dto.data:
            try:
                self.validate_topic_id(question.topic_id)
                options_list = generate_options_list(question.options)
                topics_payload.append(
                    {
                        'title': question.title,
                        'options': options_list,
                        'tags': question.tags,
                        'is_active': question.is_active,
                        'topic_id': question.topic_id,
                        'created_at': current_time_string(),
                        'updated_at': current_time_string(),
                        'created_by': user_id,
                    }
                )
            except bson_errors.InvalidId:
                raise ValidationException(ErrorMessages.INVALID_OBJECT_ID.value)

        return topics_payload

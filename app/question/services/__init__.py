import json
from os.path import join, dirname
from dotenv import load_dotenv
from typing import List
from litestar.exceptions import HTTPException, ValidationException
from litestar.types import Scope
from bson import json_util, ObjectId
from pymongo import errors

from app.question.domains import CreateQuestionsDto, CreateTopicsDto, Options
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
        topics_payload.append({"name": name, 'created_by': user_id})
    return topics_payload


def filter_existing_topics(topics_dto: CreateTopicsDto, existing_topics: List[Topics]):
    existing_topic_names = []
    for topic_object in existing_topics:
        existing_topic_names.append(topic_object.get("name"))

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
            topic = topics_collection.find_one({"_id": topic_id_object})
            if not topic:
                raise HTTPException(detail=ErrorMessages.INVALID_TOPIC.value, status_code=400)
        except HTTPException:
            raise HTTPException(detail=ErrorMessages.INVALID_TOPIC.value, status_code=400)

    def create_question(self, question_dto: CreateQuestionsDto, scope: Scope):
        try:
            questions_collection = self.database_service.questions_instance()
            user_id = scope['user_auth_data']['id']

            self.validate_topic_id(question_dto.topic_id)

            options_list = generate_options_list(question_dto.options)
            created_question = questions_collection.insert_one({
                "title": question_dto.title,
                "options": options_list,
                "tags": question_dto.tags,
                "is_active": question_dto.is_active,
                "topic_id": question_dto.topic_id,
                'created_at': current_time_string(),
                'updated_at': current_time_string(),
                'created_by': user_id
            })
            question_id = str(created_question.inserted_id)

            answers_collection = self.database_service.answers_instance()
            answers_collection.insert_one({
                'question_id': question_id,
                'answer': question_dto.answer.value,
                'created_at': current_time_string(),
                'updated_at': current_time_string()}
            )
            return {"inserted_question_id": question_id}
        except errors.DuplicateKeyError:
            raise ValidationException(ErrorMessages.DUPLICATE_QUESTION.value)

    def create_topics(self, topics_dto: CreateTopicsDto, scope: Scope) -> [TopicsResponseType]:
        topics_collection = self.database_service.topics_instance()
        existing_topics = topics_collection.find({}, {"name": 1})
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

    def get_questions(self, topic_id: str, question_id: str) -> [CreateQuestionsDto]:
        questions_instance = self.database_service.questions_instance()

        if question_id:
            question_cursor = questions_instance.find({'_id': ObjectId(question_id)})
            json_result = json.loads(json_util.dumps(question_cursor))
            return json_result

        if topic_id:
            question_cursor = questions_instance.find({'topic_id': topic_id})
            questions_list = list(question_cursor)
            json_result = json.loads(json_util.dumps(questions_list))
            return json_result

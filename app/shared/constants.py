from enum import Enum

__all__ = ['ENCODING_FORMAT', 'ErrorMessages', 'JWT_ENCODE', 'AnswerOptionKeys']

ENCODING_FORMAT = 'utf-8'

JWT_ENCODE = 'HS256'


class ErrorMessages(Enum):
    BAD_REQUEST = 'Bad Request'
    INVALID_OBJECT_ID = 'Invalid Object Id'
    ACCOUNT_ALREADY_EXISTS = 'Account with this email or phone number already exists'
    INVALID_TOKEN = 'Invalid Token provided'
    INVALID_USER = ('Invalid User',)
    INVALID_LOGIN_PASSWORD = ('Invalid Login Password',)
    INVALID_TOPIC = 'Invalid Topic Id'
    INVALID_QUESTION_ID = ('Invalid Question ID',)
    QUESTION_ALREADY_ATTEMPTED = 'Question Already Attempted'
    QUESTIONS_BULK_CREATE_ERROR = 'Error creating questions'
    DUPLICATE_QUESTION = 'Question already exists'


class AnswerOptionKeys(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'

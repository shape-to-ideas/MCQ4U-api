from enum import Enum

__all__ = ['ENCODING_FORMAT', 'ErrorMessages', 'JWT_ENCODE', 'AnswerOptionKeys']

ENCODING_FORMAT = 'utf-8'

JWT_ENCODE = 'HS256'


class ErrorMessages(Enum):
    ACCOUNT_ALREADY_EXISTS = 'Account with these credentials already exists'
    INVALID_TOPIC = 'Invalid Topic Id'


class AnswerOptionKeys(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'

from enum import Enum

__all__ = [
    'ENCODING_FORMAT',
    'ErrorMessages',
    'Messages',
    'JWT_ENCODE',
    'AnswerOptionKeys',
    'RESET_TOKEN_EXPIRY_SECONDS',
]

ENCODING_FORMAT = 'utf-8'

JWT_ENCODE = 'HS256'

RESET_TOKEN_EXPIRY_SECONDS = 3600


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
    INVALID_RESET_TOKEN = 'Invalid or expired reset token'


class Messages(Enum):
    PASSWORD_RESET_REQUESTED = (
        'If that email is registered, a password reset link has been sent.'
    )
    PASSWORD_RESET_SUCCESS = 'Password has been reset successfully.'


class AnswerOptionKeys(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'

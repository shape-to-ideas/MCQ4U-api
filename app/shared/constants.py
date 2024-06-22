from enum import Enum

__all__ = ['ENCODING_FORMAT', 'ErrorMessages', 'JWT_ENCODE']

ENCODING_FORMAT = 'utf-8'

JWT_ENCODE = 'HS256'


class ErrorMessages(Enum):
    ACCOUNT_ALREADY_EXISTS = 'Account with these credentials already exists'

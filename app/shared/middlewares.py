import logging
import os
import jwt

from litestar.types import ASGIApp, Receive, Scope, Send
from litestar import Request
from litestar.middleware.base import MiddlewareProtocol
from litestar.exceptions import ValidationException, NotAuthorizedException
from bson import ObjectId

from app.shared.constants import ErrorMessages, JWT_ENCODE
from app.shared.utils import current_timestamp, parse_token
from app.db import DatabaseService

logger = logging.getLogger(__name__)

__all__ = ['AuthorizationMiddleware']


class AuthorizationMiddleware(MiddlewareProtocol):
    database_service = DatabaseService()

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope)
        try:
            auth_token_string = request.headers["authorization"].__str__()
            user = self.validate_auth_token(auth_token_string)
            self.validate_user(user['id'])
            scope['user_auth_data'] = user
        except KeyError:
            raise NotAuthorizedException()

        await self.app(scope, receive, send)

    def validate_user(self, user_id: str):
        user_instance = self.database_service.user_instance()
        user_details_cursor = user_instance.find_one({'_id': ObjectId(user_id)}, {'_id': True})
        if not user_details_cursor:
            raise NotAuthorizedException(ErrorMessages.INVALID_USER.value)

    @staticmethod
    def validate_auth_token(token: str):
        try:
            token_str = parse_token(token)
            jwt_secret = os.getenv('JWT_SECRET')
            jwt_decode = jwt.decode(token_str, jwt_secret, algorithms=JWT_ENCODE)
            token_time = jwt_decode['expiry']
            if token_time > current_timestamp():
                return jwt_decode
            else:
                raise ValidationException(detail=ErrorMessages.INVALID_TOKEN.value)
        except:
            raise ValidationException(detail=ErrorMessages.INVALID_TOKEN.value)

from litestar import Controller, post, get
from typing import Annotated
from litestar.params import Body, Parameter
from litestar.di import Provide
from litestar.types import Scope

from app.user.services import UserService
from app.user.domains import RegisterUserDto, LoginUserDto, LoginResponse, RegisterUserResponse
from app.user.domains import AttemptQuestionDto, AttemptQuestionResponse
from app.shared.middlewares import AuthorizationMiddleware

__all__ = [
    'UserController',
]


class UserController(Controller):
    tags = ['Users']
    dependencies = {
        "user_service": Provide(UserService, sync_to_thread=False),
    }

    signature_namespace = {
        "UserService": UserService,
    }

    @post('/user/register', sync_to_thread=False)
    def register_user(
            self,
            data: Annotated[RegisterUserDto, Body(title="Create User", description="Create a new user.")],
            user_service: UserService,
    ) -> RegisterUserResponse:
        return user_service.register_user(user_payload=data)

    @post('/user/login', sync_to_thread=False)
    def login(self,
              data: Annotated[LoginUserDto, Body(title="Create User", description="Create a new user.")],
              user_service: UserService
              ) -> LoginResponse:
        return user_service.login(login_payload=data)

    @get('/user', middleware=[AuthorizationMiddleware], sync_to_thread=False)
    def user_details(self,
                     user_service: UserService,
                     scope: Scope
                     ) -> LoginResponse:
        user_auth_details = scope["user_auth_data"]
        user_id = user_auth_details["id"]
        return user_service.get_user_details(user_id)

    @post('/user/attempt_question', middleware=[AuthorizationMiddleware], sync_to_thread=False)
    def attempt_question(self,
                         data: Annotated[
                             AttemptQuestionDto, Body(title="Attempt Question", description="Attempt a Question")],
                         token: Annotated[str, Parameter(header="Authorization")],
                         user_service: UserService,
                         scope: Scope
                         ) -> AttemptQuestionResponse:
        return user_service.attempt_question(attempt_question_payload=data, scope=scope)

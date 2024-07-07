from litestar import Controller, post
from typing import Annotated
from app.user.services import UserService
from litestar.params import Body
from litestar.di import Provide
from app.user.domains import RegisterUserDto, LoginUserDto, LoginResponse, RegisterUserResponse

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
              user_service: UserService) -> LoginResponse:
        return user_service.login(login_payload=data)

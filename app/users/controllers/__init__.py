from litestar import Router

from . import users

__all__ = ['create_router', '']


def create_router() -> Router:
    return Router(path='/v1', route_handlers=[users.UserController])

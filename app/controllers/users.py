import json
import pprint
from litestar import Controller, get
# from app.db import get_database

__all__ = [
    "UserController",
]


class UserController(Controller):
    path = "/user"
    tags = ["Users"]

    @get()
    async def get_user(self) -> json:
        try:
            # dbConnection = get_database()
            # usersCollection = dbConnection.users
            # pprint.pprint(usersCollection)
            # pprint.pprint(usersCollection.get_collection('users').insert_one({"user": "abc"}))
            return json.dumps({"c": 0, "b": 0, "a": 0})
        except Exception as e:
            pprint.pprint('ValueError', e)

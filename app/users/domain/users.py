from typing import List, Optional
from pydantic import BaseModel, UUID4
from dataclasses import dataclass

__all__ = ['Users', 'RegisterUser']


class Users(BaseModel):
    _id: UUID4
    email: str
    username: str
    password: str
    firstname: str
    lastname: str
    liked_movies: Optional[List[int]] = None


# TO BE REMOVED
@dataclass
class RegisterUser:
    password: str
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = ''

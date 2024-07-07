from typing import Optional
from pydantic import BaseModel
from dataclasses import dataclass

__all__ = ['RegisterUserDto', 'LoginUserDto', 'LoginResponse', 'RegisterUserResponse']


@dataclass
class RegisterUserDto(BaseModel):
    password: str
    first_name: str
    last_name: str
    phone: str
    is_admin: bool
    email: Optional[str] = None


@dataclass
class LoginUserDto(BaseModel):
    phone: str
    password: str


class LoginResponse(BaseModel):
    token: str


class RegisterUserResponse(BaseModel):
    id: str

from typing import Optional
from dataclasses import dataclass

__all__ = ['RegisterUserDto', 'LoginUserDto', 'LoginResponse']


@dataclass
class RegisterUserDto:
    password: str
    first_name: str
    last_name: str
    phone: str
    is_admin: bool
    email: Optional[str] = None


@dataclass
class LoginUserDto:
    phone: str
    password: str


class LoginResponse:
    token: str

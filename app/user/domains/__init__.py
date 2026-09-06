from typing import Optional
from pydantic import BaseModel
from dataclasses import dataclass
from app.shared.constants import AnswerOptionKeys

__all__ = [
    'RegisterUserDto',
    'LoginUserDto',
    'LoginResponse',
    'RegisterUserResponse',
    'AttemptQuestionDto',
    'AttemptQuestionResponse',
    'ForgotPasswordDto',
    'ResetPasswordDto',
    'MessageResponse',
]


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


@dataclass
class AttemptQuestionDto(BaseModel):
    question_id: str
    option: AnswerOptionKeys


@dataclass
class ForgotPasswordDto(BaseModel):
    email: str


@dataclass
class ResetPasswordDto(BaseModel):
    token: str
    new_password: str


class LoginResponse(BaseModel):
    token: str


class RegisterUserResponse(BaseModel):
    id: str


class AttemptQuestionResponse(BaseModel):
    id: str


class MessageResponse(BaseModel):
    message: str

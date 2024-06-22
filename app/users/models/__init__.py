from pydantic import BaseModel, UUID4, Field

__all__ = ['Users']


class Users(BaseModel):
    _id: UUID4
    email: str
    phone: str
    first_name: str
    password: str
    last_name: str
    is_admin: bool = Field(default=False)

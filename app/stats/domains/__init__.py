from pydantic import BaseModel

__all__ = ['StatsResponse']


class StatsResponse(BaseModel):
    total_topics: int
    total_users: int
    questions_attempted: int
    users_attempted: int

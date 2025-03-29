from datetime import timedelta, datetime

__all__ = [
    'current_timestamp',
    'get_bearer_string',
    'token_expiry_time',
    'current_time_string',
    'find_in_list',
]


def get_bearer_string(token: str) -> str:
    return token.replace('Bearer ', '')


def token_expiry_time() -> float:
    now = datetime.today()
    return (now + timedelta(days=30)).timestamp()


def current_timestamp():
    return datetime.now().timestamp()


def current_time_string() -> str:
    return datetime.now().isoformat()


def find_in_list(list_input: list, key_to_find_by: str, value: str | int):
    return next((i for i in list_input if i[key_to_find_by] == value), 0)

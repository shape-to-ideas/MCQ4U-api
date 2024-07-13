from datetime import timedelta, datetime

__all__ = ['current_timestamp', 'parse_token', 'token_expiry_time', 'current_time_string']


def parse_token(token) -> str:
    return token.replace('Bearer ', '')


def token_expiry_time():
    now = datetime.today()
    return (now + timedelta(days=30)).timestamp()


def current_timestamp():
    return datetime.now().timestamp()


def current_time_string():
    return datetime.now().isoformat()

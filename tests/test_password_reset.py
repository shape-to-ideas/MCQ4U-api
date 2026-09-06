import os
from unittest.mock import MagicMock, patch

import pytest
from litestar.exceptions import ValidationException

os.environ.setdefault('SALT_ROUNDS', '4')

from app.shared.utils import current_timestamp
from app.user.domains import ForgotPasswordDto, ResetPasswordDto
from app.user.services import UserService


def make_service_with_mock_db(users_collection: MagicMock) -> UserService:
    service = UserService()
    service.database_service = MagicMock()
    service.database_service.user_instance.return_value = users_collection
    return service


@patch('app.user.services.send_password_reset_email')
def test_request_password_reset_sends_email_for_existing_user(mock_send_email):
    users_collection = MagicMock()
    users_collection.find_one.return_value = {'_id': 'user-1', 'email': 'a@b.com'}
    service = make_service_with_mock_db(users_collection)

    result = service.request_password_reset(ForgotPasswordDto.model_construct(email='a@b.com'))

    mock_send_email.assert_called_once()
    sent_to_email = mock_send_email.call_args.args[0]
    assert sent_to_email == 'a@b.com'
    users_collection.update_one.assert_called_once()
    assert 'message' in result


@patch('app.user.services.send_password_reset_email')
def test_request_password_reset_does_not_send_email_for_unknown_user(mock_send_email):
    users_collection = MagicMock()
    users_collection.find_one.return_value = None
    service = make_service_with_mock_db(users_collection)

    result = service.request_password_reset(ForgotPasswordDto.model_construct(email='nobody@b.com'))

    mock_send_email.assert_not_called()
    users_collection.update_one.assert_not_called()
    assert 'message' in result


@patch('app.user.services.send_password_reset_email')
def test_forgot_password_response_is_identical_for_known_and_unknown_email(mock_send_email):
    known_collection = MagicMock()
    known_collection.find_one.return_value = {'_id': 'user-1', 'email': 'a@b.com'}
    known_result = make_service_with_mock_db(known_collection).request_password_reset(
        ForgotPasswordDto.model_construct(email='a@b.com')
    )

    unknown_collection = MagicMock()
    unknown_collection.find_one.return_value = None
    unknown_result = make_service_with_mock_db(unknown_collection).request_password_reset(
        ForgotPasswordDto.model_construct(email='nobody@b.com')
    )

    assert known_result == unknown_result


def test_reset_password_updates_password_with_valid_token():
    users_collection = MagicMock()
    users_collection.find_one.return_value = {
        '_id': 'user-1',
        'reset_token_hash': 'irrelevant-because-mocked-lookup',
        'reset_token_expiry': current_timestamp() + 3600,
    }
    service = make_service_with_mock_db(users_collection)

    result = service.reset_password(ResetPasswordDto.model_construct(token='raw-token', new_password='NewPass123'))

    update_call = users_collection.update_one.call_args
    assert update_call.args[0] == {'_id': 'user-1'}
    set_fields = update_call.args[1]['$set']
    assert 'password' in set_fields
    assert set_fields['password'] != 'NewPass123'
    assert update_call.args[1]['$unset'] == {'reset_token_hash': '', 'reset_token_expiry': ''}
    assert 'message' in result


def test_reset_password_raises_for_unknown_token():
    users_collection = MagicMock()
    users_collection.find_one.return_value = None
    service = make_service_with_mock_db(users_collection)

    with pytest.raises(ValidationException):
        service.reset_password(ResetPasswordDto.model_construct(token='bad-token', new_password='NewPass123'))

    users_collection.update_one.assert_not_called()


def test_reset_password_raises_for_expired_token():
    users_collection = MagicMock()
    users_collection.find_one.return_value = {
        '_id': 'user-1',
        'reset_token_hash': 'hash',
        'reset_token_expiry': current_timestamp() - 10,
    }
    service = make_service_with_mock_db(users_collection)

    with pytest.raises(ValidationException):
        service.reset_password(ResetPasswordDto.model_construct(token='raw-token', new_password='NewPass123'))

    users_collection.update_one.assert_not_called()

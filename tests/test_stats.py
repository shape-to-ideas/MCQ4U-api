from unittest.mock import MagicMock

from app.stats.services import StatsService


def make_service_with_mock_db(
    topics_collection: MagicMock,
    users_collection: MagicMock,
    attempted_questions_collection: MagicMock,
) -> StatsService:
    service = StatsService()
    service.database_service = MagicMock()
    service.database_service.topics_instance.return_value = topics_collection
    service.database_service.user_instance.return_value = users_collection
    service.database_service.attempted_questions_instance.return_value = (
        attempted_questions_collection
    )
    return service


def test_get_stats_returns_document_counts_for_topics_and_users():
    topics_collection = MagicMock()
    topics_collection.count_documents.return_value = 12
    users_collection = MagicMock()
    users_collection.count_documents.return_value = 6
    attempted_questions_collection = MagicMock()
    attempted_questions_collection.distinct.return_value = []

    service = make_service_with_mock_db(
        topics_collection, users_collection, attempted_questions_collection
    )

    result = service.get_stats()

    topics_collection.count_documents.assert_called_once_with({})
    users_collection.count_documents.assert_called_once_with({})
    assert result.total_topics == 12
    assert result.total_users == 6


def test_get_stats_counts_distinct_attempted_questions_and_users():
    attempted_questions_collection = MagicMock()

    def distinct(field):
        return {
            'question_id': ['q1', 'q2', 'q3'],
            'user_id': ['u1', 'u2'],
        }[field]

    attempted_questions_collection.distinct.side_effect = distinct

    service = make_service_with_mock_db(
        MagicMock(count_documents=MagicMock(return_value=0)),
        MagicMock(count_documents=MagicMock(return_value=0)),
        attempted_questions_collection,
    )

    result = service.get_stats()

    attempted_questions_collection.distinct.assert_any_call('question_id')
    attempted_questions_collection.distinct.assert_any_call('user_id')
    assert result.questions_attempted == 3
    assert result.users_attempted == 2


def test_get_stats_deduplicates_attempts_from_the_same_question_or_user():
    # distinct() is what mongo does the dedup with, but this pins the
    # expectation that repeated attempts of one question by one user
    # do not inflate the counts (distinct() naturally returns unique values).
    attempted_questions_collection = MagicMock()

    def distinct(field):
        return {
            'question_id': ['q1'],
            'user_id': ['u1'],
        }[field]

    attempted_questions_collection.distinct.side_effect = distinct

    service = make_service_with_mock_db(
        MagicMock(count_documents=MagicMock(return_value=0)),
        MagicMock(count_documents=MagicMock(return_value=0)),
        attempted_questions_collection,
    )

    result = service.get_stats()

    assert result.questions_attempted == 1
    assert result.users_attempted == 1


def test_get_stats_returns_zero_counts_for_an_empty_database():
    empty_collection = MagicMock()
    empty_collection.count_documents.return_value = 0
    attempted_questions_collection = MagicMock()
    attempted_questions_collection.distinct.return_value = []

    service = make_service_with_mock_db(
        empty_collection, empty_collection, attempted_questions_collection
    )

    result = service.get_stats()

    assert result.total_topics == 0
    assert result.total_users == 0
    assert result.questions_attempted == 0
    assert result.users_attempted == 0

from app.db import DatabaseService
from app.stats.domains import StatsResponse

__all__ = ['StatsService']


class StatsService:
    database_service = DatabaseService()

    def get_stats(self) -> StatsResponse:
        topics_collection = self.database_service.topics_instance()
        users_collection = self.database_service.user_instance()
        attempted_questions_collection = (
            self.database_service.attempted_questions_instance()
        )

        return StatsResponse(
            total_topics=topics_collection.count_documents({}),
            total_users=users_collection.count_documents({}),
            questions_attempted=len(
                attempted_questions_collection.distinct('question_id')
            ),
            users_attempted=len(
                attempted_questions_collection.distinct('user_id')
            ),
        )

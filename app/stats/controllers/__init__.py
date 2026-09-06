from litestar import Controller, get
from litestar.di import Provide

from app.stats.domains import StatsResponse
from app.stats.services import StatsService
from app.shared.middlewares import AuthorizationMiddleware

__all__ = ['StatsController']


class StatsController(Controller):
    tags = ['Stats']
    dependencies = {
        'stats_service': Provide(StatsService, sync_to_thread=False),
    }

    signature_namespace = {
        'StatsService': StatsService,
    }

    @get('/stats', middleware=[AuthorizationMiddleware], sync_to_thread=False)
    def get_stats(self, stats_service: StatsService) -> StatsResponse:
        return stats_service.get_stats()

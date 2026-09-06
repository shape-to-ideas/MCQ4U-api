import logging
import os
import uuid

from dotenv import load_dotenv
from litestar import Litestar, Router, Request, Response
from litestar.config.cors import CORSConfig
from contextlib import asynccontextmanager
from litestar.openapi import OpenAPIConfig
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
import uvicorn

from app.db import DatabaseService
from app.shared import logger, logging_config
from app.user.controllers import UserController
from app.question.controllers import QuestionController
from app.stats.controllers import StatsController


def create_router() -> Router:
    return Router(
        path='/api/v1',
        route_handlers=[UserController, QuestionController, StatsController],
    )


load_dotenv()
cors_config = CORSConfig(allow_origins=['*'])
database_service = DatabaseService()


def internal_server_error_handler(request: Request, exc: Exception) -> Response:
    """Catch-all for unexpected (non-HTTPException) errors. The full traceback is
    already logged by `logging_config`'s exception logging - a stack trace is not
    safe to hand back over the API, so the client only gets a generic message plus
    an id they can quote back to us to find the matching log entry."""
    error_id = uuid.uuid4().hex
    logger.error('Unhandled exception (error_id=%s) on %s %s', error_id, request.method, request.url.path)
    return Response(
        content={
            'status_code': HTTP_500_INTERNAL_SERVER_ERROR,
            'detail': 'Internal Server Error',
            'error_id': error_id,
        },
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )


@asynccontextmanager
async def lifespan(app: Litestar):
    try:
        client = app.state.mongodb_client = database_service.get_db_client()
    except Exception:
        logger.exception('Failed to connect to the database during startup')
        # Re-raising here would let it propagate into uvicorn's own lifespan
        # handling, which logs its own raw, unformatted ExceptionGroup dump on
        # top of the one above. Flush our clean log line and exit immediately
        # instead, so this is the only trace anyone sees.
        logging.shutdown()
        os._exit(1)
    logger.info('Successfully Connected to Database')
    try:
        yield
    finally:
        client.close()


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[create_router()],
        cors_config=cors_config,
        lifespan=[lifespan],
        logging_config=logging_config,
        exception_handlers={HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error_handler},
        debug=os.getenv('APP_DEBUG', 'false').strip().lower() in ('1', 'true', 'yes'),
        openapi_config=OpenAPIConfig(title='MCQ4U API Documentation', version='1.0.0'),
    )


app = create_app()

if __name__ == '__main__':
    # @TODO to configure port
    uvicorn.run(
        app,
    )

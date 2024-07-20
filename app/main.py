from dotenv import load_dotenv
from litestar import Litestar, Router
from litestar.config.cors import CORSConfig
from contextlib import asynccontextmanager
from litestar.openapi import OpenAPIConfig
import uvicorn

from app.db import DatabaseService
from app.shared import logger, logging_config
from app.user.controllers import UserController
from app.question.controllers import QuestionController


def create_router() -> Router:
    return Router(path='/api/v1', route_handlers=[UserController, QuestionController])


load_dotenv()
cors_config = CORSConfig(allow_origins=['*'])
database_service = DatabaseService()


@asynccontextmanager
async def lifespan(app: Litestar):
    client = app.state.mongodb_client = database_service.get_db_client()
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
        debug=True,
        openapi_config=OpenAPIConfig(title="MCQ4U API Documentation", version="1.0.0")
    )


app = create_app()

if __name__ == '__main__':
    # @TODO to configure port
    uvicorn.run(
        app,
    )

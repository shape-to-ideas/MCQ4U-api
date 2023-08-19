"""Minimal Litestar application."""
from asyncio import sleep
from typing import Any
from litestar import Litestar

import uvicorn

from app.controllers import create_router

__all__ = ["create_app"]


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[create_router()]
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
    )

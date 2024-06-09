import logging
from litestar.logging import LoggingConfig

__all__ = ['logger', 'logging_config']

logging_config = LoggingConfig(
    root={"level": logging.getLevelName(logging.INFO), "handlers": ["console"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
)

logger = logging_config.configure()()

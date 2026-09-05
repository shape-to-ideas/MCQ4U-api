import logging

from litestar.logging import LoggingConfig
from rich.traceback import install as install_rich_traceback

__all__ = ['logger', 'logging_config']

# Frames from these are collapsed in rendered tracebacks (still counted, just not
# printed line-by-line) so a real error is dominated by app code, not framework
# internals like anyio's task-group machinery.
_SUPPRESSED_FRAMES = ['litestar', 'anyio', 'uvicorn', 'contextlib', 'asyncio']

# Handles exceptions that escape all the way to the top of the process (e.g. a
# startup/lifespan failure) - the one case the `logging` module below never sees,
# since nothing calls logger.exception() for it. Without this, Python's default
# excepthook prints the raw ExceptionGroup/traceback dump.
install_rich_traceback(show_locals=False, suppress=_SUPPRESSED_FRAMES)

logging_config = LoggingConfig(
    handlers={
        'console': {
            '()': 'rich.logging.RichHandler',
            'formatter': 'standard',
            'rich_tracebacks': True,
            # Local variables can hold secrets (DB connection strings, JWT
            # secrets, passwords) - never render them, even in a "pretty" trace.
            'tracebacks_show_locals': False,
            'tracebacks_suppress': _SUPPRESSED_FRAMES,
            'show_path': False,
            'markup': False,
        },
    },
    formatters={'standard': {'format': '%(name)s | %(message)s'}},
    root={'level': logging.getLevelName(logging.INFO), 'handlers': ['console']},
    log_exceptions='always',
    # Litestar's own default caps request-time exception logs at the last 20
    # traceback lines. Raised well past any realistic stack depth here so
    # nothing gets silently cut off.
    traceback_line_limit=1000,
)

logger = logging_config.configure()()

import asyncio
import sys

from uvicorn.loops.auto import auto_loop_factory


def selector_loop_factory() -> asyncio.AbstractEventLoop:
    """Event loop factory for uvicorn's ``--loop`` option.

    psycopg's async pool refuses to run on Windows' ProactorEventLoop, which
    is exactly what uvicorn picks there by default -- every connection
    attempt fails and startup dies on a PoolTimeout. Force the
    SelectorEventLoop on Windows; everywhere else keep uvicorn's own choice
    (uvloop when it is installed).

    Note: for a custom ``--loop`` target uvicorn uses the imported object as
    the loop factory itself, so this returns a loop instance rather than a
    callable.
    """
    if sys.platform == "win32":
        return asyncio.SelectorEventLoop()
    return auto_loop_factory()()

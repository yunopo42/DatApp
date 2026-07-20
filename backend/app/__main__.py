import asyncio
import sys
from argparse import ArgumentParser

import uvicorn

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    parser = ArgumentParser(description="Run the DatApp API")
    parser.add_argument("--host", default=settings.app_host)
    parser.add_argument("--port", type=int, default=settings.app_port)
    arguments = parser.parse_args()
    uvicorn.run(
        "app.main:app",
        host=arguments.host,
        port=arguments.port,
        loop=asyncio.SelectorEventLoop if sys.platform == "win32" else "auto",
    )


if __name__ == "__main__":
    main()

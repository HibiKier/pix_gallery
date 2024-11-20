from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

LOG_PATH = Path() / "logs"

LOG_PATH.mkdir(exist_ok=True, parents=True)

default_format: str = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    "<c><u>{name}</u></c> | "
    # "<c>{function}:{line}</c>| "
    "{message}"
)


logger.add(
    LOG_PATH / f"{datetime.now().date()}.log",
    level="INFO",
    rotation="00:00",
    format=default_format,
    retention=timedelta(days=30),
)

logger.add(
    LOG_PATH / f"error_{datetime.now().date()}.log",
    level="ERROR",
    rotation="00:00",
    format=default_format,
    retention=timedelta(days=30),
)

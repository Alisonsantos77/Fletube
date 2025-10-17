import os
from pathlib import Path

from loguru import logger


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
    )

    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )

    logger.info("Sistema de logging configurado com sucesso")


def get_logger(name: str):
    return logger.bind(name=name)

import os
import sys
from pathlib import Path

from loguru import logger


def setup_logging(app_name="Fletube"):
    if getattr(sys, "frozen", False):
        base_path = Path.home()
    else:
        base_path = Path.home()

    log_dir = base_path / f"{app_name}_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    logger.remove()

    logger.add(
        log_file,
        rotation="10 MB",
        retention="14 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )

    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )

    logger.info(f"Sistema de logging inicializado -> {log_file}")
    return logger


def get_logger():
    return logger

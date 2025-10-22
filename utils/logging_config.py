import os
from pathlib import Path

from loguru import logger

try:
    from flet.security import encrypt

    FLET_SECURITY_AVAILABLE = True
except ImportError:
    FLET_SECURITY_AVAILABLE = False


class EncryptedLogHandler:
    def __init__(self, log_file: Path, secret_key: str):
        self.log_file = log_file
        self.secret_key = secret_key
        self.buffer = []
        self.buffer_size = 10

    def write(self, message: str):
        try:
            encrypted_message = encrypt(message, self.secret_key)
            self.buffer.append(encrypted_message + "\n")
            if len(self.buffer) >= self.buffer_size:
                self.flush()
        except Exception as e:
            print(f"Erro ao criptografar log: {e}")

    def flush(self):
        if self.buffer:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.writelines(self.buffer)
                self.buffer.clear()
            except Exception as e:
                print(f"Erro ao salvar logs: {e}")

    def __del__(self):
        self.flush()


def setup_logging(app_name="Fletube"):
    app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
    if not app_data_path:
        app_data_path = str(Path.home() / ".flet_storage")

    log_dir = Path(app_data_path) / f"{app_name}_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    logger.remove()

    secret_key = os.getenv("SECURE_STORAGE_SECRET_KEY")

    if secret_key and FLET_SECURITY_AVAILABLE:
        encrypted_handler = EncryptedLogHandler(log_file, secret_key)
        logger.add(
            encrypted_handler.write,
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            backtrace=True,
            diagnose=True,
        )
        logger.info(f"Sistema de logging criptografado inicializado -> {log_file}")
    else:
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

        logger.info(f"Sistema de logging inicializado -> {log_file}")

        if not secret_key:
            logger.warning("SECRET_KEY ausente - logs nao criptografados")
        if not FLET_SECURITY_AVAILABLE:
            logger.warning("flet.security indisponível - logs nao criptografados")

    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )

    return logger

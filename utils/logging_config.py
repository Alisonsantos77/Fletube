import os
import sys
from pathlib import Path

from loguru import logger


def setup_logging(app_name="Fletube"):
    """
    Setup avançado de logging.
    Detecta se está compilado e cria pasta de logs na área de trabalho ou pública.
    """

    # Detecta se está compilado (PyInstaller ou Briefcase)
    if getattr(sys, "frozen", False):
        base_path = Path(os.environ.get("PUBLIC", "C:\\Users\\Public"))  # pasta pública
    else:
        base_path = Path.home() / "Desktop"  # usuário normal -> Desktop

    # Pasta de logs
    log_dir = base_path / f"{app_name}_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    # Remove handlers padrão
    logger.remove()

    # Log para arquivo
    logger.add(
        log_file,
        rotation="10 MB",  # roda arquivo quando atingir 10MB
        retention="14 days",  # mantém 14 dias
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
        backtrace=True,  # detalha tracebacks
        diagnose=True,  # diagnóstico avançado
    )

    # Log para console
    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )

    logger.info(f"Sistema de logging inicializado -> {log_file}")
    return logger


# Exemplo de uso
if __name__ == "__main__":
    log = setup_logging()
    log.info("Teste de log avançado funcionando!")

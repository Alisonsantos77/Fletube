"""
Configuração centralizada de logging para o Fletube.
Evita duplicação de configurações em múltiplos arquivos.
"""

import logging
import os
from pathlib import Path


def setup_logging():
    """
    Configura o sistema de logging de forma centralizada.
    Deve ser chamada apenas uma vez no início da aplicação.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configuração principal
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("logs/app.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    # Configurar níveis específicos para bibliotecas externas
    logging.getLogger("flet_core").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Log de inicialização
    logger = logging.getLogger(__name__)
    logger.info("Sistema de logging configurado com sucesso")


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger configurado para o módulo especificado.

    Args:
        name: Nome do módulo (geralmente __name__)

    Returns:
        Logger configurado
    """
    return logging.getLogger(name)

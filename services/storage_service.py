"""
Serviço centralizado de armazenamento usando SecureStorage V2
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from utils.ClientStoragev2 import SecureStorage, StorageType

logger = logging.getLogger(__name__)


class FletubeStorage:
    """
    Gerenciador de armazenamento centralizado para o Fletube.
    Usa SecureStorage V2 como backend.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """Inicializa os storages da aplicação"""
        if base_path is None:
            base_path = Path.home() / ".fletube"

        base_path.mkdir(parents=True, exist_ok=True)

        self.downloads = SecureStorage(
            storage_path=base_path / "downloads.json",
            storage_type=StorageType.JSON,
            auto_save=True,
            encrypt_data=False,
        )

        self.settings = SecureStorage(
            storage_path=base_path / "settings.json",
            storage_type=StorageType.JSON,
            auto_save=True,
            encrypt_data=False,
        )

        secret_key = os.getenv("SECURE_STORAGE_SECRET_KEY")
        try:
            self.secure = SecureStorage(
                storage_path=base_path / "secure.enc",
                storage_type=StorageType.JSON,
                auto_save=True,
                encrypt_data=True,
                secret_key=secret_key,
            )
            logger.info("🔐 Storage seguro inicializado com sucesso")
        except Exception as e:
            logger.warning(f"Storage seguro não disponível: {e}")
            self.secure = None

    def save_download(self, download_id: str, data: Dict[str, Any]):
        """Salva um download concluído"""
        self.downloads.set(download_id, data, namespace="completed")
        logger.info(f"Download salvo: {download_id}")

    def get_download(self, download_id: str) -> Optional[Dict[str, Any]]:
        """Recupera dados de um download"""
        return self.downloads.get(download_id, namespace="completed")

    def list_downloads(self) -> list:
        """Lista todos os downloads"""
        keys = self.downloads.list_keys(namespace="completed")
        return [self.get_download(k) for k in keys]

    def delete_download(self, download_id: str) -> bool:
        """Remove um download do histórico"""
        return self.downloads.delete(download_id, namespace="completed")

    def clear_downloads(self):
        """Limpa todo o histórico de downloads"""
        self.downloads.clear(namespace="completed")

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Obtém uma configuração"""
        return self.settings.get(key, namespace="app", default=default)

    def set_setting(self, key: str, value: Any):
        """Define uma configuração"""
        self.settings.set(key, value, namespace="app")

    def get_all_settings(self) -> Dict[str, Any]:
        """Retorna todas as configurações"""
        keys = self.settings.list_keys(namespace="app")
        return {k: self.get_setting(k) for k in keys}

    def save_secure(self, key: str, value: Any):
        """Salva dado sensível criptografado"""
        if self.secure:
            self.secure.set(key, value, namespace="credentials")
        else:
            logger.warning("Storage seguro não disponível!")

    def get_secure(self, key: str, default: Any = None) -> Any:
        """Recupera dado sensível"""
        if self.secure:
            return self.secure.get(key, namespace="credentials", default=default)
        return default

    def export_all(self) -> Dict[str, Any]:
        """Exporta todos os dados para backup"""
        return {
            "downloads": self.downloads.export_data(),
            "settings": self.settings.export_data(),
            "metadata": {"version": "1.3", "app": "Fletube"},
        }

    def get_storage_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o armazenamento"""
        return {
            "downloads_count": len(self.downloads.list_keys(namespace="completed")),
            "settings_count": len(self.settings.list_keys(namespace="app")),
            "secure_available": self.secure is not None,
            "downloads_metadata": self.downloads.get_metadata(),
            "settings_metadata": self.settings.get_metadata(),
        }

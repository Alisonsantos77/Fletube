import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from utils.ClientStoragev2 import SecureStorage, StorageType
from utils.logging_config import setup_logging

logger = setup_logging()


class StorageError(Exception):
    pass


class FletubeStorage:
    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            base_path = Path.home() / ".fletube"

        try:
            base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Storage path: {base_path}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório de storage: {e}")
            raise StorageError(f"Não foi possível criar diretório: {base_path}")

        try:
            self.downloads = SecureStorage(
                storage_path=base_path / "downloads.json",
                storage_type=StorageType.JSON,
                auto_save=True,
                encrypt_data=False,
            )
            logger.info("Downloads storage inicializado")
        except Exception as e:
            logger.error(f"Falha no downloads storage: {e}")
            raise

        try:
            self.settings = SecureStorage(
                storage_path=base_path / "settings.json",
                storage_type=StorageType.JSON,
                auto_save=True,
                encrypt_data=False,
            )
            logger.info("Settings storage inicializado")
        except Exception as e:
            logger.error(f"Falha no settings storage: {e}")
            raise

        self.secure = None
        secret_key = os.getenv("SECURE_STORAGE_SECRET_KEY")

        if secret_key:
            try:
                self.secure = SecureStorage(
                    storage_path=base_path / "secure.enc",
                    storage_type=StorageType.JSON,
                    auto_save=True,
                    encrypt_data=True,
                    secret_key=secret_key,
                )
                logger.info("Storage seguro inicializado")
            except Exception as e:
                logger.warning(f"Storage seguro não disponível: {e}")

    def save_download(self, download_id: str, data: Dict[str, Any]):
        try:
            self.downloads.set(download_id, data, namespace="completed")
            logger.info(f"Download salvo: {download_id}")
        except Exception as e:
            logger.error(f"Erro ao salvar download {download_id}: {e}")

    def get_download(self, download_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.downloads.get(download_id, namespace="completed")
        except Exception as e:
            logger.error(f"Erro ao recuperar download {download_id}: {e}")
            return None

    def list_downloads(self) -> list:
        try:
            keys = self.downloads.list_keys(namespace="completed")
            return [self.get_download(k) for k in keys if self.get_download(k)]
        except Exception as e:
            logger.error(f"Erro ao listar downloads: {e}")
            return []

    def delete_download(self, download_id: str) -> bool:
        try:
            result = self.downloads.delete(download_id, namespace="completed")
            if result:
                logger.info(f"Download removido: {download_id}")
            return result
        except Exception as e:
            logger.error(f"Erro ao deletar download {download_id}: {e}")
            return False

    def clear_downloads(self):
        try:
            self.downloads.clear(namespace="completed")
            logger.info("Histórico de downloads limpo")
        except Exception as e:
            logger.error(f"Erro ao limpar downloads: {e}")

    def get_setting(self, key: str, default: Any = None) -> Any:
        try:
            return self.settings.get(key, namespace="app", default=default)
        except Exception as e:
            logger.error(f"Erro ao obter setting {key}: {e}")
            return default

    def set_setting(self, key: str, value: Any):
        try:
            self.settings.set(key, value, namespace="app")
        except Exception as e:
            logger.error(f"Erro ao salvar setting {key}: {e}")

    def get_all_settings(self) -> Dict[str, Any]:
        try:
            keys = self.settings.list_keys(namespace="app")
            return {k: self.get_setting(k) for k in keys}
        except Exception as e:
            logger.error(f"Erro ao obter settings: {e}")
            return {}

    def save_secure(self, key: str, value: Any):
        if self.secure:
            try:
                self.secure.set(key, value, namespace="credentials")
            except Exception as e:
                logger.error(f"Erro ao salvar dado seguro {key}: {e}")
        else:
            logger.warning("Storage seguro não disponível")

    def get_secure(self, key: str, default: Any = None) -> Any:
        if self.secure:
            try:
                return self.secure.get(key, namespace="credentials", default=default)
            except Exception as e:
                logger.error(f"Erro ao recuperar dado seguro {key}: {e}")
                return default
        return default

    def export_all(self) -> Dict[str, Any]:
        try:
            return {
                "downloads": self.downloads.export_data(),
                "settings": self.settings.export_data(),
                "metadata": {"version": "1.3", "app": "Fletube"},
            }
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {e}")
            return {"error": str(e)}

    def get_storage_info(self) -> Dict[str, Any]:
        try:
            return {
                "downloads_count": len(self.downloads.list_keys(namespace="completed")),
                "settings_count": len(self.settings.list_keys(namespace="app")),
                "secure_available": self.secure is not None,
                "downloads_metadata": self.downloads.get_metadata(),
                "settings_metadata": self.settings.get_metadata(),
            }
        except Exception as e:
            logger.error(f"Erro ao obter info de storage: {e}")
            return {"error": str(e)}

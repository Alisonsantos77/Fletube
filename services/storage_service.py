import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.ClientStoragev2 import SecureStorage
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
            logger.error(f"Erro ao criar diretorio de storage: {e}")
            raise StorageError(f"Nao foi possivel criar diretorio: {base_path}")

        secret_key = os.getenv("SECURE_STORAGE_SECRET_KEY")

        try:
            self.downloads = SecureStorage(
                storage_path=base_path / "downloads.json",
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
                auto_save=True,
                encrypt_data=False,
            )
            logger.info("Settings storage inicializado")
        except Exception as e:
            logger.error(f"Falha no settings storage: {e}")
            raise

        try:
            if secret_key:
                self.credentials = SecureStorage(
                    storage_path=base_path / "credentials.enc",
                    auto_save=True,
                    encrypt_data=True,
                    secret_key=secret_key,
                )
                logger.info("Credentials storage inicializado (criptografado)")
            else:
                self.credentials = None
                logger.warning(
                    "Credentials storage nao disponivel - SECRET_KEY ausente"
                )
        except Exception as e:
            logger.error(f"Falha no credentials storage: {e}")
            self.credentials = None

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

    def list_downloads(self) -> List[Dict[str, Any]]:
        try:
            keys = self.downloads.list_keys(namespace="completed")
            downloads = []
            for k in keys:
                download = self.get_download(k)
                if download:
                    downloads.append(download)
            return downloads
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
            logger.info("Historico de downloads limpo")
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

    def save_credential(self, key: str, value: Any):
        if not self.credentials:
            logger.warning("Credentials storage nao disponivel")
            return

        try:
            self.credentials.set(key, value, namespace="user")
            logger.info(f"Credencial salva: {key}")
        except Exception as e:
            logger.error(f"Erro ao salvar credencial {key}: {e}")

    def get_credential(self, key: str, default: Any = None) -> Any:
        if not self.credentials:
            logger.warning("Credentials storage nao disponivel")
            return default

        try:
            return self.credentials.get(key, namespace="user", default=default)
        except Exception as e:
            logger.error(f"Erro ao recuperar credencial {key}: {e}")
            return default

    def delete_credential(self, key: str) -> bool:
        if not self.credentials:
            logger.warning("Credentials storage nao disponivel")
            return False

        try:
            result = self.credentials.delete(key, namespace="user")
            if result:
                logger.info(f"Credencial removida: {key}")
            return result
        except Exception as e:
            logger.error(f"Erro ao deletar credencial {key}: {e}")
            return False

    def clear_credentials(self):
        if not self.credentials:
            logger.warning("Credentials storage nao disponivel")
            return

        try:
            self.credentials.clear(namespace="user")
            logger.info("Credenciais limpas")
        except Exception as e:
            logger.error(f"Erro ao limpar credenciais: {e}")

    def export_all(self) -> Dict[str, Any]:
        try:
            export_data = {
                "downloads": self.downloads.export_data(),
                "settings": self.settings.export_data(),
                "metadata": {"version": "1.3.0", "app": "Fletube"},
            }

            if self.credentials:
                export_data["credentials"] = self.credentials.export_data(
                    decrypt_export=True
                )

            return export_data
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {e}")
            return {"error": str(e)}

    def get_storage_info(self) -> Dict[str, Any]:
        try:
            downloads_keys = self.downloads.list_keys(namespace="completed")
            settings_keys = self.settings.list_keys(namespace="app")

            info = {
                "downloads_count": len(downloads_keys),
                "settings_count": len(settings_keys),
                "secure_available": self.credentials is not None,
                "credentials_available": self.credentials is not None,
                "downloads_path": str(self.downloads.storage_path),
                "settings_path": str(self.settings.storage_path),
            }

            if self.credentials:
                credentials_keys = self.credentials.list_keys(namespace="user")
                info["credentials_count"] = len(credentials_keys)
                info["credentials_path"] = str(self.credentials.storage_path)

            return info
        except Exception as e:
            logger.error(f"Erro ao obter info de storage: {e}")
            return {"error": str(e)}

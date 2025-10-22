import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.logging_config import setup_logging

logger = setup_logging()

try:
    from flet.security import decrypt, encrypt

    FLET_SECURITY_AVAILABLE = True
except ImportError:
    FLET_SECURITY_AVAILABLE = False
    logger.warning("flet.security não disponível - criptografia desabilitada")


class StorageError(Exception):
    pass


class EncryptionError(StorageError):
    pass


class SecureStorage:
    def __init__(
        self,
        storage_path: Path,
        auto_save: bool = True,
        encrypt_data: bool = False,
        secret_key: Optional[str] = None,
    ):
        self.storage_path = Path(storage_path)
        self.auto_save = auto_save
        self.encrypt_data = encrypt_data
        self._secret_key = secret_key
        self._data: Dict[str, Any] = {}
        self._lock = threading.Lock()

        if self.encrypt_data:
            if not FLET_SECURITY_AVAILABLE:
                raise EncryptionError("flet.security não disponível")
            if not self._secret_key:
                raise EncryptionError("secret_key obrigatória quando encrypt_data=True")
            logger.info(f"Modo criptografado ativado: {self.storage_path.name}")

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_existing()

    def _encrypt_value(self, value: Any) -> str:
        if not self.encrypt_data:
            return value

        try:
            if not isinstance(value, str):
                value = json.dumps(value, default=str)
            return encrypt(value, self._secret_key)
        except Exception as e:
            raise EncryptionError(f"Erro ao criptografar: {e}")

    def _decrypt_value(self, encrypted_value: str) -> Any:
        if not self.encrypt_data:
            return encrypted_value

        try:
            decrypted = decrypt(encrypted_value, self._secret_key)
            try:
                return json.loads(decrypted)
            except (json.JSONDecodeError, TypeError):
                return decrypted
        except Exception as e:
            raise EncryptionError(f"Erro ao descriptografar: {e}")

    def _load_existing(self) -> None:
        if self.storage_path.exists():
            try:
                with self._lock:
                    with open(self.storage_path, "r", encoding="utf-8") as f:
                        loaded = json.load(f)

                        was_encrypted = loaded.get("metadata", {}).get(
                            "encrypted", False
                        )

                        if was_encrypted != self.encrypt_data:
                            logger.warning(
                                f"Mudança no modo de criptografia detectada - "
                                f"Arquivo: {was_encrypted}, Atual: {self.encrypt_data}"
                            )

                        self._data = loaded.get("data", {})
                        logger.info(f"Dados carregados: {len(self._data)} chaves")
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao carregar {self.storage_path}: {e}")
                self._create_backup()
            except Exception as e:
                logger.error(f"Erro inesperado ao carregar dados: {e}")

    def _create_backup(self) -> None:
        if self.storage_path.exists():
            backup_path = self.storage_path.with_suffix(".backup")
            try:
                self.storage_path.rename(backup_path)
                logger.info(f"Backup criado: {backup_path}")
            except Exception as e:
                logger.error(f"Erro ao criar backup: {e}")

    def _save_if_auto(self) -> None:
        if self.auto_save:
            self.save()

    def set(self, key: str, value: Any, namespace: Optional[str] = None) -> None:
        with self._lock:
            stored_value = self._encrypt_value(value) if self.encrypt_data else value

            if namespace:
                if namespace not in self._data:
                    self._data[namespace] = {}
                self._data[namespace][key] = stored_value
            else:
                self._data[key] = stored_value

        self._save_if_auto()
        logger.debug(f"Set: {namespace}.{key if namespace else key}")

    def get(
        self, key: str, namespace: Optional[str] = None, default: Any = None
    ) -> Any:
        with self._lock:
            if namespace:
                stored_value = self._data.get(namespace, {}).get(key, default)
            else:
                stored_value = self._data.get(key, default)

            if stored_value != default and self.encrypt_data:
                try:
                    return self._decrypt_value(stored_value)
                except EncryptionError as e:
                    logger.error(f"Erro ao descriptografar {key}: {e}")
                    return default

            return stored_value

    def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        with self._lock:
            try:
                if namespace:
                    if namespace in self._data and key in self._data[namespace]:
                        del self._data[namespace][key]
                        if not self._data[namespace]:
                            del self._data[namespace]
                    else:
                        return False
                else:
                    if key in self._data:
                        del self._data[key]
                    else:
                        return False

                self._save_if_auto()
                logger.debug(f"Deleted: {namespace}.{key if namespace else key}")
                return True
            except Exception as e:
                logger.error(f"Erro ao deletar {key}: {e}")
                return False

    def exists(self, key: str, namespace: Optional[str] = None) -> bool:
        with self._lock:
            if namespace:
                return namespace in self._data and key in self._data[namespace]
            return key in self._data

    def list_keys(self, namespace: Optional[str] = None) -> List[str]:
        with self._lock:
            if namespace:
                return list(self._data.get(namespace, {}).keys())
            return list(self._data.keys())

    def clear(self, namespace: Optional[str] = None) -> None:
        with self._lock:
            if namespace:
                if namespace in self._data:
                    del self._data[namespace]
                    logger.info(f"Namespace limpo: {namespace}")
            else:
                self._data.clear()
                logger.info("Todos os dados limpos")

        self._save_if_auto()

    def save(self) -> None:
        try:
            with self._lock:
                full_data = {
                    "data": self._data,
                    "metadata": {
                        "last_saved": datetime.now().isoformat(),
                        "version": "1.3.0",
                        "encrypted": self.encrypt_data,
                    },
                }

                temp_path = self.storage_path.with_suffix(".tmp")
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(full_data, f, indent=2, ensure_ascii=False, default=str)

                temp_path.replace(self.storage_path)
                logger.debug(f"Dados salvos: {self.storage_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
            raise StorageError(f"Falha ao salvar: {e}")

    def export_data(self, decrypt_export: bool = True) -> Dict[str, Any]:
        with self._lock:
            if decrypt_export and self.encrypt_data:
                decrypted_data = {}
                for key, value in self._data.items():
                    if isinstance(value, dict):
                        decrypted_data[key] = {
                            k: self._decrypt_value(v) for k, v in value.items()
                        }
                    else:
                        decrypted_data[key] = self._decrypt_value(value)

                return {
                    "data": decrypted_data,
                    "metadata": {
                        "exported_at": datetime.now().isoformat(),
                        "version": "1.3.0",
                    },
                }
            else:
                return {
                    "data": self._data.copy(),
                    "metadata": {
                        "exported_at": datetime.now().isoformat(),
                        "version": "1.3.0",
                    },
                }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type and self.auto_save:
            self.save()

    def __repr__(self) -> str:
        crypto = "encrypted" if self.encrypt_data else "plain"
        return f"SecureStorage({crypto}, keys={len(self._data)}, path={self.storage_path.name})"

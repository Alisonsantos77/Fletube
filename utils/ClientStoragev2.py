"""
Sistema de Armazenamento Seguro de Cliente V2
Um sistema flexível e reutilizável para armazenamento de dados de cliente
com suporte para múltiplos backends (arquivo e memória) e criptografia nativa.
"""

import json
import logging
import os
import pickle
import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from flet.security import decrypt, encrypt

    FLET_SECURITY_AVAILABLE = True
except ImportError:
    FLET_SECURITY_AVAILABLE = False
    logging.warning("flet.security não disponível. Criptografia desabilitada.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StorageType(Enum):
    """Tipos de armazenamento disponíveis."""

    JSON = "json"
    PICKLE = "pickle"
    MEMORY = "memory"


class StorageError(Exception):
    """Exceção base para erros de armazenamento."""

    pass


class EncryptionError(StorageError):
    """Exceção para erros de criptografia."""

    pass


class StorageBackend(ABC):
    """Interface abstrata para backends de armazenamento."""

    @abstractmethod
    def save(self, data: Any) -> None:
        """Salva dados no backend."""
        pass

    @abstractmethod
    def load(self) -> Any:
        """Carrega dados do backend."""
        pass

    @abstractmethod
    def delete(self) -> None:
        """Remove dados do backend."""
        pass

    @abstractmethod
    def exists(self) -> bool:
        """Verifica se os dados existem."""
        pass


class FileStorageBackend(StorageBackend):
    """Backend de armazenamento em arquivo."""

    def __init__(self, filepath: Path, storage_type: StorageType = StorageType.JSON):
        """
        Inicializa o backend de arquivo.

        Args:
            filepath: Caminho do arquivo
            storage_type: Tipo de serialização (JSON ou PICKLE)
        """
        self.filepath = Path(filepath)
        self.storage_type = storage_type
        self._lock = threading.Lock()
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _file_lock(self):
        """Context manager para lock de arquivo thread-safe."""
        self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()

    def save(self, data: Any) -> None:
        """Salva dados no arquivo com backup automático."""
        with self._file_lock():
            try:
                if self.filepath.exists():
                    backup_path = self.filepath.with_suffix(
                        f".backup{self.filepath.suffix}"
                    )
                    self.filepath.rename(backup_path)

                if self.storage_type == StorageType.JSON:
                    with open(self.filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                elif self.storage_type == StorageType.PICKLE:
                    with open(self.filepath, "wb") as f:
                        pickle.dump(data, f)

                backup_path = self.filepath.with_suffix(
                    f".backup{self.filepath.suffix}"
                )
                if backup_path.exists():
                    backup_path.unlink()

                logger.info(f"Dados salvos com sucesso em {self.filepath}")

            except Exception as e:
                backup_path = self.filepath.with_suffix(
                    f".backup{self.filepath.suffix}"
                )
                if backup_path.exists():
                    backup_path.rename(self.filepath)
                raise StorageError(f"Erro ao salvar dados: {e}")

    def load(self) -> Any:
        """Carrega dados do arquivo."""
        with self._file_lock():
            try:
                if not self.filepath.exists():
                    raise StorageError(f"Arquivo não encontrado: {self.filepath}")

                if self.storage_type == StorageType.JSON:
                    with open(self.filepath, "r", encoding="utf-8") as f:
                        return json.load(f)
                elif self.storage_type == StorageType.PICKLE:
                    with open(self.filepath, "rb") as f:
                        return pickle.load(f)

            except json.JSONDecodeError as e:
                raise StorageError(f"Erro ao decodificar JSON: {e}")
            except pickle.UnpicklingError as e:
                raise StorageError(f"Erro ao desserializar pickle: {e}")
            except Exception as e:
                raise StorageError(f"Erro ao carregar dados: {e}")

    def delete(self) -> None:
        """Remove o arquivo de dados."""
        with self._file_lock():
            if self.filepath.exists():
                backup_path = self.filepath.with_suffix(
                    f".deleted{self.filepath.suffix}"
                )
                self.filepath.rename(backup_path)
                logger.info(f"Arquivo movido para backup: {backup_path}")

    def exists(self) -> bool:
        """Verifica se o arquivo existe."""
        return self.filepath.exists()


class MemoryStorageBackend(StorageBackend):
    """Backend de armazenamento em memória."""

    def __init__(self):
        """Inicializa o backend de memória."""
        self._data: Optional[Any] = None
        self._lock = threading.Lock()

    def save(self, data: Any) -> None:
        """Salva dados na memória."""
        with self._lock:
            self._data = data
            logger.debug("Dados salvos na memória")

    def load(self) -> Any:
        """Carrega dados da memória."""
        with self._lock:
            if self._data is None:
                raise StorageError("Nenhum dado na memória")
            return self._data

    def delete(self) -> None:
        """Limpa dados da memória."""
        with self._lock:
            self._data = None
            logger.debug("Dados removidos da memória")

    def exists(self) -> bool:
        """Verifica se existem dados na memória."""
        return self._data is not None


class SecureStorage:
    """
    Sistema principal de armazenamento seguro de cliente.
    Gerencia dados de cliente com suporte para múltiplos backends e criptografia.
    """

    def __init__(
        self,
        storage_path: Optional[Union[str, Path]] = None,
        storage_type: StorageType = StorageType.JSON,
        use_memory: bool = False,
        auto_save: bool = True,
        encrypt_data: bool = False,
        secret_key: Optional[str] = None,
    ):
        """
        Inicializa o sistema de armazenamento seguro.

        Args:
            storage_path: Caminho para armazenamento em arquivo
            storage_type: Tipo de serialização para arquivo
            use_memory: Se True, usa apenas memória
            auto_save: Se True, salva automaticamente após modificações
            encrypt_data: Se True, criptografa os dados
            secret_key: Chave secreta para criptografia (obrigatória se encrypt_data=True)

        Raises:
            EncryptionError: Se encrypt_data=True mas secret_key não fornecida
            EncryptionError: Se flet.security não estiver disponível
        """
        self.auto_save = auto_save
        self.encrypt_data = encrypt_data
        self._secret_key = secret_key
        self._data: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "version": "2.0.0",
            "encrypted": encrypt_data,
        }

        if self.encrypt_data:
            if not FLET_SECURITY_AVAILABLE:
                raise EncryptionError(
                    "flet.security não disponível. Instale: pip install flet"
                )
            if not self._secret_key:
                self._secret_key = os.getenv("SECURE_STORAGE_SECRET_KEY")
                if not self._secret_key:
                    raise EncryptionError(
                        "secret_key obrigatória quando encrypt_data=True. "
                        "Forneça via parâmetro ou variável SECURE_STORAGE_SECRET_KEY"
                    )
            logger.info("🔐 Modo de criptografia ativado")

        if use_memory:
            self.backend = MemoryStorageBackend()
        else:
            if storage_path is None:
                storage_path = Path.home() / ".secure_storage" / "data.json"
            self.backend = FileStorageBackend(Path(storage_path), storage_type)

        self._load_existing()

    def _encrypt_value(self, value: Any) -> str:
        """
        Criptografa um valor.

        Args:
            value: Valor a ser criptografado

        Returns:
            String criptografada (base64)
        """
        if not self.encrypt_data:
            return value

        try:
            if not isinstance(value, str):
                value = json.dumps(value, default=str)

            encrypted = encrypt(value, self._secret_key)
            logger.debug(
                f"✓ Valor criptografado: {value[:30]}... -> {encrypted[:50]}..."
            )
            return encrypted

        except Exception as e:
            raise EncryptionError(f"Erro ao criptografar dados: {e}")

    def _decrypt_value(self, encrypted_value: str) -> Any:
        """
        Descriptografa um valor.

        Args:
            encrypted_value: Valor criptografado

        Returns:
            Valor descriptografado
        """
        if not self.encrypt_data:
            return encrypted_value

        try:
            decrypted = decrypt(encrypted_value, self._secret_key)
            logger.debug(f"✓ Valor descriptografado: {encrypted_value[:50]}...")

            try:
                return json.loads(decrypted)
            except (json.JSONDecodeError, TypeError):
                return decrypted

        except Exception as e:
            raise EncryptionError(
                f"Erro ao descriptografar dados. Verifique se a secret_key está correta: {e}"
            )

    def _validate_encryption_key(self) -> bool:
        """
        Valida se a chave de criptografia está correta.
        Usa um valor de teste armazenado nos metadados.

        Returns:
            True se a chave é válida, False caso contrário
        """
        if not self.encrypt_data:
            return True

        test_key = "_encryption_test"
        test_value = "SecureStorage_V2_Valid"

        if test_key not in self._metadata:
            try:
                self._metadata[test_key] = self._encrypt_value(test_value)
                return True
            except Exception:
                return False

        try:
            decrypted = self._decrypt_value(self._metadata[test_key])
            return decrypted == test_value
        except Exception:
            return False

    def _load_existing(self) -> None:
        """Carrega dados existentes do backend."""
        if self.backend.exists():
            try:
                stored_data = self.backend.load()
                if isinstance(stored_data, dict):
                    self._metadata = stored_data.get("metadata", self._metadata)

                    was_encrypted = self._metadata.get("encrypted", False)

                    if was_encrypted != self.encrypt_data:
                        logger.warning(
                            f"⚠️  Mudança no modo de criptografia detectada! "
                            f"Arquivo: {was_encrypted}, Atual: {self.encrypt_data}"
                        )

                    if self.encrypt_data:
                        if not self._validate_encryption_key():
                            raise EncryptionError(
                                "❌ Chave de criptografia inválida! "
                                "Verifique sua secret_key."
                            )
                        logger.info("✅ Chave de criptografia validada com sucesso")

                    self._data = stored_data.get("data", {})
                    logger.info(
                        f"Dados existentes carregados com sucesso ({len(self._data)} chaves)"
                    )

            except EncryptionError:
                raise
            except StorageError as e:
                logger.warning(f"Não foi possível carregar dados existentes: {e}")

    def _save_if_auto(self) -> None:
        """Salva automaticamente se auto_save estiver habilitado."""
        if self.auto_save:
            self.save()

    def set(self, key: str, value: Any, namespace: Optional[str] = None) -> None:
        """
        Define um valor no armazenamento.

        Args:
            key: Chave do valor
            value: Valor a ser armazenado
            namespace: Namespace opcional para organização
        """
        stored_value = self._encrypt_value(value) if self.encrypt_data else value

        if namespace:
            if namespace not in self._data:
                self._data[namespace] = {}
            self._data[namespace][key] = stored_value
        else:
            self._data[key] = stored_value

        self._metadata["last_modified"] = datetime.now().isoformat()
        self._save_if_auto()

        crypto_status = "🔐 criptografado" if self.encrypt_data else "🔓 plain"
        logger.debug(
            f"Valor definido ({crypto_status}): {namespace}.{key if namespace else key}"
        )

    def get(
        self, key: str, namespace: Optional[str] = None, default: Any = None
    ) -> Any:
        """
        Obtém um valor do armazenamento.

        Args:
            key: Chave do valor
            namespace: Namespace opcional
            default: Valor padrão se não encontrado

        Returns:
            Valor armazenado (descriptografado se necessário) ou default
        """
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
        """
        Remove um valor do armazenamento.

        Args:
            key: Chave do valor
            namespace: Namespace opcional

        Returns:
            True se removido, False se não encontrado
        """
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

            self._metadata["last_modified"] = datetime.now().isoformat()
            self._save_if_auto()
            logger.debug(f"Valor removido: {namespace}.{key if namespace else key}")
            return True

        except Exception as e:
            logger.error(f"Erro ao deletar {key}: {e}")
            return False

    def exists(self, key: str, namespace: Optional[str] = None) -> bool:
        """
        Verifica se uma chave existe.

        Args:
            key: Chave a verificar
            namespace: Namespace opcional

        Returns:
            True se existe, False caso contrário
        """
        if namespace:
            return namespace in self._data and key in self._data[namespace]
        return key in self._data

    def list_keys(self, namespace: Optional[str] = None) -> List[str]:
        """
        Lista todas as chaves em um namespace.

        Args:
            namespace: Namespace opcional

        Returns:
            Lista de chaves
        """
        if namespace:
            return list(self._data.get(namespace, {}).keys())
        return list(self._data.keys())

    def list_namespaces(self) -> List[str]:
        """
        Lista todos os namespaces.

        Returns:
            Lista de namespaces
        """
        return [k for k, v in self._data.items() if isinstance(v, dict)]

    def clear(self, namespace: Optional[str] = None) -> None:
        """
        Limpa dados do armazenamento.

        Args:
            namespace: Se especificado, limpa apenas o namespace
        """
        if namespace:
            if namespace in self._data:
                del self._data[namespace]
                logger.info(f"Namespace '{namespace}' limpo")
        else:
            self._data.clear()
            logger.info("Todos os dados foram limpos")

        self._metadata["last_modified"] = datetime.now().isoformat()
        self._save_if_auto()

    def save(self) -> None:
        """Salva manualmente os dados no backend."""
        try:
            full_data = {"data": self._data, "metadata": self._metadata}
            self.backend.save(full_data)
            crypto_info = " (criptografado)" if self.encrypt_data else ""
            logger.info(f"Dados salvos com sucesso{crypto_info}")
        except StorageError as e:
            logger.error(f"Erro ao salvar dados: {e}")
            raise

    def reload(self) -> None:
        """Recarrega dados do backend."""
        self._load_existing()

    def get_metadata(self) -> Dict[str, Any]:
        """
        Retorna metadados do armazenamento.

        Returns:
            Dicionário com metadados
        """
        meta = self._metadata.copy()
        meta.pop("_encryption_test", None)
        return meta

    def export_data(self, decrypt_export: bool = True) -> Dict[str, Any]:
        """
        Exporta todos os dados.

        Args:
            decrypt_export: Se True, exporta dados descriptografados

        Returns:
            Dicionário com todos os dados
        """
        if decrypt_export and self.encrypt_data:
            decrypted_data = {}
            for key, value in self._data.items():
                if isinstance(value, dict):
                    decrypted_data[key] = {
                        k: self._decrypt_value(v) for k, v in value.items()
                    }
                else:
                    decrypted_data[key] = self._decrypt_value(value)

            return {"data": decrypted_data, "metadata": self.get_metadata()}
        else:
            return {"data": self._data.copy(), "metadata": self.get_metadata()}

    def import_data(self, data: Dict[str, Any], merge: bool = False) -> None:
        """
        Importa dados.

        Args:
            data: Dados a importar
            merge: Se True, mescla com dados existentes
        """
        imported_data = data.get("data", {})

        if self.encrypt_data:
            encrypted_import = {}
            for key, value in imported_data.items():
                if isinstance(value, dict):
                    encrypted_import[key] = {
                        k: self._encrypt_value(v) for k, v in value.items()
                    }
                else:
                    encrypted_import[key] = self._encrypt_value(value)
            imported_data = encrypted_import

        if merge:
            self._data.update(imported_data)
            self._metadata.update(data.get("metadata", {}))
        else:
            self._data = imported_data
            self._metadata = data.get("metadata", self._metadata)

        self._metadata["last_modified"] = datetime.now().isoformat()
        self._metadata["encrypted"] = self.encrypt_data
        self._save_if_auto()
        logger.info("Dados importados com sucesso")

    def change_secret_key(self, new_secret_key: str) -> None:
        """
        Altera a chave secreta de criptografia.
        Descriptografa todos os dados com a chave antiga e recriptografa com a nova.

        Args:
            new_secret_key: Nova chave secreta

        Raises:
            EncryptionError: Se não estiver usando criptografia
        """
        if not self.encrypt_data:
            raise EncryptionError("Criptografia não está ativada")

        logger.info("🔄 Iniciando troca de chave de criptografia...")

        decrypted_data = {}
        for key, value in self._data.items():
            if isinstance(value, dict):
                decrypted_data[key] = {
                    k: self._decrypt_value(v) for k, v in value.items()
                }
            else:
                decrypted_data[key] = self._decrypt_value(value)

        self._secret_key = new_secret_key

        self._data = {}
        for key, value in decrypted_data.items():
            if isinstance(value, dict):
                self._data[key] = {k: self._encrypt_value(v) for k, v in value.items()}
            else:
                self._data[key] = self._encrypt_value(value)

        self._metadata.pop("_encryption_test", None)
        self._validate_encryption_key()

        self.save()
        logger.info("✅ Chave de criptografia alterada com sucesso!")

    def __enter__(self):
        """Context manager entrada."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager saída - salva automaticamente."""
        if not exc_type:
            self.save()

    def __repr__(self) -> str:
        """Representação string do objeto."""
        crypto = "🔐" if self.encrypt_data else "🔓"
        return f"SecureStorage({crypto} keys={len(self._data)}, backend={type(self.backend).__name__})"


if __name__ == "__main__":
    print("=" * 70)
    print("🔐 SECURE STORAGE V2 - TESTES")
    print("=" * 70)

    print("\n=== Exemplo 1: Modo Normal (Sem Criptografia) ===")
    storage = SecureStorage(storage_path="test_normal.json", encrypt_data=False)

    storage.set("user_id", "12345")
    storage.set("username", "john_doe")
    storage.set("preferences", {"theme": "dark", "language": "pt-BR"})

    print(f"User ID: {storage.get('user_id')}")
    print(f"Username: {storage.get('username')}")
    print(f"Preferences: {storage.get('preferences')}")

    print("\n=== Exemplo 2: Modo Seguro (Com Criptografia) ===")

    SECRET_KEY = os.getenv("SECURE_STORAGE_SECRET_KEY")

    secure_storage = SecureStorage(
        storage_path="test_encrypted.json", encrypt_data=True, secret_key=SECRET_KEY
    )

    secure_storage.set("api_key", "sk_live_123456789abcdef")
    secure_storage.set("credit_card", "4111-1111-1111-1111", namespace="payment")
    secure_storage.set("password", "minha_senha_secreta", namespace="auth")

    print(f"API Key: {secure_storage.get('api_key')}")
    print(f"Credit Card: {secure_storage.get('credit_card', namespace='payment')}")
    print(f"Password: {secure_storage.get('password', namespace='auth')}")

    print("\n=== Exemplo 3: Validação de Chave ===")
    try:
        wrong_storage = SecureStorage(
            storage_path="test_encrypted.json",
            encrypt_data=True,
            secret_key="chave_errada_123",
        )
    except EncryptionError as e:
        print(f"✓ Erro esperado capturado: {e}")

    print("\n=== Exemplo 4: Export/Import ===")
    exported = secure_storage.export_data(decrypt_export=True)
    print(f"Dados exportados (descriptografados): {list(exported['data'].keys())}")

    print("\n=== Exemplo 5: Troca de Chave de Criptografia ===")
    NEW_SECRET_KEY = "nova_senha_ainda_mais_secreta_456"
    secure_storage.change_secret_key(NEW_SECRET_KEY)
    print(f"✓ Chave alterada! Testando acesso: {secure_storage.get('api_key')}")

    print("\n=== Exemplo 6: Secret Key via Environment ===")
    env_storage = SecureStorage(
        storage_path="test_env.json",
        encrypt_data=True,
        secret_key=SECRET_KEY,
    )
    env_storage.set("env_data", "dados via ambiente")
    print(f"✓ Dados via ambiente: {env_storage.get('env_data')}")

    print("\n=== Limpeza ===")
    for file in ["test_normal.json", "test_encrypted.json", "test_env.json"]:
        if Path(file).exists():
            Path(file).unlink()
            print(f"Arquivo '{file}' removido")

    print("\n" + "=" * 70)
    print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 70)

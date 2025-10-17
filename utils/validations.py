import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import flet as ft

from services.supabase_utils import set_user_inactive

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado de uma validação com informações de erro."""

    valid: bool
    error: Optional[str] = None

    def __bool__(self) -> bool:
        return self.valid

    def __str__(self) -> str:
        return self.error if self.error else "Válido"


class URLValidator:
    """Validador de URLs do YouTube."""

    YOUTUBE_PATTERN = r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$"

    @classmethod
    def validate(cls, url: str) -> ValidationResult:
        """
        Valida se a URL fornecida é um link válido do YouTube.

        Args:
            url: URL a ser validada

        Returns:
            ValidationResult: Resultado da validação
        """
        if not url or not url.strip():
            return ValidationResult(False, "O campo de link não pode estar vazio")

        url = url.strip()

        if not re.match(cls.YOUTUBE_PATTERN, url):
            return ValidationResult(
                False, "URL inválida. Por favor, insira um link válido do YouTube"
            )

        return ValidationResult(True)


class EmailValidator:
    """Validador de endereços de e-mail."""

    EMAIL_PATTERN = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    @classmethod
    def validate(cls, email: str) -> ValidationResult:
        """
        Valida se o e-mail tem formato válido.

        Args:
            email: E-mail a ser validado

        Returns:
            ValidationResult: Resultado da validação
        """
        if not email or not email.strip():
            return ValidationResult(False, "E-mail não pode estar vazio")

        email = email.strip()

        if not re.match(cls.EMAIL_PATTERN, email):
            return ValidationResult(False, "Formato de e-mail inválido")

        return ValidationResult(True)


class AuthValidator:
    """Validador de autenticação e autorização de usuários."""

    @staticmethod
    def verify_auth(page: ft.Page) -> bool:
        """
        Verifica a autenticação do usuário e a validade da assinatura.

        Args:
            page: Página Flet atual

        Returns:
            bool: True se usuário está autenticado e assinatura válida
        """
        data_expiracao = page.client_storage.get("data_expiracao")

        if not data_expiracao:
            logger.info("Data de expiração não encontrada")
            page.client_storage.set("autenticado", False)
            page.update()
            page.go("/login")
            return False

        try:
            data_expiracao = datetime.fromisoformat(data_expiracao).replace(
                tzinfo=timezone.utc
            )
            agora = datetime.now(timezone.utc)

            if agora > data_expiracao:
                logger.info("Assinatura expirada")
                page.client_storage.set("autenticado", False)

                user_id = page.client_storage.get("user_id")
                if user_id:
                    set_user_inactive(user_id)

                page.update()
                page.go("/login")
                return False

            dias_restantes = (data_expiracao - agora).days
            page.client_storage.set("dias_restantes", dias_restantes)

            logger.info(f"Usuário autenticado. Dias restantes: {dias_restantes}")

            return True

        except (ValueError, TypeError) as e:
            logger.error(f"Erro ao processar data de expiração: {e}")
            page.client_storage.set("autenticado", False)
            page.update()
            page.go("/login")
            return False


class UIValidator:
    """Validador com integração UI para feedback visual."""

    @staticmethod
    def show_error(page: ft.Page, message: str):
        """
        Exibe mensagem de erro na interface.

        Args:
            page: Página Flet atual
            message: Mensagem de erro a ser exibida
        """
        snack_bar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR),
                    ft.Text(message),
                ]
            ),
            duration=3000,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    @staticmethod
    def validate_input(page: ft.Page, input_value: str) -> bool:
        """
        Valida o input do usuário e exibe erro se necessário.

        Args:
            page: Página Flet atual
            input_value: Valor de entrada a ser validado

        Returns:
            bool: True se válido, False caso contrário
        """
        result = URLValidator.validate(input_value)

        if not result:
            UIValidator.show_error(page, result.error)
            return False

        return True


def validar_url_youtube(url: str) -> bool:
    """
    DEPRECATED: Use URLValidator.validate() ao invés.
    Mantido para compatibilidade.
    """
    import warnings

    warnings.warn(
        "validar_url_youtube está depreciado. Use URLValidator.validate()",
        DeprecationWarning,
        stacklevel=2,
    )

    result = URLValidator.validate(url)
    return result.valid


def validar_email(email: str) -> bool:
    """
    DEPRECATED: Use EmailValidator.validate() ao invés.
    Mantido para compatibilidade.
    """
    import warnings

    warnings.warn(
        "validar_email está depreciado. Use EmailValidator.validate()",
        DeprecationWarning,
        stacklevel=2,
    )

    result = EmailValidator.validate(email)
    return result.valid


def exibir_mensagem_erro(page: ft.Page, message: str):
    """
    DEPRECATED: Use UIValidator.show_error() ao invés.
    Mantido para compatibilidade.
    """
    import warnings

    warnings.warn(
        "exibir_mensagem_erro está depreciado. Use UIValidator.show_error()",
        DeprecationWarning,
        stacklevel=2,
    )

    UIValidator.show_error(page, message)


def validar_input(page: ft.Page, input_value: str) -> bool:
    """
    DEPRECATED: Use UIValidator.validate_input() ao invés.
    Mantido para compatibilidade.
    """
    import warnings

    warnings.warn(
        "validar_input está depreciado. Use UIValidator.validate_input()",
        DeprecationWarning,
        stacklevel=2,
    )

    return UIValidator.validate_input(page, input_value)


def verify_auth(page: ft.Page) -> bool:
    """
    DEPRECATED: Use AuthValidator.verify_auth() ao invés.
    Mantido para compatibilidade.
    """
    import warnings

    warnings.warn(
        "verify_auth está depreciado. Use AuthValidator.verify_auth()",
        DeprecationWarning,
        stacklevel=2,
    )

    return AuthValidator.verify_auth(page)

import re
import logging
import flet as ft
from datetime import datetime, timezone
from services.supabase_utils import set_user_inactive
# Configura o logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def validar_url_youtube(url: str) -> bool:
    """
    Valida se a URL fornecida é um link válido do YouTube.

    Args:
        url (str): A URL do vídeo.

    Returns:
        bool: True se a URL for válida, False caso contrário.
    """
    youtube_regex = r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$"
    return re.match(youtube_regex, url) is not None


def exibir_mensagem_erro(page: ft.Page, message: str):
    """
    Exibe uma mensagem de erro na interface.

    Args:
        page (ft.Page): A página atual da aplicação Flet.
        message (str): A mensagem de erro a ser exibida.
    """
    snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.Colors.ERROR,
    )
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()


def validar_input(page: ft.Page, input_value: str) -> bool:
    """
    Valida o valor de entrada do usuário, verificando se o campo está vazio e se a URL é válida.

    Args:
        page (ft.Page): A página atual da aplicação Flet.
        input_value (str): O valor de entrada a ser validado.

    Returns:
        bool: True se o input for válido, False caso contrário.
    """
    if not input_value.strip():
        exibir_mensagem_erro(page, "O campo de link não pode estar vazio.")
        return False

    if not validar_url_youtube(input_value.strip()):
        exibir_mensagem_erro(
            page, "URL inválida. Por favor, insira um link válido do YouTube.")
        return False

    return True


def verify_auth(page: ft.Page) -> bool:
    """
    Verifica a autenticação do usuário e a validade da assinatura.

    Args:
        page (ft.Page): A página atual da aplicação Flet.

    Returns:
        bool: True se o usuário estiver autenticado e a assinatura for válida, False caso contrário.
    """
    data_expiracao = page.client_storage.get("data_expiracao")

    if data_expiracao:
        # Converte a data_expiracao para datetime e adiciona o fuso horário UTC
        data_expiracao = datetime.fromisoformat(
            data_expiracao).replace(tzinfo=timezone.utc)
        agora = datetime.now(timezone.utc)

        if agora > data_expiracao:
            page.client_storage.set("autenticado", False)
            logging.info("Usuário expirado")
            # Inativa o usuário no banco de dados
            user_id = page.client_storage.get("user_id")
            set_user_inactive(user_id)
            page.update()
            page.go("/login")
            return False
        else:
            # Caso a data de expiração seja válida, mostra os dias restantes
            dias_restantes = (data_expiracao - agora).days
            page.client_storage.set("dias_restantes", dias_restantes)
            logging.info(f"Usuário autenticado. Dias restantes: {
                         dias_restantes}")
            return True
    else:
        # Se não encontrar a chave de expiração, desautentica o usuário
        page.client_storage.set("autenticado", False)
        logging.info("Usuário não autenticado")
        page.update()
        page.go("/login")
        return False


def validar_email(email: str) -> bool:
    """
    Valida se o e-mail fornecido tem um formato válido.

    Args:
        email (str): O e-mail a ser validado.

    Returns:
        bool: True se o e-mail for válido, False caso contrário.
    """
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

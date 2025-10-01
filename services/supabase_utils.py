import os
import logging
from datetime import datetime
import pytz
import requests
from dotenv import load_dotenv
import flet as ft

load_dotenv()

SUPABASE_KEY_USERS = os.getenv("SUPABASE_KEY_USERS")
SUPABASE_URL_USERS = os.getenv("SUPABASE_URL_USERS")
LOCAL_TIMEZONE = pytz.timezone("America/Sao_Paulo")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def _get_headers() -> dict:
    """
    Retorna os headers padrão para requisições ao Supabase.
    """
    return {
        "apikey": SUPABASE_KEY_USERS,
        "Authorization": f"Bearer {SUPABASE_KEY_USERS}",
        "Content-Type": "application/json"
    }


def validate_user(username: str, password: str) -> tuple[str, dict | None]:
    """
    Valida um usuário no Supabase verificando existência, senha e status.

    Args:
        username: Nome de usuário.
        password: Senha fornecida.

    Returns:
        Tuple contendo status ("success", "invalid", "inactive") e dados do usuário se aplicável.
    """
    url = f"{SUPABASE_URL_USERS}/rest/v1/users?username=eq.{username}&select=*"

    try:
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()

        user_data = response.json()
        if not user_data:
            logging.warning(f"Usuário {username} não encontrado.")
            return "invalid", None

        user = user_data[0]

        if user.get('password') != password:
            logging.warning(f"Senha incorreta para o usuário {username}.")
            return "invalid", None

        if user.get('status') != "ativo":
            logging.warning(f"Usuário {username} não está ativo.")
            return "inactive", user

        return "success", user

    except requests.RequestException as e:
        logging.error(f"Erro ao verificar o usuário {username}: {e}")
        return "invalid", None


def set_user_inactive(user_id: str) -> None:
    """
    Marca o usuário como inativo no Supabase.

    Args:
        user_id: ID do usuário.
    """
    url = f"{SUPABASE_URL_USERS}/rest/v1/users?id=eq.{user_id}"
    data = {"status": "inativo"}

    try:
        response = requests.patch(url, headers=_get_headers(), json=data)
        response.raise_for_status()
        if response.status_code in [200, 204]:
            logging.info(f"Usuário {user_id} inativado com sucesso.")
        else:
            logging.error(
                f"Erro ao inativar o usuário {user_id}: {response.text}")
    except requests.RequestException as e:
        logging.error(f"Erro ao inativar o usuário {user_id}: {e}")


def update_user_last_login(user_id: str, last_login: str) -> None:
    """
    Atualiza a data/hora do último login de um usuário.

    Args:
        user_id: ID do usuário.
        last_login: Data/hora do último login em formato ISO.
    """
    logging.info(f"Atualizando último login do usuário {user_id}...")

    try:
        last_login_dt = datetime.fromisoformat(last_login)
    except ValueError as e:
        logging.error(f"Erro ao converter last_login para datetime: {e}")
        return

    local_last_login = last_login_dt.astimezone(LOCAL_TIMEZONE)
    url = f"{SUPABASE_URL_USERS}/rest/v1/users?id=eq.{user_id}"
    data = {"ultimo_login": local_last_login.isoformat()}

    try:
        response = requests.patch(url, headers=_get_headers(), json=data)
        response.raise_for_status()
        logging.info(
            f"Último login do usuário {user_id} atualizado com sucesso.")
    except requests.RequestException as e:
        logging.error(f"Erro ao atualizar os dados do usuário {user_id}: {e}")


def user_is_active(user_id: str) -> bool:
    """
    Verifica se o usuário está ativo.

    Args:
        user_id: ID do usuário.

    Returns:
        True se o usuário estiver ativo, False caso contrário.
    """
    url = f"{SUPABASE_URL_USERS}/rest/v1/users?id=eq.{user_id}&select=status"

    try:
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()

        user_data = response.json()
        if not user_data:
            logging.warning(f"Usuário {user_id} não encontrado.")
            return False

        return user_data[0].get('status') == "ativo"

    except requests.RequestException as e:
        logging.error(f"Erro ao verificar o usuário {user_id}: {e}")
        return False


def verificar_status_usuario(page: ft.Page) -> None:
    """
    Verifica se o usuário está logado e ativo, caso contrário redireciona para login.

    Args:
        page: Página Flet corrente.
    """
    try:
        logging.info("Tentando acessar 'user_id' no clientStorage...")
        user_id = page.client_storage.get("user_id")

        if not user_id:
            logging.error(
                "Chave 'user_id' não encontrada ou clientStorage indisponível.")
            page.client_storage.clear()
            page.go("/login")
            return

        if not user_is_active(user_id):
            logging.info(
                "Usuário inativo, redirecionando para a página de login.")
            page.client_storage.clear()
            page.go("/login")

    except Exception as e:
        logging.error(f"Erro ao verificar o status do usuário: {e}")

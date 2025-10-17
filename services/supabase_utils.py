import os
from datetime import datetime

import flet as ft
import pytz
from dotenv import load_dotenv
from loguru import logger
from supabase import Client, create_client

load_dotenv()

SUPABASE_KEY_USERS = os.getenv("SUPABASE_KEY_USERS")
SUPABASE_URL_USERS = os.getenv("SUPABASE_URL_USERS")
LOCAL_TIMEZONE = pytz.timezone("America/Sao_Paulo")

supabase: Client = create_client(SUPABASE_URL_USERS, SUPABASE_KEY_USERS)


def validate_user(username: str, password: str) -> tuple[str, dict | None]:
    try:
        response = (
            supabase.table("users").select("*").eq("username", username).execute()
        )

        if not response.data:
            logger.warning(f"Usuário {username} não encontrado.")
            return "invalid", None

        user = response.data[0]

        if user.get("password") != password:
            logger.warning(f"Senha incorreta para o usuário {username}.")
            return "invalid", None

        if user.get("status") != "ativo":
            logger.warning(f"Usuário {username} não está ativo.")
            return "inactive", user

        return "success", user

    except Exception as e:
        logger.error(f"Erro ao verificar o usuário {username}: {e}")
        return "invalid", None


def set_user_inactive(user_id: str) -> None:
    try:
        response = (
            supabase.table("users")
            .update({"status": "inativo"})
            .eq("id", user_id)
            .execute()
        )

        if response.data:
            logger.info(f"Usuário {user_id} inativado com sucesso.")
        else:
            logger.error(f"Erro ao inativar o usuário {user_id}")
    except Exception as e:
        logger.error(f"Erro ao inativar o usuário {user_id}: {e}")


def update_user_last_login(user_id: str, last_login: str) -> None:
    logger.info(f"Atualizando último login do usuário {user_id}...")

    try:
        last_login_dt = datetime.fromisoformat(last_login)
        local_last_login = last_login_dt.astimezone(LOCAL_TIMEZONE)

        response = (
            supabase.table("users")
            .update({"ultimo_login": local_last_login.isoformat()})
            .eq("id", user_id)
            .execute()
        )

        if response.data:
            logger.info(f"Último login do usuário {user_id} atualizado com sucesso.")
        else:
            logger.error(f"Erro ao atualizar último login do usuário {user_id}")
    except ValueError as e:
        logger.error(f"Erro ao converter last_login para datetime: {e}")
    except Exception as e:
        logger.error(f"Erro ao atualizar os dados do usuário {user_id}: {e}")


def user_is_active(user_id: str) -> bool:
    try:
        response = supabase.table("users").select("status").eq("id", user_id).execute()

        if not response.data:
            logger.warning(f"Usuário {user_id} não encontrado.")
            return False

        return response.data[0].get("status") == "ativo"

    except Exception as e:
        logger.error(f"Erro ao verificar o usuário {user_id}: {e}")
        return False


def verificar_status_usuario(page: ft.Page) -> None:
    try:
        logger.info("Tentando acessar 'user_id' no clientStorage...")
        user_id = page.client_storage.get("user_id")

        if not user_id:
            logger.error(
                "Chave 'user_id' não encontrada ou clientStorage indisponível."
            )
            page.client_storage.clear()
            page.go("/login")
            return

        if not user_is_active(user_id):
            logger.info("Usuário inativo, redirecionando para a página de login.")
            page.client_storage.clear()
            page.go("/login")

    except Exception as e:
        logger.error(f"Erro ao verificar o status do usuário: {e}")

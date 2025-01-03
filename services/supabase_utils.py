import asyncio
import os
import logging
import requests
import pysnooper
from dotenv import load_dotenv
from datetime import datetime
import pytz
import flet as ft

load_dotenv()

SUPABASE_KEY_USERS = os.getenv("SUPABASE_KEY_USERS")
SUPABASE_URL_USERS = os.getenv("SUPABASE_URL_USERS")

# Configurando o logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

# Defina o fuso horário local
LOCAL_TIMEZONE = pytz.timezone("America/Sao_Paulo")


def validate_user(username: str, password: str) -> tuple:
    headers = {
        "apikey": SUPABASE_KEY_USERS,
        "Authorization": f"Bearer {SUPABASE_KEY_USERS}"
    }

    url = f"{SUPABASE_URL_USERS}/rest/v1/users?username=eq.{username}&select=*"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        user_data = response.json()
        if not user_data:
            logging.warning(f"Usuário {username} não encontrado.")
            return "invalid", None

        user = user_data[0]

        if user['password'] != password:
            logging.warning(f"Senha incorreta para o usuário {username}.")
            return "invalid", None

        if user['status'] != "ativo":
            logging.warning(f"Usuário {username} não está ativo.")
            return "inactive", user

        return "success", user

    except requests.RequestException as e:
        logging.error(f"Erro ao verificar o usuário {username}: {e}")
        return "invalid", None

def user_inative(user_id: str):
    headers = {
        "apikey": SUPABASE_KEY_USERS,
        "Authorization": f"Bearer {SUPABASE_KEY_USERS}",
        "Content-Type": "application/json"
    }

    update_url = f"{SUPABASE_URL_USERS}/rest/v1/users?id=eq.{user_id}"

    data = {
        "status": "inativo"
    }

    try:
        response = requests.patch(update_url, headers=headers, json=data)
        response.raise_for_status()

        if response.status_code in [200, 204]:
            logging.info(f"Usuário {user_id} inativado com sucesso.")
        else:
            logging.error(f"Erro ao inativar o usuário {user_id}: {response.text}")

    except requests.RequestException as e:
        logging.error(f"Erro ao inativar o usuário {user_id}: {e}")

def update_user_last_login(user_id: str, last_login: str):
    logging.info(f"Atualizando último login do usuário {user_id}...")
    headers = {
        "apikey": SUPABASE_KEY_USERS,
        "Authorization": f"Bearer {SUPABASE_KEY_USERS}",
        "Content-Type": "application/json"
    }

    update_url = f"{SUPABASE_URL_USERS}/rest/v1/users?id=eq.{user_id}"

    # Converte last_login de string para datetime
    try:
        last_login_datetime = datetime.fromisoformat(last_login)
    except ValueError as e:
        logging.error(f"Erro ao converter last_login para datetime: {e}")
        return

    # Ajusta o last_login para o fuso horário local
    local_last_login = last_login_datetime.astimezone(LOCAL_TIMEZONE)

    data = {
        "ultimo_login": local_last_login.isoformat()
    }

    try:
        response = requests.patch(update_url, headers=headers, json=data)
        response.raise_for_status()

        if response.status_code in [200, 204]:
            logging.info(f"Último login do usuário {user_id} atualizado com sucesso.")
        else:
            logging.error(f"Erro ao atualizar o último login do usuário {user_id}: {response.text}")

    except requests.RequestException as e:
        logging.error(f"Erro ao atualizar os dados do usuário {user_id}: {e}")

# verifica se o usuário ainda está ativo
def user_is_active(user_id: str):
    headers = {
        "apikey": SUPABASE_KEY_USERS,
        "Authorization": f"Bearer {SUPABASE_KEY_USERS}"
    }

    url = f"{SUPABASE_URL_USERS}/rest/v1/users?id=eq.{user_id}&select=status"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        user_data = response.json()
        if not user_data:
            logging.warning(f"Usuário {user_id} não encontrado.")
            return False

        user = user_data[0]

        if user['status'] != "ativo":
            logging.warning(f"Usuário {user_id} não está ativo.")
            return False

        return True

    except requests.RequestException as e:
        logging.error(f"Erro ao verificar o usuário {user_id}: {e}")
        return False
    
def verificar_status_usuario(page):
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
            page.client_storage.clear()
            page.go("/login")
            logging.info(
                "Usuário inativo, redirecionando para a página de login.")
    except Exception as e:
        logging.error(f"Erro ao verificar o status do usuário: {e}")

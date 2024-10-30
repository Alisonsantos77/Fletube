# send_feedback.py

import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
from dotenv import load_dotenv
import requests
import flet as ft
import re
from datetime import datetime, timezone

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    filename="logs/app.log",
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("flet_core").setLevel(logging.INFO)

# Variáveis de configuração
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FEEDBACK_RECIPIENT_EMAIL = os.getenv("FEEDBACK_RECIPIENT_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def is_valid_email(email):
    """
    Verifica se o email está no formato correto.
    """
    email_regex = r"(^[\w\.\-]+@[\w\-]+\.[a-zA-Z]{2,}$)"
    return re.match(email_regex, email) is not None


def save_feedback_locally(feedback_data):
    backup_file = "feedback_backup.json"
    try:
        if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
            with open(backup_file, "r", encoding="utf-8") as file:
                backups = json.load(file)
        else:
            backups = []

        feedback_data["created_at"] = datetime.now(timezone.utc).isoformat()
        backups.append(feedback_data)

        with open(backup_file, "w", encoding="utf-8") as file:
            json.dump(backups, file, ensure_ascii=False, indent=4)

        logging.info("Feedback salvo localmente devido à falha no Supabase.")
    except Exception as e:
        logging.error(f"Erro ao salvar feedback localmente: {e}")


def sync_local_feedback(page: ft.Page):
    """
    Tenta sincronizar os feedbacks salvos localmente com o Supabase.
    """
    backup_file = "feedback_backup.json"
    if not os.path.exists(backup_file):
        logging.info("Nenhum feedback pendente para reenvio.")
        return

    try:
        with open(backup_file, "r", encoding="utf-8") as file:
            backups = json.load(file)

        if not backups:
            logging.info("Nenhum feedback pendente para reenvio.")
            return

        supabase_endpoint = f"{SUPABASE_URL}/rest/v1/feedbacks"
        headers_supabase = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        successfully_synced = []

        for feedback in backups:
            # Verifica se o feedback é um dicionário antes de tentar acessar as chaves
            if not isinstance(feedback, dict):
                logging.warning("Formato inválido de feedback no arquivo de backup.")
                continue  # Ignora itens com formato incorreto

            feedback_data = {
                "email": feedback.get("email", ""),
                "rating": feedback.get("rating", 0),
                "category": feedback.get("category", ""),
                "subcategory": feedback.get("subcategory", ""),
                "feedback_text": feedback.get("feedback_text", ""),
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

            try:
                res_supabase = requests.post(
                    supabase_endpoint,
                    headers=headers_supabase,
                    json=feedback_data,
                    timeout=10,
                )

                if res_supabase.status_code in [200, 201]:
                    logging.info(f"Feedback sincronizado com sucesso: {feedback_data}")
                    successfully_synced.append(feedback)
                else:
                    error_message = f"Erro ao sincronizar feedback: {res_supabase.status_code}, {res_supabase.text}"
                    logging.error(error_message)

            except Exception as e:
                logging.error(f"Erro ao sincronizar feedback para o Supabase: {e}")

        # Remover feedbacks sincronizados com sucesso
        backups = [fb for fb in backups if fb not in successfully_synced]

        # Atualizar o arquivo de backup
        with open(backup_file, "w", encoding="utf-8") as file:
            json.dump(backups, file, ensure_ascii=False, indent=4)

        if not backups:
            os.remove(backup_file)  # Remove o arquivo se estiver vazio
            logging.info(
                "Todos os feedbacks locais foram sincronizados e o arquivo de backup foi removido."
            )
        else:
            logging.info("Alguns feedbacks ainda precisam ser reenviados.")
    except Exception as e:
        logging.error(f"Erro ao sincronizar feedbacks locais: {e}")


def retry_failed_feedbacks(page: ft.Page):
    """
    Retenta enviar feedbacks locais ao iniciar a aplicação.
    """
    sync_local_feedback(page)


def send_feedback_email(user_email, user_message, page: ft.Page):
    """
    Envia um email de feedback e armazena os dados no Supabase.
    """
    if not is_valid_email(user_email):
        snack_bar = ft.SnackBar(
            content=ft.Text(
                "Endereço de email inválido. Por favor, insira um email válido."
            ),
            bgcolor=ft.colors.ERROR,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        logging.error(f"Email inválido fornecido: {user_email}")
        return False

    feedback_data = {
        "email": user_email,
        "rating": user_message.get("rating", 0),
        "category": user_message.get("category", ""),
        "subcategory": user_message.get("subcategory", ""),
        "feedback_text": user_message.get("feedback_text", ""),
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        supabase_endpoint = f"{SUPABASE_URL}/rest/v1/feedbacks"
        headers_supabase = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        res_supabase = requests.post(
            supabase_endpoint, headers=headers_supabase, json=feedback_data, timeout=10
        )

        if res_supabase.status_code in [200, 201]:
            logging.info("Feedback armazenado no Supabase com sucesso.")
        else:
            logging.error(
                f"Erro ao armazenar feedback no Supabase: {res_supabase.status_code}, {res_supabase.text}"
            )
            save_feedback_locally(feedback_data)
            return False

    except requests.exceptions.Timeout:
        logging.error("Timeout ao conectar com o Supabase.")
        save_feedback_locally(feedback_data)
        return False

    except Exception as e:
        logging.error(f"Erro ao enviar feedback para o Supabase: {e}")
        save_feedback_locally(feedback_data)
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_USER
        msg["To"] = FEEDBACK_RECIPIENT_EMAIL
        msg["Subject"] = "Feedback - Fletube"
        feedback_text = user_message.get("feedback_text", "")
        markdown_body = (
            f"## Feedback - Fletube\n\n"
            f"**Email do Usuário:** {user_email}\n"
            f"**Avaliação:** {user_message.get('rating', 0)} estrelas\n"
            f"**Categoria:** {user_message.get('category', '')}\n"
            f"**Subcategoria:** {user_message.get('subcategory', '')}\n\n"
            f"**Feedback:**\n{feedback_text}"
        )
        msg.attach(MIMEText(markdown_body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, FEEDBACK_RECIPIENT_EMAIL, msg.as_string())

        logging.info("Feedback enviado por e-mail com sucesso.")
        return True

    except Exception as e:
        logging.error(f"Erro ao enviar feedback por e-mail: {e}")
        return False


def clean_feedback_backup():
    """
    Limpa o arquivo de backup para garantir que todos os feedbacks estejam no formato correto.
    """
    backup_file = "feedback_backup.json"
    if not os.path.exists(backup_file):
        logging.info("Nenhum feedback de backup para limpar.")
        return

    try:
        with open(backup_file, "r", encoding="utf-8") as file:
            backups = json.load(file)

        # Manter apenas itens que são dicionários com as chaves esperadas
        cleaned_backups = [
            fb
            for fb in backups
            if isinstance(fb, dict) and "email" in fb and "feedback_text" in fb
        ]

        # Atualizar o arquivo com os feedbacks válidos
        with open(backup_file, "w", encoding="utf-8") as file:
            json.dump(cleaned_backups, file, ensure_ascii=False, indent=4)

        logging.info("Arquivo de backup de feedbacks foi limpo e atualizado.")
    except Exception as e:
        logging.error(f"Erro ao limpar o arquivo de backup de feedbacks: {e}")

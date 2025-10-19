import json
import os
import re
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import flet as ft
from dotenv import load_dotenv
from loguru import logger
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL_USERS")
SUPABASE_KEY = os.getenv("SUPABASE_KEY_USERS")
FEEDBACK_RECIPIENT_EMAIL = os.getenv("FEEDBACK_RECIPIENT_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def is_valid_email(email: str) -> bool:
    email_regex = r"(^[\w\.\-]+@[\w\-]+\.[a-zA-Z]{2,}$)"
    return re.match(email_regex, email) is not None


def save_feedback_locally(feedback_data: dict) -> None:
    backup_file = "feedback_backup.json"
    try:
        backups = []
        if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
            with open(backup_file, "r", encoding="utf-8") as file:
                backups = json.load(file)

        feedback_data["created_at"] = datetime.now(timezone.utc).isoformat()
        backups.append(feedback_data)

        with open(backup_file, "w", encoding="utf-8") as file:
            json.dump(backups, file, ensure_ascii=False, indent=4)

        logger.info("Feedback salvo localmente devido à falha no Supabase.")
    except Exception as e:
        logger.error(f"Erro ao salvar feedback localmente: {e}")


def sync_local_feedback(page: ft.Page) -> None:
    backup_file = "feedback_backup.json"
    if not os.path.exists(backup_file):
        logger.info("Nenhum feedback pendente para reenvio.")
        return

    try:
        with open(backup_file, "r", encoding="utf-8") as file:
            backups = json.load(file)

        if not backups:
            logger.info("Nenhum feedback pendente para reenvio.")
            return

        successfully_synced = []

        for feedback in backups:
            if not isinstance(feedback, dict):
                logger.warning("Formato inválido de feedback no arquivo de backup.")
                continue

            feedback_data = {
                "email": feedback.get("email", ""),
                "rating": feedback.get("rating", 0),
                "category": feedback.get("category", ""),
                "subcategory": feedback.get("subcategory", ""),
                "feedback_text": feedback.get("feedback_text", ""),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            try:
                response = supabase.table("feedbacks").insert(feedback_data).execute()

                if response.data:
                    logger.info(f"Feedback sincronizado com sucesso: {feedback_data}")
                    successfully_synced.append(feedback)
                else:
                    logger.error(f"Erro ao sincronizar feedback")
            except Exception as e:
                logger.error(f"Erro ao sincronizar feedback para o Supabase: {e}")

        backups = [fb for fb in backups if fb not in successfully_synced]

        with open(backup_file, "w", encoding="utf-8") as file:
            json.dump(backups, file, ensure_ascii=False, indent=4)

        if not backups:
            os.remove(backup_file)
            logger.info(
                "Todos os feedbacks locais foram sincronizados e o backup removido."
            )
        else:
            logger.info("Alguns feedbacks ainda precisam ser reenviados.")
    except Exception as e:
        logger.error(f"Erro ao sincronizar feedbacks locais: {e}")


def retry_failed_feedbacks(page: ft.Page) -> None:
    sync_local_feedback(page)


def send_feedback_email(user_email: str, user_message: dict, page: ft.Page) -> bool:
    from utils.ui_helpers import show_error_snackbar

    if not is_valid_email(user_email):
        show_error_snackbar(page, "Endereço de email inválido. Insira um email válido.")
        logger.error(f"Email inválido fornecido: {user_email}")
        return False

    feedback_data = {
        "email": user_email,
        "rating": user_message.get("rating", 0),
        "category": user_message.get("category", ""),
        "subcategory": user_message.get("subcategory", ""),
        "feedback_text": user_message.get("feedback_text", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        response = supabase.table("feedbacks").insert(feedback_data).execute()

        if not response.data:
            logger.error(f"Erro ao armazenar feedback no Supabase")
            save_feedback_locally(feedback_data)
            return False
        logger.info("Feedback armazenado no Supabase com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao enviar feedback para o Supabase: {e}")
        save_feedback_locally(feedback_data)
        return False

    try:
        if not all([SMTP_SERVER, EMAIL_USER, EMAIL_PASSWORD, FEEDBACK_RECIPIENT_EMAIL]):
            logger.warning("Configurações SMTP incompletas. Email não enviado.")
            logger.info("Feedback salvo no banco, mas email não foi enviado.")
            return True

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

        server = None
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
            server.ehlo()  # Identifica-se ao servidor

            # Inicia TLS
            server.starttls()
            server.ehlo()  # Identifica-se novamente após TLS

            # Faz login
            server.login(EMAIL_USER, EMAIL_PASSWORD)

            # Envia o email
            server.sendmail(EMAIL_USER, FEEDBACK_RECIPIENT_EMAIL, msg.as_string())

            logger.info("✅ Feedback enviado por e-mail com sucesso.")
            return True

        finally:
            if server:
                try:
                    server.quit()
                except:
                    server.close()

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Erro de autenticação SMTP: {e}")
        logger.info("Feedback salvo no banco, mas email não foi enviado.")
        return True

    except smtplib.SMTPException as e:
        logger.error(f"❌ Erro SMTP ao enviar feedback: {e}")
        logger.info("Feedback salvo no banco, mas email não foi enviado.")
        return True

    except Exception as e:
        logger.error(f"❌ Erro inesperado ao enviar feedback por e-mail: {e}")
        logger.info("Feedback salvo no banco, mas email não foi enviado.")
        return True


def clean_feedback_backup() -> None:
    backup_file = "feedback_backup.json"
    if not os.path.exists(backup_file):
        logger.info("Nenhum feedback de backup para limpar.")
        return

    try:
        with open(backup_file, "r", encoding="utf-8") as file:
            backups = json.load(file)

        cleaned_backups = [
            fb
            for fb in backups
            if isinstance(fb, dict) and "email" in fb and "feedback_text" in fb
        ]

        with open(backup_file, "w", encoding="utf-8") as file:
            json.dump(cleaned_backups, file, ensure_ascii=False, indent=4)

        logger.info("Arquivo de backup de feedbacks foi limpo e atualizado.")
    except Exception as e:
        logger.error(f"Erro ao limpar o arquivo de backup de feedbacks: {e}")

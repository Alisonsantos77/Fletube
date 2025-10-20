import json
import os
import re
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

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
FEEDBACK_LOGO_URL = os.getenv("FEEDBACK_LOGO_URL")

supabase: Client = (
    create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
)


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
                if supabase:
                    response = (
                        supabase.table("feedbacks").insert(feedback_data).execute()
                    )
                    if getattr(response, "data", None):
                        logger.info(
                            f"Feedback sincronizado com sucesso: {feedback_data}"
                        )
                        successfully_synced.append(feedback)
                    else:
                        logger.error(f"Erro ao sincronizar feedback")
                else:
                    logger.error("Supabase não configurado para sincronização.")
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


def _build_feedback_email_parts_mobile(user_email: str, user_message: dict):
    email = escape(user_email)
    rating = (
        int(user_message.get("rating", 0))
        if user_message.get("rating") is not None
        else 0
    )
    category = escape(str(user_message.get("category", "")))
    subcategory = escape(str(user_message.get("subcategory", "")))
    feedback_text_raw = str(user_message.get("feedback_text", "") or "")
    feedback_text_escaped = escape(feedback_text_raw).replace("\n", "<br>")
    created_at = (
        datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    )
    stars = "⭐" * rating if rating > 0 else "Sem avaliação"
    plain = (
        f"Feedback - Fletube\n\n"
        f"Email do usuário: {user_email}\n"
        f"Avaliação: {rating} estrela(s)\n"
        f"Categoria: {user_message.get('category', '')}\n"
        f"Subcategoria: {user_message.get('subcategory', '')}\n\n"
        f"Feedback:\n{feedback_text_raw}\n\n"
        f"Enviado em: {created_at}\n"
    )
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
      :root {{ color-scheme: light; }}
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; background:#f6f7fb; margin:0; padding:12px; }}
      .card {{ max-width:600px; margin:12px auto; background:#ffffff; border-radius:10px; padding:16px; box-shadow:0 6px 20px rgba(2,6,23,0.08); }}
      .logo {{ display:block; margin:0 auto 12px auto; width:84px; height:auto; }}
      h1 {{ font-size:18px; margin:6px 0 2px; text-align:center; }}
      .meta {{ text-align:center; color:#6b7280; font-size:13px; margin-bottom:12px; }}
      .item {{ display:flex; flex-direction:column; gap:6px; padding:10px 0; border-top:1px solid #f0f2f7; }}
      .label {{ font-weight:600; font-size:13px; color:#111827; }}
      .value {{ font-size:15px; color:#0f1724; word-break:break-word; }}
      .feedback-box {{ margin-top:10px; background:#fbfdff; padding:12px; border-radius:8px; border:1px solid #eef2ff; }}
      .footer {{ margin-top:14px; text-align:center; color:#9aa4b2; font-size:12px; }}
      .btn {{ display:inline-block; margin-top:10px; padding:10px 14px; background:#2563eb; color:#fff; text-decoration:none; border-radius:8px; font-weight:600; }}
      @media (min-width:480px) {{
        .card {{ padding:22px; }}
        h1 {{ font-size:20px; }}
      }}
    </style>
  </head>
  <body>
    <div class="card">
      <img class="logo" src="{FEEDBACK_LOGO_URL}" alt="Fletube logo">
      <h1>Novo feedback recebido</h1>
      <div class="meta">Resumo do feedback enviado pelo usuário</div>
      <div class="item">
        <div class="label">Email</div>
        <div class="value">{email}</div>
      </div>
      <div class="item">
        <div class="label">Avaliação</div>
        <div class="value">{stars} ({rating})</div>
      </div>
      <div class="item">
        <div class="label">Categoria</div>
        <div class="value">{category}</div>
      </div>
      <div class="item">
        <div class="label">Subcategoria</div>
        <div class="value">{subcategory}</div>
      </div>
      <div class="item">
        <div class="label">Enviado em</div>
        <div class="value">{created_at}</div>
      </div>
      <div class="feedback-box">
        <div class="label">Feedback do usuário</div>
        <div style="margin-top:8px; line-height:1.5; color:#111827;">
          {feedback_text_escaped if feedback_text_escaped else "<em>Sem comentário adicional</em>"}
        </div>
      </div>
      <div style="text-align:center;">
        <a class="btn" href="mailto:{FEEDBACK_RECIPIENT_EMAIL}?subject=Re:%20Feedback%20Fletube">Responder ao usuário</a>
      </div>
      <div class="footer">Fletube • Obrigado por revisar o feedback.</div>
    </div>
  </body>
</html>"""
    return plain, html


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
        if supabase:
            response = supabase.table("feedbacks").insert(feedback_data).execute()
            if not getattr(response, "data", None):
                logger.error(f"Erro ao armazenar feedback no Supabase")
                save_feedback_locally(feedback_data)
                return False
            logger.info("Feedback armazenado no Supabase com sucesso.")
        else:
            logger.error("Supabase não configurado. Salvando localmente.")
            save_feedback_locally(feedback_data)
            return False
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
        plain_body, html_body = _build_feedback_email_parts_mobile(
            user_email, user_message
        )
        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        server = None
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
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

import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import flet as ft

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_feedback_email(user_email, user_message, page: ft.Page):
    """
    Envia um e-mail de feedback utilizando smtplib.

    Args:
        user_email (str): Endereço de e-mail do usuário que está enviando o feedback.
        user_message (str): Mensagem de feedback do usuário.
    """
    try:
        # Identifica o provedor de e-mail usando regex
        if re.search(r"@gmail\.com$", user_email, re.IGNORECASE):
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = (os.getenv("SMTP_PORT"))
            smtp_username = os.getenv("EMAIL_USER")
            smtp_password = os.getenv("EMAIL_PASSWORD")

        else:
            logger.error("Provedor de e-mail não suportado.")
            snack_bar = ft.SnacBar("Provedor de e-mail não suportado.")
            page.overlay.append(snack_bar)
            snack_bar.open = True
            return False
        # Configura a mensagem
        msg = MIMEMultipart()
        msg["From"] = smtp_username
        msg["To"] = "Alisondev77@hotmail.com"  # Meu email que receberá o feedback
        msg["Subject"] = "Feedback - Fletube"
        msg.attach(MIMEText(user_message, "plain"))

        # Conecta ao servidor SMTP e envia o e-mail
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, msg["To"], msg.as_string())
        server.quit()

        logger.info("E-mail enviado com sucesso.")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar o e-mail: {e}")
        return False

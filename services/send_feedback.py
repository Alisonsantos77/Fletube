# send_feedback.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import requests
import flet as ft

# Configure logging
logging.basicConfig(
    filename="logs/app.log",
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("flet_core").setLevel(logging.INFO)

# Load environment variables (if needed)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FEEDBACK_RECIPIENT_EMAIL = os.getenv(
    "FEEDBACK_RECIPIENT_EMAIL", "your_email@example.com"
)
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_feedback_email(user_email, user_message, page: ft.Page):
    """
    Sends a feedback email using smtplib and stores the data in Supabase.

    Args:
        user_email (str): User's email address who is sending the feedback.
        user_message (dict): Dictionary containing feedback data.
        page (ft.Page): Flet page instance to display notifications.

    Returns:
        bool: True if the email was sent and data stored successfully, False otherwise.
    """
    try:
        # Insert feedback into Supabase
        supabase_endpoint = f"{SUPABASE_URL}/rest/v1/feedbacks"
        headers_supabase = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",  # To return the inserted data
        }

        feedback_data = {
            "email": user_email,
            "rating": user_message.get("rating", 0),
            "category": user_message.get("category", ""),
            "subcategory": user_message.get("subcategory", ""),
            "feedback_text": user_message.get("feedback_text", ""),
        }

        res_supabase = requests.post(
            supabase_endpoint, headers=headers_supabase, json=feedback_data
        )

        if res_supabase.status_code in [200, 201]:
            logging.info("Feedback stored in Supabase successfully.")
        else:
            logging.error(
                f"Error storing feedback in Supabase: {res_supabase.status_code}, {res_supabase.text}"
            )
            return False

        # Create the email message
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_USER
        msg["To"] = FEEDBACK_RECIPIENT_EMAIL
        msg["Subject"] = "Feedback - Fletube"

        # HTML email template
        html_body = f"""
        <html>
            <body>
                <h2>Feedback - Fletube</h2>
                <p><strong>User Email:</strong> {user_email}</p>
                <p><strong>Rating:</strong> {user_message.get('rating', 0)} stars</p>
                <p><strong>Category:</strong> {user_message.get('category', '')}</p>
                <p><strong>Subcategory:</strong> {user_message.get('subcategory', '')}</p>
                <p><strong>Feedback:</strong><br>{user_message.get('feedback_text', '').replace('\n', '<br>')}</p>
            </body>
        </html>
        """

        # Attach the HTML body
        msg.attach(MIMEText(html_body, "html"))

        # Send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, FEEDBACK_RECIPIENT_EMAIL, msg.as_string())

        logging.info("Feedback email sent successfully.")
        return True

    except Exception as e:
        logging.error(f"Error sending feedback email: {e}")
        return False

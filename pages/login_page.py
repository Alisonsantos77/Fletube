import os
import logging
import flet as ft
from flet.auth.providers import GitHubOAuthProvider, GoogleOAuthProvider
from flet.security import encrypt, decrypt

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET = os.getenv("SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")


def LoginPage(page: ft.Page):

    github_provider = GitHubOAuthProvider(
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        redirect_url=REDIRECT_URL,
    )

    google_provider = GoogleOAuthProvider(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_url=REDIRECT_URL,
    )

    # Função para tentar login automático
    def attempt_auto_login(provider_name):
        if provider_name == "github":
            provider = github_provider
            token_key = "github_token"
            user_name_key = "github_user_name"
        elif provider_name == "google":
            provider = google_provider
            token_key = "google_token"
            user_name_key = "google_user_name"
        else:
            logging.error(f"Provedor desconhecido: {provider_name}")
            return

        encrypted_token = page.client_storage.get(token_key)
        if encrypted_token:
            try:
                saved_token = decrypt(encrypted_token, SECRET)
                account_name = (
                    page.client_storage.get(user_name_key)
                    or f"{provider_name.title()} User"
                )
                page.session.set("provider", provider_name)
                # login com o token salvo
                page.login(provider=provider, saved_token=saved_token)
                logging.info(
                    f"Tentativa de auto-login com {provider_name} para {account_name}"
                )
            except Exception as e:
                logging.error(
                    f"Erro ao descriptografar o token do {provider_name.title()}: {e}"
                )
                # Remove tokens inválidos
                page.client_storage.remove(token_key)
                page.client_storage.remove(user_name_key)
        else:
            logging.info(f"Nenhum token {provider_name.title()} encontrado.")

    # Chama a função para tentar auto-login com GitHub e Google
    attempt_auto_login("github")
    attempt_auto_login("google")

    def on_login(e: ft.LoginEvent):
        if not e.error:
            token = page.auth.token.to_json()
            provider_name = page.session.get("provider")
            account_name = page.auth.user.get("name", f"{provider_name.title()} User")
            logging.info(f"Login bem-sucedido com {provider_name} para {account_name}")

            encrypted_token = encrypt(token, SECRET)
            if provider_name == "github":
                page.client_storage.set("github_token", encrypted_token)
                page.client_storage.set("github_user_name", account_name)
            elif provider_name == "google":
                page.client_storage.set("google_token", encrypted_token)
                page.client_storage.set("google_user_name", account_name)
            else:
                logging.error(f"Provedor desconhecido durante o login: {provider_name}")

            page.go("/downloads")  # Redireciona após login bem-sucedido
        else:
            logging.error(f"Erro no login: {e.error_description}")
            provider_name = page.session.get("provider")
            if provider_name == "github":
                page.client_storage.remove("github_token")
                page.client_storage.remove("github_user_name")
            elif provider_name == "google":
                page.client_storage.remove("google_token")
                page.client_storage.remove("google_user_name")

            page.snack_bar = ft.SnackBar(
                ft.Text("Erro ao fazer login. Por favor, tente novamente."),
                bgcolor=ft.colors.RED_ACCENT_200,
            )
            page.snack_bar.open = True
            page.update()

    page.on_login = on_login

    def login_with_google(e):
        page.session.set("provider", "google")
        page.login(provider=google_provider)

    def login_with_github(e):
        page.session.set("provider", "github")
        page.login(provider=github_provider)

    app_logo = ft.Image(
        src="/images/logo.png",
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN,
    )

    login_title = ft.Text(
        value="Bem-vindo ao Fletube!",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.BLUE_GREY_800,
        text_align=ft.TextAlign.CENTER,
    )

    login_description = ft.Text(
        value="Entre para acessar seus downloads e histórico!",
        size=16,
        color=ft.colors.BLUE_GREY_600,
        text_align=ft.TextAlign.CENTER,
    )

    google_button = ft.ElevatedButton(
        text="Continuar com Google",
        content=ft.Row(
            controls=[
                ft.Image(src="/images/contact/google-logo.png", width=20, height=20),
                ft.Text("Continuar com Google", size=16, color=ft.colors.BLACK),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.colors.WHITE,
                ft.ControlState.HOVERED: ft.colors.WHITE,
            },
            color={ft.ControlState.DEFAULT: ft.colors.BLACK},
            elevation={"pressed": 0, "": 1},
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=login_with_google,
        width=280,
    )

    github_button = ft.ElevatedButton(
        text="Continuar com GitHub",
        content=ft.Row(
            controls=[
                ft.Image(
                    src="/images/contact/icons8-github-64.png", width=20, height=20
                ),
                ft.Text("Continuar com GitHub", size=16, color=ft.colors.BLACK),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.colors.WHITE,
                ft.ControlState.HOVERED: ft.colors.WHITE,
            },
            color={ft.ControlState.DEFAULT: ft.colors.BLACK},
            elevation={"pressed": 0, "": 1},
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=login_with_github,
        width=280,
    )

    login_content = ft.SafeArea(
        content=ft.Column(
            controls=[
                app_logo,
                login_title,
                login_description,
                google_button,
                github_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        expand=True,
        top=True,
        bottom=True,
        left=True,
        right=True,
    )

    return login_content

from datetime import datetime, timezone

import flet as ft
from loguru import logger

from services.supabase_utils import update_user_last_login, validate_user


def LoginPage(page: ft.Page):
    page.title = "Fletube - Login"

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
        color=ft.Colors.BLUE_GREY_800,
        text_align=ft.TextAlign.CENTER,
    )

    login_description = ft.Text(
        value="Entre para acessar seus downloads e histórico!",
        size=16,
        color=ft.Colors.BLUE_GREY_600,
        text_align=ft.TextAlign.CENTER,
    )

    input_username = ft.TextField(
        label="Nome de usuário",
        hint_text="Digite seu nome de usuário",
        border_color=ft.Colors.BLUE_GREY_300,
        border_radius=8,
        border_width=1,
        width=280,
    )

    input_senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.BLUE_GREY_300,
        border_radius=8,
        border_width=1,
        width=280,
    )

    def on_login_click(e):
        username = input_username.value
        password = input_senha.value

        status, user = validate_user(username, password)

        if status == "success":
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Login efetuado com sucesso!"),
                bgcolor=ft.Colors.GREEN_400,
            )
            page.snack_bar.open = True
            page.update()
            logger.info(f"Usuário encontrado: {user['username']}")

            last_login = datetime.now(timezone.utc).isoformat()
            update_user_last_login(user["id"], last_login)

            page.client_storage.set("user_id", user["id"])
            page.client_storage.set("username", username)
            page.client_storage.set("ultimo_login", last_login)
            page.client_storage.set("data_expiracao", user["data_expiracao"])
            page.client_storage.set("subscription_type", user["subscription_type"])
            page.client_storage.set("user_status", user["status"])
            page.client_storage.set("telefone", user["telefone"])
            page.client_storage.set("email", user["email"])
            page.client_storage.set("autenticado", True)

            user_info_list = [
                user["id"],
                username,
                last_login,
                user["data_expiracao"],
                user["subscription_type"],
                user["telefone"],
                user["email"],
            ]

            page.client_storage.set("user_info", user_info_list)
            logger.info(f"Dados coletados: {user_info_list}")
            page.go("/downloads")

        elif status == "inactive":
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Sua conta expirou. Entre em contato com o suporte."),
                bgcolor=ft.Colors.RED_400,
                action="Falar com suporte",
                on_action=lambda _: page.launch_url("https://wa.link/tr8dei"),
            )
            page.snack_bar.open = True
            page.update()
            logger.warning(f"Usuário {username} expirado.")
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Usuário ou senha inválidos."),
                bgcolor=ft.Colors.RED_400,
            )
            page.snack_bar.open = True
            page.update()
            logger.warning("Usuário ou senha inválidos.")

    login_button = ft.ElevatedButton(
        text="Entrar",
        on_click=on_login_click,
        width=200,
    )

    login_content = ft.SafeArea(
        content=ft.Column(
            controls=[
                app_logo,
                login_title,
                login_description,
                input_username,
                input_senha,
                login_button,
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

from datetime import datetime, timezone
from math import pi
import asyncio

import flet as ft
from loguru import logger

from services.supabase_utils import update_user_last_login, validate_user


def LoginPage(page: ft.Page):
    page.title = "Fletube - Login"

    app_logo = ft.Container(
        content=ft.Image(
            src="/images/logo.png",
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,
        ),
        animate_rotation=ft.Animation(1200, ft.AnimationCurve.ELASTIC_OUT),
        animate_scale=ft.Animation(2000, ft.AnimationCurve.EASE_IN_OUT),
        rotate=0,
        scale=1,
    )

    login_title = ft.Text(
        value="Bem-vindo ao Fletube!",
        size=48,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.PRIMARY,
        text_align=ft.TextAlign.CENTER,
    )

    login_subtitle = ft.Text(
        value="Baixe seus vídeos favoritos do YouTube",
        size=20,
        text_align=ft.TextAlign.CENTER,
        color=ft.Colors.ON_SURFACE_VARIANT,
    )

    input_username = ft.TextField(
        label="Nome de usuário",
        hint_text="Digite seu nome de usuário",
        border_radius=12,
        width=500,
        height=65,
        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(100, ft.AnimationCurve.BOUNCE_OUT),
        scale=1,
        offset=ft.Offset(0, 0),
        prefix_icon=ft.Icons.PERSON,
        text_size=17,
    )

    input_senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        border_radius=12,
        width=500,
        height=65,
        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate_offset=ft.Animation(100, ft.AnimationCurve.BOUNCE_OUT),
        scale=1,
        offset=ft.Offset(0, 0),
        prefix_icon=ft.Icons.LOCK,
        text_size=17,
    )

    def animate_logo():
        app_logo.rotate += pi / 4
        app_logo.scale = 1.2
        app_logo.update()

        async def reset():
            await asyncio.sleep(0.3)
            app_logo.scale = 1
            app_logo.update()

        page.run_task(reset)

    async def shake_inputs():
        input_username.offset = ft.Offset(0.02, 0)
        input_senha.offset = ft.Offset(0.02, 0)
        input_username.update()
        input_senha.update()

        await asyncio.sleep(0.05)

        input_username.offset = ft.Offset(-0.02, 0)
        input_senha.offset = ft.Offset(-0.02, 0)
        input_username.update()
        input_senha.update()

        await asyncio.sleep(0.05)

        input_username.offset = ft.Offset(0.02, 0)
        input_senha.offset = ft.Offset(0.02, 0)
        input_username.update()
        input_senha.update()

        await asyncio.sleep(0.05)

        input_username.offset = ft.Offset(0, 0)
        input_senha.offset = ft.Offset(0, 0)
        input_username.update()
        input_senha.update()

    def on_login_click(e):
        username = input_username.value
        password = input_senha.value

        if not username or not password:
            page.snack_bar = ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING, size=20),
                        ft.Text("Preencha todos os campos!"),
                    ],
                    spacing=8,
                ),
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
            return

        login_button.disabled = True
        login_button.text = "Entrando..."
        login_button.update()

        status, user = validate_user(username, password)

        if status == "success":
            animate_logo()

            page.snack_bar = ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=20),
                        ft.Text("Login efetuado com sucesso!"),
                    ],
                    spacing=8,
                ),
            )
            page.snack_bar.open = True
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

            page.update()

        elif status == "inactive":
            login_button.disabled = False
            login_button.text = "Entrar"
            login_button.update()

            page.snack_bar = ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ERROR, size=20),
                        ft.Text("Sua conta expirou. Entre em contato com o suporte."),
                    ],
                    spacing=8,
                ),
                action="Falar com suporte",
                on_action=lambda _: page.launch_url("https://wa.link/tr8dei"),
            )
            page.snack_bar.open = True
            page.update()
            logger.warning(f"Usuário {username} expirado.")
        else:
            login_button.disabled = False
            login_button.text = "Entrar"
            login_button.update()

            page.run_task(shake_inputs)

            input_username.error_text = "Credenciais inválidas"
            input_senha.error_text = "Credenciais inválidas"
            input_username.update()
            input_senha.update()

            page.snack_bar = ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ERROR, size=20),
                        ft.Text("Usuário ou senha inválidos."),
                    ],
                    spacing=8,
                ),
            )
            page.snack_bar.open = True
            page.update()
            logger.warning("Usuário ou senha inválidos.")

    login_button = ft.ElevatedButton(
        text="Entrar",
        on_click=on_login_click,
        width=500,
        height=65,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            text_style=ft.TextStyle(size=19, weight=ft.FontWeight.BOLD),
        ),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        scale=1,
    )

    def on_button_hover(e):
        if not login_button.disabled:
            login_button.scale = 1.05 if e.data == "true" else 1
            login_button.update()

    login_button.on_hover = on_button_hover

    async def start_pulse():
        while True:
            if app_logo.page:
                current = app_logo.scale
                app_logo.scale = 1.1 if current == 1 else 1
                try:
                    app_logo.update()
                except:
                    break
            await asyncio.sleep(2)

    page.run_task(start_pulse)

    login_content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Column(
                    controls=[
                        app_logo,
                        ft.Container(height=35),
                        login_title,
                        ft.Container(height=12),
                        login_subtitle,
                        ft.Container(height=60),
                        input_username,
                        ft.Container(height=25),
                        input_senha,
                        ft.Container(height=40),
                        login_button,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(
                        "© 2024 Fletube - Desenvolvido por Alison Santos",
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    padding=ft.padding.only(bottom=25),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        expand=True,
    )

    return login_content

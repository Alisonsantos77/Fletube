import time
import asyncio
import flet as ft
from services.supabase_utils import user_is_active
import logging


def handle_user_action(action, page):
    if action == "Logout":
        try:
            logging.info("Limpando clientStorage...")
            page.client_storage.clear()
            page.go("/login")
        except Exception as e:
            logging.error(f"Erro ao realizar logout: {e}")
    elif action == "Configurações":
        page.go("/configuracoes")
    elif action == "Perfil":
        pass

# Contador regressivo para exibir o tempo restante da assinatura do usuário


class CountDown(ft.Text):
    def __init__(self, segundos):
        super().__init__()
        self.segundos = segundos

    def did_mount(self):
        self.executando = True
        self.page.run_task(self.atualizar_timer)

    def will_unmount(self):
        self.executando = False

    async def atualizar_timer(self):
        while self.segundos and self.executando:
            # Cálculo de dias, horas, minutos e segundos restantes
            dias, resto_segundos = divmod(
                self.segundos, 86400)  # 86400 segundos em um dia
            horas, resto_segundos = divmod(
                resto_segundos, 3600)  # 3600 segundos em uma hora
            # 60 segundos em um minuto
            minutos, segundos = divmod(resto_segundos, 60)

            # Formatação para exibir como 'xd xh xm xs'
            self.value = f"{dias}d {horas}h {minutos}m {segundos}s"
            self.update()
            await asyncio.sleep(1)
            self.segundos -= 1


def create_user_menu(page: ft.Page):
    username = page.client_storage.get("username")
    restantes = page.client_storage.get("dias_restantes")
    assinatura = page.client_storage.get("subscription_type")

    if restantes is None:
        restantes = 0

    # Iniciais do usuário
    user_initials = username[0].upper() if username else "Fletube"

    return ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Stack(
                [
                    ft.CircleAvatar(
                        foreground_image_src="https://robohash.org/{username}.png",
                        content=ft.Text(user_initials),
                    ),
                    ft.Container(
                        content=ft.CircleAvatar(
                            bgcolor=ft.colors.GREEN, radius=5),
                        alignment=ft.alignment.bottom_left,
                    ),
                ],
                width=40,
                height=40,
            ),
            tooltip=f"Logado como {username}",
        ),
        items=[
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.PERSON_4_SHARP,
                            size=20,
                            color=ft.colors.BLUE_GREY_500,
                        ),
                        ft.Text(
                            value=f"{username}",
                            size=14,
                        ),
                    ]
                ),
                on_click=lambda e: handle_user_action("Perfil", page),
            ),
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.CALENDAR_MONTH_ROUNDED,
                            size=20,
                            color=ft.colors.BLUE_GREY_500,
                        ),
                        ft.Text(
                            value=f"{assinatura}",
                            size=14,
                        ),]
                ),
            ),
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.TIMER,
                            size=20,
                            color=ft.colors.BLUE_GREY_500,
                        ),
                        CountDown(
                            segundos=restantes * 86400) if restantes else ft.Text(value="Carregando...", size=14),
                    ]
                ),
            ),
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.SETTINGS,
                            size=20,
                            color=ft.colors.BLUE_GREY_500,
                        ),
                        ft.Text(
                            value="Configurações",
                            size=14,
                        ),
                    ]
                ),
                on_click=lambda e: handle_user_action("Configurações", page),
            ),
            ft.PopupMenuButton(),
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.LOGOUT_SHARP,
                            size=20,
                            color=ft.colors.RED,
                        ),
                        ft.Text(
                            value="Sair",
                            size=14,
                            color=ft.colors.RED,
                        ),
                    ]
                ),
                on_click=lambda e: handle_user_action("Logout", page),
            ),
        ],
    )

import asyncio
import logging
from typing import Optional

import flet as ft

from utils.logging_config import setup_logging

logger = setup_logging()


class UserMenuManager:

    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = page.session.get("app_storage")

    def get_username(self) -> str:
        username = self.page.client_storage.get("username")
        return username if username else "Usuário"

    def get_user_initials(self) -> str:
        username = self.get_username()

        if username == "Usuário":
            return "F"

        words = username.split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()

        return username[0].upper()

    def get_remaining_days(self) -> int:
        days = self.page.client_storage.get("dias_restantes")
        return days if days is not None else 0

    def get_subscription_type(self) -> str:
        subscription = self.page.client_storage.get("subscription_type")
        return subscription if subscription else "Gratuito"

    def get_avatar_url(self) -> str:
        username = self.get_username()
        return f"https://robohash.org/{username}.png"

    def get_subscription_icon(self) -> str:
        subscription = self.get_subscription_type()
        if subscription == "Premium":
            return ft.Icons.STAR
        elif subscription == "Pro":
            return ft.Icons.VERIFIED
        else:
            return ft.Icons.INFO_OUTLINED

    def get_subscription_color(self) -> str:
        subscription = self.get_subscription_type()
        if subscription == "Premium":
            return ft.Colors.ORANGE_400
        elif subscription == "Pro":
            return ft.Colors.PURPLE_400
        else:
            return ft.Colors.BLUE_400

    def logout(self):
        try:
            logger.info(f"Logout iniciado para usuário: {self.get_username()}")

            self.page.client_storage.clear()

            self.page.views.clear()

            snack_bar = ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOGOUT),
                        ft.Text("Logout realizado com sucesso!"),
                    ],
                    spacing=8,
                ),
                duration=2000,
            )
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

            import threading

            def delayed_navigation():
                try:
                    self.page.go("/login")
                except Exception as e:
                    logger.error(f"Erro na navegação pós-logout: {e}")

            timer = threading.Timer(0.3, delayed_navigation)
            timer.start()

            logger.info("Logout concluído")

        except Exception as e:
            logger.error(f"Erro ao realizar logout: {e}")

            error_snack = ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ERROR),
                        ft.Text("Erro ao realizar logout"),
                    ],
                    spacing=8,
                ),
            )
            self.page.overlay.append(error_snack)
            error_snack.open = True
            self.page.update()


class CountdownTimer(ft.Text):

    def __init__(self, total_seconds: int):
        super().__init__()
        self.total_seconds = total_seconds
        self.running = False

    def did_mount(self):
        self.running = True
        self.page.run_task(self._update_countdown)

    def will_unmount(self):
        self.running = False

    async def _update_countdown(self):
        while self.total_seconds > 0 and self.running:
            days, remaining = divmod(self.total_seconds, 86400)
            hours, remaining = divmod(remaining, 3600)
            minutes, seconds = divmod(remaining, 60)

            self.value = f"{days}d {hours}h {minutes}m {seconds}s"
            self.weight = ft.FontWeight.W_600
            self.color = ft.Colors.ORANGE_400

            try:
                self.update()
            except Exception as e:
                logger.error(f"Erro ao atualizar countdown: {e}")
                break

            await asyncio.sleep(1)
            self.total_seconds -= 1

        if self.total_seconds <= 0 and self.running:
            self.value = "Assinatura expirada"
            self.color = ft.Colors.ERROR
            try:
                self.update()
            except Exception:
                pass


def create_user_menu(page: ft.Page):

    manager = UserMenuManager(page)

    def handle_action(action: str):
        if action == "logout":
            manager.logout()
        elif action == "settings":
            page.go("/configuracoes")
        elif action == "payment":
            page.go("/pagamento")
        elif action == "profile":
            logger.info("Perfil selecionado (funcionalidade futura)")

    username = manager.get_username()
    user_initials = manager.get_user_initials()
    remaining_days = manager.get_remaining_days()
    subscription_type = manager.get_subscription_type()
    avatar_url = manager.get_avatar_url()
    sub_icon = manager.get_subscription_icon()
    sub_color = manager.get_subscription_color()

    remaining_seconds = remaining_days * 86400

    menu_items = [
        ft.PopupMenuItem(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.PERSON,
                        size=20,
                    ),
                    ft.Column(
                        [
                            ft.Text(username, size=14, weight=ft.FontWeight.W_600),
                            ft.Text(
                                "Perfil",
                                size=11,
                                italic=True,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),
            on_click=lambda e: handle_action("profile"),
        ),
        ft.Divider(height=1),
        ft.PopupMenuItem(
            content=ft.Row(
                controls=[
                    ft.Icon(sub_icon, size=20, color=sub_color),
                    ft.Column(
                        controls=[
                            ft.Text(
                                subscription_type,
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=sub_color,
                            ),
                            ft.Text(
                                "Tipo de Assinatura",
                                size=11,
                                italic=True,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),
        ),
        ft.PopupMenuItem(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TIMER, size=20, color=ft.Colors.ORANGE),
                    ft.Column(
                        controls=[
                            (
                                CountdownTimer(remaining_seconds)
                                if remaining_days > 0
                                else ft.Text(
                                    "Expirado",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.ERROR,
                                )
                            ),
                            ft.Text(
                                "Tempo Restante",
                                size=11,
                                italic=True,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),
        ),
        ft.Divider(height=1),
        ft.PopupMenuItem(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CREDIT_CARD, size=20, color=ft.Colors.GREEN),
                    ft.Text("Assinatura", size=14, weight=ft.FontWeight.W_600),
                ],
                spacing=12,
            ),
            on_click=lambda e: handle_action("payment"),
        ),
        ft.PopupMenuItem(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SETTINGS, size=20),
                    ft.Text("Configurações", size=14),
                ],
                spacing=12,
            ),
            on_click=lambda e: handle_action("settings"),
        ),
        ft.PopupMenuItem(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT, size=20, color=ft.Colors.ERROR),
                    ft.Text("Sair", size=14, color=ft.Colors.ERROR),
                ],
                spacing=12,
            ),
            on_click=lambda e: handle_action("logout"),
        ),
    ]

    avatar_stack = ft.Stack(
        controls=[
            ft.CircleAvatar(
                foreground_image_src=avatar_url,
                content=ft.Text(
                    user_initials,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                radius=20,
            ),
            ft.Container(
                content=ft.Container(
                    content=ft.Icon(sub_icon, size=10, color=ft.Colors.WHITE),
                    width=14,
                    height=14,
                    border_radius=7,
                    bgcolor=sub_color,
                    alignment=ft.alignment.center,
                ),
                alignment=ft.alignment.bottom_right,
            ),
        ],
        width=40,
        height=40,
    )

    return ft.PopupMenuButton(
        content=ft.Container(
            content=avatar_stack,
            tooltip=f"Logado como {username}",
        ),
        items=menu_items,
    )

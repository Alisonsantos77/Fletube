import logging
from typing import Optional

import flet as ft

logger = logging.getLogger(__name__)


class DrawerManager:
    NAVIGATION_ROUTES = {
        0: "/downloads",
        1: "/historico",
        2: "/pagamento",
        3: "/configuracoes",
    }

    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = page.session.get("app_storage")

        if not self.storage:
            logger.warning("app_storage não disponível, usando fallback")

    def get_current_theme_icon(self) -> str:
        if self.storage:
            theme = self.storage.get_setting("theme_mode", "LIGHT")
            return ft.Icons.DARK_MODE if theme == "DARK" else ft.Icons.LIGHT_MODE

        return ft.Icons.LIGHT_MODE

    def get_theme_label(self) -> str:
        if self.storage:
            theme = self.storage.get_setting("theme_mode", "LIGHT")
            return f"Tema ({'Escuro' if theme == 'DARK' else 'Claro'})"

        return "Tema (Claro)"

    def toggle_theme(self) -> str:
        if not self.storage:
            logger.error("Storage não disponível para alternar tema")
            return "LIGHT"

        current = self.storage.get_setting("theme_mode", "LIGHT")
        new_theme = "DARK" if current == "LIGHT" else "LIGHT"

        self.page.theme_mode = (
            ft.ThemeMode.DARK if new_theme == "DARK" else ft.ThemeMode.LIGHT
        )
        self.storage.set_setting("theme_mode", new_theme)
        self.page.client_storage.set("theme_mode", new_theme)
        self.page.update()

        logger.info(f"Tema alternado via drawer: {current} → {new_theme}")

        return new_theme

    def navigate_to(self, index: int) -> Optional[str]:
        if index == 4:
            self.toggle_theme()
            return None

        route = self.NAVIGATION_ROUTES.get(index)

        if route:
            self.page.go(route)
            logger.info(f"Navegação via drawer: {route}")
            return route

        logger.warning(f"Índice de navegação inválido: {index}")
        return None


def create_drawer(page: ft.Page):
    manager = DrawerManager(page)

    def handle_drawer_change(e):
        selected_index = e.control.selected_index
        manager.navigate_to(selected_index)

    def open_info_dialog(e):
        def close_dialog(e):
            info_dialog.open = False
            page.update()

        social_links = [
            {
                "icon": "images/contact/icons8-whatsapp-48.png",
                "tooltip": "Abrir WhatsApp",
                "url": "https://wa.link/oebrg2",
            },
            {
                "icon": "images/contact/outlook-logo.png",
                "tooltip": "Enviar Email",
                "url": "mailto:Alisondev77@hotmail.com?subject=Feedback%20-%20Fletube&body=Olá, gostaria de fornecer feedback.",
            },
            {
                "icon": "images/contact/icons8-linkedin-48.png",
                "tooltip": "Acessar LinkedIn",
                "url": "https://www.linkedin.com/in/alisonsantosdev",
            },
            {
                "icon": "images/contact/icons8-github-64.png",
                "tooltip": "Acessar GitHub",
                "url": "https://github.com/Alisonsantos77",
            },
        ]

        social_buttons = [
            ft.IconButton(
                content=ft.Image(
                    src=link["icon"],
                    width=40,
                    height=40,
                ),
                tooltip=link["tooltip"],
                url=link["url"],
                style=ft.ButtonStyle(
                    overlay_color=ft.Colors.TRANSPARENT,
                ),
            )
            for link in social_links
        ]

        info_dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Text("Fletube", size=24, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        tooltip="Fechar",
                        on_click=close_dialog,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Entre em contato ou acesse minhas redes sociais:", size=16
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        "Sistema de download do YouTube desenvolvido com Flet",
                        size=14,
                        italic=True,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.Row(
                    controls=social_buttons,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        page.overlay.append(info_dialog)
        info_dialog.open = True
        page.update()

    drawer_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "Fletube",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "YouTube Downloader",
                            size=12,
                            italic=True,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.Image(
                    src="/images/logo.png",
                    width=80,
                    height=80,
                    fit=ft.ImageFit.CONTAIN,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(vertical=20, horizontal=15),
    )

    navigation_items = [
        ft.NavigationDrawerDestination(
            label="Downloads",
            icon=ft.Icons.DOWNLOAD_OUTLINED,
            selected_icon=ft.Icons.DOWNLOAD,
        ),
        ft.NavigationDrawerDestination(
            label="Histórico",
            icon=ft.Icons.HISTORY_OUTLINED,
            selected_icon=ft.Icons.HISTORY,
        ),
        ft.NavigationDrawerDestination(
            label="Assinaturas",
            icon=ft.Icons.SUBSCRIPTIONS_OUTLINED,
            selected_icon=ft.Icons.SUBSCRIPTIONS,
        ),
        ft.NavigationDrawerDestination(
            label="Configurações",
            icon=ft.Icons.SETTINGS_OUTLINED,
            selected_icon=ft.Icons.SETTINGS,
        ),
        ft.NavigationDrawerDestination(
            label=manager.get_theme_label(),
            icon=manager.get_current_theme_icon(),
            selected_icon=manager.get_current_theme_icon(),
        ),
    ]

    footer = ft.Container(
        content=ft.Column(
            controls=[
                ft.Divider(height=1),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Desenvolvido por Alison Santos",
                            size=14,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.INFO_OUTLINED,
                            on_click=open_info_dialog,
                            tooltip="Informações",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Versão 1.3.0",
                            size=12,
                            italic=True,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=4,
        ),
        padding=ft.padding.all(10),
    )

    return ft.NavigationDrawer(
        controls=[
            drawer_header,
            ft.Container(expand=True),
            *navigation_items,
            footer,
        ],
        on_change=handle_drawer_change,
    )

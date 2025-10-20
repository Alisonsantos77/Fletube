import logging
from typing import Dict, List

import flet as ft

logger = logging.getLogger(__name__)


class AppearanceManager:
    AVAILABLE_FONTS = [
        "Baskervville",
        "Inter",
        "Nunito",
        "Poppins",
        "Roboto",
        "EmOne-SemiBold",
        "Gadner",
    ]

    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = page.session.get("app_storage")

        if not self.storage:
            logger.error("app_storage não encontrado na sessão!")
            raise RuntimeError("Storage não inicializado")

    def get_current_theme(self) -> str:
        return self.storage.get_setting("theme_mode", "LIGHT")

    def is_dark_mode(self) -> bool:
        return self.get_current_theme() == "DARK"

    def toggle_theme(self) -> str:
        current = self.get_current_theme()
        new_theme = "DARK" if current == "LIGHT" else "LIGHT"

        self.page.theme_mode = (
            ft.ThemeMode.DARK if new_theme == "DARK" else ft.ThemeMode.LIGHT
        )
        self.storage.set_setting("theme_mode", new_theme)
        self.page.client_storage.set("theme_mode", new_theme)
        self.page.update()

        logger.info(f"Tema alternado: {current} → {new_theme}")

        return new_theme

    def get_current_font(self) -> str:
        return self.storage.get_setting("font_family", "Padrão")

    def set_font(self, font_family: str) -> bool:
        if font_family not in self.AVAILABLE_FONTS:
            logger.warning(f"Fonte inválida: {font_family}")
            return False

        self.storage.set_setting("font_family", font_family)
        self.page.client_storage.set("font_family", font_family)

        self.page.theme = (
            ft.Theme(font_family=font_family) if font_family != "Padrão" else ft.Theme()
        )

        self.page.update()

        logger.info(f"Fonte alterada para: {font_family}")

        return True

    def get_theme_icon(self) -> str:
        return ft.Icons.DARK_MODE if self.is_dark_mode() else ft.Icons.LIGHT_MODE

    def get_theme_description(self) -> str:
        return "Modo Escuro" if self.is_dark_mode() else "Modo Claro"


def AppearanceSettings(page: ft.Page):
    try:
        manager = AppearanceManager(page)
    except RuntimeError as e:
        logger.error(f"Erro ao inicializar AppearanceSettings: {e}")
        return ft.Container(
            content=ft.Text(
                "Erro ao carregar configurações de aparência.",
            ),
            padding=20,
        )

    theme_switch_ref = ft.Ref[ft.Switch]()
    font_dropdown_ref = ft.Ref[ft.Dropdown]()
    preview_text_ref = ft.Ref[ft.Text]()

    def on_theme_toggle(e):
        new_theme = manager.toggle_theme()

        is_dark = new_theme == "DARK"
        theme_switch_ref.current.label = manager.get_theme_description()

        snack_bar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.DARK_MODE if is_dark else ft.Icons.LIGHT_MODE,
                    ),
                    ft.Text(f"{manager.get_theme_description()} ativado!"),
                ]
            ),
            duration=1500,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    def on_font_change(e):
        font = e.control.value

        if manager.set_font(font):
            preview_text_ref.current.value = f"Prévia com {font}"
            preview_text_ref.current.update()

            snack_bar = ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.FONT_DOWNLOAD),
                        ft.Text(f"Fonte alterada: {font}"),
                    ]
                ),
                duration=1500,
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

    theme_switch = ft.Switch(
        ref=theme_switch_ref,
        label=manager.get_theme_description(),
        value=manager.is_dark_mode(),
        on_change=on_theme_toggle,
    )

    theme_info = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, size=16),
                ft.Text(
                    "Alterna entre tema claro e escuro",
                    size=12,
                    italic=True,
                ),
            ],
            spacing=8,
        ),
        margin=ft.margin.only(top=8),
    )

    font_dropdown = ft.Dropdown(
        ref=font_dropdown_ref,
        label="Fonte da Aplicação",
        value=manager.get_current_font(),
        options=[ft.dropdown.Option(font) for font in manager.AVAILABLE_FONTS],
        on_change=on_font_change,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        text_size=14,
        filled=True,
    )

    font_info = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, size=16),
                ft.Text(
                    "Escolha a tipografia da interface",
                    size=12,
                    italic=True,
                ),
            ],
            spacing=8,
        ),
        margin=ft.margin.only(top=8),
    )

    preview_text = ft.Text(
        ref=preview_text_ref,
        value=f"Prévia com {manager.get_current_font()}",
        size=20,
        weight=ft.FontWeight.W_500,
    )

    preview_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.PREVIEW, size=20),
                        ft.Text(
                            "Visualização",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Divider(),
                preview_text,
                ft.Text(
                    "The quick brown fox jumps over the lazy dog",
                    size=14,
                ),
                ft.Text(
                    "0123456789 !@#$%^&*()",
                    size=14,
                ),
            ],
            spacing=12,
        ),
        padding=20,
        border_radius=12,
        border=ft.border.all(1),
    )

    theme_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(manager.get_theme_icon(), size=20),
                        ft.Text(
                            "Tema da Interface",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                theme_switch,
                theme_info,
            ],
            spacing=4,
        ),
        col={"sm": 12, "md": 6},
        padding=20,
        border_radius=12,
        border=ft.border.all(1),
    )

    font_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.FONT_DOWNLOAD_OUTLINED, size=20),
                        ft.Text(
                            "Tipografia",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                font_dropdown,
                font_info,
            ],
            spacing=4,
        ),
        col={"sm": 12, "md": 6},
        padding=20,
        border_radius=12,
        border=ft.border.all(1),
    )

    return ft.ResponsiveRow(
        controls=[
            theme_section,
            font_section,
            ft.Container(
                content=preview_card,
                col={"sm": 12},
            ),
        ],
        run_spacing=20,
        spacing=20,
    )

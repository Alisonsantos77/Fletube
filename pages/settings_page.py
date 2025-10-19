import flet as ft

from components.appearence_settings import AppearanceSettings
from components.contact_settings import ContactSettings
from components.download_settings import DownloadSettings
from components.general_settings import GeneralSettings


def SettingsPage(page: ft.Page):

    appearance_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.PALETTE_OUTLINED, size=24, color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            "Aparência",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=2, color=ft.Colors.OUTLINE),
                AppearanceSettings(page),
            ],
            spacing=16,
        ),
        padding=ft.padding.all(24),
        border_radius=16,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    download_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.DOWNLOAD_OUTLINED, size=24, color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            "Downloads",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=2, color=ft.Colors.OUTLINE),
                DownloadSettings(page),
            ],
            spacing=16,
        ),
        padding=ft.padding.all(24),
        border_radius=16,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    general_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.TUNE_OUTLINED, size=24, color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            "Geral",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=2, color=ft.Colors.OUTLINE),
                GeneralSettings(page),
            ],
            spacing=16,
        ),
        padding=ft.padding.all(24),
        border_radius=16,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    contact_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.CONTACT_SUPPORT_OUTLINED,
                            size=24,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text(
                            "Contato & Suporte",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Divider(height=2, color=ft.Colors.OUTLINE),
                ContactSettings(),
            ],
            spacing=16,
        ),
        padding=ft.padding.all(24),
        border_radius=16,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    page_header = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SETTINGS, size=32, color=ft.Colors.PRIMARY),
                ft.Text(
                    "Configurações",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE,
                ),
            ],
            spacing=16,
        ),
        padding=ft.padding.only(left=24, right=24, top=24, bottom=16),
    )

    main_content = ft.Column(
        [
            page_header,
            ft.Container(
                content=ft.Column(
                    [
                        appearance_section,
                        download_section,
                        general_section,
                        contact_section,
                    ],
                    spacing=24,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.symmetric(horizontal=24, vertical=8),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )

    return ft.SafeArea(
        content=main_content,
        expand=True,
        top=True,
        bottom=True,
        left=False,
        right=False,
    )

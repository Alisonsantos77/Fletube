import logging
from typing import Optional

import flet as ft

logger = logging.getLogger(__name__)


class GeneralSettingsManager:
    """
    Gerenciador de configurações gerais da aplicação.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = page.session.get("app_storage")

        if not self.storage:
            logger.error("app_storage não encontrado na sessão!")
            raise RuntimeError("Storage não inicializado")

    def reset_all_settings(self) -> bool:
        """
        Reseta todas as configurações para valores padrão.

        Returns:
            bool: True se resetado com sucesso
        """
        try:
            storage_info = self.storage.get_storage_info()

            logger.warning(f"Resetando configurações: {storage_info}")

            self.storage.settings.clear()

            defaults = {
                "theme_mode": "LIGHT",
                "font_family": "Padrão",
                "clipboard_monitoring": False,
                "default_format": "mp4",
                "initialized": True,
            }

            for key, value in defaults.items():
                self.storage.set_setting(key, value)

            self.page.client_storage.clear()
            self.page.client_storage.set("config_reset", True)

            logger.info("Configurações resetadas com sucesso")

            return True

        except Exception as e:
            logger.error(f"Erro ao resetar configurações: {e}")
            return False

    def get_storage_statistics(self) -> dict:
        """Retorna estatísticas do armazenamento."""
        try:
            return self.storage.get_storage_info()
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                "downloads_count": 0,
                "settings_count": 0,
                "secure_available": False,
            }

    def export_settings(self) -> Optional[dict]:
        """Exporta todas as configurações para backup."""
        try:
            return self.storage.export_all()
        except Exception as e:
            logger.error(f"Erro ao exportar configurações: {e}")
            return None


def GeneralSettings(page: ft.Page):
    """
    Interface de configurações gerais da aplicação.
    """

    try:
        manager = GeneralSettingsManager(page)
    except RuntimeError as e:
        logger.error(f"Erro ao inicializar GeneralSettings: {e}")
        return ft.Container(
            content=ft.Text("Erro ao carregar configurações gerais."), padding=20
        )

    def on_reset_click(e):
        """Callback quando botão de reset é clicado."""

        def confirm_reset(e):
            dialog.open = False
            page.update()

            if manager.reset_all_settings():
                success_snack = ft.SnackBar(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_CIRCLE),
                            ft.Text("Configurações resetadas! Reiniciando..."),
                        ]
                    ),
                    duration=2000,
                )
                page.overlay.append(success_snack)
                success_snack.open = True
                page.update()

                import time

                time.sleep(2)
                page.go("/")
            else:
                error_snack = ft.SnackBar(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR),
                            ft.Text("Erro ao resetar configurações!"),
                        ]
                    ),
                )
                page.overlay.append(error_snack)
                error_snack.open = True
                page.update()

        def cancel_reset(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER, size=24),
                    ft.Text("Confirmar Reset?"),
                ]
            ),
            content=ft.Text(
                "Esta ação irá resetar TODAS as configurações para os valores padrão. "
                "Isso inclui tema, fonte, diretório de download e preferências. "
                "O histórico de downloads será mantido.\n\n"
                "Deseja continuar?",
                size=14,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=cancel_reset,
                ),
                ft.ElevatedButton(
                    "Sim, Resetar",
                    on_click=confirm_reset,
                    icon=ft.Icons.RESTART_ALT,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def on_feedback_click(e):
        """Navega para página de feedback."""
        page.go("/feedback")

    stats = manager.get_storage_statistics()

    reset_button = ft.ElevatedButton(
        text="Resetar Configurações",
        icon=ft.Icons.RESTART_ALT,
        on_click=on_reset_click,
        style=ft.ButtonStyle(
            elevation=2,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    reset_info = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, size=16),
                ft.Text(
                    "Restaura todas as configurações para os valores padrão",
                    size=12,
                    italic=True,
                ),
            ],
            spacing=8,
        ),
        margin=ft.margin.only(top=8),
    )

    feedback_description = ft.Text(
        "Sua opinião é fundamental para melhorarmos o Fletube! "
        "Compartilhe suas ideias, reporte bugs ou simplesmente nos diga "
        "o que você achou da experiência. Todo feedback é bem-vindo!",
        size=14,
    )

    feedback_button = ft.ElevatedButton(
        text="Enviar Feedback",
        icon=ft.Icons.FEEDBACK,
        on_click=on_feedback_click,
        style=ft.ButtonStyle(
            elevation=2,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    storage_stats = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.STORAGE, size=20),
                        ft.Text(
                            "Estatísticas de Armazenamento",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.DOWNLOAD_DONE, size=18),
                        ft.Text(
                            f"{stats.get('downloads_count', 0)} downloads salvos",
                            size=14,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SETTINGS, size=18),
                        ft.Text(
                            f"{stats.get('settings_count', 0)} configurações ativas",
                            size=14,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Row(
                    [
                        ft.Icon(
                            (
                                ft.Icons.LOCK
                                if stats.get("secure_available")
                                else ft.Icons.LOCK_OPEN
                            ),
                            size=18,
                        ),
                        ft.Text(
                            f"Storage seguro: {'Ativo' if stats.get('secure_available') else 'Inativo'}",
                            size=14,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            spacing=12,
        ),
        padding=20,
        border_radius=12,
        border=ft.border.all(1),
    )

    reset_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.RESTORE, size=20),
                        ft.Text(
                            "Resetar Aplicação",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                reset_button,
                reset_info,
            ],
            spacing=4,
        ),
        col={"sm": 12, "md": 6},
        padding=20,
        border_radius=12,
        border=ft.border.all(1),
    )

    feedback_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=20),
                        ft.Text(
                            "Feedback & Sugestões",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                feedback_description,
                ft.Container(height=12),
                feedback_button,
            ],
            spacing=4,
        ),
        col={"sm": 12, "md": 6},
        padding=20,
        border_radius=12,
        border=ft.border.all(1),
    )

    return ft.Column(
        controls=[
            ft.ResponsiveRow(
                controls=[
                    reset_section,
                    feedback_section,
                ],
                run_spacing=20,
                spacing=20,
            ),
            ft.Container(height=20),
            storage_stats,
        ],
        spacing=20,
    )

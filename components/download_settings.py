from pathlib import Path
from typing import Optional

import flet as ft
from loguru import logger

from utils.file_picker_utils import setup_file_picker


class DownloadSettingsManager:
    """
    Gerenciador de configurações de download usando SecureStorage.
    Separa lógica de negócio da UI.
    """

    VALID_FORMATS = [
        ("mp4", "MP4 - Vídeo"),
        ("mkv", "MKV - Vídeo"),
        ("webm", "WEBM - Vídeo"),
        ("mp3", "MP3 - Áudio"),
        ("wav", "WAV - Áudio"),
        ("m4a", "M4A - Áudio"),
    ]

    DEFAULT_DIRECTORY_MESSAGE = "Nenhum diretório selecionado"

    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = page.session.get("app_storage")

        if not self.storage:
            logger.error("app_storage não encontrado na sessão!")
            raise RuntimeError("Storage não inicializado. Verifique main.py")

    def get_download_directory(self) -> str:
        directory = self.storage.get_setting("download_directory")

        if not directory:
            return self.DEFAULT_DIRECTORY_MESSAGE

        return directory

    def set_download_directory(self, path: str) -> bool:
        if not path or path == self.DEFAULT_DIRECTORY_MESSAGE:
            logger.warning("Tentativa de salvar diretório inválido")
            return False

        path_obj = Path(path)

        if not path_obj.exists():
            logger.warning(f"Diretório não existe: {path}")
            self._show_error("O diretório selecionado não existe!")
            return False

        if not path_obj.is_dir():
            logger.warning(f"Caminho não é um diretório: {path}")
            self._show_error("O caminho selecionado não é um diretório válido!")
            return False

        try:
            test_file = path_obj / ".fletube_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            logger.error(f"Sem permissão de escrita em {path}: {e}")
            self._show_error("Sem permissão para escrever neste diretório!")
            return False

        self.storage.set_setting("download_directory", str(path_obj))
        self.page.client_storage.set("download_directory", str(path_obj))

        logger.info(f"Diretório de download atualizado: {path}")
        self._show_success(f"Diretório configurado: {path_obj.name}")

        return True

    def get_default_format(self) -> str:
        return self.storage.get_setting("default_format", "mp4")

    def set_default_format(self, format_value: str) -> bool:
        valid_formats = [code for code, _ in self.VALID_FORMATS]

        if format_value not in valid_formats:
            logger.warning(f"Formato inválido: {format_value}")
            return False

        self.storage.set_setting("default_format", format_value)
        self.page.client_storage.set("default_format", format_value)

        logger.info(f"Formato padrão atualizado: {format_value}")
        self._show_success(f"Formato padrão: {format_value.upper()}")

        return True

    def get_clipboard_monitoring(self) -> bool:
        stored_value = self.storage.get_setting("clipboard_monitoring")

        if stored_value is None:
            default_value = True
            self.storage.set_setting("clipboard_monitoring", default_value)
            self.page.client_storage.set("clipboard_monitoring", default_value)
            logger.info("🎯 Clipboard monitoring inicializado com valor padrão: True")
            return default_value

        return stored_value

    def set_clipboard_monitoring(self, enabled: bool):
        self.storage.set_setting("clipboard_monitoring", enabled)
        self.page.client_storage.set("clipboard_monitoring", enabled)

        status = "ativado" if enabled else "desativado"
        logger.info(
            f"📋 Monitoramento de clipboard {status} (sincronizado em ambos storages)"
        )

        self._show_success(f"Monitoramento {status}!")

    def _show_success(self, message: str):
        snack_bar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.WHITE),
                    ft.Text(message, color=ft.Colors.WHITE),
                ]
            ),
            bgcolor=ft.Colors.GREEN_700,
            duration=2000,
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

    def _show_error(self, message: str):
        snack_bar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE),
                    ft.Text(message, color=ft.Colors.WHITE),
                ]
            ),
            bgcolor=ft.Colors.RED_700,
            duration=3000,
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()


def DownloadSettings(page: ft.Page):
    try:
        manager = DownloadSettingsManager(page)
    except RuntimeError as e:
        logger.error(f"Erro ao inicializar DownloadSettings: {e}")
        return ft.Container(
            content=ft.Text(
                "Erro ao carregar configurações. Reinicie o aplicativo.",
                color=ft.Colors.ERROR,
            ),
            padding=20,
        )

    directory_text_ref = ft.Ref[ft.Text]()
    download_format_dropdown_ref = ft.Ref[ft.Dropdown]()
    clipboard_switch_ref = ft.Ref[ft.Switch]()

    def on_directory_selected(directory_path: Optional[str]):
        if not directory_path:
            directory_text_ref.current.value = manager.DEFAULT_DIRECTORY_MESSAGE
            directory_text_ref.current.color = ft.Colors.ERROR
            directory_text_ref.current.update()
            return

        if manager.set_download_directory(directory_path):
            directory_text_ref.current.value = directory_path
            directory_text_ref.current.color = ft.Colors.PRIMARY
        else:
            directory_text_ref.current.value = manager.DEFAULT_DIRECTORY_MESSAGE
            directory_text_ref.current.color = ft.Colors.ERROR

        directory_text_ref.current.update()

    file_picker = setup_file_picker(page, on_directory_selected)

    def on_format_change(e):
        new_format = e.control.value
        manager.set_default_format(new_format)

    def on_clipboard_toggle(e):
        enabled = e.control.value
        manager.set_clipboard_monitoring(enabled)
        logger.info(f"🔄 Switch do clipboard alterado para: {enabled}")

    current_directory = manager.get_download_directory()
    is_directory_set = current_directory != manager.DEFAULT_DIRECTORY_MESSAGE

    select_directory_button = ft.ElevatedButton(
        text="Selecionar Diretório",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=lambda e: file_picker.get_directory_path(),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
            elevation=2,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    directory_text = ft.Text(
        value=current_directory,
        ref=directory_text_ref,
        color=ft.Colors.PRIMARY if is_directory_set else ft.Colors.ERROR,
        size=14,
        weight=ft.FontWeight.W_500,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    directory_info = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.BLUE_GREY_400),
                ft.Text(
                    "Os downloads serão salvos neste diretório",
                    size=12,
                    color=ft.Colors.BLUE_GREY_400,
                    italic=True,
                ),
            ],
            spacing=8,
        ),
        margin=ft.margin.only(top=8),
    )

    download_format_dropdown = ft.Dropdown(
        ref=download_format_dropdown_ref,
        label="Formato Padrão",
        value=manager.get_default_format(),
        options=[
            ft.dropdown.Option(code, label) for code, label in manager.VALID_FORMATS
        ],
        on_change=on_format_change,
        border_color=ft.Colors.OUTLINE_VARIANT,
        focused_border_color=ft.Colors.PRIMARY,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        text_size=14,
        filled=True,
    )

    format_info = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.BLUE_GREY_400),
                ft.Text(
                    "Este formato será pré-selecionado ao baixar",
                    size=12,
                    color=ft.Colors.BLUE_GREY_400,
                    italic=True,
                ),
            ],
            spacing=8,
        ),
        margin=ft.margin.only(top=8),
    )

    clipboard_monitor_switch = ft.Switch(
        ref=clipboard_switch_ref,
        label="Monitorar Clipboard",
        value=manager.get_clipboard_monitoring(),
        on_change=on_clipboard_toggle,
        active_color=ft.Colors.PRIMARY,
    )

    clipboard_description = ft.Text(
        "Detecta automaticamente links do YouTube copiados",
        size=12,
        color=ft.Colors.BLUE_GREY_400,
        italic=True,
    )

    directory_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.FOLDER_OUTLINED, size=20, color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            "Diretório de Downloads",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                select_directory_button,
                ft.Container(height=8),
                directory_text,
                directory_info,
            ],
            spacing=4,
        ),
        col={"sm": 12, "md": 6},
        padding=20,
        border_radius=12,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
    )

    format_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.VIDEO_FILE_OUTLINED,
                            size=20,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text(
                            "Formato de Download",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                download_format_dropdown,
                format_info,
            ],
            spacing=4,
        ),
        col={"sm": 12, "md": 6},
        padding=20,
        border_radius=12,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
    )

    clipboard_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.CONTENT_PASTE_OUTLINED,
                            size=20,
                            color=ft.Colors.PRIMARY,
                        ),
                        ft.Text(
                            "Monitoramento Automático",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                clipboard_monitor_switch,
                ft.Container(height=4),
                clipboard_description,
            ],
            spacing=4,
        ),
        col={"sm": 12, "md": 6},
        padding=20,
        border_radius=12,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
    )

    storage_info_section = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.STORAGE_OUTLINED,
                            size=20,
                            color=ft.Colors.BLUE_GREY_600,
                        ),
                        ft.Text(
                            "Informações de Armazenamento",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Container(height=8),
                ft.Text(
                    f"📁 Diretório: {current_directory if is_directory_set else 'Não configurado'}",
                    size=13,
                ),
                ft.Text(
                    f"🎬 Formato padrão: {manager.get_default_format().upper()}",
                    size=13,
                ),
                ft.Text(
                    f"📋 Monitoramento: {'Ativo' if manager.get_clipboard_monitoring() else 'Inativo'}",
                    size=13,
                ),
            ],
            spacing=8,
        ),
        col={"sm": 12, "md": 6},
        padding=20,
        border_radius=12,
    )

    return ft.ResponsiveRow(
        controls=[
            directory_section,
            format_section,
            clipboard_section,
            storage_info_section,
        ],
        run_spacing=20,
        spacing=20,
    )

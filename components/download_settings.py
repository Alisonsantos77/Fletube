import flet as ft
from utils.file_picker_utils import setup_file_picker


def DownloadSettings(page: ft.Page):
    directory_text_ref = ft.Ref[ft.Text]()
    download_format_dropdown_ref = ft.Ref[ft.Dropdown]()

    def on_directory_selected(directory_path):
        if directory_path and directory_path != "Nenhum diretório selecionado!":
            directory_text_ref.current.value = directory_path
            directory_text_ref.current.update()
            # Salvar o diretório no client storage
            page.client_storage.set("download_directory", directory_path)
        else:
            directory_text_ref.current.value = "Nenhum diretório selecionado!"
            directory_text_ref.current.update()

    file_picker = setup_file_picker(page, on_directory_selected)

    select_directory_button = ft.ElevatedButton(
        text="Selecionar Diretório",
        icon=ft.icons.FOLDER_OPEN,
        on_click=lambda e: file_picker.get_directory_path(),
    )

    # Obter o valor do diretório e definir o valor padrão se necessário
    directory_value = page.client_storage.get("download_directory")
    if directory_value is None:
        directory_value = "Nenhum diretório selecionado!"

    directory_text = ft.Text(
        value=directory_value,
        ref=directory_text_ref,
    )

    def update_default_format(format_value):
        page.client_storage.set("default_format", format_value)

    # Obter o valor do formato padrão e definir o valor padrão se necessário
    format_value = page.client_storage.get("default_format")
    if format_value is None:
        format_value = "mp4"

    download_format_dropdown = ft.Dropdown(
        ref=download_format_dropdown_ref,
        label="Formato de Download Padrão",
        options=[
            ft.dropdown.Option("mp4", "MP4"),
            ft.dropdown.Option("mp3", "MP3"),
        ],
        value=format_value,
        on_change=lambda e: update_default_format(e.control.value),
    )

    return ft.ResponsiveRow(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Diretório Padrão para Downloads",
                                weight=ft.FontWeight.BOLD,
                            ),
                            select_directory_button,
                            directory_text,
                        ],
                        spacing=5,
                    ),
                    col={"sm": 12, "md": 6},
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Formato de Download Padrão",
                                weight=ft.FontWeight.BOLD,
                            ),
                            download_format_dropdown,
                        ],
                        spacing=5,
                    ),
                    col={"sm": 12, "md": 6},
                ),
            ],
            run_spacing=10,
        )

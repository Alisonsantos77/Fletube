# partials/download_content.py

import flet as ft
import threading
import logging
import re
import asyncio
import uuid
import time
from functools import partial
import os

from services.dlp_service import start_download
from utils.session_storage_utils import (
    recuperar_downloads_bem_sucedidos_session,
    salvar_downloads_bem_sucedidos_session,
)
from utils.client_storage_utils import (
    recuperar_downloads_bem_sucedidos_client,
    salvar_downloads_bem_sucedidos_client,
    excluir_download_bem_sucedido_client,
    excluir_todos_downloads_bem_sucedidos_client,
)
from utils.file_picker_utils import setup_file_picker
from utils.extract_thumbnail import extract_thumbnail_url
from utils.extract_title import extract_title_from_url
from utils.validations import validar_input
from services.download_manager import DownloadManager

logger = logging.getLogger(__name__)


def download_content(
    page: ft.Page, sidebar: ft.Control, download_manager: DownloadManager
):

    drop_format_rf = ft.Ref[ft.Dropdown]()
    img_downloader_rf = ft.Ref[ft.Image]()
    status_text_rf = ft.Ref[ft.Text]()
    download_button_rf = ft.Ref[ft.ElevatedButton]()
    barra_progress_video_rf = ft.Ref[ft.ProgressBar]()
    input_link_rf = ft.Ref[ft.TextField]()
    dlg_modal_rf = ft.Ref[ft.AlertDialog]()

    dialog_open = {"value": False}
    last_clipboard_content = {"value": None}

    barra_de_progresso = ft.ProgressBar(
        width=350,
        height=8,
        color=ft.Colors.PRIMARY,
        bgcolor=ft.Colors.ON_SURFACE,
        ref=barra_progress_video_rf,
        visible=False,
    )

    def update_thumbnail(e):
        video_url = input_link_rf.current.value.strip()
        if not validar_input(page, video_url):
            input_link_rf.current.value = None
            input_link_rf.current.update()
            return
        try:
            status_text_rf.current.value = "Extraindo thumbnail..."
            barra_progress_video_rf.current.value = 0.5
            barra_progress_video_rf.current.visible = True
            barra_progress_video_rf.current.update()

            thumb_url = extract_thumbnail_url(video_url)
            img_downloader_rf.current.src = thumb_url
            img_downloader_rf.current.update()

            status_text_rf.current.value = "Thumbnail atualizada."
            status_text_rf.current.color = ft.Colors.PRIMARY
            status_text_rf.current.update()

            barra_progress_video_rf.current.value = 1.0
            barra_progress_video_rf.current.visible = False
            barra_progress_video_rf.current.update()

        except ValueError as ve:
            status_text_rf.current.value = str(ve)
            status_text_rf.current.color = ft.Colors.ERROR
            status_text_rf.current.update()

            barra_progress_video_rf.current.value = 1.0
            barra_progress_video_rf.current.visible = False
            barra_progress_video_rf.current.update()

            snackbar = ft.SnackBar(
                content=ft.Text(str(ve)),
                bgcolor=ft.Colors.ERROR,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

    def on_directory_selected(directory_path):
        if directory_path:
            page.client_storage.set("download_directory", directory_path)
            status_text_rf.current.value = f"Diretório selecionado: {
                directory_path}"
            status_text_rf.current.color = ft.Colors.PRIMARY
            status_text_rf.current.update()
            snackbar = ft.SnackBar(
                content=ft.Text(f"Diretório selecionado: {directory_path}"),
                bgcolor=ft.Colors.PRIMARY,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

    def iniciar_download_apos_selecionar_diretorio(diretorio):
        link = input_link_rf.current.value.strip()
        format_dropdown = drop_format_rf.current.value
        page.client_storage.set("selected_format", format_dropdown)
        if link and format_dropdown:
            status_text_rf.current.value = "Iniciando download..."
            status_text_rf.current.color = ft.Colors.PRIMARY
            status_text_rf.current.update()
            snackbar = ft.SnackBar(
                content=ft.Text("Download iniciado..."),
                bgcolor=ft.Colors.PRIMARY,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

            barra_progress_video_rf.current.value = 0.0
            barra_progress_video_rf.current.visible = True
            barra_progress_video_rf.current.update()

            download_manager.iniciar_download(
                link, format_dropdown, diretorio, sidebar, page)

        else:
            status_text_rf.current.value = (
                "Por favor, insira um link e escolha um formato."
            )
            status_text_rf.current.color = ft.Colors.ERROR
            status_text_rf.current.update()
            snackbar = ft.SnackBar(
                content=ft.Text(
                    "Por favor, insira um link e escolha um formato."),
                bgcolor=ft.Colors.ERROR,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()


    def renderizar_lista_downloads_salvos(page, sidebar):
        downloads = recuperar_downloads_bem_sucedidos_client(page)
        if downloads:
            logger.info(f"Downloads recuperados: {downloads}")
            for download in downloads:
                download_id = download.get("id")
                if not download_id:
                    logger.warning(f"Download sem ID encontrado: {download}")
                    continue
                title = download.get("title", "Título Indisponível")
                format = download.get("format", "Formato Indisponível")
                thumbnail = download.get("thumbnail", "/images/logo.png")
                file_path = download.get("file_path", "")
                logger.info(
                    f"Adicionando download: ID: {download_id}, Título: {title}, Formato: {
                        format}, Thumbnail: {thumbnail}, Caminho: {file_path}"
                )
                sidebar.add_download_item(
                    id=download_id,
                    title=title,
                    subtitle=format,
                    thumbnail_url=thumbnail,
                    file_path=file_path,
                    download_manager=download_manager
                )
        else:
            logger.warning("Nenhum download recuperado do client_storage.")
        
    async def clipboard_reminder(page, status_text_rf):
        seconds = 60
        while seconds > 0:
            if status_text_rf.current is not None:
                status_text_rf.current.value = f"Copie o link e passe o mouse na tela dentro de {
                    seconds} segundos."
                status_text_rf.current.update()
            seconds -= 1
            await asyncio.sleep(1)
        else:
            if status_text_rf.current is not None:
                status_text_rf.current.value = "Faça o download do seu vídeo aqui!"
                status_text_rf.current.update()

    def start_download_click(e):
        diretorio = page.client_storage.get("download_directory")
        if diretorio and diretorio != "Nenhum diretório selecionado!":
            iniciar_download_apos_selecionar_diretorio(diretorio)
        else:
            status_text_rf.current.value = (
                "Nenhum diretório selecionado! Por favor, selecione um diretório."
            )
            status_text_rf.current.color = ft.Colors.ERROR
            status_text_rf.current.update()
            snackbar = ft.SnackBar(
                content=ft.Text(
                    "Nenhum diretório selecionado! Por favor, selecione um diretório."
                ),
                bgcolor=ft.Colors.ERROR,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
            file_picker.get_directory_path()

    def handle_close(e):
        dialog_open["value"] = False
        dlg_modal_rf.current.open = False
        page.update()

    dlg_modal = ft.AlertDialog(
        title=ft.Text(""),
        content=ft.Text(""),
        actions=[
            ft.TextButton(""),
            ft.TextButton(""),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        ref=dlg_modal_rf,
    )
    page.overlay.append(dlg_modal)

    def check_clipboard_for_youtube_link(e):
        clipboard_monitoring = page.client_storage.get("clipboard_monitoring")
        if not clipboard_monitoring:
            return

        if dialog_open["value"]:
            return
        clipboard_content = page.get_clipboard()
        youtube_link_pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/\S+"
        current_input_value = input_link_rf.current.value

        if isinstance(clipboard_content, str) and re.match(
            youtube_link_pattern, clipboard_content
        ):
            if clipboard_content == last_clipboard_content["value"]:
                logger.info(
                    "Conteúdo do clipboard já foi processado anteriormente.")
                return

            if current_input_value:
                if clipboard_content != current_input_value:
                    dialog_open["value"] = True
                    dlg_modal_rf.current.title.value = "Epa, link novo à vista!✨"
                    dlg_modal_rf.current.content.value = (
                        "Vai querer atualizar com esse aí?"
                    )
                    dlg_modal_rf.current.actions = [
                        ft.TextButton(
                            "Sim", on_click=lambda e: substituir_link(clipboard_content)
                        ),
                        ft.TextButton("Não", on_click=handle_close),
                    ]
                    dlg_modal_rf.current.open = True
                    page.update()
                else:
                    logger.info(
                        "O novo link é igual ao atual. Nenhuma ação necessária."
                    )
            else:
                input_link_rf.current.value = clipboard_content
                input_link_rf.current.update()
                update_thumbnail(None)

            last_clipboard_content["value"] = clipboard_content

    def substituir_link(new_link):
        dialog_open["value"] = False
        input_link_rf.current.value = new_link
        input_link_rf.current.update()
        update_thumbnail(None)
        dlg_modal_rf.current.open = False
        page.update()
        last_clipboard_content["value"] = new_link

    file_picker = setup_file_picker(page, on_directory_selected)

    img_downloader = ft.Image(
        src="/images/logo.png",
        ref=img_downloader_rf,
        width=400,
        height=400,
        visible=True,
        fit=ft.ImageFit.CONTAIN,
    )

    input_link = ft.TextField(
        label="Digite o link do vídeo",
        width=400,
        focused_border_color=ft.Colors.PRIMARY,
        focused_bgcolor=ft.Colors.SECONDARY,
        cursor_color=ft.Colors.ON_SURFACE,
        content_padding=ft.padding.all(10),
        hint_text="Cole o link do YouTube aqui...",
        prefix_icon=ft.Icons.LINK,
        on_change=update_thumbnail,
        on_focus=check_clipboard_for_youtube_link,
        ref=input_link_rf,
    )

    format_value = (
        page.client_storage.get("selected_format")
        or page.client_storage.get("default_format")
        or "mp3"
    )

    format_dropdown = ft.Dropdown(
        ref=drop_format_rf,
        label="Escolha o formato",
        value=format_value,
        options=[
            ft.dropdown.Option("mp4", "MP4"),
            ft.dropdown.Option("mkv", "MKV"),
            ft.dropdown.Option("webm", "WEBM"),
            ft.dropdown.Option("mp3", "MP3"),
            ft.dropdown.Option("wav", "WAV"),
            ft.dropdown.Option("m4a", "M4A"),
        ],
        disabled=False,
    )

    download_button = ft.ElevatedButton(
        text="Iniciar Download",
        icon=ft.Icons.DOWNLOAD,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.PRIMARY,
                ft.ControlState.HOVERED: ft.Colors.ON_PRIMARY_CONTAINER,
            },
            color={
                ft.ControlState.DEFAULT: ft.Colors.ON_PRIMARY,
                ft.ControlState.HOVERED: ft.Colors.ON_SECONDARY,
            },
            elevation={"pressed": 0, "": 1},
            animation_duration=500,
            shape=ft.RoundedRectangleBorder(radius=6),
        ),
        on_click=start_download_click,
        ref=download_button_rf,
    )

    status_text = ft.Text(
        value="Faça o download do seu vídeo aqui!",
        color=ft.Colors.PRIMARY,
        size=18,
        ref=status_text_rf,
        weight=ft.FontWeight.BOLD,
    )

    container = ft.Container(
        on_hover=check_clipboard_for_youtube_link,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.ResponsiveRow(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            img_downloader,
                            padding=5,
                            col={"sm": 12, "md": 12, "xl": 12},
                        ),
                        ft.Container(
                            status_text,
                            padding=5,
                            col={"sm": 10, "md": 10, "xl": 10},
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            barra_de_progresso,
                            padding=5,
                            col={"sm": 10, "md": 10, "xl": 10},
                        ),
                        ft.Container(
                            input_link,
                            padding=5,
                            col={"sm": 10, "md": 6, "xl": 6},
                        ),
                        ft.Container(
                            format_dropdown,
                            padding=5,
                            col={"sm": 10, "md": 6, "xl": 4},
                        ),
                        ft.Container(
                            download_button,
                            padding=5,
                            col={"sm": 10, "md": 10, "xl": 10},
                        ),
                    ],
                )
            ],
        ),
    )

    def on_layout(e):
        renderizar_lista_downloads_salvos(page, sidebar)
        start_clipboard_task()

    def start_clipboard_task():
        clipboard_monitoring = page.client_storage.get("clipboard_monitoring")
        if clipboard_monitoring:
            page.run_async_task(
                partial(clipboard_reminder, page, status_text_rf)
            )

    container.on_layout = on_layout

    return container

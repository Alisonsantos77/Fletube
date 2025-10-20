import asyncio
import re
import threading
import uuid
from functools import partial

import flet as ft
import yt_dlp
from loguru import logger

from services.dlp_service import start_download
from services.download_manager import DownloadManager
from utils.file_picker_utils import setup_file_picker
from utils.ui_helpers import show_error_snackbar, show_snackbar
from utils.validations import UIValidator
from utils.video_info_extractor import VideoInfoExtractor


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
    dlg_playlist_rf = ft.Ref[ft.AlertDialog]()
    thumbnail_container_rf = ft.Ref[ft.Container]()

    dialog_open = {"value": False}
    last_clipboard_content = {"value": None}
    pending_download = {
        "link": None,
        "format": None,
        "directory": None,
        "is_playlist": False,
        "video_count": 0,
    }

    barra_de_progresso = ft.ProgressBar(
        width=720,
        height=3,
        color=ft.Colors.PRIMARY,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
        ref=barra_progress_video_rf,
        visible=False,
    )

    def update_download_progress(progress: float, status: str = "downloading"):
        if not barra_progress_video_rf.current:
            return

        try:
            if status == "downloading":
                barra_progress_video_rf.current.value = progress
                barra_progress_video_rf.current.visible = True
                barra_progress_video_rf.current.color = ft.Colors.PRIMARY
                status_text_rf.current.value = f"Baixando... {progress*100:.1f}%"
                status_text_rf.current.color = ft.Colors.PRIMARY

            elif status == "converting":
                barra_progress_video_rf.current.value = None
                barra_progress_video_rf.current.visible = True
                barra_progress_video_rf.current.color = ft.Colors.ORANGE
                status_text_rf.current.value = "Convertendo áudio/vídeo..."
                status_text_rf.current.color = ft.Colors.ORANGE

            elif status == "finished":
                barra_progress_video_rf.current.value = 1.0
                barra_progress_video_rf.current.visible = True
                barra_progress_video_rf.current.color = ft.Colors.GREEN
                status_text_rf.current.value = "✅ Download concluído!"
                status_text_rf.current.color = ft.Colors.GREEN

                async def hide_bar():
                    await asyncio.sleep(3)
                    if barra_progress_video_rf.current:
                        barra_progress_video_rf.current.visible = False
                        barra_progress_video_rf.current.update()
                        status_text_rf.current.value = "Pronto para novo download"
                        status_text_rf.current.color = ft.Colors.ON_SURFACE_VARIANT
                        status_text_rf.current.update()

                page.run_task(hide_bar)

            elif status == "error":
                barra_progress_video_rf.current.value = 1.0
                barra_progress_video_rf.current.visible = True
                barra_progress_video_rf.current.color = ft.Colors.ERROR
                status_text_rf.current.value = "❌ Erro no download"
                status_text_rf.current.color = ft.Colors.ERROR

            barra_progress_video_rf.current.update()
            status_text_rf.current.update()

        except Exception as e:
            logger.error(f"Erro ao atualizar progress bar: {e}")

    def check_if_playlist(url: str) -> tuple[bool, int]:
        try:
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "skip_download": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info and "entries" in info:
                    entries = list(info.get("entries", []))
                    entries_count = len(entries)

                    if entries_count > 1:
                        logger.info(f"📋 Playlist detectada: {entries_count} vídeos")
                        return True, entries_count

        except Exception as e:
            logger.error(f"Erro ao verificar playlist: {e}")

        return False, 1

    async def update_thumbnail_animated(video_url: str):
        try:
            status_text_rf.current.value = "Extraindo informações..."
            status_text_rf.current.color = ft.Colors.PRIMARY
            barra_progress_video_rf.current.value = None
            barra_progress_video_rf.current.visible = True
            status_text_rf.current.update()
            barra_progress_video_rf.current.update()

            thumb_url = VideoInfoExtractor.extract_thumbnail(video_url)

            thumbnail_container_rf.current.scale = 0.95
            thumbnail_container_rf.current.opacity = 0.3
            thumbnail_container_rf.current.update()

            await asyncio.sleep(0.25)

            img_downloader_rf.current.src = thumb_url
            img_downloader_rf.current.update()

            await asyncio.sleep(0.05)

            thumbnail_container_rf.current.scale = 1.0
            thumbnail_container_rf.current.opacity = 1.0
            thumbnail_container_rf.current.update()

            status_text_rf.current.value = "Pronto para download"
            status_text_rf.current.color = ft.Colors.GREEN
            status_text_rf.current.update()

            barra_progress_video_rf.current.value = 1.0
            barra_progress_video_rf.current.visible = False
            barra_progress_video_rf.current.update()

        except ValueError as ve:
            thumbnail_container_rf.current.scale = 1.0
            thumbnail_container_rf.current.opacity = 1.0
            thumbnail_container_rf.current.update()

            status_text_rf.current.value = str(ve)
            status_text_rf.current.color = ft.Colors.ERROR
            status_text_rf.current.update()

            barra_progress_video_rf.current.value = 1.0
            barra_progress_video_rf.current.visible = False
            barra_progress_video_rf.current.update()

            show_error_snackbar(page, str(ve))

    def update_thumbnail(e):
        video_url = input_link_rf.current.value.strip()
        if not UIValidator.validate_input(page, video_url):
            input_link_rf.current.value = None
            input_link_rf.current.update()
            return

        page.run_task(update_thumbnail_animated, video_url)

    def on_directory_selected(directory_path):
        if directory_path:
            storage = page.session.get("app_storage")
            if storage:
                storage.set_setting("download_directory", directory_path)

            status_text_rf.current.value = f"Diretório: {directory_path}"
            status_text_rf.current.color = ft.Colors.PRIMARY
            status_text_rf.current.update()
            show_snackbar(page, f"Diretório selecionado: {directory_path}")

    def iniciar_download_apos_selecionar_diretorio(diretorio):
        link = input_link_rf.current.value.strip()
        format_dropdown = drop_format_rf.current.value

        if link and format_dropdown:
            is_playlist, video_count = check_if_playlist(link)

            if is_playlist:
                pending_download["link"] = link
                pending_download["format"] = format_dropdown
                pending_download["directory"] = diretorio
                pending_download["is_playlist"] = True
                pending_download["video_count"] = video_count

                dialog_open["value"] = True
                dlg_playlist_rf.current.title.value = "🎵 Playlist Detectada"
                dlg_playlist_rf.current.content.value = (
                    f"Esta URL contém uma playlist com {video_count} vídeos.\n\n"
                    "Deseja baixar toda a playlist ou apenas o vídeo atual?"
                )
                dlg_playlist_rf.current.open = True
                page.update()
            else:
                executar_download(link, format_dropdown, diretorio, False)
        else:
            status_text_rf.current.value = "Insira um link e escolha um formato"
            status_text_rf.current.color = ft.Colors.ERROR
            status_text_rf.current.update()
            show_error_snackbar(page, "Por favor, insira um link e escolha um formato.")

    def executar_download(link, formato, diretorio, is_playlist):
        status_text_rf.current.value = "Iniciando download..."
        status_text_rf.current.color = ft.Colors.PRIMARY
        status_text_rf.current.update()
        show_snackbar(page, "Download iniciado...")

        barra_progress_video_rf.current.value = 0.0
        barra_progress_video_rf.current.visible = True
        barra_progress_video_rf.current.update()

        download_manager.iniciar_download(
            link=link,
            formato=formato,
            diretorio=diretorio,
            sidebar=sidebar,
            page=page,
            is_playlist=is_playlist,
            progress_callback=update_download_progress,
        )

    def handle_playlist_response(download_playlist: bool):
        dialog_open["value"] = False
        dlg_playlist_rf.current.open = False
        page.update()

        if pending_download["link"]:
            executar_download(
                pending_download["link"],
                pending_download["format"],
                pending_download["directory"],
                download_playlist,
            )
            pending_download["link"] = None
            pending_download["format"] = None
            pending_download["directory"] = None
            pending_download["is_playlist"] = False
            pending_download["video_count"] = 0

    def renderizar_lista_downloads_salvos(page, sidebar):
        storage = page.session.get("app_storage")
        if storage:
            downloads = storage.list_downloads()
            if downloads:
                logger.info(f"Downloads recuperados: {len(downloads)}")
                for download in downloads:
                    download_id = download.get("id")
                    if not download_id:
                        logger.warning(f"Download sem ID encontrado: {download}")
                        continue
                    title = download.get("title", "Título Indisponível")
                    format = download.get("format", "Formato Indisponível")
                    thumbnail = download.get("thumbnail", "/images/thumb_broken.jpg")
                    file_path = download.get("file_path", "")
                    logger.info(
                        f"Adicionando download: ID: {download_id}, Título: {title}, Formato: {format}, Thumbnail: {thumbnail}, Caminho: {file_path}"
                    )
                    sidebar.add_download_item(
                        id=download_id,
                        title=title,
                        subtitle=format,
                        thumbnail_url=thumbnail,
                        file_path=file_path,
                        download_manager=download_manager,
                    )
            else:
                logger.warning("Nenhum download recuperado do storage.")

    async def clipboard_reminder(page, status_text_rf):
        seconds = 60
        while seconds > 0:
            if status_text_rf.current is not None:
                status_text_rf.current.value = f"Cole um link ({seconds}s)"
                status_text_rf.current.update()
            seconds -= 1
            await asyncio.sleep(1)
        else:
            if status_text_rf.current is not None:
                status_text_rf.current.value = "Cole um link do YouTube"
                status_text_rf.current.update()

    def start_download_click(e):
        storage = page.session.get("app_storage")
        diretorio = None
        if storage:
            diretorio = storage.get_setting("download_directory")

        if diretorio and diretorio != "Nenhum diretório selecionado!":
            iniciar_download_apos_selecionar_diretorio(diretorio)
        else:
            status_text_rf.current.value = "Selecione um diretório primeiro"
            status_text_rf.current.color = ft.Colors.ERROR
            status_text_rf.current.update()
            show_error_snackbar(
                page,
                "Nenhum diretório selecionado! Por favor, selecione um diretório.",
            )
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

    dlg_playlist = ft.AlertDialog(
        title=ft.Text(""),
        content=ft.Text(""),
        actions=[
            ft.TextButton(
                "Baixar Playlist Completa",
                on_click=lambda e: handle_playlist_response(True),
            ),
            ft.TextButton(
                "Apenas Este Vídeo", on_click=lambda e: handle_playlist_response(False)
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        ref=dlg_playlist_rf,
        modal=True,
    )
    page.overlay.append(dlg_playlist)

    def check_clipboard_for_youtube_link(e):
        storage = page.session.get("app_storage")
        clipboard_monitoring = False
        if storage:
            clipboard_monitoring = storage.get_setting("clipboard_monitoring", True)

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
                logger.info("Conteúdo do clipboard já foi processado anteriormente.")
                return

            if current_input_value:
                if clipboard_content != current_input_value:
                    dialog_open["value"] = True
                    dlg_modal_rf.current.title.value = "Novo link detectado"
                    dlg_modal_rf.current.content.value = (
                        "Deseja atualizar com o link copiado?"
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
        src="/images/thumb_broken.jpg",
        ref=img_downloader_rf,
        width=770,
        height=433,
        visible=True,
        fit=ft.ImageFit.COVER,
        border_radius=ft.border_radius.only(top_left=12, top_right=12),
    )

    thumbnail_container = ft.Container(
        content=img_downloader,
        width=770,
        height=433,
        padding=0,
        animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        opacity=1,
        scale=1,
        ref=thumbnail_container_rf,
    )

    status_text = ft.Text(
        value="Cole um link do YouTube",
        color=ft.Colors.ON_SURFACE_VARIANT,
        size=14,
        ref=status_text_rf,
        weight=ft.FontWeight.W_400,
        text_align=ft.TextAlign.CENTER,
    )

    input_link = ft.TextField(
        label="Link do vídeo",
        width=720,
        focused_border_color=ft.Colors.PRIMARY,
        border_color=ft.Colors.OUTLINE_VARIANT,
        cursor_color=ft.Colors.PRIMARY,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        hint_text="Cole o link aqui",
        prefix_icon=ft.Icons.LINK_ROUNDED,
        on_change=update_thumbnail,
        on_focus=check_clipboard_for_youtube_link,
        ref=input_link_rf,
        text_size=14,
        border_radius=8,
        filled=True,
    )

    storage = page.session.get("app_storage")
    format_value = "mp3"
    if storage:
        format_value = storage.get_setting("default_format", "mp3")

    format_dropdown = ft.Dropdown(
        ref=drop_format_rf,
        label="Formato",
        value=format_value,
        options=[
            ft.dropdown.Option("mp4", "MP4 - Vídeo"),
            ft.dropdown.Option("mkv", "MKV - Vídeo"),
            ft.dropdown.Option("webm", "WEBM - Vídeo"),
            ft.dropdown.Option("mp3", "MP3 - Áudio"),
            ft.dropdown.Option("wav", "WAV - Áudio"),
            ft.dropdown.Option("m4a", "M4A - Áudio"),
        ],
        disabled=False,
        width=345,
        border_color=ft.Colors.OUTLINE_VARIANT,
        focused_border_color=ft.Colors.PRIMARY,
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        text_size=14,
        filled=True,
    )

    download_button = ft.ElevatedButton(
        text="Iniciar Download",
        icon=ft.Icons.DOWNLOAD_ROUNDED,
        style=ft.ButtonStyle(
            icon_size=20,
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.PRIMARY,
                ft.ControlState.HOVERED: ft.Colors.PRIMARY_CONTAINER,
            },
            color={
                ft.ControlState.DEFAULT: ft.Colors.ON_PRIMARY,
                ft.ControlState.HOVERED: ft.Colors.ON_PRIMARY_CONTAINER,
            },
            elevation={"pressed": 0, "": 1},
            animation_duration=200,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
        on_click=start_download_click,
        ref=download_button_rf,
        height=50,
        width=345,
    )

    main_container = ft.Container(
        content=ft.Column(
            controls=[
                thumbnail_container,
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(height=16),
                            status_text,
                            barra_de_progresso,
                            ft.Container(height=16),
                            input_link,
                            ft.Container(height=12),
                            ft.Row(
                                controls=[
                                    format_dropdown,
                                    download_button,
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=30,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    padding=ft.padding.only(left=25, right=25, bottom=25),
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=770,
        border_radius=12,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=30,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            offset=ft.Offset(0, 10),
        ),
    )

    container = ft.Container(
        on_hover=check_clipboard_for_youtube_link,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                main_container,
            ],
            spacing=0,
        ),
        padding=ft.padding.all(40),
        expand=True,
    )

    def on_layout(e):
        renderizar_lista_downloads_salvos(page, sidebar)
        start_clipboard_task()

    def start_clipboard_task():
        storage = page.session.get("app_storage")
        clipboard_monitoring = False
        if storage:
            clipboard_monitoring = storage.get_setting("clipboard_monitoring", True)

        if clipboard_monitoring:
            page.run_async_task(partial(clipboard_reminder, page, status_text_rf))

    container.on_layout = on_layout

    return container

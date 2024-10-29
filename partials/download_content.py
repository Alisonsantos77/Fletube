import flet as ft
import threading
import logging
import re
import asyncio
import uuid
import time
from functools import partial
from services.dlp_service import start_download
from utils.session_storage_utils import (
    recuperar_downloads_bem_sucedidos_session,
    salvar_downloads_bem_sucedidos_session,
)
from utils.client_storage_utils import salvar_downloads_bem_sucedidos_client
from utils.file_picker_utils import setup_file_picker
from utils.extract_thumbnail import extract_thumbnail_url
from utils.extract_title import extract_title_from_url
from utils.validations import validar_input
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def clipboard_reminder(page, status_text_rf, download_in_progress):
    seconds = 60
    while seconds > 0:
        if not download_in_progress["value"]:
            if status_text_rf.current is not None:
                status_text_rf.current.value = f"Copie o link e passe o mouse na tela dentro de {seconds} segundos."
                status_text_rf.current.update()
            seconds -= 1
            await asyncio.sleep(1)
        else:
            break
    else:
        if not download_in_progress["value"] and status_text_rf.current is not None:
            status_text_rf.current.value = "Faça o download do seu vídeo aqui!"
            status_text_rf.current.update()


def renderizar_lista_downloads_salvos(page, sidebar):
    downloads = recuperar_downloads_bem_sucedidos_session(page)
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
                f"Adicionando download: ID: {download_id}, Título: {title}, Formato: {format}, Thumbnail: {thumbnail}, Caminho: {file_path}"
            )
            sidebar.add_download_item(
                id=download_id,
                title=title,
                subtitle=format,
                thumbnail_url=thumbnail,
                file_path=file_path,
            )
    else:
        logger.warning("Nenhum download recuperado do session_storage.")


def download_content(page: ft.Page, sidebar):
    drop_format_rf = ft.Ref[ft.Dropdown]()
    img_downloader_rf = ft.Ref[ft.Image]()
    status_text_rf = ft.Ref[ft.Text]()
    download_button_rf = ft.Ref[ft.ElevatedButton]()
    barra_progress_video_rf = ft.Ref[ft.ProgressBar]()
    input_link_rf = ft.Ref[ft.TextField]()
    dlg_modal_rf = ft.Ref[ft.AlertDialog]()

    download_in_progress = {"value": False}
    dialog_open = {"value": False}
    last_clipboard_content = {"value": None}
    download_states = {}

    barra_de_progresso = ft.ProgressBar(
        width=350,
        height=8,
        color=ft.colors.PRIMARY,
        bgcolor=ft.colors.ON_SURFACE,
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
            status_text_rf.current.color = ft.colors.PRIMARY
            status_text_rf.current.update()

            barra_progress_video_rf.current.value = 1.0
            barra_progress_video_rf.current.visible = False
            barra_progress_video_rf.current.update()

            snackbar = ft.SnackBar(
                content=ft.Text("Thumbnail atualizada com sucesso!"),
                bgcolor=ft.colors.PRIMARY,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
        except ValueError as ve:
            status_text_rf.current.value = str(ve)
            status_text_rf.current.color = ft.colors.ERROR
            status_text_rf.current.update()

            barra_progress_video_rf.current.value = 1.0
            barra_progress_video_rf.current.visible = False
            barra_progress_video_rf.current.update()

            snackbar = ft.SnackBar(
                content=ft.Text(str(ve)),
                bgcolor=ft.colors.ERROR,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

    def on_directory_selected(directory_path):
        if directory_path:
            page.client_storage.set("download_directory", directory_path)
            status_text_rf.current.value = f"Diretório selecionado: {directory_path}"
            status_text_rf.current.color = ft.colors.PRIMARY
            status_text_rf.current.update()
            snackbar = ft.SnackBar(
                content=ft.Text(f"Diretório selecionado: {directory_path}"),
                bgcolor=ft.colors.PRIMARY,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

    def iniciar_download_apos_selecionar_diretorio(diretorio):
        download_in_progress["value"] = True
        link = input_link_rf.current.value.strip()
        format_dropdown = drop_format_rf.current.value
        page.client_storage.set("selected_format", format_dropdown)
        if link and format_dropdown:
            status_text_rf.current.value = "Iniciando download..."
            status_text_rf.current.color = ft.colors.PRIMARY
            status_text_rf.current.update()
            snackbar = ft.SnackBar(
                content=ft.Text("Download iniciado..."),
                bgcolor=ft.colors.PRIMARY,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

            input_link_rf.current.disabled = True
            input_link_rf.current.update()
            drop_format_rf.current.disabled = True
            drop_format_rf.current.update()
            download_button_rf.current.disabled = True
            download_button_rf.current.update()

            barra_progress_video_rf.current.value = 0.0
            barra_progress_video_rf.current.visible = True
            barra_progress_video_rf.current.update()

            def progress_hook(d):
                if d["status"] == "downloading":
                    if "total_bytes" in d and "downloaded_bytes" in d:
                        progress = d["downloaded_bytes"] / d["total_bytes"]
                        barra_progress_video_rf.current.value = progress
                        barra_progress_video_rf.current.update()
                        status_text_rf.current.value = (
                            f"Baixando... {progress*100:.2f}%"
                        )
                        status_text_rf.current.color = ft.colors.PRIMARY
                        status_text_rf.current.update()
                elif d["status"] == "finished":
                    try:
                        info_dict = d.get("info_dict", {})
                        video_id = info_dict.get("id", "")
                        if not video_id:
                            video_id = str(uuid.uuid4())
                            logger.warning(
                                f"ID não encontrado nos metadados. Gerado ID: {video_id}"
                            )
                        title = info_dict.get("title", "Título Indisponível")
                        thumbnail = info_dict.get("thumbnail", "/images/logo.png")
                        file_path = d.get("filename", "")
                        format_selected = format_dropdown
                        download_data = {
                            "id": video_id,
                            "title": title,
                            "thumbnail": thumbnail,
                            "format": format_selected,
                            "file_path": file_path,
                        }
                        salvar_downloads_bem_sucedidos_client(page, download_data)
                        salvar_downloads_bem_sucedidos_session(page, download_data)

                        if video_id not in sidebar.items:
                            sidebar.add_download_item(
                                id=download_data["id"],
                                title=download_data["title"],
                                subtitle=download_data["format"],
                                thumbnail_url=download_data["thumbnail"],
                                file_path=download_data["file_path"],
                            )

                        download_in_progress["value"] = False
                        status_text_rf.current.value = (
                            "Download concluído! Iniciando conversão..."
                        )
                        status_text_rf.current.color = ft.colors.PRIMARY
                        status_text_rf.current.update()

                        status_text_rf.current.value = "Convertendo arquivo..."
                        status_text_rf.current.update()

                        barra_progress_video_rf.current.value = 0.0
                        barra_progress_video_rf.current.visible = True
                        barra_progress_video_rf.current.update()

                        def conversion_hook():
                            try:
                                for i in range(1, 11):
                                    barra_progress_video_rf.current.value = i * 0.1
                                    barra_progress_video_rf.current.update()
                                    status_text_rf.current.value = (
                                        f"Convertendo arquivo... {i*10}%"
                                    )
                                    status_text_rf.current.update()
                                    time.sleep(0.2)
                                barra_progress_video_rf.current.visible = False
                                barra_progress_video_rf.current.update()
                                status_text_rf.current.value = "Conversão concluída!"
                                status_text_rf.current.color = (
                                    ft.colors.SURFACE_CONTAINER_HIGHEST
                                )
                                status_text_rf.current.update()

                                input_link_rf.current.disabled = False
                                input_link_rf.current.update()
                                drop_format_rf.current.disabled = False
                                drop_format_rf.current.update()
                                download_button_rf.current.disabled = False
                                download_button_rf.current.text = "Iniciar Download"
                                download_button_rf.current.update()

                                input_link_rf.current.value = ""
                                input_link_rf.current.update()
                                img_downloader_rf.current.src = "/images/logo.png"
                                img_downloader_rf.current.update()

                                snackbar = ft.SnackBar(
                                    content=ft.Text(
                                        "Download e conversão concluídos com sucesso!"
                                    ),
                                    bgcolor=ft.colors.ON_PRIMARY_CONTAINER,
                                    action="OK",
                                )
                                snackbar.on_action = lambda e: None
                                page.overlay.append(snackbar)
                                snackbar.open = True
                                page.update()
                            except Exception as e:
                                logger.error(f"Erro durante a conversão: {e}")

                        conversion_thread = threading.Thread(
                            target=conversion_hook, daemon=True
                        )
                        conversion_thread.start()

                    except Exception as e:
                        logger.error(f"Exception during processing download: {e}")
                        download_in_progress["value"] = False
                        status_text_rf.current.value = "Erro ao processar o download."
                        status_text_rf.current.color = ft.colors.ERROR
                        status_text_rf.current.update()

                        input_link_rf.current.disabled = False
                        input_link_rf.current.update()
                        drop_format_rf.current.disabled = False
                        drop_format_rf.current.update()
                        download_button_rf.current.text = "Iniciar Download"
                        download_button_rf.current.disabled = False
                        download_button_rf.current.bgcolor = ft.colors.PRIMARY
                        download_button_rf.current.update()

                        snackbar = ft.SnackBar(
                            content=ft.Text("Erro ao processar o download."),
                            bgcolor=ft.colors.ERROR,
                            action="OK",
                        )
                        snackbar.on_action = lambda e: None
                        page.overlay.append(snackbar)
                        snackbar.open = True
                        page.update()
                elif d["status"] == "error":
                    download_in_progress["value"] = False
                    status_text_rf.current.value = "Erro no download."
                    status_text_rf.current.color = ft.colors.ERROR
                    status_text_rf.current.update()
                    barra_progress_video_rf.current.visible = False
                    barra_progress_video_rf.current.update()
                    download_button_rf.current.text = "Iniciar Download"
                    download_button_rf.current.disabled = False
                    download_button_rf.current.bgcolor = ft.colors.PRIMARY
                    download_button_rf.current.update()
                    snackbar = ft.SnackBar(
                        content=ft.Text("Erro no download."),
                        bgcolor=ft.colors.ERROR,
                        action="OK",
                    )
                    snackbar.on_action = lambda e: None
                    page.overlay.append(snackbar)
                    snackbar.open = True
                    page.update()

            def download_thread():
                try:
                    start_download(link, format_dropdown, diretorio, progress_hook)
                except Exception as e:
                    logger.error(f"Erro ao iniciar o download: {e}")
                    download_in_progress["value"] = False
                    status_text_rf.current.value = "Erro ao iniciar o download."
                    status_text_rf.current.color = ft.colors.ERROR
                    status_text_rf.current.update()
                    snackbar = ft.SnackBar(
                        content=ft.Text("Erro ao iniciar o download."),
                        bgcolor=ft.colors.ERROR,
                        action="OK",
                    )
                    snackbar.on_action = lambda e: None
                    page.overlay.append(snackbar)
                    snackbar.open = True
                    page.update()

            thread = threading.Thread(target=download_thread, daemon=True)
            thread.start()
        else:
            status_text_rf.current.value = (
                "Por favor, insira um link e escolha um formato."
            )
            status_text_rf.current.color = ft.colors.ERROR
            status_text_rf.current.update()
            snackbar = ft.SnackBar(
                content=ft.Text("Por favor, insira um link e escolha um formato."),
                bgcolor=ft.colors.ERROR,
                action="OK",
            )
            snackbar.on_action = lambda e: None
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()

    def start_download_click(e):
        diretorio = page.client_storage.get("download_directory")
        if diretorio and diretorio != "Nenhum diretório selecionado!":
            iniciar_download_apos_selecionar_diretorio(diretorio)
        else:
            status_text_rf.current.value = (
                "Nenhum diretório selecionado! Por favor, selecione um diretório."
            )
            status_text_rf.current.color = ft.colors.ERROR
            status_text_rf.current.update()
            snackbar = ft.SnackBar(
                content=ft.Text(
                    "Nenhum diretório selecionado! Por favor, selecione um diretório."
                ),
                bgcolor=ft.colors.ERROR,
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

        if download_in_progress["value"] or dialog_open["value"]:
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
                    dlg_modal_rf.current.title.value = "Link Detectado no Clipboard"
                    dlg_modal_rf.current.content.value = (
                        "Deseja substituir o link atual pelo do clipboard?"
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
        focused_border_color=ft.colors.ON_BACKGROUND,
        focused_bgcolor=ft.colors.SECONDARY,
        cursor_color=ft.colors.ON_SURFACE,
        content_padding=ft.padding.all(10),
        hint_text="Cole o link do YouTube aqui...",
        prefix_icon=ft.icons.LINK,
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
        icon=ft.icons.DOWNLOAD,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.colors.PRIMARY,
                ft.ControlState.HOVERED: ft.colors.ON_PRIMARY_CONTAINER,
            },
            color={
                ft.ControlState.DEFAULT: ft.colors.ON_PRIMARY,
                ft.ControlState.HOVERED: ft.colors.ON_SECONDARY,
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
        color=ft.colors.PRIMARY,
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
                            col={"sm": 6, "md": 4, "xl": 12},
                        ),
                        ft.Container(
                            status_text,
                            padding=5,
                            col={"sm": 6, "md": 4, "xl": 10},
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            barra_de_progresso,
                            padding=5,
                            col={"sm": 6, "md": 4, "xl": 10},
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
                            col={"sm": 6, "md": 4, "xl": 10},
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
                partial(clipboard_reminder, page, status_text_rf, download_in_progress)
            )

    container.on_layout = on_layout

    return container

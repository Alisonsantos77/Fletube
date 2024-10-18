import flet as ft
import threading
import logging
from services.dlp_service import start_download
from utils.session_storage_utils import (
    recuperar_downloads_bem_sucedidos_session,
    salvar_downloads_bem_sucedidos_session,
)
from utils.file_picker_utils import setup_file_picker
from utils.extract_thumbnail import extract_thumbnail_url
from utils.extract_title import extract_title_from_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def renderizar_lista_downloads_salvos(page, sidebar):
    # Recupera os downloads salvos no session_storage
    downloads = recuperar_downloads_bem_sucedidos_session(page)

    # Verifica se a lista de downloads foi recuperada corretamente
    if downloads:
        logger.info(f"Downloads recuperados: {downloads}")
        for download in downloads:
            title = download.get("title", "Título Indisponível")
            format = download.get("format", "Formato Indisponível")
            thumbnail = download.get("thumbnail", "/images/logo.png")
            src = download.get("src", "")

            logger.info(
                f"Adicionando download: Título: {title}, Formato: {format}, Thumbnail: {thumbnail}"
            )

            # Adiciona o item à sidebar
            sidebar.add_download_item(
                title=title,
                subtitle=format,
                thumbnail_url=thumbnail,
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

    barra_de_progresso = ft.ProgressBar(
        width=350,
        height=8,
        color=ft.colors.PRIMARY,
        bgcolor=ft.colors.ON_SURFACE,
        ref=barra_progress_video_rf,
        visible=False,
    )

    def update_thumbnail(e):
        """
        Atualiza a imagem de thumbnail com base na URL do vídeo fornecida.

        Args:
            e: O evento que acionou esta função.
        """
        video_url = input_link.value.strip()
        logger.info(f"Atualizando thumbnail para URL: {video_url}")
        try:
            thumb_url = extract_thumbnail_url(video_url)
            img_downloader_rf.current.src = thumb_url
            img_downloader_rf.current.update()
            status_text_rf.current.value = "Thumbnail atualizado."
            status_text_rf.current.color = ft.colors.GREEN
            status_text_rf.current.update()
            logger.info(f"Thumbnail atualizado para: {thumb_url}")
        except ValueError as ve:
            status_text_rf.current.value = str(ve)
            status_text_rf.current.color = ft.colors.ERROR
            status_text_rf.current.update()
            logger.error(f"Erro ao extrair thumbnail: {ve}")

    def on_directory_selected(directory_path):
        if directory_path:
            page.session.set("download_directory", directory_path)
            status_text_rf.current.value = f"Diretório selecionado: {directory_path}"
            status_text_rf.current.color = ft.colors.PRIMARY
            status_text_rf.current.update()

    def iniciar_download_apos_selecionar_diretorio(diretorio):
        link = input_link.value.strip()
        format_dropdown = drop_format_rf.current.value
        logger.info(f"Formato selecionado pelo usuário: {format_dropdown}")
        page.session.set("selected_format", format_dropdown)

        if link and format_dropdown:
            status_text_rf.current.value = "Iniciando download..."
            status_text_rf.current.color = ft.colors.PRIMARY
            status_text_rf.current.update()

            def progress_hook(d):
                """
                Hook de progresso que atualiza a barra de progresso e o texto de status durante o download.
                Também lida com erros no processo de download.
                """
                if d["status"] == "downloading":
                    if "total_bytes" in d and "downloaded_bytes" in d and "eta" in d:
                        progress = d["downloaded_bytes"] / d["total_bytes"]

                        download_button_rf.current.disabled = True
                        download_button_rf.current.bgcolor = ft.colors.SECONDARY
                        download_button_rf.current.text = "Aguarde..."
                        download_button_rf.current.update()

                        barra_progress_video_rf.current.value = progress
                        barra_progress_video_rf.current.visible = True
                        barra_progress_video_rf.current.update()

                        status_text_rf.current.value = (
                            f"Baixando... {progress*100:.2f}%"
                        )
                        status_text_rf.current.color = ft.colors.PRIMARY
                        status_text_rf.current.update()

                elif d["status"] == "finished":
                    try:
                        title = extract_title_from_url(link)
                        thumbnail = extract_thumbnail_url(link)
                        src = d["filename"]
                        download_data = {
                            "title": title,
                            "thumbnail": thumbnail,
                            "format": format_dropdown,
                        }

                        salvar_downloads_bem_sucedidos_session(page, download_data)

                        sidebar.add_download_item(
                            title=download_data["title"],
                            subtitle=download_data["format"],
                            thumbnail_url=download_data["thumbnail"],
                        )

                        download_button_rf.current.text = "Iniciar download"
                        download_button_rf.current.disabled = False
                        download_button_rf.current.bgcolor = ft.colors.PRIMARY
                        download_button_rf.current.update()

                        status_text_rf.current.value = "Download concluído!"
                        status_text_rf.current.color = ft.colors.GREEN
                        status_text_rf.current.update()

                        barra_progress_video_rf.current.value = 1.0
                        barra_progress_video_rf.current.visible = False
                        barra_progress_video_rf.current.update()

                        input_link_rf.current.value = None
                        input_link_rf.current.update()

                    except Exception as e:
                        logger.error(f"Erro ao processar o download: {e}")
                        status_text_rf.current.value = "Erro ao processar o download."
                        status_text_rf.current.color = ft.colors.ERROR
                        status_text_rf.current.update()

                        download_button_rf.current.text = "Iniciar download"
                        download_button_rf.current.disabled = False
                        download_button_rf.current.bgcolor = ft.colors.PRIMARY
                        download_button_rf.current.update()

                elif d["status"] == "error":
                    status_text_rf.current.value = "Erro no download."
                    status_text_rf.current.color = ft.colors.ERROR
                    status_text_rf.current.update()

                    barra_progress_video_rf.current.visible = False
                    barra_progress_video_rf.current.update()

                    download_button_rf.current.text = "Iniciar download"
                    download_button_rf.current.disabled = False
                    download_button_rf.current.bgcolor = ft.colors.PRIMARY
                    download_button_rf.current.update()

            def download_thread():
                try:
                    start_download(link, format_dropdown, diretorio, progress_hook)
                    logger.info(f"Iniciando download com formato: {format_dropdown}")
                except Exception as e:
                    logger.error(f"Erro ao iniciar o download: {e}")

            thread = threading.Thread(target=download_thread, daemon=True)
            thread.start()
        else:
            status_text_rf.current.value = (
                "Por favor, insira um link e escolha um formato."
            )
            status_text_rf.current.color = ft.colors.ERROR
            status_text_rf.current.update()

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
            file_picker.get_directory_path()

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
        width=100,
        focused_border_color=ft.colors.ON_BACKGROUND,
        focused_bgcolor=ft.colors.SECONDARY,
        cursor_color=ft.colors.ON_SURFACE,
        content_padding=ft.padding.all(10),
        hint_text="Cole o link do YouTube aqui...",
        prefix_icon=ft.icons.LINK,
        on_change=update_thumbnail,
        ref=input_link_rf,
    )

    format_dropdown = ft.Dropdown(
        ref=drop_format_rf,
        label="Escolha o formato",
        value=page.session.get("selected_format")
        or page.session.get("default_format")
        or "mp3",
        options=[
            ft.dropdown.Option("mp4", "MP4"),
            ft.dropdown.Option("mkv", "MKV"),
            ft.dropdown.Option("flv", "FLV"),
            ft.dropdown.Option("webm", "WEBM"),
            ft.dropdown.Option("avi", "AVI"),
            ft.dropdown.Option("mp3", "MP3"),
            ft.dropdown.Option("aac", "AAC"),
            ft.dropdown.Option("wav", "WAV"),
            ft.dropdown.Option("m4a", "M4A"),
            ft.dropdown.Option("opus", "OPUS"),
        ],
    )

    download_button = ft.ElevatedButton(
        text="Iniciar Download",
        icon=ft.icons.DOWNLOAD,
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.colors.PRIMARY,
                ft.ControlState.HOVERED: ft.colors.SECONDARY,
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
        value="Faça o download do seu vídeo aqui!" ,
        color=ft.colors.PRIMARY,
        size=16,
        ref=status_text_rf,
    )

    container = ft.Container(
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
                        ft.Container(
                            status_text,
                            padding=5,
                            col={"sm": 6, "md": 4, "xl": 10},
                            alignment=ft.alignment.center,
                        ),
                    ],
                )
            ],
        )
    )

    # Renderizar os downloads já salvos no carregamento
    renderizar_lista_downloads_salvos(page, sidebar)

    return container

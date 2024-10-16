import flet as ft
import threading
import logging
from utils.extract_thumbnail import extract_thumbnail_url
from utils.file_picker_utils import setup_file_picker
from services.dlp_service import start_download
from utils.ffmpeg_utils import check_ffmpeg_installed, install_ffmpeg
from yt_dlp import YoutubeDL
from partials.download_sidebar import SidebarList

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def download_content(page: ft.Page, sidebar: SidebarList):
    """
    Configura a interface de download e gerencia o processo de download.

    Args:
        page (ft.Page): O objeto da página Flet.
        sidebar (SidebarList): O componente da barra lateral para exibir itens de download.
    """
    logger.info("Inicializando download_content.")

    # Verifica se o FFmpeg está instalado; instala se não estiver
    if not check_ffmpeg_installed(page):
        install_ffmpeg(page)
        logger.info("FFmpeg não estava instalado e foi instalado.")

    # Referências para os componentes
    drop_format_rf = ft.Ref[ft.Dropdown]()
    img_downloader_rf = ft.Ref[ft.Image]()
    barra_progress_video_rf = ft.Ref[ft.ProgressBar]()
    status_text_rf = ft.Ref[ft.Text]()

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
        """
        Lida com o evento quando um diretório é selecionado.

        Args:
            directory_path (str): O caminho do diretório selecionado.
        """
        if directory_path:
            page.client_storage.set("download_directory", directory_path)
            logger.info(f"Diretório selecionado: {directory_path}")

            status_text_rf.current.value = f"Diretório selecionado: {directory_path}"
            status_text_rf.current.color = ft.colors.GREEN
            status_text_rf.current.update()

            iniciar_download_apos_selecionar_diretorio(directory_path)


    def iniciar_download_apos_selecionar_diretorio(diretorio):
        """
        Inicia o processo de download após a seleção do diretório.

        Args:
            diretorio (str): O diretório onde o download será salvo.
        """
        logger.info(f"Iniciando download para o diretório: {diretorio}")
        link = input_link.value.strip()
        format_dropdown = drop_format_rf.current.value

        logger.debug(f"Link: {link}, Formato: {format_dropdown}")

        page.client_storage.set("selected_format", format_dropdown)

        if link and format_dropdown:
            status_text_rf.current.value = "Iniciando download..."
            status_text_rf.current.color = ft.colors.PRIMARY
            status_text_rf.current.update()
            logger.info("Download iniciado.")

            barra_progress_video_rf.current.visible = True
            barra_progress_video_rf.current.value = 0.0
            barra_progress_video_rf.current.update()

            img_downloader_rf.current.src = "https://i.gifer.com/YCZH.gif"
            img_downloader_rf.current.update()

            # Busca informações do vídeo para obter título, thumbnail e duração
            with YoutubeDL() as ydl:
                try:
                    info_dict = ydl.extract_info(link, download=False)
                    video_title = info_dict.get("title", "Vídeo")
                    thumbnail_url = info_dict.get("thumbnail", "/images/logo.png")
                    video_duration = info_dict.get(
                        "duration", "00:00"
                    )
                    logger.info(
                        f"Título do vídeo: {video_title}, URL da thumbnail: {thumbnail_url}, Duração: {video_duration}"
                    )
                except Exception as e:
                    status_text_rf.current.value = (
                        f"Erro ao obter informações do vídeo: {e}"
                    )
                    status_text_rf.current.color = ft.colors.ERROR
                    status_text_rf.current.update()
                    logger.error(f"Erro ao extrair informações do vídeo: {e}")
                    return

            # Adiciona item à barra lateral com duração
            sidebar.add_download_item(
                title=video_title,
                subtitle=format_dropdown,
                thumbnail_url=thumbnail_url,
                duration=video_duration,  # Agora passamos a duração do vídeo
                progress=0.0,
            )
            item_index = len(sidebar.items) - 1  # Índice do item adicionado

            # Função de callback de progresso do download
            def progress_hook(d):
                # Código para atualização de progresso
                pass

            # Inicia o download em uma thread separada
            def download_thread():
                try:
                    start_download(link, format_dropdown, diretorio, progress_hook)
                except Exception as e:
                    logger.error(f"Erro ao iniciar o download: {e}")

            thread = threading.Thread(target=download_thread, daemon=True)
            thread.start()
            logger.info("Thread de download iniciada.")
        else:
            status_text_rf.current.value = "Por favor, insira um link e escolha um formato."
            status_text_rf.current.color = ft.colors.ERROR
            status_text_rf.current.update()
            logger.warning("Download tentado sem link ou formato.")

    def start_download_click(e):
        """
        Lida com o evento de clique no botão de download.

        Args:
            e: O evento que acionou esta função.
        """
        diretorio = page.client_storage.get(
            "download_directory"
        )

        if not diretorio:
            status_text_rf.current.value = (
                "Por favor, selecione um diretório para salvar o download."
            )
            status_text_rf.current.color = ft.colors.ERROR
            status_text_rf.current.update()
            logger.info("Diretório não selecionado. Abrindo FilePicker.")
            file_picker.get_directory_path()
        else:
            iniciar_download_apos_selecionar_diretorio(diretorio)

    file_picker = setup_file_picker(page, on_directory_selected)

    img_downloader = ft.Image(
        src="/images/logo.png",
        ref=img_downloader_rf,
        width=400,
        height=400,
        visible=True,
        fit=ft.ImageFit.CONTAIN,
    )

    barra_progress_video = ft.ProgressBar(
        width=350,
        bgcolor=ft.colors.PRIMARY,
        color=ft.colors.RED,
        visible=False,
        ref=barra_progress_video_rf,
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
    )

    format_dropdown = ft.Dropdown(
        ref=drop_format_rf,
        label="Escolha o formato",
        value=page.client_storage.get("selected_format")
        or page.client_storage.get("default_format")
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
    )

    status_text = ft.Text(
        value="Aguardando o download...",
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
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            barra_progress_video,
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

    logger.info("Configuração de download_content completa.")

    return container

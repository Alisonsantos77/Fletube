import flet as ft
from utils.extract_thumbnail import extract_thumbnail_url
from utils.file_picker_utils import setup_file_picker


def download_content(page: ft.Page):

    drop_format_rf = ft.Ref[ft.Dropdown]()
    img_downloader_rf = ft.Ref[ft.Image]()

    def update_thumbnail(e):
        video_url = input_link.value
        try:
            thumb_url = extract_thumbnail_url(video_url)
            img_downloader_rf.current.src = thumb_url
            img_downloader_rf.current.update()
        except ValueError as ve:
            status_text.value = str(ve)
            status_text.color = ft.colors.ERROR
            status_text.update()

    def on_directory_selected(directory_path):
        # Exibe o diretório selecionado para testar o valor
        print(f"Diretório selecionado: {directory_path}")
        status_text.value = f"Diretório selecionado: {directory_path}"
        status_text.update()

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
        width=350, col=8, bgcolor=ft.colors.PRIMARY, color=ft.colors.RED, visible=False
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

    def start_download(e):
        print(f"Input URL: {input_link.value}")
        print(f"Formato selecionado: {drop_format_rf.current.value}")

        # Se o diretório já foi selecionado, ele será exibido
        default_dir = page.client_storage.get("download_directory")
        default_format = page.client_storage.get("default_format")
        
        if default_dir and default_dir != "Nenhum diretório selecionado!":
            print(f"Usando diretório padrão: {default_dir}")
        else:
            # Se o diretório não foi selecionado ainda
            file_picker.get_directory_path()
        
        if default_format:
            print(f"Formato padrão: {default_format}")
            drop_format_rf.current.value = default_format
            drop_format_rf.current.update()
        else:
            # Se o formato padrão não foi definido ainda
            drop_format_rf.current.value = "mp3"
            drop_format_rf.current.update()

        # Simulando salvamento na sessão
        print(
            f"Salvando na sessão: Diretório - {default_dir}, URL - {input_link.value}, Formato - {drop_format_rf.current.value}"
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
        on_click=start_download,
    )

    status_text = ft.Text(
        value="Aguardando o download...",
        color=ft.colors.PRIMARY,
        size=16,
    )

    return ft.Container(
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

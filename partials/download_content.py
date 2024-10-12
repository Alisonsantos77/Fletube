import flet as ft


def download_content(page: ft.Page):

    drop_format_rf = ft.Ref[ft.Dropdown]()

    img_downloader = ft.Image(
        src="/images/logo-fletube.png",
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
    )

    status_text = ft.Text(
        value="Aguardando o download...",
        color=ft.colors.PRIMARY,
        size=16,
    )

    img_teste = ft.Image(
        src="https://img.youtube.com/vi/jQMsWL0g0jc/hqdefault.jpg",
        width=100,
        height=100,
        fit=ft.ImageFit.CONTAIN,
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

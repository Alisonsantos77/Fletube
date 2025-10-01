import flet as ft


def ContactSettings():
    return ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Contatos",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.Text(
                    "Entre em contato conosco através dos meios abaixo:",
                    size=16,
                    text_align=ft.TextAlign.JUSTIFY,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            content=ft.Image(
                                src="images/contact/icons8-whatsapp-48.png",
                                width=40,
                                height=40,
                            ),
                            icon_color=ft.Colors.PRIMARY,
                            tooltip="Abrir WhatsApp",
                            url="https://wa.link/oebrg2",
                            style=ft.ButtonStyle(
                                overlay_color={
                                    "": ft.Colors.TRANSPARENT,
                                    "hovered": ft.Colors.GREEN,
                                },
                            ),
                        ),
                        ft.IconButton(
                            content=ft.Image(
                                src="images/contact/outlook-logo.png",
                                width=40,
                                height=40,
                            ),
                            icon_color=ft.Colors.PRIMARY,
                            tooltip="Enviar Email",
                            url="mailto:Alisondev77@hotmail.com?subject=Feedback%20-%20MultiTools&body=Olá, gostaria de fornecer feedback.",
                            style=ft.ButtonStyle(
                                overlay_color={
                                    "": ft.Colors.TRANSPARENT,
                                    "hovered": ft.Colors.BLUE,
                                },
                            ),
                        ),
                        ft.IconButton(
                            content=ft.Image(
                                src="images/contact/icons8-linkedin-48.png",
                                width=40,
                                height=40,
                            ),
                            tooltip="Acessar LinkedIn",
                            url="https://www.linkedin.com/in/alisonsantosdev",
                            style=ft.ButtonStyle(
                                overlay_color={
                                    "": ft.Colors.TRANSPARENT,
                                    "hovered": ft.Colors.BLUE,
                                },
                            ),
                        ),
                        ft.IconButton(
                            content=ft.Image(
                                src="images/contact/icons8-github-64.png",
                                width=40,
                                height=40,
                            ),
                            icon_color=ft.Colors.PRIMARY,
                            tooltip="Acessar GitHub",
                            url="https://github.com/Alisonsantos77",
                            style=ft.ButtonStyle(
                                overlay_color={
                                    "": ft.Colors.TRANSPARENT,
                                    "hovered": ft.Colors.GREY,
                                },
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            spacing=20,
        ),
    )

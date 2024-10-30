import flet as ft


def create_drawer(page: ft.Page):
    theme = (page.client_storage.get("theme_mode") or "LIGHT").upper()
    theme_icon = ft.icons.DARK_MODE if theme == "DARK" else ft.icons.LIGHT_MODE
    
    drawer_header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    "Fletube",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_600,
                    expand=True,
                    text_align=ft.TextAlign.LEFT,
                ),
                ft.Image(
                    src="/images/logo.png",
                    width=100,
                    height=100,
                    fit=ft.ImageFit.CONTAIN,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(vertical=20, horizontal=15),
    )

    def open_info_dialog(e):
        info_dialog = ft.AlertDialog(
            title=ft.Row(
                [
                    ft.Text(
                        "Fletube", size=24, weight=ft.FontWeight.BOLD
                    ),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        tooltip="Fechar",
                        on_click=lambda e: close_info_dialog(),
                        icon_color=ft.colors.RED,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            content=ft.Text("Entre em contato ou acesse minhas redes sociais:", size=16),
            actions=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            content=ft.Image(
                                src="images/contact/icons8-whatsapp-48.png",
                                width=40,
                                height=40,
                            ),
                            icon_color=ft.colors.GREEN,
                            tooltip="Abrir WhatsApp",
                            url="https://wa.link/oebrg2",
                            style=ft.ButtonStyle(
                                overlay_color={
                                    "": ft.colors.TRANSPARENT,
                                    "hovered": ft.colors.GREEN,
                                },
                            ),
                        ),
                        ft.IconButton(
                            content=ft.Image(
                                src="images/contact/outlook-logo.png",
                                width=40,
                                height=40,
                            ),
                            icon_color=ft.colors.PRIMARY,
                            tooltip="Enviar Email",
                            url="mailto:Alisondev77@hotmail.com?subject=Feedback%20-%20MultiTools&body=Olá, gostaria de fornecer feedback.",
                            style=ft.ButtonStyle(
                                overlay_color={
                                    "": ft.colors.TRANSPARENT,
                                    "hovered": ft.colors.BLUE,
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
                                    "": ft.colors.TRANSPARENT,
                                    "hovered": ft.colors.BLUE,
                                },
                            ),
                        ),
                        ft.IconButton(
                            content=ft.Image(
                                src="images/contact/icons8-github-64.png",
                                width=40,
                                height=40,
                            ),
                            icon_color=ft.colors.PRIMARY,
                            tooltip="Acessar GitHub",
                            url="https://github.com/Alisonsantos77",
                            style=ft.ButtonStyle(
                                overlay_color={
                                    "": ft.colors.TRANSPARENT,
                                    "hovered": ft.colors.GREY,
                                },
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        page.overlay.append(info_dialog)
        info_dialog.open = True
        page.update()

    def close_info_dialog():
        for dialog in page.overlay:
            if isinstance(dialog, ft.AlertDialog):
                dialog.open = False
        page.update()

    return ft.NavigationDrawer(
        controls=[
            drawer_header,
            ft.Container(expand=True),
            ft.NavigationDrawerDestination(
                label="Downloads",
                icon=ft.icons.DOWNLOAD_OUTLINED,
                selected_icon_content=ft.FilledButton(
                    text="Downloads",
                    icon=ft.icons.DOWNLOAD,
                ),
            ),
            ft.NavigationDrawerDestination(
                label="Histórico",
                icon=ft.icons.HISTORY_TOGGLE_OFF_OUTLINED,
                selected_icon_content=ft.FilledButton(
                    text="Histórico",
                    icon=ft.icons.HISTORY,
                ),
            ),
            ft.NavigationDrawerDestination(
                label="Configurações",
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon_content=ft.FilledButton(
                    text="Configurações",
                    icon=ft.icons.SETTINGS,
                ),
            ),
            ft.NavigationDrawerDestination(
                label=f"Tema ({'Escuro' if theme == 'DARK' else 'Claro'})",
                icon=theme_icon,
                selected_icon_content=ft.Icon(theme_icon, color=ft.colors.BLUE_600),
            ),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Desenvolvido por Alison Santos", size=14),
                        ft.IconButton(
                            icon=ft.icons.INFO_OUTLINED,
                            on_click=open_info_dialog,
                            tooltip="Informações",
                            icon_color=ft.colors.GREY,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(10),
            ),
        ],
        on_change=lambda e: handle_drawer_change(e, page),
    )


def handle_drawer_change(e, page):
    selected_index = e.control.selected_index
    if selected_index == 0:
        page.go("/downloads")
    elif selected_index == 1:
        page.go("/historico")
    elif selected_index == 2:
        page.go("/configuracoes")

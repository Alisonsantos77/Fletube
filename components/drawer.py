import flet as ft


def create_drawer(page: ft.Page):
    theme = page.client_storage.get("theme_mode")

    theme_icon = ft.icons.DARK_MODE if theme == "dark" else ft.icons.LIGHT_MODE

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
                label=f"Tema ({'Escuro' if theme == 'dark' else 'Claro'})",
                icon=theme_icon,
                selected_icon_content=ft.Icon(theme_icon, color=ft.colors.BLUE_600),
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

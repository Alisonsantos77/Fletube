import flet as ft

def create_drawer(page: ft.Page):
    theme = page.client_storage.get("theme_mode")
    return ft.NavigationDrawer(
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Fletube", size=30, weight=ft.FontWeight.BOLD, color=ft.colors.PRIMARY),
                        ft.Image(
                            src="icon_windows.png",
                            width=100,
                            height=100,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                    ],
                ),
                padding=ft.padding.all(10),
            ),
            ft.Divider(height=1),
            ft.NavigationDrawerDestination(
                label="Downloads",
                icon=ft.icons.DOWNLOAD_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.DOWNLOAD),
            ),
            ft.NavigationDrawerDestination(
                label="Histórico",
                icon=ft.icons.HISTORY_TOGGLE_OFF_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.HISTORY),
            ),
            ft.NavigationDrawerDestination(
                label="Configurações",
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
            ),
            ft.Divider(height=1),
            ft.NavigationDrawerDestination(
                label=f"Tema {theme}",
                icon=ft.icons.WB_SUNNY_OUTLINED,
                selected_icon_content=ft.Icon(ft.icons.WB_SUNNY),
            ),
        ],
        on_change=lambda e: handle_drawer_change(e, page)
    )

def handle_drawer_change(e, page):
    selected_index = e.control.selected_index
    if selected_index == 0:
        page.go('/downloads')
    elif selected_index == 1:
        page.go('/historico')
    elif selected_index == 2:
        page.go('/configuracoes')

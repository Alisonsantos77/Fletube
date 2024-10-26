import flet as ft
from partials.download_content import download_content
from partials.download_sidebar import SidebarList


def DownloadPage(page: ft.Page):
    # Inicialize a sidebar
    sidebar = SidebarList()

    # Inicialize o conteúdo da página
    content = download_content(page, sidebar)

    return ft.SafeArea(
        content=ft.ResponsiveRow(
            controls=[
                ft.Column(col={"sm": 12, "xl": 8}, controls=[content], expand=True),
                ft.Column(col={"sm": 0, "xl": 4}, controls=[sidebar], expand=False),
            ],
            spacing=20,
            expand=True,
        ),
        expand=True,
        top=True,
        bottom=True,
        left=False,
        right=False,
    )

import flet as ft
from partials.download_content import download_content
from partials.download_sidebar import sidebar_list


def DownloadPage(page: ft.Page):
    page.title = "Fletube"

    sidebar = sidebar_list()
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

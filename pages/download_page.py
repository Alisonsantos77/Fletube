import flet as ft

from utils.logging_config import setup_logging

logger = setup_logging()

from partials.download_content import download_content
from partials.download_sidebar import SidebarList
from services.download_manager import DownloadManager


def DownloadPage(page: ft.Page, download_manager: DownloadManager):
    sidebar = SidebarList(page)

    content = download_content(page, sidebar, download_manager)

    def on_unmount(e):
        logger.info("DownloadPage desmontada.")
        sidebar.on_unmount()
        logger.info("SidebarList desmontada.")

    download_page_container = ft.SafeArea(
        content=ft.Container(
            content=ft.ResponsiveRow(
                controls=[
                    ft.Column(col={"sm": 12, "xl": 8}, controls=[content], expand=True),
                    ft.Column(col={"sm": 0, "xl": 4}, controls=[sidebar], expand=False),
                ],
                spacing=10,
                expand=True,
            ),
        ),
        expand=True,
        top=True,
        bottom=True,
        left=False,
        right=False,
    )

    download_page_container.on_unmount = on_unmount

    return download_page_container

import flet as ft
import logging
from utils.client_storage_utils import (
    recuperar_downloads_bem_sucedidos_client,
    excluir_download_bem_sucedido_client,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def HistoryPage(page: ft.Page):
    download_history = recuperar_downloads_bem_sucedidos_client(page)

    def render_download_item(item):
        item_id = item.get("id")
        if not item_id:
            logger.warning(f"Item sem ID encontrado: {item}")
            return ft.Container()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(
                        src=item.get("thumbnail", "/images/logo.png"),
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                item.get("title", "Título Indisponível"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"Formato: {item.get('format', 'Formato Indisponível')}"
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        on_click=lambda e, item_id=item_id: delete_item(e, item_id),
                        tooltip="Excluir do histórico",
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(8),
            bgcolor=ft.colors.SURFACE_VARIANT,
            margin=ft.margin.symmetric(vertical=5),
        )

    def delete_item(e, item_id):
        if item_id:
            excluir_download_bem_sucedido_client(page, item_id)
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Item excluído do histórico."),
                bgcolor=ft.colors.PRIMARY_CONTAINER,
            )
            page.snack_bar.open = True
            page.views.clear()
            page.views.append(HistoryPage(page))
            page.update()
        else:
            logger.error("Tentativa de excluir um item sem ID.")

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Histórico de Downloads", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color=ft.colors.OUTLINE),
                ft.Column(
                    controls=[
                        render_download_item(item)
                        for item in download_history
                        if item.get("id")
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.all(20),
    )

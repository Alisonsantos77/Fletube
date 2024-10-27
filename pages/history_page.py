import flet as ft
from utils.client_storage_utils import (
    recuperar_downloads_bem_sucedidos_client,
    excluir_download_bem_sucedido_client,
)
import logging

logger = logging.getLogger(__name__)


def HistoryPage(page: ft.Page):
    download_history = recuperar_downloads_bem_sucedidos_client(page)
    search_query = ft.Ref[ft.TextField]()
    sort_by = ft.Ref[ft.Dropdown]()

    def render_download_item(item):
        item_id = item.get("id")
        if not item_id:
            logger.warning(f"Item sem ID encontrado: {item}")
            return ft.Container()

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Image(
                        src=item.get("thumbnail", "/images/logo.png"),
                        width=150,
                        height=150,
                        fit=ft.ImageFit.CONTAIN,
                        animate_opacity=300,
                    ),
                    ft.Text(
                        item.get("title", "Título Indisponível"),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(f"Formato: {item.get('format', 'Formato Indisponível')}"),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        on_click=lambda e, item_id=item_id: delete_item(e, item_id),
                        tooltip="Excluir do histórico",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(8),
            bgcolor=ft.colors.SURFACE_VARIANT,
            width=200,
            animate_scale=ft.animation.Animation(300, "easeInOut"),
        )

    def delete_item(e, item_id):
        if item_id:
            excluir_download_bem_sucedido_client(page, item_id)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Item excluído do histórico."),
                bgcolor=ft.colors.PRIMARY_CONTAINER,
            )
            page.snack_bar.open = True
            page.views.clear()
            page.views.append(HistoryPage(page))
            page.update()
        else:
            logger.error("Tentativa de excluir um item sem ID.")

    def update_history_view(e=None):
        query = search_query.current.value.lower() if search_query.current.value else ""
        sort_criteria = sort_by.current.value

        filtered_history = [
            item for item in download_history if query in item.get("title", "").lower()
        ]

        if sort_criteria == "title":
            filtered_history.sort(key=lambda x: x.get("title", "").lower())
        elif sort_criteria == "format":
            filtered_history.sort(key=lambda x: x.get("format", ""))

        history_grid.controls = [
            render_download_item(item) for item in filtered_history
        ]
        page.update()

    # Campo de busca
    search_field = ft.TextField(
        hint_text="Pesquisar...",
        on_change=update_history_view,
        ref=search_query,
        border_radius=8,
        content_padding=ft.padding.all(10),
    )

    # Dropdown de ordenação
    sort_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("title", "Título"),
            ft.dropdown.Option("format", "Formato"),
        ],
        value="title",
        on_change=update_history_view,
        ref=sort_by,
    )

    # GridView para exibir histórico de downloads com animações
    history_grid = ft.GridView(
        controls=[render_download_item(item) for item in download_history],
        max_extent=200,
        child_aspect_ratio=0.75,
        spacing=10,
    )

    # Tabs para organizar a interface com histórico e filtros
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Histórico de Downloads", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[search_field, sort_dropdown],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=1, color=ft.colors.OUTLINE),
                history_grid,
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.all(20),
    )

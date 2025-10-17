import os

import flet as ft
from loguru import logger


def HistoryPage(page: ft.Page):
    storage = page.session.get("app_storage")
    search_query = ft.Ref[ft.TextField]()
    sort_by = ft.Ref[ft.Dropdown]()
    selected_items = set()
    last_deleted_items = []

    dlg_modal_rf = ft.Ref[ft.AlertDialog]()

    counts_text = ft.Text("", size=16, weight=ft.FontWeight.W_600)

    def get_download_history():
        if storage:
            return storage.list_downloads()
        return []

    def render_download_item(item):
        item_id = item.get("id")
        file_path = item.get("file_path", "")
        if not item_id:
            logger.warning(f"Item sem ID encontrado: {item}")
            return ft.Container()

        def toggle_selection(e):
            if item_id in selected_items:
                selected_items.remove(item_id)
            else:
                selected_items.add(item_id)
            checkbox.checked = item_id in selected_items
            page.update()

        def delete_item(e, item_id=item_id, current_item=item):
            try:
                if storage:
                    storage.delete_download(item_id)
                last_deleted_items.append(current_item)
                update_history_view()

                from utils.ui_helpers import show_snackbar

                snack_bar = ft.SnackBar(
                    content=ft.Text("Item excluído."),
                    bgcolor=ft.Colors.PRIMARY,
                    action="Desfazer",
                )
                snack_bar.on_action = lambda e: undo_delete(e)
                page.overlay.append(snack_bar)
                snack_bar.open = True
                page.update()
            except Exception as ex:
                logger.error(f"Erro ao excluir o item: {ex}")
                from utils.ui_helpers import show_error_snackbar

                show_error_snackbar(page, "Erro ao excluir o item.")

        def undo_delete(e):
            for deleted_item in last_deleted_items:
                if storage:
                    storage.save_download(deleted_item.get("id"), deleted_item)
            last_deleted_items.clear()
            update_history_view()

            from utils.ui_helpers import show_snackbar

            show_snackbar(page, "Exclusão desfeita.")

        checkbox = ft.Checkbox(
            value=item_id in selected_items,
            on_change=toggle_selection,
        )

        container_ref = ft.Ref[ft.Container]()

        return ft.Container(
            ref=container_ref,
            content=ft.Column(
                controls=[
                    ft.Image(
                        src=item.get("thumbnail", "/images/logo.png"),
                        width=235,
                        height=120,
                        fit=ft.ImageFit.COVER,
                        border_radius=ft.border_radius.only(top_left=8, top_right=8),
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    item.get("title", "Título Indisponível"),
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    f"Formato: {item.get('format', 'Formato Indisponível')}",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.PLAY_ARROW,
                                            on_click=None,
                                            tooltip="Em breve",
                                            icon_size=20,
                                            disabled=True,
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.all(8)
                                            ),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.FOLDER_OPEN,
                                            on_click=None,
                                            tooltip="Em breve",
                                            icon_size=20,
                                            disabled=True,
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.all(8)
                                            ),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            on_click=lambda e, item_id=item_id: delete_item(
                                                e, item_id
                                            ),
                                            tooltip="Excluir do Histórico",
                                            icon_size=20,
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.all(8)
                                            ),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            on_click=None,
                                            tooltip="Em breve",
                                            icon_size=20,
                                            disabled=True,
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.all(8)
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=ft.padding.all(10),
                    ),
                ],
            ),
            width=220,
            border_radius=ft.border_radius.all(8),
            bgcolor=ft.Colors.SURFACE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=lambda e: on_hover(e, container_ref.current),
        )

    def on_hover(e, container):
        if e.data == "true":
            container.scale = 1.05
        else:
            container.scale = 1.0
        container.update()

    def delete_all(e):
        download_history = get_download_history()
        if not download_history:
            from utils.ui_helpers import show_error_snackbar

            show_error_snackbar(page, "Nenhum item para excluir.")
            return

        def confirm_delete(e):
            if storage:
                storage.clear_downloads()
            last_deleted_items.extend(download_history)
            update_history_view()
            dlg_modal_rf.current.open = False

            from utils.ui_helpers import show_snackbar

            snack_bar = ft.SnackBar(
                content=ft.Text("Todos os itens foram excluídos."),
                bgcolor=ft.Colors.PRIMARY,
                action="Desfazer",
            )
            snack_bar.on_action = lambda e: undo_delete_all(e)
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

        def cancel_delete(e):
            dlg_modal_rf.current.open = False
            page.update()

        dlg_modal_rf.current.title.value = "Confirmar Exclusão"
        dlg_modal_rf.current.content.value = (
            "Deseja excluir todos os itens do histórico?"
        )
        dlg_modal_rf.current.actions = [
            ft.TextButton("Sim", on_click=confirm_delete),
            ft.TextButton("Não", on_click=cancel_delete),
        ]
        dlg_modal_rf.current.open = True
        page.update()

    def undo_delete_all(e):
        for item in last_deleted_items:
            if storage:
                storage.save_download(item.get("id"), item)
        last_deleted_items.clear()
        update_history_view()

        from utils.ui_helpers import show_snackbar

        show_snackbar(page, "Exclusão desfeita.")

    def update_history_view(e=None):
        download_history = get_download_history()
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

        total_downloads = len(download_history)
        filtered_downloads = len(filtered_history)
        counts_text.value = (
            f"Total de downloads: {total_downloads} | Exibindo: {filtered_downloads}"
        )
        counts_text.update()

        page.update()

    excluir_tudo_button = ft.ElevatedButton(
        text="Excluir Tudo",
        icon=ft.Icons.DELETE_FOREVER,
        bgcolor=ft.Colors.ERROR,
        color=ft.Colors.ON_ERROR,
        on_click=delete_all,
    )

    atualizar_lista_button = ft.ElevatedButton(
        text="Atualizar Lista",
        icon=ft.Icons.UPDATE,
        bgcolor=ft.Colors.ON_PRIMARY_CONTAINER,
        color=ft.Colors.PRIMARY_CONTAINER,
        on_click=update_history_view,
    )

    search_field = ft.TextField(
        hint_text="Pesquisar...",
        on_change=update_history_view,
        ref=search_query,
        border_radius=8,
        content_padding=ft.padding.all(10),
    )

    sort_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("title", "Título"),
            ft.dropdown.Option("format", "Formato"),
        ],
        value="title",
        on_change=update_history_view,
        ref=sort_by,
    )

    download_history = get_download_history()
    history_grid = ft.GridView(
        controls=[render_download_item(item) for item in download_history],
        max_extent=240,
        child_aspect_ratio=0.75,
        spacing=10,
        expand=True,
    )

    dlg_modal = ft.AlertDialog(
        title=ft.Text(""),
        content=ft.Text(""),
        actions=[
            ft.TextButton(""),
            ft.TextButton(""),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        ref=dlg_modal_rf,
    )
    page.overlay.append(dlg_modal)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Histórico de Downloads", size=28, weight=ft.FontWeight.BOLD),
                counts_text,
                ft.Row(
                    controls=[
                        search_field,
                        sort_dropdown,
                        excluir_tudo_button,
                        atualizar_lista_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=2, color=ft.Colors.OUTLINE),
                ft.Container(
                    content=history_grid,
                    expand=True,
                ),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        ),
        padding=ft.padding.all(20),
    )

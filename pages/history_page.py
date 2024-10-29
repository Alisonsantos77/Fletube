import flet as ft
from utils.client_storage_utils import (
    recuperar_downloads_bem_sucedidos_client,
    salvar_downloads_bem_sucedidos_client,
    excluir_download_bem_sucedido_client,
    excluir_todos_downloads_bem_sucedidos_client,
)
# from utils.session_storage_utils import (
#     recuperar_downloads_bem_sucedidos_session,
#     salvar_downloads_bem_sucedidos_session,
#     excluir_download_bem_sucedido_session,
#     excluir_todos_downloads_bem_sucedidos_session,
# )

import logging
import os

logger = logging.getLogger(__name__)


def HistoryPage(page: ft.Page):
    download_history = recuperar_downloads_bem_sucedidos_client(page)
    search_query = ft.Ref[ft.TextField]()
    sort_by = ft.Ref[ft.Dropdown]()
    selected_items = set()  # Conjunto para armazenar IDs selecionados
    last_deleted_items = []  # Lista para armazenar itens excluídos temporariamente

    dlg_modal_rf = ft.Ref[ft.AlertDialog]()  # Definindo a referência para AlertDialog

    def render_download_item(item):
        item_id = item.get("id")
        file_path = item.get("file_path", "")
        if not item_id:
            logger.warning(f"Item sem ID encontrado: {item}")
            return ft.Container()

        # Funções para os botões
        # def open_folder(e):
        #     try:
        #         if os.path.exists(file_path):
        #             os.startfile(os.path.dirname(file_path))

        #             snack_bar = ft.SnackBar(
        #                 content=ft.Text("Abrindo local do arquivo."),
        #                 bgcolor=ft.colors.PRIMARY,
        #             )
        #             page.overlay.append(snack_bar)
        #             snack_bar.open = True
        #             page.update()
        #         else:
        #             logger.error(f"O caminho do arquivo não existe: {file_path}")
        #             snack_bar = ft.SnackBar(
        #                 content=ft.Text("Caminho do arquivo não encontrado."),
        #                 bgcolor=ft.colors.ERROR,
        #             )
        #             page.overlay.append(snack_bar)
        #             snack_bar.open = True
        #             page.update()
        #     except Exception as ex:
        #         logger.error(f"Erro ao abrir a pasta: {ex}")
        #         snack_bar = ft.SnackBar(
        #             content=ft.Text("Erro ao abrir a pasta."),
        #             bgcolor=ft.colors.ERROR,
        #         )
        #         page.overlay.append(snack_bar)
        #         snack_bar.open = True
        #         page.update()

        # def delete_from_device(e):
        #     try:
        #         if os.path.exists(file_path):
        #             os.remove(file_path)
        #             logger.info(f"Arquivo excluído: {file_path}")
        #             # Remove do armazenamento
        #             excluir_download_bem_sucedido_client(page, item_id)
        #             # Adiciona ao histórico de exclusões para possível desfazer
        #             last_deleted_items.append(item)
        #             # Atualiza a interface
        #             update_history_view()
        #             # Mostra SnackBar com opção de desfazer
        #             snack_bar = ft.SnackBar(
        #                 content=ft.Text("Arquivo excluído."),
        #                 bgcolor=ft.colors.ERROR,
        #                 actions=[
        #                     ft.TextButton(
        #                         "Desfazer", on_click=lambda e: undo_delete(e)
        #                     ),
        #                 ],
        #             )
        #             page.overlay.append(snack_bar)
        #             snack_bar.open = True
        #             page.update()
        #         else:
        #             logger.error(f"O caminho do arquivo não existe: {file_path}")
        #             snack_bar = ft.SnackBar(
        #                 content=ft.Text("Caminho do arquivo não encontrado."),
        #                 bgcolor=ft.colors.ERROR,
        #             )
        #             page.overlay.append(snack_bar)
        #             snack_bar.open = True
        #             page.update()
        #     except Exception as ex:
        #         logger.error(f"Erro ao excluir o arquivo: {ex}")
        #         snack_bar = ft.SnackBar(
        #             content=ft.Text("Erro ao excluir o arquivo."),
        #             bgcolor=ft.colors.ERROR,
        #         )
        #         page.overlay.append(snack_bar)
        #         snack_bar.open = True
        #         page.update()

        # def play_video(e):
        #     if os.path.exists(file_path):
        #         try:
        #             # Adiciona o controle de vídeo à sobreposição
        #             video_control = ft.Video(
        #                 src=file_path,
        #                 autoplay=True,
        #                 controls=True,
        #                 loop=False,
        #                 width=800,
        #                 height=450,
        #                 on_completed=lambda e: (
        #                     page.overlay.remove(video_control),
        #                     page.update(),
        #                 ),
        #             )
        #             page.overlay.append(video_control)
        #             snack_bar = ft.SnackBar(
        #                 content=ft.Text("Reproduzindo vídeo."),
        #                 bgcolor=ft.colors.ON_PRIMARY_CONTAINER,
        #             )
        #             page.overlay.append(snack_bar)
        #             snack_bar.open = True
        #             page.update()
        #         except Exception as ex:
        #             logger.error(f"Erro ao reproduzir o vídeo: {ex}")
        #             snack_bar = ft.SnackBar(
        #                 content=ft.Text("Erro ao reproduzir o vídeo."),
        #                 bgcolor=ft.colors.ERROR,
        #             )
        #             page.overlay.append(snack_bar)
        #             snack_bar.open = True
        #             page.update()
        #     else:
        #         logger.error(f"O caminho do arquivo não existe: {file_path}")
        #         snack_bar = ft.SnackBar(
        #             content=ft.Text("Caminho do arquivo não encontrado."),
        #             bgcolor=ft.colors.ERROR,
        #         )
        #         page.overlay.append(snack_bar)
        #         snack_bar.open = True
        #         page.update()

        # Função para alternar a seleção do item
        def toggle_selection(e):
            if item_id in selected_items:
                selected_items.remove(item_id)
            else:
                selected_items.add(item_id)
            checkbox.checked = item_id in selected_items
            page.update()

        # Função para deletar um item do histórico
        def delete_item(e, item_id=item_id, current_item=item):
            try:
                excluir_download_bem_sucedido_client(page, item_id)
                last_deleted_items.append(current_item)
                update_history_view()
                # Mostra SnackBar com opção de desfazer
                snack_bar = ft.SnackBar(
                    content=ft.Text("Item excluído."),
                    bgcolor=ft.colors.SURFACE,
                    action="Desfazer",
                )
                snack_bar.on_action = lambda e: undo_delete(e)
                page.overlay.append(snack_bar)
                snack_bar.open = True
                page.update()
            except Exception as ex:
                logger.error(f"Erro ao excluir o item: {ex}")
                snack_bar = ft.SnackBar(
                    content=ft.Text("Erro ao excluir o item."),
                    bgcolor=ft.colors.ERROR,
                )
                page.overlay.append(snack_bar)
                snack_bar.open = True
                page.update()

        def undo_delete(e):
            for deleted_item in last_deleted_items:
                salvar_downloads_bem_sucedidos_client(page, deleted_item)
                # salvar_downloads_bem_sucedidos_session(page, deleted_item)
            last_deleted_items.clear()
            update_history_view()
            snack_bar = ft.SnackBar(
                content=ft.Text("Exclusão desfeita."),
                bgcolor=ft.colors.PRIMARY_CONTAINER,
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()

        # Checkbox para multi-seleção
        checkbox = ft.Checkbox(
            value=item_id in selected_items,
            on_change=toggle_selection,
        )

        # Definindo a referência do container para animações de hover
        container_ref = ft.Ref[ft.Container]()

        # Novo estilo do card
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
                                    color=ft.colors.ON_SURFACE_VARIANT,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.icons.PLAY_ARROW,
                                            on_click=None,  # Desativar a função de clique
                                            tooltip="Em breve",
                                            icon_size=20,
                                            disabled=True,  # Desativar o botão
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.all(8)
                                            ),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.FOLDER_OPEN,
                                            on_click=None,  # Desativar a função de clique
                                            tooltip="Em breve",
                                            icon_size=20,
                                            disabled=True,  # Desativar o botão
                                            style=ft.ButtonStyle(
                                                padding=ft.padding.all(8)
                                            ),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE_OUTLINE,
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
                                            icon=ft.icons.DELETE,
                                            on_click=None,  # Desativar a função de clique
                                            tooltip="Em breve",
                                            icon_size=20,
                                            disabled=True,  # Desativar o botão
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
            bgcolor=ft.colors.SURFACE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
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
        download_history = recuperar_downloads_bem_sucedidos_client(page)
        if not download_history:
            snack_bar = ft.SnackBar(
                content=ft.Text("Nenhum item para excluir."),
                bgcolor=ft.colors.ERROR,
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
            return

        def confirm_delete(e):
            excluir_todos_downloads_bem_sucedidos_client(page)
            # excluir_todos_downloads_bem_sucedidos_session(page)
            last_deleted_items.extend(download_history)
            update_history_view()
            dlg_modal_rf.current.open = False
            # Mostra SnackBar com opção de desfazer
            snack_bar = ft.SnackBar(
                content=ft.Text("Todos os itens foram excluídos."),
                bgcolor=ft.colors.PRIMARY,
                action="Desfazer",
            )
            snack_bar.on_action = lambda e: undo_delete_all(
                e
            )  # Define a função de "Desfazer"
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
            salvar_downloads_bem_sucedidos_client(page, item)
            # salvar_downloads_bem_sucedidos_session(page, item)
        last_deleted_items.clear()
        update_history_view()
        snack_bar = ft.SnackBar(
            content=ft.Text("Exclusão desfeita."),
            bgcolor=ft.colors.PRIMARY_CONTAINER,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    def update_history_view(e=None):
        nonlocal download_history
        download_history = recuperar_downloads_bem_sucedidos_client(page)
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

    # Botão "Excluir Tudo"
    excluir_tudo_button = ft.ElevatedButton(
        text="Excluir Tudo",
        icon=ft.icons.DELETE_FOREVER,
        bgcolor=ft.colors.ERROR,
        color=ft.colors.ON_ERROR,
        on_click=delete_all,
    )

    # Botão "Atualizar Lista"
    atualizar_lista_button = ft.ElevatedButton(
        text="Atualizar Lista",
        icon=ft.icons.UPDATE,
        bgcolor=ft.colors.ON_PRIMARY_CONTAINER,
        color=ft.colors.PRIMARY_CONTAINER,
        on_click=update_history_view,
    )

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
        max_extent=240,
        child_aspect_ratio=0.75,
        spacing=10,
        expand=True,  # Expande o GridView para preencher o espaço disponível
    )

    # AlertDialog para confirmações
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

    # Layout da página de histórico
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Histórico de Downloads", size=28, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        search_field,
                        sort_dropdown,
                        excluir_tudo_button,
                        atualizar_lista_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=2, color=ft.colors.OUTLINE),
                ft.Container(
                    content=history_grid,
                    expand=True,  # Expande o Container que envolve o GridView
                ),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.START,
            expand=True,  # Expande o Column para preencher o espaço disponível
        ),
        padding=ft.padding.all(20),
    )

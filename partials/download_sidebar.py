import logging
import flet as ft

logger = logging.getLogger(__name__)


class SidebarList(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            padding=10,
            border_radius=ft.border_radius.all(10),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Downloads",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(thickness=2, color=ft.colors.BLUE_GREY_300),
                    ft.Column(
                        controls=[],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                        expand=True,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
        )
        self.items = {}
        self.title_control = self.content.controls[0]
        self.downloads_column = self.content.controls[2]
        logger.info("SidebarList inicializado.")

    def add_download_item(self, id, title, subtitle, thumbnail_url, file_path):
        """
        Adiciona um novo item de download à barra lateral com animação de opacidade.
        """
        # Criação inicial do item
        item = ft.ListTile(
            leading=ft.Container(
                content=ft.Image(
                    src=thumbnail_url,
                    width=50,
                    height=50,
                    fit=ft.ImageFit.COVER,
                ),
                width=50,
                height=50,
                border_radius=ft.border_radius.all(5),
                animate_opacity=500,
                opacity=1,  # Animação controlada sem delay
            ),
            title=ft.Text(
                value=title,
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.BLUE_GREY_800,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            subtitle=ft.Text(
                value=f"Formato: {subtitle}",
                size=14,
                color=ft.colors.BLUE_GREY_600,
            ),
            trailing=ft.Container(
                content=ft.Icon(name=ft.icons.INFO, color=ft.colors.BLUE_500),
                animate_opacity=500,
                opacity=1,  # Sem delay, controle direto
            ),
            data={"id": id, "status": "pending", "file_path": file_path},
            on_click=lambda e, id=id: self.on_item_click(id),
            animate_opacity=500,
            opacity=1,  # Visível sem delay
        )

        # Adiciona o item ao layout para garantir que ele esteja na página antes das atualizações
        self.items[id] = item
        self.downloads_column.controls.append(item)
        self.downloads_column.update()  # Garante que o item foi adicionado visualmente

        # Atualiza a contagem de downloads
        self.update_download_counts()
        logger.info(
            f"Item de download adicionado: ID: {id}, título: {title}, formato: {subtitle}, caminho: {file_path}"
        )

    def on_item_click(self, id):
        """
        Função de callback quando um item de download é clicado.
        """
        logger.info(f"Item clicado: ID {id}")

    def update_download_item(self, id, progress, status):
        """
        Atualiza o estado de um item de download com animação.
        """
        item = self.items.get(id)
        if item:
            if status == "downloading":
                # Verificar se o item está na página
                if not self.page or not item in self.page.controls:
                    logger.warning(
                        f"Tentativa de atualizar item que não está na página: ID {id}"
                    )
                    return
                item.trailing.content = ft.Text(
                    f"{progress*100:.2f}%", size=14, color=ft.colors.BLUE_700
                )
                item.data["status"] = "downloading"
            elif status == "finished":
                item.trailing.content = ft.Icon(
                    name=ft.icons.CHECK, color=ft.colors.GREEN
                )
                item.data["status"] = "finished"
            elif status == "error":
                item.trailing.content = ft.Icon(
                    name=ft.icons.ERROR, color=ft.colors.RED
                )
                item.data["status"] = "error"
            item.update()

            self.update_download_counts()
        else:
            logger.warning(
                f"Tentativa de atualizar item não existente na Sidebar: ID {id}"
            )

    def update_download_counts(self):
        """
        Atualiza a contagem de downloads concluídos e com erro.
        """
        total = len(self.items)
        errors = sum(
            1 for item in self.items.values() if item.data.get("status") == "error"
        )
        finished = sum(
            1 for item in self.items.values() if item.data.get("status") == "finished"
        )

        # Atualiza o título com animação de opacidade
        self.title_control.value = f"🟢 Concluídos: {finished} | 🔴 Falhas: {errors}"
        self.title_control.color = ft.colors.BLUE_GREY_900
        self.title_control.animate_opacity = 500
        self.title_control.update()

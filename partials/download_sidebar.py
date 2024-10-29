import logging
import flet as ft

logger = logging.getLogger(__name__)


class SidebarList(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text("Downloads", size=20, weight=ft.FontWeight.BOLD),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            ),
        )
        self.items = {}
        self.title_control = self.content.controls[0]
        logger.info("SidebarList inicializado.")

    def add_download_item(self, id, title, subtitle, thumbnail_url, file_path):
        item = ft.ListTile(
            leading=ft.Image(
                src=thumbnail_url,
                width=50,
                height=50,
                fit=ft.ImageFit.COVER,
            ),
            title=ft.Text(
                value=title,
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.PRIMARY,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            subtitle=ft.Text(
                value=f"Formato: {subtitle}",
                size=14,
                color=ft.colors.PRIMARY,
            ),
            trailing=ft.Text("0%"),
            data={"id": id, "status": "pending", "file_path": file_path},
        )

        self.items[id] = item
        self.content.controls.append(item)
        self.update()
        logger.info(
            f"Item de download adicionado: ID: {id}, título: {title}, formato: {subtitle}, caminho: {file_path}"
        )
        self.update_download_counts()

    def update_download_item(self, id, progress, status):
        item = self.items.get(id)
        if item:
            if status == "downloading":
                item.trailing = ft.Text(f"{progress*100:.2f}%")
                item.data["status"] = "downloading"
            elif status == "finished":
                item.trailing = ft.Icon(name=ft.icons.CHECK, color=ft.colors.GREEN)
                item.data["status"] = "finished"
            elif status == "error":
                item.trailing = ft.Icon(name=ft.icons.ERROR, color=ft.colors.RED)
                item.data["status"] = "error"
            self.update()
            self.update_download_counts()
        else:
            logger.warning(
                f"Tentativa de atualizar item não existente na Sidebar: ID {id}"
            )

    def update_download_counts(self):
        total = len(self.items)
        downloading = sum(
            1
            for item in self.items.values()
            if item.data.get("status") == "downloading"
        )
        errors = sum(
            1 for item in self.items.values() if item.data.get("status") == "error"
        )
        finished = sum(
            1 for item in self.items.values() if item.data.get("status") == "finished"
        )

        self.title_control.value = f"{downloading} baixando, {errors} com erro, {finished} concluídos de {total}"
        self.title_control.update()

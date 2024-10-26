import logging
import flet as ft

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class SidebarList(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            content=ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            ),
        )
        self.items = self.content.controls
        logger.info("SidebarList inicializado.")

    def add_download_item(self, id, title, subtitle, thumbnail_url):
        item = ft.ListTile(
            leading=ft.Image(
                src=thumbnail_url,
                width=50,
                height=50,
                fit=ft.ImageFit.COVER,
            ),
            title=ft.Text(
                value=f"{title}",
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
            data=id,
        )

        self.items.append(item)
        self.update()
        logger.info(
            f"Item de download adicionado: ID: {id}, título: {title}, formato: {subtitle}"
        )


class ItemDownloading(ft.Card):
    def __init__(
        self,
        id: str,
        title: str,
        subtitle: str,
        thumbnail_url: str,
        format: str = "MP4",
        has_error: bool = False,
    ):
        super().__init__()

        self.id = id
        self.thumbnail = thumbnail_url
        self.title = title
        self.format = format

        icon_to_use = "/images/logo.png" if not has_error else ft.icons.CLOSE
        icon_widget = (
            ft.Image(src=icon_to_use, width=30, height=30, fit=ft.ImageFit.CONTAIN)
            if not has_error
            else ft.Icon(name=icon_to_use, color=ft.colors.RED, size=30)
        )

        self.elevation = 4
        self.bgcolor = ft.colors.PRIMARY
        self.color = ft.colors.PRIMARY
        self.shape = ft.RoundedRectangleBorder(radius=8)
        self.margin = ft.margin.symmetric(vertical=6, horizontal=10)

        self.content = ft.ListTile(
            leading=ft.Image(
                src=self.thumbnail,
                width=45,
                height=45,
                fit=ft.ImageFit.COVER,
            ),
            title=ft.Text(
                value=f"{self.title}",
                size=16,
                weight=ft.FontWeight.NORMAL,
                color=ft.colors.PRIMARY,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            subtitle=ft.Text(
                value=f"Formato: {self.format}",
                size=12,
                color=ft.colors.PRIMARY,
            ),
            trailing=icon_widget,
            data=self.id,
        )
        logger.info(f"ItemDownloading criado: ID: {self.id}, título: {self.title}")

import logging
import flet as ft

# Configure logging para este módulo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class SidebarList(ft.Container):
    """
    Representa a lista da barra lateral que contém todos os itens de download finalizados.
    """

    def __init__(self):
        super().__init__(
            expand=True,
            content=ft.Column(
                controls=[],  # Lista de controles para exibir os downloads finalizados
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            ),
        )
        self.items = self.content.controls
        logger.info("SidebarList inicializado.")

    def add_download_item(self, title, subtitle, thumbnail_url):
        """
        Adiciona um novo item de download à barra lateral.

        Args:
            title (str): O título do item de download.
            subtitle (str): O subtítulo ou formato do download.
            thumbnail_url (str): A URL da imagem de thumbnail.
        """
        # Criando o item de download finalizado
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
                color=ft.colors.ON_PRIMARY,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            subtitle=ft.Text(
                value=f"Formato: {subtitle}",
                size=14,
                color=ft.colors.ON_SECONDARY,
            ),
        )

        self.items.append(item)
        self.update()
        logger.info(f"Item de download adicionado: {title}, formato: {subtitle}")


class ItemDownloading(ft.Card):
    def __init__(
        self,
        title: str,
        subtitle: str,
        thumbnail: str,
        format: str = "MP4",
        has_error: bool = False,
    ):
        super().__init__()

        self.thumbnail = thumbnail
        self.title = title
        self.format = format

        # Ícone baseado em erro
        icon_to_use = "/images/logo.png" if not has_error else ft.icons.CLOSE
        icon_widget = (
            ft.Image(src=icon_to_use, width=30, height=30, fit=ft.ImageFit.CONTAIN)
            if not has_error
            else ft.Icon(name=icon_to_use, color=ft.colors.RED, size=30)
        )

        # Propriedades do Card
        self.elevation = 4  
        self.bgcolor = ft.colors.SURFACE  
        self.color = ft.colors.SURFACE_VARIANT
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
                color=ft.colors.ON_SURFACE, 
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            subtitle=ft.Text(
                value=f"Formato: {self.format}",
                size=12,
                color=ft.colors.ON_SURFACE_VARIANT,
            ),
            trailing=icon_widget,
        )
        logger.info(f"ItemDownloading criado: {self.title}")

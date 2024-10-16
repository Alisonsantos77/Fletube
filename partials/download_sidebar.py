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
    Representa a lista da barra lateral que contém todos os itens de download.
    """

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

    def add_download_item(self, title, subtitle, thumbnail_url, duration, progress=0.0):
        """
        Adiciona um novo item de download à barra lateral.

        Args:
            title (str): O título do item de download.
            subtitle (str): O subtítulo ou formato do download.
            thumbnail_url (str): A URL da imagem de thumbnail.
            duration (str): A duração do vídeo.
            progress (float): O progresso inicial do download.
        """
        item = ItemDownloading(
            title=title,
            subtitle=subtitle,
            thumbnail=thumbnail_url,
            duration=duration,
            progress=progress,
        )
        self.items.append(item)
        self.update()
        logger.info(
            f"Item de download adicionado: {title}, formato: {subtitle}, duração: {duration}"
        )

    def update_progress(self, index, progress):
        """
        Atualiza o progresso de um item de download específico.

        Args:
            index (int): O índice do item de download na barra lateral.
            progress (float): O novo valor de progresso (0.0 a 1.0).
        """
        if index < len(self.items):
            item = self.items[index]
            item.update_progress(progress)
            item.update()
            logger.info(
                f"Progresso atualizado para o item {index}: {progress*100:.2f}%"
            )
        else:
            logger.warning(
                f"Tentativa de atualizar progresso para índice inválido: {index}"
            )


class ItemDownloading(ft.Card):
    """
    Representa um item individual de download dentro da barra lateral.
    Armazena informações como thumbnail, título, duração, ícone, barra de progresso e formato.
    """

    def __init__(
        self,
        title: str,
        subtitle: str,
        thumbnail: str,
        duration: str,  
        progress: float = 0.0,
        format: str = "MP4",  
        has_error: bool = False,
    ):
        super().__init__()

        # Armazenar as informações no objeto
        self.thumbnail = thumbnail
        self.title = title
        self.duration = duration
        self.format = format
        self.progress_value = progress

        self.progress_bar = ft.ProgressBar(
            value=self.progress_value,
            bgcolor=ft.colors.GREY_300,
            color=self.get_progress_color(self.progress_value),
            width=300,
            height=8,
        )

        icon_to_use = "/images/logo.png" if not has_error else ft.icons.CLOSE
        icon_widget = (
            ft.Image(src=icon_to_use, width=30, height=30, fit=ft.ImageFit.CONTAIN)
            if not has_error
            else ft.Icon(name=icon_to_use, color=ft.colors.RED, size=30)
        )

        # Configura propriedades do Card
        self.elevation = 4
        self.color = ft.colors.BLUE_GREY_50
        self.shape = ft.RoundedRectangleBorder(radius=10)
        self.margin = ft.margin.symmetric(vertical=8, horizontal=12)

        self.content = ft.ListTile(
            leading=ft.Image(
                src=self.thumbnail,
                width=50,
                height=50,
                fit=ft.ImageFit.COVER,
            ),
            title=ft.Text(
                value=f"{self.title} - {self.duration}",  
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.BLACK,
                max_lines=1,  
                overflow=ft.TextOverflow.ELLIPSIS, 
            ),
            subtitle=ft.Text(
                value=f"Formato: {self.format}", size=14, color=ft.colors.GREY_700
            ),
            trailing=icon_widget,
            bottom=self.progress_bar,
        )

        logger.info(f"ItemDownloading criado: {self.title} - {self.duration}")

    def get_progress_color(self, progress):
        """
        Determina a cor da barra de progresso com base no progresso atual.

        Args:
            progress (float): O valor atual de progresso (0.0 a 1.0).

        Returns:
            str: O código de cor para a barra de progresso.
        """
        if progress > 0.7:
            return ft.colors.GREEN
        elif progress > 0.3:
            return ft.colors.BLUE
        else:
            return ft.colors.RED

    def update_progress(self, progress):
        """
        Atualiza o valor e a cor da barra de progresso.

        Args:
            progress (float): O novo valor de progresso (0.0 a 1.0).
        """
        self.progress_bar.value = progress
        self.progress_bar.color = self.get_progress_color(progress)
        self.progress_bar.update()
        logger.info(f"Progresso atualizado para {progress*100:.2f}%")


def sidebar_list():
    """
    Função fábrica para criar uma nova instância de SidebarList.

    Returns:
        SidebarList: Uma nova instância de SidebarList.
    """
    return SidebarList()

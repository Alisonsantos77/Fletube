import flet as ft


def sidebar_list():
    items = []

    class ItemDownloading(ft.Card):
        def __init__(
            self,
            title: str,
            subtitle: str,
            icon: str,
            icon_color: str,
            progress: float,
            thumbnail: str,
            has_error: bool = False,
        ):
            super().__init__()

            if progress > 0.7:
                progress_color = ft.colors.GREEN
            elif progress > 0.3:
                progress_color = ft.colors.BLUE
            else:
                progress_color = ft.colors.RED

            # Configurando propriedades do Card
            self.elevation = 4
            self.color = ft.colors.BLUE_GREY_50
            self.shape = ft.RoundedRectangleBorder(radius=10)
            self.margin = ft.margin.symmetric(vertical=8, horizontal=12)

            icon_to_use = (
                "/images/icone-fletube.png" if not has_error else ft.icons.CLOSE
            )
            icon_widget = (
                ft.Image(src=icon_to_use, width=30, height=30, fit=ft.ImageFit.CONTAIN)
                if not has_error
                else ft.Icon(name=icon_to_use, color=ft.colors.RED, size=30)
            )

            self.content = ft.ListTile(
                leading=ft.Image(
                    src=thumbnail,
                    width=50,
                    height=50,
                    fit=ft.ImageFit.COVER,
                ),
                title=ft.Text(
                    value=title,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLACK,
                ),
                subtitle=ft.Text(value=subtitle, size=14, color=ft.colors.GREY_700),
                trailing=icon_widget,
            )

            self.progress_bar = ft.ProgressBar(
                value=progress,
                bgcolor=ft.colors.GREY_300,
                color=progress_color,
                width=300,
                height=8,
            )

            # Contêiner para o conteúdo e barra de progresso
            self.container = ft.Column(
                controls=[self.content, self.progress_bar],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
            )

            # Define o container principal do Card
            self.content = self.container

    for i in range(1, 16):
        has_error = i % 5 == 0
        items.append(
            ItemDownloading(
                title=f"Item {i}",
                subtitle=f"Subtítulo do Item {i}",
                icon=ft.icons.DOWNLOADING,
                icon_color=ft.colors.BLUE,
                progress=i * 0.05,
                thumbnail=f"https://img.youtube.com/vi/{i}/hqdefault.jpg",
                has_error=has_error,
            )
        )

    return ft.Container(
        expand=True,
        content=ft.Column(
            controls=items,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        ),
    )

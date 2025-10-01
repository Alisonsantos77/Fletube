import logging
import flet as ft

logger = logging.getLogger(__name__)


class SidebarList(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page

        super().__init__(
            expand=True,
            padding=10,
            border_radius=ft.border_radius.all(10),
            content=ft.Column(
                controls=[
                    ft.Text(
                        value=f"✅ Concluídos: {0} | ❌ Falhas: {
                            0} | 📊 Total: {0} ",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900,
                        text_align=ft.TextAlign.CENTER,
                        key="downloads_title",
                    ),
                    ft.Divider(thickness=2, color=ft.Colors.BLUE_GREY_300),
                    ft.Column(
                        controls=[],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                        expand=True,
                        key="downloads_column",
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                expand=True,
            ),
            key="sidebar_container",
        )

        self.items = {}
        self.title_control = self.content.controls[0]
        self.downloads_column = self.content.controls[2]

        self.mounted = True
        logger.info("SidebarList inicializado e montado.")

        self.update_title_color()

    def update_title_color(self):
        """Atualiza a cor do título baseado no tema armazenado no client storage."""
        if self.page:
            theme_mode = self.page.client_storage.get("theme_mode", "light")
            self.title_control.color = ft.Colors.BLUE_700 if theme_mode == "light" else ft.Colors.WHITE
            self.title_control.animate_opacity = 500
            self.title_control.update()
        else:
            logger.warning(
                "self.page ainda não está inicializado. Adiando atualização da cor do título.")

    def on_unmount(self, e=None):
        """Callback quando o SidebarList é desmontado."""
        self.mounted = False
        logger.info("SidebarList desmontado.")

    def add_download_item(self, id, title, subtitle, thumbnail_url, file_path):
        """Adiciona um novo item de download à barra lateral com animação de opacidade."""
        if not self.mounted:
            print(f"A SidebarList está tirando uma folga! Tentaremos adicionar o item '{
                  title}' quando ela voltar ao trabalho.")
            return

        # Criação inicial do item
        item = ft.ListTile(
            leading=ft.Container(
                content=ft.Image(src=thumbnail_url, width=50,
                                 height=50, fit=ft.ImageFit.COVER),
                width=50, height=50, border_radius=ft.border_radius.all(5), animate_opacity=500, opacity=1,
            ),
            title=ft.Text(value=title, size=18, weight=ft.FontWeight.BOLD,
                          color=ft.Colors.LIGHT_BLUE_800, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            subtitle=ft.Text(value=f"Formato: {
                             subtitle}", size=14, color=ft.Colors.LIGHT_BLUE_600),
            trailing=ft.Container(content=ft.Icon(
                name=ft.Icons.INFO, color=ft.Colors.BLUE_500), animate_opacity=500, opacity=1),
            data={"id": id, "status": "pending", "file_path": file_path},
            on_click=lambda e, id=id: self.on_item_click(id),
            animate_opacity=500,
            opacity=1,
        )

        self.items[id] = item
        self.downloads_column.controls.append(item)
        self.downloads_column.update()

        # Atualiza a contagem de downloads
        self.update_download_counts()

        logger.info(f"Item de download adicionado: ID: {id}, título: {
                    title}, formato: {subtitle}, caminho: {file_path}")

    def on_item_click(self, id):
        """Função de callback quando um item de download é clicado."""
        logger.info(f"Item clicado: ID {id}")

    def update_download_item(self, id, progress, status):
        """Atualiza o estado de um item de download com animação."""
        if not self.mounted:
            print(f"A SidebarList está ausente! O item '{
                  id}' será atualizado na próxima oportunidade.")
            return

        item = self.items.get(id)
        if item:
            try:
                if status == "downloading":
                    item.trailing.content = ft.Text(
                        f"{progress*100:.2f}%", size=14, color=ft.Colors.BLUE_700)
                    item.data["status"] = "downloading"
                elif status == "converting":
                    item.trailing.content = ft.Text(
                        f"{progress*100:.2f}%", size=14, color=ft.Colors.BLUE_700)
                    item.data["status"] = "converting"
                elif status == "pending":
                    item.trailing.content = ft.Icon(
                        name=ft.Icons.INFO, color=ft.Colors.BLUE_500)
                    item.data["status"] = "pending"
                    item.trailing.content.value = "📥 "
                elif status == "finished":
                    item.trailing.content = ft.Icon(
                        name=ft.Icons.CHECK, color=ft.Colors.GREEN)
                    item.data["status"] = "finished"
                elif status == "error":
                    item.trailing.content = ft.Icon(
                        name=ft.Icons.ERROR, color=ft.Colors.RED)
                    item.data["status"] = "error"
                item.update()

                self.update_download_counts()
            except Exception as e:
                print(f"vish... deu ruim: {e}")
        else:
            print(f"Oops! Parece que o item '{
                  id}' ainda não foi adicionado à SidebarList.")

    def update_download_counts(self):
        """Atualiza a contagem de downloads concluídos e com erro."""

        total = len(self.items)

        errors = sum(1 for item in self.items.values()
                     if item.data.get("status") == "error")

        finished = sum(1 for item in self.items.values()
                       if item.data.get("status") == "finished")

        # Atualiza o título com as contagens (finalizados, falhas e total)
        self.title_control.value = f"✅ Concluídos: {
            finished} | ❌ Falhas: {errors} | 📊 Total: {total}"
        self.title_control.color = ft.Colors.BLUE_700
        self.title_control.animate_opacity = 500
        self.title_control.update()

    def refresh_downloads(self, downloads):
        """Atualiza toda a lista de downloads com base no estado atual."""
        if not self.mounted:
            print(
                "A SidebarList está tirando uma pausa. Vamos atualizar os downloads quando ela voltar!")
            return

        try:
            # Limpa os controles existentes
            self.downloads_column.controls.clear()
            self.items.clear()

            # Adiciona novamente os itens com base nos downloads atuais
            for download_id, dados in downloads.items():
                self.add_download_item(
                    id=download_id,
                    title=dados.get("title", "Título Indisponível"),
                    subtitle=dados.get("format", "Formato Indisponível"),
                    thumbnail_url=dados.get("thumbnail", "/images/logo.png"),
                    file_path=dados.get("file_path", ""),
                )

            self.update_download_counts()
            self.update()
        except Exception as e:
            logger.error(f"Erro ao refrescar a lista de downloads: {e}")

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
                        value=f"✅ Concluídos: {0} | ❌ Falhas: {0} | 📊 Total: {0} ",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900,
                        text_align=ft.TextAlign.CENTER,
                        key="downloads_title",
                    ),
                    ft.Divider(thickness=2, color=ft.Colors.BLUE_GREY_300),
                    ft.Container(
                        height=500,
                        content=ft.Column(
                            controls=[],
                            scroll=ft.ScrollMode.AUTO,
                            spacing=10,
                            key="downloads_column",
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=10,
                expand=False,
            ),
            key="sidebar_container",
        )

        self.items = {}
        self.title_control = self.content.controls[0]
        self.downloads_column = self.content.controls[2].content

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

    def add_download_item(self, id, title, subtitle, thumbnail_url, file_path, download_manager=None):
        """Adiciona um novo item de download à barra lateral."""
        if not self.mounted:
            print(
                f"A SidebarList está tirando uma folga! Tentaremos adicionar o item '{title}' quando ela voltar ao trabalho.")
            return

        status_text = ft.Text("🔥 Aguardando...", size=14,
                              color=ft.Colors.BLUE_500)

        cancel_btn = ft.IconButton(
            icon=ft.Icons.CANCEL,
            icon_color=ft.Colors.RED_400,
            icon_size=20,
            tooltip="Cancelar download",
            visible=False,
            on_click=lambda e, did=id, dm=download_manager: self.cancel_download(
                did, dm)
        )

        item = ft.ListTile(
            leading=ft.Container(
                content=ft.Image(src=thumbnail_url, width=50,
                                 height=50, fit=ft.ImageFit.COVER),
                width=50, height=50, border_radius=ft.border_radius.all(5), animate_opacity=500, opacity=1,
            ),
            title=ft.Text(value=title, size=18, weight=ft.FontWeight.BOLD,
                          color=ft.Colors.LIGHT_BLUE_800, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            subtitle=ft.Text(
                value=f"Formato: {subtitle}", size=14, color=ft.Colors.LIGHT_BLUE_600),
            trailing=ft.Row([status_text, cancel_btn], spacing=5, tight=True),
            data={"id": id, "status": "pending", "file_path": file_path,
                  "download_manager": download_manager, "cancel_btn": cancel_btn},
            on_click=lambda e, id=id: self.on_item_click(id),
            animate_opacity=500,
            opacity=1,
        )

        self.items[id] = item
        self.downloads_column.controls.append(item)
        self.downloads_column.update()

        self.update_download_counts()

        logger.info(
            f"Item de download adicionado: ID: {id}, título: {title}, formato: {subtitle}, caminho: {file_path}")

    def on_item_click(self, id):
        """Função de callback quando um item de download é clicado."""
        logger.info(f"Item clicado: ID {id}")

    def cancel_download(self, download_id, download_manager):
        """Cancela um download em andamento."""
        if download_manager:
            download_manager.cancel_download(download_id)
            logger.info(f"Cancelamento solicitado para download {download_id}")
        else:
            logger.warning("DownloadManager não disponível para cancelamento")

    def update_download_item(self, id, progress, status):
        if not self.mounted:
            print(
                f"A SidebarList está ausente! O item '{id}' será atualizado na próxima oportunidade.")
            return

        item = self.items.get(id)
        if item:
            try:
                trailing_row = item.trailing
                status_text = trailing_row.controls[0]
                cancel_btn = trailing_row.controls[1]

                if status == "downloading":
                    progress_percent = min(progress * 100, 100.0)
                    status_text.value = f"🔥 {progress_percent:.1f}%"
                    status_text.color = ft.Colors.BLUE_700
                    cancel_btn.visible = True
                    item.data["status"] = "downloading"
                elif status == "converting":
                    progress_percent = min(progress * 100, 100.0)
                    status_text.value = f"🔄 {progress_percent:.1f}%"
                    status_text.color = ft.Colors.ORANGE_700
                    cancel_btn.visible = True
                    item.data["status"] = "converting"
                elif status == "pending":
                    status_text.value = "🔥 Aguardando..."
                    status_text.color = ft.Colors.BLUE_500
                    cancel_btn.visible = False
                    item.data["status"] = "pending"
                elif status == "finished":
                    status_text.value = "✅ Concluído"
                    status_text.color = ft.Colors.GREEN
                    cancel_btn.visible = False
                    item.data["status"] = "finished"
                elif status == "error":
                    status_text.value = "❌ Erro"
                    status_text.color = ft.Colors.RED
                    cancel_btn.visible = False
                    item.data["status"] = "error"
                elif status == "cancelled":
                    status_text.value = "🚫 Cancelado"
                    status_text.color = ft.Colors.RED
                    cancel_btn.visible = False
                    item.data["status"] = "cancelled"

                item.update()
                self.update_download_counts()
            except Exception as e:
                logger.error(f"Erro ao atualizar item de download: {e}")
        else:
            logger.warning(f"Item '{id}' não encontrado na SidebarList.")

    def update_download_counts(self):
        """Atualiza a contagem de downloads concluídos e com erro."""

        total = len(self.items)

        errors = sum(1 for item in self.items.values()
                     if item.data.get("status") == "error")

        finished = sum(1 for item in self.items.values()
                       if item.data.get("status") == "finished")

        self.title_control.value = f"✅ Concluídos: {finished} | ❌ Falhas: {errors} | 📊 Total: {total}"
        self.title_control.color = ft.Colors.BLUE_700
        self.title_control.animate_opacity = 500
        self.title_control.update()

    def refresh_downloads(self, downloads, download_manager=None):
        """Atualiza toda a lista de downloads com base no estado atual."""
        if not self.mounted:
            print(
                "A SidebarList está tirando uma pausa. Vamos atualizar os downloads quando ela voltar!")
            return

        try:
            self.downloads_column.controls.clear()
            self.items.clear()

            for download_id, dados in downloads.items():
                self.add_download_item(
                    id=download_id,
                    title=dados.get("title", "Título Indisponível"),
                    subtitle=dados.get("format", "Formato Indisponível"),
                    thumbnail_url=dados.get("thumbnail", "/images/logo.png"),
                    file_path=dados.get("file_path", ""),
                    download_manager=download_manager
                )

            self.update_download_counts()
            self.update()
        except Exception as e:
            logger.error(f"Erro ao refrescar a lista de downloads: {e}")

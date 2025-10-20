import flet as ft
from loguru import logger


class SidebarList(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page

        super().__init__(
            expand=True,
            padding=10,
            border_radius=ft.border_radius.all(10),
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                value=f"✅ Concluídos: {0} | ❌ Falhas: {0} | 📊 Total: {0} ",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_SURFACE,
                                text_align=ft.TextAlign.CENTER,
                                key="downloads_title",
                            ),
                        ],
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
        self.title_control = self.content.controls[0].controls[0]
        self.downloads_column = self.content.controls[2].content

        self.mounted = True
        logger.info("✅ SidebarList inicializado e montado.")

    def on_unmount(self, e=None):
        self.mounted = False
        logger.info("⚠️ SidebarList desmontado.")

    def add_download_item(
        self, id, title, subtitle, thumbnail_url, file_path, download_manager=None
    ):
        if not self.mounted:
            logger.warning(f"⚠️ Sidebar desmontada, ignorando adição: {title}")
            return

        status_text = ft.Text(
            "📥 Aguardando...",
            size=14,
            color=ft.Colors.BLUE_500,
            animate_opacity=300,
            key=f"status_{id}",
        )

        cancel_btn = ft.IconButton(
            icon=ft.Icons.CANCEL,
            icon_color=ft.Colors.RED_400,
            icon_size=20,
            tooltip="Cancelar download",
            visible=False,
            on_click=lambda e, did=id, dm=download_manager: self.cancel_download(
                did, dm
            ),
            animate_opacity=300,
        )

        thumbnail_container = ft.Container(
            content=ft.Image(
                src=thumbnail_url,
                width=50,
                height=50,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(5),
            ),
            width=50,
            height=50,
            border_radius=ft.border_radius.all(5),
            animate_opacity=300,
            opacity=1,
        )

        item = ft.ListTile(
            leading=thumbnail_container,
            title=ft.Text(
                value=title,
                size=18,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.LIGHT_BLUE_800,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            subtitle=ft.Text(
                value=f"Formato: {subtitle}",
                size=14,
                color=ft.Colors.LIGHT_BLUE_600,
            ),
            trailing=ft.Row(
                [status_text, cancel_btn],
                spacing=5,
                tight=True,
            ),
            data={
                "id": id,
                "status": "pending",
                "file_path": file_path,
                "download_manager": download_manager,
                "cancel_btn": cancel_btn,
                "status_text": status_text,
                "thumbnail_container": thumbnail_container,
            },
            on_click=lambda e, item_id=id: self.on_item_click(item_id),
            animate_opacity=300,
            opacity=1,
        )

        self.items[id] = item
        self.downloads_column.controls.append(item)

        try:
            self.downloads_column.update()
        except Exception as e:
            logger.error(f"Erro ao atualizar UI após adicionar item: {e}")

        self.update_download_counts()
        logger.info(f"➕ Download adicionado: {title[:30]}... ({subtitle})")

    def on_item_click(self, id):
        logger.info(f"🖱️ Item clicado: ID {id}")

    def cancel_download(self, download_id, download_manager):
        if download_manager:
            download_manager.cancel_download(download_id)
            logger.info(f"🚫 Cancelamento solicitado: {download_id}")
        else:
            logger.warning("⚠️ DownloadManager não disponível")

    def update_download_item(
        self,
        id,
        progress,
        status,
        downloaded_bytes=None,
        total_bytes=None,
        speed=None,
        eta=None,
    ):
        if not self.mounted:
            logger.warning(f"⚠️ Sidebar desmontada, ignorando atualização: {id}")
            return

        item = self.items.get(id)
        if not item:
            logger.warning(f"⚠️ Item não encontrado: {id}")
            return

        try:
            status_text = item.data.get("status_text")
            cancel_btn = item.data.get("cancel_btn")

            if not status_text or not cancel_btn:
                trailing_row = item.trailing
                status_text = trailing_row.controls[0]
                cancel_btn = trailing_row.controls[1]

            if status == "downloading":
                progress_percent = min(progress * 100, 100.0)

                if downloaded_bytes and total_bytes:
                    total_mb = total_bytes / (1024 * 1024)
                    status_text.value = (
                        f"📥 {progress_percent:.1f}% de {total_mb:.2f}MiB"
                    )
                elif speed:
                    speed_mb = speed / (1024 * 1024)
                    if eta:
                        status_text.value = f"📥 {progress_percent:.1f}% • {speed_mb:.2f}MiB/s • ETA {eta}"
                    else:
                        status_text.value = (
                            f"📥 {progress_percent:.1f}% • {speed_mb:.2f}MiB/s"
                        )
                else:
                    status_text.value = f"📥 {progress_percent:.1f}%"

                status_text.color = ft.Colors.BLUE_700
                cancel_btn.visible = True
                item.data["status"] = "downloading"

            elif status == "converting":
                progress_percent = min(progress * 100, 100.0)
                status_text.value = f"🔄 Convertendo... {progress_percent:.0f}%"
                status_text.color = ft.Colors.ORANGE_700
                cancel_btn.visible = False
                item.data["status"] = "converting"

            elif status == "merging":
                status_text.value = "🔄 Mesclando..."
                status_text.color = ft.Colors.ORANGE_700
                cancel_btn.visible = False
                item.data["status"] = "merging"

            elif status == "pending":
                status_text.value = "📥 Aguardando..."
                status_text.color = ft.Colors.BLUE_500
                cancel_btn.visible = False
                item.data["status"] = "pending"

            elif status == "finished":
                status_text.value = "✅ Concluído"
                status_text.color = ft.Colors.GREEN
                cancel_btn.visible = False
                item.data["status"] = "finished"

                thumbnail_container = item.data.get("thumbnail_container")
                if thumbnail_container:
                    thumbnail_container.opacity = 0.8
                    thumbnail_container.update()

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
                item.opacity = 0.5

            try:
                item.update()
            except Exception as update_error:
                logger.error(f"Erro ao atualizar item: {update_error}")

            if status in ["finished", "error", "cancelled"]:
                self.update_download_counts()

        except Exception as e:
            logger.error(f"❌ Erro ao atualizar item {id}: {e}")

    def update_download_counts(self):
        try:
            total = len(self.items)
            errors = sum(
                1 for item in self.items.values() if item.data.get("status") == "error"
            )
            finished = sum(
                1
                for item in self.items.values()
                if item.data.get("status") == "finished"
            )

            self.title_control.value = (
                f"✅ Concluídos: {finished} | ❌ Falhas: {errors} | 📊 Total: {total}"
            )

            if self.page:
                try:
                    storage = self.page.session.get("app_storage")
                    if storage:
                        theme_mode = storage.get_setting("theme_mode", "light")
                    else:
                        theme_mode = "light"

                    self.title_control.color = (
                        ft.Colors.BLUE_700 if theme_mode == "light" else ft.Colors.WHITE
                    )
                except Exception as e:
                    logger.error(f"Erro ao obter tema: {e}")
                    self.title_control.color = ft.Colors.BLUE_700

            try:
                self.title_control.update()
            except Exception as e:
                logger.error(f"Erro ao atualizar título: {e}")

        except Exception as e:
            logger.error(f"Erro ao atualizar contadores: {e}")

    def refresh_downloads(self, downloads, download_manager=None):
        if not self.mounted:
            logger.warning("⚠️ Sidebar desmontada, ignorando refresh")
            return

        try:
            self.downloads_column.controls.clear()
            self.items.clear()

            for download_id, dados in downloads.items():
                self.add_download_item(
                    id=download_id,
                    title=dados.get("title", "Título Indisponível"),
                    subtitle=dados.get("format", "Formato Indisponível"),
                    thumbnail_url=dados.get("thumbnail", "/images/thumb_broken.jpg"),
                    file_path=dados.get("file_path", ""),
                    download_manager=download_manager,
                )

            self.update_download_counts()
            try:
                self.update()
            except:
                pass

            logger.info(f"🔄 Sidebar atualizada: {len(downloads)} downloads")

        except Exception as e:
            logger.error(f"❌ Erro ao refresh downloads: {e}")

    def clear_finished_downloads(self):
        if not self.mounted:
            return

        try:
            finished_ids = [
                item_id
                for item_id, item in self.items.items()
                if item.data.get("status") == "finished"
            ]

            for item_id in finished_ids:
                item = self.items[item_id]
                self.downloads_column.controls.remove(item)
                del self.items[item_id]

            self.update_download_counts()
            self.update()

            logger.info(f"🧹 {len(finished_ids)} downloads finalizados removidos")

        except Exception as e:
            logger.error(f"Erro ao limpar downloads: {e}")

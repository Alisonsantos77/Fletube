
from utils.client_storage_utils import (
    salvar_downloads_bem_sucedidos_client,
    salvar_downloads_ativos_client,
    recuperar_downloads_ativos_client
)
import threading
import uuid
import logging
from services.dlp_service import start_download
import flet as ft
logger = logging.getLogger(__name__)


class DownloadManager:
    def __init__(self, page, max_downloads=3):
        self.downloads = {}
        self.lock = threading.Lock()
        self.page = page
        self.max_downloads = max_downloads
        self.semaphore = threading.Semaphore(self.max_downloads)
        self.active_downloads = 0
        self.cancelled_downloads = set()
        self.download_threads = {}

        self.carregar_downloads_ativos()

    def carregar_downloads_ativos(self):
        try:
            downloads_ativos = recuperar_downloads_ativos_client(self.page)
            self.downloads.update(downloads_ativos)
            logger.info(
                f"Carregados {len(downloads_ativos)} downloads ativos do client_storage")
        except Exception as e:
            logger.error(f"Erro ao carregar downloads ativos: {e}")

    def salvar_downloads_ativos(self):
        try:
            salvar_downloads_ativos_client(self.page, self.downloads)
        except Exception as e:
            logger.error(f"Erro ao salvar downloads ativos: {e}")

    def iniciar_download(self, link, formato, diretorio, sidebar, page):
        if not self.semaphore.acquire(blocking=False):
            snack = ft.Snackbar(
                message="Limite de downloads simultâneos atingido.", timeout=5000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
            logger.info("Limite de downloads simultâneos atingido.")
            return

        self.sidebar = sidebar

        download_id = str(uuid.uuid4())
        thread = threading.Thread(
            target=self.download_thread,
            args=(link, formato, diretorio, download_id, sidebar),
            daemon=True,
        )

        with self.lock:
            self.download_threads[download_id] = thread

        thread.start()

    def cancel_download(self, video_id):
        with self.lock:
            self.cancelled_downloads.add(video_id)
            logger.info(
                f"Vídeo {video_id} marcado para cancelamento - thread será interrompida")

            if hasattr(self, 'sidebar') and self.sidebar and self.sidebar.mounted:
                try:
                    self.sidebar.update_download_item(video_id, 0, "cancelled")

                    def remove_later():
                        import time
                        time.sleep(2)
                        with self.lock:
                            if video_id in self.sidebar.items:
                                self.sidebar.downloads_column.controls.remove(
                                    self.sidebar.items[video_id]
                                )
                                del self.sidebar.items[video_id]
                                self.sidebar.update_download_counts()
                                if self.sidebar.mounted:
                                    self.sidebar.update()

                    threading.Thread(target=remove_later, daemon=True).start()
                except Exception as e:
                    logger.error(
                        f"Erro ao atualizar UI após cancelamento: {e}")

    def is_cancelled(self, video_id):
        return video_id in self.cancelled_downloads

    def download_thread(self, link, formato, diretorio, download_id, sidebar):
        import time

        last_progress_time = 0

        def progress_hook(d):
            nonlocal last_progress_time

            info_dict = d.get("info_dict", {})
            video_id = info_dict.get("id", "")

            if video_id and self.is_cancelled(video_id):
                logger.info(
                    f"Vídeo {video_id} cancelado - interrompendo download")
                raise Exception(f"Download cancelado pelo usuário")

            current_time = time.time()
            if current_time - last_progress_time < 0.1:
                return
            last_progress_time = current_time

            with self.lock:
                self.downloads[download_id] = d
                self.salvar_downloads_ativos()

                if sidebar and sidebar.mounted:
                    try:
                        if not video_id:
                            video_id = str(uuid.uuid4())
                            logger.warning(
                                f"ID não encontrado nos metadados. Gerado ID: {video_id}")

                        if d["status"] == "downloading":
                            if video_id not in sidebar.items:
                                title = info_dict.get(
                                    "title", "Título Indisponível")
                                thumbnail = info_dict.get(
                                    "thumbnail", "/images/logo.png")
                                file_path = d.get("filename", "")
                                format_selected = formato
                                download_data = {
                                    "id": video_id,
                                    "title": title,
                                    "thumbnail": thumbnail,
                                    "format": format_selected,
                                    "file_path": file_path,
                                }
                                sidebar.add_download_item(
                                    id=download_data["id"],
                                    title=download_data["title"],
                                    subtitle=download_data["format"],
                                    thumbnail_url=download_data["thumbnail"],
                                    file_path=download_data["file_path"],
                                    download_manager=self
                                )

                            if "total_bytes" in d and "downloaded_bytes" in d:
                                progress = d["downloaded_bytes"] / \
                                    max(d["total_bytes"], 1)
                                sidebar.update_download_item(
                                    video_id, progress, "downloading")

                        elif d["status"] == "finished":
                            try:
                                if not video_id:
                                    video_id = str(uuid.uuid4())
                                    logger.warning(
                                        f"ID não encontrado nos metadados. Gerado ID: {video_id}")
                                title = info_dict.get(
                                    "title", "Título Indisponível")
                                thumbnail = info_dict.get(
                                    "thumbnail", "/images/logo.png")
                                file_path = d.get("filename", "")
                                format_selected = formato
                                download_data = {
                                    "id": video_id,
                                    "title": title,
                                    "thumbnail": thumbnail,
                                    "format": format_selected,
                                    "file_path": file_path,
                                }

                                salvar_downloads_bem_sucedidos_client(
                                    self.page, download_data)

                                if video_id not in sidebar.items:
                                    sidebar.add_download_item(
                                        id=download_data["id"],
                                        title=download_data["title"],
                                        subtitle=download_data["format"],
                                        thumbnail_url=download_data["thumbnail"],
                                        file_path=download_data["file_path"],
                                        download_manager=self
                                    )

                                sidebar.update_download_item(
                                    video_id, 1.0, "finished")

                            except Exception as e:
                                logger.error(
                                    f"Exception during processing download: {e}")
                                sidebar.update_download_item(
                                    video_id, 0, "error")

                        elif d["status"] == "error":
                            sidebar.update_download_item(video_id, 0, "error")
                    except Exception as e:
                        logger.error(f"Erro ao atualizar a UI: {e}")
                else:
                    logger.warning(
                        f"Sidebar não montada. Ignorando atualização para download_id: {download_id}")

        try:
            start_download(link, formato, diretorio, progress_hook)

            with self.lock:
                if download_id in self.cancelled_downloads:
                    self.cancelled_downloads.remove(download_id)

        except Exception as e:
            if "cancelado pelo usuário" in str(e).lower():
                logger.info(
                    f"Download {download_id} foi cancelado com sucesso")
            else:
                with self.lock:
                    self.downloads[download_id] = {
                        "status": "error", "error": str(e)}
                logger.error(f"Erro ao iniciar o download: {e}")
                if sidebar and sidebar.mounted:
                    try:
                        info_dict = self.downloads.get(
                            download_id, {}).get("info_dict", {})
                        video_id = info_dict.get("id", download_id)
                        sidebar.update_download_item(video_id, 0, "error")
                    except Exception as e:
                        logger.error(
                            f"Erro ao atualizar a UI após falha no download: {e}")
        finally:
            self.semaphore.release()

            with self.lock:
                if download_id in self.download_threads:
                    del self.download_threads[download_id]

                cancelled_to_remove = set()
                for cancelled_id in self.cancelled_downloads:
                    if cancelled_id not in [item.data.get("id") for item in sidebar.items.values() if sidebar.mounted]:
                        cancelled_to_remove.add(cancelled_id)

                for cancelled_id in cancelled_to_remove:
                    self.cancelled_downloads.discard(cancelled_id)

import asyncio
import threading
import uuid
from queue import Queue

import flet as ft
from loguru import logger

from services.dlp_service import start_download


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
        self.progress_queue = Queue()
        self.progress_callback = None
        self._start_progress_processor()

    def _start_progress_processor(self):
        if hasattr(self.page, "run_task"):
            self.page.run_task(self._process_progress_updates)
        else:
            logger.warning("página não suporta run_task, usando fallback síncrono")

    async def _process_progress_updates(self):
        logger.info("🚀 Processador de progresso assíncrono iniciado")

        while True:
            try:
                await asyncio.sleep(0.03)

                updates_batch = []
                while not self.progress_queue.empty():
                    try:
                        update = self.progress_queue.get_nowait()
                        updates_batch.append(update)
                    except:
                        break

                if (
                    updates_batch
                    and hasattr(self, "sidebar")
                    and self.sidebar
                    and self.sidebar.mounted
                ):
                    for update in updates_batch:
                        await self._apply_update_async(update)

            except Exception as e:
                logger.error(f"Erro no processador de progresso: {e}")
                await asyncio.sleep(1)

    async def _apply_update_async(self, update):
        try:
            video_id = update.get("video_id")
            status = update.get("status")
            progress = update.get("progress", 0)
            data = update.get("data", {})

            if not video_id:
                return

            if self.is_cancelled(video_id):
                logger.info(f"Vídeo {video_id} cancelado - ignorando atualização")
                return

            if self.progress_callback and status == "downloading":
                try:
                    self.progress_callback(progress, "downloading")
                except Exception as e:
                    logger.error(f"Erro no callback de progresso: {e}")

            if status == "add_item":
                if video_id not in self.sidebar.items:
                    self.sidebar.add_download_item(
                        id=video_id,
                        title=data.get("title", "Título Indisponível"),
                        subtitle=data.get("format", "Formato"),
                        thumbnail_url=data.get("thumbnail", "/images/logo.png"),
                        file_path=data.get("file_path", ""),
                        download_manager=self,
                    )

            elif status == "downloading":
                self.sidebar.update_download_item(video_id, progress, "downloading")

            elif status == "converting":
                if self.progress_callback:
                    self.progress_callback(progress, "converting")
                self.sidebar.update_download_item(video_id, progress, "converting")

            elif status == "merging":
                self.sidebar.update_download_item(video_id, 0.95, "merging")

            elif status == "finished":
                if self.progress_callback:
                    self.progress_callback(1.0, "finished")

                storage = self.page.session.get("app_storage")
                if storage and data:
                    storage.save_download(video_id, data)

                self.sidebar.update_download_item(video_id, 1.0, "finished")
                logger.info(f"✅ Download concluído: {video_id}")

            elif status == "error":
                if self.progress_callback:
                    self.progress_callback(0, "error")
                self.sidebar.update_download_item(video_id, 0, "error")
                logger.error(f"❌ Erro no download: {video_id}")

            elif status == "cancelled":
                self.sidebar.update_download_item(video_id, 0, "cancelled")

                await asyncio.sleep(2)
                if video_id in self.sidebar.items:
                    self.sidebar.downloads_column.controls.remove(
                        self.sidebar.items[video_id]
                    )
                    del self.sidebar.items[video_id]
                    self.sidebar.update_download_counts()
                    if self.sidebar.mounted:
                        self.sidebar.update()

        except Exception as e:
            logger.error(f"Erro ao aplicar atualização async: {e}")

    def iniciar_download(
        self,
        link,
        formato,
        diretorio,
        sidebar,
        page,
        is_playlist=False,
        progress_callback=None,
    ):
        if not self.semaphore.acquire(blocking=False):
            from utils.ui_helpers import show_error_snackbar

            show_error_snackbar(page, "Limite de downloads simultâneos atingido.")
            logger.info("Limite de downloads simultâneos atingido.")
            return

        self.sidebar = sidebar
        self.progress_callback = progress_callback
        download_id = str(uuid.uuid4())

        thread = threading.Thread(
            target=self.download_thread,
            args=(link, formato, diretorio, sidebar, download_id, is_playlist),
            daemon=True,
        )

        with self.lock:
            self.download_threads[download_id] = thread

        thread.start()
        logger.info(f"🚀 Download iniciado: {download_id}")

    def cancel_download(self, video_id):
        with self.lock:
            self.cancelled_downloads.add(video_id)
            logger.info(f"🚫 Vídeo {video_id} marcado para cancelamento")

            self.progress_queue.put(
                {"video_id": video_id, "status": "cancelled", "progress": 0}
            )

    def is_cancelled(self, video_id):
        return video_id in self.cancelled_downloads

    def download_thread(
        self, link, formato, diretorio, sidebar, download_id, is_playlist=False
    ):
        import time

        last_progress_time = 0
        last_progress_value = -1
        video_id_global = None
        playlist_videos = {}

        def progress_hook(d):
            nonlocal last_progress_time, last_progress_value, video_id_global, playlist_videos

            info_dict = d.get("info_dict", {})
            video_id = info_dict.get("id", "")

            if is_playlist and video_id:
                if video_id not in playlist_videos:
                    playlist_videos[video_id] = {
                        "title": info_dict.get("title", "Título Indisponível"),
                        "thumbnail": info_dict.get("thumbnail", "/images/logo.png"),
                        "added_to_ui": False,
                    }
                    logger.info(f"📹 Novo vídeo detectado na playlist: {video_id}")

            if not video_id_global and video_id:
                video_id_global = video_id

            current_video_id = video_id or video_id_global

            if current_video_id and self.is_cancelled(current_video_id):
                logger.info(f"⚠️ Vídeo {current_video_id} cancelado - interrompendo")
                raise Exception(f"Download cancelado pelo usuário")

            current_time = time.time()
            if current_time - last_progress_time < 0.05:
                return

            progress = 0
            if d["status"] == "downloading":
                if "total_bytes" in d and "downloaded_bytes" in d:
                    progress = d["downloaded_bytes"] / max(d["total_bytes"], 1)
                elif "total_bytes_estimate" in d and "downloaded_bytes" in d:
                    progress = d["downloaded_bytes"] / max(d["total_bytes_estimate"], 1)

            if (
                abs(progress - last_progress_value) < 0.005
                and d["status"] == "downloading"
            ):
                return

            last_progress_time = current_time
            last_progress_value = progress

            if not current_video_id:
                current_video_id = str(uuid.uuid4())
                video_id_global = current_video_id
                logger.warning(f"ID não encontrado, gerado: {current_video_id}")

            try:
                if d["status"] == "downloading":
                    if current_video_id not in sidebar.items:
                        video_info = playlist_videos.get(current_video_id, {})

                        self.progress_queue.put(
                            {
                                "video_id": current_video_id,
                                "status": "add_item",
                                "data": {
                                    "id": current_video_id,
                                    "title": video_info.get("title")
                                    or info_dict.get("title", "Título Indisponível"),
                                    "thumbnail": video_info.get("thumbnail")
                                    or info_dict.get("thumbnail", "/images/logo.png"),
                                    "format": formato,
                                    "file_path": d.get("filename", ""),
                                },
                            }
                        )

                        if is_playlist and current_video_id in playlist_videos:
                            playlist_videos[current_video_id]["added_to_ui"] = True

                    self.progress_queue.put(
                        {
                            "video_id": current_video_id,
                            "status": "downloading",
                            "progress": progress,
                        }
                    )

                elif d["status"] == "finished":
                    filename = d.get("filename", "")

                    if (
                        "f251" in filename
                        or "f140" in filename
                        or ".webm" in filename
                        or filename.endswith(".m4a")
                    ):
                        logger.debug(f"Arquivo parcial concluído: {filename}")
                    else:
                        self.progress_queue.put(
                            {
                                "video_id": current_video_id,
                                "status": "downloading",
                                "progress": 0.95,
                            }
                        )
                        logger.info(
                            f"Download principal concluído, aguardando merge: {current_video_id}"
                        )

            except Exception as e:
                logger.error(f"Erro no progress_hook: {e}")

        try:
            logger.info(f"📥 Iniciando download: {link}")

            result_info = start_download(
                link, formato, diretorio, progress_hook, is_playlist
            )

            if (
                is_playlist
                and isinstance(result_info, dict)
                and "entries" in result_info
            ):
                logger.info(
                    f"📋 Processando playlist com {len(result_info['entries'])} vídeos"
                )

                for entry in result_info.get("entries", []):
                    entry_id = entry.get("id")
                    if entry_id and entry_id in playlist_videos:
                        download_data = {
                            "id": entry_id,
                            "title": entry.get("title", "Título Indisponível"),
                            "thumbnail": entry.get("thumbnail", "/images/logo.png"),
                            "format": formato,
                            "file_path": entry.get("filepath", ""),
                        }

                        if not playlist_videos[entry_id].get("added_to_ui"):
                            self.progress_queue.put(
                                {
                                    "video_id": entry_id,
                                    "status": "add_item",
                                    "data": download_data,
                                }
                            )

                        self.progress_queue.put(
                            {
                                "video_id": entry_id,
                                "status": "finished",
                                "progress": 1.0,
                                "data": download_data,
                            }
                        )

            elif video_id_global:
                download_data = {
                    "id": video_id_global,
                    "title": result_info.get("title", "Título Indisponível"),
                    "thumbnail": result_info.get("thumbnail", "/images/logo.png"),
                    "format": formato,
                    "file_path": result_info.get("filepath", ""),
                }

                if video_id_global not in sidebar.items:
                    self.progress_queue.put(
                        {
                            "video_id": video_id_global,
                            "status": "add_item",
                            "data": download_data,
                        }
                    )

                self.progress_queue.put(
                    {
                        "video_id": video_id_global,
                        "status": "downloading",
                        "progress": 0.99,
                    }
                )

                time.sleep(0.1)

                self.progress_queue.put(
                    {
                        "video_id": video_id_global,
                        "status": "finished",
                        "progress": 1.0,
                        "data": download_data,
                    }
                )

            with self.lock:
                if download_id in self.cancelled_downloads:
                    self.cancelled_downloads.remove(download_id)

        except Exception as e:
            if "cancelado pelo usuário" in str(e).lower():
                logger.info(f"✅ Download {download_id} cancelado com sucesso")
            else:
                logger.error(f"❌ Erro no download: {e}")

                if video_id_global:
                    self.progress_queue.put(
                        {"video_id": video_id_global, "status": "error", "progress": 0}
                    )

        finally:
            self.semaphore.release()

            with self.lock:
                if download_id in self.download_threads:
                    del self.download_threads[download_id]

            logger.info(f"🏁 Thread de download finalizada: {download_id}")

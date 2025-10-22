import asyncio
import threading
import uuid
from queue import Queue

import flet as ft

from utils.logging_config import setup_logging

logger = setup_logging()

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
        self.sidebar = None

        self.playlist_progress = {}

        self._start_progress_processor()

    def _start_progress_processor(self):
        if hasattr(self.page, "run_task"):
            self.page.run_task(self._process_progress_updates)
        else:
            logger.warning("página não suporta run_task, usando fallback síncrono")

    async def _process_progress_updates(self):
        logger.info("Processador de progresso assíncrono iniciado")

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

                if updates_batch and self.sidebar and self.sidebar.mounted:
                    for update in updates_batch:
                        await self._apply_update_async(update)

            except Exception as e:
                logger.error(f"Erro no processador de progresso: {e}")
                await asyncio.sleep(1)

    def _calculate_total_progress(self, download_id):
        """
        Calcula o progresso total da playlist usando proporção matemática.

        Fórmula: progresso_total = (videos_completos + progresso_atual) / total_videos
        """
        if download_id not in self.playlist_progress:
            return 0.0

        info = self.playlist_progress[download_id]
        total_videos = info.get("total", 1)
        completed_count = len(info.get("completed", []))
        current_progress = info.get("current_progress", {})

        # Soma dos vídeos completos (cada um vale 1.0)
        completed_sum = float(completed_count)

        # Soma do progresso dos vídeos atuais (vale de 0.0 a 1.0 cada)
        current_sum = sum(current_progress.values())

        # Progresso total proporcional
        total_progress = (completed_sum + current_sum) / max(total_videos, 1)

        logger.debug(
            f"[{download_id[:8]}] Progresso: {completed_count}/{total_videos} completos "
            f"+ {current_sum:.2f} atual = {total_progress*100:.1f}%"
        )

        return min(total_progress, 1.0)

    async def _apply_update_async(self, update):
        try:
            video_id = update.get("video_id")
            download_id = update.get("download_id")
            status = update.get("status")
            progress = update.get("progress", 0)
            data = update.get("data", {})

            if not video_id:
                return

            if self.is_cancelled(video_id):
                logger.info(f"Vídeo {video_id} cancelado - ignorando atualização")
                return

            # Atualiza progresso proporcional para playlists
            if download_id and download_id in self.playlist_progress:
                info = self.playlist_progress[download_id]

                if status == "downloading":
                    info["current_progress"][video_id] = progress

                elif status == "finished":
                    if video_id not in info["completed"]:
                        info["completed"].append(video_id)
                    info["current_progress"].pop(video_id, None)

                # Calcula e envia progresso total proporcional
                total_progress = self._calculate_total_progress(download_id)

                if self.progress_callback:
                    try:
                        self.progress_callback(total_progress, status)
                    except Exception as e:
                        logger.error(f"Erro no callback: {e}")

            # Atualiza callback para downloads únicos
            elif self.progress_callback and status == "downloading":
                try:
                    self.progress_callback(progress, "downloading")
                except Exception as e:
                    logger.error(f"Erro no callback de progresso: {e}")

            # ATUALIZA SIDEBAR
            if status == "add_item":
                if video_id not in self.sidebar.items:
                    logger.info(
                        f"Adicionando item à sidebar: {data.get('title', 'N/A')[:30]}..."
                    )
                    self.sidebar.add_download_item(
                        id=video_id,
                        title=data.get("title", "Título Indisponível"),
                        subtitle=data.get("format", "Formato"),
                        thumbnail_url=data.get("thumbnail", "/images/thumb_broken.jpg"),
                        file_path=data.get("file_path", ""),
                        download_manager=self,
                    )

            elif status == "downloading":
                self.sidebar.update_download_item(video_id, progress, "downloading")

            elif status == "converting":
                if self.progress_callback and not download_id:
                    self.progress_callback(progress, "converting")
                self.sidebar.update_download_item(video_id, progress, "converting")

            elif status == "merging":
                self.sidebar.update_download_item(video_id, 0.95, "merging")

            elif status == "finished":
                # Verifica se playlist está completa
                if download_id and download_id in self.playlist_progress:
                    info = self.playlist_progress[download_id]
                    if len(info["completed"]) >= info["total"]:
                        if self.progress_callback:
                            self.progress_callback(1.0, "finished")
                        logger.info(
                            f"Playlist completa: {len(info['completed'])}/{info['total']}"
                        )
                elif self.progress_callback:
                    self.progress_callback(1.0, "finished")

                storage = self.page.session.get("app_storage")
                if storage and data:
                    storage.save_download(video_id, data)

                self.sidebar.update_download_item(video_id, 1.0, "finished")
                logger.info(f"Download concluído: {video_id}")

            elif status == "error":
                if self.progress_callback:
                    self.progress_callback(0, "error")
                self.sidebar.update_download_item(video_id, 0, "error")
                logger.error(f"Erro no download: {video_id}")

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

        # Inicializa controle de progresso para playlists
        if is_playlist:
            logger.info(f"Inicializando controle de playlist: {download_id}")
            self.playlist_progress[download_id] = {
                "total": 0,
                "completed": [],
                "current_progress": {},
            }

        thread = threading.Thread(
            target=self.download_thread,
            args=(link, formato, diretorio, sidebar, download_id, is_playlist),
            daemon=True,
        )

        with self.lock:
            self.download_threads[download_id] = thread

        thread.start()
        logger.info(
            f"Download iniciado: {download_id[:8]}... (playlist={is_playlist})"
        )

    def cancel_download(self, video_id):
        with self.lock:
            self.cancelled_downloads.add(video_id)
            logger.info(f"Vídeo {video_id} marcado para cancelamento")

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

            # Detecta novos vídeos da playlist
            if is_playlist and video_id:
                if video_id not in playlist_videos:
                    playlist_videos[video_id] = {
                        "title": info_dict.get("title", "Título Indisponível"),
                        "thumbnail": info_dict.get(
                            "thumbnail", "/images/thumb_broken.jpg"
                        ),
                        "added_to_ui": False,
                    }

                    # Atualiza total de vídeos
                    if download_id in self.playlist_progress:
                        self.playlist_progress[download_id]["total"] = len(
                            playlist_videos
                        )
                        logger.info(
                            f"Vídeo {len(playlist_videos)} detectado: "
                            f"{info_dict.get('title', 'N/A')[:40]}..."
                        )

            if not video_id_global and video_id:
                video_id_global = video_id

            current_video_id = video_id or video_id_global

            if current_video_id and self.is_cancelled(current_video_id):
                logger.info(f"Vídeo {current_video_id} cancelado - interrompendo")
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
                    # Adiciona à UI se ainda não foi adicionado
                    if current_video_id not in sidebar.items:
                        video_info = playlist_videos.get(current_video_id, {})

                        self.progress_queue.put(
                            {
                                "video_id": current_video_id,
                                "download_id": download_id if is_playlist else None,
                                "status": "add_item",
                                "data": {
                                    "id": current_video_id,
                                    "title": video_info.get("title")
                                    or info_dict.get("title", "Título Indisponível"),
                                    "thumbnail": video_info.get("thumbnail")
                                    or info_dict.get(
                                        "thumbnail", "/images/thumb_broken.jpg"
                                    ),
                                    "format": formato,
                                    "file_path": d.get("filename", ""),
                                },
                            }
                        )

                        if is_playlist and current_video_id in playlist_videos:
                            playlist_videos[current_video_id]["added_to_ui"] = True

                    # Atualiza progresso
                    self.progress_queue.put(
                        {
                            "video_id": current_video_id,
                            "download_id": download_id if is_playlist else None,
                            "status": "downloading",
                            "progress": progress,
                        }
                    )

                elif d["status"] == "finished":
                    filename = d.get("filename", "")

                    # Ignora arquivos parciais
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
                                "download_id": download_id if is_playlist else None,
                                "status": "downloading",
                                "progress": 0.95,
                            }
                        )

            except Exception as e:
                logger.error(f"Erro no progress_hook: {e}")

        try:
            logger.info(f"Iniciando download: {link}")

            result_info = start_download(
                link, formato, diretorio, progress_hook, is_playlist
            )

            if (
                is_playlist
                and isinstance(result_info, dict)
                and "entries" in result_info
            ):
                total_entries = len(result_info["entries"])
                logger.info(f"Playlist completa: {total_entries} vídeos")

                # Atualiza total final
                if download_id in self.playlist_progress:
                    self.playlist_progress[download_id]["total"] = total_entries

                for entry in result_info.get("entries", []):
                    entry_id = entry.get("id")
                    if entry_id:
                        download_data = {
                            "id": entry_id,
                            "title": entry.get("title", "Título Indisponível"),
                            "thumbnail": entry.get(
                                "thumbnail", "/images/thumb_broken.jpg"
                            ),
                            "format": formato,
                            "file_path": entry.get("filepath", ""),
                        }

                        if entry_id not in sidebar.items:
                            self.progress_queue.put(
                                {
                                    "video_id": entry_id,
                                    "download_id": download_id,
                                    "status": "add_item",
                                    "data": download_data,
                                }
                            )

                        # Marca como finalizado
                        self.progress_queue.put(
                            {
                                "video_id": entry_id,
                                "download_id": download_id,
                                "status": "finished",
                                "progress": 1.0,
                                "data": download_data,
                            }
                        )

            elif video_id_global:
                download_data = {
                    "id": video_id_global,
                    "title": result_info.get("title", "Título Indisponível"),
                    "thumbnail": result_info.get(
                        "thumbnail", "/images/thumb_broken.jpg"
                    ),
                    "format": formato,
                    "file_path": result_info.get("filepath", ""),
                }

                if video_id_global not in sidebar.items:
                    self.progress_queue.put(
                        {
                            "video_id": video_id_global,
                            "download_id": None,
                            "status": "add_item",
                            "data": download_data,
                        }
                    )

                self.progress_queue.put(
                    {
                        "video_id": video_id_global,
                        "download_id": None,
                        "status": "downloading",
                        "progress": 0.99,
                    }
                )

                time.sleep(0.1)

                self.progress_queue.put(
                    {
                        "video_id": video_id_global,
                        "download_id": None,
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
                logger.info(f"Download {download_id[:8]} cancelado com sucesso")
            else:
                logger.error(f"Erro no download: {e}")

                if video_id_global:
                    self.progress_queue.put(
                        {
                            "video_id": video_id_global,
                            "download_id": None,
                            "status": "error",
                            "progress": 0,
                        }
                    )

        finally:
            self.semaphore.release()

            with self.lock:
                if download_id in self.download_threads:
                    del self.download_threads[download_id]

                if download_id in self.playlist_progress:
                    logger.info(f"Limpando progresso: {download_id[:8]}")
                    del self.playlist_progress[download_id]

            logger.info(f"Thread de download finalizada: {download_id[:8]}")

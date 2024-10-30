# services/download_manager.py

import threading
import uuid
import logging

from services.dlp_service import start_download
from utils.client_storage_utils import (
    salvar_downloads_bem_sucedidos_client,
)

logger = logging.getLogger(__name__)


class DownloadManager:
    def __init__(self, page):
        self.downloads = {}
        self.lock = threading.Lock()
        self.page = page 

    def iniciar_download(self, link, formato, diretorio, sidebar):
        download_id = str(uuid.uuid4())
        thread = threading.Thread(
            target=self.download_thread,
            args=(link, formato, diretorio, download_id, sidebar),
            daemon=True,
        )
        thread.start()

    def download_thread(self, link, formato, diretorio, download_id, sidebar):
        def progress_hook(d):
            with self.lock:
                self.downloads[download_id] = d
                logger.info(f"progress_hook chamado para download_id: {download_id}")
                logger.info(f"sidebar.mounted: {sidebar.mounted}")
                if sidebar and sidebar.mounted:
                    try:
                        info_dict = d.get("info_dict", {})
                        video_id = info_dict.get("id", "")
                        if not video_id:
                            video_id = str(uuid.uuid4())
                            logger.warning(
                                f"ID não encontrado nos metadados. Gerado ID: {video_id}"
                            )
                        if d["status"] == "downloading":
                            if video_id not in sidebar.items:
                                title = info_dict.get("title", "Título Indisponível")
                                thumbnail = info_dict.get(
                                    "thumbnail", "/images/logo.png"
                                )
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
                                )

                            if "total_bytes" in d and "downloaded_bytes" in d:
                                progress = d["downloaded_bytes"] / max(
                                    d["total_bytes"], 1
                                )
                                sidebar.update_download_item(
                                    video_id, progress, "downloading"
                                )

                        elif d["status"] == "finished":
                            try:
                                info_dict = d.get("info_dict", {})
                                video_id = info_dict.get("id", "")
                                if not video_id:
                                    video_id = str(uuid.uuid4())
                                    logger.warning(
                                        f"ID não encontrado nos metadados. Gerado ID: {video_id}"
                                    )
                                title = info_dict.get("title", "Título Indisponível")
                                thumbnail = info_dict.get(
                                    "thumbnail", "/images/logo.png"
                                )
                                file_path = d.get("filename", "")
                                format_selected = formato
                                download_data = {
                                    "id": video_id,
                                    "title": title,
                                    "thumbnail": thumbnail,
                                    "format": format_selected,
                                    "file_path": file_path,
                                }
                                # Salva os dados do download
                                salvar_downloads_bem_sucedidos_client(
                                    self.page, download_data
                                )
                                if video_id not in sidebar.items:
                                    sidebar.add_download_item(
                                        id=download_data["id"],
                                        title=download_data["title"],
                                        subtitle=download_data["format"],
                                        thumbnail_url=download_data["thumbnail"],
                                        file_path=download_data["file_path"],
                                    )

                                # Atualiza o item como concluído
                                sidebar.update_download_item(video_id, 1.0, "finished")

                            except Exception as e:
                                logger.error(
                                    f"Exception during processing download: {e}"
                                )
                                # Atualiza o item como erro
                                sidebar.update_download_item(video_id, 0, "error")

                        elif d["status"] == "error":
                            sidebar.update_download_item(video_id, 0, "error")
                    except Exception as e:
                        logger.error(f"Erro ao atualizar a UI: {e}")
                else:
                    logger.warning(
                        f"Sidebar não montada. Ignorando atualização para download_id: {download_id}"
                    )

        try:
            start_download(link, formato, diretorio, progress_hook)
        except Exception as e:
            with self.lock:
                self.downloads[download_id] = {"status": "error", "error": str(e)}
            logger.error(f"Erro ao iniciar o download: {e}")
            if sidebar and sidebar.mounted:
                try:
                    sidebar.update_download_item(download_id, 0, "error")
                except Exception as e:
                    logger.error(f"Erro ao atualizar a UI após falha no download: {e}")

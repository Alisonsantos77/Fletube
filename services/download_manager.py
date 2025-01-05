# services/download_manager.py

from utils.client_storage_utils import salvar_downloads_bem_sucedidos_client
import threading
import uuid
import logging
from services.dlp_service import start_download
import flet as ft
logger = logging.getLogger(__name__)

# Variável global para controle de download em andamento
download_in_progress = False


class DownloadManager:
    def __init__(self, page, max_downloads=3):
        """
        Inicializa o gerenciador de downloads com o número máximo de downloads simultâneos.

        Args:
            page: A página associada ao gerenciador de downloads.
            max_downloads (int): O número máximo de downloads simultâneos permitidos. O padrão é 3.
        """
        self.downloads = {}
        self.lock = threading.Lock()
        self.page = page
        self.max_downloads = max_downloads
        self.semaphore = threading.Semaphore(
            self.max_downloads)  # Inicializa o semáforo
        self.active_downloads = 0  # Contador de downloads ativos

    def iniciar_download(self, link, formato, diretorio, sidebar, page):
        global download_in_progress

        if download_in_progress:
            # Verifica se já existe um download em andamento
            snack = ft.Snackbar(
                message="Já existe um download em andamento.", timeout=5000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()   
            logger.warning("Já existe um download em andamento.")
            return

        # Atualiza o estado global para indicar que o download foi iniciado
        download_in_progress = True
        """
        Inicia o download se o número de downloads simultâneos permitidos não for atingido.

        Args:
            link (str): O link do vídeo a ser baixado.
            formato (str): O formato desejado para o download.
            diretorio (str): O diretório onde o arquivo será salvo.
            sidebar: A barra lateral que exibe o progresso do download.
        """
        # Verifica se há capacidade para mais downloads
        if not self.semaphore.acquire(blocking=False):
            snack = ft.Snackbar(
                message="Limite de downloads simultâneos atingido.", timeout=5000
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
            logger.info("Limite de downloads simultâneos atingido.")
            return  # Impede o novo download se o limite de downloads simultâneos for atingido

        download_id = str(uuid.uuid4())
        thread = threading.Thread(
            target=self.download_thread,
            args=(link, formato, diretorio, download_id, sidebar),
            daemon=True,
        )
        thread.start()

    def download_thread(self, link, formato, diretorio, download_id, sidebar):
        global download_in_progress

        """
        Executa o download em uma thread separada e atualiza o progresso do download.
        """
        def progress_hook(d):
            global download_in_progress

            """
            Função de callback para monitorar o progresso do download.
            """
            with self.lock:
                self.downloads[download_id] = d
                logger.info(
                    f"progress_hook chamado para download_id: {download_id}")
                if sidebar and sidebar.mounted:
                    try:
                        info_dict = d.get("info_dict", {})
                        video_id = info_dict.get("id", "")
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
                                )

                            if "total_bytes" in d and "downloaded_bytes" in d:
                                progress = d["downloaded_bytes"] / \
                                    max(d["total_bytes"], 1)
                                sidebar.update_download_item(
                                    video_id, progress, "downloading")

                        elif d["status"] == "finished":
                            try:
                                info_dict = d.get("info_dict", {})
                                video_id = info_dict.get("id", "")
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
                                # Salva os dados do download
                                salvar_downloads_bem_sucedidos_client(
                                    self.page, download_data)
                                if video_id not in sidebar.items:
                                    sidebar.add_download_item(
                                        id=download_data["id"],
                                        title=download_data["title"],
                                        subtitle=download_data["format"],
                                        thumbnail_url=download_data["thumbnail"],
                                        file_path=download_data["file_path"],
                                    )

                                # Atualiza o item como concluído
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
        except Exception as e:
            with self.lock:
                self.downloads[download_id] = {
                    "status": "error", "error": str(e)}
            logger.error(f"Erro ao iniciar o download: {e}")
            if sidebar and sidebar.mounted:
                try:
                    sidebar.update_download_item(download_id, 0, "error")
                except Exception as e:
                    logger.error(
                        f"Erro ao atualizar a UI após falha no download: {e}")
        finally:
            # Libera o semáforo após o download (independente do sucesso ou falha)
            self.semaphore.release()
            download_in_progress = False

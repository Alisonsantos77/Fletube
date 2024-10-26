import logging
import flet as ft
import uuid

logger = logging.getLogger(__name__)


def salvar_downloads_bem_sucedidos_client(page: ft.Page, download_data: dict):
    downloads = page.client_storage.get("successful_downloads") or []
    if isinstance(downloads, str):
        try:
            downloads = eval(downloads)
        except Exception as e:
            logger.error(f"Erro ao avaliar downloads do client_storage: {e}")
            downloads = []

    existing_ids = [d.get("id") for d in downloads]
    if download_data["id"] not in existing_ids:
        downloads.append(download_data)
        page.client_storage.set("successful_downloads", downloads)
        logger.info(f"Download salvo no client_storage: {download_data}")
    else:
        logger.info("Download já existe no client_storage.")


def recuperar_downloads_bem_sucedidos_client(page: ft.Page):
    downloads = page.client_storage.get("successful_downloads") or []
    if isinstance(downloads, str):
        try:
            downloads = eval(downloads)
        except Exception as e:
            logger.error(f"Erro ao avaliar downloads do client_storage: {e}")
            downloads = []
    # Adiciona IDs únicos a itens que não possuem
    for download in downloads:
        if "id" not in download or not download["id"]:
            download["id"] = str(uuid.uuid4())
            logger.info(f"ID adicionado ao download: {download}")
    page.client_storage.set("successful_downloads", downloads)
    return downloads


def excluir_download_bem_sucedido_client(page: ft.Page, download_id: str):
    downloads = recuperar_downloads_bem_sucedidos_client(page)
    downloads = [d for d in downloads if d.get("id") != download_id]
    page.client_storage.set("successful_downloads", downloads)
    logger.info(f"Download com ID {download_id} excluído do client_storage.")

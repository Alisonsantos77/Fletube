import logging
import json

logger = logging.getLogger(__name__)


def salvar_downloads_bem_sucedidos_session(page, download_data):
    try:
        downloads_json = page.session.get("successful_downloads")
        if downloads_json:
            downloads = json.loads(downloads_json)
        else:
            downloads = []

        existing_ids = [d.get("id") for d in downloads]
        if download_data["id"] not in existing_ids:
            downloads.append(download_data)
            page.session.set("successful_downloads", json.dumps(downloads))
            logger.info("Download bem-sucedido salvo no session storage.")
        else:
            logger.info("Download já existe no session storage.")
    except Exception as e:
        logger.error(f"Erro ao salvar download no session storage: {e}")


def recuperar_downloads_bem_sucedidos_session(page):
    try:
        downloads_json = page.session.get("successful_downloads")
        if downloads_json:
            downloads = json.loads(downloads_json)
            logger.info("Downloads recuperados do session storage.")
            return downloads
        else:
            return []
    except Exception as e:
        logger.error(f"Erro ao recuperar downloads do session storage: {e}")
        return []


def excluir_download_bem_sucedido_session(page, download_id: str):
    try:
        downloads_json = page.session.get("successful_downloads")
        if downloads_json:
            downloads = json.loads(downloads_json)
            downloads = [d for d in downloads if d.get("id") != download_id]
            page.session.set("successful_downloads", json.dumps(downloads))
            logger.info(f"Download com ID {download_id} excluído do session storage.")
    except Exception as e:
        logger.error(f"Erro ao excluir download do session storage: {e}")


import logging
import flet as ft
import uuid
import json

logger = logging.getLogger(__name__)


def salvar_downloads_bem_sucedidos_client(page: ft.Page, download_data: dict):
    """
    Salva um download bem-sucedido no client_storage (persistente).

    Args:
        page (ft.Page): A página Flet.
        download_data (dict): Dados do download a serem salvos.
    """
    downloads_json = page.client_storage.get("downloads_bem_sucedidos")
    if downloads_json:
        try:
            downloads = json.loads(downloads_json)
        except json.JSONDecodeError as e:
            logger.error(
                f"Erro ao decodificar downloads do client_storage: {e}")
            downloads = []
    else:
        downloads = []

    downloads.append(download_data)

    try:
        page.client_storage.set(
            "downloads_bem_sucedidos", json.dumps(downloads))
        logger.info(f"Download salvo no client_storage: {download_data}")
    except Exception as e:
        logger.error(f"Erro ao salvar downloads no client_storage: {e}")


def recuperar_downloads_bem_sucedidos_client(page: ft.Page):
    """
    Recupera os downloads bem-sucedidos do client_storage.

    Args:
        page (ft.Page): A página Flet.

    Returns:
        list: Lista de downloads bem-sucedidos.
    """
    downloads_json = page.client_storage.get("downloads_bem_sucedidos")
    if downloads_json:
        try:
            downloads = json.loads(downloads_json)
        except json.JSONDecodeError as e:
            logger.error(
                f"Erro ao decodificar downloads do client_storage: {e}")
            downloads = []
    else:
        downloads = []

    # Adiciona IDs únicos a itens que não possuem
    for download in downloads:
        if "id" not in download or not download["id"]:
            download["id"] = str(uuid.uuid4())
            logger.info(f"ID adicionado ao download: {download}")

    try:
        page.client_storage.set(
            "downloads_bem_sucedidos", json.dumps(downloads))
    except Exception as e:
        logger.error(f"Erro ao salvar downloads no client_storage: {e}")

    return downloads


def excluir_download_bem_sucedido_client(page: ft.Page, download_id: str):
    """
    Exclui um download específico do client_storage.

    Args:
        page (ft.Page): A página Flet.
        download_id (str): ID do download a ser excluído.
    """
    downloads = recuperar_downloads_bem_sucedidos_client(page)
    downloads = [d for d in downloads if d.get("id") != download_id]
    try:
        page.client_storage.set(
            "downloads_bem_sucedidos", json.dumps(downloads))
        logger.info(
            f"Download com ID {download_id} excluído do client_storage.")
    except Exception as e:
        logger.error(f"Erro ao excluir download do client_storage: {e}")


def excluir_todos_downloads_bem_sucedidos_client(page: ft.Page):
    """
    Exclui todos os downloads do client_storage.

    Args:
        page (ft.Page): A página Flet.
    """
    try:
        page.client_storage.set("downloads_bem_sucedidos", json.dumps([]))
        logger.info("Todos os downloads foram excluídos do client_storage.")
    except Exception as e:
        logger.error(
            f"Erro ao excluir todos os downloads do client_storage: {e}")


def salvar_downloads_ativos_client(page: ft.Page, downloads_ativos: dict):
    """
    Salva downloads ativos no client_storage para persistir na atualização.

    Args:
        page (ft.Page): A página Flet.
        downloads_ativos (dict): Dicionário com downloads ativos.
    """
    try:
        page.client_storage.set(
            "downloads_ativos", json.dumps(downloads_ativos))
        logger.info(
            f"Downloads ativos salvos no client_storage: {len(downloads_ativos)} itens")
    except Exception as e:
        logger.error(f"Erro ao salvar downloads ativos no client_storage: {e}")


def recuperar_downloads_ativos_client(page: ft.Page):
    """
    Recupera downloads ativos do client_storage.

    Args:
        page (ft.Page): A página Flet.

    Returns:
        dict: Dicionário com downloads ativos.
    """
    downloads_json = page.client_storage.get("downloads_ativos")
    if downloads_json:
        try:
            downloads = json.loads(downloads_json)
            logger.info(
                f"Downloads ativos recuperados do client_storage: {len(downloads)} itens")
            return downloads
        except json.JSONDecodeError as e:
            logger.error(
                f"Erro ao decodificar downloads ativos do client_storage: {e}")
            return {}
    else:
        return {}

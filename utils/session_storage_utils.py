import json
import logging
import uuid

import flet as ft

from utils.logging_config import setup_logging

logger = setup_logging()


def salvar_downloads_bem_sucedidos_session(page: ft.Page, download_data: dict):
    """
    Salva um download bem-sucedido no session_storage.

    Args:
        page (ft.Page): A página Flet.
        download_data (dict): Dados do download a serem salvos.
    """
    downloads_json = page.session.get("downloads_bem_sucedidos_session")
    if downloads_json:
        try:
            downloads = json.loads(downloads_json)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar downloads do session_storage: {e}")
            downloads = []
    else:
        downloads = []

    downloads.append(download_data)

    try:
        page.session.set("downloads_bem_sucedidos_session", json.dumps(downloads))
        logger.info(f"Download salvo na session_storage: {download_data}")
    except Exception as e:
        logger.error(f"Erro ao salvar downloads na session_storage: {e}")


def recuperar_downloads_bem_sucedidos_session(page: ft.Page):
    """
    Recupera os downloads bem-sucedidos do session_storage.

    Args:
        page (ft.Page): A página Flet.

    Returns:
        list: Lista de downloads bem-sucedidos.
    """
    downloads_json = page.session.get("downloads_bem_sucedidos_session")
    if downloads_json:
        try:
            downloads = json.loads(downloads_json)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar downloads do session_storage: {e}")
            downloads = []
    else:
        downloads = []

    # Adiciona IDs únicos a itens que não possuem
    for download in downloads:
        if "id" not in download or not download["id"]:
            download["id"] = str(uuid.uuid4())
            logger.info(f"ID adicionado ao download: {download}")

    try:
        page.session.set("downloads_bem_sucedidos_session", json.dumps(downloads))
    except Exception as e:
        logger.error(f"Erro ao salvar downloads na session_storage: {e}")

    return downloads


def excluir_download_bem_sucedido_session(page: ft.Page, download_id: str):
    """
    Exclui um download específico do session_storage.

    Args:
        page (ft.Page): A página Flet.
        download_id (str): ID do download a ser excluído.
    """
    downloads = recuperar_downloads_bem_sucedidos_session(page)
    downloads = [d for d in downloads if d.get("id") != download_id]
    try:
        page.session.set("downloads_bem_sucedidos_session", json.dumps(downloads))
        logger.info(f"Download com ID {download_id} excluído da session_storage.")
    except Exception as e:
        logger.error(f"Erro ao excluir download da session_storage: {e}")


def excluir_todos_downloads_bem_sucedidos_session(page: ft.Page):
    """
    Exclui todos os downloads do session_storage.

    Args:
        page (ft.Page): A página Flet.
    """
    try:
        page.session.set("downloads_bem_sucedidos_session", json.dumps([]))
        logger.info("Todos os downloads foram excluídos da session_storage.")
    except Exception as e:
        logger.error(f"Erro ao excluir todos os downloads da session_storage: {e}")

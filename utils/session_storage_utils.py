import logging

logger = logging.getLogger(__name__)

import json


def salvar_downloads_bem_sucedidos_session(page, downloads):
    """
    Salva a lista de downloads bem-sucedidos no session storage.

    Args:
        page (ft.Page): A página atual da aplicação Flet.
        downloads (list): A lista de downloads a serem salvos.
    """
    try:
        # Serializa os downloads para uma string JSON
        page.session.set("successful_downloads", json.dumps(downloads))
        logger.info("Downloads bem-sucedidos salvos no session storage.")
    except Exception as e:
        logger.error(f"Erro ao salvar downloads no session storage: {e}")




def recuperar_downloads_bem_sucedidos_session(page):
    """
    Recupera a lista de downloads bem-sucedidos do session storage.

    Args:
        page (ft.Page): A página atual da aplicação Flet.

    Returns:
        list: A lista de downloads bem-sucedidos, ou uma lista vazia se não houver dados.
    """
    try:
        downloads = page.session.get("successful_downloads")
        if downloads is None:
            downloads = []
        elif isinstance(downloads, str):
            # Se os downloads forem uma string, tente converter para uma lista de dicionários
            downloads = json.loads(downloads)

        if not isinstance(downloads, list):
            downloads = []

        logger.info("Downloads recuperados do session storage.")
        return downloads
    except Exception as e:
        logger.error(f"Erro ao recuperar downloads do session storage: {e}")
        return []

import logging
import flet as ft
logger = logging.getLogger(__name__)


def recuperar_downloads_bem_sucedidos(page: ft.Page):
    """
    Recupera a lista de downloads bem-sucedidos armazenados no client_storage.

    :param page: Instância do Flet Page para acesso ao client_storage.
    :return: Lista de downloads bem-sucedidos ou uma lista vazia se não houver dados.
    """
    successful_downloads = page.client_storage.get("fletube.successful_downloads")

    # Se for uma string (por algum erro anterior), converte para lista
    if isinstance(successful_downloads, str):
        try:
            successful_downloads = eval(
                successful_downloads
            )  # Converte a string para lista
            logger.info("Downloads convertidos de string para lista.")
        except Exception as e:
            logger.error(f"Erro ao converter downloads para lista: {e}")
            successful_downloads = []

    # Se não houver dados ou a lista for None, inicializa uma lista vazia
    if successful_downloads is None:
        successful_downloads = []

    # Retorna a lista de downloads bem-sucedidos
    return successful_downloads

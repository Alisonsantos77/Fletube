import re
import flet as ft


def validar_url_youtube(url: str) -> bool:
    """
    Valida se a URL fornecida é um link válido do YouTube.

    Args:
        url (str): A URL do vídeo.

    Returns:
        bool: True se a URL for válida, False caso contrário.
    """
    youtube_regex = r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$"
    return re.match(youtube_regex, url) is not None


def exibir_mensagem_erro(page: ft.Page, message: str):
    """
    Exibe uma mensagem de erro na interface.

    Args:
        page (ft.Page): A página atual da aplicação Flet.
        message (str): A mensagem de erro a ser exibida.
    """
    snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.colors.ERROR,
    )
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()


def validar_input(page: ft.Page, input_value: str) -> bool:
    """
    Valida o valor de entrada do usuário, verificando se o campo está vazio e se a URL é válida.

    Args:
        page (ft.Page): A página atual da aplicação Flet.
        input_value (str): O valor de entrada a ser validado.

    Returns:
        bool: True se o input for válido, False caso contrário.
    """
    if not input_value.strip():
        exibir_mensagem_erro(page, "O campo de link não pode estar vazio.")
        return False

    if not validar_url_youtube(input_value.strip()):
        exibir_mensagem_erro(
            page, "URL inválida. Por favor, insira um link válido do YouTube."
        )
        return False

    return True

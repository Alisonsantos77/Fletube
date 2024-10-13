import flet as ft


def setup_file_picker(page: ft.Page, on_directory_selected):
    """
    Configura o FilePicker para selecionar um diretório.

    Args:
        page (ft.Page): A página Flet onde o FilePicker será adicionado.
        on_directory_selected (function): Função callback que será chamada quando um diretório for selecionado.

    Returns:
        ft.FilePicker: O componente FilePicker configurado.
    """

    def get_directory_result(e: ft.FilePickerResultEvent):
        selected_directory = e.path if e.path else "Nenhum diretório selecionado!"
        on_directory_selected(selected_directory)

    file_picker = ft.FilePicker(on_result=get_directory_result)

    page.overlay.append(file_picker)

    return file_picker

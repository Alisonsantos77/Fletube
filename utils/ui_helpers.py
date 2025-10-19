import flet as ft


def show_snackbar(page: ft.Page, message: str, bgcolor=None, icon=None):
    """
    Exibe um snackbar estilizado com ícone e texto branco.

    Args:
        page: Página Flet
        message: Mensagem a exibir
        bgcolor: Cor de fundo (padrão: PRIMARY)
        icon: Ícone a exibir (opcional)
    """
    if bgcolor is None:
        bgcolor = ft.Colors.PRIMARY

    if icon is None:
        icon = ft.Icons.INFO_OUTLINED

    snackbar = ft.SnackBar(
        content=ft.Row(
            [
                ft.Icon(icon, color=ft.Colors.WHITE, size=20),
                ft.Text(
                    message,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            spacing=12,
        ),
        bgcolor=bgcolor,
        action="OK",
        action_color=ft.Colors.WHITE,
        duration=3000,
        behavior=ft.SnackBarBehavior.FLOATING,
        width=400,
    )
    snackbar.on_action = lambda e: None
    page.open(snackbar)


def show_error_snackbar(page: ft.Page, message: str):
    """Exibe snackbar de erro com ícone apropriado."""
    show_snackbar(page, message, ft.Colors.RED_700, ft.Icons.ERROR_OUTLINE)


def show_success_snackbar(page: ft.Page, message: str):
    """Exibe snackbar de sucesso com ícone apropriado."""
    show_snackbar(page, message, ft.Colors.GREEN_700, ft.Icons.CHECK_CIRCLE_OUTLINE)


def show_warning_snackbar(page: ft.Page, message: str):
    """Exibe snackbar de aviso com ícone apropriado."""
    show_snackbar(page, message, ft.Colors.ORANGE_700, ft.Icons.WARNING_AMBER_OUTLINED)


def show_info_snackbar(page: ft.Page, message: str):
    """Exibe snackbar informativo com ícone apropriado."""
    show_snackbar(page, message, ft.Colors.BLUE_700, ft.Icons.INFO_OUTLINED)

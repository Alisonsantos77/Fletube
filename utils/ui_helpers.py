import flet as ft


def show_snackbar(page: ft.Page, message: str, bgcolor=None):
    if bgcolor is None:
        bgcolor = ft.Colors.PRIMARY

    snackbar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=bgcolor,
        action="OK",
    )
    snackbar.on_action = lambda e: None
    page.open(snackbar)


def show_error_snackbar(page: ft.Page, message: str):
    show_snackbar(page, message, ft.Colors.ERROR)


def show_success_snackbar(page: ft.Page, message: str):
    show_snackbar(page, message, ft.Colors.GREEN)

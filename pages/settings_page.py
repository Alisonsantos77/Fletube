import flet as ft
from components.download_settings import DownloadSettings
from components.appearence_settings import AppearanceSettings
from components.general_settings import GeneralSettings
from components.contact_settings import ContactSettings

def SettingsPage(page: ft.Page):
    download_settings = DownloadSettings(page)
    appearance_settings = AppearanceSettings(page)
    general_settings = GeneralSettings(page)
    contact_settings = ContactSettings()

    return ft.SafeArea(
        content=ft.Column(
            controls=[
                ft.Text("Configurações", size=30, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                download_settings,
                appearance_settings,
                general_settings,
                contact_settings,
            ],
            spacing=20,
            expand=True,
        ),
        expand=True,
        top=True,
        bottom=True,
        left=False,
        right=False,
    )

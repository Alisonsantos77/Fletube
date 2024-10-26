import logging
import flet as ft
from routes import setup_routes
from utils.theme import BlueVibesDarkTheme, BlueVibesLightTheme
import os

# Configurar logging nativo
logging.basicConfig(
    filename="logs/app.log",  # Arquivo onde os logs serão armazenados
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,  # Nível de log (INFO ou DEBUG, conforme necessidade)
)
logging.getLogger("flet_core").setLevel(logging.INFO)


def toggle_theme(page: ft.Page, theme_mode: ft.ThemeMode):
    """
    Alterna o tema da aplicação e salva a escolha no client storage.
    """
    if theme_mode == ft.ThemeMode.DARK:
        page.theme = BlueVibesDarkTheme()
        logging.info("Tema: Dark")
    else:
        page.theme = BlueVibesLightTheme()
        logging.info("Tema: Light")

    page.theme_mode = theme_mode
    page.client_storage.set("theme_mode", theme_mode.name)
    page.update()


def main(page: ft.Page):
    # page.client_storage.clear()
    logging.info("Fletube iniciado")

    # Carregar o tema salvo no client_storage
    dark_theme_value = page.client_storage.get("dark_theme")
    if dark_theme_value is not None:
        theme_mode = ft.ThemeMode.DARK if dark_theme_value else ft.ThemeMode.LIGHT
        toggle_theme(page, theme_mode)
    else:
        toggle_theme(page, ft.ThemeMode.LIGHT)

    # Carregar a fonte salva no client_storage
    font_family_value = page.client_storage.get("font_family")
    if font_family_value is not None:
        page.fonts = {
            "Kanit": "/fonts/Kanit.ttf",
            "Open Sans": "/fonts/OpenSans.ttf",
            "BradBunR": "/fonts/BradBunR.ttf",
            "Heathergreen": "/fonts/Heathergreen.otf",
            "Ashemark": "/fonts/Ashemark regular.otf",
            "EmOne-SemiBold": "/fonts/EmOne-SemiBold.otf",
            "Gadner": "/fonts/Gadner.ttf",
        }
        page.theme = ft.Theme(font_family=font_family_value)
        page.update()

    page.title = "Fletube"

    # Gerenciar eventos de teclado
    def on_key_event(e: ft.KeyboardEvent):
        logging.info(f"Tecla: {e.key}")
        if e.key == "F1":
            page.go("/")
        elif e.key == "F2":
            page.go("/downloads")
        elif e.key == "F3":
            page.go("/historico")
        elif e.key == "F4":
            page.go("/configuracoes")

    page.on_keyboard_event = on_key_event

    setup_routes(page)
    page.update()


if __name__ == "__main__":
    logging.info("Inicializando Fletube")
    ft.app(target=main, assets_dir="assets")

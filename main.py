# main.py

import logging
import flet as ft
from routes import setup_routes
from services.send_feedback import (
    retry_failed_feedbacks,
    send_feedback_email,
    clean_feedback_backup,
)
from services.download_manager import DownloadManager

# Configuração de logging
logging.basicConfig(
    filename="logs/app.log",
    format="%(asctime)s %(levelname)s: %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("flet_core").setLevel(logging.INFO)


def apply_saved_theme_and_font(page: ft.Page):
    # Carregar e aplicar o tema salvo no client_storage
    theme_mode_value = page.client_storage.get("theme_mode") or "LIGHT"
    page.theme_mode = (
        ft.ThemeMode.DARK if theme_mode_value == "DARK" else ft.ThemeMode.LIGHT
    )
    logging.info(f"Tema carregado: {page.theme_mode}")

    # Carregar e aplicar a fonte salva no client_storage
    font_family_value = page.client_storage.get("font_family") or "Padrão"
    page.fonts = {
        "Kanit": "/fonts/Kanit.ttf",
        "Open Sans": "/fonts/OpenSans.ttf",
        "BradBunR": "/fonts/BradBunR.ttf",
        "Heathergreen": "/fonts/Heathergreen.otf",
        "Ashemark": "/fonts/Ashemark regular.otf",
        "EmOne-SemiBold": "/fonts/EmOne-SemiBold.otf",
        "Gadner": "/fonts/Gadner.ttf",
    }
    page.theme = (
        ft.Theme(font_family=font_family_value)
        if font_family_value != "Padrão"
        else ft.Theme()
    )
    logging.info(f"Fonte carregada: {font_family_value}")

    page.update()


def main(page: ft.Page):
    logging.info("Iniciando Fletube")
    
    download_manager = DownloadManager(page)

    # Tenta enviar feedbacks locais ao iniciar
    retry_failed_feedbacks(page)

    # Carregar e aplicar tema e fonte salvos antes de configurar a interface
    apply_saved_theme_and_font(page)

    # Configuração do título da página
    page.title = "Fletube"

    # Configuração de rotas, passando o DownloadManager
    setup_routes(page, download_manager)

    # Função para alternar tema
    def alternar_tema(e):
        current_theme = page.client_storage.get("theme_mode") or "LIGHT"
        new_theme_mode = (
            ft.ThemeMode.LIGHT if current_theme == "DARK" else ft.ThemeMode.DARK
        )
        page.theme_mode = new_theme_mode
        page.client_storage.set("theme_mode", new_theme_mode.name)
        page.update()

    # Configuração de evento de ciclo de vida da aplicação
    def handle_lifecycle_change(e: ft.AppLifecycleStateChangeEvent):
        if e.data == "inactive":
            logging.info("Aplicação em segundo plano")
            page.session.set("app_in_background", True)
        elif e.data == "active":
            logging.info("Aplicação voltou ao primeiro plano")
            page.session.set("app_in_background", False)
            page.update()

    # Atribuir o manipulador de ciclo de vida ao evento
    page.on_app_lifecycle_state_change = handle_lifecycle_change

    # Configurar evento de teclado para atalhos de navegação
    def on_key_event(e: ft.KeyboardEvent):
        if e.key.lower() == "f4":
            alternar_tema(None)
        elif e.key.lower() == "f1":
            page.go("/downloads")
        elif e.key.lower() == "f2":
            page.go("/historico")
        elif e.key.lower() == "f3":
            page.go("/configuracoes")

    page.on_keyboard_event = on_key_event

    # Atualizar a página final após todas as configurações
    page.update()


if __name__ == "__main__":
    logging.info("Inicializando aplicação Fletube")
    ft.app(target=main, assets_dir="assets")

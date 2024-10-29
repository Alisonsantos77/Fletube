import logging
import flet as ft
from routes import setup_routes
import os
# Configuração de logging
logging.basicConfig(
    filename="logs/app.log",
    format="%(asctime)s %(levelname)s: %(message)s",
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

    # Forçar atualização para aplicar tema e fonte
    page.update()

valores_venv = [
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
]

def main(page: ft.Page):
    logging.info("Iniciando Fletube")
    print(valores_venv)

    # Carregar e aplicar tema e fonte salvos antes de configurar a interface
    apply_saved_theme_and_font(page)

    # Configuração do título da página
    page.title = "Fletube"

    # Configuração de rotas
    setup_routes(page)

    # Função para alternar tema
    def alternar_tema(e):
        current_theme = page.client_storage.get("theme_mode") or "LIGHT"
        new_theme_mode = (
            ft.ThemeMode.LIGHT if current_theme == "DARK" else ft.ThemeMode.DARK
        )
        page.theme_mode = new_theme_mode
        page.client_storage.set("theme_mode", new_theme_mode.name)
        page.update()

    # Configurar evento de teclado para atalhos de navegação
    def on_key_event(e: ft.KeyboardEvent):
        logging.info(f"Tecla pressionada: {e.key}")
        if e.key.lower() == "t":
            alternar_tema(None)
        elif e.key == "F1":
            page.go("/home")
        elif e.key == "F2":
            page.go("/questions")
        elif e.key == "F3":
            page.go("/about")
        elif e.key == "F4":
            page.go("/score")
        elif e.key == "F5":
            page.go("/quiz")

    page.on_keyboard_event = on_key_event

    # Atualizar a página final após todas as configurações
    page.update()


if __name__ == "__main__":
    logging.info("Inicializando aplicação Fletube")
    ft.app(target=main, assets_dir="assets")

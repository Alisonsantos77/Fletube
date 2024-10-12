import logging
import flet as ft
from routes import setup_routes
from utils.theme import DarkVideoQTheme, RelaxVideoQTheme

# Configurar logging nativo
logging.basicConfig(
    filename="logs/app.log",  # Arquivo onde os logs serão armazenados
    format="%(asctime)s %(levelname)s: %(message)s",  # Formato dos logs
    level=logging.INFO,  # Nível de log (INFO ou DEBUG, conforme necessidade)
)
logging.getLogger("flet_core").setLevel(logging.INFO)


def toggle_theme(page: ft.Page, theme_mode: ft.ThemeMode):
    if theme_mode == ft.ThemeMode.DARK:
        page.theme = DarkVideoQTheme()
        logging.info("Tema: Dark")
    else:
        page.theme = RelaxVideoQTheme()
        logging.info("Tema: Light")
    page.theme_mode = theme_mode
    page.client_storage.set("theme_mode", theme_mode.name)
    page.update()


def main(page: ft.Page):
    logging.info("Fletube iniciado")

    theme_mode_value = page.client_storage.get("theme_mode")
    if theme_mode_value:
        try:
            theme_mode = ft.ThemeMode[theme_mode_value]
            toggle_theme(page, theme_mode)
        except KeyError:
            toggle_theme(page, ft.ThemeMode.LIGHT)
    else:
        toggle_theme(page, ft.ThemeMode.LIGHT)

    page.title = "Fletube"

    def alternar_tema(e):
        current_theme = page.client_storage.get("theme_mode") or "LIGHT"
        new_theme_mode = (
            ft.ThemeMode.LIGHT if current_theme == "DARK" else ft.ThemeMode.DARK
        )
        toggle_theme(page, new_theme_mode)

    shd = ft.ShakeDetector(
        minimum_shake_count=2,
        shake_slop_time_ms=300,
        shake_count_reset_time_ms=1000,
        on_shake=lambda _: print("SHAKE DETECTED!"),
    )
    page.overlay.append(shd)

    def on_key_event(e: ft.KeyboardEvent):
        logging.info(f"Tecla: {e.key}")
        if e.key == "F1":
            page.go("/home")
        elif e.key == "F2":
            page.go("/questions")
        elif e.key == "F3":
            page.go("/about")
        elif e.key == "F4":
            page.go("/score")
        elif e.key == "F5":
            page.go("/quiz")
        elif e.key.lower() == "t" or shd:
            alternar_tema(None)

    page.on_keyboard_event = on_key_event

    setup_routes(page)
    page.update()


if __name__ == "__main__":
    logging.info("Inicializando Fletube")
    ft.app(target=main, assets_dir="assets")

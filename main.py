import logging
from datetime import datetime, timezone
from pathlib import Path

import flet as ft

from routes import setup_routes
from services.download_manager import DownloadManager
from services.send_feedback import retry_failed_feedbacks
from services.storage_service import FletubeStorage
from services.supabase_utils import user_is_active
from utils.logging_config import get_logger, setup_logging
from utils.validations import AuthValidator

setup_logging()
logger = get_logger(__name__)


class AppState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.storage = FletubeStorage()
        self.download_manager = DownloadManager(page)

        self._initialize_defaults()

    def _initialize_defaults(self):
        if not self.storage.get_setting("initialized"):
            logger.info("Primeira execução detectada, configurando padrões...")

            defaults = {
                "theme_mode": "LIGHT",
                "font_family": "Padrão",
                "clipboard_monitoring": True,
                "default_format": "mp4",
                "initialized": True,
            }

            for key, value in defaults.items():
                self.storage.set_setting(key, value)
                self.page.client_storage.set(key, value)

            logger.info("Configurações padrão aplicadas com sucesso")


def verificar_status_usuario(page: ft.Page, max_retries: int = 3) -> bool:
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Verificando status do usuário (tentativa {attempt}/{max_retries})"
            )

            user_id = page.client_storage.get("user_id")

            if not user_id:
                logger.error("user_id não encontrado, redirecionando para login")
                return False

            cached_status = page.client_storage.get("user_status")
            last_checked = page.client_storage.get("last_checked") or 0
            current_time = datetime.now(timezone.utc).timestamp()

            cache_ttl = 600
            if cached_status and (current_time - last_checked) < cache_ttl:
                logger.info("Status do usuário obtido do cache")

                if cached_status == "inativo":
                    page.client_storage.clear()
                    return False

                return True

            is_active = user_is_active(user_id)

            status = "ativo" if is_active else "inativo"
            page.client_storage.set("user_status", status)
            page.client_storage.set("last_checked", current_time)

            if not is_active:
                logger.warning(f"Usuário {user_id} está inativo")
                page.client_storage.clear()
                return False

            logger.info(f"Usuário {user_id} verificado com sucesso")
            return True

        except Exception as e:
            logger.error(
                f"Erro ao verificar status do usuário (tentativa {attempt}): {e}"
            )

            if attempt < max_retries:
                import time

                delay = 2**attempt
                time.sleep(min(delay, 8))
            else:
                logger.critical("Falha permanente na verificação do usuário")
                return False

    return False


def apply_theme_and_fonts(page: ft.Page, app_state: AppState):
    theme_mode = app_state.storage.get_setting("theme_mode", "LIGHT")
    page.theme_mode = ft.ThemeMode.DARK if theme_mode == "DARK" else ft.ThemeMode.LIGHT
    logger.info(f"Tema aplicado: {theme_mode}")

    font_family = app_state.storage.get_setting("font_family", "Padrão")

    page.fonts = {
        "Baskervville": "/fonts/Baskervville.ttf",
        "Inter": "/fonts/Inter.ttf",
        "Nunito": "/fonts/Nunito.ttf",
        "Poppins": "/fonts/Poppins.otf",
        "Roboto": "/fonts/Roboto regular.otf",
        "EmOne-SemiBold": "/fonts/EmOne-SemiBold.otf",
        "Gadner": "/fonts/Gadner.ttf",
    }

    page.theme = (
        ft.Theme(font_family=font_family) if font_family != "Padrão" else ft.Theme()
    )
    logger.info(f"Fonte aplicada: {font_family}")

    page.update()


def setup_window_properties(page: ft.Page):
    page.window.min_width = 1600
    page.window.min_height = 900
    page.window.center()
    page.title = "Fletube"

def setup_keyboard_shortcuts(page: ft.Page, app_state: AppState):
    def toggle_theme():
        current_theme = app_state.storage.get_setting("theme_mode", "LIGHT")
        new_theme = "DARK" if current_theme == "LIGHT" else "LIGHT"

        page.theme_mode = (
            ft.ThemeMode.DARK if new_theme == "DARK" else ft.ThemeMode.LIGHT
        )
        app_state.storage.set_setting("theme_mode", new_theme)
        page.client_storage.set("theme_mode", new_theme)
        page.update()

        logger.info(f"Tema alternado para: {new_theme}")

    def on_key_event(e: ft.KeyboardEvent):
        key = e.key.lower()

        shortcuts = {
            "f1": "/downloads",
            "f2": "/historico",
            "f3": "/pagamento",
            "f4": "/feedback",
            "f5": "/configuracoes",
            "f6": lambda: toggle_theme(),
        }

        action = shortcuts.get(key)

        if action:
            if callable(action):
                action()
            else:
                page.go(action)
            logger.info(f"Atalho acionado: {key.upper()}")

    page.on_keyboard_event = on_key_event


def setup_lifecycle_handler(page: ft.Page):
    def handle_lifecycle_change(e: ft.AppLifecycleStateChangeEvent):
        if e.data == "inactive":
            logger.info("Aplicação em segundo plano")
            page.session.set("app_in_background", True)

            if page.client_storage.get("autenticado"):
                verificar_status_usuario(page)

        elif e.data == "active":
            logger.info("Aplicação voltou ao primeiro plano")
            page.session.set("app_in_background", False)
            page.update()

    page.on_app_lifecycle_state_change = handle_lifecycle_change


def initialize_app_services(page: ft.Page):
    retry_failed_feedbacks(page)
    logger.info("Tentativa de envio de feedbacks locais concluída")


def clear_invalid_auth(page: ft.Page):
    autenticado = page.client_storage.get("autenticado")
    user_id = page.client_storage.get("user_id")

    if autenticado and not user_id:
        logger.warning("Sessão inválida detectada, limpando storage")
        page.client_storage.clear()
        return True

    return False


def main(page: ft.Page):
    logger.info("🚀 Iniciando Fletube")

    setup_window_properties(page)

    clear_invalid_auth(page)

    if not AuthValidator.verify_auth(page):
        logger.warning("Usuário não autenticado, redirecionando para login")

        app_state = AppState(page)
        page.session.set("app_storage", app_state.storage)
        page.session.set("download_manager", app_state.download_manager)

        apply_theme_and_fonts(page, app_state)
        setup_routes(page, app_state.download_manager)

        page.go("/login")
        return

    app_state = AppState(page)

    page.session.set("app_storage", app_state.storage)
    page.session.set("download_manager", app_state.download_manager)

    apply_theme_and_fonts(page, app_state)

    setup_routes(page, app_state.download_manager)

    setup_keyboard_shortcuts(page, app_state)
    setup_lifecycle_handler(page)

    initialize_app_services(page)

    storage_info = app_state.storage.get_storage_info()
    logger.info(
        f"📊 Storage Info: {storage_info['downloads_count']} downloads, "
        f"{storage_info['settings_count']} configurações salvas"
    )

    page.update()

    logger.info("✅ Fletube inicializado com sucesso")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Fletube - Sistema de Download do YouTube")
    logger.info("=" * 60)
    ft.app(target=main, assets_dir="assets")

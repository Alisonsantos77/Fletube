import asyncio
import logging
import time
import flet as ft
import pysnooper
from routes import setup_routes
from services.send_feedback import (
    retry_failed_feedbacks,
    send_feedback_email,
    clean_feedback_backup,
)
from services.download_manager import DownloadManager
from datetime import datetime, timezone
from services.supabase_utils import user_is_active
from utils.validations import verify_auth
# Configuração de logging
logging.basicConfig(
    filename="logs/app.log",
    format="%(asctime)s %(levelname)s: %(name)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("flet_core").setLevel(logging.INFO)


@pysnooper.snoop()
def verificar_status_usuario(page):
    """
    Função que verifica o status do usuário, fazendo várias tentativas para acessar o 'user_id' no clientStorage e
    validando se o usuário está ativo ou não. A função aplica um backoff exponencial em caso de falhas ao tentar
    acessar os dados do usuário.

    O processo inclui:
    1. Verificar o 'user_id' no clientStorage.
    2. Usar um cache de status do usuário válido por 10 minutos para evitar chamadas repetitivas ao backend.
    3. Se o status do usuário não for encontrado ou o usuário for inativo, redireciona para a página de login.
    4. Caso contrário, a função armazena o status do usuário e a hora da última verificação no clientStorage.

    Parâmetros:
    page (ft.Page): A página atual da aplicação, usada para acessar o clientStorage e navegar entre páginas.

    Exceções:
    Se ocorrer um erro durante o processo, ele será registrado no log.
    """
    retries = 5  # Número máximo de tentativas
    initial_delay = 5  # Atraso inicial de 1 segundo
    max_delay = 32  # O backoff exponencial não deve exceder 32 segundos
    delay = initial_delay  # Começa com 1 segundo

    for attempt in range(retries):
        try:
            logging.info(
                f"Tentando acessar 'user_id' no clientStorage (tentativa {attempt + 1})...")

            # Verifica se o 'user_id' está armazenado no clientStorage
            user_id = page.client_storage.get("user_id")

            if user_id is None:
                logging.error("Chave 'user_id' não encontrada.")
                page.client_storage.clear()
                page.go("/login")
                return

            # Verifica se o status do usuário foi armazenado em cache e se está recente
            cached_status = page.client_storage.get("user_status")
            last_checked = page.client_storage.get("last_checked") or 0
            current_time = time.time()

            if cached_status and current_time - last_checked < 600:  # Cache válido por 10 minutos
                logging.info("Status do usuário obtido do cache.")
                if cached_status == "inativo":
                    page.client_storage.clear()
                    page.go("/login")
                    logging.info(
                        "Usuário inativo, redirecionando para a página de login.")
                return  # Usando o status do cache sem fazer outra requisição

            # Verifica o status do usuário
            if not user_is_active(user_id):
                page.client_storage.clear()
                page.go("/login")
                logging.info(
                    "Usuário inativo, redirecionando para a página de login.")

            # Cache o status do usuário e a hora da última verificação
            page.client_storage.set(
                "user_status", "ativo" if user_is_active(user_id) else "inativo")
            page.client_storage.set("last_checked", current_time)

            break  # Se conseguiu, sai do loop

        except Exception as e:
            logging.error(f"Erro ao verificar o status do usuário: {e}")
            # Aplica o backoff exponencial entre as tentativas
            # Limita o delay máximo a max_delay
            time.sleep(min(delay, max_delay))
            delay *= 2  # Dobra o tempo de espera a cada falha

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
    
    # Verificar se o usuário está autenticado
    if not verify_auth(page):
        logging.info("Usuário não autenticado")
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Faça login para acessar esta página."),
            bgcolor=ft.colors.RED_400,
        )
        page.snack_bar.open = True
        page.go("/login")


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
            # Verifica o status do usuário
            verificar_status_usuario(page)
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

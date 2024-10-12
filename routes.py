import logging
import flet as ft
from pages.download_page import DownloadPage
from pages.history_page import HistoryPage
from pages.settings_page import SettingsPage
from pages.page_404 import PageNotFound
from components.drawer import create_drawer

# Configurando o logging nativo
logging.basicConfig(
    filename="logs/app.log",  # Arquivo de logs
    format="%(asctime)s %(levelname)s: %(message)s",  # Formato das mensagens de log
    level=logging.INFO,  # Nível de log (INFO ou DEBUG, conforme necessário)
)
logging.getLogger("flet_core").setLevel(logging.INFO)


def setup_routes(page: ft.Page):
    logging.info("Configurando rotas")

    def route_change(route):
        logging.info(f"Rota alterada para: {route}")
        page.views.clear()
        page.views.append(
            ft.View(
                route="/downloads",
                appbar=ft.AppBar(bgcolor=ft.colors.TRANSPARENT),
                controls=[DownloadPage(page)],
                scroll=ft.ScrollMode.AUTO,
                drawer=create_drawer(page),
            )
        )
        if page.route == "/historico":
            page.title = "Histórico - Fletube"
            page.views.append(
                ft.View(
                    route="/historico",
                    appbar=ft.AppBar(bgcolor=ft.colors.TRANSPARENT),
                    controls=[HistoryPage(page)],
                    scroll=ft.ScrollMode.AUTO,
                    drawer=create_drawer(page),
                )
            )
        elif page.route == "/configuracoes":
            page.title = "Configurações - Fletube"
            page.views.append(
                ft.View(
                    route="/configuracoes",
                    appbar=ft.AppBar(bgcolor=ft.colors.TRANSPARENT),
                    controls=[SettingsPage(page)],
                    drawer=create_drawer(page),
                )
            )
        elif route == "/404":
            logging.warning(f"Rota desconhecida: {route}, redirecionando para 404")
            page.views.append(
                ft.View(
                    route="/404",
                    appbar=ft.AppBar(title=ft.Text("Página Não Encontrada")),
                    controls=[PageNotFound(page)],
                    drawer=create_drawer(page),
                )
            )
        page.update()

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            logging.info(f"Retornando para a rota anterior: {top_view.route}")
            page.go(top_view.route)
        else:
            logging.info("Sem mais views no histórico, retornando à home.")
            page.go("/downloads")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if not page.route:
        logging.info("Nenhuma rota especificada, redirecionando para a home")
        page.go("/downloads")
    else:
        route_change(page.route)

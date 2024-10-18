import logging
import flet as ft
from pages.download_page import DownloadPage
from pages.history_page import HistoryPage
from pages.settings_page import SettingsPage
from pages.page_404 import PageNotFound
from pages.login_page import LoginPage
from pages.feedback_page import FeedbackPage
from components.drawer import create_drawer
from components.user_menu import create_user_menu

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
        print(f"Rota alterada para: {route}")
        page.views.clear()
        # page.title = "Fletube"
        # page.views.append(
        #     ft.View(
        #         route="/",
        #         drawer=create_drawer(page),
        #         vertical_alignment=ft.MainAxisAlignment.CENTER,
        #         horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        #         controls=[LoginPage(page)],
        #     )
        # )

        page.title = "Downloads - Fletube"
        page.views.append(
            ft.View(
                route="/downloads",
                drawer=create_drawer(page),
                appbar=ft.AppBar(
                    bgcolor=ft.colors.TRANSPARENT,
                    actions=[create_user_menu(page)],
                ),
                controls=[DownloadPage(page)],
            )
        )

        if page.route == "/historico":
            page.title = "Histórico - Fletube"
            page.views.append(
                ft.View(
                    drawer=create_drawer(page),
                    route="/historico",
                    appbar=ft.AppBar(
                        bgcolor=ft.colors.TRANSPARENT,
                        actions=[create_user_menu(page)],
                    ),
                    controls=[HistoryPage(page)],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        elif page.route == "/configuracoes":
            page.title = "Configurações - Fletube"
            page.views.append(
                ft.View(
                    route="/configuracoes",
                    drawer=create_drawer(page),
                    appbar=ft.AppBar(
                        bgcolor=ft.colors.TRANSPARENT,
                        actions=[create_user_menu(page)],
                    ),
                    controls=[SettingsPage(page)],
                    scroll=ft.ScrollMode.AUTO,
                )
            )
        elif page.route == "/feedback":
            page.title = "Feedback - Fletube"
            page.views.append(
                ft.View(
                    route="/feedback",
                    drawer=create_drawer(page),
                    appbar=ft.AppBar(
                        bgcolor=ft.colors.TRANSPARENT,
                        actions=[create_user_menu(page)],
                    ),
                    controls=[FeedbackPage(page)],
                    scroll=ft.ScrollMode.AUTO,
                )
            )
        elif route == "/404":
            logging.warning(f"Rota desconhecida: {route}, redirecionando para 404")
            page.views.append(
                ft.View(
                    route="/404",
                    appbar=ft.AppBar(
                        title=ft.Text("Página Não Encontrada"),
                        drawer=create_drawer(page),
                        actions=[create_user_menu(page)],
                    ),
                    controls=[PageNotFound(page)],
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

import logging

import flet as ft

from components.drawer import create_drawer
from components.user_menu import create_user_menu
from pages.download_page import DownloadPage
from pages.feedback_page import FeedbackPage
from pages.history_page import HistoryPage
from pages.login_page import LoginPage
from pages.page_404 import PageNotFound
from pages.payment_page import PaymentPageView
from pages.settings_page import SettingsPage
from services.download_manager import DownloadManager
from utils.logging_config import get_logger, setup_logging

# Configuração de logging
logger = setup_logging()


def setup_routes(page: ft.Page, download_manager: DownloadManager):
    """
    Sistema de rotas moderno seguindo melhores práticas do Flet.
    Inspirado no padrão de views builders com guards de autenticação.
    """
    logger.info("🚀 Inicializando sistema de rotas")

    # ============================================================================
    # CONFIGURAÇÕES DE ROTAS
    # ============================================================================

    PUBLIC_ROUTES = ["/login"]
    PROTECTED_ROUTES = [
        "/downloads",
        "/historico",
        "/configuracoes",
        "/feedback",
        "/pagamento",
    ]

    # ============================================================================
    # GUARDS DE AUTENTICAÇÃO
    # ============================================================================

    def is_authenticated() -> bool:
        """Verifica se o usuário está autenticado."""
        authenticated = page.client_storage.get("autenticado")
        user_id = page.client_storage.get("user_id")

        logger.info(f"🔍 Verificando autenticação:")
        logger.info(f"  - autenticado: {authenticated}")
        logger.info(f"  - user_id: {user_id}")

        result = bool(authenticated and user_id)
        logger.info(f"🔐 Status de autenticação final: {result}")
        return result

    def require_auth(route: str) -> bool:
        """
        Guard de autenticação.
        Redireciona para login se não autenticado.
        """
        logger.info(f"🛡️ Guard de autenticação para rota: {route}")

        if not is_authenticated():
            logger.warning(f"⚠️ Acesso negado a {route} - usuário não autenticado")
            show_snackbar(
                "🔒 Faça login para acessar esta página", ft.Colors.ORANGE_700
            )
            page.go("/login")
            return False

        logger.info(f"✅ Acesso permitido a {route}")
        return True

    # ============================================================================
    # UTILITÁRIOS DE UI
    # ============================================================================

    def show_snackbar(message: str, color: str = ft.Colors.GREEN_700):
        """Exibe feedback visual para o usuário."""
        snackbar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO, color=ft.Colors.WHITE),
                    ft.Text(message, color=ft.Colors.WHITE),
                ],
                spacing=10,
            ),
            bgcolor=color,
            duration=3000,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
        logger.info(f"📢 Snackbar: {message}")

    def create_authenticated_appbar() -> ft.AppBar:
        """Cria AppBar padrão para rotas autenticadas."""
        return ft.AppBar(
            bgcolor=ft.Colors.TRANSPARENT, actions=[create_user_menu(page)]
        )

    # ============================================================================
    # VIEW BUILDERS (Pattern: Factory)
    # ============================================================================

    def build_root_view() -> ft.View:
        """View raiz vazia (sempre presente na stack)."""
        return ft.View(
            route="/",
            controls=[],
        )

    def build_login_view() -> ft.View:
        """
        View de login (pública).
        Não requer autenticação.
        """
        logger.info("🔑 Construindo view de login")
        return ft.View(
            route="/login",
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[LoginPage(page)],
            scroll=ft.ScrollMode.AUTO,
        )

    def build_downloads_view() -> ft.View:
        """
        View de downloads (protegida).
        Página inicial após login.
        """
        logger.info("📥 Construindo view de downloads")
        return ft.View(
            route="/downloads",
            drawer=create_drawer(page),
            appbar=create_authenticated_appbar(),
            controls=[DownloadPage(page, download_manager)],
        )

    def build_history_view() -> ft.View:
        """
        View de histórico (protegida).
        Exibe downloads anteriores.
        """
        logger.info("📜 Construindo view de histórico")
        return ft.View(
            route="/historico",
            drawer=create_drawer(page),
            appbar=create_authenticated_appbar(),
            controls=[HistoryPage(page)],
            scroll=ft.ScrollMode.AUTO,
        )

    def build_payment_view() -> ft.View:
        """
        View de pagamento (protegida).
        Exibe planos e facilita pagamento via PIX.
        """
        logger.info("💳 Construindo view de pagamento")
        return ft.View(
            route="/pagamento",
            drawer=create_drawer(page),
            appbar=create_authenticated_appbar(),
            controls=[PaymentPageView(page)],
            scroll=ft.ScrollMode.AUTO,
        )

    def build_settings_view() -> ft.View:
        """
        View de configurações (protegida).
        Gerencia preferências do usuário.
        """
        logger.info("⚙️ Construindo view de configurações")

        try:
            settings_page = SettingsPage(page)
            logger.info("✅ SettingsPage criada com sucesso")

            return ft.View(
                route="/configuracoes",
                drawer=create_drawer(page),
                appbar=create_authenticated_appbar(),
                controls=[settings_page],
                scroll=ft.ScrollMode.AUTO,
            )

        except Exception as e:
            logger.error(f"❌ ERRO ao criar SettingsPage: {e}", exc_info=True)

            # Fallback: exibe erro amigável
            return ft.View(
                route="/configuracoes",
                drawer=create_drawer(page),
                appbar=create_authenticated_appbar(),
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    ft.Icons.ERROR_OUTLINE,
                                    size=64,
                                    color=ft.Colors.RED_400,
                                ),
                                ft.Text(
                                    "Ops! Algo deu errado",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    str(e),
                                    size=14,
                                    color=ft.Colors.RED_300,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.ElevatedButton(
                                    "Voltar para Downloads",
                                    icon=ft.Icons.HOME,
                                    on_click=lambda _: page.go("/downloads"),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        padding=40,
                        alignment=ft.alignment.center,
                        expand=True,
                    )
                ],
            )

    def build_feedback_view() -> ft.View:
        """
        View de feedback (protegida).
        Coleta opinião do usuário.
        """
        logger.info("💬 Construindo view de feedback")
        return ft.View(
            route="/feedback",
            drawer=create_drawer(page),
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            appbar=create_authenticated_appbar(),
            controls=[FeedbackPage(page)],
        )

    def build_404_view() -> ft.View:
        """
        View de página não encontrada.
        Fallback para rotas inválidas.
        """
        logger.warning("🚫 Construindo view 404")
        return ft.View(
            route="/404",
            drawer=create_drawer(page),
            appbar=ft.AppBar(
                title=ft.Text("404 - Página Não Encontrada"),
                bgcolor=ft.Colors.TRANSPARENT,
                actions=[create_user_menu(page)],
            ),
            controls=[PageNotFound(page)],
        )

    # ============================================================================
    # ROTEADOR PRINCIPAL
    # ============================================================================

    def build_views_for_route(route: str):
        """
        Constrói a stack de views baseada na rota atual.
        Pattern: Strategy + Factory combinados.
        """
        logger.info(f"🎯 Processando rota: '{route}'")
        logger.info(f"📊 Views atuais antes de limpar: {len(page.views)}")

        # Limpa views anteriores
        page.views.clear()
        logger.info(f"🧹 Views limpas")

        # Sempre adiciona view raiz (necessário para navegação)
        page.views.append(build_root_view())
        logger.info(f"➕ View raiz adicionada")

        # ====================================================================
        # ROTEAMENTO CONDICIONAL
        # ====================================================================

        # Rota raiz -> redireciona baseado em autenticação
        if route == "/" or route == "":
            logger.info("🏠 Rota raiz detectada")
            if is_authenticated():
                logger.info("✅ Usuário autenticado, indo para /downloads")
                page.views.append(build_downloads_view())
            else:
                logger.info("❌ Usuário não autenticado, indo para /login")
                page.views.append(build_login_view())

        # Rotas públicas (sem autenticação necessária)
        elif route == "/login":
            logger.info("🔐 Rota de login")
            page.title = "Login - Fletube"
            page.views.append(build_login_view())

        # Rotas protegidas (requerem autenticação)
        elif route == "/downloads":
            logger.info("📥 Rota de downloads requisitada")
            if not require_auth(route):
                logger.warning("⛔ Autenticação falhou, abortando")
                return
            page.title = "Downloads - Fletube"
            page.views.append(build_downloads_view())
            logger.info("✅ View de downloads adicionada")

        elif route == "/historico":
            logger.info("📜 Rota de histórico requisitada")
            if not require_auth(route):
                return
            page.title = "Histórico - Fletube"
            page.views.append(build_history_view())

        elif route == "/configuracoes":
            logger.info("⚙️ Rota de configurações requisitada")
            if not require_auth(route):
                return
            page.title = "Configurações - Fletube"
            page.views.append(build_settings_view())

        elif route == "/feedback":
            logger.info("💬 Rota de feedback requisitada")
            if not require_auth(route):
                return
            page.title = "Feedback - Fletube"
            page.views.append(build_feedback_view())

        elif route == "/pagamento":
            logger.info("💳 Rota de pagamento requisitada")
            if not require_auth(route):
                return
            page.title = "Pagamento - Fletube"
            page.views.append(build_payment_view())

        # Rota desconhecida -> 404
        else:
            logger.warning(f"⚠️ Rota não encontrada: {route}")
            page.title = "404 - Fletube"
            page.views.append(build_404_view())

        logger.info(f"📊 Total de views na stack: {len(page.views)}")
        logger.info(f"✅ Rota {route} construída com sucesso")

    # ============================================================================
    # EVENT HANDLERS
    # ============================================================================

    def route_change(e: ft.RouteChangeEvent):
        """
        Handler principal de mudança de rotas.
        Intercepta navegação e constrói views apropriadas.
        """
        try:
            current_route = e.route if e and e.route else page.route
            logger.info("=" * 60)
            logger.info(f"🔔 EVENTO DE MUDANÇA DE ROTA DISPARADO")
            logger.info(f"📍 Rota solicitada: '{current_route}'")
            logger.info(f"📍 page.route: '{page.route}'")
            logger.info("=" * 60)

            build_views_for_route(current_route)

            logger.info("🔄 Atualizando página...")
            page.update()
            logger.info("✅ Página atualizada com sucesso")

            logger.info(f"✅ Navegação concluída: {current_route}")
            logger.info("=" * 60)

        except Exception as ex:
            logger.error("=" * 60)
            logger.error(f"❌ ERRO CRÍTICO ao processar rota {current_route}")
            logger.error(f"Detalhes: {ex}", exc_info=True)
            logger.error("=" * 60)

            # Fallback de emergência
            show_snackbar(f"Erro ao carregar página: {str(ex)}", ft.Colors.RED_700)

            page.views.clear()
            page.views.append(build_root_view())
            page.views.append(build_login_view())
            page.update()

    def view_pop(e: ft.ViewPopEvent):
        """
        Handler de navegação para trás (botão voltar).
        Gerencia stack de views corretamente.
        """
        try:
            logger.info("⬅️ View pop solicitado")

            if len(page.views) > 1:
                page.views.pop()
                top_view = page.views[-1]
                logger.info(f"⬅️ Navegando para: {top_view.route}")
                page.go(top_view.route)
            else:
                # Stack vazia -> volta pra home
                default_route = "/downloads" if is_authenticated() else "/login"
                logger.info(f"⬅️ Stack vazia, indo para {default_route}")
                page.go(default_route)

        except Exception as ex:
            logger.error(f"❌ Erro no view_pop: {ex}", exc_info=True)
            page.go("/login")

        page.update()

    # ============================================================================
    # REGISTRO DE HANDLERS
    # ============================================================================

    logger.info("📝 Registrando handlers de rotas...")
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    logger.info("✅ Handlers registrados com sucesso")

    # ============================================================================
    # INICIALIZAÇÃO
    # ============================================================================

    # Define rota inicial
    initial_route = page.route if page.route else "/"
    logger.info(f"🏁 Rota inicial: '{initial_route}'")
    logger.info(f"🔄 Executando page.go('{initial_route}')...")
    page.go(initial_route)
    logger.info(f"✅ page.go() executado")

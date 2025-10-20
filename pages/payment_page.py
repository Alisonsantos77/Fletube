import random
import threading
from math import pi

import flet as ft
from loguru import logger


class AnimatedCard(ft.Container):
    """Card com animações suaves e modernas"""

    def __init__(self, content, **kwargs):
        super().__init__()
        self.content = content
        self.padding = 24
        self.border_radius = 16
        self.border = ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        self.animate = ft.Animation(800, ft.AnimationCurve.EASE_OUT)
        self.animate_scale = ft.Animation(300, ft.AnimationCurve.ELASTIC_OUT)
        self.animate_opacity = ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT)
        self.scale = 1
        self.opacity = 1

        for key, value in kwargs.items():
            setattr(self, key, value)


class FletubeAvatar(ft.Container):
    """Avatar animado do Fletube com múltiplas animações"""

    def __init__(self):
        super().__init__()
        self.icon_ref = ft.Icon(
            ft.Icons.MOVIE_FILTER_ROUNDED,
            size=80,
            color=ft.Colors.PRIMARY,
        )

        self.content = self.icon_ref
        self.width = 120
        self.height = 120
        self.border_radius = 60
        self.border = ft.border.all(3, ft.Colors.PRIMARY)
        self.alignment = ft.alignment.center
        self.animate_rotation = ft.Animation(1000, ft.AnimationCurve.ELASTIC_OUT)
        self.animate_scale = ft.Animation(400, ft.AnimationCurve.BOUNCE_OUT)
        self.rotate = 0
        self.scale = 1

    def animate_avatar(self):
        """Anima o avatar com rotação e escala"""
        self.rotate += pi / 2
        self.scale = 1.15
        self.update()

        def reset_scale():
            self.scale = 1
            if hasattr(self, "page") and self.page:
                self.update()

        timer = threading.Timer(0.4, reset_scale)
        timer.start()


class PixKeyCard(ft.Container):
    """Card da chave PIX com animações de feedback"""

    def __init__(self, pix_key, on_copy):
        super().__init__()
        self.pix_key = pix_key
        self.padding = 24
        self.border = ft.border.all(2, ft.Colors.PRIMARY)
        self.border_radius = 16
        self.animate_scale = ft.Animation(200, ft.AnimationCurve.BOUNCE_OUT)
        self.scale = 1

        self.copy_button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.COPY_ALL, size=24),
                    ft.Text(
                        "COPIAR CHAVE PIX",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            border=ft.border.all(2, ft.Colors.PRIMARY),
            border_radius=12,
            padding=ft.padding.symmetric(vertical=16, horizontal=24),
            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            ink=True,
            on_click=on_copy,
            scale=1,
        )

        self.content = ft.Column(
            [
                ft.Icon(ft.Icons.PIX, size=56, color=ft.Colors.PRIMARY),
                ft.Container(height=8),
                ft.Text(
                    "💰 Chave PIX",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.PRIMARY,
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Text(
                        pix_key,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        selectable=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    border_radius=8,
                    padding=12,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                ),
                ft.Container(height=16),
                self.copy_button,
                ft.Container(height=8),
                ft.Text(
                    "Cole no seu app e escolha o valor do plano! 🚀",
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

    def animate_copy_success(self):
        """Anima feedback de cópia bem-sucedida"""
        self.copy_button.scale = 0.9
        self.copy_button.update()

        def reset():
            self.copy_button.scale = 1
            self.copy_button.update()

        timer = threading.Timer(0.15, reset)
        timer.start()


class PlanCard(ft.Container):
    """Card de plano com hover e animações"""

    def __init__(self, days: int, price: str, recommended: bool = False):
        super().__init__()

        self.padding = 28
        self.border_radius = 16
        self.animate_scale = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.animate_opacity = ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT)
        self.scale = 1
        self.opacity = 1

        if recommended:
            self.border = ft.border.all(4, ft.Colors.ORANGE_600)
        else:
            self.border = ft.border.all(2, ft.Colors.OUTLINE_VARIANT)

        self.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=24 if recommended else 12,
            color=ft.Colors.with_opacity(
                0.2 if recommended else 0.08, ft.Colors.PRIMARY
            ),
            offset=ft.Offset(0, 6),
        )

        # Badge de recomendado
        badge = ft.Container(
            content=ft.Text(
                "⭐ MAIS ESCOLHIDO",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            border=ft.border.all(2, ft.Colors.ORANGE_600),
            padding=ft.padding.symmetric(horizontal=14, vertical=7),
            border_radius=20,
            visible=recommended,
        )

        # Preço principal
        price_display = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("R$", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            price,
                            size=64,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.PRIMARY,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                ),
                ft.Text(
                    f"{days} dias de acesso",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )

        # Cálculo do custo diário
        daily_cost = float(price.replace(",", ".")) / days

        # Features do plano
        features = [
            ("✅", "Downloads ilimitados"),
            ("✅", "Qualidade máxima"),
            ("✅", "Sem anúncios"),
            ("✅", "Suporte técnico"),
            ("💰", f"Apenas R$ {daily_cost:.2f}/dia"),
        ]

        feature_items = [
            ft.Row(
                [
                    ft.Text(icon, size=20),
                    ft.Text(text, size=15, weight=ft.FontWeight.W_500),
                ],
                spacing=12,
            )
            for icon, text in features
        ]

        self.content = ft.Column(
            [
                badge,
                ft.Container(height=12 if recommended else 24),
                price_display,
                ft.Divider(height=32, thickness=2),
                ft.Column(
                    feature_items,
                    spacing=14,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )


class PaymentPageHandlers:
    """Handlers de eventos da página de pagamento"""

    def __init__(self, page: ft.Page, pix_key: str, avatar, pix_card=None):
        self.page = page
        self.pix_key = pix_key
        self.avatar = avatar
        self.pix_card = pix_card

    def copy_pix_key(self, e=None):
        """Copia a chave PIX para a área de transferência"""
        try:
            self.page.set_clipboard(self.pix_key)

            if self.pix_card:
                self.pix_card.animate_copy_success()

            self._show_snackbar(
                "✅ PIX copiado! Abra seu banco e cole!",
                ft.Colors.GREEN_600,
                ft.Icons.CHECK_CIRCLE,
            )

            self.avatar.animate_avatar()

        except Exception as ex:
            logger.error(f"Erro ao copiar PIX: {ex}")
            self._show_snackbar(
                "Erro ao copiar 😞", ft.Colors.RED_600, ft.Icons.ERROR_OUTLINE
            )

    def animate_avatar_click(self, e):
        """Anima o avatar ao clicar"""
        try:
            self.avatar.animate_avatar()

            messages = [
                "Obrigado pelo apoio! 💙",
                "Você é incrível! ⭐",
                "Juntos vamos longe! 🚀",
                "Sua ajuda faz diferença! 💪",
                "Gratidão eterna! 🙏",
                "Você acredita no Fletube! ✨",
            ]

            message = random.choice(messages)
            self._show_snackbar(message, ft.Colors.BLUE_600, ft.Icons.FAVORITE)

        except Exception as e:
            logger.error(f"Erro ao animar avatar: {e}")

    def _show_snackbar(self, message: str, color: str, icon):
        """Exibe snackbar animado com feedback visual"""
        snackbar = ft.SnackBar(
            content=ft.Row(
                [
                    ft.Icon(icon, size=22),
                    ft.Text(
                        message,
                        weight=ft.FontWeight.W_600,
                        size=15,
                    ),
                ],
                spacing=10,
            ),
            duration=2500,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.margin.all(12),
            elevation=10,
            shape=ft.RoundedRectangleBorder(radius=12),
            open=True,
        )

        self.page.overlay.append(snackbar)
        self.page.update()


def PaymentPageView(page: ft.Page) -> ft.Container:
    """
    Cria a página de pagamento do Fletube

    Args:
        page: Instância da página Flet

    Returns:
        Container com a interface de pagamento
    """

    PIX_KEY = "alisondev77@hotmail.com"

    # Criação do avatar
    avatar = FletubeAvatar()
    pix_card_ref = []

    # Handlers de eventos
    handlers = PaymentPageHandlers(page, PIX_KEY, avatar)
    avatar.on_click = handlers.animate_avatar_click

    # ============================================================================
    # SEÇÃO HERO - Boas-vindas
    # ============================================================================
    hero_section = AnimatedCard(
        content=ft.Column(
            [
                ft.GestureDetector(
                    content=avatar,
                    on_tap=handlers.animate_avatar_click,
                ),
                ft.Container(height=12),
                ft.Text(
                    "Bem-vindo ao Fletube Premium!",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.PRIMARY,
                ),
                ft.Container(height=8),
                ft.Text(
                    "Escolha seu plano e baixe sem limites! 🎬",
                    size=18,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Text(
                        "💡 Toque no ícone para me animar! 😊",
                        size=13,
                        text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(italic=True),
                    ),
                    padding=12,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
    )

    # ============================================================================
    # SEÇÃO DE PLANOS - Cards de assinatura
    # ============================================================================
    plans_section = AnimatedCard(
        content=ft.Column(
            [
                ft.Text(
                    "📋 Nossos Planos",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                ft.Text(
                    "Todos os planos incluem acesso completo ao Fletube",
                    size=15,
                    text_align=ft.TextAlign.CENTER,
                    style=ft.TextStyle(italic=True),
                ),
                ft.Container(height=24),
                ft.Row(
                    [
                        PlanCard(days=7, price="5,00"),
                        PlanCard(days=21, price="12,00", recommended=True),
                        PlanCard(days=30, price="15,00"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=24,
                    wrap=True,
                ),
            ],
            spacing=0,
        ),
    )

    # ============================================================================
    # SEÇÃO PIX - Informações de pagamento
    # ============================================================================
    pix_card = PixKeyCard(PIX_KEY, handlers.copy_pix_key)
    pix_card_ref.append(pix_card)
    handlers.pix_card = pix_card

    pix_section = AnimatedCard(
        content=ft.Column(
            [
                ft.Text(
                    "💳 Como Pagar",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                ft.Text(
                    "Pagamento instantâneo via PIX",
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(height=20),
                pix_card,
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "📝 Passo a passo:",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(height=12),
                            _create_step("1", "Copie a chave PIX acima"),
                            _create_step("2", "Abra seu aplicativo bancário"),
                            _create_step("3", "Faça o PIX com o valor do plano"),
                            _create_step("4", "Envie o comprovante no suporte"),
                        ],
                        spacing=12,
                    ),
                    padding=24,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
    )

    # ============================================================================
    # SEÇÃO DE BENEFÍCIOS
    # ============================================================================
    benefits_section = AnimatedCard(
        content=ft.Column(
            [
                ft.Text(
                    "🎯 Por Que Assinar?",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                ft.Row(
                    [
                        _create_benefit_card(
                            "🚀", "Velocidade", "Downloads super rápidos"
                        ),
                        _create_benefit_card("🎬", "Qualidade", "Até 4K de resolução"),
                        _create_benefit_card("⚡", "Ilimitado", "Sem limites de uso"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=24,
                    wrap=True,
                ),
            ],
            spacing=0,
        ),
    )

    # ============================================================================
    # SEÇÃO DE SUPORTE
    # ============================================================================
    support_section = AnimatedCard(
        content=ft.Column(
            [
                ft.Text(
                    "💬 Precisa de Ajuda?",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=12),
                ft.Text(
                    "Entre em contato e ative seu plano rapidamente!",
                    size=15,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Falar com Suporte",
                    icon=ft.Icons.SUPPORT_AGENT,
                    width=280,
                    height=56,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                    on_click=lambda _: page.launch_url("https://wa.link/tr8dei"),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
    )

    # ============================================================================
    # SEÇÃO DE GRATIDÃO
    # ============================================================================
    gratitude_section = AnimatedCard(
        content=ft.Column(
            [
                ft.Text(
                    "🙏 Obrigado por Apoiar!",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=12),
                ft.Text(
                    "Cada assinatura nos ajuda a manter o Fletube sempre ativo\n"
                    "e em constante evolução. Você faz parte desta história!",
                    size=15,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.SECURITY, color=ft.Colors.GREEN, size=22),
                            ft.Text("100% Seguro", size=13, weight=ft.FontWeight.W_500),
                            ft.Container(width=20),
                            ft.Icon(ft.Icons.FLASH_ON, color=ft.Colors.ORANGE, size=22),
                            ft.Text(
                                "PIX Instantâneo", size=13, weight=ft.FontWeight.W_500
                            ),
                            ft.Container(width=20),
                            ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.RED, size=22),
                            ft.Text(
                                "Feito com Amor", size=13, weight=ft.FontWeight.W_500
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        wrap=True,
                        spacing=8,
                    ),
                    padding=20,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                ),
                ft.Container(height=12),
                ft.Text(
                    "🎬 Fletube - Baixe o que você ama, quando quiser!",
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                    weight=ft.FontWeight.BOLD,
                    style=ft.TextStyle(italic=True),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
    )

    # ============================================================================
    # COLUNA PRINCIPAL
    # ============================================================================
    main_content = ft.Column(
        [
            hero_section,
            plans_section,
            pix_section,
            benefits_section,
            support_section,
            gratitude_section,
        ],
        spacing=28,
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ============================================================================
    # ANIMAÇÃO DE BOAS-VINDAS
    # ============================================================================
    def show_welcome():
        """Mostra mensagem de boas-vindas após carregar"""
        try:

            def delayed_welcome():
                try:
                    handlers._show_snackbar(
                        "Bem-vindo! 🎬 Escolha seu plano!",
                        ft.Colors.BLUE_600,
                        ft.Icons.WAVING_HAND,
                    )
                except Exception as e:
                    logger.error(f"Erro ao mostrar boas-vindas: {e}")

            timer = threading.Timer(0.8, delayed_welcome)
            timer.start()

        except Exception as e:
            logger.error(f"Erro ao configurar boas-vindas: {e}")

    show_welcome()

    return ft.Container(
        content=main_content,
        padding=24,
        expand=True,
    )


def _create_step(number: str, text: str) -> ft.Row:
    """Cria um item de passo a passo"""
    return ft.Row(
        [
            ft.Container(
                content=ft.Text(
                    number,
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
                width=32,
                height=32,
                border_radius=16,
                border=ft.border.all(2, ft.Colors.PRIMARY),
                alignment=ft.alignment.center,
            ),
            ft.Text(
                text,
                size=15,
                weight=ft.FontWeight.W_500,
            ),
        ],
        spacing=12,
    )


def _create_benefit_card(icon: str, title: str, description: str) -> ft.Container:
    """Cria um card de benefício"""
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text(icon, size=36),
                    width=70,
                    height=70,
                    border_radius=35,
                    border=ft.border.all(2, ft.Colors.PRIMARY),
                    alignment=ft.alignment.center,
                ),
                ft.Container(height=8),
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=4),
                ft.Text(
                    description,
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=24,
        width=190,
        border_radius=12,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
    )

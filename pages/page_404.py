import asyncio
import random
from math import pi

import flet as ft


def PageNotFound(page: ft.Page):

    error_icon = ft.Container(
        content=ft.Icon(
            ft.Icons.SEARCH_OFF_ROUNDED,
            size=180,
            color=ft.Colors.PRIMARY,
        ),
        animate_rotation=ft.Animation(1500, ft.AnimationCurve.ELASTIC_OUT),
        animate_scale=ft.Animation(3000, ft.AnimationCurve.EASE_IN_OUT),
        rotate=0,
        scale=1,
    )

    def animate_icon():
        error_icon.rotate += pi / 2
        error_icon.scale = 1.25
        error_icon.update()

        import threading

        def reset():
            error_icon.scale = 1
            error_icon.update()

        timer = threading.Timer(0.4, reset)
        timer.start()

    error_code = ft.Text(
        "404",
        size=140,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.PRIMARY,
    )

    error_title = ft.Text(
        "Página Não Encontrada",
        size=42,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.LEFT,
    )

    error_description = ft.Text(
        "A página que você está procurando não existe ou foi movida.",
        size=18,
        text_align=ft.TextAlign.LEFT,
        color=ft.Colors.ON_SURFACE_VARIANT,
    )

    fun_messages = [
        "🎬 Parece que este vídeo não existe...",
        "🚀 Houston, temos um problema!",
        "🎯 Ops! Você se perdeu?",
        "🌌 Esta página foi para outra dimensão!",
        "🎪 Nada por aqui, circule!",
    ]

    fun_text = ft.Text(
        random.choice(fun_messages),
        size=16,
        italic=True,
        text_align=ft.TextAlign.LEFT,
        color=ft.Colors.ON_SURFACE_VARIANT,
    )

    suggestions = [
        ("🏠", "Voltar ao Início", "/downloads"),
        ("📥", "Ver Downloads", "/downloads"),
        ("📜", "Ver Histórico", "/historico"),
        ("⚙️", "Configurações", "/configuracoes"),
    ]

    def create_suggestion_button(icon, label, route):
        button = ft.Container(
            content=ft.Row(
                [
                    ft.Text(icon, size=24),
                    ft.Text(label, size=16, weight=ft.FontWeight.W_600),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            border_radius=12,
            border=ft.border.all(2, ft.Colors.PRIMARY),
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            scale=1,
            ink=True,
            on_click=lambda e: page.go(route),
            width=280,
        )

        def on_hover(e):
            button.scale = 1.05 if e.data == "true" else 1
            button.update()

        button.on_hover = on_hover

        return button

    suggestion_buttons = [
        create_suggestion_button(icon, label, route)
        for icon, label, route in suggestions
    ]

    def start_pulse():
        import threading

        def pulse_loop():
            if error_icon.page:
                current = error_icon.scale
                error_icon.scale = 1.15 if current == 1 else 1
                try:
                    error_icon.update()
                except:
                    pass
                threading.Timer(2.5, pulse_loop).start()

        threading.Timer(2.5, pulse_loop).start()

    # Lado esquerdo - Visual (Ícone e código 404)
    left_side = ft.Container(
        content=ft.Column(
            [
                ft.GestureDetector(
                    content=error_icon,
                    on_tap=lambda e: animate_icon(),
                ),
                ft.Container(height=30),
                error_code,
                ft.Container(height=20),
                ft.Container(
                    content=ft.Text(
                        "💡 Toque no ícone para animar!",
                        size=13,
                        text_align=ft.TextAlign.CENTER,
                        italic=True,
                    ),
                    padding=12,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.all(40),
        expand=1,
    )

    # Lado direito - Informações e ações
    right_side = ft.Container(
        content=ft.Column(
            [
                error_title,
                ft.Container(height=16),
                error_description,
                ft.Container(height=12),
                fun_text,
                ft.Container(height=40),
                ft.Text(
                    "Sugestões:",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=20),
                ft.Column(
                    [
                        suggestion_buttons[0],
                        ft.Container(height=12),
                        suggestion_buttons[1],
                        ft.Container(height=12),
                        suggestion_buttons[2],
                        ft.Container(height=12),
                        suggestion_buttons[3],
                    ],
                    spacing=0,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.all(40),
        expand=1,
    )

    # Layout horizontal principal
    page_content = ft.Container(
        content=ft.Row(
            [
                left_side,
                ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT),
                right_side,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            expand=True,
        ),
        expand=True,
    )

    start_pulse()

    return page_content

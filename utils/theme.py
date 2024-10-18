import flet as ft


def BlueVibesDarkTheme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            # Cores primárias
            primary="#0077B6",  # Azul médio, vibrante
            on_primary="#fefeff",  # Texto branco sobre a cor primária para contraste
            # Cores de fundo e superfícies
            background="#03045E",  # Fundo azul marinho profundo
            on_background="#fefeff",  # Texto branco sobre fundo
            surface="#023E8A",  # Superfícies em azul escuro
            on_surface="#fefeff",  # Texto branco sobre superfícies
            # Cores secundárias
            secondary="#00B4D8",  # Azul claro secundário
            on_secondary="#fefeff",  # Texto branco sobre cor secundária
        )
    )


def BlueVibesLightTheme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            # Cores primárias
            primary="#0096C7",  # Azul brilhante, suave
            on_primary="#03045E",  # Texto azul escuro para contraste com a cor primária
            # Cores de fundo e superfícies
            background="#CAF0F8",  # Fundo azul muito claro, vibrante
            on_background="#023E8A",  # Texto azul escuro sobre fundo
            surface="#ADE8F4",  # Superfícies em azul claro
            on_surface="#03045E",  # Texto azul escuro sobre superfícies
            # Cores secundárias
            secondary="#48CAE4",  # Azul aqua secundário
            on_secondary="#03045E",  # Texto azul escuro sobre cor secundária
        )
    )

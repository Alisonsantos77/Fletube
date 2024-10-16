import flet as ft


def BlueVibesDarkTheme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#0077B6",  # Cor principal vibrante (azul médio)
            on_primary="#fefeff",  # Texto sobre a cor primária (branco para contraste)
            background="#03045E",  # Cor de fundo escura (azul marinho profundo)
            surface="#023E8A",  # Cor de superfícies (azul escuro)
            on_surface="#fefeff",  # Texto sobre superfícies (branco para contraste)
            secondary="#00B4D8",  # Cor secundária (azul claro)
            on_secondary="#fefeff",  # Texto sobre a cor secundária (branco)
            on_background="#fefeff",  # Texto sobre fundo (branco)
        )
    )


def BlueVibesLightTheme():
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#0096C7",  # Cor principal suave (azul brilhante)
            on_primary="#03045E",  # Texto sobre a cor primária (azul escuro para contraste)
            background="#CAF0F8",  # Cor de fundo vibrante (azul muito claro)
            surface="#ADE8F4",  # Cor de superfícies (azul claro)
            on_surface="#03045E",  # Texto sobre superfícies (azul escuro)
            secondary="#48CAE4",  # Cor secundária (azul aqua)
            on_secondary="#03045E",  # Texto sobre a cor secundária (azul escuro)
            on_background="#023E8A",  # Texto sobre fundo (azul escuro)
        )
    )

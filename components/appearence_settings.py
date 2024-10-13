import flet as ft
from utils.fonts_loader import load_custom_fonts


def AppearanceSettings(page: ft.Page):
    theme_switch_ref = ft.Ref[ft.Switch]()
    font_dropdown_ref = ft.Ref[ft.Dropdown]()

    # Obter o valor do tema escuro e definir o valor padrão se necessário
    dark_theme_value = page.client_storage.get("dark_theme")
    if dark_theme_value is None:
        dark_theme_value = False

    theme_switch = ft.Switch(
        label="Tema Escuro",
        ref=theme_switch_ref,
        value=dark_theme_value,
        on_change=lambda e: toggle_theme(e.control.value),
    )

    def toggle_theme(is_dark):
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.client_storage.set("dark_theme", is_dark)
        page.update()

    def update_font_family(font_family):
        page.client_storage.set("font_family", font_family)
        if font_family == "Padrão":
            page.theme = ft.Theme()
        else:
            page.fonts = load_custom_fonts(font_family)
            page.theme = ft.Theme(font_family=font_family)
        page.update()

    font_options = ["Padrão", "Kanit", "Open Sans"]

    # Obter o valor da fonte da aplicação e definir o valor padrão se necessário
    font_family_value = page.client_storage.get("font_family")
    if font_family_value is None:
        font_family_value = "Padrão"

    font_dropdown = ft.Dropdown(
        ref=font_dropdown_ref,
        label="Fonte da Aplicação",
        options=[ft.dropdown.Option(font) for font in font_options],
        value=font_family_value,
        on_change=lambda e: update_font_family(e.control.value),
    )

    return ft.ResponsiveRow(
        [
            ft.Container(
                content=theme_switch,
                col={"sm": 12, "md": 6},
            ),
            ft.Container(
                content=font_dropdown,
                col={"sm": 12, "md": 6},
            ),
        ],
        run_spacing=10,
    )

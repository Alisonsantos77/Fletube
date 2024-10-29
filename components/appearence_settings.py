import flet as ft


def AppearanceSettings(page: ft.Page):
    theme_switch_ref = ft.Ref[ft.Switch]()
    font_dropdown_ref = ft.Ref[ft.Dropdown]()

    # Obter o tema salvo ou padrão para LIGHT
    theme_mode_value = page.client_storage.get("theme_mode") or "LIGHT"
    is_dark_theme = theme_mode_value == "DARK"
    page.theme_mode = ft.ThemeMode.DARK if is_dark_theme else ft.ThemeMode.LIGHT

    # Switch para alternar tema
    theme_switch = ft.Switch(
        label="Tema Escuro",
        ref=theme_switch_ref,
        value=is_dark_theme,
        on_change=lambda e: toggle_theme(e.control.value),
    )

    def toggle_theme(is_dark):
        new_theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.theme_mode = new_theme_mode
        page.client_storage.set("theme_mode", new_theme_mode.name)
        page.update()

    def update_font_family(font_family):
        page.client_storage.set("font_family", font_family)
        page.theme = (
            ft.Theme(font_family=font_family) if font_family != "Padrão" else ft.Theme()
        )
        page.update()

    # Carregar e aplicar o valor da fonte salva
    font_family_value = page.client_storage.get("font_family") or "Padrão"
    font_options = [
        "Padrão",
        "Kanit",
        "Open Sans",
        "BradBunR",
        "Heathergreen",
        "Ashemark",
        "EmOne-SemiBold",
        "Gadner",
    ]

    font_dropdown = ft.Dropdown(
        ref=font_dropdown_ref,
        label="Fonte da Aplicação",
        options=[ft.dropdown.Option(font) for font in font_options],
        value=font_family_value,
        on_change=lambda e: update_font_family(e.control.value),
    )

    return ft.ResponsiveRow(
        [
            ft.Container(content=theme_switch, col={"sm": 12, "md": 6}),
            ft.Container(content=font_dropdown, col={"sm": 12, "md": 6}),
        ],
        run_spacing=10,
    )

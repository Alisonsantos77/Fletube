import flet as ft


def AppearanceSettings(page: ft.Page):
    theme_switch_ref = ft.Ref[ft.Switch]()
    font_dropdown_ref = ft.Ref[ft.Dropdown]()

    def load_custom_fonts():
        page.fonts = {
            "Kanit": "/fonts/Kanit.ttf",
            "Open Sans": "/fonts/OpenSans.ttf",
            "BradBunR": "/fonts/BradBunR.ttf",
            "Heathergreen": "/fonts/Heathergreen.otf",
            "Ashemark": "/fonts/Ashemark regular.otf",
            "EmOne-SemiBold": "/fonts/EmOne-SemiBold.otf",
            "Gadner": "/fonts/Gadner.ttf",
        }
        page.update()

    load_custom_fonts()

    # Verificar e aplica o tema salvo no client_storage ao carregar a página
    dark_theme_value = page.client_storage.get("dark_theme")
    if dark_theme_value is None:
        dark_theme_value = False
    else:
        page.theme_mode = ft.ThemeMode.DARK if dark_theme_value else ft.ThemeMode.LIGHT
        page.update()

    theme_switch = ft.Switch(
        label="Tema Escuro",
        ref=theme_switch_ref,
        value=dark_theme_value,
        on_change=lambda e: toggle_theme(e.control.value),
    )

    def toggle_theme(is_dark):
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.client_storage.set(
            "dark_theme", is_dark
        )
        page.update()

    def update_font_family(font_family):
        page.client_storage.set(
            "font_family", font_family
        ) 
        if font_family == "Padrão":
            page.theme = ft.Theme() 
        else:
            page.theme = ft.Theme(
                font_family=font_family
            ) 
        page.update()

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

    # Obter o valor da fonte da aplicação e definir o valor padrão se necessário
    font_family_value = page.client_storage.get("font_family")
    if font_family_value is None:
        font_family_value = "Padrão"
    else:
        update_font_family(font_family_value)

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

def load_custom_fonts(font_family):
    """Carrega as fontes personalizadas com base na escolha do usuário."""
    if font_family == "Kanit":
        return {
            "Kanit": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf",
        }
    elif font_family == "Open Sans":
        return {
            "Open Sans": "fonts/OpenSans-Regular.ttf",
        }
    else:
        return {}

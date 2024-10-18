import flet as ft


def GeneralSettings(page: ft.Page):

    language_dropdown_ref = ft.Ref[ft.Dropdown]()

    locales_supported = [
        ft.Locale(language_code="pt", country_code="BR"),
        ft.Locale(language_code="en", country_code="US"),
    ]

    # Atualizar o idioma do app e salvar no client_storage
    def update_language(language_code):
        if language_code == "pt":
            page.current_locale = ft.Locale(language_code="pt", country_code="BR")
        elif language_code == "en":
            page.current_locale = ft.Locale(language_code="en", country_code="US")

        page.supported_locales = locales_supported
        page.client_storage.set("language", language_code)
        page.update()

    language_value = page.client_storage.get("language")
    if language_value is None:
        language_value = "pt"

    language_dropdown = ft.Dropdown(
        ref=language_dropdown_ref,
        label="Idioma",
        options=[
            ft.dropdown.Option("pt", "Português"),
            ft.dropdown.Option("en", "Inglês"),
        ],
        value=language_value,
        on_change=lambda e: update_language(e.control.value),
    )

    feedback_text = ft.Text(
        value="Ei, você! 🙋‍♂️ Que tal nos ajudar a melhorar ainda mais este app? Enviar um feedback é rápido, indolor e pode tornar sua experiência (e de outros usuários) ainda melhor! Queremos saber de tudo: elogios, críticas, ideias malucas... Só clicar no botão e mandar ver!",
        size=16,
        color=ft.colors.ON_SURFACE,
        max_lines=3,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    feedback_button = ft.ElevatedButton(
        text="Enviar Feedback 👍",
        icon=ft.icons.FEEDBACK,
        on_click=lambda e: page.go(
            "/feedback"
        ),
        style=ft.ButtonStyle(
            bgcolor=ft.colors.SECONDARY,
            color=ft.colors.ON_SECONDARY,
            elevation=4,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    return ft.Column(
        [
            ft.Container(
                content=language_dropdown,
                col={"sm": 12, "md": 6},
            ),
            ft.Divider(),
            ft.Text("Feedback", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column(
                    [
                        feedback_text,
                        feedback_button,
                    ],
                    spacing=10,
                ),
                col={"sm": 12, "md": 12},
                padding=ft.padding.all(10),
            ),
            ft.Divider(),
        ],
        run_spacing=10,
    )

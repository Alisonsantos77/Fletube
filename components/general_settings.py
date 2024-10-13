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

    # Obter o valor do idioma e definir o valor padrão se necessário
    language_value = page.client_storage.get("language")
    if language_value is None:
        language_value = "pt"

    # Dropdown para selecionar idioma
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

    # Função para enviar feedback e exibir um SnackBar de confirmação
    def send_feedback(feedback_text):
        if feedback_text.strip():
            # Lógica de envio do feedback (a ser implementada)
            feedback_textfield.value = ""
            feedback_textfield.update()
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Obrigado pelo seu feedback!"),
                bgcolor=ft.colors.GREEN,
            )
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Por favor, insira seu feedback antes de enviar."),
                bgcolor=ft.colors.RED,
            )
            page.snack_bar.open = True
        page.update()

    # Campo de texto para feedback
    feedback_textfield = ft.TextField(
        label="Envie seu Feedback",
        multiline=True,
        min_lines=3,
        max_lines=5,
        width=500,
    )

    # Botão para enviar feedback
    send_feedback_button = ft.ElevatedButton(
        text="Enviar Feedback",
        icon=ft.icons.SEND,
        on_click=lambda e: send_feedback(feedback_textfield.value),
    )

    # Layout da seção de configurações gerais
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
                        feedback_textfield,
                        send_feedback_button,
                    ],
                    spacing=10,
                ),
                col={"sm": 12, "md": 12},
            ),
        ],
        run_spacing=10,
    )

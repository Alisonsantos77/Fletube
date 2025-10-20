import os

import flet as ft
from loguru import logger

from services.send_feedback import send_feedback_email
from utils.validations import EmailValidator

FEEDBACK_RECIPIENT_EMAIL = os.getenv("FEEDBACK_RECIPIENT_EMAIL")


def FeedbackPage(page: ft.Page):
    email_in_app = page.client_storage.get("email")
    current_step = [0]
    user_data = {}

    def next_step(e):
        if validate_current_step():
            current_step[0] += 1
            update_view()

    def previous_step(e):
        if current_step[0] > 0:
            current_step[0] -= 1
            update_view()

    def update_view():
        for index, view in enumerate(steps_views):
            view.visible = index == current_step[0]

        progress_indicator.value = (current_step[0] + 1) / 5
        progress_text.value = f"Etapa {current_step[0] + 1} de 5"

        if current_step[0] == 4:
            update_review()

        page.update()

    def validate_current_step():
        if current_step[0] == 0:
            email = email_input.value.strip()
            result = EmailValidator.validate(email)
            if not result:
                email_input.error_text = str(result)
                email_input.update()
                return False
            else:
                email_input.error_text = None
                user_data["email"] = email
                return True

        elif current_step[0] == 1:
            if selected_rating[0] == 0:
                rating_error.value = "Por favor, selecione uma avaliação."
                rating_error.update()
                return False
            else:
                rating_error.value = ""
                user_data["rating"] = selected_rating[0]
                return True

        elif current_step[0] == 2:
            user_data["category"] = category_radio_group.value
            user_data["subcategory"] = subcategory_radio_group.value
            return True

        elif current_step[0] == 3:
            user_data["feedback_text"] = feedback_input.value.strip()
            return True

        return True

    def submit_feedback(e):
        submit_button.disabled = True
        submit_button.text = "Enviando..."
        submit_button.update()

        success = send_feedback_email(
            user_email=user_data["email"], user_message=user_data, page=page
        )

        if success:
            from utils.ui_helpers import show_success_snackbar

            show_success_snackbar(page, "Feedback enviado com sucesso!")
            current_step[0] = 0
            reset_feedback()
            update_view()
            page.go("/downloads")
        else:
            from utils.ui_helpers import show_error_snackbar

            show_error_snackbar(page, "Erro ao enviar o feedback. Tente novamente.")
            submit_button.disabled = False
            submit_button.text = "Enviar Feedback"
            submit_button.update()

    def update_review():
        email = user_data.get("email", "")
        rating = user_data.get("rating", 0)
        category = user_data.get("category", "")
        subcategory = user_data.get("subcategory", "")
        feedback_text_value = user_data.get("feedback_text", "")

        review_items = [
            {"label": "Email", "value": email, "icon": ft.Icons.EMAIL},
            {
                "label": "Avaliação",
                "value": f"{'⭐' * rating} ({rating} estrelas)",
                "icon": ft.Icons.STAR,
            },
            {"label": "Categoria", "value": category, "icon": ft.Icons.CATEGORY},
            {"label": "Subcategoria", "value": subcategory, "icon": ft.Icons.LABEL},
        ]

        review_column.controls.clear()

        for item in review_items:
            review_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(item["icon"], size=20),
                            ft.Column(
                                [
                                    ft.Text(
                                        item["label"],
                                        size=12,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(item["value"], size=14),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=12,
                    ),
                    padding=12,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                )
            )

        if feedback_text_value:
            review_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.MESSAGE, size=20),
                                    ft.Text(
                                        "Feedback adicional",
                                        size=12,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                spacing=12,
                            ),
                            ft.Text(feedback_text_value, size=14),
                        ],
                        spacing=8,
                    ),
                    padding=12,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                )
            )

        review_column.update()

    def reset_feedback():
        email_input.value = ""
        update_stars(-1)
        category_radio_group.value = "Sugestão"
        subcategory_radio_group.value = "Funcional"
        feedback_input.value = ""
        rating_error.value = ""
        email_input.error_text = None
        submit_button.disabled = False
        submit_button.text = "Enviar Feedback"
        page.update()

    progress_indicator = ft.ProgressBar(
        value=0.2,
        width=500,
        height=6,
        bar_height=6,
    )

    progress_text = ft.Text(
        "Etapa 1 de 5",
        size=13,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

    email_input = ft.TextField(
        label="Seu E-mail",
        hint_text="exemplo@dominio.com",
        width=400,
        keyboard_type=ft.KeyboardType.EMAIL,
        value=email_in_app if email_in_app else "",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_radius=8,
        text_size=15,
    )

    step1_left = ft.Column(
        [
            ft.Text(
                "Informe seu e-mail",
                size=32,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Container(height=16),
            ft.Text(
                "Usaremos seu e-mail para responder caso necessário",
                size=16,
            ),
        ],
    )

    step1_right = ft.Column(
        [
            ft.Container(
                content=ft.Image(
                    src="images/feedback/email_icon.png",
                    width=140,
                    height=140,
                    fit=ft.ImageFit.CONTAIN,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(height=20),
            email_input,
            ft.Container(height=24),
            ft.ElevatedButton(
                "Próximo",
                icon=ft.Icons.ARROW_FORWARD,
                on_click=next_step,
                width=200,
                height=48,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    step1 = ft.Row(
        [
            ft.Container(content=step1_left, expand=1),
            ft.Container(content=step1_right, expand=1),
        ],
        spacing=60,
        visible=True,
    )

    selected_rating = [0]
    stars_ref = []
    rating_error = ft.Text("", size=14)

    def update_stars(selected_index):
        selected_rating[0] = selected_index + 1
        for i, star in enumerate(stars_ref):
            if i <= selected_index:
                star.icon = ft.Icons.STAR
            else:
                star.icon = ft.Icons.STAR_BORDER
            star.update()
        rating_error.value = ""
        rating_error.update()

    def on_star_click(e):
        selected_index = int(e.control.data)
        update_stars(selected_index)

    for i in range(5):
        star = ft.IconButton(
            icon=ft.Icons.STAR_BORDER,
            icon_size=44,
            data=i,
            on_click=on_star_click,
            tooltip=f"{i + 1} estrela{'s' if i > 0 else ''}",
        )
        stars_ref.append(star)

    rating_descriptions = [
        {"stars": 1, "text": "Muito insatisfeito", "icon": "😞"},
        {"stars": 2, "text": "Insatisfeito", "icon": "😕"},
        {"stars": 3, "text": "Neutro", "icon": "😐"},
        {"stars": 4, "text": "Satisfeito", "icon": "😊"},
        {"stars": 5, "text": "Muito satisfeito", "icon": "🤩"},
    ]

    step2_left = ft.Column(
        [
            ft.Text(
                "Como foi sua experiência?",
                size=32,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Container(height=16),
            ft.Text(
                "Sua avaliação nos ajuda a melhorar continuamente",
                size=16,
            ),
            ft.Container(height=32),
            ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(item["icon"], size=24),
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"{item['stars']} estrela{'s' if item['stars'] > 1 else ''}",
                                            size=14,
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        ft.Text(item["text"], size=13),
                                    ],
                                    spacing=2,
                                ),
                            ],
                            spacing=12,
                        ),
                        padding=12,
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=8,
                    )
                    for item in rating_descriptions
                ],
                spacing=8,
            ),
        ],
    )

    step2_right = ft.Column(
        [
            ft.Container(
                content=ft.Image(
                    src="images/feedback/rating_icon.png",
                    width=140,
                    height=140,
                    fit=ft.ImageFit.CONTAIN,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(height=20),
            ft.Row(
                stars_ref,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            rating_error,
            ft.Container(height=32),
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Voltar",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=previous_step,
                        width=150,
                        height=48,
                    ),
                    ft.ElevatedButton(
                        "Próximo",
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=next_step,
                        width=150,
                        height=48,
                    ),
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    step2 = ft.Row(
        [
            ft.Container(content=step2_left, expand=1),
            ft.Container(content=step2_right, expand=1),
        ],
        spacing=60,
        visible=False,
    )

    category_radio_group = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(
                    value="Sugestão",
                    label="Sugestão - Tenho ideias para melhorar",
                    label_style=ft.TextStyle(size=15),
                ),
                ft.Radio(
                    value="Problema",
                    label="Problema - Encontrei um erro",
                    label_style=ft.TextStyle(size=15),
                ),
                ft.Radio(
                    value="Elogio",
                    label="Elogio - Gostei muito!",
                    label_style=ft.TextStyle(size=15),
                ),
            ],
            spacing=14,
        ),
        value="Sugestão",
    )

    subcategory_radio_group = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(
                    value="Funcional",
                    label="Funcional - Sobre funcionalidades",
                    label_style=ft.TextStyle(size=15),
                ),
                ft.Radio(
                    value="Estético",
                    label="Estético - Sobre design e aparência",
                    label_style=ft.TextStyle(size=15),
                ),
                ft.Radio(
                    value="Usabilidade",
                    label="Usabilidade - Sobre facilidade de uso",
                    label_style=ft.TextStyle(size=15),
                ),
            ],
            spacing=14,
        ),
        value="Funcional",
    )

    category_tips = [
        {
            "title": "Sugestão",
            "description": "Compartilhe ideias de novos recursos ou melhorias",
        },
        {
            "title": "Problema",
            "description": "Relate bugs, erros ou comportamentos inesperados",
        },
        {
            "title": "Elogio",
            "description": "Conte o que você mais gostou no aplicativo",
        },
    ]

    step3_left = ft.Column(
        [
            ft.Text(
                "Sobre o que você quer falar?",
                size=32,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Container(height=16),
            ft.Text(
                "Escolha a categoria e subcategoria que melhor descrevem seu feedback",
                size=16,
            ),
            ft.Container(height=32),
            ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    tip["title"],
                                    size=15,
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Text(
                                    tip["description"],
                                    size=13,
                                ),
                            ],
                            spacing=4,
                        ),
                        padding=12,
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=8,
                    )
                    for tip in category_tips
                ],
                spacing=8,
            ),
        ],
    )

    step3_right = ft.Column(
        [
            ft.Container(
                content=ft.Image(
                    src="images/feedback/category1_icon.png",
                    width=140,
                    height=140,
                    fit=ft.ImageFit.CONTAIN,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(height=20),
            ft.Row(
                controls=[
                    ft.Text(
                        "Selecione uma categoria:", size=14, weight=ft.FontWeight.W_600
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=8),
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                "Categoria Principal:",
                                size=13,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Container(height=4),
                            category_radio_group,
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "Subcategoria:", size=13, weight=ft.FontWeight.W_500
                            ),
                            ft.Container(height=4),
                            subcategory_radio_group,
                        ],
                        spacing=4,
                        expand=True,
                    ),
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=32),
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Voltar",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=previous_step,
                        width=150,
                        height=48,
                    ),
                    ft.ElevatedButton(
                        "Próximo",
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=next_step,
                        width=150,
                        height=48,
                    ),
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    step3 = ft.Row(
        [
            ft.Container(content=step3_left, expand=1),
            ft.Container(content=step3_right, expand=1),
        ],
        spacing=60,
        visible=False,
    )

    feedback_input = ft.TextField(
        label="Seu feedback (opcional)",
        hint_text="Compartilhe mais detalhes sobre sua experiência...",
        multiline=True,
        min_lines=8,
        max_lines=12,
        width=450,
        border_radius=8,
    )

    feedback_tips = [
        {
            "icon": ft.Icons.LIGHTBULB_OUTLINE,
            "text": "Seja específico sobre o que você gostou ou não gostou",
        },
        {
            "icon": ft.Icons.DESCRIPTION_OUTLINED,
            "text": "Descreva situações ou exemplos concretos",
        },
        {
            "icon": ft.Icons.EMOJI_EMOTIONS_OUTLINED,
            "text": "Não se preocupe com formatação, queremos ouvir você!",
        },
    ]

    step4_left = ft.Column(
        [
            ft.Text(
                "Conte-nos mais",
                size=32,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Container(height=16),
            ft.Text(
                "Detalhe sua experiência. Este campo é opcional, mas quanto mais informações, melhor!",
                size=16,
            ),
            ft.Container(height=32),
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(tip["icon"], size=20),
                            ft.Text(tip["text"], size=14, expand=True),
                        ],
                        spacing=12,
                    )
                    for tip in feedback_tips
                ],
                spacing=16,
            ),
        ],
    )

    step4_right = ft.Column(
        [
            ft.Container(
                content=ft.Image(
                    src="images/feedback/feedback_icon.png",
                    width=120,
                    height=120,
                    fit=ft.ImageFit.CONTAIN,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(height=20),
            feedback_input,
            ft.Container(height=24),
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Voltar",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=previous_step,
                        width=150,
                        height=48,
                    ),
                    ft.ElevatedButton(
                        "Próximo",
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=next_step,
                        width=150,
                        height=48,
                    ),
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    step4 = ft.Row(
        [
            ft.Container(content=step4_left, expand=1),
            ft.Container(content=step4_right, expand=1),
        ],
        spacing=60,
        visible=False,
    )

    submit_button = ft.ElevatedButton(
        "Enviar Feedback",
        icon=ft.Icons.SEND,
        on_click=submit_feedback,
        width=200,
        height=48,
    )

    review_column = ft.Column([], spacing=12)

    step5_left = ft.Column(
        [
            ft.Text(
                "Quase lá!",
                size=32,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Container(height=16),
            ft.Text(
                "Revise suas informações antes de enviar. Obrigado por contribuir para melhorar o Fletube!",
                size=16,
            ),
        ],
    )

    step5_right = ft.Column(
        [
            ft.Container(
                content=ft.Image(
                    src="images/feedback/review_icon.png",
                    width=100,
                    height=100,
                    fit=ft.ImageFit.CONTAIN,
                ),
                alignment=ft.alignment.center,
            ),
            ft.Container(height=20),
            ft.Container(
                content=ft.ListView(
                    controls=[review_column],
                    auto_scroll=False,
                    expand=True,
                    spacing=12,
                ),
                width=450,
                height=300,
                border_radius=8,
                padding=ft.Padding(12, 8, 12, 8),
            ),
            ft.Container(height=24),
            ft.Row(
                [
                    ft.OutlinedButton(
                        "Voltar",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=previous_step,
                        width=150,
                        height=48,
                    ),
                    submit_button,
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )


    step5 = ft.Row(
        [
            ft.Container(content=step5_left, expand=1),
            ft.Container(content=step5_right, expand=1),
        ],
        spacing=60,
        visible=False,
    )

    steps_views = [step1, step2, step3, step4, step5]

    header = ft.Row(
        [
            ft.Icon(ft.Icons.FEEDBACK_OUTLINED, size=32),
            ft.Text(
                "Envie seu Feedback",
                size=32,
                weight=ft.FontWeight.BOLD,
            ),
        ],
        spacing=12,
    )

    progress_footer = ft.Container(
        content=ft.Column(
            [
                progress_text,
                progress_indicator,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.alignment.bottom_center,
    )

    main_content = ft.Column(
        [
            header,
            ft.Container(height=40),
            ft.Container(
                content=ft.Column(steps_views, spacing=0),
                expand=True,
            ),
        ],
        expand=True,
    )

    layout = ft.Stack(
        [
            ft.Container(
                content=main_content,
                padding=ft.padding.symmetric(horizontal=80, vertical=40),
                expand=True,
            ),
            ft.Container(
                content=progress_footer,
                bottom=40,
                left=0,
                right=0,
            ),
        ],
        expand=True,
    )

    update_view()

    return layout

# feedback_page.py

import flet as ft
import logging
import os
import re
import requests
from utils.validations import validar_email

from services.send_feedback import send_feedback_email

# Configuração de logging
logging.basicConfig(
    filename="logs/app.log",
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("flet_core").setLevel(logging.INFO)  # Log para flet_core

logger = logging.getLogger(__name__)

# Variáveis de ambiente
FEEDBACK_RECIPIENT_EMAIL = os.getenv("FEEDBACK_RECIPIENT_EMAIL")


def FeedbackPage(page: ft.Page):
    email_in_app = page.client_storage.get("email")
    """
    Página de feedback com sistema de avaliação em etapas.
    """

    # Variável mutável para rastrear a etapa atual
    current_step = [0]
    user_data = {}

    def next_step(e):
        logger.info(
            f"Tentando avançar para a próxima etapa a partir da etapa {current_step[0]}"
        )
        if validate_current_step():
            current_step[0] += 1
            update_view()
            logger.info(f"Avançou para a etapa {current_step[0]}")
        else:
            logger.warning("Validação falhou na etapa atual.")

    def previous_step(e):
        logger.info(f"Tentando voltar da etapa {current_step[0]}")
        if current_step[0] > 0:
            current_step[0] -= 1
            update_view()
            logger.info(f"Retrocedeu para a etapa {current_step[0]}")
        else:
            logger.info("Já está na primeira etapa; não é possível voltar.")

    def update_view():
        for index, view in enumerate(steps_views):
            view.visible = index == current_step[0]
        if current_step[0] == 4:
            update_review()
        page.update()
        logger.info(f"View atualizada para a etapa {current_step[0]}")

    def validate_current_step():
        if current_step[0] == 0:
            email = email_input.value.strip()
            if not validar_email(email):
                email_input.error_text = "Por favor, insira um e-mail válido."
                email_input.update()
                logger.warning("E-mail inválido.")
                return False
            else:
                email_input.error_text = None
                user_data["email"] = email
                logger.info(f"E-mail coletado: {email}")
                return True
        elif current_step[0] == 1:
            if selected_rating[0] == 0:
                rating_error.value = "Por favor, selecione uma avaliação."
                rating_error.update()
                logger.warning("Nenhuma avaliação selecionada.")
                return False
            else:
                rating_error.value = ""
                user_data["rating"] = selected_rating[0]
                logger.info(f"Avaliação selecionada: {selected_rating[0]}")
                return True
        elif current_step[0] == 2:
            user_data["category"] = category_radio_group.value
            user_data["subcategory"] = subcategory_radio_group.value
            logger.info(f"Categoria selecionada: {user_data['category']}")
            logger.info(
                f"Subcategoria selecionada: {user_data['subcategory']}")
            return True
        elif current_step[0] == 3:
            user_data["feedback_text"] = feedback_input.value.strip()
            logger.info("Texto de feedback coletado.")
            return True
        return True

    def submit_feedback(e):
        logger.info("Enviando feedback...")
        success = send_feedback_email(
            user_email=user_data["email"], user_message=user_data, page=page
        )
        if success:
            snack_bar = ft.SnackBar(content=ft.Text(
                "Feedback enviado com sucesso!"))
            page.overlay.append(snack_bar)
            snack_bar.open = True
            logger.info("Feedback enviado com sucesso.")
            current_step[0] = 0
            reset_feedback()
            update_view()
            page.go("/downloads")
        else:
            snack_bar = ft.SnackBar(
                content=ft.Text("Erro ao enviar o feedback. Tente novamente.")
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            logger.error("Falha ao enviar o feedback.")
        page.update()

    def update_review():
        email = user_data.get("email", "")
        rating = user_data.get("rating", 0)
        category = user_data.get("category", "")
        subcategory = user_data.get("subcategory", "")
        feedback_text_value = user_data.get("feedback_text", "")
        review_content = f"""
        **Por favor, revise suas informações:**  
        **Email:** {email}  
        **Avaliação:** {rating} estrelas  
        **Categoria:** {category}  
        **Subcategoria:** {subcategory}  
        **Feedback:**  
        {feedback_text_value}
        """
        review_text.value = review_content
        review_text.update()
        logger.info("Conteúdo de revisão atualizado.")

    def reset_feedback():
        email_input.value = ""
        update_stars(-1)
        category_radio_group.value = "Sugestão"
        subcategory_radio_group.value = "Funcional"
        feedback_input.value = ""
        rating_error.value = ""
        email_input.error_text = None
        page.update()
        logger.info("Formulário de feedback reiniciado.")

    # -------- Passo 1: E-mail --------
    email_input = ft.TextField(
        label="Seu E-mail",
        hint_text="exemplo@dominio.com",
        width=300,
        keyboard_type=ft.KeyboardType.EMAIL,
        value=email_in_app if email_in_app else "",
    )

    step1 = ft.Column(
        [
            ft.Text(
                "Etapa 1 de 5: Insira seu e-mail", size=20, weight=ft.FontWeight.BOLD
            ),
            email_input,
            ft.Row(
                [ft.ElevatedButton("Próximo", on_click=next_step)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=True,
    )

    # -------- Passo 2: Avaliação por Estrelas --------
    selected_rating = [0]
    stars_ref = []

    rating_error = ft.Text("", color=ft.Colors.RED)

    def update_stars(selected_index):
        selected_rating[0] = selected_index + 1
        for i, star in enumerate(stars_ref):
            if i <= selected_index:
                star.icon = ft.Icons.STAR
                star.icon_color = ft.Colors.YELLOW
            else:
                star.icon = ft.Icons.STAR_OUTLINE
                star.icon_color = ft.Colors.GREY
            star.update()
        logger.info(
            f"Estrelas atualizadas: {selected_rating[0]} selecionadas.")

    def on_star_click(e):
        selected_index = int(e.control.data)
        update_stars(selected_index)
        logger.info(f"Estrela clicada: {selected_index + 1}")

    for i in range(5):
        star = ft.IconButton(
            icon=ft.Icons.STAR_OUTLINE,
            icon_color=ft.Colors.GREY,
            data=i,
            on_click=on_star_click,
        )
        stars_ref.append(star)

    step2 = ft.Column(
        [
            ft.Text(
                "Etapa 2 de 5: Avalie sua experiência",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Row(stars_ref, alignment=ft.MainAxisAlignment.CENTER),
            rating_error,
            ft.Row(
                [
                    ft.ElevatedButton("Voltar", on_click=previous_step),
                    ft.ElevatedButton("Próximo", on_click=next_step),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False,
    )

    # -------- Passo 3: Categoria e Subcategoria --------
    category_radio_group = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="Sugestão", label="Sugestão"),
                ft.Radio(value="Problema", label="Problema"),
                ft.Radio(value="Elogio", label="Elogio"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        value="Sugestão",
    )

    subcategory_radio_group = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="Funcional", label="Funcional"),
                ft.Radio(value="Estético", label="Estético"),
                ft.Radio(value="Usabilidade", label="Usabilidade"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        value="Funcional",
    )

    step3 = ft.Column(
        [
            ft.Text(
                "Etapa 3 de 5: Escolha a categoria", size=20, weight=ft.FontWeight.BOLD
            ),
            ft.Text("Categoria do Feedback:"),
            category_radio_group,
            ft.Text("Subcategoria do Feedback:"),
            subcategory_radio_group,
            ft.Row(
                [
                    ft.ElevatedButton("Voltar", on_click=previous_step),
                    ft.ElevatedButton("Próximo", on_click=next_step),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False,
    )

    # -------- Passo 4: Feedback Adicional --------
    feedback_input = ft.TextField(
        label="Feedback (opcional)",
        hint_text="Digite seu feedback aqui",
        multiline=True,
        min_lines=3,
        max_lines=5,
        width=400,
    )

    step4 = ft.Column(
        [
            ft.Text(
                "Etapa 4 de 5: Feedback adicional", size=20, weight=ft.FontWeight.BOLD
            ),
            feedback_input,
            ft.Row(
                [
                    ft.ElevatedButton("Voltar", on_click=previous_step),
                    ft.ElevatedButton("Próximo", on_click=next_step),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False,
    )

    # -------- Passo 5: Revisão e Envio --------
    review_text = ft.Markdown("")

    submit_button = ft.ElevatedButton(
        "Enviar Feedback", on_click=submit_feedback)

    step5 = ft.Column(
        [
            ft.Text("Etapa 5 de 5: Revisão", size=20,
                    weight=ft.FontWeight.BOLD),
            review_text,
            ft.Row(
                [
                    ft.ElevatedButton("Voltar", on_click=previous_step),
                    submit_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False,
    )

    # Listagem das etapas
    steps_views = [step1, step2, step3, step4, step5]

    # Container com animação para transições
    container_steps = ft.Container(
        content=ft.Column(
            steps_views,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
    )

    return container_steps
    update_view()  # Inicializa a primeira view

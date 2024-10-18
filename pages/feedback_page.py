import flet as ft
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def FeedbackPage(page: ft.Page):
    """
    Página de feedback com um sistema de avaliação por estrelas e opções de categorias de feedback.
    """

    # Referências para os campos e botões
    feedback_input_ref = ft.Ref[ft.TextField]()
    selected_rating_ref = 0

    # Lista para armazenar as referências das estrelas
    stars_ref = []

    # Função para atualizar as estrelas com base na seleção
    def update_stars(selected_index):
        """
        Atualiza as cores das estrelas com base no índice selecionado.
        """
        for i, star in enumerate(stars_ref):
            if i <= selected_index:
                star.icon_color = (
                    ft.colors.AMBER
                ) 
            else:
                star.icon_color = ft.colors.GREY  
            star.update()

    def on_star_click(e):
        nonlocal selected_rating_ref
        selected_index = int(e.control.data)
        selected_rating_ref = selected_index + 1
        update_stars(selected_index)
        logger.info(f"Avaliação selecionada: {selected_rating_ref} estrelas")

    for i in range(5):
        star = ft.IconButton(
            icon=ft.icons.STAR,
            icon_color=ft.colors.GREY,  
            data=i,  
            on_click=on_star_click,
        )
        stars_ref.append(star)

    category_segmented_button = ft.SegmentedButton(
        selected={"Sugestão"},  # Um valor padrão selecionado para evitar o erro
        allow_multiple_selection=False,
        allow_empty_selection=False,
        segments=[
            ft.Segment(value="Sugestão", label=ft.Text("Sugestão")),
            ft.Segment(value="Problema", label=ft.Text("Problema")),
            ft.Segment(value="Elogio", label=ft.Text("Elogio")),
        ],
    )

    subcategory_segmented_button = ft.SegmentedButton(
        selected={"Funcional"},
        allow_multiple_selection=False,
        allow_empty_selection=False,
        segments=[
            ft.Segment(value="Funcional", label=ft.Text("Funcional")),
            ft.Segment(value="Estético", label=ft.Text("Estético")),
            ft.Segment(value="Usabilidade", label=ft.Text("Usabilidade")),
        ],
    )

    feedback_input = ft.TextField(
        label="Feedback (opcional) ",
        ref=feedback_input_ref,
        hint_text="Digite seu feedback aqui",
        multiline=True,
        min_lines=3,
        max_lines=5,
        col=10,
    )



    def submit_feedback(e):
        feedback_text = feedback_input_ref.current.value
        selected_category = category_segmented_button.selected
        selected_subcategory = subcategory_segmented_button.selected

        logger.info(f"Feedback: {feedback_text}")
        logger.info(f"Avaliação: {selected_rating_ref} estrelas")
        logger.info(f"Categoria: {selected_category}")
        logger.info(f"Subcategoria: {selected_subcategory}")

        # Enviar feedback via e-mail
        try:
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = os.getenv("SMTP_PORT")
            smtp_username = os.getenv("EMAIL_USER")
            smtp_password = os.getenv("EMAIL_PASSWORD")

            # Verificar se todas as variáveis de ambiente estão definidas
            if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
                logger.error(
                    "Uma ou mais variáveis de ambiente não estão definidas corretamente."
                )
                return

            smtp_port = int(smtp_port)

            msg = MIMEMultipart()
            msg["From"] = smtp_username
            msg["To"] = "Alisondev77@hotmail.com"
            msg["Subject"] = f"Feedback - MultiTools ({selected_category})"

            # Conteúdo do e-mail
            email_body = f"""
            Avaliação: {selected_rating_ref} estrelas
            Categoria: {selected_category}
            Subcategoria: {selected_subcategory}
            Feedback: {feedback_text}
            """
            msg.attach(MIMEText(email_body, "plain"))

            # Usar gerenciador de contexto para a conexão SMTP
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()  # Identificar a conexão com o servidor SMTP
                server.starttls()  # Inicializar a conexão segura
                server.ehlo()  # Identificar a conexão segura após o starttls
                server.login(smtp_username, smtp_password)  # Login no servidor
                server.sendmail(
                    smtp_username, msg["To"], msg.as_string()
                )

            logger.info("E-mail de feedback enviado com sucesso.")

        except Exception as e:
            logger.error(f"Erro ao enviar o e-mail de feedback: {e}")

    submit_button = ft.ElevatedButton(
        text="Enviar Feedback", icon=ft.icons.SEND, on_click=submit_feedback, col=5
    )

    return ft.Container(
        padding=ft.padding.all(20),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    value="Avalie a experiência",
                    size=28,
                    color=ft.colors.PRIMARY,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Image(
                    src="/images/logo.png",
                    fit=ft.ImageFit.CONTAIN,
                    height=300,
                    width=300,
                ),
                ft.Text(
                    value="Avaliação por estrelas",
                    weight=ft.FontWeight.BOLD,
                    size=24,
                    color=ft.colors.PRIMARY,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER, controls=stars_ref
                ),
                ft.Text(
                    value="Categoria de feedback",
                    weight=ft.FontWeight.BOLD,
                    size=24,
                    color=ft.colors.PRIMARY,
                ),
                category_segmented_button,
                ft.Text(
                    value="Subcategoria de feedback",
                    weight=ft.FontWeight.BOLD,
                    size=24,
                    color=ft.colors.PRIMARY,
                ),
                subcategory_segmented_button,
                ft.ResponsiveRow(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[feedback_input, submit_button],
                ),
            ],
            spacing=20,
        ),
    )

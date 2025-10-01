# components/general_settings.py

import flet as ft
import logging


def sync_local_feedback(page: ft.Page):
    from services.send_feedback import sync_local_feedback

    sync_local_feedback(page)


def GeneralSettings(page: ft.Page):
    reset_button = ft.ElevatedButton(
        text="Resetar Configurações 🛠️",
        icon=ft.Icons.RESTART_ALT,
        on_click=lambda e: reset_app_settings(page),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.ERROR,
            color=ft.Colors.ON_ERROR,
            elevation=4,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    def reset_app_settings(page: ft.Page):
        page.client_storage.clear()  # Limpa todos os dados de configurações
        # Salva um valor indicando que as configurações foram resetadas
        page.client_storage.set("config_reset", True)

        snack_bar = ft.SnackBar(
            content=ft.Text("Configurações resetadas! 🚀 Reiniciando o app..."),
            bgcolor=ft.Colors.PRIMARY,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        logging.info("Configurações resetadas pelo usuário.")

        # Reiniciar ou redirecionar para a home
        page.go("/")

    feedback_text = ft.Text(
        value="Ei, você! 🙋‍♂️ Que tal nos ajudar a melhorar ainda mais este app? Enviar um feedback é rápido, indolor e pode tornar sua experiência (e de outros usuários) ainda melhor! Queremos saber de tudo: elogios, críticas, ideias malucas... Só clicar no botão e mandar ver!",
        size=16,
        color=ft.Colors.ON_SURFACE,
        max_lines=3,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    feedback_button = ft.ElevatedButton(
        text="Enviar Feedback 👍",
        icon=ft.Icons.FEEDBACK,
        on_click=lambda e: page.go("/feedback"),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.SECONDARY,
            color=ft.Colors.ON_SECONDARY,
            elevation=4,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    return ft.Column(
        [
            ft.Container(
                content=reset_button,
                col={"sm": 12, "md": 6},
                padding=ft.padding.all(10),
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

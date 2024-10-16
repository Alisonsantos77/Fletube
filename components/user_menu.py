import flet as ft


def logout_user(page: ft.Page):
    # Remove as informações do usuário do client storage
    page.client_storage.remove("user_avatar_url")
    page.client_storage.remove("user_initials")
    page.client_storage.remove("user_name")

    # Remove as chaves de autenticação do GitHub e Google
    page.client_storage.remove("github_token")
    page.client_storage.remove("google_token")

    page.go("/")


def handle_user_action(action, page):
    if action == "Logout":
        return logout_user(page)
    elif action == "Configurações":
        page.go("/configuracoes")
    elif action == "Perfil":
        pass


def create_user_menu(page: ft.Page):
    avatar_url = page.client_storage.get("user_avatar_url")
    user_initials = page.client_storage.get("user_initials") or "U"
    user_name = page.client_storage.get("user_name") or "Usuário"

    return ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Stack(
                [
                    ft.CircleAvatar(
                        foreground_image_src=avatar_url
                        or "https://robohash.org/userdefault",
                        content=ft.Text(user_initials),
                    ),
                    ft.Container(
                        content=ft.CircleAvatar(bgcolor=ft.colors.GREEN, radius=5),
                        alignment=ft.alignment.bottom_left,
                    ),
                ],
                width=40,
                height=40,
            ),
            tooltip=f"Logado como {user_name}",
        ),
        items=[
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.PERSON_OUTLINE,
                            size=20,
                            color=ft.colors.BLUE_GREY_500,
                        ),
                        ft.Text(
                            value="Perfil",
                            size=14,
                        ),
                    ]
                ),
                on_click=lambda e: handle_user_action("Perfil", page),
            ),
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.SETTINGS,
                            size=20,
                            color=ft.colors.BLUE_GREY_500,
                        ),
                        ft.Text(
                            value="Configurações",
                            size=14,
                        ),
                    ]
                ),
                on_click=lambda e: handle_user_action("Configurações", page),
            ),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=ft.icons.LOGOUT,
                            size=20,
                            color=ft.colors.RED,
                        ),
                        ft.Text(
                            value="Sair",
                            size=14,
                            color=ft.colors.RED,
                        ),
                    ]
                ),
                on_click=lambda e: handle_user_action("Logout", page),
            ),
        ],
    )

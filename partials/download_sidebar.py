import flet as ft


# Sidebar simplificada que será usada para listar itens
def sidebar_list():
    # Criar uma lista de controle vazia
    items = []

    # Preencher a lista com 10 itens usando um loop for
    for i in range(1, 11):
        items.append(
            ft.ListTile(
                leading=ft.Icon(ft.icons.MUSIC_NOTE),
                title=ft.Text(f"Música {i}"),
                subtitle=ft.Text(f"Artista {i}"),
                bgcolor=ft.colors.ON_BACKGROUND,
            )
        )

    # Retornar o container da sidebar com a lista preenchida
    return ft.Container(
        expand=True,
        content=ft.Column(
            controls=items,  # Lista de controles gerados pelo loop
            scroll=ft.ScrollMode.AUTO,  # Permitir rolagem caso a lista cresça
        ),
    )

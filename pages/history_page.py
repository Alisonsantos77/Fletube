import flet as ft



def HistoryPage(page: ft.Page):
    download_history = [
        {
            "title": "Python Tutorial for Beginners",
            "thumbnail": "https://img.youtube.com/vi/kqtD5dpn9C8/hqdefault.jpg",
            "date": "2024-10-10",
            "status": "Concluído",
            "format": "MP4",
        },
        {
            "title": "Lo-fi Hip Hop Mix",
            "thumbnail": "https://img.youtube.com/vi/lTRiuFIWV54/hqdefault.jpg",
            "date": "2024-10-09",
            "status": "Concluído",
            "format": "MP3",
        },
        {
            "title": "JavaScript Crash Course",
            "thumbnail": "https://img.youtube.com/vi/hdI2bqOjy3c/hqdefault.jpg",
            "date": "2024-10-08",
            "status": "Falhou",
            "format": "MKV",
        },
    ]

    def render_download_item(item):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Image(
                        src=item["thumbnail"],
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(item["title"], size=18, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Data: {item['date']}"),
                            ft.Text(f"Formato: {item['format']}"),
                            ft.Text(
                                f"Status: {item['status']}",
                                color=(
                                    ft.colors.GREEN
                                    if item["status"] == "Concluído"
                                    else ft.colors.RED
                                ),
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE_OUTLINE,
                        on_click=lambda e: delete_item(item),
                        tooltip="Excluir do histórico",
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(8),
            bgcolor=ft.colors.SURFACE_VARIANT,
            margin=ft.margin.symmetric(vertical=5),
        )

    def delete_item(item):
        print(f"Item '{item['title']}' excluído do histórico.")

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Histórico de Downloads", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color=ft.colors.OUTLINE),
                ft.Column(
                    controls=[render_download_item(item) for item in download_history],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.all(20),
    )

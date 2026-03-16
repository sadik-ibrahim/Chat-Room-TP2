import flet as ft


def main(page: ft.Page):
    page.title = "Flet Chat"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    # Lista onde as mensagens vão aparecer
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # Campo para escrever a mensagem
    new_message = ft.TextField(
        hint_text="Escreve uma mensagem...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
    )

    page.add(
        ft.Container(
            content=chat,
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            controls=[
                new_message,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED,
                    tooltip="Enviar mensagem",
                ),
            ]
        ),
    )


ft.run(main)

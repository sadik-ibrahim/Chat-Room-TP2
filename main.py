from dataclasses import dataclass
import flet as ft

# Shared across all sessions in the same process
rooms: list[str] = ["general", "random"]


@dataclass
class Message:
    user_name: str
    text: str
    message_type: str  # "chat_message" | "login_message" | "room_created"
    room: str = "general"


@ft.control
class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self._initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self._avatar_color(message.user_name),
            ),
            ft.Column(
                tight=True,
                spacing=5,
                controls=[
                    ft.Text(message.user_name, weight=ft.FontWeight.BOLD),
                    ft.Text(message.text, selectable=True),
                ],
            ),
        ]

    def _initials(self, name: str) -> str:
        return name[:1].capitalize() if name else "?"

    def _avatar_color(self, name: str) -> str:
        colors = [
            ft.Colors.AMBER, ft.Colors.BLUE, ft.Colors.BROWN, ft.Colors.CYAN,
            ft.Colors.GREEN, ft.Colors.INDIGO, ft.Colors.LIME, ft.Colors.ORANGE,
            ft.Colors.PINK, ft.Colors.PURPLE, ft.Colors.RED, ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors[hash(name) % len(colors)]


def main(page: ft.Page):
    page.title = "Flet Chat"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    def on_message(topic: str, message: Message):
        if message.message_type == "chat_message":
            chat.controls.append(ChatMessage(message))
        elif message.message_type == "login_message":
            chat.controls.append(
                ft.Text(message.text, italic=True, color=ft.Colors.BLACK_45, size=12)
            )
        page.update()

    def on_system_event(message: Message):
        # Handles broadcast events not tied to a specific room (e.g. room_created)
        if message.message_type == "room_created":
            page.update()  # will refresh room list in a later step

    page.pubsub.subscribe(on_system_event)

    async def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all_on_topic(
                "general",  # hardcoded for now; will use current_room in next step
                Message(
                    user_name=page.session.store.get("user_name"),
                    text=new_message.value,
                    message_type="chat_message",
                    room="general",
                ),
            )
            new_message.value = ""
            await new_message.focus()

    # Welcome dialog: asks the user for a name before joining
    def join_chat(_):
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
            return
        name = join_user_name.value.strip()
        page.session.store.set("user_name", name)
        new_message.prefix = ft.Text(f"{name}: ")
        page.pubsub.subscribe_topic("general", on_message)
        page.pubsub.send_all_on_topic(
            "general",
            Message(
                user_name=name,
                text=f"{name} has joined the chat.",
                message_type="login_message",
                room="general",
            ),
        )
        page.pop_dialog()
        page.update()

    join_user_name = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        on_submit=join_chat,
    )
    welcome_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Welcome to Flet Chat!"),
        content=ft.Column([join_user_name], width=300, height=70, tight=True),
        actions=[ft.Button("Join chat", on_click=join_chat)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(welcome_dlg)

    # Chat message list
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # Input field for new messages
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
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
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )


ft.run(main)

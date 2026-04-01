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

    current_room = "general"
    room_history: dict[str, list[Message]] = {r: [] for r in rooms}

    def on_message(topic: str, message: Message):
        room_history[current_room].append(message)
        if message.message_type == "chat_message":
            chat.controls.append(ChatMessage(message))
        elif message.message_type == "login_message":
            chat.controls.append(
                ft.Text(message.text, italic=True, color=ft.Colors.BLACK_45, size=12)
            )
        page.update()

    def on_system_event(message: Message):
        if message.message_type == "room_created":
            room_history[message.room] = []
            rooms_list.controls.append(room_button(message.room))
            rooms_list.update()

    page.pubsub.subscribe(on_system_event)

    def switch_room(new_room: str):
        nonlocal current_room
        page.pubsub.unsubscribe_topic(current_room)
        current_room = new_room
        chat.controls.clear()
        for msg in room_history[new_room]:
            if msg.message_type == "chat_message":
                chat.controls.append(ChatMessage(msg))
            elif msg.message_type == "login_message":
                chat.controls.append(
                    ft.Text(msg.text, italic=True, color=ft.Colors.BLACK_45, size=12)
                )
        page.pubsub.subscribe_topic(new_room, on_message)
        page.update()

    async def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all_on_topic(
                current_room,
                Message(
                    user_name=page.session.store.get("user_name"),
                    text=new_message.value,
                    message_type="chat_message",
                    room=current_room,
                ),
            )
            new_message.value = ""
            await new_message.focus()

    def create_room_click(_):
        name = new_room_name.value.strip()
        if not name:
            new_room_name.error_text = "Room name cannot be blank!"
            new_room_name.update()
            return
        if name in rooms:
            new_room_name.error_text = "Room already exists!"
            new_room_name.update()
            return
        rooms.append(name)
        room_history[name] = []  # ready before switch_room runs
        page.pubsub.send_all(
            Message(user_name=page.session.store.get("user_name"), text="", message_type="room_created", room=name)
        )
        page.pop_dialog()
        switch_room(name)

    new_room_name = ft.TextField(label="Room name", autofocus=True, on_submit=create_room_click)
    create_room_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Create a new room"),
        content=ft.Column([new_room_name], width=300, height=70, tight=True),
        actions=[ft.Button("Create", on_click=create_room_click)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Welcome dialog: asks the user for a name before joining
    def join_chat(_):
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
            return
        name = join_user_name.value.strip()
        page.session.store.set("user_name", name)
        page.pop_dialog()
        new_message.prefix = ft.Text(f"{name}: ")
        new_message.update()
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

    def room_button(name: str) -> ft.TextButton:
        return ft.TextButton(
            content=ft.Text(f"# {name}", text_align=ft.TextAlign.LEFT),
            on_click=lambda e, r=name: switch_room(r),
        )

    rooms_list = ft.Column(
        controls=[room_button(r) for r in rooms],
        spacing=0,
        tight=True,
    )

    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Rooms", weight=ft.FontWeight.BOLD, size=14),
                rooms_list,
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    tooltip="New room",
                    on_click=lambda _: page.show_dialog(create_room_dlg),
                ),
            ],
        ),
        width=180,
        padding=10,
    )

    page.add(
        ft.Row(
            expand=True,
            controls=[
                sidebar,
                ft.VerticalDivider(width=1),
                ft.Column(
                    expand=True,
                    controls=[
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
                    ],
                ),
            ],
        )
    )


ft.run(main)

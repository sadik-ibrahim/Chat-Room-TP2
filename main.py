import os
import uuid
from dataclasses import dataclass, field
import flet as ft

os.environ.setdefault("FLET_SECRET_KEY", "chatroom-dev-key")
import flet_video as ftv


EMOJI_OPTIONS = ["👍", "❤️", "😂", "😮", "😢", "🎉"]


def avatar_color(name: str) -> str:
    colors = [
        ft.Colors.AMBER, ft.Colors.BLUE, ft.Colors.BROWN, ft.Colors.CYAN,
        ft.Colors.GREEN, ft.Colors.INDIGO, ft.Colors.LIME, ft.Colors.ORANGE,
        ft.Colors.PINK, ft.Colors.PURPLE, ft.Colors.RED, ft.Colors.TEAL,
        ft.Colors.YELLOW,
    ]
    return colors[hash(name) % len(colors)]

# Shared across all sessions in the same process
rooms: list[str] = ["general", "random"]
dm_history: dict[str, list] = {}  # dm_topic → list[Message], global so late subscribers see past msgs
reactions: dict[str, dict[str, set]] = {}  # message_id → {emoji: set of usernames}


def dm_topic(a: str, b: str) -> str:
    """Deterministic DM topic name regardless of who initiates."""
    return "dm_" + "_".join(sorted([a, b]))


@dataclass
class Message:
    user_name: str
    text: str
    message_type: str  # "chat_message"|"login_message"|"room_created"|"dm_invite"|"file_message"|"edit_message"|"delete_message"|"react_message"
    room: str = "general"
    recipient: str = ""  # used for dm_invite: the target username
    file_url: str = ""   # used for file_message: server path to the file
    file_name: str = ""  # used for file_message: original filename
    target_id: str = ""  # used for react_message: id of the message being reacted to
    emoji: str = ""      # used for react_message: the emoji character
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@ft.control
class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self._initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=avatar_color(message.user_name),
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


def main(page: ft.Page):
    page.title = "Flet Chat"
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    current_room = "general"
    room_history: dict[str, list[Message]] = {r: [] for r in rooms}
    dm_peers: dict[str, str] = {}  # DM topic → peer username (per session)
    dm_opened: set[str] = set()  # DM topics already shown in this session's sidebar
    msg_widgets: dict = {}  # message id → (outer_widget, text_ctrl or None)

    def on_message(topic: str, message: Message):
        if message.message_type == "edit_message":
            if message.id in msg_widgets:
                _, text_ctrl, _ = msg_widgets[message.id]
                if text_ctrl:
                    text_ctrl.value = message.text
                    text_ctrl.update()
            return
        if message.message_type == "delete_message":
            if message.id in msg_widgets:
                widget, _, _ = msg_widgets.pop(message.id)
                if widget in chat.controls:
                    chat.controls.remove(widget)
            page.update()
            return
        if message.message_type == "react_message":
            msg_reactions = reactions.setdefault(message.target_id, {})
            users = msg_reactions.setdefault(message.emoji, set())
            if message.text == "remove":
                users.discard(message.user_name)
            else:
                users.add(message.user_name)
            if message.target_id in msg_widgets:
                _, _, r_row = msg_widgets[message.target_id]
                r_row.controls = build_reaction_buttons(message.target_id)
                r_row.update()
            return
        if topic.startswith("dm_"):
            dm_history.setdefault(topic, []).append(message)
        else:
            room_history[current_room].append(message)
        if message.message_type == "chat_message":
            chat.controls.append(make_message_widget(message))
        elif message.message_type == "login_message":
            chat.controls.append(
                ft.Text(message.text, italic=True, color=ft.Colors.BLACK_45, size=12)
            )
        elif message.message_type == "file_message":
            chat.controls.append(make_file_widget(message))
        page.update()

    def on_system_event(message: Message):
        if message.message_type == "room_created":
            room_history[message.room] = []
            rooms_list.controls.append(room_button(message.room))
            rooms_list.update()
        elif message.message_type == "dm_invite":
            my_name = page.session.store.get("user_name")
            if message.recipient == my_name:
                topic = dm_topic(my_name, message.user_name)
                if current_room != topic:  # don't re-open if already in this DM
                    open_dm(message.user_name)

    page.pubsub.subscribe(on_system_event)

    def switch_room(new_room: str):
        nonlocal current_room
        page.pubsub.unsubscribe_topic(current_room)
        current_room = new_room
        chat.controls.clear()
        msg_widgets.clear()
        history = dm_history.get(new_room, []) if new_room.startswith("dm_") else room_history.get(new_room, [])
        for msg in history:
            if msg.message_type == "chat_message":
                chat.controls.append(make_message_widget(msg))
            elif msg.message_type == "login_message":
                chat.controls.append(
                    ft.Text(msg.text, italic=True, color=ft.Colors.BLACK_45, size=12)
                )
            elif msg.message_type == "file_message":
                chat.controls.append(make_file_widget(msg))
        page.pubsub.subscribe_topic(new_room, on_message)
        page.update()

    def open_dm(other_user: str):
        """Open (or switch to) a DM conversation with other_user."""
        topic = dm_topic(page.session.store.get("user_name"), other_user)
        dm_peers[topic] = other_user
        if topic not in dm_history:
            dm_history[topic] = []
        if topic not in dm_opened:
            dm_opened.add(topic)
            dm_list.controls.append(
                ft.TextButton(
                    content=ft.Text(f"@ {other_user}", text_align=ft.TextAlign.LEFT),
                    on_click=lambda _, t=topic: switch_room(t),
                )
            )
            dm_list.update()
        switch_room(topic)  # switch_room already calls subscribe_topic

    def build_reaction_buttons(msg_id: str) -> list:
        my_name = page.session.store.get("user_name")
        return [
            ft.OutlinedButton(
                content=ft.Text(f"{e} {len(users)}"),
                on_click=lambda _, em=e, mid=msg_id: page.pubsub.send_all_on_topic(
                    current_room,
                    Message(user_name=my_name,
                            text="remove" if my_name in reactions.get(mid, {}).get(em, set()) else "",
                            message_type="react_message",
                            room=current_room, target_id=mid, emoji=em),
                ),
            )
            for e, users in reactions.get(msg_id, {}).items() if users
        ]

    def make_message_widget(msg: Message):
        my_name = page.session.store.get("user_name")
        is_mine = msg.user_name == my_name

        reactions_row = ft.Row(spacing=4, wrap=True, controls=build_reaction_buttons(msg.id))

        def react_click(_):
            def on_emoji_click(_, em=None):
                already_reacted = my_name in reactions.get(msg.id, {}).get(em, set())
                page.pubsub.send_all_on_topic(
                    current_room,
                    Message(user_name=my_name,
                            text="remove" if already_reacted else "",
                            message_type="react_message",
                            room=current_room, target_id=msg.id, emoji=em),
                )
                page.pop_dialog()
            page.show_dialog(ft.AlertDialog(
                title=ft.Text("Reagir"),
                content=ft.Row(
                    controls=[
                        ft.TextButton(e, on_click=lambda _, em=e: on_emoji_click(_, em))
                        for e in EMOJI_OPTIONS
                    ],
                    wrap=True,
                ),
                actions_alignment=ft.MainAxisAlignment.END,
            ))

        if is_mine:
            text_ctrl = ft.Text(msg.text, selectable=True)

            def edit_click(_):
                edit_field = ft.TextField(value=text_ctrl.value, autofocus=True)
                def confirm_edit(_):
                    page.pubsub.send_all_on_topic(
                        current_room,
                        Message(user_name=my_name, text=edit_field.value,
                                message_type="edit_message", room=current_room, id=msg.id),
                    )
                    page.pop_dialog()
                page.show_dialog(ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Editar mensagem"),
                    content=ft.Column([edit_field], width=300, height=70, tight=True),
                    actions=[ft.Button("Guardar", on_click=confirm_edit)],
                    actions_alignment=ft.MainAxisAlignment.END,
                ))

            def delete_click(_):
                page.pubsub.send_all_on_topic(
                    current_room,
                    Message(user_name=my_name, text="",
                            message_type="delete_message", room=current_room, id=msg.id),
                )

            popup = ft.PopupMenuButton(
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(my_name[:1].capitalize()),
                            color=ft.Colors.WHITE,
                            bgcolor=avatar_color(my_name),
                        ),
                        ft.Column(tight=True, spacing=5, controls=[
                            ft.Text(my_name, weight=ft.FontWeight.BOLD),
                            text_ctrl,
                        ]),
                    ],
                ),
                items=[
                    ft.PopupMenuItem(content=ft.Text("Editar"), on_click=edit_click),
                    ft.PopupMenuItem(content=ft.Text("Eliminar"), on_click=delete_click),
                    ft.PopupMenuItem(content=ft.Text("Reagir"), on_click=react_click),
                ],
            )
            outer = ft.Column(tight=True, spacing=2, controls=[popup, reactions_row])
            msg_widgets[msg.id] = (outer, text_ctrl, reactions_row)
            return outer

        # Other user's message
        def dm_click(_):
            open_dm(msg.user_name)

        popup = ft.PopupMenuButton(
            content=ChatMessage(msg),
            items=[
                ft.PopupMenuItem(content=ft.Text("Reagir"), on_click=react_click),
                ft.PopupMenuItem(content=ft.Text("Mensagem privada"), on_click=dm_click),
            ],
        )
        outer = ft.Column(tight=True, spacing=2, controls=[popup, reactions_row])
        msg_widgets[msg.id] = (outer, None, reactions_row)
        return outer

    def make_file_widget(msg: Message) -> ft.Row:
        ext = msg.file_name.rsplit(".", 1)[-1].lower() if "." in msg.file_name else ""
        if ext in {"jpg", "jpeg", "png", "gif", "webp"}:
            media = ft.Image(src=msg.file_url, width=200, fit="contain")
        elif ext in {"mp4", "mov", "avi", "webm", "mkv"}:
            media = ftv.Video(
                playlist=[ftv.VideoMedia(msg.file_url)],
                width=300, height=180,
                show_controls=True,
                autoplay=False,
            )
        else:
            async def open_url(_, u=msg.file_url):
                await ft.UrlLauncher().launch_url(u)
            media = ft.TextButton(
                content=ft.Text(f"[file] {msg.file_name}"),
                on_click=open_url,
            )
        return ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.CircleAvatar(
                    content=ft.Text(msg.user_name[:1].capitalize()),
                    color=ft.Colors.WHITE,
                    bgcolor=avatar_color(msg.user_name),
                ),
                ft.Column(tight=True, spacing=5, controls=[
                    ft.Text(msg.user_name, weight=ft.FontWeight.BOLD),
                    media,
                ]),
            ],
        )

    def on_upload_progress(e: ft.FilePickerUploadEvent):
        if e.progress == 1.0:
            page.pubsub.send_all_on_topic(
                current_room,
                Message(
                    user_name=page.session.store.get("user_name"),
                    text="",
                    message_type="file_message",
                    room=current_room,
                    file_url=f"/uploads/{e.file_name}",
                    file_name=e.file_name,
                ),
            )

    async def send_message_click(e):
        if new_message.value != "":
            my_name = page.session.store.get("user_name")
            page.pubsub.send_all_on_topic(
                current_room,
                Message(
                    user_name=my_name,
                    text=new_message.value,
                    message_type="chat_message",
                    room=current_room,
                ),
            )
            if current_room.startswith("dm_"):
                peer = dm_peers.get(current_room)
                if peer:
                    page.pubsub.send_all(
                        Message(user_name=my_name, text="", message_type="dm_invite", recipient=peer)
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

    file_picker = ft.FilePicker()
    file_picker.on_upload = on_upload_progress

    async def open_file_picker(_):
        files = await file_picker.pick_files(allow_multiple=False)
        if not files:
            return
        for f in files:
            upload_url = page.get_upload_url(f.name, 60)
            await file_picker.upload([ft.FilePickerUploadFile(name=f.name, upload_url=upload_url)])

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

    dm_list = ft.Column(spacing=0, tight=True)

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
                ft.Divider(height=1),
                ft.Text("Direct Messages", weight=ft.FontWeight.BOLD, size=14),
                dm_list,
            ],
            scroll=ft.ScrollMode.AUTO,
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
                                ft.IconButton(
                                    icon=ft.Icons.ATTACH_FILE,
                                    tooltip="Attach file",
                                    on_click=open_file_picker,
                                ),
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


ft.run(main, assets_dir="assets", upload_dir="assets/uploads")

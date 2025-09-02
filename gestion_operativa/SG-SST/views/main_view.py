import flet as ft
import asyncio
from .incident_view import IncidentView
from .risk_view import RiskView
from ..agents.corps.general_sgsst import GeneralSGSST

# --- Clases de Chat (sin cambios) ---
class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__(vertical_alignment=ft.CrossAxisAlignment.START)
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(message.user_name[:1].capitalize()),
                color=ft.colors.WHITE,
                bgcolor=ft.colors.BLUE_GREY_600 if message.message_type == "bot_message" else ft.colors.RED_600
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight=ft.FontWeight.BOLD),
                    ft.Text(message.text, selectable=True, width=700),
                ],
                tight=True,
                spacing=5,
            ),
        ]

# --- Vista del Agente de IA (hereda de ft.Column) ---
class AgentChatView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.general_sgsst = GeneralSGSST(page=self.page)
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.new_message = ft.TextField(
            hint_text="Escribe tu orden de SG-SST aquí...",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=self.send_message_click,
        )
        self.progress_ring = ft.ProgressRing(visible=False)
        # Add controls in __init__ for Column
        self.controls = [
            self.chat_list,
            ft.Row([self.progress_ring], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(
                [
                    self.new_message,
                    ft.IconButton(
                        icon=ft.icons.SEND_ROUNDED,
                        tooltip="Enviar Orden",
                        on_click=self.send_message_click,
                    ),
                ],
            ),
        ]

    def did_mount(self):
        self.add_message(Message("General SG-SST", "Hola, soy el General de SG-SST.", "bot_message"))

    def add_message(self, message: Message):
        self.chat_list.controls.append(ChatMessage(message))
        if self.page: self.page.update()

    async def send_message_click(self, e):
        user_message_text = self.new_message.value
        if not user_message_text: return

        # Add user message and clear input
        self.add_message(Message("Tú", user_message_text, "user_message"))
        self.new_message.value = ""

        # Show progress and disable input
        self.progress_ring.visible = True
        self.new_message.disabled = True
        if self.page: self.page.update()

        try:
            bot_response_text = await asyncio.to_thread(
                self.general_sgsst.process_command, user_message_text
            )
            self.add_message(Message("General SG-SST", bot_response_text, "bot_message"))
        except Exception as ex:
            self.add_message(Message("Error", f"Ocurrió un error: {ex}", "bot_message"))
        finally:
            # Hide progress and re-enable input
            self.progress_ring.visible = False
            self.new_message.disabled = False
            if self.page: self.page.update()

# --- Vista Principal (hereda de ft.Row) ---
class MainView(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.incident_view = IncidentView()
        self.risk_view = RiskView()
        self.agent_view = AgentChatView(page=self.page)

        self.navigation_rail = ft.NavigationRail(
            selected_index=2, # Start on Agent view
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.WARNING_AMBER, label="Incidentes"),
                ft.NavigationRailDestination(icon=ft.icons.SHIELD_OUTLINED, label="Riesgos"),
                ft.NavigationRailDestination(icon=ft.icons.INTELLIGENT_TOY, label="Asistente IA"),
            ],
            on_change=self.nav_change,
        )

        self.content_area = ft.Container(
            content=self.agent_view,
            expand=True,
            padding=ft.padding.all(20),
        )

        # Add controls in __init__ for Row
        self.controls = [
            self.navigation_rail,
            ft.VerticalDivider(width=1),
            self.content_area,
        ]

    def nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.content_area.content = self.incident_view
        elif index == 1:
            self.content_area.content = self.risk_view
        elif index == 2:
            self.content_area.content = self.agent_view
        if self.page: self.page.update()

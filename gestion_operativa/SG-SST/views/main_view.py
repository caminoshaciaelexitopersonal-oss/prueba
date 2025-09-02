# gestion_operativa/SG-SST/views/main_view.py
import flet as ft
import asyncio
import json
from .incident_view import IncidentView
from .risk_view import RiskView
from gestion_operativa.SG_SST.agents.corps.general_sgsst import GeneralSGSST

# --- Clases de Chat ---
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
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_GREY_600 if message.message_type == "bot_message" else ft.Colors.RED_600
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

# --- Vista del Agente de IA ---
class AgentChatView(ft.UserControl):
    def __init__(self):
        super().__init__(expand=True)
        self.general_sgsst = GeneralSGSST()
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

    def did_mount(self):
        self.add_message(Message("General SG-SST", "Hola, soy el General de SG-SST. Puedo ayudarte a reportar incidentes y gestionar riesgos.", "bot_message"))

    def build(self):
        return ft.Column(
            [
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
            ],
            expand=True
        )

    def add_message(self, message: Message):
        self.chat_list.controls.append(ChatMessage(message))
        self.update()

    async def send_message_click(self, e):
        user_message_text = self.new_message.value
        if not user_message_text: return
        self.new_message.value = ""
        self.add_message(Message("Tú", user_message_text, "user_message"))
        self.progress_ring.visible = True
        self.update()
        try:
            bot_response_text = await asyncio.to_thread(
                self.general_sgsst.process_command, user_message_text
            )
            self.add_message(Message("General SG-SST", bot_response_text, "bot_message"))
        except Exception as ex:
            self.add_message(Message("Error", f"Ocurrió un error: {ex}", "bot_message"))
        finally:
            self.progress_ring.visible = False
            self.update()

# --- Vista Principal ---
class MainView(ft.UserControl):
    def __init__(self):
        super().__init__(expand=True)
        self.incident_view = IncidentView()
        self.risk_view = RiskView()
        self.agent_view = AgentChatView()

        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.WARNING_AMBER,
                    selected_icon=ft.icons.WARNING,
                    label="Incidentes",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SHIELD_OUTLINED,
                    selected_icon=ft.icons.SHIELD,
                    label="Riesgos",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.INTELLIGENT_TOY,
                    selected_icon=ft.icons.INTELLIGENT_TOY_OUTLINED,
                    label="Asistente IA",
                ),
            ],
            on_change=self.nav_change,
        )

        self.content_area = ft.Container(
            content=self.incident_view,
            expand=True,
            padding=ft.padding.all(20),
        )

    def build(self):
        return ft.Row(
            controls=[
                self.navigation_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
        )

    def nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.content_area.content = self.incident_view
        elif index == 1:
            self.content_area.content = self.risk_view
        elif index == 2:
            self.content_area.content = self.agent_view
        self.update()

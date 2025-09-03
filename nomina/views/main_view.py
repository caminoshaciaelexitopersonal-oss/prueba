# gestion_operativa/Nomina/views/main_view.py
import flet as ft
import asyncio
import json
from .employee_view import EmployeeView
from .payroll_view import PayrollView
from gestion_operativa.Nomina.agents.corps.general_nomina import GeneralNomina

# --- Clases de Chat (reutilizadas de otros módulos) ---
class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__(vertical_alignment=ft.CrossAxisAlignment.START)
        try:
            parsed_json = json.loads(message.text)
            display_text = f"```json\n{json.dumps(parsed_json, indent=2, ensure_ascii=False)}\n```"
        except (json.JSONDecodeError, TypeError):
            display_text = message.text

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(message.user_name[:1].capitalize()),
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_GREY_600 if message.message_type == "bot_message" else ft.Colors.BROWN_400
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight=ft.FontWeight.BOLD),
                    ft.Markdown(display_text, selectable=True, extension_set="gitweblinks", code_theme="atom-one-dark"),
                ],
                tight=True,
                spacing=5,
            ),
        ]

# --- Vista del Agente de IA ---
class AgentChatView(ft.UserControl):
    def __init__(self):
        super().__init__(expand=True)
        self.general_nomina = GeneralNomina()
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.new_message = ft.TextField(
            hint_text="Escribe tu orden de nómina aquí...",
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
        self.add_message(Message("General Nómina", "Hola, soy el General de Nómina. Puedo ayudarte a añadir empleados y a realizar cálculos de nómina.", "bot_message"))

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
                self.general_nomina.process_command, user_message_text
            )
            self.add_message(Message("General Nómina", bot_response_text, "bot_message"))
        except Exception as ex:
            self.add_message(Message("Error", f"Ocurrió un error: {ex}", "bot_message"))
        finally:
            self.progress_ring.visible = False
            self.update()


# --- Vista Principal Modificada ---
class MainView(ft.UserControl):
    def __init__(self):
        super().__init__(expand=True)

        # Las vistas existentes
        self.employee_view = EmployeeView()
        self.payroll_view = PayrollView()
        # La nueva vista del agente
        self.agent_view = AgentChatView()

        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.PERSON_SEARCH,
                    selected_icon=ft.icons.PERSON_SEARCH_OUTLINED,
                    label="Empleados",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PAYMENT,
                    selected_icon=ft.icons.PAYMENT_OUTLINED,
                    label="Nómina",
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
            content=self.employee_view,
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
            self.content_area.content = self.employee_view
        elif index == 1:
            self.content_area.content = self.payroll_view
        elif index == 2:
            self.content_area.content = self.agent_view
        self.update()

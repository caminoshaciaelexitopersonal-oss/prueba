# views/agente_view.py
import flet as ft
import asyncio
from agent import agent_interface

class Message:
    """Clase de datos para un mensaje en el chat."""
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type # "user_message" o "bot_message"

class ChatMessage(ft.Row):
    """Control de Flet para mostrar un mensaje de chat."""
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight=ft.FontWeight.BOLD),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else ""

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER, ft.colors.BLUE, ft.colors.BROWN, ft.colors.CYAN,
            ft.colors.GREEN, ft.colors.INDIGO, ft.colors.LIME, ft.colors.ORANGE,
            ft.colors.PINK, ft.colors.PURPLE, ft.colors.RED, ft.colors.TEAL,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

class AgenteViewContent(ft.UserControl):
    """Contenido para la vista de chat con el agente de IA."""
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.chat_list = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )
        self.new_message = ft.TextField(
            hint_text="Escribe tu pregunta aquí...",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=self.send_message_click,
        )
        self.progress_ring = ft.ProgressRing(visible=False)

    def build(self):
        # Añadir un mensaje de bienvenida inicial del bot
        self.add_message(Message("SARITA", "Hola, soy tu asistente contable. ¿En qué puedo ayudarte hoy?", "bot_message"))

        return ft.Column(
            [
                self.chat_list,
                ft.Row(
                    [
                        self.new_message,
                        ft.IconButton(
                            icon=ft.icons.SEND_ROUNDED,
                            tooltip="Enviar mensaje",
                            on_click=self.send_message_click,
                        ),
                    ],
                ),
                ft.Row([self.progress_ring], alignment=ft.MainAxisAlignment.CENTER),
            ],
            expand=True,
        )

    def add_message(self, message: Message):
        self.chat_list.controls.append(ChatMessage(message))
        self.update()

    async def send_message_click(self, e):
        user_message_text = self.new_message.value
        if not user_message_text:
            return

        self.new_message.value = ""
        self.add_message(Message("Tú", user_message_text, "user_message"))
        self.progress_ring.visible = True
        self.update()

        try:
            # Aquí es donde llamamos al agente de IA
            # NOTA: En una app real, el tenant_id y la api_key vendrían de la sesión del usuario
            # o de un sistema de configuración seguro. Aquí los hardcodeamos por simplicidad.
            bot_response_text = await agent_interface.invoke_agent_for_area(
                page=self.page,
                area='Contabilidad',
                user_input=user_message_text,
                user_id=self.page.session.get("user_id"),
                tenant_id=1, # Hardcoded para demo
                tenant_api_key="inquilino_demo_key" # Hardcoded para demo
            )
            self.add_message(Message("SARITA", bot_response_text, "bot_message"))
        except Exception as ex:
            self.add_message(Message("Error", f"Ocurrió un error: {ex}", "bot_message"))
        finally:
            self.progress_ring.visible = False
            self.update()


def AgenteView(page: ft.Page):
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/agente")

    return ft.View(
        "/agente",
        appbar=ft.AppBar(
            title=ft.Text("Asistente de Contabilidad"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            AgenteViewContent(page)
        ],
        padding=15
    )

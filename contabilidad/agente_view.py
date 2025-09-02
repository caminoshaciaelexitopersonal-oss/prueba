# views/agente_view.py
import flet as ft
import asyncio
from contabilidad.agents.corps.general_contable import ContabilidadGeneral

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
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight=ft.FontWeight.BOLD),
                    ft.Text(message.text, selectable=True, width=700), # Ancho para evitar desbordamiento
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else ""

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER, ft.Colors.BLUE, ft.Colors.BROWN, ft.Colors.CYAN,
            ft.Colors.GREEN, ft.Colors.INDIGO, ft.Colors.LIME, ft.Colors.ORANGE,
            ft.Colors.PINK, ft.Colors.PURPLE, ft.Colors.RED, ft.Colors.TEAL,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

class AgenteViewContent(ft.UserControl):
    """Contenido para la vista de chat con el agente de IA."""
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        # Instanciar el nuevo General Contable
        try:
            self.general_contable = ContabilidadGeneral()
            self.agent_ready = True
        except ValueError as e:
            self.general_contable = None
            self.agent_ready = False
            self.initial_bot_message = f"Error de configuración: {e}"

        self.chat_list = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )
        self.new_message = ft.TextField(
            hint_text="Escribe tu orden aquí... (ej: registrar compra de papelería por 50.000 pagada con caja)",
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
        """Se llama cuando el control se añade a la página."""
        welcome_message = "Hola, soy el General Contable. ¿En qué puedo ayudarte hoy?"
        if not self.agent_ready:
            welcome_message = self.initial_bot_message

        self.add_message(Message("General Contable", welcome_message, "bot_message"))

    def build(self):
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
                            disabled=not self.agent_ready,
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
        if not user_message_text or not self.agent_ready:
            return

        self.new_message.value = ""
        self.add_message(Message("Tú", user_message_text, "user_message"))
        self.progress_ring.visible = True
        self.update()

        try:
            # Ejecutar el proceso síncrono del agente en un hilo separado
            # para no bloquear el bucle de eventos de la UI de Flet.
            bot_response_text = await asyncio.to_thread(
                self.general_contable.process_command,
                user_message_text
            )
            self.add_message(Message("General Contable", bot_response_text, "bot_message"))
        except Exception as ex:
            self.add_message(Message("Error", f"Ocurrió un error crítico durante la ejecución: {ex}", "bot_message"))
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
            title=ft.Text("Asistente de Contabilidad (Agente Jerárquico)"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            AgenteViewContent(page)
        ],
        padding=15
    )

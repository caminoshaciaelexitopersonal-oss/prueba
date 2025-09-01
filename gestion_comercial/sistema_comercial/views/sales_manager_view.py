# gestion_comercial/sistema_comercial/views/sales_manager_view.py
import flet as ft
import asyncio
from gestion_comercial.sistema_comercial.agents.corps.general_comercial import GeneralComercial

# --- Clases para la Interfaz de Chat ---
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
                bgcolor=ft.Colors.BLUE_GREY_600 if message.message_type == "bot_message" else ft.Colors.CYAN_800
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight=ft.FontWeight.BOLD),
                    ft.Text(message.text, selectable=True, width=500),
                ],
                tight=True,
                spacing=5,
            ),
        ]

class SalesManagerView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.visible = True
        self.general_comercial = GeneralComercial()

        # --- Controles de la UI ---
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.new_message = ft.TextField(
            hint_text="Escribe tu orden de ventas aquí...",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=self.send_message_click,
        )
        self.progress_ring = ft.ProgressRing(visible=False)

        # Placeholder for other sales-related controls
        self.other_controls = ft.Column(
            [
                ft.Text("Panel de Control de Ventas", size=16),
                ft.Text("Aquí irían otros gráficos y tablas de ventas."),
            ]
        )

    def did_mount(self):
        self.add_message(Message("General Comercial", "Hola, soy el General Comercial. Puedes darme órdenes para gestionar clientes y pedidos.", "bot_message"))

    def build(self):
        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Gestión de Ventas", size=18, weight=ft.FontWeight.BOLD),
                        self.other_controls,
                    ],
                    expand=1,
                ),
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        ft.Text("Asistente de IA de Ventas", size=18, weight=ft.FontWeight.BOLD),
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
                    expand=1,
                ),
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH
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
                self.general_comercial.process_command, user_message_text
            )
            self.add_message(Message("General Comercial", bot_response_text, "bot_message"))
        except Exception as ex:
            self.add_message(Message("Error", f"Ocurrió un error: {ex}", "bot_message"))
        finally:
            self.progress_ring.visible = False
            self.update()

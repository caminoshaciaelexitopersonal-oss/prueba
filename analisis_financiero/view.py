# analisis_financiero/view.py
import flet as ft
import asyncio
import json
from analisis_financiero.agents.corps.general_analisis import GeneralAnalisis

# --- Clases para la Interfaz de Chat ---
class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__(vertical_alignment=ft.CrossAxisAlignment.START)

        # Intentar formatear el texto si es un JSON
        try:
            parsed_json = json.loads(message.text)
            display_text = f"```json\n{json.dumps(parsed_json, indent=2, ensure_ascii=False)}\n```"
        except (json.JSONDecodeError, TypeError):
            display_text = message.text

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(message.user_name[:1].capitalize()),
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_GREY_600 if message.message_type == "bot_message" else ft.Colors.PURPLE_600
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

# --- Contenido Principal de la Vista ---
class AnalisisFinancieroViewContent(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.general_analisis = GeneralAnalisis()

        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.new_message = ft.TextField(
            hint_text="Pide un análisis financiero aquí...",
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
        self.add_message(Message("General Análisis", "Hola, soy el General de Análisis Financiero. Pídeme un reporte y lo generaré para ti.", "bot_message"))

    def build(self):
        return ft.Column(
            [
                ft.Text("Asistente de Análisis Financiero", size=20, weight=ft.FontWeight.BOLD),
                self.chat_list,
                ft.Row([self.progress_ring], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(
                    [
                        self.new_message,
                        ft.IconButton(
                            icon=ft.icons.SEND_ROUNDED,
                            tooltip="Enviar Petición",
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
                self.general_analisis.process_command, user_message_text
            )
            self.add_message(Message("General Análisis", bot_response_text, "bot_message"))
        except Exception as ex:
            self.add_message(Message("Error", f"Ocurrió un error: {ex}", "bot_message"))
        finally:
            self.progress_ring.visible = False
            self.update()

def AnalisisFinancieroView(page: ft.Page):
    return ft.View(
        "/analisis_financiero",
        appbar=ft.AppBar(
            title=ft.Text("Análisis Financiero"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            AnalisisFinancieroViewContent(page)
        ],
        padding=15
    )

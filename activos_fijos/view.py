# activos_fijos/view.py
import flet as ft
import asyncio
from activos_fijos.agents.corps.general_activos import GeneralActivos
from database import db_manager # Para cargar los activos en la tabla
from utils.helpers import format_currency

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
                bgcolor=ft.Colors.BLUE_GREY_600 if message.message_type == "bot_message" else ft.Colors.DEEP_ORANGE_600
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

# --- Contenido Principal de la Vista ---
class ActivosFijosViewContent(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.general_activos = GeneralActivos()

        # --- Controles de la UI ---
        self.chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.new_message = ft.TextField(
            hint_text="Escribe tu orden sobre activos fijos aquí...",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_submit=self.send_message_click,
        )
        self.progress_ring = ft.ProgressRing(visible=False)

        self.tabla_activos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Fecha Adq.")),
                ft.DataColumn(ft.Text("Costo"), numeric=True),
                ft.DataColumn(ft.Text("Vida Útil (M)")),
            ],
            rows=[],
            expand=True,
        )

    def did_mount(self):
        self.add_message(Message("General Activos", "Hola, soy el General de Activos Fijos. Puedes ordenarme registrar nuevos activos o ejecutar la depreciación mensual.", "bot_message"))
        self.cargar_activos()

    def build(self):
        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Activos Fijos Registrados", size=18, weight=ft.FontWeight.BOLD),
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=lambda e: self.cargar_activos(), tooltip="Recargar Tabla"),
                        ft.Container(content=self.tabla_activos, expand=True, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=5),
                    ],
                    expand=2,
                ),
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        ft.Text("Asistente de IA", size=18, weight=ft.FontWeight.BOLD),
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
                self.general_activos.process_command, user_message_text
            )
            self.add_message(Message("General Activos", bot_response_text, "bot_message"))
            self.cargar_activos()
        except Exception as ex:
            self.add_message(Message("Error", f"Ocurrió un error: {ex}", "bot_message"))
        finally:
            self.progress_ring.visible = False
            self.update()

    def cargar_activos(self):
        self.tabla_activos.rows.clear()
        activos = db_manager.obtener_activos_fijos_db()
        for a in activos:
            self.tabla_activos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(a.get('id', ''))),
                    ft.DataCell(ft.Text(a.get('nombre', ''))),
                    ft.DataCell(ft.Text(a.get('fecha_adquisicion', ''))),
                    ft.DataCell(ft.Text(format_currency(a.get('costo_adquisicion', 0)))),
                    ft.DataCell(ft.Text(str(a.get('vida_util_meses', 0)))),
                ])
            )
        self.update()

def ActivosFijosView(page: ft.Page):
    return ft.View(
        "/activos_fijos",
        appbar=ft.AppBar(
            title=ft.Text("Gestión de Activos Fijos"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            ActivosFijosViewContent(page)
        ],
        padding=15
    )

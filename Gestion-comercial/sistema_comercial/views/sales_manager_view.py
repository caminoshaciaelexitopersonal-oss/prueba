import flet as ft

class SalesManagerView(ft.UserControl):
    def build(self):
        # --- UI Controls for Chat ---
        self.page_title = ft.Text("Agente de Ventas IA", style=ft.TextThemeStyle.HEADLINE_MEDIUM)

        self.chat_history = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True,
        )

        self.user_input = ft.TextField(
            hint_text="Habla con el agente...",
            expand=True,
            border_radius=30,
            shift_enter=True,
            # on_submit will be handled by the controller
        )

        self.send_button = ft.IconButton(
            icon=ft.icons.SEND_ROUNDED,
            tooltip="Enviar Mensaje",
            # on_click will be handled by the controller
        )

        self.progress_ring = ft.ProgressRing(visible=False)

        # --- Main Layout ---
        return ft.Column(
            controls=[
                ft.Row([self.page_title, self.progress_ring], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                self.chat_history,
                ft.Row(
                    controls=[
                        self.user_input,
                        self.send_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            expand=True,
        )

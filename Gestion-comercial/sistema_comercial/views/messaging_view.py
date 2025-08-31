import flet as ft

class MessagingView(ft.UserControl):
    def build(self):
        # --- UI Controls ---
        self.page_title = ft.Text("Gestor de Envíos Masivos", style=ft.TextThemeStyle.HEADLINE_MEDIUM)

        # Recipient List
        self.select_all_checkbox = ft.Checkbox(label="Seleccionar Todos")
        self.recipients_list = ft.ListView(expand=True, spacing=5, padding=ft.padding.only(top=10))

        # Message Composition
        self.subject_field = ft.TextField(label="Asunto", border_radius=5)
        self.body_field = ft.TextField(
            label="Cuerpo del Mensaje",
            multiline=True,
            min_lines=8,
            max_lines=15,
            border_radius=5,
            expand=True
        )
        self.send_button = ft.ElevatedButton("Enviar Mensaje", icon=ft.icons.SEND)

        # Channel Tabs
        self.channel_tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Email", icon=ft.icons.EMAIL),
                ft.Tab(text="SMS", icon=ft.icons.SMS),
                ft.Tab(text="WhatsApp", icon=ft.icons.WHATSAPP),
            ],
        )

        # --- Layout ---
        main_composer_layout = ft.Column(
            [
                self.subject_field,
                self.body_field,
                ft.Row([self.send_button], alignment=ft.MainAxisAlignment.END)
            ],
            spacing=10,
            expand=True,
        )

        recipient_panel = ft.Column(
            [
                ft.Text("Seleccionar Destinatarios", style=ft.TextThemeStyle.TITLE_MEDIUM),
                self.select_all_checkbox,
                ft.Divider(),
                self.recipients_list
            ],
            expand=True
        )

        return ft.Column(
            [
                self.page_title,
                self.channel_tabs,
                ft.Row(
                    [
                        ft.Container(
                            content=recipient_panel,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=ft.border_radius.all(5),
                            padding=15,
                            expand=1,
                        ),
                        ft.Container(
                            content=main_composer_layout,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=ft.border_radius.all(5),
                            padding=15,
                            expand=2,
                        )
                    ],
                    spacing=20,
                    expand=True
                )
            ],
            expand=True,
            spacing=10
        )

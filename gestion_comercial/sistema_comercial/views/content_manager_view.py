import flet as ft

class ContentManagerView(ft.UserControl):
    def build(self):
        # --- Text Generation Tab Controls ---
        self.text_idea_input = ft.TextField(label="Idea para el post de texto", multiline=True, min_lines=5, max_lines=5, expand=True)
        self.generate_text_button = ft.ElevatedButton("Generar Texto", icon=ft.icons.AUTO_AWESOME)
        self.generated_text_area = ft.Markdown("Aquí aparecerá el texto generado...", selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, code_theme="atom-one-dark")

        # --- Video Generation Tab Controls ---
        self.video_idea_input = ft.TextField(label="Idea para el guion del video", multiline=True, min_lines=5, max_lines=5, expand=True)
        self.video_format_dropdown = ft.Dropdown(
            label="Formato del Video",
            options=[
                ft.dropdown.Option("16:9 (YouTube, X)"),
                ft.dropdown.Option("9:16 (Reels, TikTok, Shorts)"),
                ft.dropdown.Option("1:1 (Instagram, Facebook)"),
            ],
            border_radius=5,
        )
        self.video_duration_input = ft.TextField(label="Duración (segundos)", width=180, border_radius=5)
        self.generate_video_button = ft.ElevatedButton("Generar Guion de Video", icon=ft.icons.VIDEOCAM)
        self.generated_video_area = ft.Markdown("Aquí aparecerá el guion generado...", selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, code_theme="atom-one-dark")

        # --- Shared Controls ---
        self.schedule_button = ft.ElevatedButton("Programar en Calendario", icon=ft.icons.CALENDAR_MONTH, disabled=True)

        # --- Tab Layouts ---
        text_tab_content = ft.Column([
            self.text_idea_input,
            ft.Row([self.generate_text_button], alignment=ft.MainAxisAlignment.END),
            ft.Divider(),
            ft.Text("Contenido de Texto Generado:", style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Container(content=self.generated_text_area, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=5, padding=10, expand=True),
        ], spacing=10, expand=True)

        video_tab_content = ft.Column([
            self.video_idea_input,
            ft.Row([self.video_format_dropdown, self.video_duration_input], spacing=10),
            ft.Row([self.generate_video_button], alignment=ft.MainAxisAlignment.END),
            ft.Divider(),
            ft.Text("Guion de Video Generado:", style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Container(content=self.generated_video_area, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=5, padding=10, expand=True),
        ], spacing=10, expand=True)

        # --- Main View Layout ---
        return ft.Column(
            controls=[
                ft.Row(
                    [
                        ft.Text("Gestor de Contenido IA", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                        self.schedule_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(text="Generador de Texto", icon=ft.icons.TEXT_FIELDS, content=text_tab_content),
                        ft.Tab(text="Generador de Video", icon=ft.icons.MOVIE, content=video_tab_content),
                    ],
                    expand=True,
                ),
            ],
            expand=True
        )

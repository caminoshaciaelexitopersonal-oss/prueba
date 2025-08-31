import flet as ft
import datetime

class CalendarView(ft.UserControl):
    def build(self):
        # --- Header Controls ---
        self.month_year_label = ft.Text(style=ft.TextThemeStyle.HEADLINE_SMALL)
        self.prev_month_button = ft.IconButton(
            icon=ft.icons.CHEVRON_LEFT,
            tooltip="Mes Anterior"
        )
        self.next_month_button = ft.IconButton(
            icon=ft.icons.CHEVRON_RIGHT,
            tooltip="Mes Siguiente"
        )

        # --- Calendar Grid ---
        # The controller will populate this grid.
        self.calendar_grid = ft.GridView(
            expand=False, # We will control height
            runs_count=7, # 7 days a week
            max_extent=120,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
        )

        week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        days_header = ft.Row(
            controls=[
                ft.Text(day, text_align=ft.TextAlign.CENTER, expand=True, weight=ft.FontWeight.BOLD) for day in week_days
            ]
        )

        # --- Main Layout ---
        return ft.Column(
            controls=[
                ft.Text("Calendario de Contenidos", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Row(
                    [
                        self.prev_month_button,
                        self.month_year_label,
                        self.next_month_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                days_header,
                ft.Divider(),
                ft.Container(
                    content=self.calendar_grid,
                    expand=True,
                )
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

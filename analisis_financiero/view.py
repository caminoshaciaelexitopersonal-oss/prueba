# analisis_financiero/view.py
import flet as ft
from analisis_financiero import logic as analisis_logic
import datetime

import flet_charts
from flet_core import Theme

class AnalisisFinancieroView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/analisis_financiero")
        self.page = page
        self.page.theme = Theme(color_scheme_seed=ft.colors.INDIGO)
        self.appbar = ft.AppBar(
            title=ft.Text("Análisis Financiero con Gráficos"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
        )

        # --- Controles ---
        self.fecha_picker = ft.DatePicker(on_change=self._on_date_change)
        self.page.overlay.append(self.fecha_picker)

        self.fecha_display = ft.Text(datetime.date.today().isoformat(), weight=ft.FontWeight.BOLD)
        self.fecha_button = ft.ElevatedButton("Seleccionar Fecha", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.fecha_picker.pick_date())

        self.generar_button = ft.ElevatedButton("Generar Análisis Gráfico", icon=ft.icons.INSIGHTS, on_click=self.generar_analisis)
        self.results_container = ft.Row(wrap=True, scroll=ft.ScrollMode.ALWAYS, expand=True, alignment=ft.MainAxisAlignment.START)

        self.controls = [
            ft.Row([ft.Text("Análisis a fecha:"), self.fecha_display, self.fecha_button, self.generar_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            self.results_container
        ]

    def _on_date_change(self, e):
        if self.fecha_picker.value:
            self.fecha_display.value = self.fecha_picker.value.strftime('%Y-%m-%d')
            self.update()

    def generar_analisis(self, e):
        fecha_analisis = self.fecha_display.value
        self.results_container.controls.clear()
        self.results_container.controls.append(ft.ProgressRing())
        self.update()

        try:
            analisis = analisis_logic.generar_analisis_financiero_completo(fecha_analisis)

            self.results_container.controls.clear()

            for categoria, ratios in analisis.items():
                for nombre_ratio, valor in ratios.items():
                    # Para cada ratio, obtener su historial
                    historial = analisis_logic.generar_historial_de_ratio(nombre_ratio, categoria)

                    # Crear los puntos para el gráfico de líneas
                    line_data_points = [
                        flet_charts.LineChartDataPoint(x, y)
                        for x, y in enumerate(historial['values'])
                    ]

                    line_chart_data = flet_charts.LineChartData(
                        data_points=line_data_points,
                        stroke_width=2,
                        color=ft.colors.with_opacity(0.5, ft.colors.BLUE_GREY),
                        below_stroke_color=ft.colors.with_opacity(0.2, ft.colors.BLUE),
                        show_data_points=True,
                    )

                    chart = flet_charts.LineChart(
                        data_series=[line_chart_data],
                        chart_padding=10,
                        height=100,
                        expand=True,
                        # Configuración de ejes y etiquetas podría ir aquí
                    )

                    card = ft.Card(
                        elevation=2,
                        content=ft.Container(
                            padding=15,
                            width=350, # Ancho fijo para cada tarjeta
                            content=ft.Column([
                                ft.Text(nombre_ratio.replace("_", " ").title(), weight=ft.FontWeight.BOLD, size=14),
                                ft.Text(f"Valor Actual: {valor:.2f}", size=20, weight=ft.FontWeight.W_500),
                                ft.Text(f"Tendencia últimos {len(historial['labels'])} meses", size=10, color=ft.colors.GREY),
                                chart,
                            ])
                        )
                    )
                    self.results_container.controls.append(card)

        except Exception as ex:
            self.results_container.controls.clear()
            self.results_container.controls.append(ft.Text(f"Ocurrió un error al generar el análisis: {ex}", color=ft.colors.RED))

        self.update()

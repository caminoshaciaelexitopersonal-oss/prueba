# views/reportes_view.py
import flet as ft
import datetime
from contabilidad import reportes_logic
from utils.helpers import format_currency, mostrar_snackbar

class ReportesViewContent(ft.UserControl):
    """Contenido para la generación de informes y reportes."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page

        # Controles de Filtros
        self.fecha_inicio_picker = ft.DatePicker(on_change=self._on_date_change)
        self.fecha_fin_picker = ft.DatePicker(on_change=self._on_date_change)
        self.page.overlay.extend([self.fecha_inicio_picker, self.fecha_fin_picker])

        self.fecha_inicio_button = ft.ElevatedButton(
            "Fecha Inicio", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.fecha_inicio_picker.pick_date()
        )
        self.fecha_fin_button = ft.ElevatedButton(
            "Fecha Fin", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.fecha_fin_picker.pick_date()
        )
        self.fecha_inicio_display = ft.Text(value=(datetime.date.today().replace(day=1)).isoformat())
        self.fecha_fin_display = ft.Text(value=datetime.date.today().isoformat())

        self.tipo_reporte_selector = ft.Dropdown(
            label="Tipo de Reporte",
            width=300,
            options=[
                ft.dropdown.Option("Balance de Comprobación"),
                ft.dropdown.Option("Estado de Resultados"),
                ft.dropdown.Option("Balance General"),
            ],
            value="Balance de Comprobación",
            on_change=self.tipo_reporte_changed, # Para ajustar visibilidad de fechas
        )
        self.generar_button = ft.FilledButton("Generar Reporte", icon=ft.icons.PIE_CHART, on_click=self.generar_reporte)

        # Contenedor para mostrar el reporte
        self.tabla_reporte = ft.DataTable(
            columns=[], # Se definirán dinámicamente
            rows=[],
            column_spacing=20,
            expand=True,
        )
        self.reporte_container = ft.Container(
            content=self.tabla_reporte,
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=ft.border_radius.all(5)
        )
        self.progreso = ft.ProgressRing(visible=False)

    def _on_date_change(self, e):
        if e.control == self.fecha_inicio_picker and self.fecha_inicio_picker.value:
            self.fecha_inicio_display.value = self.fecha_inicio_picker.value.strftime('%Y-%m-%d')
        if e.control == self.fecha_fin_picker and self.fecha_fin_picker.value:
            self.fecha_fin_display.value = self.fecha_fin_picker.value.strftime('%Y-%m-%d')
        self.update()

    def build(self):
        return ft.Column(
            [
                ft.Text("Generación de Informes", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10),
                ft.Card(ft.Container(padding=15, content=ft.Row(
                    [
                        ft.Column([ft.Text("Desde:"), self.fecha_inicio_display, self.fecha_inicio_button]),
                        ft.Column([ft.Text("Hasta:"), self.fecha_fin_display, self.fecha_fin_button]),
                        self.tipo_reporte_selector,
                        self.generar_button,
                        self.progreso,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ))),
                ft.Divider(height=10),
                self.reporte_container,
            ],
            expand=True,
            spacing=10
        )

    def did_mount(self):
        # Generar un reporte inicial al cargar la vista
        self.generar_reporte(None)

    def generar_reporte(self, e):
        tipo_reporte = self.tipo_reporte_selector.value
        fecha_inicio = self.fecha_inicio_display.value
        fecha_fin = self.fecha_fin_display.value

        if not tipo_reporte:
            mostrar_snackbar(self.page, "Por favor, seleccione un tipo de reporte.")
            return

        self.progreso.visible = True
        self.tabla_reporte.rows.clear()
        self.update()

        try:
            if tipo_reporte == "Balance de Comprobación":
                self.mostrar_balance_comprobacion(fecha_inicio, fecha_fin)
            elif tipo_reporte == "Estado de Resultados":
                self.mostrar_estado_resultados(fecha_inicio, fecha_fin)
            elif tipo_reporte == "Balance General":
                self.mostrar_balance_general(fecha_fin)
        except Exception as ex:
            mostrar_snackbar(self.page, f"Error al generar el reporte: {ex}", ft.Colors.RED)
        finally:
            self.progreso.visible = False
            self.update()

    def mostrar_balance_comprobacion(self, fecha_inicio, fecha_fin):
        self.tabla_reporte.columns = [
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Nombre de Cuenta")),
            ft.DataColumn(ft.Text("Total Débitos"), numeric=True),
            ft.DataColumn(ft.Text("Total Créditos"), numeric=True),
            ft.DataColumn(ft.Text("Saldo Final"), numeric=True),
        ]

        datos = reportes_logic.generar_balance_comprobacion(fecha_inicio, fecha_fin)

        if not datos:
            mostrar_snackbar(self.page, "No se encontraron datos para el periodo seleccionado.")
            return

        total_debitos = 0
        total_creditos = 0

        for item in datos:
            self.tabla_reporte.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item['codigo'])),
                    ft.DataCell(ft.Text(item['nombre'])),
                    ft.DataCell(ft.Text(format_currency(item['total_debito']), text_align=ft.TextAlign.RIGHT)),
                    ft.DataCell(ft.Text(format_currency(item['total_credito']), text_align=ft.TextAlign.RIGHT)),
                    ft.DataCell(ft.Text(format_currency(item['saldo_final']), text_align=ft.TextAlign.RIGHT)),
                ])
            )
            total_debitos += item['total_debito']
            total_creditos += item['total_credito']

        # Fila de Totales
        self.tabla_reporte.rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("")),
                ft.DataCell(ft.Text("SUMAS IGUALES", weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(format_currency(total_debitos), weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
                ft.DataCell(ft.Text(format_currency(total_creditos), weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
                ft.DataCell(ft.Text("")),
            ], color=ft.Colors.BLUE_GREY_50)
        )

    def tipo_reporte_changed(self, e):
        # Ocultar fecha de inicio si el reporte es Balance General
        is_balance_general = self.tipo_reporte_selector.value == "Balance General"
        self.fecha_inicio_button.visible = not is_balance_general
        self.fecha_inicio_display.visible = not is_balance_general
        self.update()

    def mostrar_estado_resultados(self, fecha_inicio, fecha_fin):
        self.tabla_reporte.columns = [
            ft.DataColumn(ft.Text("")), # Para indentación
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Saldo"), numeric=True),
        ]
        datos = reportes_logic.generar_estado_resultados(fecha_inicio, fecha_fin)

        def add_row(label, value, bold=False, indent=False, color=None):
            self.tabla_reporte.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("   " if indent else "")),
                ft.DataCell(ft.Text(label, weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL)),
                ft.DataCell(ft.Text(format_currency(value), weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL, text_align=ft.TextAlign.RIGHT)),
            ], color=color))

        add_row("Ingresos Operacionales", datos['total_ingresos'], bold=True)
        for cuenta in datos['ingresos']:
            add_row(f"{cuenta['codigo']} - {cuenta['nombre']}", cuenta['saldo_final'], indent=True)

        add_row("(-) Costos de Ventas/Servicios", -datos['total_costos'], bold=True)
        for cuenta in datos['costos']:
            add_row(f"{cuenta['codigo']} - {cuenta['nombre']}", -cuenta['saldo_final'], indent=True)

        add_row("= Utilidad Bruta", datos['utilidad_bruta'], bold=True, color=ft.Colors.BLUE_GREY_50)

        add_row("(-) Gastos Operacionales", -datos['total_gastos'], bold=True)
        for cuenta in datos['gastos']:
            add_row(f"{cuenta['codigo']} - {cuenta['nombre']}", -cuenta['saldo_final'], indent=True)

        add_row("= Utilidad Antes de Impuestos", datos['utilidad_antes_impuestos'], bold=True, color=ft.Colors.BLUE_GREY_100)

    def mostrar_balance_general(self, fecha_fin):
        self.tabla_reporte.columns = [
            ft.DataColumn(ft.Text("")), # Para indentación
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Saldo"), numeric=True),
        ]
        datos = reportes_logic.generar_balance_general(fecha_fin)

        def add_row(label, value, bold=False, indent=False, color=None):
             self.tabla_reporte.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("   " if indent else "")),
                ft.DataCell(ft.Text(label, weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL)),
                ft.DataCell(ft.Text(format_currency(value), weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL, text_align=ft.TextAlign.RIGHT)),
            ], color=color))

        # Activos
        add_row("ACTIVOS", datos['total_activos'], bold=True, color=ft.Colors.BLUE_50)
        for cuenta in datos['activos']:
             add_row(f"{cuenta['codigo']} - {cuenta['nombre']}", cuenta['saldo_final'], indent=True)

        # Pasivos
        add_row("PASIVOS", datos['total_pasivos'], bold=True, color=ft.Colors.ORANGE_50)
        for cuenta in datos['pasivos']:
             add_row(f"{cuenta['codigo']} - {cuenta['nombre']}", cuenta['saldo_final'], indent=True)

        # Patrimonio
        add_row("PATRIMONIO", datos['total_patrimonio'], bold=True, color=ft.Colors.GREEN_50)
        for cuenta in datos['patrimonio']:
             add_row(f"{cuenta['codigo']} - {cuenta['nombre']}", cuenta['saldo_final'], indent=True)
        add_row("Resultado del Ejercicio", datos['resultado_del_ejercicio'], indent=True)

        # Verificación
        color_verificacion = ft.Colors.GREEN_100 if abs(datos['verificacion_ecuacion']) < 0.01 else ft.Colors.RED_100
        add_row("TOTAL PASIVO + PATRIMONIO", datos['total_pasivos'] + datos['total_patrimonio'], bold=True, color=color_verificacion)
        add_row("Verificación (Activo - Pasivo - Patrimonio)", datos['verificacion_ecuacion'], bold=True, color=color_verificacion)


def ReportesView(page: ft.Page):
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/reportes")

    return ft.View(
        "/reportes",
        appbar=ft.AppBar(
            title=ft.Text("Informes y Reportes"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            ReportesViewContent(page)
        ],
        padding=15
    )
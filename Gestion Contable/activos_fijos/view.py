# activos_fijos/view.py
import flet as ft
import datetime
from activos_fijos import logic as activos_fijos_logic
from utils.helpers import format_currency, mostrar_snackbar

class ActivosFijosView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/activos_fijos")
        self.page = page
        self.appbar = ft.AppBar(
            title=ft.Text("Gestión de Activos Fijos"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
        )

        # --- Controles ---
        self.tabla_activos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Fecha Adquisición")),
                ft.DataColumn(ft.Text("Costo"), numeric=True),
                ft.DataColumn(ft.Text("Estado")),
            ],
            rows=[],
            expand=True,
        )

        self.depreciacion_button = ft.ElevatedButton(
            "Ejecutar Depreciación Mensual",
            icon=ft.icons.CALCULATE,
            on_click=self.ejecutar_depreciacion
        )

        self.controls = [
            ft.Row(
                [
                    ft.Text("Activos Fijos", size=20, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton("Registrar Nuevo Activo", icon=ft.icons.ADD, on_click=self.mostrar_formulario_activo),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            self.depreciacion_button,
            ft.Divider(),
            ft.Column([self.tabla_activos], scroll=ft.ScrollMode.ALWAYS, expand=True)
        ]

        self.cargar_activos()

    def cargar_activos(self):
        """Carga los activos fijos en la tabla."""
        self.tabla_activos.rows.clear()
        activos = activos_fijos_logic.db_manager.obtener_activos_fijos_db()
        for activo in activos:
            self.tabla_activos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(activo['nombre'])),
                    ft.DataCell(ft.Text(activo['fecha_adquisicion'])),
                    ft.DataCell(ft.Text(format_currency(activo['costo_adquisicion']))),
                    ft.DataCell(ft.Text(activo['estado'])),
                ])
            )
        self.update()

    def mostrar_formulario_activo(self, e):
        # En una aplicación completa, esto podría ser una nueva vista o un diálogo más complejo.
        # Por simplicidad, usaremos un diálogo básico.
        mostrar_snackbar(self.page, "Funcionalidad para registrar nuevo activo no implementada en esta vista.", ft.colors.BLUE)

    def ejecutar_depreciacion(self, e):
        # Lógica para obtener el mes y año (ej: del mes anterior)
        hoy = datetime.date.today()
        primer_dia_mes = hoy.replace(day=1)
        ultimo_dia_mes_anterior = primer_dia_mes - datetime.timedelta(days=1)
        ano = ultimo_dia_mes_anterior.year
        mes = ultimo_dia_mes_anterior.month

        usuario_id = self.page.session.get("user_id")

        success = activos_fijos_logic.ejecutar_proceso_depreciacion_mensual(ano, mes, usuario_id)

        if success:
            mostrar_snackbar(self.page, f"Proceso de depreciación para {ano}-{mes} completado.", ft.colors.GREEN)
        else:
            mostrar_snackbar(self.page, f"Error en el proceso de depreciación para {ano}-{mes}.", ft.colors.RED)

        self.cargar_activos()

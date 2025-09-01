# views/conciliacion_view.py
import flet as ft
from contabilidad import conciliacion_logic
from utils.helpers import format_currency

class ConciliacionView(ft.View):
    """
    Vista para el proceso de Conciliación Bancaria.
    """
    def __init__(self, page: ft.Page):
        super().__init__(route="/conciliacion")
        self.page = page
        self.appbar = ft.AppBar(
            title=ft.Text("Conciliación Bancaria"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
        )

        # --- Controles de la UI ---
        self.cuenta_banco_selector = ft.Dropdown(
            label="Seleccionar Cuenta de Banco*",
            hint_text="Elige la cuenta a conciliar",
            # Las opciones se deberían cargar desde el PUC (cuentas de clase 'Banco')
            options=[ft.dropdown.Option("111005", "Banco Nacional")], # Placeholder
            width=300
        )
        self.cargar_datos_button = ft.ElevatedButton("Cargar Datos", icon=ft.icons.REFRESH, on_click=self.cargar_datos)

        # Tabla para Transacciones Bancarias (Izquierda)
        self.tabla_banco = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Monto"), numeric=True),
            ],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text("Cargue datos para empezar"), colspan=3)])],
            expand=True
        )

        # Tabla para Movimientos Contables (Derecha)
        self.tabla_libros = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Débito"), numeric=True),
                ft.DataColumn(ft.Text("Crédito"), numeric=True),
            ],
            rows=[ft.DataRow(cells=[ft.DataCell(ft.Text("Cargue datos para empezar"), colspan=4)])],
            expand=True
        )

        self.sugerir_button = ft.ElevatedButton("Sugerir Coincidencias", icon=ft.icons.LIGHTBULB_OUTLINE, on_click=self.sugerir, disabled=True)
        self.reconciliar_button = ft.ElevatedButton("Reconciliar Selección", icon=ft.icons.CHECK_CIRCLE_OUTLINE, on_click=self.reconciliar, disabled=True)

        self.controls = [
            ft.Row([self.cuenta_banco_selector, self.cargar_datos_button], alignment=ft.MainAxisAlignment.START),
            ft.Divider(),
            ft.Row(
                [
                    ft.Column([ft.Text("Extracto Bancario", weight=ft.FontWeight.BOLD), self.tabla_banco], expand=1),
                    ft.VerticalDivider(),
                    ft.Column([ft.Text("Libro Auxiliar de Banco", weight=ft.FontWeight.BOLD), self.tabla_libros], expand=1),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            ft.Row([self.sugerir_button, self.reconciliar_button], alignment=ft.MainAxisAlignment.CENTER)
        ]

    def cargar_datos(self, e):
        cuenta_banco = self.cuenta_banco_selector.value
        if not cuenta_banco:
            # Mostrar error
            return

        transacciones, movimientos = conciliacion_logic.obtener_datos_para_conciliacion(cuenta_banco)

        # Cargar tabla de banco
        self.tabla_banco.rows.clear()
        for t in transacciones:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(t['fecha'])),
                    ft.DataCell(ft.Text(t['descripcion'])),
                    ft.DataCell(ft.Text(format_currency(t['monto']), color=ft.colors.GREEN if t['monto'] > 0 else ft.colors.RED)),
                ],
                data=t, # Guardar el diccionario completo en la fila
                on_select_changed=self.on_row_select_changed
            )
            self.tabla_banco.rows.append(row)

        # Cargar tabla de libros
        self.tabla_libros.rows.clear()
        for m in movimientos:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(m['fecha'])),
                    ft.DataCell(ft.Text(m['descripcion_detalle'])),
                    ft.DataCell(ft.Text(format_currency(m['debito']))),
                    ft.DataCell(ft.Text(format_currency(m['credito']))),
                ],
                data=m, # Guardar el diccionario completo en la fila
                on_select_changed=self.on_row_select_changed
            )
            self.tabla_libros.rows.append(row)

        self.sugerir_button.disabled = False
        # Guardar los datos cargados para usarlos en sugerencias/reconciliación
        self.transacciones_cargadas = transacciones
        self.movimientos_cargados = movimientos
        self.update()

    def on_row_select_changed(self, e):
        """Habilita o deshabilita el botón de reconciliar basado en la selección."""
        selected_banco = [row for row in self.tabla_banco.rows if row.selected]
        selected_libros = [row for row in self.tabla_libros.rows if row.selected]

        self.reconciliar_button.disabled = not (len(selected_banco) == 1 and len(selected_libros) == 1)
        self.update()

    def sugerir(self, e):
        """Llama a la lógica de sugerencias y resalta las filas."""
        sugerencias = conciliacion_logic.sugerir_coincidencias(self.transacciones_cargadas, self.movimientos_cargados)

        # Resetear colores
        for row in self.tabla_banco.rows: row.color = ""
        for row in self.tabla_libros.rows: row.color = ""

        color_sugerencia = ft.colors.LIGHT_BLUE_100
        for i, sugerencia in enumerate(sugerencias):
            trans_id = sugerencia['transaccion']['id']
            mov_id = sugerencia['movimiento']['id']

            # Encontrar y colorear las filas correspondientes
            for row in self.tabla_banco.rows:
                if row.data['id'] == trans_id: row.color = color_sugerencia
            for row in self.tabla_libros.rows:
                if row.data['id'] == mov_id: row.color = color_sugerencia
        self.update()

    def reconciliar(self, e):
        """Toma las filas seleccionadas y las reconcilia."""
        selected_banco_row = next((row for row in self.tabla_banco.rows if row.selected), None)
        selected_libro_row = next((row for row in self.tabla_libros.rows if row.selected), None)

        if not selected_banco_row or not selected_libro_row:
            return

        trans_id = selected_banco_row.data['id']
        mov_id = selected_libro_row.data['id']

        success = conciliacion_logic.reconciliar_par(movimiento_id=mov_id, transaccion_id=trans_id)

        if success:
            # Recargar los datos para refrescar las listas
            self.cargar_datos(None)
        else:
            # Mostrar error
            pass

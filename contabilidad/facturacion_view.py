# views/facturacion_view.py
import flet as ft
import datetime
from contabilidad import facturacion_logic
from utils.helpers import format_currency

class FacturacionView(ft.View):
    """
    Vista principal para el módulo de facturación.
    Muestra la lista de facturas y permite crear nuevas.
    """
    def __init__(self, page: ft.Page):
        super().__init__(route="/facturacion")
        self.page = page
        self.appbar = ft.AppBar(
            title=ft.Text("Módulo de Facturación"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
        )

        self.tabla_facturas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Fecha Emisión")),
                ft.DataColumn(ft.Text("Total"), numeric=True),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
            expand=True,
        )

        self.controls = [
            ft.Row(
                [
                    ft.Text("Historial de Facturas", size=20, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "Crear Nueva Factura",
                        icon=ft.icons.ADD,
                        on_click=lambda _: self.page.go("/facturacion/nueva") # Navegar a la vista de creación
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(height=10),
            ft.Container(
                content=self.tabla_facturas,
                expand=True,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(5)
            )
        ]

        self.cargar_facturas()

    def cargar_facturas(self):
        """Carga las facturas desde la capa de lógica y las muestra en la tabla."""
        self.tabla_facturas.rows.clear()
        facturas = facturacion_logic.obtener_todas_las_facturas()

        if not facturas:
            self.tabla_facturas.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("No se han encontrado facturas.", italic=True), colspan=6)]))
        else:
            for f in facturas:
                self.tabla_facturas.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(f['id'])),
                            ft.DataCell(ft.Text(f['cliente_nombre'])),
                            ft.DataCell(ft.Text(f['fecha_emision'])),
                            ft.DataCell(ft.Text(format_currency(f['total']), text_align=ft.TextAlign.RIGHT)),
                            ft.DataCell(ft.Chip(ft.Text(f['estado']))), # Usar un Chip para el estado
                            ft.DataCell(
                                ft.IconButton(
                                    icon=ft.icons.VISIBILITY,
                                    tooltip="Ver Detalle",
                                    # on_click=lambda e, fid=f['id']: self.page.go(f"/facturacion/{fid}") # Futura implementación
                                )
                            ),
                        ]
                    )
                )
        self.update()

class FacturaFormView(ft.View):
    """
    Vista de formulario para crear o editar una factura.
    """
    def __init__(self, page: ft.Page):
        super().__init__(route="/facturacion/nueva")
        self.page = page
        self.appbar = ft.AppBar(
            title=ft.Text("Crear Nueva Factura"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/facturacion"))
        )

        # --- Controles del Formulario ---
        self.cliente_dropdown = ft.Dropdown(label="Cliente*", hint_text="Seleccione un cliente")
        self.fecha_emision_picker = ft.DatePicker(on_change=self._on_date_change)
        self.page.overlay.append(self.fecha_emision_picker)
        self.fecha_emision_button = ft.ElevatedButton("Fecha Emisión*", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.fecha_emision_picker.pick_date())
        self.fecha_emision_display = ft.Text(datetime.date.today().isoformat())

        self.items_container = ft.Column(controls=[], spacing=5)
        self.total_display = ft.Text("Total Factura: $ 0.00", size=16, weight=ft.FontWeight.BOLD)

        self.controls = [
            ft.Row([self.cliente_dropdown, self.fecha_emision_button, self.fecha_emision_display], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=20),
            ft.Text("Items de la Factura", size=16, weight=ft.FontWeight.BOLD),
            self.items_container,
            ft.IconButton(icon=ft.icons.ADD, on_click=self.agregar_item_fila, tooltip="Añadir Item"),
            ft.Divider(height=20),
            self.total_display,
            ft.ElevatedButton("Guardar Factura", icon=ft.icons.SAVE, on_click=self.guardar_factura),
        ]

        self.cargar_clientes()
        self.agregar_item_fila(None) # Añadir una fila inicial

    def _on_date_change(self, e):
        if e.control == self.fecha_emision_picker and self.fecha_emision_picker.value:
            self.fecha_emision_display.value = self.fecha_emision_picker.value.strftime('%Y-%m-%d')
            self.update()

    def cargar_clientes(self):
        from contabilidad import terceros_logic # Importación local para evitar importación circular a nivel de módulo
        clientes = terceros_logic.get_clientes()
        self.cliente_dropdown.options = [
            ft.dropdown.Option(key=c['id'], text=f"{c['nombre']} (NIT: {c['nit']})") for c in clientes
        ]

    def agregar_item_fila(self, e):
        desc_field = ft.TextField(label="Descripción", expand=3)
        cant_field = ft.TextField(label="Cantidad", value="1", width=100, on_change=self.actualizar_total)
        precio_field = ft.TextField(label="Precio Unitario", value="0", prefix_text="$", width=150, on_change=self.actualizar_total)
        subtotal_text = ft.Text("Subtotal: $ 0.00", width=150)

        new_row = ft.Row(
            [
                desc_field,
                cant_field,
                precio_field,
                subtotal_text,
                ft.IconButton(icon=ft.icons.REMOVE_CIRCLE_OUTLINE, icon_color=ft.colors.RED, data=None, on_click=self.eliminar_item_fila)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        new_row.controls[-1].data = new_row # Asociar la fila al botón de eliminar
        self.items_container.controls.append(new_row)
        self.update()
        self.actualizar_total(None)

    def eliminar_item_fila(self, e):
        row_to_delete = e.control.data
        self.items_container.controls.remove(row_to_delete)
        self.update()
        self.actualizar_total(None)

    def actualizar_total(self, e):
        total_factura = 0
        for row in self.items_container.controls:
            try:
                cantidad = float(row.controls[1].value or 0)
                precio = float(row.controls[2].value or 0)
                subtotal = cantidad * precio
                row.controls[3].value = f"Subtotal: {format_currency(subtotal)}"
                total_factura += subtotal
            except (ValueError, TypeError):
                continue # Ignorar si los campos no son números válidos

        self.total_display.value = f"Total Factura: {format_currency(total_factura)}"
        self.update()

    def guardar_factura(self, e):
        # Recopilar datos
        cliente_id = self.cliente_dropdown.value
        fecha_emision = self.fecha_emision_display.value
        usuario_id = self.page.session.get("user_id")

        if not cliente_id or not fecha_emision or not usuario_id:
            # Mostrar error
            return

        items = []
        for row in self.items_container.controls:
            try:
                descripcion = row.controls[0].value
                cantidad = float(row.controls[1].value or 0)
                precio = float(row.controls[2].value or 0)
                if descripcion and cantidad > 0 and precio > 0:
                    items.append({
                        "descripcion": descripcion,
                        "cantidad": cantidad,
                        "precio_unitario": precio,
                        "subtotal": cantidad * precio
                    })
            except (ValueError, TypeError):
                continue

        if not items:
            # Mostrar error
            return

        # Llamar a la lógica de negocio
        success, factura_id = facturacion_logic.crear_nueva_factura(
            tercero_id=int(cliente_id),
            fecha_emision=fecha_emision,
            items=items,
            usuario_id=usuario_id
        )

        if success:
            self.page.go("/facturacion")
        else:
            # Mostrar error
            pass

# NOTA: La vista de creación/edición se manejará por separado para mayor claridad.
# El router principal deberá ser capaz de manejar rutas como "/facturacion/nueva".

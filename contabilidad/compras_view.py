# views/compras_view.py
import flet as ft
import datetime
from contabilidad import compras_logic, terceros_logic
from utils.helpers import format_currency

class ComprasView(ft.View):
    """
    Vista principal para el módulo de Compras.
    Muestra la lista de facturas de proveedores.
    """
    def __init__(self, page: ft.Page):
        super().__init__(route="/compras")
        self.page = page
        self.appbar = ft.AppBar(
            title=ft.Text("Módulo de Compras"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
        )

        self.tabla_compras = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Proveedor")),
                ft.DataColumn(ft.Text("Fecha Emisión")),
                ft.DataColumn(ft.Text("Total"), numeric=True),
                ft.DataColumn(ft.Text("Estado")),
            ],
            rows=[],
            expand=True,
        )

        self.controls = [
            ft.Row(
                [
                    ft.Text("Historial de Compras", size=20, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "Registrar Nueva Compra",
                        icon=ft.icons.ADD,
                        on_click=lambda _: self.page.go("/compras/nueva")
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(height=10),
            ft.Container(content=self.tabla_compras, expand=True, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5))
        ]

        self.cargar_compras()

    def cargar_compras(self):
        self.tabla_compras.rows.clear()
        compras = compras_logic.obtener_todas_las_compras()
        if not compras:
            self.tabla_compras.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("No se han encontrado compras.", italic=True), colspan=5)]))
        else:
            for c in compras:
                self.tabla_compras.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(c['id'])),
                        ft.DataCell(ft.Text(c['proveedor_nombre'])),
                        ft.DataCell(ft.Text(c['fecha_emision'])),
                        ft.DataCell(ft.Text(format_currency(c['total']), text_align=ft.TextAlign.RIGHT)),
                        ft.DataCell(ft.Chip(ft.Text(c['estado']))),
                    ])
                )
        self.update()

class CompraFormView(ft.View):
    """
    Vista de formulario para registrar una nueva factura de compra.
    """
    def __init__(self, page: ft.Page):
        super().__init__(route="/compras/nueva")
        self.page = page
        self.appbar = ft.AppBar(
            title=ft.Text("Registrar Nueva Compra"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/compras"))
        )

        self.proveedor_dropdown = ft.Dropdown(label="Proveedor*", hint_text="Seleccione un proveedor")
        self.fecha_emision_picker = ft.DatePicker(on_change=self._on_date_change)
        self.page.overlay.append(self.fecha_emision_picker)
        self.fecha_emision_button = ft.ElevatedButton("Fecha Emisión*", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: self.fecha_emision_picker.pick_date())
        self.fecha_emision_display = ft.Text(datetime.date.today().isoformat())

        self.items_container = ft.Column(controls=[], spacing=5)
        self.total_display = ft.Text("Total Compra: $ 0.00", size=16, weight=ft.FontWeight.BOLD)

        self.controls = [
            ft.Row([self.proveedor_dropdown, self.fecha_emision_button, self.fecha_emision_display], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=20),
            ft.Text("Items de la Compra", size=16, weight=ft.FontWeight.BOLD),
            self.items_container,
            ft.IconButton(icon=ft.icons.ADD, on_click=self.agregar_item_fila, tooltip="Añadir Item"),
            ft.Divider(height=20),
            self.total_display,
            ft.ElevatedButton("Guardar Compra", icon=ft.icons.SAVE, on_click=self.guardar_compra),
        ]

        self.cargar_proveedores()
        self.agregar_item_fila(None)

    def _on_date_change(self, e):
        if self.fecha_emision_picker.value:
            self.fecha_emision_display.value = self.fecha_emision_picker.value.strftime('%Y-%m-%d')
            self.update()

    def cargar_proveedores(self):
        proveedores = terceros_logic.get_proveedores()
        self.proveedor_dropdown.options = [
            ft.dropdown.Option(key=p['id'], text=f"{p['nombre']} (NIT: {p['nit']})") for p in proveedores
        ]

    def agregar_item_fila(self, e):
        new_row = ft.Row([
            ft.TextField(label="Descripción", expand=3),
            ft.TextField(label="Cantidad", value="1", width=100, on_change=self.actualizar_total),
            ft.TextField(label="Precio Unitario", value="0", prefix_text="$", width=150, on_change=self.actualizar_total),
            ft.Text("Subtotal: $ 0.00", width=150),
            ft.IconButton(icon=ft.icons.REMOVE_CIRCLE_OUTLINE, icon_color=ft.Colors.RED, data=None, on_click=self.eliminar_item_fila)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        new_row.controls[-1].data = new_row
        self.items_container.controls.append(new_row)
        self.update()
        self.actualizar_total(None)

    def eliminar_item_fila(self, e):
        self.items_container.controls.remove(e.control.data)
        self.update()
        self.actualizar_total(None)

    def actualizar_total(self, e):
        total_compra = 0
        for row in self.items_container.controls:
            try:
                cantidad = float(row.controls[1].value or 0)
                precio = float(row.controls[2].value or 0)
                subtotal = cantidad * precio
                row.controls[3].value = f"Subtotal: {format_currency(subtotal)}"
                total_compra += subtotal
            except (ValueError, TypeError): continue
        self.total_display.value = f"Total Compra: {format_currency(total_compra)}"
        self.update()

    def guardar_compra(self, e):
        proveedor_id = self.proveedor_dropdown.value
        fecha_emision = self.fecha_emision_display.value
        usuario_id = self.page.session.get("user_id")

        if not all([proveedor_id, fecha_emision, usuario_id]):
            # Mostrar error
            return

        items = []
        for row in self.items_container.controls:
            try:
                descripcion = row.controls[0].value
                cantidad = float(row.controls[1].value or 0)
                precio = float(row.controls[2].value or 0)
                if descripcion and cantidad > 0 and precio > 0:
                    items.append({"descripcion": descripcion, "cantidad": cantidad, "precio_unitario": precio, "subtotal": cantidad * precio})
            except (ValueError, TypeError): continue

        if not items:
            # Mostrar error
            return

        success, _ = compras_logic.crear_nueva_compra(
            tercero_id=int(proveedor_id),
            fecha_emision=fecha_emision,
            items=items,
            usuario_id=usuario_id
        )

        if success:
            self.page.go("/compras")
        else:
            # Mostrar error
            pass

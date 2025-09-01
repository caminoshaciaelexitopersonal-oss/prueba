# views/inventario_view.py
import flet as ft
from inventario import inventario_logic
from utils.helpers import format_currency

class InventarioView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/inventario")
        self.page = page
        self.appbar = ft.AppBar(
            title=ft.Text("Gestión de Inventario"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
        )

        # --- Controles de la UI ---
        self.file_picker = ft.FilePicker(on_result=self.on_file_picker_result)
        self.page.overlay.append(self.file_picker) # El FilePicker es un overlay

        self.import_button = ft.ElevatedButton(
            "Importar Productos desde CSV",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["csv"]
            )
        )
        self.status_text = ft.Text()

        self.tabla_productos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("SKU")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Stock"), numeric=True),
                ft.DataColumn(ft.Text("Costo Promedio"), numeric=True),
            ],
            rows=[],
            expand=True
        )

        self.help_text = ft.Text(
            "El archivo CSV debe contener las siguientes columnas: nombre,sku,descripcion,costo_inicial,cantidad_inicial",
            italic=True,
            color=ft.colors.GREY_600
        )

        self.controls = [
            ft.Row([self.import_button]),
            ft.Row([self.help_text]),
            ft.Row([self.status_text]),
            ft.Divider(),
            ft.Column([self.tabla_productos], scroll=ft.ScrollMode.ALWAYS)
        ]

        # Cargar los productos al iniciar la vista
        self.cargar_productos()

    def cargar_productos(self):
        """Carga o recarga la tabla de productos desde la base de datos."""
        self.tabla_productos.rows.clear()
        productos = inventario_logic.obtener_productos()
        for p in productos:
            self.tabla_productos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p['sku'])),
                    ft.DataCell(ft.Text(p['nombre'])),
                    ft.DataCell(ft.Text(str(p['cantidad_disponible']))),
                    ft.DataCell(ft.Text(format_currency(p['costo_unitario_promedio']))),
                ])
            )
        self.update()

    def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            filepath = e.files[0].path
            self.status_text.value = f"Procesando archivo: {e.files[0].name}..."
            self.update()

            # Llamar a la lógica de importación
            resumen = inventario_logic.importar_productos_csv(filepath)

            # Mostrar resultados
            creados = resumen.get("creados", 0)
            errores = resumen.get("errores", [])

            status_message = f"Importación completada: {creados} productos creados."
            if errores:
                status_message += f" Se encontraron {len(errores)} errores."
                # En una app real, mostraríamos los errores en un diálogo o un área de texto.
                print("Errores de importación:", errores)

            self.status_text.value = status_message
            self.cargar_productos() # Recargar la tabla con los nuevos productos
            self.update()
        else:
            self.status_text.value = "No se seleccionó ningún archivo."
            self.update()

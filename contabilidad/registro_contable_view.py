# views/registro_contable_view.py
import flet as ft
import datetime
from database.db_manager import obtener_cuentas_puc # Se mantiene para el dropdown
from contabilidad import contabilidad_logic
from utils.constants import TIPOS_COMPROBANTE_OPCIONES
from utils.helpers import mostrar_snackbar, format_currency

class RegistroContableViewContent(ft.UserControl):
    """Contenido para registrar comprobantes contables."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.cuentas_puc = [] # Cache local de cuentas PUC
        self.movimientos = [] # Lista para guardar los controles de las filas de movimiento
        self.user_id = page.session.get("user_id")

        # Controles para datos del comprobante
        self.fecha_picker = ft.DatePicker(
             on_change=self._on_date_change,
             # Puedes añadir first_date, last_date si quieres limitar
        )
        # self.fecha_field = ft.TextField(label="Fecha (AAAA-MM-DD)", width=150, value=datetime.date.today().isoformat(), read_only=True) # Podría ser un DatePicker
        self.fecha_button = ft.ElevatedButton(
            "Seleccionar Fecha",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.fecha_picker.pick_date(),
        )
        self.fecha_display = ft.Text(datetime.date.today().isoformat()) # Muestra fecha seleccionada
        self.tipo_comprobante = ft.Dropdown(
            label="Tipo de Comprobante",
            options=[ft.dropdown.Option(key=tipo) for tipo in TIPOS_COMPROBANTE_OPCIONES],
            width=250,
        )
        self.descripcion_comprobante = ft.TextField(label="Descripción General", multiline=True, max_lines=2, width=400)

        # Sección para agregar movimientos (dinámica)
        self.movimientos_container = ft.Column(controls=[], spacing=5, scroll=ft.ScrollMode.ADAPTIVE)

        # Totales
        self.total_debito_text = ft.Text("Total Débito: $ 0", weight=ft.FontWeight.BOLD)
        self.total_credito_text = ft.Text("Total Crédito: $ 0", weight=ft.FontWeight.BOLD)
        self.diferencia_text = ft.Text("Diferencia: $ 0", color=ft.colors.GREEN, weight=ft.FontWeight.BOLD)

        # Lista de comprobantes recientes
        self.tabla_comprobantes = ft.DataTable(
             columns=[
                 ft.DataColumn(ft.Text("ID")),
                 ft.DataColumn(ft.Text("Fecha")),
                 ft.DataColumn(ft.Text("Tipo")),
                 ft.DataColumn(ft.Text("Descripción")),
                 ft.DataColumn(ft.Text("Débito"), numeric=True),
                 ft.DataColumn(ft.Text("Crédito"), numeric=True),
                 ft.DataColumn(ft.Text("Acciones")),
             ],
             rows=[],
             column_spacing=15,
             # expand=True
        )
        # Diálogo para ver detalles
        self.detalle_dlg = ft.AlertDialog(
             title=ft.Text("Detalle del Comprobante"),
             content=ft.Column(scroll=ft.ScrollMode.ADAPTIVE, tight=True),
             modal=True
        )

        # Registrar DatePicker y diálogo en la page
        self.page.overlay.append(self.fecha_picker)
        self.page.dialog = self.detalle_dlg

    def _cargar_cuentas_puc(self):
        """Carga las cuentas del PUC para los Dropdowns."""
        self.cuentas_puc = obtener_cuentas_puc()
        # Idealmente, filtrar solo cuentas de detalle (último nivel), pero para empezar, todas.
        # self.cuentas_puc = [c for c in self.cuentas_puc if not any(o['codigo'].startswith(c['codigo'] + '.') for o in self.cuentas_puc if o['codigo'] != c['codigo'])]

    def _on_date_change(self, e):
         if self.fecha_picker.value:
             self.fecha_display.value = self.fecha_picker.value.strftime('%Y-%m-%d')
             self.update()


    def build(self):
        # Cargar las cuentas al construir el control por primera vez
        self._cargar_cuentas_puc()

        return ft.Column(
            [
                ft.Text("Registro de Comprobantes", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10),
                # Sección de Datos del Comprobante
                ft.Card(ft.Container(padding=15, content=ft.Column([
                     ft.Row([
                         ft.Text("Fecha: "), self.fecha_display, self.fecha_button
                         ], alignment=ft.MainAxisAlignment.START),
                     ft.Row([self.tipo_comprobante, self.descripcion_comprobante], alignment=ft.MainAxisAlignment.START),
                     ], spacing=10))),

                 ft.Divider(height=15),

                # Sección de Movimientos
                 ft.Text("Movimientos Contables (Partida Doble):", weight=ft.FontWeight.W_500),
                 ft.Row( # Encabezados de movimientos
                     [
                         ft.Text("Cuenta Contable", width=250, weight=ft.FontWeight.BOLD),
                         ft.Text("Descripción Detalle", width=200, weight=ft.FontWeight.BOLD),
                         ft.Text("Débito ($)", width=100, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD),
                         ft.Text("Crédito ($)", width=100, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD),
                         ft.Text("Tipo Activo", width=150, weight=ft.FontWeight.BOLD),
                         ft.Text("Método Depreciación", width=150, weight=ft.FontWeight.BOLD),
                         ft.Text("Valor Razonable", width=100, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD),
                         ft.Text("Vida Útil (Meses)", width=100, text_align=ft.TextAlign.RIGHT, weight=ft.FontWeight.BOLD),
                         ft.Text("", width=50) # Espacio para botón eliminar fila
                     ], alignment=ft.MainAxisAlignment.START),
                 ft.Container(
                      content=self.movimientos_container,
                      # border=ft.border.all(1, ft.colors.OUTLINE),
                      padding=ft.padding.only(bottom=5),
                      height=200, # Altura fija para el área de movimientos scrollable
                 ),
                 ft.Row(
                     [
                         ft.IconButton(
                             icon=ft.icons.ADD,
                             tooltip="Añadir Movimiento",
                             on_click=self.agregar_fila_movimiento,
                         ),
                     ],
                 ),
                 ft.Divider(height=10),

                # Sección de Totales y Guardado
                 ft.Row(
                     [
                         self.total_debito_text,
                         self.total_credito_text,
                         self.diferencia_text,
                     ],
                     alignment=ft.MainAxisAlignment.SPACE_AROUND
                 ),
                 ft.ElevatedButton("Guardar Comprobante", icon=ft.icons.SAVE, on_click=self.guardar_comprobante),

                 ft.Divider(height=20),
                 ft.Text("Comprobantes Recientes", size=16, weight=ft.FontWeight.BOLD),
                 ft.Container( # Para hacer scrollable la tabla si es necesario
                    content=self.tabla_comprobantes,
                    expand=False, # No expandir verticalmente aquí, o se sale
                    # height=300 # Podrías limitar la altura si quieres
                    border=ft.border.all(1, ft.colors.OUTLINE), # Borde opcional
                    border_radius=ft.border_radius.all(5)
                 ),
                 ft.IconButton(icon=ft.icons.REFRESH, tooltip="Recargar Comprobantes", on_click=lambda e: self.cargar_comprobantes_recientes())
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=10
        )

    def did_mount(self):
        """Al montar, añadir una fila inicial y cargar comprobantes."""
        if not self.movimientos: # Añadir filas iniciales solo si está vacío
            self.agregar_fila_movimiento(None)
            self.agregar_fila_movimiento(None) # Empezar con 2 filas
        self.cargar_comprobantes_recientes()

    def agregar_fila_movimiento(self, e):
        """Añade una nueva fila de controles para un movimiento."""
        if not self.cuentas_puc:
             mostrar_snackbar(self.page, "Error: No se pudieron cargar las cuentas del PUC.")
             return

        cuenta_dropdown = ft.Dropdown(
            # label="Cuenta",
            dense=True,
            width=250,
            options=[ft.dropdown.Option(key=c['codigo'], text=f"{c['codigo']} - {c['nombre'][:30]}") for c in self.cuentas_puc]
        )
        desc_detalle_field = ft.TextField(label="Detalle", dense=True, width=200)
        debito_field = ft.TextField(label="Débito", prefix_text="$", dense=True, width=100, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER, on_change=self._on_valor_change)
        credito_field = ft.TextField(label="Crédito", prefix_text="$", dense=True, width=100, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER, on_change=self._on_valor_change)
        tipo_activo_field = ft.TextField(label="Tipo Activo", dense=True, width=150)
        metodo_depreciacion_dropdown = ft.Dropdown(label="Método Depreciación", dense=True, width=150, options=[
            ft.dropdown.Option("Lineal"),
            ft.dropdown.Option("Decreciente")
        ])
        valor_razonable_field = ft.TextField(label="Valor Razonable", prefix_text="$", dense=True, width=100, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER)
        vida_util_estimada_field = ft.TextField(label="Vida Útil (Meses)", dense=True, width=100, text_align=ft.TextAlign.RIGHT, keyboard_type=ft.KeyboardType.NUMBER)

        # Enlazar débito y crédito: si se escribe en uno, limpiar el otro
        def clear_other(event):
            field = event.control
            row_controls = event.control.data # Obtenemos la referencia a la fila
            other_field = None
            if field == debito_field and field.value:
                other_field = next((ctrl for ctrl in row_controls if isinstance(ctrl, ft.TextField) and ctrl.label == "Crédito"), None)
            elif field == credito_field and field.value:
                other_field = next((ctrl for ctrl in row_controls if isinstance(ctrl, ft.TextField) and ctrl.label == "Débito"), None)

            if other_field:
                 other_field.value = ""
                 other_field.update() # Actualizar el campo borrado
            self._actualizar_totales()

        debito_field.on_change = clear_other
        credito_field.on_change = clear_other

        # Botón eliminar esta fila específica
        delete_button = ft.IconButton(
            ft.icons.REMOVE_CIRCLE_OUTLINE,
            icon_color=ft.colors.RED,
            tooltip="Eliminar Movimiento",
            data=None, # Se establecerá después
            on_click=self.eliminar_fila_movimiento
        )

        # Crear la fila
        new_row = ft.Row(
            [cuenta_dropdown, desc_detalle_field, debito_field, credito_field, tipo_activo_field, metodo_depreciacion_dropdown, valor_razonable_field, vida_util_estimada_field, delete_button],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # Asociar los controles a la fila y viceversa para referencias
        debito_field.data = new_row.controls
        credito_field.data = new_row.controls
        delete_button.data = new_row # Asociar el botón a la fila que debe eliminar

        self.movimientos.append(new_row) # Guardar la referencia a la fila completa
        self.movimientos_container.controls.append(new_row)
        self.update() # Actualizar la vista
        self._actualizar_totales() # Recalcular totales

    def _on_valor_change(self, e):
         """Se llama cuando cambia un valor de débito o crédito para recalcular totales."""
         # (Se eliminó el código que borraba el otro campo aquí, se hace en clear_other)
         self._actualizar_totales()


    def eliminar_fila_movimiento(self, e):
        """Elimina la fila de movimiento asociada al botón presionado."""
        fila_a_eliminar = e.control.data # Obtenemos la fila desde el botón

        if fila_a_eliminar in self.movimientos:
            self.movimientos.remove(fila_a_eliminar)
            self.movimientos_container.controls.remove(fila_a_eliminar)
            self.update()
            self._actualizar_totales()

    def _actualizar_totales(self):
        """Calcula y muestra los totales de débito y crédito."""
        total_debito = 0.0
        total_credito = 0.0

        for fila in self.movimientos:
             # Acceder a los TextField dentro de la fila por índice o referencia guardada
             try:
                 debito_field = next((ctrl for ctrl in fila.controls if isinstance(ctrl, ft.TextField) and ctrl.label == "Débito"), None)
                 credito_field = next((ctrl for ctrl in fila.controls if isinstance(ctrl, ft.TextField) and ctrl.label == "Crédito"), None)

                 if debito_field and debito_field.value:
                      total_debito += float(debito_field.value.replace(",", "") or 0) # Limpiar comas si las hay
                 if credito_field and credito_field.value:
                     total_credito += float(credito_field.value.replace(",", "") or 0)
             except (ValueError, IndexError, StopIteration):
                 # Ignorar filas incompletas o con errores de formato
                 pass


        self.total_debito_text.value = f"Total Débito: {format_currency(total_debito)}"
        self.total_credito_text.value = f"Total Crédito: {format_currency(total_credito)}"

        diferencia = total_debito - total_credito
        self.diferencia_text.value = f"Diferencia: {format_currency(diferencia)}"
        self.diferencia_text.color = ft.colors.RED if abs(diferencia) > 0.01 else ft.colors.GREEN # Rojo si no cuadra

        self.update() # Actualiza los textos de totales

    def obtener_datos_movimientos(self) -> list[dict]:
        """Extrae los datos de las filas de movimientos en formato diccionario."""
        datos_movimientos = []
        for fila in self.movimientos:
             try:
                cuenta_dropdown = next((ctrl for ctrl in fila.controls if isinstance(ctrl, ft.Dropdown)), None)
                desc_detalle_field = next((ctrl for ctrl in fila.controls if isinstance(ctrl, ft.TextField) and ctrl.label == "Detalle"), None)
                debito_field = next((ctrl for ctrl in fila.controls if isinstance(ctrl, ft.TextField) and ctrl.label == "Débito"), None)
                credito_field = next((ctrl for ctrl in fila.controls if isinstance(ctrl, ft.TextField) and ctrl.label == "Crédito"), None)

                codigo_cuenta = cuenta_dropdown.value if cuenta_dropdown else None
                debito_valor = float(debito_field.value.replace(",", "") or 0) if debito_field else 0.0
                credito_valor = float(credito_field.value.replace(",", "") or 0) if credito_field else 0.0

                # Solo incluir si hay cuenta y algún valor
                if codigo_cuenta and (debito_valor > 0 or credito_valor > 0):
                     datos_movimientos.append({
                         'cuenta_codigo': codigo_cuenta,
                         'descripcion_detalle': desc_detalle_field.value.strip() if desc_detalle_field else None,
                         'debito': debito_valor,
                         'credito': credito_valor,
                         'tipo_activo': tipo_activo_field.value,
                         'metodo_depreciacion': metodo_depreciacion_dropdown.value,
                         'valor_razonable': valor_razonable_field.value,
                         'vida_util_estimada': vida_util_estimada_field.value,
                     })
             except (ValueError, IndexError, StopIteration, AttributeError):
                 mostrar_snackbar(self.page, "Error al procesar una fila de movimiento. Verifique los datos.", ft.colors.ORANGE)
                 # Podrías decidir detener el proceso o solo saltar la fila
                 continue # Saltar fila con error y continuar
        return datos_movimientos


    def guardar_comprobante(self, e):
        """Valida y guarda el comprobante y sus movimientos."""
        if not self.user_id:
             mostrar_snackbar(self.page, "Error: Sesión de usuario no válida.", ft.colors.RED)
             return

        fecha = self.fecha_display.value # Ya está en formato AAAA-MM-DD
        tipo = self.tipo_comprobante.value
        descripcion = self.descripcion_comprobante.value.strip()

        if not fecha or not tipo or not descripcion:
            mostrar_snackbar(self.page, "Fecha, Tipo y Descripción del comprobante son requeridos.")
            return

        movimientos_data = self.obtener_datos_movimientos()

        if not movimientos_data:
            mostrar_snackbar(self.page, "Debe agregar al menos un movimiento contable con valor.")
            return

        # La validación de partida doble ahora se hace en la capa de lógica.
        # Intentar guardar usando la capa de lógica
        success, comprobante_id = contabilidad_logic.registrar_nuevo_comprobante(
            fecha=fecha,
            tipo=tipo,
            descripcion=descripcion,
            movimientos=movimientos_data,
            usuario_id=self.user_id # Pasar el ID del usuario de la sesión
        )

        if success:
            mostrar_snackbar(self.page, f"Comprobante {comprobante_id} guardado exitosamente.", ft.colors.GREEN)
            self.limpiar_formulario_comprobante()
            self.cargar_comprobantes_recientes() # Recargar la lista
        else:
            mostrar_snackbar(self.page, "Error al guardar el comprobante en la base de datos.")


    def limpiar_formulario_comprobante(self):
        """Limpia todos los campos del formulario de comprobante."""
        # self.fecha_field.value = datetime.date.today().isoformat() # Opcional: resetear fecha
        self.tipo_comprobante.value = None
        self.descripcion_comprobante.value = ""

        # Eliminar todas las filas de movimiento y añadir 2 nuevas vacías
        self.movimientos.clear()
        self.movimientos_container.controls.clear()
        self.agregar_fila_movimiento(None)
        self.agregar_fila_movimiento(None)

        self._actualizar_totales() # Resetear totales a 0
        self.update()

    def cargar_comprobantes_recientes(self, limit=20):
        """Carga los últimos comprobantes guardados."""
        comprobantes_db = contabilidad_logic.obtener_lista_comprobantes(limit=limit)
        self.tabla_comprobantes.rows.clear()
        for comp in comprobantes_db:
            self.tabla_comprobantes.rows.append(
                ft.DataRow(
                     [
                        ft.DataCell(ft.Text(comp['id'])),
                        ft.DataCell(ft.Text(comp['fecha'])),
                        ft.DataCell(ft.Text(comp['tipo'])),
                        ft.DataCell(ft.Text(comp['descripcion'][:40] + ('...' if len(comp['descripcion']) > 40 else ''))), # Acortar desc
                        ft.DataCell(ft.Text(format_currency(comp['total_debito']), text_align=ft.TextAlign.RIGHT)),
                        ft.DataCell(ft.Text(format_currency(comp['total_credito']), text_align=ft.TextAlign.RIGHT)),
                         ft.DataCell(
                             ft.Row([
                                ft.IconButton(ft.icons.VISIBILITY, tooltip="Ver Detalles", data=comp['id'], on_click=self.mostrar_detalle_comprobante),
                                # ft.IconButton(ft.icons.EDIT, tooltip="Editar", data=comp['id'], on_click=self.editar_comprobante), # Pendiente
                                # ft.IconButton(ft.icons.DELETE_FOREVER, tooltip="Anular", data=comp['id'], on_click=self.anular_comprobante), # Pendiente
                             ])
                        ),
                     ]
                 )
            )
        self.update()

    def mostrar_detalle_comprobante(self, e):
        comprobante_id = e.control.data
        movimientos = contabilidad_logic.obtener_detalle_comprobante(comprobante_id)

        if not movimientos:
            mostrar_snackbar(self.page, f"No se encontraron movimientos para el comprobante {comprobante_id}.")
            return

        # Construir contenido del diálogo
        detalle_content = [
            ft.DataTable(
                 columns=[
                     ft.DataColumn(ft.Text("Código")),
                     ft.DataColumn(ft.Text("Cuenta")),
                     ft.DataColumn(ft.Text("Detalle")),
                     ft.DataColumn(ft.Text("Débito"), numeric=True),
                     ft.DataColumn(ft.Text("Crédito"), numeric=True),
                     ft.DataColumn(ft.Text("Tipo Activo")),
                     ft.DataColumn(ft.Text("Método Depreciación")),
                     ft.DataColumn(ft.Text("Valor Razonable"), numeric=True),
                     ft.DataColumn(ft.Text("Vida Útil (Meses)"), numeric=True),
                 ],
                 rows=[
                    ft.DataRow(
                         [
                            ft.DataCell(ft.Text(m['cuenta_codigo'])),
                            ft.DataCell(ft.Text(m['cuenta_nombre'])),
                            ft.DataCell(ft.Text(m.get('descripcion_detalle', ''))),
                            ft.DataCell(ft.Text(format_currency(m['debito']), text_align=ft.TextAlign.RIGHT)),
                            ft.DataCell(ft.Text(format_currency(m['credito']), text_align=ft.TextAlign.RIGHT)),
                            ft.DataCell(ft.Text(m.get('tipo_activo', ''))),
                            ft.DataCell(ft.Text(m.get('metodo_depreciacion', ''))),
                            ft.DataCell(ft.Text(m.get('valor_razonable', ''), text_align=ft.TextAlign.RIGHT)),
                            ft.DataCell(ft.Text(m.get('vida_util_estimada', ''), text_align=ft.TextAlign.RIGHT)),
                         ]
                     ) for m in movimientos
                 ]
            )
        ]
        self.detalle_dlg.content = ft.Column(detalle_content, scroll=ft.ScrollMode.ADAPTIVE, height=300, width=700) # Ajusta tamaño
        self.detalle_dlg.title = ft.Text(f"Detalle Comprobante ID: {comprobante_id}")
        self.detalle_dlg.actions = [ft.TextButton("Cerrar", on_click=lambda _: setattr(self.detalle_dlg, 'open', False) or self.page.update())] # Cierra el diálogo
        self.detalle_dlg.open = True
        self.page.update()


# --- Función para crear la vista completa (usada por el router) ---
def RegistroContableView(page: ft.Page):
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/registro_contable")

    return ft.View(
        "/registro_contable",
        appbar=ft.AppBar(
            title=ft.Text("Registro Contable"),
            bgcolor=ft.colors.SURFACE_VARIANT,
             leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
             RegistroContableViewContent(page)
        ],
        padding=15,
        # floating_action_button=ft.FloatingActionButton( # Opcional: botón para añadir rápido
        #     icon=ft.icons.ADD, on_click=???, tooltip="Nuevo Comprobante Rápido"
        # )
    )
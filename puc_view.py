# views/puc_view.py
import flet as ft
from database.db_manager import obtener_cuentas_puc, agregar_cuenta_puc, eliminar_cuenta_puc, obtener_cuenta_puc_por_codigo
from utils.constants import NATURALEZA_CUENTA_OPCIONES, CLASE_CUENTA_OPCIONES
from utils.helpers import mostrar_snackbar

class PUCViewContent(ft.UserControl):
    """Contenido para la gestión del Plan Único de Cuentas (PUC)."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        # Controles de la UI
        self.filtro_field = ft.TextField(label="Buscar por Código o Nombre", on_change=self.filtrar_cuentas, width=300, dense=True)
        self.tabla_cuentas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Naturaleza")),
                ft.DataColumn(ft.Text("Clase")),
                ft.DataColumn(ft.Text("Acciones")), # Para botones editar/eliminar
            ],
            rows=[],
            column_spacing=20,
            # width=800, # O ajusta según necesites
            expand=True,
        )

        # Controles para agregar/editar cuenta (en un diálogo o panel)
        self.dlg_modal = None # Se definirá en build
        self.dlg_codigo = ft.TextField(label="Código PUC", autofocus=True)
        self.dlg_nombre = ft.TextField(label="Nombre de la Cuenta")
        self.dlg_naturaleza = ft.Dropdown(
            label="Naturaleza",
            options=[ft.dropdown.Option(key=nat) for nat in NATURALEZA_CUENTA_OPCIONES],
        )
        self.dlg_clase = ft.Dropdown(
            label="Clase",
             options=[ft.dropdown.Option(key=cla) for cla in CLASE_CUENTA_OPCIONES],
        )
        self.dlg_grupo_niif = ft.TextField(label="Grupo NIIF (Opcional)")
        self.dlg_error = ft.Text("", color=ft.colors.RED, visible=False)
        self.editing_codigo = None # Guarda el código si estamos editando

    def build(self):
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agregar/Editar Cuenta Contable"),
            content=ft.Column(
                [
                    self.dlg_codigo,
                    self.dlg_nombre,
                    self.dlg_naturaleza,
                    self.dlg_clase,
                    self.dlg_grupo_niif,
                    self.dlg_error,
                ], tight=True, scroll=ft.ScrollMode.ADAPTIVE, height=350 # Ajusta altura si es necesario
            ),
            actions=[
                ft.TextButton("Guardar", on_click=self.guardar_cuenta),
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Contenedor principal
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Catálogo de Cuentas (PUC)", size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.ADD_CIRCLE_OUTLINE,
                            tooltip="Agregar Nueva Cuenta",
                            on_click=self.abrir_dialogo_nueva,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(height=10),
                ft.Row([self.filtro_field]),
                ft.Divider(height=10),
                # Para hacer la tabla scrollable si excede el tamaño
                 ft.Container(
                    content=self.tabla_cuentas,
                    expand=True, # Ocupa el espacio disponible
                    border=ft.border.all(1, ft.colors.OUTLINE), # Borde opcional
                    border_radius=ft.border_radius.all(5)
                 )
                # ft.ListView([self.tabla_cuentas], expand=True, spacing=10)
            ],
            expand=True, # Ocupar todo el espacio vertical disponible
            spacing=10
        )

    def did_mount(self):
        """Se llama después de que el control se añade a la página."""
        self.cargar_cuentas()
        self.page.dialog = self.dlg_modal # Registrar el diálogo en la página

    def cargar_cuentas(self, filtro: Optional[str] = None):
        """Carga las cuentas desde la BD y actualiza la tabla."""
        cuentas_db = obtener_cuentas_puc(filtro=filtro)
        self.tabla_cuentas.rows.clear()
        for cuenta in cuentas_db:
            self.tabla_cuentas.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(cuenta['codigo'])),
                        ft.DataCell(ft.Text(cuenta['nombre'])),
                        ft.DataCell(ft.Text(cuenta['naturaleza'])),
                        ft.DataCell(ft.Text(cuenta['clase'])),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.icons.EDIT, tooltip="Editar", data=cuenta['codigo'], on_click=self.abrir_dialogo_editar),
                                ft.IconButton(ft.icons.DELETE, tooltip="Eliminar", data=cuenta['codigo'], on_click=self.confirmar_eliminar, icon_color=ft.colors.RED),
                            ])
                        ),
                    ]
                )
            )
        self.update() # Actualiza este UserControl

    def filtrar_cuentas(self, e):
        """Llamado cuando cambia el texto del filtro."""
        self.cargar_cuentas(filtro=self.filtro_field.value.strip())

    def limpiar_formulario_dialogo(self):
        self.dlg_codigo.value = ""
        self.dlg_nombre.value = ""
        self.dlg_naturaleza.value = None
        self.dlg_clase.value = None
        self.dlg_grupo_niif.value = ""
        self.dlg_error.value = ""
        self.dlg_error.visible = False
        self.editing_codigo = None
        self.dlg_codigo.disabled = False # Habilitar código por defecto

    def abrir_dialogo_nueva(self, e):
        self.limpiar_formulario_dialogo()
        self.dlg_modal.title = ft.Text("Agregar Nueva Cuenta Contable")
        self.dlg_modal.open = True
        self.page.update()

    def abrir_dialogo_editar(self, e):
        self.limpiar_formulario_dialogo()
        codigo = e.control.data
        cuenta = obtener_cuenta_puc_por_codigo(codigo)
        if cuenta:
            self.editing_codigo = codigo
            self.dlg_modal.title = ft.Text(f"Editar Cuenta: {codigo}")
            self.dlg_codigo.value = cuenta['codigo']
            self.dlg_codigo.disabled = True # No permitir editar el código
            self.dlg_nombre.value = cuenta['nombre']
            self.dlg_naturaleza.value = cuenta['naturaleza']
            self.dlg_clase.value = cuenta['clase']
            self.dlg_grupo_niif.value = cuenta.get('grupo_niif', '') # Usar get por si es None
            self.dlg_modal.open = True
            self.page.update()
        else:
            mostrar_snackbar(self.page, f"No se encontró la cuenta {codigo} para editar.")


    def cerrar_dialogo(self, e):
        self.dlg_modal.open = False
        self.page.update()

    def guardar_cuenta(self, e):
        """Guarda la cuenta nueva o editada."""
        codigo = self.dlg_codigo.value.strip()
        nombre = self.dlg_nombre.value.strip()
        naturaleza = self.dlg_naturaleza.value
        clase = self.dlg_clase.value
        grupo_niif = self.dlg_grupo_niif.value.strip() or None

        # Validaciones básicas
        if not codigo or not nombre or not naturaleza or not clase:
            self.dlg_error.value = "Código, Nombre, Naturaleza y Clase son requeridos."
            self.dlg_error.visible = True
            self.dlg_modal.update() # Actualiza solo el contenido del diálogo
            return

        if self.editing_codigo: # Estamos editando
             # Aquí necesitarías una función db_manager.actualizar_cuenta_puc()
             mostrar_snackbar(self.page, "Funcionalidad de editar aún no implementada en DB.", ft.colors.AMBER)
             # success = db_manager.actualizar_cuenta_puc(self.editing_codigo, nombre, naturaleza, clase, grupo_niif)
             # if success:
             #     mostrar_snackbar(self.page, f"Cuenta {self.editing_codigo} actualizada.", ft.colors.GREEN)
             #     self.cerrar_dialogo(None)
             #     self.cargar_cuentas()
             # else:
             #      self.dlg_error.value = f"Error al actualizar la cuenta {self.editing_codigo}."
             #      self.dlg_error.visible = True
             #      self.dlg_modal.update()
             self.cerrar_dialogo(None) # Cierra por ahora

        else: # Creando nueva cuenta
            success = agregar_cuenta_puc(codigo, nombre, naturaleza, clase, grupo_niif)
            if success:
                mostrar_snackbar(self.page, f"Cuenta {codigo} - {nombre} agregada.", ft.colors.GREEN)
                self.cerrar_dialogo(None)
                self.cargar_cuentas() # Recargar la tabla
            else:
                # El error de duplicado ya se maneja en db_manager, mostremos un mensaje genérico aquí
                self.dlg_error.value = f"Error al agregar la cuenta {codigo}. ¿El código ya existe?"
                self.dlg_error.visible = True
                self.dlg_modal.update()

    def confirmar_eliminar(self, e):
        codigo_a_eliminar = e.control.data

        def handle_delete(ev):
            confirm_dialog.open = False
            self.page.update() # Cierra el dialogo de confirmación
            if ev.control.text == "Sí, Eliminar":
                success = eliminar_cuenta_puc(codigo_a_eliminar)
                if success:
                    mostrar_snackbar(self.page, f"Cuenta {codigo_a_eliminar} eliminada.", ft.colors.GREEN)
                    self.cargar_cuentas()
                else:
                    mostrar_snackbar(self.page, f"Error al eliminar cuenta {codigo_a_eliminar}. Verifique que no esté en uso.")


        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Está seguro de que desea eliminar la cuenta {codigo_a_eliminar}? Esta acción no se puede deshacer y fallará si la cuenta está en uso."),
            actions=[
                ft.TextButton("Sí, Eliminar", on_click=handle_delete),
                ft.TextButton("Cancelar", on_click=lambda _: setattr(confirm_dialog, 'open', False) or self.page.update()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = confirm_dialog # Asigna el diálogo de confirmación
        confirm_dialog.open = True
        self.page.update()

# --- Función para crear la vista completa (usada por el router) ---
def PUCView(page: ft.Page):
     user_id = page.session.get("user_id")
     if not user_id:
         page.go("/login")
         return ft.View("/puc") # Vista vacía temporal

     return ft.View(
        "/puc",
        appbar=ft.AppBar(
            title=ft.Text("Catálogo Contable (PUC)"),
            bgcolor=ft.colors.SURFACE_VARIANT,
             leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            PUCViewContent(page) # Añade el contenido reutilizable
        ],
         padding=15,
    )
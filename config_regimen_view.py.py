# views/config_regimen_view.py
import flet as ft
from database.db_manager import actualizar_regimen_usuario, obtener_datos_usuario
from utils.constants import REGIMEN_TRIBUTARIO_OPCIONES
from utils.helpers import mostrar_snackbar

def ConfigRegimenView(page: ft.Page):
    """Vista para seleccionar/actualizar el régimen tributario."""

    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login") # Si no hay sesión, redirigir a login
        return ft.View("/config_regimen") # Evita error si la redirección tarda


    current_regimen = ft.Text("Cargando régimen actual...")
    regimen_dropdown = ft.Dropdown(
        label="Selecciona tu Régimen Tributario",
        options=[ft.dropdown.Option(key=reg) for reg in REGIMEN_TRIBUTARIO_OPCIONES],
        width=400
    )

    def cargar_regimen_actual():
        user_data = obtener_datos_usuario(user_id)
        if user_data and user_data.get("regimen_tributario"):
            reg = user_data["regimen_tributario"]
            current_regimen.value = f"Régimen Actual: {reg}"
            regimen_dropdown.value = reg # Pre-seleccionar en el dropdown
        else:
             current_regimen.value = "Régimen Actual: No Definido"
             regimen_dropdown.value = "No Definido"
        page.update()

    def guardar_regimen(e):
        nuevo_regimen = regimen_dropdown.value
        if not nuevo_regimen or nuevo_regimen == "No Definido":
            mostrar_snackbar(page, "Debes seleccionar un régimen válido.")
            return

        if user_id:
            success = actualizar_regimen_usuario(user_id, nuevo_regimen)
            if success:
                page.session.set("regimen_tributario", nuevo_regimen) # Actualizar sesión
                mostrar_snackbar(page, f"Régimen actualizado a '{nuevo_regimen}'.", ft.colors.GREEN)
                cargar_regimen_actual() # Recargar para mostrar
                page.go("/dashboard") # Opcional: redirigir después de guardar
            else:
                mostrar_snackbar(page, "Error al guardar el régimen.")
        else:
             mostrar_snackbar(page, "Error: Usuario no identificado.")


    # Cargar el régimen actual al iniciar la vista
    cargar_regimen_actual()

    return ft.View(
        "/config_regimen",
         appbar=ft.AppBar(title=ft.Text("Configuración Fiscal"), bgcolor=ft.colors.SURFACE_VARIANT),
         controls=[
             ft.Column(
                 [
                     ft.Text("Configuración del Régimen Fiscal", size=20, weight=ft.FontWeight.BOLD),
                     ft.Divider(height=15, color=ft.colors.TRANSPARENT),
                     current_regimen,
                     ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                     regimen_dropdown,
                     ft.ElevatedButton("Guardar Régimen", on_click=guardar_regimen),
                     ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                     ft.Text("Seleccionar tu régimen (Común, Simplificado, Especial) es crucial.", italic=True),
                     ft.Text("Esto habilitará funciones como cálculo de IVA y Retenciones si aplican.", italic=True),
                     ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                     ft.TextButton("Volver al Dashboard", icon=ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
                 ],
                 spacing=10,
                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,

             )
         ],
         vertical_alignment=ft.MainAxisAlignment.START,
         horizontal_alignment=ft.CrossAxisAlignment.CENTER,
         padding=20
    )
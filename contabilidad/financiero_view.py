# views/financiero_view.py
import flet as ft

def FinancieroViewContent(page: ft.Page):
    """Contenido placeholder para Estados Financieros."""
    return ft.Column(
        [
            ft.Text("Estados Financieros", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10),
            ft.Text("Módulo en construcción.", italic=True),
            ft.Divider(height=20),
            ft.Text("Aquí se generarán:"),
            ft.Text("- Balance General (Estado de Situación Financiera)"),
            ft.Text("- Estado de Resultados (Integral)"),
            ft.Text("- Estado de Flujos de Efectivo"),
            ft.Text("- Estado de Cambios en el Patrimonio"),
            ft.Divider(height=20),
            ft.Text("Opciones de exportación a PDF/Excel se añadirán aquí.")
        ],
        spacing=10
    )

def FinancieroView(page: ft.Page):
     user_id = page.session.get("user_id")
     if not user_id:
         page.go("/login")
         return ft.View("/financiero")

     return ft.View(
        "/financiero",
        appbar=ft.AppBar(
            title=ft.Text("Estados Financieros"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
             leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            FinancieroViewContent(page)
        ],
        padding=15
    )
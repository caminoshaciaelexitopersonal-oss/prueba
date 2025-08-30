# views/reportes_view.py
import flet as ft

def ReportesViewContent(page: ft.Page):
    """Contenido placeholder para Informes y Reportes."""
    return ft.Column(
        [
            ft.Text("Informes y Reportes", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10),
             ft.Text("Módulo en construcción.", italic=True),
             ft.Divider(height=20),
             ft.Text("Aquí se podrán generar y personalizar reportes como:"),
             ft.Text("- Libro Diario"),
             ft.Text("- Libro Mayor por cuenta"),
             ft.Text("- Balances de prueba"),
             ft.Text("- Informes de Cartera / Proveedores"),
             ft.Text("- Reportes específicos NIIF / DIAN (futuro)"),
             ft.Divider(height=20),
            ft.Text("Opciones de filtros (fechas, cuentas, terceros) y exportación.")

        ],
        spacing=10
    )

def ReportesView(page: ft.Page):
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/reportes")

    return ft.View(
        "/reportes",
        appbar=ft.AppBar(
            title=ft.Text("Informes y Reportes"),
            bgcolor=ft.colors.SURFACE_VARIANT,
             leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            ReportesViewContent(page)
        ],
        padding=15
    )
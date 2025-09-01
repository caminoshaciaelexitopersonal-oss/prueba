# views/auditoria_view.py
import flet as ft

def AuditoriaViewContent(page: ft.Page):
    """Contenido placeholder para Soporte y Auditoría."""
    return ft.Column(
        [
            ft.Text("Soporte y Auditoría", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10),
             ft.Text("Módulo en construcción.", italic=True),
             ft.Divider(height=20),
             ft.Text("Funcionalidades planeadas:"),
             ft.Text("- Historial de cambios críticos (ej: modificación de comprobantes - requiere triggers en DB)."),
             ft.Text("- Bitácora de accesos y acciones importantes (requiere logging detallado)."),
             ft.Text("- Gestión de permisos de usuario (si se implementan roles)."),
        ],
        spacing=10
    )

def AuditoriaView(page: ft.Page):
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/auditoria")

    return ft.View(
        "/auditoria",
        appbar=ft.AppBar(
            title=ft.Text("Auditoría y Soporte"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            AuditoriaViewContent(page)
        ],
        padding=15
    )
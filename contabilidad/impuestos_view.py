# views/impuestos_view.py
import flet as ft

def ImpuestosViewContent(page: ft.Page):
    """Contenido placeholder para IVA y Retenciones."""
    regimen = page.session.get("regimen_tributario", "No Definido")

    content_controls = [
        ft.Text("Gestión de IVA y Retenciones", size=20, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10),
        ft.Text(f"Régimen detectado: {regimen}", italic=True),
         ft.Divider(height=10),
    ]

    # Mostrar contenido diferente según el régimen (ejemplo básico)
    if regimen == "Común":
        content_controls.extend([
             ft.Text("Funcionalidades para Régimen Común (en desarrollo):", weight=ft.FontWeight.W_500),
             ft.Text("- Cálculo de IVA generado y descontable."),
             ft.Text("- Gestión de compras y ventas gravadas/excluidas/exentas."),
             ft.Text("- Cálculo de retenciones (Fuente, ICA, etc.)."),
             ft.Text("- Generación de reportes para declaraciones."),
         ])
    elif regimen == "Simplificado": # Ahora "No responsables de IVA"
        content_controls.extend([
            ft.Text("Régimen Simplificado (No responsable de IVA):", weight=ft.FontWeight.W_500),
            ft.Text("- Generalmente no requiere gestión detallada de IVA."),
            ft.Text("- Podría aplicar retenciones si actúa como agente retenedor (casos específicos)."),
            ft.Text("- Funcionalidad limitada o no aplicable para este módulo."),
        ])
    elif regimen == "Especial":
        content_controls.extend([
            ft.Text("Régimen Tributario Especial (ESAL, etc.):", weight=ft.FontWeight.W_500),
            ft.Text("- Requiere configuración específica según normatividad."),
            ft.Text("- Gestión de IVA y Retenciones adaptada (en desarrollo)."),
        ])
    else:
        content_controls.append(ft.Text("Seleccione un régimen tributario en la configuración para ver las opciones aplicables.", color=ft.Colors.ORANGE))

    content_controls.append(ft.Divider(height=20))
    content_controls.append(ft.Text("Módulo en construcción.", italic=True))

    return ft.Column(content_controls, spacing=10)


def ImpuestosView(page: ft.Page):
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.View("/impuestos")

    # Opcional: Podrías incluso ocultar esta vista si el régimen no la requiere
    # regimen = page.session.get("regimen_tributario")
    # if regimen == "Simplificado": # Ejemplo
    #      page.go("/dashboard") # O mostrar un mensaje simple
    #      return ft.View(...)

    return ft.View(
        "/impuestos",
        appbar=ft.AppBar(
            title=ft.Text("IVA y Retenciones"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
             leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"), tooltip="Volver al Dashboard")
        ),
        controls=[
            ImpuestosViewContent(page)
        ],
        padding=15
    )
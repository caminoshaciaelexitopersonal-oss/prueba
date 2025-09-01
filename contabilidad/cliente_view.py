# views/cliente_view.py
import flet as ft

def ClienteView(page: ft.Page):
    """
    Placeholder view for Client Management.
    """
    return ft.View(
        "/clientes",
        appbar=ft.AppBar(
            title=ft.Text("Gestión de Clientes"),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: page.go("/dashboard"))
        ),
        controls=[
            ft.Text("Módulo de Clientes en construcción.", size=20)
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

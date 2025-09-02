# views/login_view.py
import flet as ft
from database.db_manager import verificar_usuario
from contabilidad.auth import verify_password
from utils.helpers import mostrar_snackbar

def LoginView(page: ft.Page):
    """Crea la vista de inicio de sesión."""

    username_field = ft.TextField(label="Usuario", width=300)
    password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
    error_text = ft.Text(value="", color=ft.Colors.RED, visible=False)

    def handle_login(e):
        username = username_field.value.strip()
        password = password_field.value

        error_text.visible = False

        if not username or not password:
            mostrar_snackbar(page, "Usuario y contraseña son requeridos.")
            error_text.value = "Usuario y contraseña son requeridos."
            error_text.visible = True
            page.update()
            return

        try:
            user_data = verificar_usuario(username)

            if user_data and verify_password(user_data['password_hash'], password):
                page.session.set("user_id", user_data['id'])
                page.session.set("username", user_data['username'])
                mostrar_snackbar(page, f"Bienvenido, {username}!", ft.Colors.GREEN)
                page.go("/dashboard")
            else:
                mostrar_snackbar(page, "Usuario o contraseña incorrectos.")
                error_text.value = "Usuario o contraseña incorrectos."
                error_text.visible = True
                page.update()

        except Exception as ex:
            mostrar_snackbar(page, f"Error inesperado al iniciar sesión: {ex}")
            error_text.value = f"Error inesperado: {ex}"
            error_text.visible = True
            page.update()

    def go_to_register(e):
        page.go("/register")

    return ft.View(
        "/login",
        controls=[
            ft.Column(
                [
                    ft.Text("Inicio de Sesión", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    username_field,
                    password_field,
                    error_text,
                    ft.ElevatedButton("Iniciar Sesión", on_click=handle_login, width=300),
                    ft.TextButton("¿No tienes cuenta? Regístrate", on_click=go_to_register),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

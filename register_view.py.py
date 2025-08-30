# views/register_view.py
import flet as ft
from database.db_manager import crear_usuario
from logic.auth import hash_password
from utils.helpers import mostrar_snackbar
from cryptography.fernet import Fernet
import os

def RegisterView(page: ft.Page):
    """Crea la vista de registro de usuario."""

    username_field = ft.TextField(label="Nuevo Usuario", width=300)
    password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
    confirm_password_field = ft.TextField(label="Confirmar Contraseña", password=True, can_reveal_password=True, width=300)
    nombre_empresa_field = ft.TextField(label="Nombre Empresa (Opcional)", width=300)
    nit_field = ft.TextField(label="NIT (Opcional)", width=300)
    error_text = ft.Text(value="", color=ft.colors.RED, visible=False)

    def handle_register(e):
        username = username_field.value.strip()
        password = password_field.value
        confirm_password = confirm_password_field.value
        nombre_empresa = nombre_empresa_field.value.strip() or None
        nit = nit_field.value.strip() or None

        error_text.visible = False # Resetear errores

        if not username or not password or not confirm_password:
            mostrar_snackbar(page, "Usuario y ambas contraseñas son requeridos.")
            error_text.value = "Usuario y ambas contraseñas son requeridos."
            error_text.visible = True
            page.update()
            return

        if password != confirm_password:
            mostrar_snackbar(page, "Las contraseñas no coinciden.")
            error_text.value = "Las contraseñas no coinciden."
            error_text.visible = True
            page.update()
            return

        if len(password) < 6: # Validación simple de longitud
             mostrar_snackbar(page, "La contraseña debe tener al menos 6 caracteres.")
             error_text.value = "La contraseña debe tener al menos 6 caracteres."
             error_text.visible = True
             page.update()
             return

        try:
            # Encriptar el nombre de usuario
            key = Fernet.generate_key().decode()
            cipher = Fernet(key)
            encrypted_username = cipher.encrypt(username.encode()).decode()

            hashed_pass = hash_password(password)
            user_id = crear_usuario(encrypted_username, hashed_pass, nombre_empresa, nit, key)

            if user_id:
                mostrar_snackbar(page, f"Usuario '{username}' registrado exitosamente. Inicia sesión.", ft.colors.GREEN)
                page.go("/login") # Redirigir a login
            else:
                mostrar_snackbar(page, f"El nombre de usuario '{username}' ya existe.")
                error_text.value = f"El nombre de usuario '{username}' ya existe."
                error_text.visible = True
                page.update()
        except ValueError as ve: # Capturar error de hashing
            mostrar_snackbar(page, f"Error al registrar: {ve}")
            error_text.value = f"Error: {ve}"
            error_text.visible = True
            page.update()
        except Exception as ex:
            mostrar_snackbar(page, f"Error inesperado al registrar: {ex}")
            error_text.value = f"Error inesperado: {ex}"
            error_text.visible = True
            page.update()


    def go_to_login(e):
        page.go("/login")

    return ft.View(
        "/register",
        controls=[
            ft.Column(
                [
                    ft.Text("Registro de Nuevo Usuario", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                    username_field,
                    password_field,
                    confirm_password_field,
                    nombre_empresa_field,
                    nit_field,
                    error_text,
                    ft.ElevatedButton("Registrar", on_click=handle_register, width=300),
                    ft.TextButton("¿Ya tienes cuenta? Inicia Sesión", on_click=go_to_login),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.ADAPTIVE, # Para permitir scroll si hay muchos campos
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
# utils/helpers.py
import flet as ft

def mostrar_snackbar(page: ft.Page, mensaje: str, color: str = ft.colors.RED):
    """Muestra un mensaje temporal en la parte inferior."""
    page.show_snack_bar(
        ft.SnackBar(ft.Text(mensaje), bgcolor=color)
    )

def format_currency(value: float) -> str:
    """Formatea un número como moneda COP (simplificado)."""
    if value is None:
        return "$ 0"
    try:
        # Format with thousands separators (,) and no decimals for simplicity here
        # A library like 'babel' would be better for locale-aware formatting
        return f"$ {int(value):,}".replace(",",".") # Simple placeholder format
    except (ValueError, TypeError):
        return "$ 0"

# Puedes añadir más funciones de utilidad aquí
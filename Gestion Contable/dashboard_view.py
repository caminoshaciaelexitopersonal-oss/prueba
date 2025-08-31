# views/dashboard_view.py
import flet as ft
from database.db_manager import obtener_datos_usuario

# --- Importar las demás vistas que se mostrarán en el dashboard ---
from views.puc_view import PUCViewContent # Cambiar nombre para evitar colisión
from views.registro_contable_view import RegistroContableViewContent
from views.financiero_view import FinancieroViewContent
from views.impuestos_view import ImpuestosViewContent
from views.reportes_view import ReportesViewContent
from views.auditoria_view import AuditoriaViewContent
from views.config_regimen_view import ConfigRegimenView # Para acceso rápido a config


# --- Definición de un control reutilizable para las secciones del dashboard ---
class ModuleCard(ft.UserControl):
    def __init__(self, title, description, icon, route_name, page):
        super().__init__()
        self.title = title
        self.description = description
        self.icon = icon
        self.route_name = route_name
        self.page = page

    def go_to_module(self, e):
        self.page.go(self.route_name)

    def build(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(self.icon),
                            title=ft.Text(self.title, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(self.description),
                        ),
                        ft.Row(
                            [ft.TextButton("Acceder", on_click=self.go_to_module)],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ]
                ),
                width=280,
                padding=10,
            )
        )


def DashboardView(page: ft.Page):
    """Vista principal del Dashboard."""
    user_id = page.session.get("user_id")
    username = page.session.get("username", "Invitado")
    regimen = page.session.get("regimen_tributario", "No Definido")

    if not user_id:
        page.go("/login")
        return ft.View("/dashboard")

    # --- Mensaje de bienvenida y Régimen ---
    welcome_text = ft.Text(f"Bienvenido/a, {username}", size=20, weight=ft.FontWeight.BOLD)
    regimen_text = ft.Text(f"Régimen Tributario: {regimen}", italic=True)
    config_regimen_button = ft.TextButton("Configurar Régimen", icon=ft.icons.SETTINGS, on_click=lambda _: page.go("/config_regimen"))

    # --- Contenido Principal: Tarjetas de Módulos ---
    modules_grid = ft.GridView(
        expand=1,
        runs_count=5, # Ajusta cuántas tarjetas por fila (aprox)
        max_extent=300, # Ancho máximo de cada tarjeta
        child_aspect_ratio=1.5, # Relación ancho/alto
        spacing=10,
        run_spacing=10,
        padding=20,
    )

    # Definir los módulos disponibles
modulos = [
    {"title": "Facturación", "desc": "Crear y gestionar facturas de venta", "icon": ft.icons.REQUEST_QUOTE, "route": "/facturacion"},
    {"title": "Compras", "desc": "Registrar facturas de proveedores", "icon": ft.icons.SHOPPING_CART, "route": "/compras"},
    {"title": "Conciliación Bancaria", "desc": "Conciliar extractos con libros", "icon": ft.icons.ACCOUNT_BALANCE, "route": "/conciliacion"},
    {"title": "Catálogo Contable", "desc": "Gestionar Plan de Cuentas (PUC)", "icon": ft.icons.ACCOUNT_BALANCE_WALLET, "route": "/puc"},
    {"title": "Registro Contable", "desc": "Ingresar comprobantes y movimientos", "icon": ft.icons.POST_ADD, "route": "/registro_contable"},
    {"title": "IVA y Retenciones", "desc": "Gestión de impuestos (Según Régimen)", "icon": ft.icons.RECEIPT_LONG, "route": "/impuestos"},
    {"title": "Estados Financieros", "desc": "Balance, Resultados, Flujo Caja", "icon": ft.icons.ASSESSMENT, "route": "/financiero"},
    {"title": "Análisis Financiero", "desc": "Calcular Ratios e Indicadores", "icon": ft.icons.INSIGHTS, "route": "/analisis"},  # Placeholder route
    {"title": "Informes y Reportes", "desc": "Generar reportes personalizados", "icon": ft.icons.PIE_CHART, "route": "/reportes"},
    {"title": "Auditoría y Soporte", "desc": "Historial de cambios y Logs", "icon": ft.icons.HISTORY_EDU, "route": "/auditoria"},
    {"title": "Asistente IA", "desc": "Chatea con la IA para obtener ayuda", "icon": ft.icons.ASSISTANT, "route": "/agente"},
    # Añadir Nómina aquí si se implementa
]
    # --- Filtrar módulos según régimen (EJEMPLO BÁSICO) ---
    modulos_visibles = []
    for mod in modulos:
        if mod["route"] == "/impuestos":
             # Mostrar solo si es Régimen Común (simplificación extrema)
             if regimen == "Común":
                 modulos_visibles.append(mod)
             # En un caso real, la lógica sería más compleja
        else:
            modulos_visibles.append(mod)


    # Crear las tarjetas
    for mod in modulos_visibles:
         modules_grid.controls.append(
             ModuleCard(mod["title"], mod["desc"], mod["icon"], mod["route"], page)
         )


    def handle_logout(e):
        # Limpiar la sesión
        page.session.clear()
        page.go("/login")


    return ft.View(
        "/dashboard",
        appbar=ft.AppBar(
            title=ft.Text("Sistema Contable NIIF - Colombia"),
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(ft.icons.LOGOUT, tooltip="Cerrar Sesión", on_click=handle_logout)
            ]
        ),
        controls=[
             ft.Column(
                [
                    ft.Row([welcome_text, ft.Container(width=20), regimen_text, config_regimen_button], spacing=15),
                    ft.Divider(height=20),
                    ft.Text("Módulos Disponibles:", size=16, weight=ft.FontWeight.W_500),
                    modules_grid, # La rejilla con las tarjetas
                 ],
                expand=True,
             )
        ],
        padding=15
    )

# NOTA: Las otras vistas (PUC, Registro, etc.) ahora devolverán solo su *contenido*
# para ser potencialmente integradas en un layout principal si se desea más adelante,
# o para ser llamadas como vistas completas desde el routing.
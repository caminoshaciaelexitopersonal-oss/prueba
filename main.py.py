# main.py
import flet as ft
import logging
from cliente_view import ClienteView

# --- Configuración de Logging ---
# Puedes configurarlo más detalladamente si necesitas (archivo, rotación, etc.)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Importar Vistas ---
# Es crucial importar las funciones de vista *después* de la configuración de logging si usan logger
from login_view import LoginView
from register_view import RegisterView
from views.config_regimen_view import ConfigRegimenView
from views.dashboard_view import DashboardView
from views.puc_view import PUCView
from views.registro_contable_view import RegistroContableView
from views.financiero_view import FinancieroView # Placeholder
from views.impuestos_view import ImpuestosView # Placeholder
from views.reportes_view import ReportesView # Placeholder
from views.auditoria_view import AuditoriaView # Placeholder
# Importa otras vistas aquí (Análisis, Nómina, etc.) cuando las crees

# --- Importar Inicializador de BD ---
from database.db_manager import init_db # , popular_puc_basico si creas esa función


def main(page: ft.Page):
    """Función principal de la aplicación Flet."""

    page.title = "Sistema Contable NIIF - Colombia"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.theme_mode = ft.ThemeMode.SYSTEM # O LIGHT, DARK
    # page.window_width = 1000 # Opcional: definir tamaño inicial
    # page.window_height = 700

    logger.info("Iniciando aplicación Flet.")

    # --- Inicializar Base de Datos ---
    try:
        logger.info("Inicializando bases de datos...")
        init_db()
        # Opcional: poblar con PUC básico si está vacío la primera vez
        # from database.db_manager import agregar_cuenta_puc, obtener_cuentas_puc
        # from utils.constants import PUC_BASICO_COLOMBIA
        # if not obtener_cuentas_puc(limit=1): # Verifica si hay al menos una cuenta
        #     logger.info("Poblando PUC básico...")
        #     for codigo, data in PUC_BASICO_COLOMBIA.items():
        #          agregar_cuenta_puc(codigo, data['nombre'], data['naturaleza'], data['clase'])
        logger.info("Bases de datos listas.")
    except Exception as e:
        logger.critical(f"Error CRÍTICO al inicializar la base de datos: {e}")
        # Mostrar error crítico en la UI y detener?
        page.add(ft.Text(f"Error fatal al iniciar la BD: {e}", color=ft.colors.RED))
        return # Detener la carga de la app

    # --- Definición de Rutas y Vistas ---
    app_routes = {
        "/login": LoginView(page),
        "/register": RegisterView(page),
        "/dashboard": DashboardView(page),
        "/config_regimen": ConfigRegimenView(page),
        "/puc": PUCView(page),
        "/registro_contable": RegistroContableView(page),
        "/financiero": FinancieroView(page),
        "/impuestos": ImpuestosView(page),
        "/reportes": ReportesView(page),
        "/auditoria": AuditoriaView(page),
        "/clientes": ClienteView(page),
         # "/analisis": AnalisisView(page), # Añadir ruta para análisis
        # Añade más rutas aquí
    }

    def route_change(route):
        """Maneja el cambio de ruta."""
        logger.info(f"Navegando a la ruta: {page.route}")
        page.views.clear()

        # --- Lógica de Autenticación y Rutas Protegidas ---
        user_id = page.session.get("user_id")
        is_public_route = page.route in ["/login", "/register"]

        if not user_id and not is_public_route:
            # Si no está logueado y la ruta no es pública, redirige a login
            logger.warning("Acceso no autenticado a ruta protegida. Redirigiendo a /login.")
            page.go("/login")
            # Es importante añadir la vista de login aquí también para que se muestre
            page.views.append(app_routes["/login"])
        elif user_id and is_public_route:
             # Si está logueado e intenta ir a login/register, redirige a dashboard
             logger.info("Usuario autenticado intentando acceder a ruta pública. Redirigiendo a /dashboard.")
             page.go("/dashboard")
             page.views.append(app_routes["/dashboard"])
        else:
            # Si está logueado y la ruta es válida, o si no está logueado y es pública
            view = app_routes.get(page.route)
            if view:
                 page.views.append(view)
                 # Opcional: Verificar régimen para ciertas vistas
                 # regimen = page.session.get("regimen_tributario")
                 # if page.route == "/impuestos" and regimen != "Común":
                 #     # Podrías mostrar una vista diferente o redirigir
                 #     logger.info("Acceso a /impuestos denegado/modificado por régimen.")
                 #     # page.views.append(VistaAlternativaImpuestos(page)) # O redirigir
            else:
                # Ruta no encontrada, ir a dashboard si está logueado, si no a login
                logger.error(f"Ruta desconocida: {page.route}. Redirigiendo...")
                default_route = "/dashboard" if user_id else "/login"
                page.go(default_route)
                page.views.append(app_routes[default_route])


        page.update()


    def view_pop(view):
        """Se ejecuta cuando el usuario navega hacia atrás."""
        logger.debug(f"View pop: {view.view.route}")
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route) # Actualiza la ruta en la URL/historial


    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # --- Estado Inicial ---
    # Determinar la ruta inicial basada en si hay una sesión activa
    initial_route = "/dashboard" if page.session.get("user_id") else "/login"
    logger.info(f"Ruta inicial determinada: {initial_route}")
    page.go(initial_route)


# --- Punto de Entrada ---
if __name__ == "__main__":
    # def main(page: ft.Page):
    #     page.title = "SARITA"
    #     def route(route):
    #         page.views.clear()
    #         page.views.append(
    #             ft.View(
                #     route,
                #     [
                #         ft.AppBar(title=ft.Text(f"Sarita App - {route}")),
                #         ft.ElevatedButton(text="Go Home", on_click=lambda _: page.go("/")),
                #     ],
            #     )
        # )
        if page.route == "/":
            page.views.clear()
            page.views.append(
                dashboard_view.DashboardView(page)
            )
        if page.route == "/clientes":
            page.views.clear()
            page.views.append(
                cliente.cliente_view.ClienteView(page)
            )
        page.update()

    #     page.on_route_change = route
    #     page.go(page.route)

    # ft.app(target=main) # Para ejecutar como app de escritorio/web normal
    ft.app(target=main, view=ft.WEB_BROWSER) # Para forzar vista web browser
    # ft.app(target=main, assets_dir="assets") # Si tienes assets (imágenes, etc.)
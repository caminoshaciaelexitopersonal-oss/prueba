# gestion_operativa/Nomina/main.py
import flet as ft
import sys
import os
import logging

# --- Add project root to sys.path ---
# This allows finding the root 'gestion_operativa' package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from gestion_operativa.Nomina.views.main_view import MainView
from gestion_operativa.Nomina.database import init_db

# --- Basic Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    """Main function for the standalone Payroll Flet app."""

    page.title = "Sistema de Nómina Independiente"
    logger.info("Initializing standalone payroll application.")

    # --- Initialize Database ---
    try:
        # This module has its own database logic
        init_db()
        logger.info("Payroll database initialized successfully.")
    except Exception as e:
        logger.critical(f"Critical error initializing database: {e}")
        page.add(ft.Text(f"Fatal error initializing DB: {e}", color=ft.Colors.RED))
        return

    # The MainView is a UserControl, so it needs to be placed in a View or directly on the page.
    main_view_control = MainView()
    page.add(main_view_control)
    page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)

# activos_fijos/main.py
import flet as ft
import sys
import os
import logging

# --- Add project root to sys.path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from activos_fijos.view import ActivosFijosView
from database.db_manager import init_db

# --- Basic Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    """Main function for the standalone fixed assets Flet app."""

    page.title = "Sistema de Activos Fijos Independiente"
    logger.info("Initializing standalone fixed assets application.")

    # --- Initialize Database ---
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Critical error initializing database: {e}")
        page.add(ft.Text(f"Fatal error initializing DB: {e}", color=ft.Colors.RED))
        return

    # The ActivosFijosView is a full ft.View, so it can be added directly.
    fixed_assets_view = ActivosFijosView(page)

    page.views.append(fixed_assets_view)
    page.go("/activos_fijos")
    page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)

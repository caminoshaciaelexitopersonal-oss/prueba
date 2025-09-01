# analisis_financiero/main.py
import flet as ft
import sys
import os
import logging

# --- Add project root to sys.path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analisis_financiero.view import AnalisisFinancieroView
from database.db_manager import init_db

# --- Basic Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    """Main function for the standalone financial analysis Flet app."""

    page.title = "Sistema de Análisis Financiero Independiente"
    logger.info("Initializing standalone financial analysis application.")

    # --- Initialize Database ---
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Critical error initializing database: {e}")
        page.add(ft.Text(f"Fatal error initializing DB: {e}", color=ft.Colors.RED))
        return

    # The AnalisisFinancieroView is a full ft.View.
    financial_analysis_view = AnalisisFinancieroView(page)

    page.views.append(financial_analysis_view)
    page.go("/analisis_financiero")
    page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)

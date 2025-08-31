import flet as ft
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import all MVC components
from database import init_db
from models.content_model import ContentModel
from views.content_manager_view import ContentManagerView
from controllers.content_manager_controller import ContentManagerController

from models.sales_model import SalesModel
from views.sales_manager_view import SalesManagerView
from controllers.sales_manager_controller import SalesManagerController

from models.messaging_model import MessagingModel
from views.messaging_view import MessagingView
from controllers.messaging_controller import MessagingController

from models.calendar_model import CalendarModel
from views.calendar_view import CalendarView
from controllers.calendar_controller import CalendarController

from models.invoicing_model import InvoicingModel
from views.invoicing_view import InvoicingView
from controllers.invoicing_controller import InvoicingController


async def main(page: ft.Page):
    # --- Database Initialization ---
    init_db()

    # --- Page Configuration ---
    page.title = "Sistema Comercial IA"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 800

    # --- MVC Setup ---
    # Models
    content_model = ContentModel()
    invoicing_model = InvoicingModel()
    sales_model = SalesModel(invoicing_model=invoicing_model)
    messaging_model = MessagingModel()
    calendar_model = CalendarModel()

    # Views
    content_view = ContentManagerView()
    sales_view = SalesManagerView()
    messaging_view = MessagingView()
    calendar_view = CalendarView()
    invoicing_view = InvoicingView()

    # Controllers
    calendar_controller = CalendarController(model=calendar_model, view=calendar_view)
    ContentManagerController(
        model=content_model,
        view=content_view,
        calendar_model=calendar_model,
        calendar_controller=calendar_controller
    )
    SalesManagerController(model=sales_model, view=sales_view, page=page)
    MessagingController(msg_model=messaging_model, sales_model=sales_model, view=messaging_view, page=page)
    InvoicingController(invoicing_model=invoicing_model, sales_model=sales_model, view=invoicing_view)

    # --- Navigation Logic ---
    def navigate(e):
        selected_index = e.control.selected_index
        content_view.visible = (selected_index == 0)
        sales_view.visible = (selected_index == 1)
        messaging_view.visible = (selected_index == 2)
        calendar_view.visible = (selected_index == 3)
        invoicing_view.visible = (selected_index == 4)
        page.update()

    # --- UI Layout ---
    navigation_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.TEXT_SNIPPET_OUTLINED, selected_icon=ft.icons.TEXT_SNIPPET, label="Contenido"),
            ft.NavigationRailDestination(icon=ft.icons.PEOPLE_OUTLINE, selected_icon=ft.icons.PEOPLE, label="Ventas"),
            ft.NavigationRailDestination(icon=ft.icons.SEND_OUTLINED, selected_icon=ft.icons.SEND, label="Mensajería"),
            ft.NavigationRailDestination(icon=ft.icons.CALENDAR_MONTH_OUTLINED, selected_icon=ft.icons.CALENDAR_MONTH, label="Calendario"),
            ft.NavigationRailDestination(icon=ft.icons.RECEIPT_LONG_OUTLINED, selected_icon=ft.icons.RECEIPT_LONG, label="Facturación"),
        ],
        on_change=navigate,
    )

    # Set initial visibility
    sales_view.visible = False
    messaging_view.visible = False
    calendar_view.visible = False
    invoicing_view.visible = False

    content_container = ft.Container(
        content=ft.Column(controls=[content_view, sales_view, messaging_view, calendar_view, invoicing_view], expand=True),
        padding=ft.padding.all(20),
        expand=True
    )

    main_layout = ft.Row(
        controls=[navigation_rail, ft.VerticalDivider(width=1), content_container],
        expand=True,
    )

    page.add(main_layout)

    # API key check
    if not os.getenv("OPENAI_API_KEY"):
        page.snack_bar = ft.SnackBar(content=ft.Text("ADVERTENCIA: OPENAI_API_KEY no configurada."), action="Cerrar")
        page.snack_bar.open = True
        await page.update_async()
    else:
        await page.update_async()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, assets_dir="assets")

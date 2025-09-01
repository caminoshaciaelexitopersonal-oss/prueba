import flet as ft
import datetime
from fpdf import FPDF
import os

from models.invoicing_model import InvoicingModel, Order
from models.sales_model import SalesModel
from views.invoicing_view import InvoicingView

class InvoicingController:
    def __init__(self, invoicing_model: InvoicingModel, sales_model: SalesModel, view: InvoicingView):
        self.invoicing_model = invoicing_model
        self.sales_model = sales_model
        self.view = view
        # This allows other controllers to call this method
        self.view.update_orders_list = self.update_orders_list

    def update_orders_list(self, e=None):
        """Fetches completed orders and populates the table."""
        if not self.view.page:
            return # View is not ready yet

        self.view.orders_table.rows.clear()
        completed_orders = self.invoicing_model.get_completed_orders()

        for order in completed_orders:
            customer = self.sales_model.get_customer_by_id(order.customer_id)
            customer_name = customer.name if customer else "N/A"

            self.view.orders_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(order.id[:8] + "...")),
                        ft.DataCell(ft.Text(customer_name)),
                        ft.DataCell(ft.Text(f"${order.total_amount:.2f}")),
                        ft.DataCell(
                            ft.ElevatedButton(
                                "Generar Factura",
                                icon=ft.icons.RECEIPT_LONG,
                                data=order,
                                on_click=self.generate_invoice_clicked
                            )
                        ),
                    ]
                )
            )
        self.view.update()

    def _create_pdf_invoice(self, order: Order, customer_name: str, cufe: str) -> str:
        """Generates a PDF invoice for the given order and returns the file path."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)

        pdf.cell(0, 10, "Factura de Venta (Resumen)", 0, 1, "C")
        pdf.ln(10)

        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1)
        pdf.cell(0, 10, f"Cliente: {customer_name}", 0, 1)
        pdf.cell(0, 10, f"ID de Pedido: {order.id}", 0, 1)
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(100, 10, "Producto", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(30, 10, "Precio", 1)
        pdf.cell(30, 10, "Total", 1)
        pdf.ln()

        pdf.set_font("Helvetica", "", 12)
        for item in order.items:
            pdf.cell(100, 10, item.product.name, 1)
            pdf.cell(30, 10, str(item.quantity), 1, 0, "C")
            pdf.cell(30, 10, f"${item.product.price:.2f}", 1, 0, "R")
            pdf.cell(30, 10, f"${item.total:.2f}", 1, 0, "R")
            pdf.ln()

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(160, 10, "Total Factura:", 1, 0, "R")
        pdf.cell(30, 10, f"${order.total_amount:.2f}", 1, 0, "R")
        pdf.ln(20)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 5, f"CUFE (Simulado): {cufe}\n\nEste es un resumen de compra y no un documento fiscal válido bajo la legislación colombiana. La factura electrónica legal será enviada por separado.")

        if not os.path.exists("invoices"):
            os.makedirs("invoices")

        file_path = f"invoices/factura_{order.id[:8]}.pdf"
        pdf.output(file_path)
        return file_path

    async def generate_invoice_clicked(self, e):
        """Full invoice generation and simulation logic."""
        order: Order = e.control.data
        customer = self.sales_model.get_customer_by_id(order.customer_id)
        if not customer:
            return

        cufe = self.invoicing_model.simulate_dian_submission(order)
        pdf_path = self._create_pdf_invoice(order, customer.name, cufe)

        print("="*50)
        print("SIMULANDO ENVÍO DE CORREO DE CONFIRMACIÓN")
        print(f"Destinatario: {customer.email}")
        print(f"Asunto: Resumen de su compra - Pedido {order.id[:8]}")
        print(f"Adjunto: {pdf_path}")
        print("="*50)

        self.update_orders_list()
        self.view.page.snack_bar = ft.SnackBar(ft.Text(f"Factura para pedido {order.id[:8]} generada y procesada (simulación)."))
        self.view.page.snack_bar.open = True
        await self.view.page.update_async()

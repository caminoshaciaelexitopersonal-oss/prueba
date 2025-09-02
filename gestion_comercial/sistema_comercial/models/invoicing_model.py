import uuid
from typing import List, Optional
from sqlalchemy import select, update

from database import Session, products_table, orders_table, line_items_table
from models.data_models import Product, Order, LineItem

class InvoicingModel:
    def get_all_products(self) -> List[Product]:
        with Session() as session:
            stmt = select(products_table)
            results = session.execute(stmt).all()
            return [Product(**row._asdict()) for row in results]

    def get_product_by_name(self, name: str) -> Optional[Product]:
        with Session() as session:
            stmt = select(products_table).where(products_table.c.name.ilike(f"%{name}%"))
            result = session.execute(stmt).first()
            return Product(**result._asdict()) if result else None

    def get_completed_orders_with_details(self) -> List[dict]:
        """
        Fetches completed orders and joins with customer data for display.
        Returns a list of dictionaries for easier use in the controller.
        """
        from database import customers_table
        with Session() as session:
            stmt = (
                select(orders_table.c.id, orders_table.c.total_amount, customers_table.c.name.label("customer_name"))
                .join(customers_table, orders_table.c.customer_id == customers_table.c.id)
                .where(orders_table.c.status == 'completed')
            )
            results = session.execute(stmt).all()
            return [row._asdict() for row in results]

    def get_full_order_details(self, order_id: str) -> Optional[Order]:
        """Fetches a full order with its line items."""
        with Session() as session:
            order_stmt = select(orders_table).where(orders_table.c.id == order_id)
            order_result = session.execute(order_stmt).first()
            if not order_result:
                return None

            items_stmt = (
                select(line_items_table, products_table.c.name, products_table.c.price)
                .join(products_table, line_items_table.c.product_id == products_table.c.id)
                .where(line_items_table.c.order_id == order_id)
            )
            items_results = session.execute(items_stmt).all()

            line_items = []
            for item_row in items_results:
                product = Product(id=item_row.product_id, name=item_row.name, price=item_row.price)
                line_items.append(LineItem(product=product, quantity=item_row.quantity))

            order_data = order_result._asdict()
            order_data['items'] = line_items
            return Order(**order_data)

    def simulate_dian_submission(self, order_id: str) -> str:
        with Session() as session:
            stmt = update(orders_table).where(orders_table.c.id == order_id).values(status="invoiced")
            session.execute(stmt)
            session.commit()

        print("="*50)
        print(f"SIMULANDO ENVÍO A LA DIAN PARA LA ORDEN {order_id}")
        cufe = f"simulated-cufe-{uuid.uuid4()}"
        print(f"CUFE RECIBIDO: {cufe}")
        print("="*50)
        return cufe

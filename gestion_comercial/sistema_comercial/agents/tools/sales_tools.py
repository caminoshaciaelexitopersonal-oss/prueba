# gestion_comercial/sistema_comercial/agents/tools/sales_tools.py
import uuid
from sqlalchemy import select, insert, update, sum as sql_sum
from langchain_core.tools import tool

# Importar dependencias de la base de datos del módulo comercial
from gestion_comercial.sistema_comercial.database import Session, customers_table, products_table, orders_table, line_items_table

@tool
def search_customer(name: str) -> str:
    """Busca un cliente por su nombre y devuelve sus detalles y ID."""
    with Session() as session:
        stmt = select(customers_table).where(customers_table.c.name.ilike(f"%{name}%"))
        results = session.execute(stmt).all()
        if not results: return "Cliente no encontrado."
        return "\n".join([f"Nombre: {r.name}, ID: {r.id}" for r in results])

@tool
def create_order(customer_id: str) -> str:
    """Crea un nuevo pedido vacío para un cliente y devuelve el nuevo ID del pedido."""
    with Session() as session:
        cust_stmt = select(customers_table).where(customers_table.c.id == customer_id)
        if not session.execute(cust_stmt).first():
            return "ID de cliente no encontrado."

        new_order_id = str(uuid.uuid4())
        stmt = insert(orders_table).values(id=new_order_id, customer_id=customer_id, total_amount=0, status="pending")
        session.execute(stmt)
        session.commit()
        return f"Nuevo pedido creado con ID: {new_order_id}. Por favor, usa este ID para añadir productos."

@tool
def list_products() -> str:
    """Lista todos los productos disponibles y sus precios."""
    with Session() as session:
        stmt = select(products_table)
        results = session.execute(stmt).all()
        if not results: return "No hay productos disponibles."
        return "\n".join([f"Producto: {p.name}, Precio: ${p.price:.2f}, ID: {p.id}" for p in results])

@tool
def add_product_to_order(order_id: str, product_name: str, quantity: int) -> str:
    """Añade una cantidad específica de un producto a un pedido dado."""
    with Session() as session:
        prod_stmt = select(products_table).where(products_table.c.name.ilike(f"%{product_name}%"))
        product = session.execute(prod_stmt).first()
        if not product: return f"Producto '{product_name}' no encontrado."

        line_item_total = product.price * quantity
        li_stmt = insert(line_items_table).values(
            order_id=order_id, product_id=product.id, quantity=quantity, total=line_item_total
        )
        session.execute(li_stmt)

        total_stmt = select(sql_sum(line_items_table.c.total)).where(line_items_table.c.order_id == order_id)
        new_total = session.execute(total_stmt).scalar_one() or 0
        ord_update_stmt = update(orders_table).where(orders_table.c.id == order_id).values(total_amount=new_total)
        session.execute(ord_update_stmt)

        session.commit()
        return f"Añadido {quantity} x {product.name} al pedido {order_id}."

@tool
def finalize_order(order_id: str) -> str:
    """Finaliza la venta de un pedido, marcándolo como 'completado' y listo para facturación."""
    with Session() as session:
        stmt = update(orders_table).where(orders_table.c.id == order_id).values(status="completed")
        result = session.execute(stmt)
        session.commit()
        if result.rowcount == 0: return f"Pedido con ID {order_id} no encontrado."
        return f"Pedido {order_id} ha sido finalizado y está listo para facturación."

# Lista consolidada de herramientas para el agente de ventas
sales_tools = [
    search_customer,
    create_order,
    list_products,
    add_product_to_order,
    finalize_order,
]

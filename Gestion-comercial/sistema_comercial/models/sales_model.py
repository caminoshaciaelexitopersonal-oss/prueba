import uuid
from typing import List, Optional, TypedDict, Annotated
from sqlalchemy import select, insert, update, func, sum as sql_sum

from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from database import Session, customers_table, products_table, orders_table, line_items_table
from models.data_models import Customer, Product, LineItem, Order

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

class SalesModel:
    def __init__(self):
        # This model no longer needs other models injected, it's self-sufficient with the database.

        @tool
        def search_customer(name: str) -> str:
            """Searches for a customer by name and returns their details and ID."""
            with Session() as session:
                stmt = select(customers_table).where(customers_table.c.name.ilike(f"%{name}%"))
                results = session.execute(stmt).all()
                if not results: return "Customer not found."
                return "\n".join([f"Name: {r.name}, ID: {r.id}" for r in results])

        @tool
        def create_order(customer_id: str) -> str:
            """Creates a new, empty order for a customer and returns the new Order ID."""
            with Session() as session:
                cust_stmt = select(customers_table).where(customers_table.c.id == customer_id)
                if not session.execute(cust_stmt).first():
                    return "Customer ID not found."

                new_order_id = str(uuid.uuid4())
                stmt = insert(orders_table).values(id=new_order_id, customer_id=customer_id, total_amount=0)
                session.execute(stmt)
                session.commit()
                return f"New order created with ID: {new_order_id}. Please use this ID to add products."

        @tool
        def list_products() -> str:
            """Lists all available products and their prices."""
            with Session() as session:
                stmt = select(products_table)
                results = session.execute(stmt).all()
                return "\n".join([f"Product: {p.name}, Price: ${p.price:.2f}" for p in results])

        @tool
        def add_product_to_order(order_id: str, product_name: str, quantity: int) -> str:
            """Adds a specified quantity of a product to a given order."""
            with Session() as session:
                prod_stmt = select(products_table).where(products_table.c.name.ilike(f"%{product_name}%"))
                product = session.execute(prod_stmt).first()
                if not product: return f"Product '{product_name}' not found."

                line_item_total = product.price * quantity
                li_stmt = insert(line_items_table).values(
                    order_id=order_id, product_id=product.id, quantity=quantity, total=line_item_total
                )
                session.execute(li_stmt)

                total_stmt = select(sql_sum(line_items_table.c.total)).where(line_items_table.c.order_id == order_id)
                new_total = session.execute(total_stmt).scalar_one()
                ord_update_stmt = update(orders_table).where(orders_table.c.id == order_id).values(total_amount=new_total)
                session.execute(ord_update_stmt)

                session.commit()
                return f"Added {quantity} x {product.name} to order {order_id}."

        @tool
        def finalize_order(order_id: str) -> str:
            """Finalizes the sale for an order, marking it as 'completed' and ready for invoicing."""
            with Session() as session:
                stmt = update(orders_table).where(orders_table.c.id == order_id).values(status="completed")
                result = session.execute(stmt)
                session.commit()
                if result.rowcount == 0: return f"Order with ID {order_id} not found."
                return f"Order {order_id} has been finalized and is ready for invoicing."

        self.tools = [search_customer, create_order, list_products, add_product_to_order, finalize_order]
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_retries=1).bind_tools(self.tools)

    def get_agent_executor(self):
        def agent_node(state: AgentState):
            response = self.llm.invoke(state["messages"])
            return {"messages": [response]}

        def tool_node(state: AgentState):
            tool_calls = state["messages"][-1].tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_to_call = {t.name: t for t in self.tools}[tool_name]
                try: output = tool_to_call.invoke(tool_call["args"])
                except Exception as e: output = f"Error executing tool {tool_name}: {e}"
                tool_outputs.append({"tool_call_id": tool_call["id"], "content": str(output)})
            return {"messages": tool_outputs}

        def should_continue(state: AgentState):
            if state["messages"][-1].tool_calls: return "tools"
            return END

        graph = StateGraph(AgentState)
        graph.add_node("agent", agent_node)
        graph.add_node("tools", tool_node)
        graph.set_entry_point("agent")
        graph.add_conditional_edges("agent", should_continue)
        graph.add_edge("tools", "agent")

        return graph.compile()

    def get_customer_by_id(self, customer_id: str) -> Optional[dict]:
        with Session() as session:
            stmt = select(customers_table).where(customers_table.c.id == customer_id)
            result = session.execute(stmt).first()
            return result._asdict() if result else None

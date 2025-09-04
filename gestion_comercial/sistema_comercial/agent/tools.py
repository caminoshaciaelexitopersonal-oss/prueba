from langchain_core.tools import tool
import gestion_comercial.sistema_comercial.database as db
from gestion_comercial.sistema_comercial.models.data_models import Customer
import json

@tool
def add_new_customer(name: str, email: str, phone: str, address: str = "", age: int = 0, location: str = "", interests: list = []) -> str:
    """
    Adds a new customer to the database.

    Args:
        name: The customer's full name.
        email: The customer's email address.
        phone: The customer's phone number.
        address: The customer's physical address.
        age: The customer's age.
        location: The customer's city or region.
        interests: A list of the customer's interests, provided as a JSON string list (e.g., '["tech", "music"]').

    Returns:
        A confirmation message with the new customer's ID.
    """
    try:
        # If interests are provided as a string, parse them.
        if isinstance(interests, str):
            interests_list = json.loads(interests.replace("'", '"'))
        else:
            interests_list = interests

        new_customer = Customer(
            name=name,
            email=email,
            phone=phone,
            address=address,
            age=age,
            location=location,
            interests=interests_list
        )
        db.add_customer(new_customer)
        return f"Éxito: Cliente '{name}' añadido con ID {new_customer.id}."
    except Exception as e:
        return f"Error al añadir cliente: {e}"


@tool
def get_customer_details(customer_id: str) -> str:
    """
    Retrieves the full details of a customer by their ID.

    Args:
        customer_id: The unique ID of the customer.

    Returns:
        A JSON string with the customer's details or an error message.
    """
    customer = db.get_customer_by_id(customer_id)
    if customer:
        return json.dumps(customer.__dict__, default=str)
    return f"Error: No se encontró ningún cliente con el ID {customer_id}."

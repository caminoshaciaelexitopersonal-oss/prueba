from langchain_core.tools import tool
import gestion_comercial.sistema_comercial.database as db
from gestion_comercial.sistema_comercial.models.data_models import Customer, Lead
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

# --- Lead/Opportunity Management Tools ---

@tool
def add_new_lead(customer_id: str, source: str, estimated_value: float = 0.0) -> str:
    """
    Creates a new lead/opportunity for a given customer.

    Args:
        customer_id: The ID of the existing customer.
        source: Where the lead came from (e.g., 'website', 'referral').
        estimated_value: The estimated monetary value of the potential sale.

    Returns:
        A confirmation message with the new lead's ID.
    """
    # First, check if the customer exists
    if not db.get_customer_by_id(customer_id):
        return f"Error: No se puede crear una oportunidad para un cliente que no existe. ID de cliente no encontrado: {customer_id}"

    new_lead = Lead(
        customer_id=customer_id,
        source=source,
        estimated_value=estimated_value
    )
    db.add_lead(new_lead)
    return f"Éxito: Oportunidad creada para el cliente {customer_id} con el ID de oportunidad {new_lead.id}."

@tool
def update_lead_status_tool(lead_id: str, new_status: str, new_pipeline_stage: str) -> str:
    """
    Updates the status and pipeline stage of an existing lead.

    Args:
        lead_id: The ID of the lead to update.
        new_status: The new status (e.g., 'contactado', 'calificado', 'cerrado ganado').
        new_pipeline_stage: The new stage in the sales pipeline (e.g., 'negociacion', 'propuesta').

    Returns:
        A confirmation message.
    """
    success = db.update_lead_status(lead_id, new_status, new_pipeline_stage)
    if success:
        return f"Éxito: El estado de la oportunidad {lead_id} ha sido actualizado."
    else:
        return f"Error: No se pudo actualizar la oportunidad {lead_id}. Verifique que el ID es correcto."

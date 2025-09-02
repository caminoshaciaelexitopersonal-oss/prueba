# gestion_operativa/SG-SST/tools/document_tools.py
from langchain_core.tools import tool
from typing import List, Dict
import datetime

# This is a simplified in-memory storage for documents.
# In a real system, this would use a database or a file storage system.
sgsst_documents = {}

@tool
def create_sgsst_document(title: str, doc_type: str, content: str) -> str:
    """
    Creates a new OHS document, such as a policy, a safe operating procedure (SOP),
    an internal regulation, or a form.

    Args:
        title (str): The title of the document.
        doc_type (str): The type of document. Examples: 'Policy', 'SOP', 'Regulation', 'Form', 'Checklist'.
        content (str): The full text content of the document.

    Returns:
        str: A confirmation message with the ID of the new document.
    """
    doc_id = f"DOC-{len(sgsst_documents) + 1}"
    sgsst_documents[doc_id] = {
        "id": doc_id,
        "title": title,
        "type": doc_type,
        "content": content,
        "version": 1,
        "created_at": datetime.datetime.now().isoformat()
    }
    return f"Successfully created document '{title}' of type '{doc_type}' with ID {doc_id}."

@tool
def find_sgsst_document(query: str) -> str:
    """
    Finds an OHS document by its title or type.

    Args:
        query (str): The title or type of document to search for.

    Returns:
        str: A list of found documents or a 'not found' message.
    """
    results = []
    for doc_id, doc in sgsst_documents.items():
        if query.lower() in doc['title'].lower() or query.lower() in doc['type'].lower():
            results.append(f"- ID: {doc_id}, Title: {doc['title']}, Type: {doc['type']}")

    if not results:
        return f"No documents found matching '{query}'."

    return "Found documents:\n" + "\n".join(results)

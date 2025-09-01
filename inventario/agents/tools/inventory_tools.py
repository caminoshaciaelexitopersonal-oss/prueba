# inventario/agents/tools/inventory_tools.py
"""
Herramientas especializadas para que los agentes de inventario puedan interactuar
con la lógica de negocio del sistema.
"""
import json
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from .... import inventario_logic

def _serializar_respuesta(datos) -> str:
    """Función de ayuda para convertir la salida a una cadena JSON."""
    if not datos:
        return "No se encontraron datos."
    return json.dumps(datos, indent=2, ensure_ascii=False)

# --- Herramientas para el Capitán de Gestión de Stock ---

@tool
def crear_nuevo_producto_tool(nombre: str, sku: str, descripcion: str, costo_inicial: float = 0.0, cantidad_inicial: float = 0.0) -> str:
    """
    Crea un nuevo producto en el inventario. El SKU debe ser único.
    Si se provee cantidad_inicial y costo_inicial, se registrará un movimiento inicial de ajuste.
    """
    try:
        success, producto_id = inventario_logic.crear_producto(
            nombre=nombre, sku=sku, descripcion=descripcion,
            costo_inicial=costo_inicial, cantidad_inicial=cantidad_inicial
        )
        if success:
            return f"Producto '{nombre}' (ID: {producto_id}) creado exitosamente."
        else:
            return "Fallo al crear el producto. El SKU ya podría existir."
    except Exception as e:
        return f"Ocurrió una excepción inesperada: {e}"

@tool
def registrar_movimiento_stock_tool(producto_id: int, tipo_movimiento: str, cantidad: float, costo_unitario: float, fecha: str) -> str:
    """
    Registra un movimiento de stock para un producto existente, como 'compra', 'venta', 'ajuste_positivo' o 'ajuste_negativo'.
    Esto actualizará la cantidad disponible y el costo promedio del producto.
    """
    try:
        success, message = inventario_logic.registrar_movimiento_inventario(
            producto_id=producto_id, tipo_movimiento=tipo_movimiento, cantidad=cantidad,
            costo_unitario=costo_unitario, fecha=fecha
        )
        if success:
            return f"Movimiento '{tipo_movimiento}' para el producto ID {producto_id} registrado con éxito."
        else:
            return f"Fallo al registrar el movimiento: {message}"
    except Exception as e:
        return f"Ocurrió una excepción inesperada: {e}"

@tool
def importar_productos_desde_csv_tool(filepath: str) -> str:
    """
    Importa masivamente productos desde un archivo CSV ubicado en el servidor.
    El archivo debe tener las columnas: nombre,sku,descripcion,costo_inicial,cantidad_inicial.
    Devuelve un resumen de la importación.
    """
    try:
        resumen = inventario_logic.importar_productos_csv(filepath)
        return _serializar_respuesta(resumen)
    except Exception as e:
        return f"Ocurrió una excepción inesperada durante la importación: {e}"

# --- Herramientas para el Capitán de Reportería de Inventario ---

@tool
def obtener_listado_productos_tool() -> str:
    """Obtiene un listado de todos los productos en el inventario."""
    try:
        productos = inventario_logic.obtener_productos()
        return _serializar_respuesta(productos)
    except Exception as e:
        return f"Ocurrió una excepción al obtener el listado de productos: {e}"

@tool
def obtener_kardex_de_producto_tool(producto_id: int) -> str:
    """
    Obtiene el historial detallado de movimientos (Kardex) para un único producto, identificado por su ID.
    """
    try:
        kardex = inventario_logic.obtener_kardex_producto(producto_id)
        return _serializar_respuesta(kardex)
    except Exception as e:
        return f"Ocurrió una excepción al obtener el kardex del producto: {e}"

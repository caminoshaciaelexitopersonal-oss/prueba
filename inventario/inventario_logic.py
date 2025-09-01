# logic/inventario_logic.py
"""
Módulo para la lógica de negocio relacionada con el Inventario.
"""
import logging
import csv
from typing import List, Dict, Any, Optional, Tuple
from database import db_manager
import datetime
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# --- Lógica de Productos ---
@tool
def crear_producto(nombre: str, sku: str, descripcion: str, costo_inicial: float, cantidad_inicial: float) -> str:
    """
    Crea un nuevo producto en el sistema con su stock y costo iniciales.

    Args:
        nombre (str): El nombre del producto.
        sku (str): El código de referencia único (SKU) para el producto.
        descripcion (str): Una breve descripción del producto.
        costo_inicial (float): El costo de adquisición de cada unidad.
        cantidad_inicial (float): La cantidad de unidades con la que se inicia el stock.

    Returns:
        str: Un mensaje de éxito con el ID del nuevo producto o un mensaje de error.
    """
    success, producto_id_or_msg = db_manager.crear_producto_db(nombre, sku, descripcion, 0.0, 0.0)

    if not success:
        return f"Error: No se pudo crear el producto. {producto_id_or_msg}"

    if cantidad_inicial > 0:
        # Usar la función interna para registrar el movimiento
        success_mov, msg_mov = _registrar_movimiento_interno(
            producto_id=producto_id_or_msg,
            tipo_movimiento='ajuste_positivo',
            cantidad=cantidad_inicial,
            costo_unitario=costo_inicial,
            fecha=datetime.date.today().isoformat()
        )
        if not success_mov:
            return f"Producto creado con ID {producto_id_or_msg}, pero falló el registro del stock inicial: {msg_mov}"

    return f"Éxito: Producto '{nombre}' creado con ID {producto_id_or_msg} y stock inicial de {cantidad_inicial}."

@tool
def obtener_productos(filtro: Optional[str] = None) -> str:
    """
    Busca y obtiene una lista de productos del inventario.

    Args:
        filtro (Optional[str]): Un término de búsqueda para filtrar por nombre o SKU. Si se omite, devuelve todos los productos.

    Returns:
        str: Una cadena formateada con la lista de productos, su SKU, stock y costo.
    """
    productos = db_manager.obtener_productos_db(filtro=filtro)
    if not productos:
        return "No se encontraron productos con ese filtro."

    return json.dumps(productos, indent=2, ensure_ascii=False)


# --- Lógica de Movimientos de Inventario (Kardex) ---
import json

# Se renombra a una versión interna para evitar confusión con la herramienta
def _registrar_movimiento_interno(producto_id: int, tipo_movimiento: str, cantidad: float, costo_unitario: float, fecha: str, comprobante_id: Optional[int] = None) -> Tuple[bool, str]:
    """Lógica interna para registrar un movimiento y actualizar el stock."""
    producto_actual = db_manager.obtener_producto_por_id_db(producto_id)
    if not producto_actual:
        msg = f"No se puede registrar movimiento. Producto con ID {producto_id} no encontrado."
        logger.error(msg)
        return False, msg

    cantidad_anterior = producto_actual['cantidad_disponible']
    costo_anterior = producto_actual['costo_unitario_promedio']

    cantidad_cambio = cantidad if tipo_movimiento in ['compra', 'ajuste_positivo'] else -cantidad

    if cantidad_anterior + cantidad_cambio < 0:
        msg = "Stock insuficiente"
        logger.error(f"{msg} para el producto ID {producto_id}. Stock actual: {cantidad_anterior}, se intenta sacar: {cantidad}")
        return False, msg

    cantidad_nueva = cantidad_anterior + cantidad_cambio
    costo_nuevo_promedio = costo_anterior

    if tipo_movimiento in ['compra', 'ajuste_positivo']:
        if cantidad_nueva > 0:
            numerador = (cantidad_anterior * costo_anterior) + (cantidad * costo_unitario)
            denominador = cantidad_nueva
            costo_nuevo_promedio = numerador / denominador
        else:
            costo_nuevo_promedio = costo_unitario

    conn = db_manager.get_db_connection(db_manager.DB_CONTABILIDAD_PATH)
    try:
        with conn:
            db_manager.crear_movimiento_inventario_db(
                conn, producto_id, fecha, tipo_movimiento, cantidad, costo_unitario, comprobante_id
            )
            db_manager.actualizar_stock_producto_db(
                conn, producto_id, cantidad_nueva, costo_nuevo_promedio
            )
        logger.info(f"Movimiento '{tipo_movimiento}' registrado para producto ID {producto_id}. Nuevo stock: {cantidad_nueva}, nuevo costo prom: {costo_nuevo_promedio:.2f}")
        return True, "Éxito"
    except Exception as e:
        msg = f"Error en la transacción de movimiento de inventario: {e}"
        logger.error(msg)
        return False, msg
    finally:
        db_manager.close_connection(conn)

@tool
def registrar_movimiento_inventario(producto_id: int, tipo_movimiento: str, cantidad: float, costo_unitario: float) -> str:
    """
    Registra un movimiento de inventario (Kardex) para un producto, como una compra o una venta.

    Args:
        producto_id (int): El ID del producto que se está moviendo.
        tipo_movimiento (str): El tipo de movimiento. Debe ser 'compra', 'venta', 'ajuste_positivo' o 'ajuste_negativo'.
        cantidad (float): La cantidad de unidades que se mueven.
        costo_unitario (float): El costo por unidad. Para una venta, este debería ser el costo promedio actual del producto.

    Returns:
        str: Un mensaje indicando el resultado de la operación.
    """
    fecha_hoy = datetime.date.today().isoformat()
    success, message = _registrar_movimiento_interno(
        producto_id=producto_id,
        tipo_movimiento=tipo_movimiento,
        cantidad=cantidad,
        costo_unitario=costo_unitario,
        fecha=fecha_hoy
    )
    if success:
        return f"Éxito: Movimiento de inventario '{tipo_movimiento}' registrado para el producto ID {producto_id}."
    else:
        return f"Error al registrar movimiento: {message}"

def obtener_kardex_producto(producto_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de movimientos (Kardex) para un producto específico.
    """
    return db_manager.obtener_movimientos_de_un_producto_db(producto_id)

def importar_productos_csv(filepath: str) -> Dict[str, Any]:
    """
    Importa productos desde un archivo CSV.
    Espera un encabezado: nombre,sku,descripcion,costo_inicial,cantidad_inicial
    Devuelve un diccionario con un resumen de la importación.
    """
    productos_creados = 0
    errores = []

    try:
        with open(filepath, mode='r', encoding='utf-8') as csvfile:
            # Usar DictReader para leer filas como diccionarios
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                try:
                    # Limpiar y convertir datos
                    nombre = row.get('nombre', '').strip()
                    sku = row.get('sku', '').strip()

                    if not nombre or not sku:
                        errores.append(f"Fila {i+2}: 'nombre' y 'sku' son campos obligatorios.")
                        continue

                    costo = float(row.get('costo_inicial', 0.0) or 0.0)
                    cantidad = float(row.get('cantidad_inicial', 0.0) or 0.0)

                    success, result = crear_producto(
                        nombre=nombre,
                        sku=sku,
                        descripcion=row.get('descripcion', ''),
                        costo_inicial=costo,
                        cantidad_inicial=cantidad
                    )
                    if success:
                        productos_creados += 1
                    else:
                        errores.append(f"Fila {i+2}: No se pudo crear el producto con SKU '{sku}' (puede que ya exista).")
                except (KeyError, TypeError, ValueError) as e:
                    errores.append(f"Fila {i+2}: Error de formato o dato faltante - {e}")

        resumen = {"creados": productos_creados, "errores": errores}
        logger.info(f"Importación CSV completada: {resumen}")
        return resumen

    except FileNotFoundError:
        return {"creados": 0, "errores": [f"El archivo no fue encontrado en la ruta: {filepath}"]}
    except Exception as e:
        logger.error(f"Error inesperado al procesar el archivo CSV: {e}")
        return {"creados": 0, "errores": [f"Error inesperado al leer el archivo: {e}"]}

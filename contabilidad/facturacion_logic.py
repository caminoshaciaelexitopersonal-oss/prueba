# logic/facturacion_logic.py
"""
Módulo para la lógica de negocio relacionada con la facturación.
"""
import logging
import datetime
from typing import List, Dict, Any, Optional, Tuple
from database import db_manager
from contabilidad import contabilidad_logic
from inventario import inventario_logic

logger = logging.getLogger(__name__)

# --- Lógica de Lectura ---

def obtener_todas_las_facturas(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Obtiene una lista de todas las facturas.
    """
    return db_manager.obtener_facturas(limit=limit)

def obtener_factura_por_id(factura_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene los detalles completos de una factura específica.
    """
    return db_manager.obtener_factura_con_items(factura_id)

# --- Lógica de Escritura ---

def _generar_asiento_contable_de_factura(factura_id: int, tercero_id: int, total_factura: float, subtotal_ingresos: float, total_impuestos: float, usuario_id: int, fecha: str) -> Optional[int]:
    """
    Función interna para generar el comprobante contable de una factura de venta.
    """
    CUENTA_CLIENTES = "130505"
    CUENTA_INGRESOS = "4135"
    CUENTA_IVA_GENERADO = "240801"

    descripcion_asiento = f"Registro de factura de venta Nro. {factura_id}"
    movimientos = [
        {"cuenta_codigo": CUENTA_CLIENTES, "descripcion_detalle": f"Factura {factura_id}", "debito": total_factura, "credito": 0, "tercero_id": tercero_id},
        {"cuenta_codigo": CUENTA_INGRESOS, "descripcion_detalle": f"Ingreso por factura {factura_id}", "debito": 0, "credito": subtotal_ingresos, "tercero_id": tercero_id},
    ]
    if total_impuestos > 0:
        movimientos.append({"cuenta_codigo": CUENTA_IVA_GENERADO, "descripcion_detalle": f"IVA generado en factura {factura_id}", "debito": 0, "credito": total_impuestos, "tercero_id": tercero_id})

    success, comprobante_id = contabilidad_logic.registrar_nuevo_comprobante(
        fecha=fecha, tipo="Factura de Venta", descripcion=descripcion_asiento,
        movimientos=movimientos, usuario_id=usuario_id
    )
    return comprobante_id if success else None

def _generar_asiento_costo_venta(factura_id: int, total_costo: float, usuario_id: int, fecha: str) -> Optional[int]:
    """
    Genera el asiento contable para el costo de venta (COGS).
    """
    CUENTA_COSTO_VENTA = "6135"  # Costo de Mercancía Vendida
    CUENTA_INVENTARIO = "1435"   # Mercancías no fabricadas por la empresa

    descripcion = f"Costo de venta para factura Nro. {factura_id}"
    movimientos = [
        {"cuenta_codigo": CUENTA_COSTO_VENTA, "descripcion_detalle": descripcion, "debito": total_costo, "credito": 0},
        {"cuenta_codigo": CUENTA_INVENTARIO, "descripcion_detalle": descripcion, "debito": 0, "credito": total_costo},
    ]

    success, comprobante_id = contabilidad_logic.registrar_nuevo_comprobante(
        fecha=fecha, tipo="Costo de Venta", descripcion=descripcion,
        movimientos=movimientos, usuario_id=usuario_id
    )
    return comprobante_id if success else None

def crear_nueva_factura(tercero_id: int, fecha_emision: str, items: List[Dict[str, Any]], usuario_id: int, fecha_vencimiento: Optional[str] = None, estado: str = 'Enviada') -> Tuple[bool, Optional[int]]:
    """
    Orquesta la creación de una factura, su asiento contable, la actualización de inventario y el asiento de costo de venta.
    """
    # 1. Calcular totales
    subtotal_general = sum(item['subtotal'] for item in items)
    total_impuestos = sum(item['subtotal'] * (item.get('impuesto_porcentaje', 0.0) / 100.0) for item in items)
    total_factura = subtotal_general + total_impuestos

    # 2. Guardar la factura en la BD
    success, factura_id = db_manager.crear_factura_db(
        tercero_id=tercero_id, fecha_emision=fecha_emision, fecha_vencimiento=fecha_vencimiento,
        total=total_factura, estado=estado, items=items
    )
    if not success:
        logger.error("No se pudo crear la factura en la base de datos. Abortando.")
        return False, None

    # 3. Generar asiento contable de la Venta (Ingresos)
    comprobante_venta_id = _generar_asiento_contable_de_factura(
        factura_id=factura_id, tercero_id=tercero_id, total_factura=total_factura,
        subtotal_ingresos=subtotal_general, total_impuestos=total_impuestos,
        usuario_id=usuario_id, fecha=fecha_emision
    )
    if not comprobante_venta_id:
        logger.error(f"La factura {factura_id} se creó pero su asiento de VENTA falló.")
        return False, factura_id

    db_manager.enlazar_comprobante_a_factura(factura_id, comprobante_venta_id)

    # 4. Procesar inventario y costo de venta
    items_inventario = [item for item in items if 'producto_id' in item and item['producto_id']]
    total_costo_venta = 0
    if items_inventario:
        for item in items_inventario:
            producto = db_manager.obtener_producto_por_id_db(item['producto_id'])
            if not producto:
                logger.warning(f"Producto ID {item['producto_id']} en factura {factura_id} no encontrado en inventario. Saltando.")
                continue

            costo_item = producto['costo_unitario_promedio'] * item['cantidad']
            total_costo_venta += costo_item

            inventario_logic.registrar_movimiento_inventario(
                producto_id=item['producto_id'],
                tipo_movimiento='venta',
                cantidad=item['cantidad'],
                costo_unitario=producto['costo_unitario_promedio'], # El costo de salida es el promedio actual
                fecha=fecha_emision,
                comprobante_id=None # El comprobante de costo se genera después
            )

        if total_costo_venta > 0:
            comprobante_costo_id = _generar_asiento_costo_venta(
                factura_id=factura_id, total_costo=total_costo_venta,
                usuario_id=usuario_id, fecha=fecha_emision
            )
            if not comprobante_costo_id:
                logger.error(f"El asiento de VENTA para la factura {factura_id} se creó, pero el de COSTO falló.")
                # Esto deja la contabilidad inconsistente, requiere atención.

    logger.info(f"Proceso de factura {factura_id} completado.")
    return True, factura_id

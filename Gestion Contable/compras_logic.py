# logic/compras_logic.py
"""
Módulo para la lógica de negocio relacionada con las Compras y Cuentas por Pagar.
"""
import logging
import datetime
from typing import List, Dict, Any, Optional
from database import db_manager
from contabilidad import contabilidad_logic
from inventario import inventario_logic

logger = logging.getLogger(__name__)

# --- Lógica de Lectura ---

def obtener_todas_las_compras(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Obtiene una lista de todas las facturas de compra.
    """
    return db_manager.obtener_compras(limit=limit)

# --- Lógica de Escritura ---

def _generar_asiento_contable_de_compra(compra_id: int, tercero_id: int, items: List[Dict[str, Any]], concepto_retencion: str, usuario_id: int) -> Optional[int]:
    """
    Función interna para generar el comprobante contable de una factura de compra.
    Distingue entre compras de inventario y compras de gastos.
    """
    # Códigos de cuenta (hardcodeados por ahora, deberían ser configurables)
    CUENTA_PROVEEDORES = "220501"
    CUENTA_INVENTARIO = "1435"  # Mercancías no fabricadas por la empresa
    CUENTA_GASTO_DEFAULT = "5135"
    CUENTA_IVA_DESCONTABLE = "240810"
    CUENTA_RETEFUENTE_PAGAR = "236540"

    subtotal_inventario = sum(item['subtotal'] for item in items if 'producto_id' in item)
    subtotal_gasto = sum(item['subtotal'] for item in items if 'producto_id' not in item)
    subtotal_base = subtotal_inventario + subtotal_gasto

    iva_rate = items[0].get('impuesto_porcentaje', 19.0)
    total_iva = contabilidad_logic.calcular_iva(subtotal_base, iva_rate)

    total_retencion = contabilidad_logic.calcular_retencion_fuente(
        base=subtotal_base,
        concepto=concepto_retencion
    )

    total_a_pagar = subtotal_base + total_iva - total_retencion
    descripcion_asiento = f"Registro de factura de compra Nro. {compra_id}"

    movimientos = []
    # Débito a Inventario si aplica
    if subtotal_inventario > 0:
        movimientos.append({"cuenta_codigo": CUENTA_INVENTARIO, "descripcion_detalle": f"Compra de inventario fac. {compra_id}", "debito": subtotal_inventario, "credito": 0, "tercero_id": tercero_id})
    # Débito a Gasto si aplica
    if subtotal_gasto > 0:
        movimientos.append({"cuenta_codigo": CUENTA_GASTO_DEFAULT, "descripcion_detalle": f"Compra de gasto fac. {compra_id}", "debito": subtotal_gasto, "credito": 0, "tercero_id": tercero_id})

    movimientos.extend([
        {"cuenta_codigo": CUENTA_IVA_DESCONTABLE, "descripcion_detalle": f"IVA descontable en factura {compra_id}", "debito": total_iva, "credito": 0, "tercero_id": tercero_id},
        {"cuenta_codigo": CUENTA_RETEFUENTE_PAGAR, "descripcion_detalle": f"Retefuente en factura {compra_id}", "debito": 0, "credito": total_retencion, "tercero_id": tercero_id},
        {"cuenta_codigo": CUENTA_PROVEEDORES, "descripcion_detalle": f"Factura de proveedor {compra_id}", "debito": 0, "credito": total_a_pagar, "tercero_id": tercero_id},
    ])

    movimientos_reales = [m for m in movimientos if m['debito'] > 0 or m['credito'] > 0]

    success, comprobante_id = contabilidad_logic.registrar_nuevo_comprobante(
        fecha=datetime.date.today().isoformat(),
        tipo="Factura de Compra",
        descripcion=descripcion_asiento,
        movimientos=movimientos_reales,
        usuario_id=usuario_id
    )

    return comprobante_id if success else None


def crear_nueva_compra(tercero_id: int, fecha_emision: str, items: List[Dict[str, Any]], concepto_retencion: str, usuario_id: int, fecha_vencimiento: Optional[str] = None, estado: str = 'Recibida') -> Tuple[bool, Optional[int]]:
    """
    Orquesta la creación de una nueva compra, su asiento contable y la actualización del inventario.
    """
    subtotal = sum(item['subtotal'] for item in items)
    iva_rate = items[0].get('impuesto_porcentaje', 19.0)
    total_compra = subtotal * (1 + iva_rate / 100.0)

    # 1. Guardar la compra en la BD
    success, compra_id = db_manager.crear_compra_db(
        tercero_id=tercero_id, fecha_emision=fecha_emision, fecha_vencimiento=fecha_vencimiento,
        total=total_compra, estado=estado, items=items
    )
    if not success:
        return False, None

    # 2. Generar asiento contable
    comprobante_id = _generar_asiento_contable_de_compra(
        compra_id=compra_id, tercero_id=tercero_id, items=items,
        concepto_retencion=concepto_retencion, usuario_id=usuario_id
    )
    if not comprobante_id:
        # En un caso real, se debería anular la compra o marcarla para revisión
        logger.error(f"La compra {compra_id} se creó pero su asiento contable falló.")
        return False, compra_id

    # 3. Enlazar comprobante a la compra
    db_manager.enlazar_comprobante_a_compra(compra_id, comprobante_id)

    # 4. Actualizar inventario para los items que son productos
    for item in items:
        if 'producto_id' in item and item['producto_id']:
            logger.info(f"Registrando entrada de inventario para producto ID {item['producto_id']}")
            inventario_logic.registrar_movimiento_inventario(
                producto_id=item['producto_id'],
                tipo_movimiento='compra',
                cantidad=item['cantidad'],
                costo_unitario=item['precio_unitario'],
                fecha=fecha_emision,
                comprobante_id=comprobante_id
            )

    logger.info(f"Proceso de compra {compra_id} completado (Contabilidad e Inventario).")
    return True, compra_id

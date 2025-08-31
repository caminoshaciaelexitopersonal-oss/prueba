# utils/constants.py

REGIMEN_TRIBUTARIO_OPCIONES = ["Común", "Simplificado", "Especial", "No Definido"]
NATURALEZA_CUENTA_OPCIONES = ["Debito", "Credito"]
CLASE_CUENTA_OPCIONES = ["Activo", "Pasivo", "Patrimonio", "Ingreso", "Gasto", "Costo Venta", "Costo Produccion", "Cuenta Orden Deudora", "Cuenta Orden Acreedora"]
TIPOS_COMPROBANTE_OPCIONES = ["Comprobante Diario", "Recibo de Caja (Ingreso)", "Comprobante Egreso", "Factura Venta", "Factura Compra", "Nota Crédito", "Nota Débito", "Ajuste Contable"]

# Podrías añadir códigos PUC básicos si quieres pre-cargarlos
PUC_BASICO_COLOMBIA = {
    '1': {'nombre': 'ACTIVO', 'naturaleza': 'Debito', 'clase': 'Activo'},
    '11': {'nombre': 'DISPONIBLE', 'naturaleza': 'Debito', 'clase': 'Activo'},
    '1105': {'nombre': 'CAJA', 'naturaleza': 'Debito', 'clase': 'Activo'},
    '110505': {'nombre': 'Caja General', 'naturaleza': 'Debito', 'clase': 'Activo'},
    '1110': {'nombre': 'BANCOS', 'naturaleza': 'Debito', 'clase': 'Activo'},
    '111005': {'nombre': 'Moneda Nacional', 'naturaleza': 'Debito', 'clase': 'Activo'},
    '2': {'nombre': 'PASIVO', 'naturaleza': 'Credito', 'clase': 'Pasivo'},
    '21': {'nombre': 'OBLIGACIONES FINANCIERAS', 'naturaleza': 'Credito', 'clase': 'Pasivo'},
    '22': {'nombre': 'PROVEEDORES', 'naturaleza': 'Credito', 'clase': 'Pasivo'},
    '2205': {'nombre': 'Proveedores Nacionales', 'naturaleza': 'Credito', 'clase': 'Pasivo'},
    '3': {'nombre': 'PATRIMONIO', 'naturaleza': 'Credito', 'clase': 'Patrimonio'},
    '31': {'nombre': 'CAPITAL SOCIAL', 'naturaleza': 'Credito', 'clase': 'Patrimonio'},
    '3105': {'nombre': 'Capital Suscrito y Pagado', 'naturaleza': 'Credito', 'clase': 'Patrimonio'},
    '4': {'nombre': 'INGRESOS', 'naturaleza': 'Credito', 'clase': 'Ingreso'},
    '41': {'nombre': 'OPERACIONALES', 'naturaleza': 'Credito', 'clase': 'Ingreso'},
    '4135': {'nombre': 'Comercio al por mayor y al por menor', 'naturaleza': 'Credito', 'clase': 'Ingreso'},
    '5': {'nombre': 'GASTOS', 'naturaleza': 'Debito', 'clase': 'Gasto'},
    '51': {'nombre': 'OPERACIONALES DE ADMINISTRACIÓN', 'naturaleza': 'Debito', 'clase': 'Gasto'},
    '5105': {'nombre': 'Gastos de Personal', 'naturaleza': 'Debito', 'clase': 'Gasto'},
    '6': {'nombre': 'COSTOS DE VENTAS', 'naturaleza': 'Debito', 'clase': 'Costo Venta'},
    '61': {'nombre': 'COSTO DE VENTAS Y DE PRESTACIÓN DE SERVICIOS', 'naturaleza': 'Debito', 'clase': 'Costo Venta'},
    '6135': {'nombre': 'Comercio al por mayor y al por menor (Costo)', 'naturaleza': 'Debito', 'clase': 'Costo Venta'},
    # Añadir más cuentas según sea necesario
}
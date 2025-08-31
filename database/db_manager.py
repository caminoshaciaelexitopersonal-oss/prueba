# database/db_manager.py
import sqlite3
import logging
import os
from typing import List, Dict, Any, Optional, Tuple

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas a las bases de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_USUARIOS_PATH = os.path.join(DATA_DIR, 'usuarios.db')
DB_CONTABILIDAD_PATH = os.path.join(DATA_DIR, 'contabilidad.db')

os.makedirs(DATA_DIR, exist_ok=True)

# --- Funciones de Conexión ---

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Establece conexión con la base de datos SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error al conectar con la base de datos {db_path}: {e}")
        raise

def close_connection(conn: Optional[sqlite3.Connection]):
    """Cierra la conexión a la base de datos."""
    if conn:
        conn.close()

# --- Inicialización de Tablas ---

def init_db():
    """Crea las tablas si no existen en ambas bases de datos."""
    # 1. Crear tabla de usuarios
    try:
        conn_user = get_db_connection(DB_USUARIOS_PATH)
        cursor_user = conn_user.cursor()
        cursor_user.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre_empresa TEXT,
                nit TEXT,
                regimen_tributario TEXT CHECK(regimen_tributario IN ('Común', 'Simplificado', 'Especial', 'No Definido')) DEFAULT 'No Definido',
                encryption_key TEXT
            );
        """)
        conn_user.commit()
        logger.info("Tabla 'usuarios' verificada/creada.")
    except sqlite3.Error as e:
        logger.error(f"Error al inicializar DB usuarios: {e}")
    finally:
        close_connection(conn_user)

    # 2. Crear tablas de contabilidad
    try:
        conn_cont = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor_cont = conn_cont.cursor()

        # Tablas sin dependencias
        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS plan_cuentas (
                codigo TEXT PRIMARY KEY NOT NULL,
                nombre TEXT NOT NULL,
                naturaleza TEXT NOT NULL CHECK(naturaleza IN ('Debito', 'Credito')),
                clase TEXT NOT NULL,
                grupo_niif TEXT,
                balance REAL DEFAULT 0.0
            );
        """)

        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS terceros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                nit TEXT UNIQUE NOT NULL,
                tipo TEXT CHECK(tipo IN ('Cliente', 'Proveedor', 'Empleado', 'Otro')) NOT NULL,
                direccion TEXT,
                telefono TEXT,
                email TEXT
            );
        """)

        # Tablas con dependencias
        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS comprobantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                tipo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                total_debito REAL DEFAULT 0.0,
                total_credito REAL DEFAULT 0.0,
                anulado BOOLEAN DEFAULT FALSE,
                usuario_id INTEGER NOT NULL
            );
        """)

        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comprobante_id INTEGER NOT NULL,
                cuenta_codigo TEXT NOT NULL,
                descripcion_detalle TEXT,
                debito REAL DEFAULT 0.0,
                credito REAL DEFAULT 0.0,
                tercero_id INTEGER,
                reconciliado BOOLEAN DEFAULT FALSE,
                anulado BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (comprobante_id) REFERENCES comprobantes(id) ON DELETE CASCADE,
                FOREIGN KEY (cuenta_codigo) REFERENCES plan_cuentas(codigo) ON UPDATE CASCADE,
                FOREIGN KEY (tercero_id) REFERENCES terceros(id)
            );
        """)

        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tercero_id INTEGER NOT NULL,
                fecha_emision DATE NOT NULL,
                fecha_vencimiento DATE,
                total REAL NOT NULL,
                estado TEXT NOT NULL CHECK(estado IN ('Borrador', 'Enviada', 'Pagada', 'Anulada')) DEFAULT 'Borrador',
                comprobante_id INTEGER,
                FOREIGN KEY (tercero_id) REFERENCES terceros(id),
                FOREIGN KEY (comprobante_id) REFERENCES comprobantes(id)
            );
        """)

        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS factura_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER NOT NULL,
                descripcion TEXT NOT NULL,
                cantidad REAL NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                impuesto_porcentaje REAL DEFAULT 0.0,
                FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE
            );
        """)

        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tercero_id INTEGER NOT NULL,
                fecha_emision DATE NOT NULL,
                fecha_vencimiento DATE,
                total REAL NOT NULL,
                estado TEXT NOT NULL CHECK(estado IN ('Borrador', 'Recibida', 'Pagada', 'Anulada')) DEFAULT 'Borrador',
                comprobante_id INTEGER,
                FOREIGN KEY (tercero_id) REFERENCES terceros(id),
                FOREIGN KEY (comprobante_id) REFERENCES comprobantes(id)
            );
        """)

        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS compra_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compra_id INTEGER NOT NULL,
                descripcion TEXT NOT NULL,
                cantidad REAL NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE
            );
        """)

        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS transacciones_bancarias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                descripcion TEXT NOT NULL,
                monto REAL NOT NULL,
                tipo TEXT,
                referencia TEXT UNIQUE,
                movimiento_contable_id INTEGER,
                FOREIGN KEY (movimiento_contable_id) REFERENCES movimientos(id)
            );
        """)

        # Tablas para el Módulo de Inventario
        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                sku TEXT UNIQUE,
                descripcion TEXT,
                costo_unitario_promedio REAL DEFAULT 0.0,
                cantidad_disponible REAL DEFAULT 0.0
            );
        """)

        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                fecha DATE NOT NULL,
                tipo_movimiento TEXT NOT NULL CHECK(tipo_movimiento IN ('compra', 'venta', 'ajuste_positivo', 'ajuste_negativo')),
                cantidad REAL NOT NULL,
                costo_unitario REAL NOT NULL,
                comprobante_id INTEGER,
                FOREIGN KEY (producto_id) REFERENCES productos(id),
                FOREIGN KEY (comprobante_id) REFERENCES comprobantes(id)
            );
        """)

        # Tabla para el Módulo de Activos Fijos
        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS activos_fijos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                fecha_adquisicion DATE NOT NULL,
                costo_adquisicion REAL NOT NULL,
                valor_residual REAL NOT NULL,
                vida_util_meses INTEGER NOT NULL,
                metodo_depreciacion TEXT NOT NULL,
                cuenta_activo TEXT NOT NULL,
                cuenta_depreciacion_acumulada TEXT NOT NULL,
                cuenta_gasto_depreciacion TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Activo'
            );
        """)

        conn_cont.commit()
        logger.info("Tablas de 'contabilidad' verificadas/creadas.")
    except sqlite3.Error as e:
        logger.error(f"Error al inicializar DB contabilidad: {e}")
    finally:
        close_connection(conn_cont)

# --- Funciones CRUD para Usuarios ---

def crear_usuario(username: str, hashed_pass: str, nombre_empresa: Optional[str] = None, nit: Optional[str] = None) -> Optional[int]:
    conn = None
    try:
        conn = get_db_connection(DB_USUARIOS_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password_hash, nombre_empresa, nit) VALUES (?, ?, ?, ?)", (username, hashed_pass, nombre_empresa, nit))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        logger.warning(f"El nombre de usuario '{username}' ya existe.")
        return None
    except sqlite3.Error as e:
        logger.error(f"Error al crear usuario '{username}': {e}")
        return None
    finally:
        close_connection(conn)

def verificar_usuario(username: str) -> Optional[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_USUARIOS_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, regimen_tributario FROM usuarios WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        return dict(user_row) if user_row else None
    except sqlite3.Error as e:
        logger.error(f"Error al verificar usuario '{username}': {e}")
        return None
    finally:
        close_connection(conn)

def actualizar_regimen_usuario(user_id: int, regimen: str) -> bool:
    conn = None
    try:
        conn = get_db_connection(DB_USUARIOS_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET regimen_tributario = ? WHERE id = ?", (regimen, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error al actualizar régimen para usuario ID {user_id}: {e}")
        return False
    finally:
        close_connection(conn)

# --- Funciones para Módulo de Inventario ---

def crear_producto_db(nombre: str, sku: str, descripcion: str, costo: float, cantidad: float) -> Tuple[bool, Optional[int]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, sku, descripcion, costo_unitario_promedio, cantidad_disponible) VALUES (?, ?, ?, ?, ?)",
            (nombre, sku, descripcion, costo, cantidad)
        )
        conn.commit()
        return True, cursor.lastrowid
    except sqlite3.IntegrityError:
        logger.warning(f"Producto con SKU '{sku}' ya existe.")
        return False, None
    except sqlite3.Error as e:
        logger.error(f"Error al crear producto en DB: {e}")
        return False, None
    finally:
        close_connection(conn)

def obtener_productos_db() -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener productos de la DB: {e}")
        return []
    finally:
        close_connection(conn)

# --- Funciones para Módulo de Activos Fijos ---

def crear_activo_fijo_db(
    nombre: str, descripcion: str, fecha_adquisicion: str, costo_adquisicion: float,
    valor_residual: float, vida_util_meses: int, metodo_depreciacion: str,
    cuenta_activo: str, cuenta_depreciacion_acumulada: str, cuenta_gasto_depreciacion: str
) -> Tuple[bool, Optional[int]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO activos_fijos (nombre, descripcion, fecha_adquisicion, costo_adquisicion, valor_residual, vida_util_meses, metodo_depreciacion, cuenta_activo, cuenta_depreciacion_acumulada, cuenta_gasto_depreciacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (nombre, descripcion, fecha_adquisicion, costo_adquisicion, valor_residual, vida_util_meses, metodo_depreciacion, cuenta_activo, cuenta_depreciacion_acumulada, cuenta_gasto_depreciacion)
        )
        conn.commit()
        return True, cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error al crear activo fijo en DB: {e}")
        return False, None
    finally:
        close_connection(conn)

def obtener_activos_fijos_db(estado: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        query = "SELECT * FROM activos_fijos"
        params = []
        if estado:
            query += " WHERE estado = ?"
            params.append(estado)
        query += " ORDER BY fecha_adquisicion"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener activos fijos de la DB: {e}")
        return []
    finally:
        close_connection(conn)

def obtener_producto_por_id_db(producto_id: int) -> Optional[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        logger.error(f"Error al obtener producto {producto_id} de la DB: {e}")
        return None
    finally:
        close_connection(conn)

def crear_movimiento_inventario_db(conn: sqlite3.Connection, producto_id: int, fecha: str, tipo_movimiento: str, cantidad: float, costo_unitario: float, comprobante_id: Optional[int]):
    """Inserta un movimiento de inventario usando una conexión existente."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO movimientos_inventario (producto_id, fecha, tipo_movimiento, cantidad, costo_unitario, comprobante_id) VALUES (?, ?, ?, ?, ?, ?)",
        (producto_id, fecha, tipo_movimiento, cantidad, costo_unitario, comprobante_id)
    )

def actualizar_stock_producto_db(conn: sqlite3.Connection, producto_id: int, nueva_cantidad: float, nuevo_costo: float):
    """Actualiza el stock y costo de un producto usando una conexión existente."""
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET cantidad_disponible = ?, costo_unitario_promedio = ? WHERE id = ?",
        (nueva_cantidad, nuevo_costo, producto_id)
    )

def obtener_movimientos_de_un_producto_db(producto_id: int) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movimientos_inventario WHERE producto_id = ? ORDER BY fecha, id", (producto_id,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener kardex para producto {producto_id}: {e}")
        return []
    finally:
        close_connection(conn)

def obtener_datos_usuario(user_id: int) -> Optional[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_USUARIOS_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, nombre_empresa, nit, regimen_tributario FROM usuarios WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        return dict(user_row) if user_row else None
    except sqlite3.Error as e:
        logger.error(f"Error al obtener datos del usuario ID {user_id}: {e}")
        return None
    finally:
        close_connection(conn)

def obtener_terceros_por_tipo(tipo_tercero: str) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, nit FROM terceros WHERE tipo = ? ORDER BY nombre", (tipo_tercero,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener terceros por tipo '{tipo_tercero}': {e}")
        return []
    finally:
        close_connection(conn)

# --- Funciones CRUD para Plan de Cuentas (PUC) ---

def agregar_cuenta_puc(codigo: str, nombre: str, naturaleza: str, clase: str, grupo_niif: Optional[str] = None) -> bool:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO plan_cuentas (codigo, nombre, naturaleza, clase, grupo_niif) VALUES (?, ?, ?, ?, ?)", (codigo, nombre, naturaleza, clase, grupo_niif))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"El código de cuenta PUC '{codigo}' ya existe.")
        return False
    except sqlite3.Error as e:
        logger.error(f"Error al agregar cuenta PUC '{codigo}': {e}")
        return False
    finally:
        close_connection(conn)

def obtener_cuentas_puc(filtro: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        query = "SELECT codigo, nombre, naturaleza, clase, grupo_niif FROM plan_cuentas"
        params = []
        if filtro:
            query += " WHERE codigo LIKE ? OR nombre LIKE ?"
            params.extend([f'%{filtro}%', f'%{filtro}%'])
        query += " ORDER BY codigo"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener cuentas PUC: {e}")
        return []
    finally:
        close_connection(conn)

def obtener_cuenta_puc_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, naturaleza, clase FROM plan_cuentas WHERE codigo = ?", (codigo,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        logger.error(f"Error al obtener cuenta PUC por código '{codigo}': {e}")
        return None
    finally:
        close_connection(conn)

# --- Funciones CRUD para Comprobantes y Movimientos ---

def agregar_comprobante_y_movimientos(fecha: str, tipo: str, descripcion: str, movimientos: List[Dict[str, Any]], usuario_id: int) -> Tuple[bool, Optional[int]]:
    conn = None
    total_debito = sum(float(m.get('debito', 0) or 0) for m in movimientos)
    total_credito = sum(float(m.get('credito', 0) or 0) for m in movimientos)
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")
        cursor.execute("INSERT INTO comprobantes (fecha, tipo, descripcion, total_debito, total_credito, usuario_id) VALUES (?, ?, ?, ?, ?, ?)", (fecha, tipo, descripcion, total_debito, total_credito, usuario_id))
        comprobante_id = cursor.lastrowid
        if not comprobante_id:
            raise sqlite3.Error("No se pudo obtener el ID del comprobante insertado.")
        mov_to_insert = [(comprobante_id, m['cuenta_codigo'], m.get('descripcion_detalle'), float(m.get('debito', 0) or 0), float(m.get('credito', 0) or 0), m.get('tercero_id')) for m in movimientos]
        cursor.executemany("INSERT INTO movimientos (comprobante_id, cuenta_codigo, descripcion_detalle, debito, credito, tercero_id) VALUES (?, ?, ?, ?, ?, ?)", mov_to_insert)
        conn.commit()
        return True, comprobante_id
    except (sqlite3.Error, ValueError) as e:
        logger.error(f"Error al agregar comprobante y movimientos: {e}")
        if conn:
            conn.rollback()
        return False, None
    finally:
        close_connection(conn)

def obtener_comprobantes(limit: int = 50, offset: int = 0, filtro_fecha: Optional[str] = None, filtro_tipo: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene una lista de comprobantes con filtros y paginación."""
    conn = None
    comprobantes = []
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        query = "SELECT id, fecha, tipo, descripcion, total_debito, total_credito FROM comprobantes WHERE anulado = FALSE"
        params = []

        if filtro_fecha:
            query += " AND fecha = ?"
            params.append(filtro_fecha)
        if filtro_tipo:
            query += " AND tipo = ?"
            params.append(filtro_tipo)

        query += " ORDER BY fecha DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        comprobantes = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener comprobantes: {e}")
    finally:
        close_connection(conn)
    return comprobantes

def obtener_movimientos_por_comprobante(comprobante_id: int) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT m.id, m.cuenta_codigo, p.nombre as cuenta_nombre, m.descripcion_detalle, m.debito, m.credito FROM movimientos m JOIN plan_cuentas p ON m.cuenta_codigo = p.codigo WHERE m.comprobante_id = ? ORDER BY m.id", (comprobante_id,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener movimientos: {e}")
        return []
    finally:
        close_connection(conn)

def obtener_libro_diario(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        query = "SELECT c.fecha, c.id as comprobante_id, c.tipo as tipo_comprobante, m.cuenta_codigo, p.nombre as cuenta_nombre, m.descripcion_detalle, m.debito, m.credito FROM movimientos m JOIN comprobantes c ON m.comprobante_id = c.id JOIN plan_cuentas p ON m.cuenta_codigo = p.codigo WHERE c.anulado = FALSE"
        params = []
        if fecha_inicio:
            query += " AND c.fecha >= ?"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND c.fecha <= ?"
            params.append(fecha_fin)
        query += " ORDER BY c.fecha, c.id, m.id"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener libro diario: {e}")
        return []
    finally:
        close_connection(conn)

# --- Funciones para Compras y Facturas ---

def obtener_facturas(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        query = "SELECT f.id, f.fecha_emision, f.total, f.estado, t.nombre as cliente_nombre FROM facturas f JOIN terceros t ON f.tercero_id = t.id ORDER BY f.fecha_emision DESC, f.id DESC LIMIT ? OFFSET ?"
        cursor.execute(query, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener facturas: {e}")
        return []
    finally:
        close_connection(conn)

def crear_factura_db(tercero_id: int, fecha_emision: str, fecha_vencimiento: Optional[str], total: float, estado: str, items: List[Dict[str, Any]]) -> Tuple[bool, Optional[int]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")
        cursor.execute("INSERT INTO facturas (tercero_id, fecha_emision, fecha_vencimiento, total, estado) VALUES (?, ?, ?, ?, ?)", (tercero_id, fecha_emision, fecha_vencimiento, total, estado))
        factura_id = cursor.lastrowid
        if not factura_id:
            raise sqlite3.Error("No se pudo obtener el ID de la factura insertada.")
        items_to_insert = [(factura_id, item['descripcion'], item['cantidad'], item['precio_unitario'], item['subtotal'], item.get('impuesto_porcentaje', 0.0)) for item in items]
        cursor.executemany("INSERT INTO factura_items (factura_id, descripcion, cantidad, precio_unitario, subtotal, impuesto_porcentaje) VALUES (?, ?, ?, ?, ?, ?)", items_to_insert)
        conn.commit()
        return True, factura_id
    except sqlite3.Error as e:
        logger.error(f"Error al crear factura en DB: {e}")
        if conn: conn.rollback()
        return False, None
    finally:
        close_connection(conn)

def enlazar_comprobante_a_factura(factura_id: int, comprobante_id: int) -> bool:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE facturas SET comprobante_id = ? WHERE id = ?", (comprobante_id, factura_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error al enlazar comprobante {comprobante_id} a factura {factura_id}: {e}")
        return False
    finally:
        close_connection(conn)

def obtener_compras(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        query = "SELECT c.id, c.fecha_emision, c.total, c.estado, t.nombre as proveedor_nombre FROM compras c JOIN terceros t ON c.tercero_id = t.id ORDER BY c.fecha_emision DESC, c.id DESC LIMIT ? OFFSET ?"
        cursor.execute(query, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener compras: {e}")
        return []
    finally:
        close_connection(conn)

def crear_compra_db(tercero_id: int, fecha_emision: str, fecha_vencimiento: Optional[str], total: float, estado: str, items: List[Dict[str, Any]]) -> Tuple[bool, Optional[int]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")
        cursor.execute("INSERT INTO compras (tercero_id, fecha_emision, fecha_vencimiento, total, estado) VALUES (?, ?, ?, ?, ?)", (tercero_id, fecha_emision, fecha_vencimiento, total, estado))
        compra_id = cursor.lastrowid
        if not compra_id:
            raise sqlite3.Error("No se pudo obtener el ID de la compra insertada.")
        items_to_insert = [(compra_id, item['descripcion'], item['cantidad'], item['precio_unitario'], item['subtotal']) for item in items]
        cursor.executemany("INSERT INTO compra_items (compra_id, descripcion, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)", items_to_insert)
        conn.commit()
        return True, compra_id
    except sqlite3.Error as e:
        logger.error(f"Error al crear compra en DB: {e}")
        if conn: conn.rollback()
        return False, None
    finally:
        close_connection(conn)

def enlazar_comprobante_a_compra(compra_id: int, comprobante_id: int) -> bool:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE compras SET comprobante_id = ? WHERE id = ?", (comprobante_id, compra_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error al enlazar comprobante {comprobante_id} a compra {compra_id}: {e}")
        return False
    finally:
        close_connection(conn)

# --- Funciones para Conciliación Bancaria ---

def insertar_transacciones_bancarias(transacciones: List[Dict[str, Any]]) -> bool:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO transacciones_bancarias (fecha, descripcion, monto, tipo, referencia) VALUES (?, ?, ?, ?, ?)", [(t['fecha'], t['descripcion'], t['monto'], t.get('tipo'), t.get('referencia')) for t in transacciones])
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error al insertar transacciones bancarias: {e}")
        return False
    finally:
        close_connection(conn)

def obtener_transacciones_bancarias_no_reconciliadas() -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transacciones_bancarias WHERE movimiento_contable_id IS NULL ORDER BY fecha")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener transacciones bancarias no reconciliadas: {e}")
        return []
    finally:
        close_connection(conn)

def obtener_movimientos_contables_no_reconciliados(cuenta_banco_codigo: str) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movimientos WHERE cuenta_codigo = ? AND reconciliado = FALSE AND anulado = FALSE ORDER BY fecha", (cuenta_banco_codigo,))
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener movimientos contables no reconciliados: {e}")
        return []
    finally:
        close_connection(conn)

def marcar_como_reconciliados(movimiento_id: int, transaccion_id: int) -> bool:
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;")
        cursor.execute("UPDATE movimientos SET reconciliado = TRUE WHERE id = ?", (movimiento_id,))
        cursor.execute("UPDATE transacciones_bancarias SET movimiento_contable_id = ? WHERE id = ?", (movimiento_id, transaccion_id))
        if cursor.rowcount == 0:
            raise sqlite3.Error("La transacción bancaria no fue encontrada para actualizar.")
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error al marcar como reconciliados: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        close_connection(conn)

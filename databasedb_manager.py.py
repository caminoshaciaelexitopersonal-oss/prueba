# database/db_manager.py
import sqlite3
import logging
import os
from typing import List, Dict, Any, Optional, Tuple

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas a las bases de datos (asegúrate que la carpeta 'data' exista o créala)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Directorio raíz del proyecto
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_USUARIOS_PATH = os.path.join(DATA_DIR, 'usuarios.db')
DB_CONTABILIDAD_PATH = os.path.join(DATA_DIR, 'contabilidad.db')

# Crear carpeta data si no existe
os.makedirs(DATA_DIR, exist_ok=True)

# --- Funciones de Conexión ---

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Establece conexión con la base de datos SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Devuelve filas como diccionarios
        conn.execute("PRAGMA foreign_keys = ON;") # Habilitar claves foráneas
        logger.info(f"Conexión establecida con {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error al conectar con la base de datos {db_path}: {e}")
        raise  # Relanza la excepción para manejarla arriba

def close_connection(conn: Optional[sqlite3.Connection]):
    """Cierra la conexión a la base de datos si está abierta."""
    if conn:
        try:
            conn.close()
            logger.info("Conexión cerrada.")
        except sqlite3.Error as e:
            logger.error(f"Error al cerrar la conexión: {e}")

# --- Inicialización de Tablas ---

def init_db():
    """Crea las tablas si no existen en ambas bases de datos."""
    # Crear tablas de usuarios
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

    # Crear tablas de contabilidad
    try:
        conn_cont = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor_cont = conn_cont.cursor()

        # Tabla Plan de Cuentas (PUC)
        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS plan_cuentas (
                codigo TEXT PRIMARY KEY NOT NULL,
                nombre TEXT NOT NULL,
                naturaleza TEXT NOT NULL CHECK(naturaleza IN ('Debito', 'Credito')),
                clase TEXT NOT NULL,
                grupo_niif TEXT -- Opcional
            );
        """)

        # Tabla Comprobantes
        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS comprobantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                tipo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                total_debito REAL DEFAULT 0.0,
                total_credito REAL DEFAULT 0.0,
                anulado BOOLEAN DEFAULT FALSE,
                usuario_id INTEGER NOT NULL -- En una app real, referenciaría a usuarios.id de usuarios.db (complejo con SQLite separados)
                -- Por simplicidad aquí, asumimos un ID, pero no hay FK directa entre archivos DB
                -- FOREIGN KEY (usuario_id) REFERENCES usuarios(id) NO ES POSIBLE ENTRE ARCHIVOS DIFERENTES
            );
        """)
        cursor_cont.execute("CREATE INDEX IF NOT EXISTS idx_comprobantes_fecha ON comprobantes(fecha);")


        # Tabla Movimientos (Detalle del comprobante - Libro Diario)
        cursor_cont.execute("""
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comprobante_id INTEGER NOT NULL,
                cuenta_codigo TEXT NOT NULL,
                descripcion_detalle TEXT,
                debito REAL DEFAULT 0.0,
                credito REAL DEFAULT 0.0,
                tipo_activo TEXT, -- Tipo de activo (ej: edificio, maquinaria, etc.)
                metodo_depreciacion TEXT, -- Método de depreciación (ej: lineal, decreciente, etc.)
                valor_razonable REAL, -- Valor razonable del activo
                vida_util_estimada INTEGER, -- Vida útil estimada en meses
                FOREIGN KEY (comprobante_id) REFERENCES comprobantes(id) ON DELETE CASCADE,
                FOREIGN KEY (cuenta_codigo) REFERENCES plan_cuentas(codigo) ON UPDATE CASCADE
            );
        """)
        cursor_cont.execute("CREATE INDEX IF NOT EXISTS idx_movimientos_comprobante ON movimientos(comprobante_id);")
        cursor_cont.execute("CREATE INDEX IF NOT EXISTS idx_movimientos_cuenta ON movimientos(cuenta_codigo);")

        # Placeholder para Impuestos (simplificado, podría ir en movimientos o tabla separada)
        # CREATE TABLE IF NOT EXISTS impuestos (...)

        conn_cont.commit()
        logger.info("Tablas de 'contabilidad' verificadas/creadas.")

    except sqlite3.Error as e:
        logger.error(f"Error al inicializar DB contabilidad: {e}")
    finally:
        close_connection(conn_cont)

# --- Funciones CRUD para Usuarios ---

def crear_usuario(username: str, hashed_pass: str, nombre_empresa: Optional[str] = None, nit: Optional[str] = None) -> Optional[int]:
    """Inserta un nuevo usuario y devuelve su ID."""
    conn = None
    try:
        conn = get_db_connection(DB_USUARIOS_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, nombre_empresa, nit) VALUES (?, ?, ?, ?)",
            (username, hashed_pass, nombre_empresa, nit)
        )
        conn.commit()
        user_id = cursor.lastrowid
        logger.info(f"Usuario '{username}' creado con ID: {user_id}")
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
    """Busca un usuario por username y devuelve sus datos o None si no existe."""
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
    """Actualiza el régimen tributario de un usuario."""
    conn = None
    try:
        conn = get_db_connection(DB_USUARIOS_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET regimen_tributario = ? WHERE id = ?", (regimen, user_id))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            logger.info(f"Régimen actualizado a '{regimen}' para usuario ID: {user_id}")
        else:
            logger.warning(f"No se encontró usuario con ID: {user_id} para actualizar régimen.")
        return success
    except sqlite3.Error as e:
        logger.error(f"Error al actualizar régimen para usuario ID {user_id}: {e}")
        return False
    finally:
        close_connection(conn)

def obtener_datos_usuario(user_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene todos los datos de un usuario por ID."""
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

# --- Funciones CRUD para Plan de Cuentas (PUC) ---

def agregar_cuenta_puc(codigo: str, nombre: str, naturaleza: str, clase: str, grupo_niif: Optional[str] = None) -> bool:
    """Agrega una nueva cuenta al plan de cuentas."""
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO plan_cuentas (codigo, nombre, naturaleza, clase, grupo_niif) VALUES (?, ?, ?, ?, ?)",
            (codigo, nombre, naturaleza, clase, grupo_niif)
        )
        conn.commit()
        logger.info(f"Cuenta PUC '{codigo} - {nombre}' agregada.")
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
    """Obtiene todas las cuentas del PUC, opcionalmente filtradas por código o nombre."""
    conn = None
    cuentas = []
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
        cuentas = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener cuentas PUC: {e}")
    finally:
        close_connection(conn)
    return cuentas

def obtener_cuenta_puc_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """Obtiene una cuenta específica por su código."""
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


def eliminar_cuenta_puc(codigo: str) -> bool:
    """Elimina una cuenta del PUC (¡cuidado con las dependencias!)."""
    # Advertencia: Asegúrate de que la cuenta no esté en uso en movimientos antes de eliminarla
    # Esto requeriría una verificación adicional.
    conn = None
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        # Primero verificar si se usa en movimientos (simplificado)
        cursor.execute("SELECT 1 FROM movimientos WHERE cuenta_codigo = ? LIMIT 1", (codigo,))
        if cursor.fetchone():
            logger.warning(f"No se puede eliminar la cuenta '{codigo}'. Está en uso en movimientos.")
            return False

        cursor.execute("DELETE FROM plan_cuentas WHERE codigo = ?", (codigo,))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            logger.info(f"Cuenta PUC '{codigo}' eliminada.")
        else:
            logger.warning(f"No se encontró la cuenta PUC '{codigo}' para eliminar.")
        return success
    except sqlite3.Error as e:
        logger.error(f"Error al eliminar cuenta PUC '{codigo}': {e}")
        return False
    finally:
        close_connection(conn)


# --- Funciones CRUD para Comprobantes y Movimientos ---

def agregar_comprobante_y_movimientos(fecha: str, tipo: str, descripcion: str, movimientos: List[Dict[str, Any]], usuario_id: int) -> Tuple[bool, Optional[int]]:
    """
    Agrega un comprobante y sus movimientos asociados en una transacción, incluyendo información NIIF.
    Devuelve (True, comprobante_id) si es exitoso, (False, None) en caso contrario.
    """
    conn = None
    comprobante_id = None
    total_debito = sum(float(m.get('debito', 0) or 0) for m in movimientos)
    total_credito = sum(float(m.get('credito', 0) or 0) for m in movimientos)

    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION;") # Iniciar transacción

        # Insertar Comprobante
        cursor.execute(
            """
            INSERT INTO comprobantes (fecha, tipo, descripcion, total_debito, total_credito, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (fecha, tipo, descripcion, total_debito, total_credito, usuario_id)
        )
        comprobante_id = cursor.lastrowid
        logger.info(f"Comprobante {comprobante_id} ('{tipo}') creado temporalmente.")

        if not comprobante_id:
             raise sqlite3.Error("No se pudo obtener el ID del comprobante insertado.")

        # Insertar Movimientos
        movimientos_sql = []
        for mov in movimientos:
            debito = float(mov.get('debito', 0) or 0)
            credito = float(mov.get('credito', 0) or 0)
            tipo_activo = mov.get('tipo_activo', None)
            metodo_depreciacion = mov.get('metodo_depreciacion', None)
            valor_razonable = mov.get('valor_razonable', None)
            vida_util_estimada = mov.get('vida_util_estimada', None)

            # Validar que una cuenta exista antes de insertarla (opcional pero bueno)
            cuenta_existe = obtener_cuenta_puc_por_codigo(mov['cuenta_codigo'])
            if not cuenta_existe:
                raise ValueError(f"La cuenta PUC con código '{mov['cuenta_codigo']}' no existe.")

            # Solo añadir si hay valor de débito o crédito
            if debito > 0 or credito > 0:
                 mov['comprobante_id'] = comprobante_id
                 movimientos_sql.append(mov)

        if not movimientos_sql:
             raise ValueError("El comprobante debe tener al menos un movimiento con valor.")


        cursor.executemany(
            """
            INSERT INTO movimientos (comprobante_id, cuenta_codigo, descripcion_detalle, debito, credito, tipo_activo, metodo_depreciacion, valor_razonable, vida_util_estimada)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(
                mov['comprobante_id'],
                mov['cuenta_codigo'],
                mov.get('descripcion_detalle', None),
                mov['debito'],
                mov['credito'],
                mov.get('tipo_activo', None),
                mov.get('metodo_depreciacion', None),
                mov.get('valor_razonable', None),
                mov.get('vida_util_estimada', None)
            ) for mov in movimientos_sql]
        )

        conn.commit() # Confirmar transacción
        logger.info(f"Comprobante ID {comprobante_id} y sus {len(movimientos_sql)} movimientos guardados exitosamente.")
        return True, comprobante_id

    except (sqlite3.Error, ValueError) as e:
        logger.error(f"Error al agregar comprobante y movimientos: {e}")
        if conn:
            conn.rollback() # Revertir cambios en caso de error
            logger.info("Transacción revertida.")
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
        query = "SELECT id, fecha, tipo, descripcion, total_debito, total_credito, anulado, usuario_id FROM comprobantes WHERE anulado = FALSE" # Excluir anulados por defecto
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
    """Obtiene los movimientos de un comprobante específico."""
    conn = None
    movimientos = []
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.id, m.cuenta_codigo, p.nombre as cuenta_nombre, m.descripcion_detalle, m.debito, m.credito, m.tipo_activo, m.metodo_depreciacion, m.valor_razonable, m.vida_util_estimada
            FROM movimientos m
            JOIN plan_cuentas p ON m.cuenta_codigo = p.codigo
            WHERE m.comprobante_id = ?
            ORDER BY m.id
            """,
            (comprobante_id,)
        )
        movimientos = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener movimientos del comprobante {comprobante_id}: {e}")
    finally:
        close_connection(conn)
    return movimientos

# --- Funciones para Libros (Diario, Mayor) ---

def obtener_libro_diario(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene todos los movimientos ordenados por fecha y comprobante (Libro Diario)."""
    conn = None
    movimientos = []
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        query = """
            SELECT
                c.fecha, c.id as comprobante_id, c.tipo as tipo_comprobante,
                m.cuenta_codigo, p.nombre as cuenta_nombre,
                m.descripcion_detalle, m.debito, m.credito
            FROM movimientos m
            JOIN comprobantes c ON m.comprobante_id = c.id
            JOIN plan_cuentas p ON m.cuenta_codigo = p.codigo
            WHERE c.anulado = FALSE
        """
        params = []
        if fecha_inicio:
            query += " AND c.fecha >= ?"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND c.fecha <= ?"
            params.append(fecha_fin)

        query += " ORDER BY c.fecha, c.id, m.id"
        cursor.execute(query, params)
        movimientos = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener libro diario: {e}")
    finally:
        close_connection(conn)
    return movimientos

def obtener_libro_mayor_por_cuenta(cuenta_codigo: str, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene los movimientos de una cuenta específica para el Libro Mayor."""
    conn = None
    movimientos = []
    try:
        conn = get_db_connection(DB_CONTABILIDAD_PATH)
        cursor = conn.cursor()
        query = """
            SELECT
                c.fecha, c.id as comprobante_id, c.tipo as tipo_comprobante, c.descripcion as desc_comprobante,
                m.id as movimiento_id, m.descripcion_detalle, m.debito, m.credito
            FROM movimientos m
            JOIN comprobantes c ON m.comprobante_id = c.id
            WHERE m.cuenta_codigo = ? AND c.anulado = FALSE
        """
        params = [cuenta_codigo]
        if fecha_inicio:
            query += " AND c.fecha >= ?"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND c.fecha <= ?"
            params.append(fecha_fin)

        query += " ORDER BY c.fecha, c.id, m.id"
        cursor.execute(query, params)
        movimientos = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Error al obtener libro mayor para la cuenta '{cuenta_codigo}': {e}")
    finally:
        close_connection(conn)
    return movimientos


# Inicializar las bases de datos al importar el módulo si no existen
# init_db() # Puedes descomentar esto si quieres que se creen al iniciar
#           # O llamarlo explícitamente en main.py
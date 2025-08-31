import unittest
import sys
import os
import sqlite3
import datetime
import csv

# Añadir el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inventario import inventario_logic
from database import db_manager

class TestInventarioLogic(unittest.TestCase):

    def setUp(self):
        """
        Configura una base de datos de prueba en un archivo temporal para cada test.
        """
        self.db_path = "test_inventario_logic.db"
        db_manager.DB_CONTABILIDAD_PATH = self.db_path

        # Asegurarse de que no exista un archivo de BD de una corrida anterior
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        db_manager.init_db()

        success, self.producto_id = inventario_logic.crear_producto(
            nombre="Producto de Prueba",
            sku="PRUEBA-001",
            descripcion="Un producto para testing",
            costo_inicial=100.0,
            cantidad_inicial=10.0
        )
        self.assertTrue(success, "La creación del producto de prueba inicial falló.")
        self.assertIsNotNone(self.producto_id)

    def tearDown(self):
        """
        Elimina la base de datos de prueba después de cada test.
        """
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_compra_actualiza_stock_y_costo(self):
        """Prueba que una compra actualiza correctamente el stock y el costo promedio."""
        # Estado inicial: 10 unidades a $100

        # Registrar una nueva compra: 10 unidades a $120
        inventario_logic.registrar_movimiento_inventario(
            producto_id=self.producto_id,
            tipo_movimiento='compra',
            cantidad=10.0,
            costo_unitario=120.0,
            fecha=datetime.date.today().isoformat()
        )

        producto = db_manager.obtener_producto_por_id_db(self.producto_id)

        # Verificar nuevo stock: 10 + 10 = 20
        self.assertAlmostEqual(producto['cantidad_disponible'], 20.0)

        # Verificar nuevo costo promedio ponderado:
        # ((10 * 100) + (10 * 120)) / 20 = 110
        self.assertAlmostEqual(producto['costo_unitario_promedio'], 110.0)

    def test_venta_actualiza_stock(self):
        """Prueba que una venta disminuye el stock pero no cambia el costo promedio."""
        # Estado inicial: 10 unidades a $100
        producto_antes = db_manager.obtener_producto_por_id_db(self.producto_id)
        costo_antes = producto_antes['costo_unitario_promedio']

        # Registrar una venta: 3 unidades
        inventario_logic.registrar_movimiento_inventario(
            producto_id=self.producto_id,
            tipo_movimiento='venta',
            cantidad=3.0,
            costo_unitario=costo_antes, # El costo de salida es el promedio actual
            fecha=datetime.date.today().isoformat()
        )

        producto_despues = db_manager.obtener_producto_por_id_db(self.producto_id)

        # Verificar nuevo stock: 10 - 3 = 7
        self.assertAlmostEqual(producto_despues['cantidad_disponible'], 7.0)

        # Verificar que el costo promedio no ha cambiado
        self.assertAlmostEqual(producto_despues['costo_unitario_promedio'], costo_antes)

    def test_venta_sin_stock_suficiente(self):
        """Prueba que no se puede vender más stock del disponible."""
        # Estado inicial: 10 unidades

        # Intentar vender 15 unidades
        resultado, msg = inventario_logic.registrar_movimiento_inventario(
            producto_id=self.producto_id,
            tipo_movimiento='venta',
            cantidad=15.0,
            costo_unitario=100.0,
            fecha=datetime.date.today().isoformat()
        )

        # La operación debería fallar
        self.assertFalse(resultado)
        self.assertEqual(msg, "Stock insuficiente")

        # El stock no debería haber cambiado
        producto = db_manager.obtener_producto_por_id_db(self.producto_id)
        self.assertAlmostEqual(producto['cantidad_disponible'], 10.0)

    def test_importar_productos_csv(self):
        """Prueba la importación de productos desde un archivo CSV."""
        # El producto de prueba del setUp ya existe.

        # Crear un archivo CSV de prueba
        csv_path = "test_import.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["nombre","sku","descripcion","costo_inicial","cantidad_inicial"])
            writer.writerow(["Producto CSV 1","CSV-001","Desc 1", "10.0", "5"])
            writer.writerow(["Producto CSV 2","CSV-002","Desc 2", "20.0", "10"])

        resumen = inventario_logic.importar_productos_csv(csv_path)

        # Verificar el resumen de la importación
        self.assertEqual(resumen['creados'], 2)
        self.assertEqual(len(resumen['errores']), 0)

        # Verificar que los productos se hayan añadido a la base de datos
        # (1 del setUp + 2 del CSV = 3 total)
        productos_en_db = db_manager.obtener_productos_db()
        self.assertEqual(len(productos_en_db), 3)

        # Limpiar el archivo CSV de prueba
        os.remove(csv_path)

if __name__ == '__main__':
    unittest.main()

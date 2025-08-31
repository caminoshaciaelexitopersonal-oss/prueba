import unittest
import sys
import os
import datetime

# Añadir el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from activos_fijos import logic as activos_fijos_logic
from contabilidad import contabilidad_logic
from database import db_manager

class TestActivosFijosLogic(unittest.TestCase):

    def setUp(self):
        """Configura una base de datos de prueba en un archivo temporal."""
        self.db_path = "test_activos_fijos.db"
        db_manager.DB_CONTABILIDAD_PATH = self.db_path

        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        db_manager.init_db()

        # Añadir cuentas necesarias para las pruebas
        cuentas = [
            ("1540", "Flota y Equipo de Transporte", "Debito", "Activo"),
            ("1592", "Depreciación Acumulada", "Credito", "Activo"),
            ("5160", "Gasto Depreciación", "Debito", "Gasto"),
            ("1105", "Caja", "Debito", "Activo"),
        ]
        for cta in cuentas:
            db_manager.agregar_cuenta_puc(*cta)

        # Registrar un activo de prueba
        self.usuario_id = 1 # Simular un usuario
        success = activos_fijos_logic.registrar_activo(
            nombre="Vehículo de Reparto",
            descripcion="Camioneta 4x2",
            fecha_adquisicion="2023-01-01",
            costo_adquisicion=100000.0,
            valor_residual=10000.0,
            vida_util_meses=60,
            metodo_depreciacion="linea_recta",
            cuenta_activo="1540",
            cuenta_dep_acum="1592",
            cuenta_gasto_dep="5160",
            usuario_id=self.usuario_id,
            cuenta_contrapartida="1105"
        )
        self.assertTrue(success, "La creación del activo de prueba falló.")

    def tearDown(self):
        """Elimina la base de datos de prueba después de cada test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_registro_activo_crea_comprobante(self):
        """Verifica que al registrar un activo se cree el comprobante de adquisición."""
        comprobantes = db_manager.obtener_comprobantes(limit=1, filtro_tipo="Adquisición Activo")
        self.assertEqual(len(comprobantes), 1)

        comprobante = comprobantes[0]
        self.assertEqual(comprobante['total_debito'], 100000.0)
        self.assertEqual(comprobante['total_credito'], 100000.0)

        movimientos = db_manager.obtener_movimientos_por_comprobante(comprobante['id'])
        self.assertEqual(len(movimientos), 2)

        # Verificar débito a la cuenta de activo
        debito = next(m for m in movimientos if m['cuenta_codigo'] == "1540")
        self.assertEqual(debito['debito'], 100000.0)

        # Verificar crédito a la cuenta de contrapartida (caja/banco)
        credito = next(m for m in movimientos if m['cuenta_codigo'] == "1105")
        self.assertEqual(credito['credito'], 100000.0)

    def test_calculo_depreciacion_linea_recta(self):
        """Verifica el cálculo de la depreciación mensual por línea recta."""
        activos = db_manager.obtener_activos_fijos_db()
        self.assertEqual(len(activos), 1)
        activo = activos[0]

        depreciacion_mensual = activos_fijos_logic._calcular_depreciacion_un_mes(activo)

        # (100000 - 10000) / 60 = 90000 / 60 = 1500
        self.assertAlmostEqual(depreciacion_mensual, 1500.0)

    def test_proceso_depreciacion_genera_comprobante(self):
        """Verifica que el proceso de depreciación mensual genera un comprobante correcto."""
        success = activos_fijos_logic.ejecutar_proceso_depreciacion_mensual(2023, 1, self.usuario_id)
        self.assertTrue(success)

        # Verificar que se creó el comprobante de depreciación
        comprobantes = db_manager.obtener_comprobantes(limit=1, filtro_tipo="Depreciación")
        self.assertEqual(len(comprobantes), 1)
        comprobante = comprobantes[0]

        # Verificar que el total del comprobante es correcto
        self.assertAlmostEqual(comprobante['total_debito'], 1500.0)
        self.assertAlmostEqual(comprobante['total_credito'], 1500.0)

        # Verificar los movimientos del comprobante
        movimientos = db_manager.obtener_movimientos_por_comprobante(comprobante['id'])
        self.assertEqual(len(movimientos), 2)

        # Verificar débito a la cuenta de gasto
        gasto = next(m for m in movimientos if m['cuenta_codigo'] == "5160")
        self.assertEqual(gasto['debito'], 1500.0)

        # Verificar crédito a la depreciación acumulada
        dep_acum = next(m for m in movimientos if m['cuenta_codigo'] == "1592")
        self.assertEqual(dep_acum['credito'], 1500.0)

if __name__ == '__main__':
    unittest.main()

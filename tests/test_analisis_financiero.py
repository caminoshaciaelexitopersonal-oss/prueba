import unittest
import sys
import os

# Añadir el directorio raíz del proyecto al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analisis_financiero import logic as analisis_logic

class TestAnalisisFinancieroLogic(unittest.TestCase):

    def setUp(self):
        """Prepara un diccionario de datos de ejemplo para usar en las pruebas."""
        self.datos_ejemplo = {
            "activo_corriente": 1000.0,
            "pasivo_corriente": 500.0,
            "inventario": 200.0,
            "caja_y_bancos": 150.0,
            "cuentas_por_cobrar": 300.0,
            "ventas_a_credito": 2000.0,
            "costo_de_venta": 1200.0,
            "ventas_totales": 2500.0,
            "activo_total": 2000.0,
            "pasivo_total": 800.0,
            "patrimonio_neto": 1200.0,
            "utilidad_bruta": 1300.0, # ventas - costo
            "utilidad_operacional": 500.0,
            "utilidad_neta": 300.0,
            "acciones_en_circulacion": 100.0,
            "precio_por_accion": 15.0,
            "valor_contable_por_accion": 12.0, # patrimonio / acciones
            "capitalizacion_de_mercado": 1500.0, # precio * acciones
            "ventas_anuales": 2500.0,
            "dividendo_anual_por_accion": 1.0,
        }

    def test_ratios_liquidez(self):
        """Prueba los cálculos de los ratios de liquidez."""
        ratios = analisis_logic.calcular_ratios_liquidez(self.datos_ejemplo)
        self.assertAlmostEqual(ratios['ratio_liquidez_general'], 2.0) # 1000 / 500
        self.assertAlmostEqual(ratios['prueba_acida'], 1.6) # (1000 - 200) / 500
        self.assertAlmostEqual(ratios['capital_trabajo_neto'], 500.0) # 1000 - 500

    def test_ratios_endeudamiento(self):
        """Prueba los cálculos de los ratios de endeudamiento."""
        ratios = analisis_logic.calcular_ratios_endeudamiento(self.datos_ejemplo)
        self.assertAlmostEqual(ratios['endeudamiento_total'], 0.4) # 800 / 2000
        self.assertAlmostEqual(ratios['razon_pasivo_patrimonio'], 2/3) # 800 / 1200

    def test_ratios_rentabilidad(self):
        """Prueba los cálculos de los ratios de rentabilidad."""
        ratios = analisis_logic.calcular_ratios_rentabilidad(self.datos_ejemplo)
        self.assertAlmostEqual(ratios['margen_utilidad_neta'], 0.12) # 300 / 2500
        self.assertAlmostEqual(ratios['retorno_sobre_activos_roa'], 0.15) # 300 / 2000
        self.assertAlmostEqual(ratios['retorno_sobre_patrimonio_roe'], 0.25) # 300 / 1200

    def test_division_por_cero(self):
        """Prueba que la división segura maneja los ceros correctamente."""
        datos_cero = {"activo_corriente": 100, "pasivo_corriente": 0}
        ratios = analisis_logic.calcular_ratios_liquidez(datos_cero)
        self.assertEqual(ratios['ratio_liquidez_general'], 0.0)

if __name__ == '__main__':
    unittest.main()

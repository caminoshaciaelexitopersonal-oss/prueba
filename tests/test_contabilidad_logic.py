import unittest
import sys
import os

# Añadir el directorio raíz del proyecto al sys.path
# para que los módulos como 'logic' puedan ser importados.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from contabilidad import contabilidad_logic

class TestContabilidadLogic(unittest.TestCase):

    def test_calcular_iva(self):
        """Prueba el cálculo de IVA con valores estándar."""
        self.assertAlmostEqual(contabilidad_logic.calcular_iva(100.0, 19.0), 19.0)
        self.assertAlmostEqual(contabilidad_logic.calcular_iva(250.0, 5.0), 12.5)
        self.assertAlmostEqual(contabilidad_logic.calcular_iva(100.0, 0.0), 0.0)
        # Prueba con valores negativos, debería devolver 0
        self.assertAlmostEqual(contabilidad_logic.calcular_iva(-100.0, 19.0), 0.0)

    def test_calcular_retencion_fuente_servicios_exitosa(self):
        """Prueba una retención exitosa para servicios generales."""
        # Base para servicios (4 UVT * 47065) = 188260
        base = 200000.0
        concepto = "servicios_generales"
        # 6% de 200000 = 12000
        resultado_esperado = 12000.0
        self.assertAlmostEqual(contabilidad_logic.calcular_retencion_fuente(base, concepto), resultado_esperado)

    def test_calcular_retencion_fuente_compras_base_insuficiente(self):
        """Prueba una retención para compras donde la base no es suficiente."""
        # Base para compras (27 UVT * 47065) = 1270755
        base = 1000000.0
        concepto = "compras_generales"
        # Debería devolver 0 porque la base es menor a la mínima
        self.assertAlmostEqual(contabilidad_logic.calcular_retencion_fuente(base, concepto), 0.0)

    def test_calcular_retencion_fuente_honorarios_sin_base(self):
        """Prueba una retención para honorarios que no tienen base mínima."""
        base = 500000.0
        concepto = "honorarios"
        # 11% de 500000 = 55000
        resultado_esperado = 55000.0
        self.assertAlmostEqual(contabilidad_logic.calcular_retencion_fuente(base, concepto), resultado_esperado)

    def test_calcular_retencion_fuente_concepto_invalido(self):
        """Prueba una retención con un concepto que no existe."""
        base = 500000.0
        concepto = "concepto_fantasma"
        self.assertAlmostEqual(contabilidad_logic.calcular_retencion_fuente(base, concepto), 0.0)

    def test_calcular_retencion_fuente_autoretenedor(self):
        """Prueba que un autorretenedor no tiene retención."""
        base = 500000.0
        concepto = "servicios_generales"
        self.assertAlmostEqual(contabilidad_logic.calcular_retencion_fuente(base, concepto, es_autoretenedor=True), 0.0)

    def test_validar_partida_doble_correcta(self):
        """Prueba la validación de partida doble con un asiento correcto."""
        movimientos = [
            {'debito': 100, 'credito': 0},
            {'debito': 0, 'credito': 100}
        ]
        self.assertTrue(contabilidad_logic.validar_partida_doble(movimientos))

    def test_validar_partida_doble_incorrecta(self):
        """Prueba la validación de partida doble con un asiento incorrecto."""
        movimientos = [
            {'debito': 100, 'credito': 0},
            {'debito': 0, 'credito': 99.9}
        ]
        self.assertFalse(contabilidad_logic.validar_partida_doble(movimientos))

if __name__ == '__main__':
    unittest.main()

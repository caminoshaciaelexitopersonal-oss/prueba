import pytest

def test_import_general():
    """Verifica que el módulo del General de SG-SST se pueda importar."""
    try:
        from gestion_operativa.SG_SST.agents.corps import general_sgsst
        assert general_sgsst is not None
    except ImportError as e:
        pytest.fail(f"No se pudo importar el General de SG-SST: {e}")

def test_import_capitanes():
    """Verifica que todos los módulos de los Capitanes se puedan importar."""
    capitanes = [
        "capitan_matriz_peligros",
        "capitan_planes_procedimientos",
        "capitan_documentacion_formatos",
        "capitan_capacitacion",
        "capitan_incidentes_investigacion",
        "capitan_indicadores_dashboards",
        "capitan_biblioteca_normatividad",
        "capitan_comunicaciones_senaletica"
    ]
    for capitan in capitanes:
        try:
            module = __import__(f"gestion_operativa.SG_SST.agents.corps.capitanes.{capitan}", fromlist=[capitan])
            assert module is not None
        except ImportError as e:
            pytest.fail(f"No se pudo importar el Capitán '{capitan}': {e}")

def test_import_equipos_tacticos():
    """Verifica que todos los módulos de los Equipos Tácticos se puedan importar."""
    equipos = {
        "matriz_peligros": ["teniente", "sargento", "soldado"],
        "planes_procedimientos": ["teniente", "sargento", "soldado"],
        "documentacion_formatos": ["teniente", "sargento", "soldado"],
        "capacitacion": ["teniente", "sargento", "soldado"],
        "incidentes_investigacion": ["teniente", "sargento", "soldado"],
        "indicadores_dashboards": ["teniente", "sargento", "soldado"],
        "biblioteca_normatividad": ["teniente", "sargento", "soldado"],
        "comunicaciones_senaletica": ["teniente", "sargento", "soldado"]
    }
    base_path = "gestion_operativa.SG_SST.agents.corps.capitanes.equipos_tacticos"
    for equipo, rangos in equipos.items():
        for rango in rangos:
            try:
                module_path = f"{base_path}.{equipo}.{rango}"
                module = __import__(module_path, fromlist=[rango])
                assert module is not None
            except ImportError as e:
                pytest.fail(f"No se pudo importar el '{rango}' del equipo '{equipo}': {e}")

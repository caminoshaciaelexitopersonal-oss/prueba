from langchain_core.tools import tool
import datetime

@tool
def registrar_peligro(descripcion: str) -> str:
    """
    Registra un nuevo peligro o riesgo en la base de datos de la matriz IPERC.
    Utiliza esta herramienta para añadir un nuevo peligro identificado.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] PELIGRO REGISTRADO: {descripcion}\n"

        # For this Proof of Concept, we'll use a simple text file as our database.
        with open("sgsst_riesgos.txt", "a") as f:
            f.write(log_entry)

        return f"Éxito: Peligro '{descripcion}' registrado correctamente."
    except Exception as e:
        return f"Error al registrar el peligro: {e}"

@tool
def registrar_inspeccion(area_inspeccionada: str, hallazgos: list[str]) -> str:
    """
    Registra el resultado de una inspección de seguridad en un área específica.
    Utiliza esta herramienta para documentar los hallazgos (conformidades y no conformidades) de una inspección.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hallazgos_str = ", ".join(hallazgos)
        log_entry = f"[{timestamp}] INSPECCION REALIZADA: Area='{area_inspeccionada}', Hallazgos='{hallazgos_str}'\n"

        # For now, we'll use a simple text file as our database for inspections.
        with open("sgsst_inspecciones.txt", "a") as f:
            f.write(log_entry)

        return f"Éxito: Inspección del área '{area_inspeccionada}' registrada correctamente."
    except Exception as e:
        return f"Error al registrar la inspección: {e}"

# Example of how to use the tool directly
if __name__ == '__main__':
    # Test the tool
    print(registrar_peligro.invoke({"descripcion": "Cableado expuesto en pasillo B"}))
    print(registrar_inspeccion.invoke({"area_inspeccionada": "Taller Mecánico", "hallazgos": ["Extintor vencido", "Falta de orden y aseo"]}))

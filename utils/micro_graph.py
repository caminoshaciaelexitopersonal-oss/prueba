import asyncio
from typing import Any, Callable, Dict, Optional

# Constante para representar el final del grafo, igual que en langgraph
END = "__end__"

class MicroGraph:
    """
    Una emulación ligera de langgraph.StateGraph para entornos donde
    la librería original está bloqueada. Utiliza asyncio para orquestar
    la ejecución de nodos.
    """
    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, tuple[Callable, Dict[str, str]]] = {}
        self.entry_point: Optional[str] = None

    def add_node(self, name: str, node_function: Callable):
        """Registra un nuevo nodo en el grafo."""
        if name in self.nodes:
            raise ValueError(f"El nodo '{name}' ya está registrado.")
        self.nodes[name] = node_function
        print(f"[MicroGraph] Nodo '{name}' añadido.")

    def set_entry_point(self, name: str):
        """Define el nodo de inicio del grafo."""
        if name not in self.nodes:
            raise ValueError(f"El punto de entrada '{name}' no es un nodo válido.")
        self.entry_point = name
        print(f"[MicroGraph] Punto de entrada establecido en '{name}'.")

    def add_edge(self, start_node: str, end_node: str):
        """Añade una arista directa entre dos nodos."""
        if start_node not in self.nodes:
            raise ValueError(f"El nodo de inicio '{start_node}' no existe.")
        if end_node not in self.nodes and end_node != END:
            raise ValueError(f"El nodo final '{end_node}' no existe.")
        self.edges[start_node] = end_node
        print(f"[MicroGraph] Arista añadida de '{start_node}' a '{end_node}'.")

    def add_conditional_edge(self, start_node: str, router_function: Callable, path_map: Dict[str, str]):
        """
        Añade una arista condicional que enruta a diferentes nodos
        basado en el resultado de la función de enrutamiento.
        """
        if start_node not in self.nodes:
            raise ValueError(f"El nodo de inicio '{start_node}' no existe.")
        for path_name, node_name in path_map.items():
            if node_name not in self.nodes and node_name != END:
                raise ValueError(f"El nodo '{node_name}' en el mapa de rutas no existe.")
        self.conditional_edges[start_node] = (router_function, path_map)
        print(f"[MicroGraph] Arista condicional añadida desde '{start_node}'.")

    async def run(self, initial_state: Dict[str, Any]):
        """
        Ejecuta el grafo de forma asíncrona, pasando el estado entre nodos.
        """
        if not self.entry_point:
            raise ValueError("El punto de entrada no ha sido establecido.")

        current_node_name = self.entry_point
        state = dict(initial_state)

        while current_node_name != END:
            print(f"[MicroGraph] Ejecutando nodo: '{current_node_name}'")

            node_function = self.nodes.get(current_node_name)
            if not node_function:
                raise ValueError(f"Nodo '{current_node_name}' no encontrado en el grafo.")

            # Ejecuta la lógica del nodo actual
            result = await node_function(state)

            # Actualiza el estado con el resultado del nodo
            if isinstance(result, dict):
                state.update(result)

            # Determina el siguiente nodo
            if current_node_name in self.conditional_edges:
                router_function, path_map = self.conditional_edges[current_node_name]
                next_path = router_function(state)

                if next_path not in path_map:
                    raise ValueError(f"La ruta '{next_path}' devuelta por el enrutador de '{current_node_name}' no es válida. Rutas disponibles: {list(path_map.keys())}")

                current_node_name = path_map[next_path]
                print(f"[MicroGraph] Enrutado condicionalmente a '{current_node_name}'.")

            elif current_node_name in self.edges:
                current_node_name = self.edges[current_node_name]
                print(f"[MicroGraph] Transición directa a '{current_node_name}'.")
            else:
                print(f"[MicroGraph] El nodo '{current_node_name}' no tiene aristas de salida. Finalizando.")
                break

        print("[MicroGraph] Ejecución del grafo finalizada.")
        return state

    def compile(self):
        """
        Método de compatibilidad con la API de langgraph. Devuelve la propia
        instancia, ya que no hay un paso de compilación real.
        """
        print(f"[MicroGraph] Compilación simulada. El grafo está listo para ejecutarse.")
        return self

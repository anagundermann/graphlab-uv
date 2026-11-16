# ==========================================
# DATOS MATEMÁTICOS DE LOS CONCEPTOS
# ==========================================

# Vértices y posiciones del grafo de ejemplo
vertices = [
    {"data": {"id": "A", "label": "A"}, "position": {"x": 60, "y": 70}},
    {"data": {"id": "B", "label": "B"}, "position": {"x": 210, "y": 30}},
    {"data": {"id": "C", "label": "C"}, "position": {"x": 360, "y": 90}},
    {"data": {"id": "D", "label": "D"}, "position": {"x": 210, "y": 210}},
]

# Aristas del grafo de referencia
aristas = [("A", "B"), ("B", "C"), ("A", "C"), ("B", "D"), ("C", "D"), ("A", "D")]


# ==========================================
# DICCIONARIO DE CONCEPTOS
# ==========================================

conceptos = {
    "camino": {
        "nombre": "Camino simple",
        "definicion": (
            "Un camino simple es una sucesión de "
            "vértices distintos en la que cada par "
            "consecutivo está unido por una arista."
        ),
        "explicacion": (
            "Es una forma de ir de un vértice a otro "
            "sin visitar dos veces el mismo vértice."
        ),
        "aristas": [("A", "B"), ("B", "C"), ("C", "D")],
    },
    "grafo": {
        "nombre": "Grafo simple no dirigido",
        "definicion": (
            r"Sea $V$ un conjunto finito y no vacío. "
            r"Un grafo simple no dirigido es un par ordenado "
            r"$$G=(V,E)$$ "
            r"donde "
            r"$$E\subseteq\left\{\{u,v\}:u,v\in V,\;u\neq v\right\}$$ "
            r"El conjunto $V$ contiene los vértices y "
            r"$E$ contiene las aristas."
        ),
        "explicacion": (
            "Es un conjunto de vértices unidos por aristas "
            "que no tienen dirección. No existen lazos "
            "ni aristas paralelas."
        ),
        "aristas": [("A", "B"), ("B", "C"), ("A", "D"), ("C", "D")],
    },
    "ciclo": {
        "nombre": "Ciclo simple",
        "definicion": (
            "Un ciclo simple es un camino cerrado "
            "en el que solamente coinciden el "
            "primer y el último vértice."
        ),
        "explicacion": (
            "Es un recorrido que regresa al punto "
            "de partida sin repetir los vértices "
            "intermedios."
        ),
        "aristas": [("A", "B"), ("B", "C"), ("A", "C")],
    },
    "arbol": {
        "nombre": "Árbol",
        "definicion": (
            "Un árbol es un grafo no dirigido que es conexo y no contiene ciclos."
        ),
        "explicacion": (
            "Todos sus vértices están conectados, "
            "pero no existen caminos alternativos "
            "que formen ciclos."
        ),
        "aristas": [("A", "B"), ("B", "C"), ("B", "D")],
    },
    "matching": {
        "nombre": "Matching",
        "definicion": (
            "Sea G = (V, E). Un matching es un "
            "subconjunto M de E tal que ninguna "
            "pareja de aristas distintas de M "
            "comparte un extremo."
        ),
        "explicacion": (
            "Es una selección de aristas que no comparten vértices entre sí."
        ),
        "aristas": [("A", "B"), ("C", "D")],
    },
}

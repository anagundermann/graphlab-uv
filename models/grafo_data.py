# ==========================================
# GRAFO METRICO - GRAPHLAB UV
# ==========================================

from itertools import permutations


# ==========================================
# 1. VERTICES
# ==========================================

CORRESPONDENCIA = {
    1: "a",
    2: "b",
    3: "c",
    4: "d",
    5: "e",
    6: "f",
    7: "g",
}

VERTICES = ["a", "b", "c", "d", "e", "f", "g"]


# ==========================================
# 2. POSICIONES FIJAS
# ==========================================

# Disposicion exacta elegida para el dibujo:
#
#           b              e
#    a                d              g
#
#            c                   f
#
# Las coordenadas solo afectan el dibujo.


POSICIONES = {
    "a": {"x": 100, "y": 130},
    "b": {"x": 260, "y": 50},
    "d": {"x": 425, "y": 95},
    "e": {"x": 590, "y": 50},
    "g": {"x": 750, "y": 130},
    "c": {"x": 245, "y": 310},
    "f": {"x": 720, "y": 310},
}


# ==========================================
# 3. PESOS DEL GRAFO COMPLETO
# ==========================================

# Adaptacion de la matriz metrica anterior.
# Se conserva la estructura matematica
# mediante un renombramiento de vertices.
#
# Arbol generador minimo esperado:
# a-c, b-c, c-d, d-e, e-g, f-g
#
# Peso total esperado: 64

PESOS_NUMERICOS = {
    (1, 2): 14,
    (1, 3): 10,
    (1, 4): 13,
    (1, 5): 22,
    (1, 6): 29,
    (1, 7): 27,
    (2, 3): 9,
    (2, 4): 14,
    (2, 5): 25,
    (2, 6): 19,
    (2, 7): 23,
    (3, 4): 6,
    (3, 5): 17,
    (3, 6): 20,
    (3, 7): 18,
    (4, 5): 11,
    (4, 6): 21,
    (4, 7): 15,
    (5, 6): 26,
    (5, 7): 12,
    (6, 7): 16,
}


# ==========================================
# 4. CONSTRUIR ARISTAS CON LETRAS
# ==========================================

ARISTAS = [
    (CORRESPONDENCIA[u], CORRESPONDENCIA[v], peso)
    for (u, v), peso in PESOS_NUMERICOS.items()
]


# ==========================================
# 5. DICCIONARIO DE PESOS
# ==========================================

PESOS = {frozenset((u, v)): peso for u, v, peso in ARISTAS}


# ==========================================
# 6. VALIDACIONES
# ==========================================

if len(VERTICES) != 7:
    raise ValueError("El grafo debe tener siete vertices.")

if len(ARISTAS) != 21:
    raise ValueError("El grafo completo debe tener 21 aristas.")

if any(peso <= 0 for _, _, peso in ARISTAS):
    raise ValueError("Los pesos deben ser positivos.")

# Verificar desigualdad triangular.

for a, b, c in permutations(VERTICES, 3):
    peso_ac = PESOS[frozenset((a, c))]
    peso_ab = PESOS[frozenset((a, b))]
    peso_bc = PESOS[frozenset((b, c))]

    if peso_ac > peso_ab + peso_bc:
        raise ValueError(f"Desigualdad triangular incumplida: {a}, {b}, {c}")

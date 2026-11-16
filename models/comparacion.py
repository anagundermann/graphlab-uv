"""Capa matematica pura de comparacion. Sin componentes Dash."""

from models.grafo_data import VERTICES, POSICIONES, ARISTAS
from models import doble_arbol, christofides

PESOS = {frozenset((u, v)): peso for u, v, peso in ARISTAS}

if doble_arbol.PESO_ARBOL != christofides.PESO_ARBOL:
    raise ValueError("Los algoritmos no comparten el mismo arbol minimo.")

PESO_ARBOL = doble_arbol.PESO_ARBOL
PESO_DOBLE = doble_arbol.PESO_DOBLE
PESO_MATCHING = christofides.PESO_MATCHING
PESO_MULTIGRAFO = christofides.PESO_MULTIGRAFO


def datos_comparacion(inicio):
    """Reutilizar resultados autenticos de ambas paginas (no inventar rutas)."""
    datos_doble = doble_arbol.obtener_datos(inicio)
    datos_christofides = christofides.obtener_datos(inicio)

    circuito_doble = datos_doble["circuito"]
    circuito_christofides = datos_christofides["circuito"]
    costo_doble = datos_doble["peso_circuito"]
    costo_christofides = datos_christofides["costo"]

    for circuito, costo in (
        (circuito_doble, costo_doble),
        (circuito_christofides, costo_christofides),
    ):
        if (
            len(circuito) != len(VERTICES) + 1
            or circuito[0] != inicio
            or circuito[-1] != inicio
            or set(circuito[:-1]) != set(VERTICES)
            or len(set(circuito[:-1])) != len(VERTICES)
        ):
            raise ValueError("La comparacion recibio un circuito no hamiltoniano.")
        calculado = sum(
            PESOS[frozenset((u, v))] for u, v in zip(circuito[:-1], circuito[1:])
        )
        if calculado != costo:
            raise ValueError("El costo calculado no coincide con el circuito.")

    return {
        "inicio": inicio,
        "doble": circuito_doble,
        "christofides": circuito_christofides,
        "costo_doble": costo_doble,
        "costo_christofides": costo_christofides,
        "ahorro_doble": sum(a["ahorro"] for a in datos_doble["atajos"]),
        "ahorro_christofides": sum(a["ahorro"] for a in datos_christofides["atajos"]),
        "atajos_doble": len(datos_doble["atajos"]),
        "atajos_christofides": len(datos_christofides["atajos"]),
        "mismo_ciclo": conjunto_aristas(circuito_doble)
        == conjunto_aristas(circuito_christofides),
    }


def conjunto_aristas(circuito):
    """Comparar ciclos no dirigidos, independientemente del sentido de lectura."""
    return {frozenset((u, v)) for u, v in zip(circuito[:-1], circuito[1:])}


# Computar una sola vez los siete escenarios; cada pestaña sigue siendo autónoma.
RESULTADOS = {v: datos_comparacion(v) for v in VERTICES}


# ==========================================
# 2. GRAFOS LADO A LADO
# ==========================================

# Misma geometria relativa para ambos dibujos, escalada para dos columnas.

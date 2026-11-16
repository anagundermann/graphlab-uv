"""Optimo exacto por enumeracion para la instancia pequena de GraphLab."""
from itertools import permutations
from models.grafo_data import ARISTAS, VERTICES
from models import comparacion

PESOS = {frozenset((u, v)): peso for u, v, peso in ARISTAS}


def costo_circuito(circuito):
    return sum(PESOS[frozenset((u, v))] for u, v in zip(circuito[:-1], circuito[1:]))


def obtener_optimo_exacto():
    """Enumeración exhaustiva; adecuada para siete vértices, no para TSP grande."""
    if len(VERTICES) > 9:
        return None, None

    inicio = VERTICES[0]
    restantes = [v for v in VERTICES if v != inicio]
    mejor_peso = None
    mejor_circuito = None

    for orden in permutations(restantes):
        circuito = [inicio, *orden, inicio]
        peso = costo_circuito(circuito)
        if mejor_peso is None or peso < mejor_peso:
            mejor_peso = peso
            mejor_circuito = circuito

    return mejor_peso, mejor_circuito


def es_metrico():
    """Comprobar la desigualdad triangular con los pesos, no las posiciones."""
    for x in VERTICES:
        for y in VERTICES:
            for z in VERTICES:
                if len({x, y, z}) != 3:
                    continue
                if PESOS[frozenset((x, z))] > (
                    PESOS[frozenset((x, y))] + PESOS[frozenset((y, z))]
                ):
                    return False
    return True


COSTO_OPTIMO, CIRCUITO_OPTIMO = obtener_optimo_exacto()
METRICO = es_metrico()
DATOS_A = comparacion.RESULTADOS["a"]
DATOS_E = comparacion.RESULTADOS["e"]


def porcentaje_error(valor, optimo):
    if optimo is None or optimo <= 0:
        return "No disponible"
    return f"{100 * (valor - optimo) / optimo:.2f}".replace(".", ",") + " %"



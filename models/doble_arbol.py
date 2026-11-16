"""Capa matematica pura de doble_arbol. Sin componentes Dash."""

from collections import Counter
from models.grafo_data import VERTICES, POSICIONES, ARISTAS
from models.kruskal import PASOS as PASOS_KRUSKAL

PESOS = {frozenset((u, v)): peso for u, v, peso in ARISTAS}

ESTADOS_KRUSKAL = PASOS_KRUSKAL[-1]["estados"]

ARISTAS_ARBOL = sorted(
    [
        (u, v, peso)
        for u, v, peso in ARISTAS
        if ESTADOS_KRUSKAL.get(f"{u}-{v}") == "aceptada"
    ],
    key=lambda arista: (
        arista[2],
        arista[0],
        arista[1],
    ),
)

if len(ARISTAS_ARBOL) != len(VERTICES) - 1:
    raise ValueError("Kruskal no produjo un arbol generador completo.")

CLAVES_ARBOL = {frozenset((u, v)) for u, v, _ in ARISTAS_ARBOL}

DATOS_ARBOL = {frozenset((u, v)): (u, v, peso) for u, v, peso in ARISTAS_ARBOL}

PESO_ARBOL = sum(peso for _, _, peso in ARISTAS_ARBOL)

PESO_DOBLE = 2 * PESO_ARBOL


def peso_recorrido(recorrido):

    return sum(PESOS[frozenset((u, v))] for u, v in zip(recorrido[:-1], recorrido[1:]))


# ==========================================
# 2. CIRCUITO EULERIANO
# ==========================================


def recorrer_arbol_duplicado(inicio):

    vecinos = {v: [] for v in VERTICES}

    for u, v, peso in ARISTAS_ARBOL:
        vecinos[u].append((v, peso))
        vecinos[v].append((u, peso))

    for v in VERTICES:
        vecinos[v].sort(key=lambda arista: (arista[1], arista[0]))

    recorrido = [inicio]

    def visitar(actual, padre):

        for vecino, _peso in vecinos[actual]:
            if vecino == padre:
                continue

            recorrido.append(vecino)
            visitar(vecino, actual)
            recorrido.append(actual)

    visitar(inicio, None)

    # Cada recorrido usa una copia diferente.

    veces = Counter()
    travesias = []

    for origen, destino in zip(recorrido[:-1], recorrido[1:]):
        clave = frozenset((origen, destino))

        veces[clave] += 1

        u, v, peso = DATOS_ARBOL[clave]

        copia = veces[clave]

        travesias.append(
            {
                "id": f"doble-{u}-{v}-{copia}",
                "origen": origen,
                "destino": destino,
                "peso": peso,
                "copia": copia,
                "arista": f"{u}-{v}",
            }
        )

    if any(veces[clave] != 2 for clave in CLAVES_ARBOL):
        raise ValueError("No se recorrieron las dos copias de cada arista.")

    if recorrido[0] != recorrido[-1]:
        raise ValueError("El circuito euleriano no es cerrado.")

    if peso_recorrido(recorrido) != PESO_DOBLE:
        raise ValueError("El peso euleriano es incorrecto.")

    return recorrido, travesias


# ==========================================
# 3. IDENTIFICAR LOS ATAJOS
# ==========================================


def identificar_atajos(euler, primeras, circuito):

    posiciones = [euler.index(v) for v in primeras]

    posiciones.append(len(euler) - 1)

    atajos = []

    for i, origen in enumerate(primeras):
        destino = circuito[i + 1]

        tramo = euler[posiciones[i] : posiciones[i + 1] + 1]

        if len(tramo) <= 2:
            continue

        costo_tramo = peso_recorrido(tramo)

        costo_directo = PESOS[frozenset((origen, destino))]

        if costo_directo > costo_tramo:
            raise ValueError("Los pesos no cumplen la desigualdad triangular.")

        atajos.append(
            {
                "origen": origen,
                "destino": destino,
                "tramo": tramo,
                "omitidos": tramo[1:-1],
                "costo_tramo": costo_tramo,
                "costo_directo": costo_directo,
                "ahorro": costo_tramo - costo_directo,
            }
        )

    return atajos


# ==========================================
# 4. CONSTRUIR LOS PASOS DEL ALGORITMO
# ==========================================


def obtener_datos(inicio):

    if inicio not in VERTICES:
        raise ValueError("Selecciona un vertice inicial valido.")

    euler, travesias = recorrer_arbol_duplicado(inicio)

    primeras = list(dict.fromkeys(euler))

    circuito = primeras + [inicio]

    atajos = identificar_atajos(euler, primeras, circuito)

    costo = peso_recorrido(circuito)

    if len(primeras) != len(VERTICES):
        raise ValueError("El recorrido no visita todos los vertices.")

    ahorro_total = sum(atajo["ahorro"] for atajo in atajos)

    if costo != PESO_DOBLE - ahorro_total:
        raise ValueError("No coincide el ahorro total de los atajos.")

    pasos = [
        {
            "etapa": "arbol",
            "avance": 0,
            "titulo": "Árbol mínimo de Kruskal",
            "mensaje": (
                f"Elegiste {inicio}. "
                f"Partimos del árbol generador mínimo, "
                f"de peso {PESO_ARBOL}."
            ),
        },
        {
            "etapa": "duplicado",
            "avance": 0,
            "titulo": "Duplicar las aristas",
            "mensaje": (
                "Cada arista se convierte en dos copias. "
                f"El multigrafo pesa {PESO_DOBLE} "
                "y todos sus vértices tienen grado par."
            ),
        },
    ]

    # Recorrido euleriano: una copia por paso.

    for i, travesia in enumerate(travesias, start=1):
        pasos.append(
            {
                "etapa": "euler",
                "avance": i,
                "titulo": (f"Circuito euleriano: arista {i}/{len(travesias)}"),
                "mensaje": (
                    f"{travesia['origen']} → "
                    f"{travesia['destino']}: "
                    f"recorremos la copia "
                    f"{travesia['copia']} de "
                    f"{travesia['arista']}, "
                    f"de peso {travesia['peso']}."
                ),
            }
        )

    # Identificar primeras visitas.

    pasos.append(
        {
            "etapa": "seleccion",
            "avance": 0,
            "titulo": "Conservar las primeras visitas",
            "mensaje": (
                "El circuito euleriano está completo. "
                "Conservamos la primera visita a cada vértice "
                "y omitimos las visitas repetidas."
            ),
        }
    )

    # Mostrar cada atajo por separado.

    for i, atajo in enumerate(atajos, start=1):
        pasos.append(
            {
                "etapa": "atajo",
                "avance": i,
                "titulo": (
                    f"Atajo {i}/{len(atajos)}: {atajo['origen']} - {atajo['destino']}"
                ),
                "mensaje": (
                    "Sustituimos un tramo que contiene "
                    "visitas repetidas por una arista directa."
                ),
            }
        )

    # UN SOLO PASO FINAL.
    # La animacion se reproduce automaticamente.

    pasos.append(
        {
            "etapa": "final",
            "avance": 0,
            "titulo": "Circuito hamiltoniano obtenido",
            "mensaje": (
                "Por lo tanto, hemos encontrado "
                "nuestro circuito hamiltoniano. "
                "La animación lo recorre automáticamente."
            ),
        }
    )

    return {
        "inicio": inicio,
        "euler": euler,
        "travesias": travesias,
        "primeras": primeras,
        "circuito": circuito,
        "atajos": atajos,
        "peso_circuito": costo,
        "pasos": pasos,
    }


DATOS_REFERENCIA = obtener_datos(VERTICES[0])


# ==========================================
# 5. CONSTRUIR LOS ELEMENTOS DEL GRAFO
# ==========================================



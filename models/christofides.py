"""Capa matematica pura de christofides. Sin componentes Dash."""

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
    key=lambda a: (a[2], a[0], a[1]),
)

if len(ARISTAS_ARBOL) != len(VERTICES) - 1:
    raise ValueError("Kruskal no entrego un arbol generador completo.")

PESO_ARBOL = sum(peso for _, _, peso in ARISTAS_ARBOL)
GRADOS_ARBOL = {v: sum(v in (u, w) for u, w, _ in ARISTAS_ARBOL) for v in VERTICES}
IMPARES = [v for v in VERTICES if GRADOS_ARBOL[v] % 2 == 1]

if len(IMPARES) % 2 != 0:
    raise ValueError("El numero de vertices de grado impar debe ser par.")


# ==========================================
# 2. EMPAREJAMIENTO PERFECTO DE PESO MINIMO
# ==========================================


def enumerar_emparejamientos(vertices):
    """Enumerar todos los emparejamientos perfectos de pocos vertices."""
    if not vertices:
        yield []
        return

    primero = vertices[0]
    for i in range(1, len(vertices)):
        segundo = vertices[i]
        restantes = vertices[1:i] + vertices[i + 1 :]
        for otros in enumerar_emparejamientos(restantes):
            yield [(primero, segundo)] + otros


OPCIONES = []
for parejas in enumerar_emparejamientos(IMPARES):
    costo = sum(PESOS[frozenset((u, v))] for u, v in parejas)
    OPCIONES.append({"parejas": parejas, "costo": costo})

OPCIONES.sort(key=lambda o: tuple(tuple(p) for p in o["parejas"]))

MEJOR = min(OPCIONES, key=lambda o: o["costo"])
PAREJAS_MATCHING = MEJOR["parejas"]
PESO_MATCHING = MEJOR["costo"]
PESO_MULTIGRAFO = PESO_ARBOL + PESO_MATCHING

# El grafo auxiliar es el grafo completo sobre los vertices impares.
# Utiliza los pesos del grafo original, NO las distancias sobre el arbol.
ARISTAS_AUXILIAR = [
    (u, v, PESOS[frozenset((u, v))])
    for i, u in enumerate(IMPARES)
    for v in IMPARES[i + 1 :]
]

# Posiciones propias para visualizar K4 de manera ordenada.
# El resto del proyecto conserva sus posiciones originales.
POSICIONES_AUXILIAR = {v: POSICIONES[v].copy() for v in IMPARES}


# ==========================================
# 3. MULTIGRAFO CON ARISTAS DISTINTAS
# ==========================================

# Guardar la orientacion de cada arista para que Cytoscape
# dibuje correctamente las aristas paralelas.
ARISTAS_MULTI = []

for u, v, peso in ARISTAS_ARBOL:
    ARISTAS_MULTI.append(
        {
            "id": f"arbol-{u}-{v}",
            "source": u,
            "target": v,
            "peso": peso,
            "tipo": "arbol",
        }
    )

for u, v in PAREJAS_MATCHING:
    ARISTAS_MULTI.append(
        {
            "id": f"matching-{u}-{v}",
            "source": u,
            "target": v,
            "peso": PESOS[frozenset((u, v))],
            "tipo": "matching",
        }
    )

if len({a["id"] for a in ARISTAS_MULTI}) != len(ARISTAS_MULTI):
    raise ValueError("Los ID del multigrafo deben ser diferentes.")

GRADOS_MULTI = {
    v: sum(v in (a["source"], a["target"]) for a in ARISTAS_MULTI) for v in VERTICES
}

if any(grado % 2 for grado in GRADOS_MULTI.values()):
    raise ValueError("El multigrafo tiene vertices de grado impar.")

PARALELAS = Counter(frozenset((a["source"], a["target"])) for a in ARISTAS_MULTI)


# ==========================================
# 4. CIRCUITO EULERIANO Y ATAJOS
# ==========================================


def circuito_euleriano(inicio):
    """Hierholzer: utiliza cada ID de arista exactamente una vez."""
    adyacencia = {v: [] for v in VERTICES}

    for arista in ARISTAS_MULTI:
        u = arista["source"]
        v = arista["target"]
        adyacencia[u].append((v, arista["peso"], arista["id"]))
        adyacencia[v].append((u, arista["peso"], arista["id"]))

    for v in VERTICES:
        adyacencia[v].sort(key=lambda t: (t[1], t[0], t[2]))

    usados = set()
    pila_vertices = [inicio]
    pila_aristas = []
    salida_vertices = []
    salida_aristas = []

    while pila_vertices:
        actual = pila_vertices[-1]
        disponibles = [
            (vecino, ident)
            for vecino, _peso, ident in adyacencia[actual]
            if ident not in usados
        ]

        if disponibles:
            vecino, ident = disponibles[0]
            usados.add(ident)
            pila_vertices.append(vecino)
            pila_aristas.append(ident)
        else:
            salida_vertices.append(pila_vertices.pop())
            if pila_aristas:
                salida_aristas.append(pila_aristas.pop())

    euler = list(reversed(salida_vertices))
    ids = list(reversed(salida_aristas))

    if len(ids) != len(ARISTAS_MULTI) or len(usados) != len(ARISTAS_MULTI):
        raise ValueError("El recorrido no uso todas las aristas del multigrafo.")
    if euler[0] != inicio or euler[-1] != inicio:
        raise ValueError("El circuito euleriano no se cierra en el origen.")

    aristas_por_id = {a["id"]: a for a in ARISTAS_MULTI}
    pasos = [
        {
            "id": ident,
            "origen": euler[i],
            "destino": euler[i + 1],
            "peso": aristas_por_id[ident]["peso"],
            "tipo": aristas_por_id[ident]["tipo"],
        }
        for i, ident in enumerate(ids)
    ]

    # Validar continuidad real del recorrido y el peso.
    for p in pasos:
        a = aristas_por_id[p["id"]]
        if {p["origen"], p["destino"]} != {a["source"], a["target"]}:
            raise ValueError("Una travesia no corresponde a su arista.")

    if sum(p["peso"] for p in pasos) != PESO_MULTIGRAFO:
        raise ValueError("El circuito no pesa lo mismo que el multigrafo.")

    return euler, pasos


def costo_camino(vertices):
    return sum(PESOS[frozenset((u, v))] for u, v in zip(vertices[:-1], vertices[1:]))


def calcular_atajos(euler, primeras, circuito):
    posiciones = [euler.index(v) for v in primeras]
    posiciones.append(len(euler) - 1)
    atajos = []

    for i, origen in enumerate(primeras):
        tramo = euler[posiciones[i] : posiciones[i + 1] + 1]
        if len(tramo) <= 2:
            continue

        destino = circuito[i + 1]
        anterior = costo_camino(tramo)
        nuevo = PESOS[frozenset((origen, destino))]

        if nuevo > anterior:
            raise ValueError("Los datos no respetan la desigualdad triangular.")

        atajos.append(
            {
                "origen": origen,
                "destino": destino,
                "tramo": tramo,
                "omitidos": tramo[1:-1],
                "original": anterior,
                "directo": nuevo,
                "ahorro": anterior - nuevo,
            }
        )

    return atajos


def obtener_datos(inicio):
    if inicio not in VERTICES:
        raise ValueError("Selecciona un vertice inicial valido.")

    euler, travesias = circuito_euleriano(inicio)
    primeras = list(dict.fromkeys(euler))
    circuito = primeras + [inicio]
    atajos = calcular_atajos(euler, primeras, circuito)
    costo = costo_camino(circuito)

    if len(primeras) != len(VERTICES):
        raise ValueError("No se visitaron todos los vertices.")

    if costo != PESO_MULTIGRAFO - sum(a["ahorro"] for a in atajos):
        raise ValueError("El costo no coincide con los atajos.")

    pasos = [
        {"etapa": "arbol", "avance": 0, "titulo": "Árbol de Kruskal"},
        {"etapa": "impares", "avance": 0, "titulo": "Identificar grados impares"},
        {
            "etapa": "auxiliar",
            "avance": 0,
            "titulo": "Construir el grafo auxiliar completo",
        },
    ]

    for i in range(len(OPCIONES)):
        pasos.append(
            {
                "etapa": "candidato",
                "avance": i,
                "titulo": f"Emparejamiento candidato {i + 1}/{len(OPCIONES)}",
            }
        )

    pasos.extend(
        [
            {
                "etapa": "matching",
                "avance": 0,
                "titulo": "Elegir el emparejamiento mínimo",
            },
            {
                "etapa": "multigrafo",
                "avance": 0,
                "titulo": "Construir el multigrafo euleriano",
            },
        ]
    )

    for i in range(1, len(travesias) + 1):
        pasos.append(
            {
                "etapa": "euler",
                "avance": i,
                "titulo": f"Circuito euleriano: {i}/{len(travesias)} aristas",
            }
        )

    pasos.append(
        {
            "etapa": "seleccion",
            "avance": 0,
            "titulo": "Conservar las primeras visitas",
        }
    )

    for i, atajo in enumerate(atajos, start=1):
        pasos.append(
            {
                "etapa": "atajo",
                "avance": i,
                "titulo": f"Atajo {i}/{len(atajos)}: {atajo['origen']} → {atajo['destino']}",
            }
        )

    pasos.append(
        {"etapa": "final", "avance": 0, "titulo": "Circuito hamiltoniano final"}
    )

    return {
        "inicio": inicio,
        "euler": euler,
        "travesias": travesias,
        "primeras": primeras,
        "circuito": circuito,
        "atajos": atajos,
        "costo": costo,
        "pasos": pasos,
    }


DATOS_REFERENCIA = obtener_datos(VERTICES[0])


# ==========================================
# 5. ELEMENTOS VISUALES DEL GRAFO
# ==========================================



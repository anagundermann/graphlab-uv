"""Capa matematica pura de kruskal. Sin componentes Dash."""

from models.grafo_data import VERTICES, POSICIONES, ARISTAS

def calcular_pasos():

    padre = {v: v for v in VERTICES}
    tamano = {v: 1 for v in VERTICES}

    # Buscar representante de una componente
    def encontrar(v):

        if padre[v] != v:
            padre[v] = encontrar(padre[v])

        return padre[v]

    # Unir dos componentes si son diferentes
    def unir(u, v):

        ru = encontrar(u)
        rv = encontrar(v)

        if ru == rv:
            return False

        if tamano[ru] < tamano[rv]:
            ru, rv = rv, ru

        padre[rv] = ru
        tamano[ru] += tamano[rv]

        return True

    # Obtener las componentes actuales
    def componentes():

        grupos = {}

        for v in VERTICES:
            raiz = encontrar(v)
            grupos.setdefault(raiz, []).append(v)

        return list(grupos.values())

    # Estado inicial
    pasos = [
        {
            "estados": {},
            "actual": None,
            "peso_total": 0,
            "aceptadas": 0,
            "componentes": componentes(),
            "mensaje": (
                "Estado inicial: los siete vértices son "
                "componentes separadas. Kruskal examinará "
                "las aristas por peso creciente."
            ),
        }
    ]

    estados = {}
    peso_total = 0
    aceptadas = 0

    # Ordenar aristas por peso creciente
    aristas_ordenadas = sorted(ARISTAS, key=lambda a: (a[2], a[0], a[1]))

    for u, v, peso in aristas_ordenadas:
        arista_id = f"{u}-{v}"

        if unir(u, v):
            estados[arista_id] = "aceptada"
            peso_total += peso
            aceptadas += 1

            mensaje = (
                f"ACEPTADA {u}-{v} (peso {peso}): "
                "une componentes diferentes "
                "sin formar un ciclo."
            )

        else:
            estados[arista_id] = "rechazada"

            mensaje = (
                f"RECHAZADA {u}-{v} (peso {peso}): "
                "sus extremos ya están conectados; "
                "formaría un ciclo."
            )

        # Guardar una copia del estado
        pasos.append(
            {
                "estados": estados.copy(),
                "actual": arista_id,
                "peso_total": peso_total,
                "aceptadas": aceptadas,
                "componentes": componentes(),
                "mensaje": mensaje,
            }
        )

        # Terminar con |V| - 1 aristas
        if aceptadas == len(VERTICES) - 1:
            break

    if aceptadas != len(VERTICES) - 1:
        raise ValueError("El grafo debe ser conexo.")

    return pasos


PASOS = calcular_pasos()

ULTIMO_PASO = len(PASOS) - 1

ARISTAS_ORDENADAS = sorted(ARISTAS, key=lambda a: (a[2], a[0], a[1]))


# ==========================================
# 3. CONSTRUIR EL GRAFO PARA CYTOSCAPE
# ==========================================



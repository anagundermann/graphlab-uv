"""Christofides: interfaz guiada, sincronizada con el modelo matematico.

La logica de Kruskal, matching, Euler y atajos permanece en models/.
Las posiciones del grafo son fijas y el dibujo nunca anticipa pasos.
"""

from collections import Counter

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import Input, Output, State, ctx, dcc, html

from models.grafo_data import VERTICES, POSICIONES
from models.christofides import (
    ARISTAS_ARBOL,
    ARISTAS_AUXILIAR,
    ARISTAS_MULTI,
    DATOS_REFERENCIA,
    GRADOS_ARBOL,
    GRADOS_MULTI,
    IMPARES,
    MEJOR,
    OPCIONES,
    PAREJAS_MATCHING,
    PESO_ARBOL,
    PESO_MATCHING,
    PESO_MULTIGRAFO,
    PESOS,
    obtener_datos,
)
from models.tsp_optimo import COSTO_OPTIMO


# Las diez etapas tecnicas del modelo se agrupan en siete hitos legibles.
ETAPAS = [
    ("arbol", "AGM"),
    ("impares", "Impares"),
    ("candidato", "Matching"),
    ("multigrafo", "Multigrafo"),
    ("euler", "Euler"),
    ("atajo", "Atajos"),
    ("final", "Resultado"),
]
GRUPOS_ETAPAS = {"auxiliar": "candidato", "matching": "candidato", "seleccion": "euler"}
INDICE_MEJOR = OPCIONES.index(MEJOR)
CANONICAS_ARBOL = {frozenset((u, v)): (u, v, peso) for u, v, peso in ARISTAS_ARBOL}


def segmentos_tras_atajos(datos, cantidad):
    """Caminata real: reemplaza solamente los atajos ya ejecutados."""
    cantidad = max(0, min(cantidad, len(datos["atajos"])))
    euler = datos["euler"]
    posiciones = [euler.index(v) for v in datos["primeras"]]
    posiciones.append(len(euler) - 1)
    indice_atajo = {
        tuple(atajo["tramo"]): (i, atajo)
        for i, atajo in enumerate(datos["atajos"], start=1)
    }
    segmentos = []
    for extremo_a, extremo_b in zip(posiciones[:-1], posiciones[1:]):
        tramo = euler[extremo_a : extremo_b + 1]
        opcion = indice_atajo.get(tuple(tramo))
        if opcion is not None and opcion[0] <= cantidad:
            numero, atajo = opcion
            segmentos.append(
                {
                    "origen": atajo["origen"],
                    "destino": atajo["destino"],
                    "peso": atajo["directo"],
                    "tipo": "atajo",
                    "numero": numero,
                    "id": f"atajo-{numero}",
                }
            )
        else:
            for indice in range(extremo_a, extremo_b):
                travesia = datos["travesias"][indice]
                segmentos.append(
                    {
                        "origen": travesia["origen"],
                        "destino": travesia["destino"],
                        "peso": travesia["peso"],
                        "tipo": travesia["tipo"],
                        "numero": indice + 1,
                        "id": travesia["id"],
                    }
                )
    secuencia = [datos["inicio"]] + [s["destino"] for s in segmentos]
    if any(a["destino"] != b["origen"] for a, b in zip(segmentos[:-1], segmentos[1:])):
        raise ValueError("El recorrido intermedio no tiene continuidad.")
    if secuencia[-1] != datos["inicio"]:
        raise ValueError("El recorrido intermedio no regresa al origen.")
    costo = sum(s["peso"] for s in segmentos)
    ahorro = sum(a["ahorro"] for a in datos["atajos"][:cantidad])
    if costo != PESO_MULTIGRAFO - ahorro:
        raise ValueError("La representacion del atajo no conserva el costo.")
    if cantidad == len(datos["atajos"]) and secuencia != datos["circuito"]:
        raise ValueError("La representacion final no corresponde al ciclo.")
    return segmentos


def arista_visual(
    elementos,
    ident,
    u,
    v,
    peso,
    estado,
    tipo="Arista",
    modo="simple",
    sentido="ninguno",
):
    elementos.append(
        {
            "data": {
                "id": ident,
                "source": u,
                "target": v,
                "peso": peso,
                "arista": f"{u}–{v}",
                "estado": estado,
                "tipo": tipo,
                "modo": modo,
                "sentido": sentido,
            }
        }
    )


def agregar_etiquetas_contextuales(elementos, etapa):
    """Etiquetas de peso en las aristas relevantes, sin duplicar parejas.

    Las aristas del matching se destacan durante la exploracion; en el
    multigrafo y en Euler se identifica una sola vez cada pareja de vertices.
    Los atajos nunca rotulan el AGM de referencia, que aparece atenuado.
    """
    elegidas = {}
    actuales = {"euler-actual", "atajo-actual", "final-actual"}

    for elemento in elementos:
        arista = elemento.get("data", {})
        if "source" not in arista:
            continue

        estado = arista.get("estado")
        if estado == "guia":
            continue
        if etapa in ("candidato", "matching") and estado != "aux-elegida":
            continue

        pareja = frozenset((arista["source"], arista["target"]))
        prioridad = (
            0
            if estado in actuales
            else 1
            if estado in ("aux-elegida", "matching", "atajo")
            else 2
        )
        if pareja not in elegidas or prioridad < elegidas[pareja][0]:
            elegidas[pareja] = (prioridad, elemento)

    for _, elemento in elegidas.values():
        elemento["data"]["etiqueta_peso"] = str(elemento["data"]["peso"])

    return elementos


def construir_elementos(paso, datos, candidato=None, animacion=0):
    """Usa siempre la etapa actual; nunca mezcla resultados futuros."""
    estado = datos["pasos"][paso]
    etapa, avance = estado["etapa"], estado["avance"]
    auxiliar = etapa in ("auxiliar", "candidato", "matching")
    actual = datos["inicio"]
    if etapa == "euler":
        actual = datos["euler"][avance]
    elif etapa == "atajo":
        actual = datos["atajos"][avance - 1]["destino"]
    elif etapa == "final":
        actual = datos["circuito"][min(animacion, len(VERTICES))]

    elementos = []
    for v in VERTICES:
        if auxiliar:
            condicion = "impar" if v in IMPARES else "inactivo"
        elif etapa == "impares" and v in IMPARES:
            condicion = "impar"
        elif v == actual:
            condicion = "actual"
        else:
            condicion = "normal"
        elementos.append(
            {
                "data": {"id": v, "label": v, "estado": condicion},
                "position": POSICIONES[v].copy(),
            }
        )

    if auxiliar:
        if etapa == "matching":
            parejas = PAREJAS_MATCHING
        elif etapa == "candidato":
            indice = avance if candidato is None else candidato
            parejas = OPCIONES[indice]["parejas"]
        else:
            parejas = []
        seleccionadas = {frozenset((u, v)) for u, v in parejas}
        for u, v, peso in ARISTAS_AUXILIAR:
            estado_arista = (
                "aux-elegida"
                if frozenset((u, v)) in seleccionadas
                else ("aux-suave" if seleccionadas else "aux")
            )
            arista_visual(
                elementos,
                f"aux-{u}-{v}",
                u,
                v,
                peso,
                estado_arista,
                tipo="Arista del grafo auxiliar",
            )
        return agregar_etiquetas_contextuales(elementos, etapa)

    if etapa in ("arbol", "impares"):
        for u, v, peso in ARISTAS_ARBOL:
            arista_visual(
                elementos, f"arbol-{u}-{v}", u, v, peso, "arbol", tipo="Árbol mínimo"
            )
        return agregar_etiquetas_contextuales(elementos, etapa)

    if etapa in ("multigrafo", "euler", "seleccion"):
        recorridas = set()
        travesia_actual = None
        if etapa in ("euler", "seleccion"):
            cantidad = avance if etapa == "euler" else len(datos["travesias"])
            recorridas = {t["id"] for t in datos["travesias"][:cantidad]}
        if etapa == "euler":
            travesia_actual = datos["travesias"][avance - 1]
        multiplicidades = Counter(
            frozenset((a["source"], a["target"])) for a in ARISTAS_MULTI
        )
        for arista in ARISTAS_MULTI:
            u, v, ident, tipo = (
                arista["source"],
                arista["target"],
                arista["id"],
                arista["tipo"],
            )
            modo = (
                "arbol"
                if multiplicidades[frozenset((u, v))] > 1 and tipo == "arbol"
                else (
                    "matching" if multiplicidades[frozenset((u, v))] > 1 else "simple"
                )
            )
            visual = (
                tipo
                if etapa == "multigrafo"
                else ("euler-recorrida" if ident in recorridas else "euler-pendiente")
            )
            sentido = "ninguno"
            if travesia_actual and travesia_actual["id"] == ident:
                visual = "euler-actual"
                sentido = "normal" if travesia_actual["origen"] == u else "inverso"
            arista_visual(
                elementos,
                ident,
                u,
                v,
                arista["peso"],
                visual,
                tipo="Matching" if tipo == "matching" else "Árbol mínimo",
                modo=modo,
                sentido=sentido,
            )
        return agregar_etiquetas_contextuales(elementos, etapa)

    if etapa == "atajo":
        # Guía gris tenue del AGM; superpuesto, únicamente el recorrido vigente.
        for u, v, peso in ARISTAS_ARBOL:
            arista_visual(
                elementos,
                f"guia-{u}-{v}",
                u,
                v,
                peso,
                "guia",
                tipo="Árbol de referencia",
            )
        segmentos = segmentos_tras_atajos(datos, avance)
        multiplicidades = Counter(
            frozenset((s["origen"], s["destino"]))
            for s in segmentos
            if s["tipo"] != "atajo"
        )
        for i, s in enumerate(segmentos, start=1):
            origen, destino = s["origen"], s["destino"]
            if s["tipo"] == "atajo":
                arista_visual(
                    elementos,
                    f"ruta-atajo-{i}",
                    origen,
                    destino,
                    s["peso"],
                    "atajo-actual" if s["numero"] == avance else "atajo",
                    tipo="Atajo aplicado",
                )
            else:
                tipo = s["tipo"]
                arista_original = next(a for a in ARISTAS_MULTI if a["id"] == s["id"])
                u, v = arista_original["source"], arista_original["target"]
                modo = tipo if multiplicidades[frozenset((u, v))] > 1 else "simple"
                arista_visual(
                    elementos,
                    f"ruta-euler-{i}",
                    u,
                    v,
                    s["peso"],
                    "tramo-restante",
                    tipo="Recorrido pendiente de atajo",
                    modo=modo,
                )
        return agregar_etiquetas_contextuales(elementos, etapa)

    if etapa == "final":
        total = min(animacion, len(datos["circuito"]) - 1)
        for i, (u, v) in enumerate(zip(datos["circuito"][:-1], datos["circuito"][1:])):
            if i >= total:
                break
            arista_visual(
                elementos,
                f"final-{i}-{u}-{v}",
                u,
                v,
                PESOS[frozenset((u, v))],
                "final-actual" if i == total - 1 else "final",
                tipo="Ciclo hamiltoniano",
            )
    return agregar_etiquetas_contextuales(elementos, etapa)


ESTILO_GRAFO = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "background-color": "#267c9e",
            "color": "#ffffff",
            "text-valign": "center",
            "text-halign": "center",
            "width": 45,
            "height": 45,
            "font-size": 17,
            "font-weight": "bold",
            "border-width": 2,
            "border-color": "#ffffff",
        },
    },
    {
        "selector": 'node[estado = "actual"]',
        "style": {
            "background-color": "#196d82",
            "border-width": 4,
            "border-color": "#acd6dc",
        },
    },
    {
        "selector": 'node[estado = "impar"]',
        "style": {
            "background-color": "#7760a2",
            "border-width": 3,
            "border-color": "#dfd5f0",
        },
    },
    {
        "selector": 'node[estado = "inactivo"]',
        "style": {
            "background-color": "#d2dbe1",
            "color": "#748b99",
            "opacity": 0.32,
        },
    },
    {"selector": "edge", "style": {"width": 3, "line-color": "#9fb3c1"}},
    {
        "selector": 'edge[estado = "arbol"]',
        "style": {
            "width": 5,
            "line-color": "#238a80",
        },
    },
    {
        "selector": 'edge[estado = "aux"]',
        "style": {
            "width": 3.2,
            "line-color": "#8096a5",
            "opacity": 0.75,
        },
    },
    {
        "selector": 'edge[estado = "aux-suave"]',
        "style": {
            "width": 2.5,
            "line-color": "#afbdc7",
            "opacity": 0.27,
        },
    },
    {
        "selector": 'edge[estado = "aux-elegida"]',
        "style": {
            "width": 6,
            "line-color": "#7760a2",
            "opacity": 1,
        },
    },
    {
        "selector": 'edge[modo = "arbol"]',
        "style": {
            "curve-style": "unbundled-bezier",
            "control-point-distances": -25,
            "control-point-weights": 0.5,
        },
    },
    {
        "selector": 'edge[modo = "matching"]',
        "style": {
            "curve-style": "unbundled-bezier",
            "control-point-distances": 25,
            "control-point-weights": 0.5,
        },
    },
    {
        "selector": 'edge[estado = "matching"]',
        "style": {
            "width": 5,
            "line-color": "#7760a2",
        },
    },
    {
        "selector": 'edge[estado = "euler-pendiente"]',
        "style": {
            "width": 3.5,
            "line-color": "#c58a35",
            "line-style": "dashed",
            "opacity": 0.85,
        },
    },
    {
        "selector": 'edge[estado = "euler-recorrida"]',
        "style": {
            "width": 4.6,
            "line-color": "#238a80",
        },
    },
    {
        "selector": 'edge[estado = "euler-actual"]',
        "style": {
            "width": 6.4,
            "line-color": "#cc6570",
        },
    },
    {
        "selector": 'edge[estado = "euler-actual"][sentido = "normal"]',
        "style": {
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#cc6570",
            "arrow-scale": 1.05,
        },
    },
    {
        "selector": 'edge[estado = "euler-actual"][sentido = "inverso"]',
        "style": {
            "source-arrow-shape": "triangle",
            "source-arrow-color": "#cc6570",
            "arrow-scale": 1.05,
        },
    },
    {
        "selector": 'edge[estado = "guia"]',
        "style": {
            "width": 2,
            "line-color": "#bdcbd4",
            "opacity": 0.15,
        },
    },
    {
        "selector": 'edge[estado = "tramo-restante"]',
        "style": {
            "width": 4,
            "line-color": "#589d96",
            "opacity": 0.85,
        },
    },
    {
        "selector": 'edge[estado = "atajo"]',
        "style": {
            "width": 5,
            "line-color": "#7760a2",
        },
    },
    {
        "selector": 'edge[estado = "atajo-actual"]',
        "style": {
            "width": 6.5,
            "line-color": "#7760a2",
            "line-style": "dashed",
        },
    },
    {
        "selector": 'edge[estado = "final"]',
        "style": {
            "width": 5,
            "line-color": "#416b86",
        },
    },
    {
        "selector": 'edge[estado = "final-actual"]',
        "style": {
            "width": 6.5,
            "line-color": "#275b7c",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#275b7c",
            "arrow-scale": 1.05,
        },
    },
]


ESTILO_PESOS = [
    {
        "selector": "edge[etiqueta_peso]",
        "style": {
            "label": "data(etiqueta_peso)",
            "color": "#294d67",
            "font-size": 12,
            "font-weight": 700,
            "text-rotation": "none",
            "text-background-color": "#ffffff",
            "text-background-opacity": 0.96,
            "text-background-shape": "round-rectangle",
            "text-background-padding": "3px",
            "text-border-width": 1,
            "text-border-color": "#dce5ec",
            "text-border-opacity": 0.9,
        },
    },
]


def etapas_visuales(etapa):
    grupo = GRUPOS_ETAPAS.get(etapa, etapa)
    indice = next(i for i, (clave, _) in enumerate(ETAPAS) if clave == grupo)
    return [
        html.Span(
            etiqueta,
            className=(
                "gl-ch-etapa gl-ch-etapa-actual"
                if i == indice
                else "gl-ch-etapa gl-ch-etapa-lista"
                if i < indice
                else "gl-ch-etapa"
            ),
        )
        for i, (_, etiqueta) in enumerate(ETAPAS)
    ]


def metrica(nombre, valor):
    return html.Div(
        [
            html.Span(nombre, className="gl-ch-metrica-label"),
            html.Strong(str(valor), className="gl-ch-metrica-valor"),
        ],
        className="gl-ch-metrica",
    )


def secuencia(vertices, marcar_repetidos=False):
    usados = set()
    elementos = []
    for i, v in enumerate(vertices):
        if i:
            elementos.append(html.Span("→", className="gl-ch-flecha"))
        repetido = marcar_repetidos and v in usados and i != len(vertices) - 1
        elementos.append(
            html.Span(
                v,
                className=(
                    "gl-ch-vertice gl-ch-repetido" if repetido else "gl-ch-vertice"
                ),
            )
        )
        usados.add(v)
    return html.Div(elementos, className="gl-ch-secuencia")


def panel_estado(paso, datos, candidato=None, animacion=0):
    estado = datos["pasos"][paso]
    etapa, avance = estado["etapa"], estado["avance"]
    partes = [
        html.Span("ETAPA ACTUAL", className="gl-ch-eyebrow"),
        html.H3(estado["titulo"], className="gl-ch-panel-titulo"),
    ]

    if etapa == "arbol":
        partes.extend(
            [
                html.P(
                    "Partimos del mismo árbol generador mínimo construido con Kruskal.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("Peso AGM", PESO_ARBOL),
                        metrica("Aristas", "6 / 6"),
                        metrica("Origen Euler", datos["inicio"]),
                    ],
                    className="gl-ch-metricas",
                ),
                html.H4("Aristas del árbol", className="gl-ch-seccion"),
                html.Div(
                    [
                        html.Span(f"{u}–{v} · {p}", className="gl-ch-chip")
                        for u, v, p in ARISTAS_ARBOL
                    ],
                    className="gl-ch-chips",
                ),
                html.P(
                    "Un árbol conecta todos los vértices sin ciclos; no es todavía un ciclo hamiltoniano.",
                    className="gl-ch-nota",
                ),
            ]
        )

    elif etapa == "impares":
        partes.extend(
            [
                html.P(
                    "Un vértice es impar si tiene un número impar de aristas incidentes.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("Impares", ", ".join(IMPARES)),
                        metrica("Cantidad", len(IMPARES)),
                    ],
                    className="gl-ch-metricas",
                ),
                html.H4("Grados en el AGM", className="gl-ch-seccion"),
                html.Div(
                    [
                        html.Span(
                            f"{v}: {GRADOS_ARBOL[v]}",
                            className=(
                                "gl-ch-chip gl-ch-chip-impar"
                                if v in IMPARES
                                else "gl-ch-chip"
                            ),
                        )
                        for v in VERTICES
                    ],
                    className="gl-ch-chips",
                ),
                html.P(
                    "Los cuatro vértices morados deben emparejarse para volver pares sus grados.",
                    className="gl-ch-nota",
                ),
            ]
        )

    elif etapa == "auxiliar":
        partes.extend(
            [
                html.P(
                    "Construimos un grafo completo sobre los cuatro vértices de grado impar.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("Vértices impares", len(IMPARES)),
                        metrica("Aristas posibles", len(ARISTAS_AUXILIAR)),
                    ],
                    className="gl-ch-metricas",
                ),
                html.P(
                    "Los otros tres vértices se atenúan para mantener intacta la geometría del grafo.",
                    className="gl-ch-nota",
                ),
                html.P(
                    "Cada arista conserva el peso original, no una distancia medida sobre el árbol.",
                    className="gl-ch-nota",
                ),
            ]
        )

    elif etapa == "candidato":
        indice = avance if candidato is None else candidato
        opcion = OPCIONES[indice]
        partes.extend(
            [
                html.P(
                    "Selecciona una de las tres alternativas: el dibujo cambiará sin adelantar el algoritmo.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("Alternativa", f"{indice + 1} / {len(OPCIONES)}"),
                        metrica("Costo del candidato", opcion["costo"]),
                    ],
                    className="gl-ch-metricas",
                ),
                html.H4("Emparejamiento mostrado", className="gl-ch-seccion"),
                html.Div(
                    [
                        html.Span(
                            f"{u}–{v} · {PESOS[frozenset((u, v))]}",
                            className="gl-ch-chip gl-ch-chip-impar",
                        )
                        for u, v in opcion["parejas"]
                    ],
                    className="gl-ch-chips",
                ),
                html.P(
                    "Esta elección es solo una exploración. El algoritmo escogerá el costo mínimo en la siguiente etapa.",
                    className="gl-ch-nota",
                ),
            ]
        )

    elif etapa == "matching":
        partes.extend(
            [
                html.P(
                    "Se compararon todos los emparejamientos perfectos; elegimos el de menor peso.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("Matching mínimo", PESO_MATCHING),
                        metrica("Alternativas", len(OPCIONES)),
                    ],
                    className="gl-ch-metricas",
                ),
                html.H4("Aristas seleccionadas", className="gl-ch-seccion"),
                html.Div(
                    [
                        html.Span(
                            f"{u}–{v} · {PESOS[frozenset((u, v))]}",
                            className="gl-ch-chip gl-ch-chip-impar",
                        )
                        for u, v in PAREJAS_MATCHING
                    ],
                    className="gl-ch-chips",
                ),
                html.P(
                    "Este matching agrega una arista incidente a cada impar; el algoritmo no utiliza una alternativa más costosa.",
                    className="gl-ch-nota",
                ),
            ]
        )

    elif etapa == "multigrafo":
        partes.extend(
            [
                html.P(
                    "Añadimos las dos aristas moradas del matching al AGM verde.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("AGM", PESO_ARBOL),
                        metrica("Matching", PESO_MATCHING),
                        metrica("Multigrafo", PESO_MULTIGRAFO),
                    ],
                    className="gl-ch-metricas",
                ),
                html.Div(
                    f"{PESO_ARBOL} + {PESO_MATCHING} = {PESO_MULTIGRAFO}",
                    className="gl-ch-formula",
                ),
                html.H4("Grados del multigrafo", className="gl-ch-seccion"),
                html.Div(
                    [
                        html.Span(f"{v}: {GRADOS_MULTI[v]}", className="gl-ch-chip")
                        for v in VERTICES
                    ],
                    className="gl-ch-chips",
                ),
                html.P(
                    "Todos los grados son pares y el multigrafo es conexo: existe un circuito euleriano."
                    " La arista a–c aparece en dos copias distintas.",
                    className="gl-ch-nota",
                ),
            ]
        )

    elif etapa == "euler":
        usadas = datos["travesias"][:avance]
        t = usadas[-1]
        costo = sum(x["peso"] for x in usadas)
        partes.extend(
            [
                html.P(
                    "Recorremos cada arista del multigrafo una sola vez, distinguiendo las copias.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica(
                            "Aristas recorridas", f"{avance}/{len(datos['travesias'])}"
                        ),
                        metrica("Costo acumulado", costo),
                        metrica("Costo total", PESO_MULTIGRAFO),
                    ],
                    className="gl-ch-metricas",
                ),
                html.Div(
                    [
                        html.Strong(f"{t['origen']} → {t['destino']}"),
                        html.Span(f"{t['tipo'].capitalize()} · Peso {t['peso']}"),
                    ],
                    className="gl-ch-linea-actual",
                ),
                html.H4("Recorrido acumulado", className="gl-ch-seccion"),
                secuencia(datos["euler"][: avance + 1]),
            ]
        )

    elif etapa == "seleccion":
        partes.extend(
            [
                html.P(
                    "Conservamos la primera visita a cada vértice y el retorno final al origen.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("Visitas", len(datos["euler"])),
                        metrica("Vértices distintos", len(VERTICES)),
                    ],
                    className="gl-ch-metricas",
                ),
                html.H4("Repeticiones del circuito Euler", className="gl-ch-seccion"),
                secuencia(datos["euler"], marcar_repetidos=True),
                html.P(
                    "Los vértices tachados no desaparecen todavía del dibujo; los eliminamos con los atajos.",
                    className="gl-ch-nota",
                ),
            ]
        )

    elif etapa == "atajo":
        atajo = datos["atajos"][avance - 1]
        segmentos = segmentos_tras_atajos(datos, avance)
        costo = sum(s["peso"] for s in segmentos)
        ahorro = sum(a["ahorro"] for a in datos["atajos"][:avance])
        recorrido = [datos["inicio"]] + [s["destino"] for s in segmentos]
        partes.extend(
            [
                html.P(
                    "Sustituimos únicamente el tramo indicado; las aristas futuras no se dibujan todavía.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("Costo vigente", costo),
                        metrica("Ahorro acumulado", ahorro),
                        metrica("Atajos", f"{avance}/{len(datos['atajos'])}"),
                    ],
                    className="gl-ch-metricas",
                ),
                html.H4("Tramo reemplazado", className="gl-ch-seccion"),
                secuencia(atajo["tramo"]),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span("Arista directa"),
                                html.Strong(f"{atajo['origen']} → {atajo['destino']}"),
                            ]
                        ),
                        html.Div(
                            [
                                html.Span("Ahorro"),
                                html.Strong(
                                    f"{atajo['original']} − {atajo['directo']} = {atajo['ahorro']}"
                                ),
                            ]
                        ),
                    ],
                    className="gl-ch-calculo",
                ),
                html.H4("Recorrido vigente", className="gl-ch-seccion"),
                secuencia(recorrido),
                html.P(
                    f"Costo: {PESO_MULTIGRAFO} − {ahorro} = {costo}.",
                    className="gl-ch-nota",
                ),
            ]
        )

    elif etapa == "final":
        cantidad = min(animacion, len(datos["circuito"]) - 1)
        total = len(datos["circuito"]) - 1
        completo = cantidad >= total
        partes.extend(
            [
                html.P(
                    "Se dibuja el ciclo hamiltoniano, arista por arista.",
                    className="gl-ch-mensaje",
                ),
                html.Div(
                    [
                        metrica("Costo final", datos["costo"] if completo else "—"),
                        metrica("Aristas dibujadas", f"{cantidad}/{total}"),
                        metrica("Multigrafo", PESO_MULTIGRAFO),
                    ],
                    className="gl-ch-metricas",
                ),
                html.H4("Recorrido hamiltoniano", className="gl-ch-seccion"),
                secuencia(datos["circuito"][: cantidad + 1]),
            ]
        )
        if completo:
            es_optimo = datos["costo"] == COSTO_OPTIMO
            partes.append(
                html.Div(
                    [
                        html.Strong("Ciclo hamiltoniano construido"),
                        html.P(
                            f"Se visitaron {len(VERTICES)} vértices exactamente una vez y se volvió al origen. "
                            f"Costo: {datos['costo']} ≤ {PESO_MULTIGRAFO}."
                        ),
                        html.P(
                            (
                                f"Para este origen coincide con el óptimo exacto ({COSTO_OPTIMO}). "
                                if es_optimo
                                else f"El óptimo exacto de esta instancia es {COSTO_OPTIMO}. "
                            )
                            + "En general, Christofides tiene una garantía de aproximación 3/2 "
                            "para el TSP métrico; no siempre alcanza el óptimo."
                        ),
                    ],
                    className="gl-ch-conclusion",
                )
            )

    return partes


LEYENDAS = {
    "arbol": [("verde", "Árbol mínimo")],
    "impares": [("verde", "Árbol mínimo"), ("violeta", "Vértices impares")],
    "auxiliar": [
        ("gris", "Aristas del grafo auxiliar"),
        ("violeta", "Vértices impares"),
    ],
    "candidato": [("violeta", "Emparejamiento mostrado"), ("gris", "Otras aristas")],
    "matching": [("violeta", "Emparejamiento mínimo")],
    "multigrafo": [("verde", "Árbol mínimo"), ("violeta", "Matching agregado")],
    "euler": [("verde", "Recorrida"), ("rojo", "Actual"), ("ambar", "Pendiente")],
    "seleccion": [("verde", "Circuito euleriano")],
    "atajo": [("violeta", "Atajo aplicado"), ("verde", "Recorrido restante")],
    "final": [("azul", "Ciclo hamiltoniano")],
}


def leyenda(etapa):
    return [
        html.Span([html.I(className=f"gl-ch-punto gl-ch-punto-{color}"), texto])
        for color, texto in LEYENDAS[etapa]
    ]


def crear_pagina(paso_inicial=0, inicio_inicial="a"):
    inicio_inicial = inicio_inicial if inicio_inicial in VERTICES else VERTICES[0]
    datos = obtener_datos(inicio_inicial)
    paso_inicial = max(0, min(len(datos["pasos"]) - 1, int(paso_inicial)))
    etapa_inicial = datos["pasos"][paso_inicial]["etapa"]
    candidato_inicial = (
        datos["pasos"][paso_inicial]["avance"] if etapa_inicial == "candidato" else 0
    )
    ultimo = len(datos["pasos"]) - 1
    return html.Div(
        [
            dcc.Store(id="christofides-paso", data=paso_inicial),
            dcc.Store(id="christofides-origen-previo", data=inicio_inicial),
            dcc.Store(id="christofides-animacion", data=0),
            dcc.Store(id="christofides-candidato", data=candidato_inicial),
            dcc.Interval(
                id="christofides-intervalo", interval=560, n_intervals=0, disabled=True
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "ALGORITMO DE APROXIMACIÓN", className="gl-ch-eyebrow"
                            ),
                            html.H2("Christofides · TSP métrico"),
                            html.P(
                                "Del árbol mínimo a un ciclo hamiltoniano mediante matching y recorrido euleriano."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("7 vértices"),
                            html.Span(f"AGM: {PESO_ARBOL}"),
                            html.Span("Matching de peso mínimo"),
                            html.Button(
                                "Ver código Python",
                                id={
                                    "type": "graphlab-abrir-codigo",
                                    "index": "christofides",
                                },
                                n_clicks=0,
                                type="button",
                                className="gl-ver-codigo",
                            ),
                        ],
                        className="gl-ch-etiquetas",
                    ),
                ],
                className="gl-ch-intro",
            ),
            html.Div(
                etapas_visuales(datos["pasos"][paso_inicial]["etapa"]),
                id="christofides-etapas",
                className="gl-ch-etapas",
            ),
            html.Div(
                [
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3("Transformación del grafo"),
                                            html.P(
                                                "Las posiciones de los vértices no cambian."
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            dbc.Checklist(
                                                id="christofides-mostrar-pesos",
                                                options=[
                                                    {
                                                        "label": "Mostrar pesos",
                                                        "value": "mostrar",
                                                    }
                                                ],
                                                value=[],
                                                switch=True,
                                                className="gl-ch-switch-pesos",
                                            ),
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "Vértice inicial",
                                                        htmlFor="christofides-inicio",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="christofides-inicio",
                                                        options=[
                                                            {"label": v, "value": v}
                                                            for v in VERTICES
                                                        ],
                                                        value=inicio_inicial,
                                                        clearable=False,
                                                        searchable=False,
                                                    ),
                                                ],
                                                className="gl-ch-selector",
                                            ),
                                        ],
                                        className="gl-ch-opciones-grafo",
                                    ),
                                ],
                                className="gl-ch-grafo-cabecera",
                            ),
                            html.Div(
                                [
                                    cyto.Cytoscape(
                                        id="christofides-grafo",
                                        layout={
                                            "name": "preset",
                                            "fit": True,
                                            "padding": 40,
                                        },
                                        elements=construir_elementos(
                                            paso_inicial,
                                            datos,
                                            candidato=candidato_inicial
                                            if etapa_inicial == "candidato"
                                            else None,
                                        ),
                                        stylesheet=ESTILO_GRAFO,
                                        style={"width": "100%", "height": "410px"},
                                        className="gl-ch-grafo",
                                        autoungrabify=True,
                                        clearOnUnhover=True,
                                    ),
                                    html.Div(
                                        id="christofides-tooltip-arista",
                                        className="gl-ch-tooltip-arista",
                                    ),
                                ],
                                className="gl-ch-grafo-marco",
                            ),
                            html.Div(
                                leyenda(datos["pasos"][paso_inicial]["etapa"]),
                                id="christofides-leyenda",
                                className="gl-ch-leyenda",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Strong(
                                                f"Paso {paso_inicial} de {ultimo}",
                                                id="christofides-contador",
                                            ),
                                            html.Div(
                                                html.Div(
                                                    id="christofides-progreso",
                                                    className="gl-ch-progreso-valor",
                                                    style={
                                                        "width": f"{100 * paso_inicial / ultimo:.1f}%"
                                                    },
                                                ),
                                                className="gl-ch-progreso-pista",
                                            ),
                                        ],
                                        className="gl-ch-avance",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Button(
                                                "← Anterior",
                                                id="christofides-anterior",
                                                n_clicks=0,
                                                color="outline-secondary",
                                                disabled=(paso_inicial == 0),
                                            ),
                                            dbc.Button(
                                                "→ Siguiente",
                                                id="christofides-siguiente",
                                                n_clicks=0,
                                                color="primary",
                                                disabled=(paso_inicial == ultimo),
                                            ),
                                            dbc.Button(
                                                "↻ Reiniciar",
                                                id="christofides-reiniciar",
                                                n_clicks=0,
                                                color="outline-secondary",
                                            ),
                                            dbc.Button(
                                                "▶ Reproducir ciclo",
                                                id="christofides-reproducir",
                                                n_clicks=0,
                                                color="outline-primary",
                                                disabled=True,
                                                style={"display": "none"},
                                            ),
                                        ],
                                        className="gl-ch-botones",
                                    ),
                                ],
                                className="gl-ch-controles",
                            ),
                        ],
                        className="gl-ch-tarjeta gl-ch-panel-grafo",
                    ),
                    html.Aside(
                        [
                            html.Div(
                                panel_estado(
                                    paso_inicial,
                                    datos,
                                    candidato=candidato_inicial
                                    if etapa_inicial == "candidato"
                                    else None,
                                ),
                                id="christofides-panel-estado",
                            ),
                            html.Div(
                                [
                                    html.H4(
                                        "Comparar emparejamientos",
                                        className="gl-ch-seccion",
                                    ),
                                    html.P(
                                        "Elige una alternativa: solo cambia la vista previa del grafo.",
                                        className="gl-ch-nota",
                                    ),
                                    *[
                                        html.Button(
                                            [
                                                html.Span(
                                                    f"Opción {i + 1}",
                                                    className="gl-ch-opcion-indice",
                                                ),
                                                html.Span(
                                                    " + ".join(
                                                        f"{u}–{v}"
                                                        for u, v in opcion["parejas"]
                                                    ),
                                                    className="gl-ch-opcion-pares",
                                                ),
                                                html.Strong(
                                                    str(opcion["costo"]),
                                                    className="gl-ch-opcion-costo",
                                                ),
                                                html.Span(
                                                    "Mínimo"
                                                    if i == INDICE_MEJOR
                                                    else "",
                                                    className="gl-ch-opcion-badge",
                                                ),
                                            ],
                                            id=f"christofides-opcion-{i}",
                                            n_clicks=0,
                                            type="button",
                                            className="gl-ch-opcion gl-ch-opcion-activa"
                                            if etapa_inicial == "candidato"
                                            and i == candidato_inicial
                                            else "gl-ch-opcion",
                                        )
                                        for i, opcion in enumerate(OPCIONES)
                                    ],
                                ],
                                id="christofides-explorador",
                                className="gl-ch-explorador"
                                if etapa_inicial == "candidato"
                                else "gl-ch-explorador gl-ch-oculto",
                            ),
                        ],
                        className="gl-ch-tarjeta gl-ch-panel-estado",
                    ),
                ],
                className="gl-ch-distribucion",
            ),
            html.P(
                "Mismo grafo métrico que Kruskal y Doble árbol. Los pesos no dependen de "
                "la ubicación de los vértices.",
                className="gl-ch-nota-final",
            ),
        ],
        className="pagina-algoritmo pagina-christofides",
    )


def registrar_callbacks(app):
    @app.callback(
        Output("christofides-paso", "data"),
        Output("christofides-origen-previo", "data"),
        Output("christofides-animacion", "data"),
        Output("christofides-candidato", "data"),
        Output("christofides-grafo", "elements"),
        Output("christofides-etapas", "children"),
        Output("christofides-panel-estado", "children"),
        Output("christofides-leyenda", "children"),
        Output("christofides-contador", "children"),
        Output("christofides-progreso", "style"),
        Output("christofides-anterior", "disabled"),
        Output("christofides-siguiente", "disabled"),
        Output("christofides-reproducir", "disabled"),
        Output("christofides-reproducir", "style"),
        Output("christofides-intervalo", "disabled"),
        Output("christofides-explorador", "className"),
        *[
            Output(f"christofides-opcion-{i}", "className")
            for i in range(len(OPCIONES))
        ],
        Input("christofides-anterior", "n_clicks"),
        Input("christofides-siguiente", "n_clicks"),
        Input("christofides-reiniciar", "n_clicks"),
        Input("christofides-reproducir", "n_clicks"),
        Input("christofides-inicio", "value"),
        Input("christofides-intervalo", "n_intervals"),
        *[Input(f"christofides-opcion-{i}", "n_clicks") for i in range(len(OPCIONES))],
        State("christofides-paso", "data"),
        State("christofides-animacion", "data"),
        State("christofides-candidato", "data"),
        State("christofides-origen-previo", "data"),
    )
    def actualizar_christofides(
        anterior,
        siguiente,
        reiniciar,
        reproducir,
        inicio,
        intervalos,
        *opciones_y_estados,
    ):
        numero_opciones = len(OPCIONES)
        paso, animacion, candidato, origen_previo = opciones_y_estados[numero_opciones:]
        if inicio not in VERTICES:
            inicio = VERTICES[0]
        datos = obtener_datos(inicio)
        ultimo = len(datos["pasos"]) - 1
        total = len(datos["circuito"]) - 1
        paso = max(0, min(ultimo, paso if isinstance(paso, int) else 0))
        animacion = max(0, min(total, animacion if isinstance(animacion, int) else 0))
        candidato = max(
            0, min(numero_opciones - 1, candidato if isinstance(candidato, int) else 0)
        )
        activador = ctx.triggered_id

        if (activador == "christofides-reiniciar" and reiniciar) or (
            activador == "christofides-inicio" and inicio != origen_previo
        ):
            paso, animacion, candidato = 0, 0, 0
        elif activador == "christofides-anterior" and anterior:
            paso, animacion = max(0, paso - 1), 0
        elif activador == "christofides-siguiente" and siguiente:
            paso, animacion = min(ultimo, paso + 1), 0
        elif activador == "christofides-reproducir" and reproducir and paso == ultimo:
            animacion = 0
        elif activador == "christofides-intervalo" and intervalos and paso == ultimo:
            animacion = min(total, animacion + 1)
        elif (
            isinstance(activador, str)
            and activador.startswith("christofides-opcion-")
            and ctx.triggered[0].get("value")
        ):
            nuevo = int(activador.rsplit("-", 1)[-1])
            if datos["pasos"][paso]["etapa"] == "candidato":
                candidato = nuevo

        etapa = datos["pasos"][paso]["etapa"]
        if (
            activador in ("christofides-anterior", "christofides-siguiente")
            and etapa == "candidato"
        ):
            candidato = datos["pasos"][paso]["avance"]
        final = paso == ultimo
        animar = final and animacion < total
        elegido = candidato if etapa == "candidato" else None
        clases = [
            "gl-ch-opcion gl-ch-opcion-activa"
            if etapa == "candidato" and i == candidato
            else "gl-ch-opcion"
            for i in range(numero_opciones)
        ]
        return (
            paso,
            inicio,
            animacion,
            candidato,
            construir_elementos(paso, datos, candidato=elegido, animacion=animacion),
            etapas_visuales(etapa),
            panel_estado(paso, datos, candidato=elegido, animacion=animacion),
            leyenda(etapa),
            f"Paso {paso} de {ultimo}",
            {"width": f"{100 * paso / ultimo:.1f}%"},
            paso == 0,
            final,
            not (final and not animar),
            {"display": "inline-flex" if final else "none"},
            not animar,
            "gl-ch-explorador"
            if etapa == "candidato"
            else "gl-ch-explorador gl-ch-oculto",
            *clases,
        )

    @app.callback(
        Output("christofides-tooltip-arista", "children"),
        Output("christofides-tooltip-arista", "className"),
        Input("christofides-grafo", "mouseoverEdgeData"),
        Input("christofides-grafo", "tapEdgeData"),
        Input("christofides-paso", "data"),
        Input("christofides-animacion", "data"),
        Input("christofides-candidato", "data"),
    )
    def mostrar_hover(hover, tap, paso, animacion, candidato):
        activadores = ctx.triggered_prop_ids
        if "christofides-grafo.tapEdgeData" in activadores:
            datos = tap
        elif "christofides-grafo.mouseoverEdgeData" in activadores:
            datos = hover
        else:
            return [], "gl-ch-tooltip-arista"
        if not datos or datos.get("peso") is None:
            return [], "gl-ch-tooltip-arista"
        return [
            html.Span(
                str(datos.get("tipo", "ARISTA")).upper(),
                className="gl-ch-tooltip-titulo",
            ),
            html.Div(
                [
                    html.Strong(
                        datos.get("arista", "—"), className="gl-ch-tooltip-extremos"
                    ),
                    html.Div(
                        [
                            html.Span("Peso", className="gl-ch-tooltip-peso-label"),
                            html.Strong(
                                str(datos["peso"]), className="gl-ch-tooltip-peso-valor"
                            ),
                        ],
                        className="gl-ch-tooltip-peso",
                    ),
                ],
                className="gl-ch-tooltip-fila",
            ),
        ], "gl-ch-tooltip-arista gl-ch-tooltip-visible"

    @app.callback(
        Output("christofides-grafo", "stylesheet"),
        Input("christofides-mostrar-pesos", "value"),
    )
    def alternar_pesos(mostrar):
        """Cambia solo el estilo, no el paso ni los elementos del grafo."""
        if "mostrar" in (mostrar or []):
            return ESTILO_GRAFO + ESTILO_PESOS
        return ESTILO_GRAFO

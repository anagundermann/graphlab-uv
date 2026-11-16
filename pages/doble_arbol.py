"""GraphLab UV - Doble arbol: interfaz didactica sincronizada.

Los calculos matematicos permanecen en models/doble_arbol.py.
Este modulo dibuja exclusivamente el estado correspondiente al paso actual.
"""

from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from models.grafo_data import VERTICES, POSICIONES
from models.doble_arbol import (
    ARISTAS_ARBOL,
    PESOS,
    PESO_ARBOL,
    PESO_DOBLE,
    DATOS_REFERENCIA,
    obtener_datos,
)


ETAPAS = [
    ("arbol", "Árbol mínimo"),
    ("duplicado", "Duplicación"),
    ("euler", "Circuito euleriano"),
    ("seleccion", "Primeras visitas"),
    ("atajo", "Atajos"),
    ("final", "Ciclo final"),
]

# Las orientaciones canonicas solo controlan la geometria de las copias.
ARISTAS_CANONICAS = {frozenset((u, v)): (u, v, peso) for u, v, peso in ARISTAS_ARBOL}


def segmentos_tras_atajos(datos, cantidad):
    """Describir la caminata real tras aplicar los primeros `cantidad` atajos.

    Un atajo reemplaza un tramo contiguo de la caminata euleriana. Las aristas
    todavia no sustituidas siguen presentes: NO se anticipa el ciclo final.
    """
    atajos = datos["atajos"]
    cantidad = max(0, min(cantidad, len(atajos)))
    euler = datos["euler"]
    posiciones = [euler.index(v) for v in datos["primeras"]]
    posiciones.append(len(euler) - 1)
    indice_atajo = {
        tuple(atajo["tramo"]): (i, atajo) for i, atajo in enumerate(atajos, start=1)
    }

    segmentos = []
    for inicio_tramo, fin_tramo in zip(posiciones[:-1], posiciones[1:]):
        tramo = euler[inicio_tramo : fin_tramo + 1]
        opcion = indice_atajo.get(tuple(tramo))

        if opcion is not None and opcion[0] <= cantidad:
            numero, atajo = opcion
            segmentos.append(
                {
                    "origen": atajo["origen"],
                    "destino": atajo["destino"],
                    "peso": atajo["costo_directo"],
                    "tipo": "atajo",
                    "numero": numero,
                    "copia": 0,
                }
            )
        else:
            for indice in range(inicio_tramo, fin_tramo):
                travesia = datos["travesias"][indice]
                segmentos.append(
                    {
                        "origen": travesia["origen"],
                        "destino": travesia["destino"],
                        "peso": travesia["peso"],
                        "tipo": "euler",
                        "numero": indice + 1,
                        "copia": travesia["copia"],
                    }
                )

    # Comprobaciones sobre la representacion: sin modificar el algoritmo.
    secuencia = [datos["inicio"]] + [s["destino"] for s in segmentos]
    if any(
        segmentos[i]["destino"] != segmentos[i + 1]["origen"]
        for i in range(len(segmentos) - 1)
    ):
        raise ValueError("La visualizacion produjo un recorrido discontinuo.")
    if secuencia[0] != secuencia[-1]:
        raise ValueError("El recorrido intermedio no regresa al origen.")
    costo = sum(segmento["peso"] for segmento in segmentos)
    ahorro = sum(a["ahorro"] for a in atajos[:cantidad])
    if costo != PESO_DOBLE - ahorro:
        raise ValueError("El costo intermedio no concuerda con los atajos.")
    if cantidad == len(atajos) and secuencia != datos["circuito"]:
        raise ValueError("La ultima visualizacion no coincide con el ciclo final.")
    return segmentos


def agregar_arista(
    elementos,
    identificador,
    u,
    v,
    peso,
    estado,
    tipo="Arista",
    copia=0,
    modo="simple",
    sentido="normal",
):
    """Incluir metadatos para el hover, sin etiquetas numericas en el grafo."""
    elementos.append(
        {
            "data": {
                "id": identificador,
                "source": u,
                "target": v,
                "peso": peso,
                "arista": f"{u}–{v}",
                "estado": estado,
                "tipo": tipo,
                "copia": copia,
                "modo": modo,
                "sentido": sentido,
            }
        }
    )


def construir_elementos(paso, datos, animacion=0):
    """Grafo con posiciones fijas y transformacion estrictamente progresiva."""
    etapa_actual = datos["pasos"][paso]
    etapa = etapa_actual["etapa"]
    avance = etapa_actual["avance"]
    actual = datos["inicio"]
    if etapa == "euler":
        actual = datos["euler"][avance]
    elif etapa == "atajo":
        actual = datos["atajos"][avance - 1]["destino"]
    elif etapa == "final":
        actual = datos["circuito"][min(animacion, len(VERTICES))]

    elementos = [
        {
            "data": {
                "id": v,
                "label": v,
                "estado": "actual" if v == actual else "normal",
            },
            "position": POSICIONES[v].copy(),
        }
        for v in VERTICES
    ]

    if etapa == "arbol":
        for u, v, peso in ARISTAS_ARBOL:
            agregar_arista(
                elementos, f"arbol-{u}-{v}", u, v, peso, "arbol", tipo="Árbol mínimo"
            )

    elif etapa in ("duplicado", "euler", "seleccion"):
        recorridas = set()
        travesia_actual = None
        if etapa in ("euler", "seleccion"):
            cantidad = avance if etapa == "euler" else len(datos["travesias"])
            recorridas = {t["id"] for t in datos["travesias"][:cantidad]}
        if etapa == "euler":
            travesia_actual = datos["travesias"][avance - 1]

        for u, v, peso in ARISTAS_ARBOL:
            for copia in (1, 2):
                identificador = f"doble-{u}-{v}-{copia}"
                estado = (
                    "copia_recorrida"
                    if identificador in recorridas
                    else "copia_pendiente"
                )
                sentido = "normal"
                if travesia_actual and identificador == travesia_actual["id"]:
                    estado = "copia_actual"
                    sentido = "normal" if travesia_actual["origen"] == u else "inverso"
                agregar_arista(
                    elementos,
                    identificador,
                    u,
                    v,
                    peso,
                    estado,
                    tipo="Copia del árbol",
                    copia=copia,
                    modo="doble",
                    sentido=sentido,
                )

    elif etapa == "atajo":
        # La guia tenue indica el AGM original. Encima se dibuja exclusivamente
        # el recorrido euleriano vigente, con los atajos ya aplicados.
        for u, v, peso in ARISTAS_ARBOL:
            agregar_arista(
                elementos,
                f"guia-{u}-{v}",
                u,
                v,
                peso,
                "guia",
                tipo="Árbol de referencia",
            )

        for i, segmento in enumerate(segmentos_tras_atajos(datos, avance), start=1):
            u_real = segmento["origen"]
            v_real = segmento["destino"]
            if segmento["tipo"] == "atajo":
                estado = (
                    "atajo_actual" if segmento["numero"] == avance else "atajo_aplicado"
                )
                agregar_arista(
                    elementos,
                    f"ruta-atajo-{i}",
                    u_real,
                    v_real,
                    segmento["peso"],
                    estado,
                    tipo="Atajo",
                )
            else:
                u, v, _ = ARISTAS_CANONICAS[frozenset((u_real, v_real))]
                sentido = "normal" if u_real == u else "inverso"
                agregar_arista(
                    elementos,
                    f"ruta-euler-{i}",
                    u,
                    v,
                    segmento["peso"],
                    "tramo_restante",
                    tipo="Recorrido euleriano pendiente de atajo",
                    copia=segmento["copia"],
                    modo="doble",
                    sentido=sentido,
                )

    elif etapa == "final":
        cantidad = min(animacion, len(datos["circuito"]) - 1)
        for i, (u, v) in enumerate(zip(datos["circuito"][:-1], datos["circuito"][1:])):
            if i >= cantidad:
                break
            agregar_arista(
                elementos,
                f"ciclo-{i + 1}-{u}-{v}",
                u,
                v,
                PESOS[frozenset((u, v))],
                "circuito_actual" if i == cantidad - 1 else "circuito",
                tipo="Ciclo hamiltoniano",
            )

    return elementos


ESTILO_GRAFO = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "background-color": "#267c9e",
            "border-width": 2,
            "border-color": "#ffffff",
            "color": "#ffffff",
            "text-valign": "center",
            "text-halign": "center",
            "width": 45,
            "height": 45,
            "font-size": 17,
            "font-weight": "bold",
        },
    },
    {
        "selector": 'node[estado = "actual"]',
        "style": {
            "background-color": "#186c83",
            "border-width": 4,
            "border-color": "#a9d7dd",
        },
    },
    {
        "selector": "edge",
        "style": {
            "line-color": "#a9bac6",
            "width": 3,
            "opacity": 1,
        },
    },
    {
        "selector": 'edge[estado = "arbol"]',
        "style": {
            "line-color": "#238a80",
            "width": 5,
        },
    },
    {
        "selector": 'edge[modo = "doble"]',
        "style": {
            "curve-style": "unbundled-bezier",
            "control-point-weights": 0.5,
        },
    },
    {
        "selector": 'edge[modo = "doble"][copia = 1]',
        "style": {
            "control-point-distances": -26,
        },
    },
    {
        "selector": 'edge[modo = "doble"][copia = 2]',
        "style": {
            "control-point-distances": 26,
        },
    },
    {
        "selector": 'edge[estado = "copia_pendiente"]',
        "style": {
            "line-color": "#c58a35",
            "width": 3.5,
            "opacity": 0.84,
        },
    },
    {
        "selector": 'edge[estado = "copia_recorrida"]',
        "style": {
            "line-color": "#238a80",
            "width": 4,
            "opacity": 0.92,
        },
    },
    {
        "selector": 'edge[estado = "copia_actual"]',
        "style": {
            "line-color": "#cc6570",
            "width": 6,
            "opacity": 1,
        },
    },
    {
        "selector": 'edge[estado = "copia_actual"][sentido = "normal"]',
        "style": {
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#cc6570",
            "arrow-scale": 1.05,
        },
    },
    {
        "selector": 'edge[estado = "copia_actual"][sentido = "inverso"]',
        "style": {
            "source-arrow-shape": "triangle",
            "source-arrow-color": "#cc6570",
            "arrow-scale": 1.05,
        },
    },
    {
        "selector": 'edge[estado = "guia"]',
        "style": {
            "line-color": "#bccbd3",
            "width": 2,
            "opacity": 0.17,
        },
    },
    {
        "selector": 'edge[estado = "tramo_restante"]',
        "style": {
            "line-color": "#559b96",
            "width": 3.8,
            "opacity": 0.85,
        },
    },
    {
        "selector": 'edge[estado = "atajo_aplicado"]',
        "style": {
            "line-color": "#6860a5",
            "width": 4.8,
            "opacity": 1,
        },
    },
    {
        "selector": 'edge[estado = "atajo_actual"]',
        "style": {
            "line-color": "#6860a5",
            "width": 6.5,
            "opacity": 1,
            "line-style": "dashed",
        },
    },
    {
        "selector": 'edge[estado = "circuito"]',
        "style": {
            "line-color": "#416b86",
            "width": 5,
            "opacity": 1,
        },
    },
    {
        "selector": 'edge[estado = "circuito_actual"]',
        "style": {
            "line-color": "#275b7c",
            "width": 6.5,
            "opacity": 1,
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#275b7c",
            "arrow-scale": 1.05,
        },
    },
]


def secuencia_vertices(vertices, visitados=None, cerrar=False):
    """Chips de una caminata: las visitas repetidas se tachan solo al comparar."""
    partes = []
    vistos = set()
    for i, v in enumerate(vertices):
        repetido = (
            visitados is not None
            and v in vistos
            and not (cerrar and i == len(vertices) - 1)
        )
        clase = "gl-da-vertice-chip" + (" gl-da-repetido" if repetido else "")
        if i:
            partes.append(html.Span("→", className="gl-da-flecha"))
        partes.append(html.Span(v, className=clase))
        vistos.add(v)
    return html.Div(partes, className="gl-da-secuencia-vertices")


def crear_etapas(etapa):
    indice = next(i for i, (clave, _) in enumerate(ETAPAS) if clave == etapa)
    return [
        html.Span(
            etiqueta,
            className=(
                "gl-da-etapa gl-da-etapa-actual"
                if i == indice
                else "gl-da-etapa gl-da-etapa-lista"
                if i < indice
                else "gl-da-etapa"
            ),
        )
        for i, (_, etiqueta) in enumerate(ETAPAS)
    ]


def metrica(titulo, valor):
    return html.Div(
        [
            html.Span(titulo, className="gl-da-metrica-label"),
            html.Strong(str(valor), className="gl-da-metrica-valor"),
        ],
        className="gl-da-metrica",
    )


def crear_panel_estado(paso, datos, animacion=0):
    """Explicacion, cifras y rutas coincidentes con el mismo paso del grafo."""
    estado = datos["pasos"][paso]
    etapa, avance = estado["etapa"], estado["avance"]
    partes = [
        html.Span("ETAPA ACTUAL", className="gl-da-eyebrow"),
        html.H3(estado["titulo"], className="gl-da-estado-titulo"),
        html.P(estado["mensaje"], className="gl-da-mensaje", **{"aria-live": "polite"}),
    ]

    if etapa == "arbol":
        partes.extend(
            [
                html.Div(
                    [
                        metrica("Peso del AGM", PESO_ARBOL),
                        metrica("Aristas", f"{len(ARISTAS_ARBOL)}/6"),
                        metrica("Origen", datos["inicio"]),
                    ],
                    className="gl-da-metricas",
                ),
                html.H4("Aristas del árbol mínimo", className="gl-da-seccion-titulo"),
                html.Div(
                    [
                        html.Span(f"{u}–{v} · {peso}", className="gl-da-arista-chip")
                        for u, v, peso in ARISTAS_ARBOL
                    ],
                    className="gl-da-chips",
                ),
                html.P(
                    "Este árbol conecta los siete vértices sin ciclos. Su costo es "
                    "una cota inferior del TSP.",
                    className="gl-da-nota-estado",
                ),
            ]
        )

    elif etapa == "duplicado":
        partes.extend(
            [
                html.Div(
                    [
                        metrica("Costo duplicado", PESO_DOBLE),
                        metrica("Copias", len(ARISTAS_ARBOL) * 2),
                        metrica("Grados", "Pares"),
                    ],
                    className="gl-da-metricas",
                ),
                html.Div(
                    [
                        html.Strong("¿Por qué se duplican?"),
                        html.P(
                            "Cada arista aparece dos veces; así todos los vértices "
                            "tienen grado par y existe un circuito euleriano."
                        ),
                        html.Div(
                            f"2 × {PESO_ARBOL} = {PESO_DOBLE}",
                            className="gl-da-formula-inline",
                        ),
                    ],
                    className="gl-da-explicacion",
                ),
            ]
        )

    elif etapa == "euler":
        usadas = datos["travesias"][:avance]
        parcial = datos["euler"][: avance + 1]
        costo = sum(t["peso"] for t in usadas)
        t = usadas[-1]
        partes.extend(
            [
                html.Div(
                    [
                        metrica(
                            "Copias recorridas", f"{avance}/{len(datos['travesias'])}"
                        ),
                        metrica("Costo recorrido", costo),
                        metrica("Costo total", PESO_DOBLE),
                    ],
                    className="gl-da-metricas",
                ),
                html.H4("Copia actual", className="gl-da-seccion-titulo"),
                html.Div(
                    [
                        html.Strong(f"{t['origen']} → {t['destino']}"),
                        html.Span(f"Copia {t['copia']} · Peso {t['peso']}"),
                    ],
                    className="gl-da-linea-actual",
                ),
                html.H4("Recorrido acumulado", className="gl-da-seccion-titulo"),
                secuencia_vertices(parcial),
            ]
        )

    elif etapa == "seleccion":
        repetidas = len(datos["euler"]) - len(VERTICES) - 1
        partes.extend(
            [
                html.Div(
                    [
                        metrica("Visitas en la lista", len(datos["euler"])),
                        metrica("Vértices distintos", len(VERTICES)),
                        metrica("Intermedias repetidas", repetidas),
                    ],
                    className="gl-da-metricas",
                ),
                html.H4(
                    "Conservar la primera visita", className="gl-da-seccion-titulo"
                ),
                secuencia_vertices(datos["euler"], visitados=True, cerrar=True),
                html.P(
                    "Las visitas repetidas se marcan en gris; conservamos el "
                    "regreso final al origen para cerrar el circuito.",
                    className="gl-da-nota-estado",
                ),
            ]
        )

    elif etapa == "atajo":
        atajo = datos["atajos"][avance - 1]
        segmentos = segmentos_tras_atajos(datos, avance)
        ahorro = sum(a["ahorro"] for a in datos["atajos"][:avance])
        costo_vigente = sum(segmento["peso"] for segmento in segmentos)
        recorrido_vigente = [datos["inicio"]] + [s["destino"] for s in segmentos]
        partes.extend(
            [
                html.Div(
                    [
                        metrica("Costo vigente", costo_vigente),
                        metrica("Ahorro acumulado", ahorro),
                        metrica("Atajos aplicados", f"{avance}/{len(datos['atajos'])}"),
                    ],
                    className="gl-da-metricas",
                ),
                html.H4("Tramo que sustituimos", className="gl-da-seccion-titulo"),
                secuencia_vertices(atajo["tramo"]),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    "Arista directa", className="gl-da-metrica-label"
                                ),
                                html.Strong(f"{atajo['origen']} → {atajo['destino']}"),
                            ]
                        ),
                        html.Div(
                            [
                                html.Span(
                                    "Ahorro de este atajo",
                                    className="gl-da-metrica-label",
                                ),
                                html.Strong(
                                    f"{atajo['costo_tramo']} − {atajo['costo_directo']} = {atajo['ahorro']}"
                                ),
                            ]
                        ),
                    ],
                    className="gl-da-calculo",
                ),
                html.H4("Recorrido vigente", className="gl-da-seccion-titulo"),
                secuencia_vertices(recorrido_vigente),
                html.P(
                    f"Costo: {PESO_DOBLE} − {ahorro} = {costo_vigente}. "
                    "Los tramos pendientes aún no se sustituyen.",
                    className="gl-da-nota-estado",
                ),
            ]
        )

    elif etapa == "final":
        total = len(datos["circuito"]) - 1
        cantidad = min(animacion, total)
        completo = cantidad == total
        ahorro = PESO_DOBLE - datos["peso_circuito"]
        partes.extend(
            [
                html.Div(
                    [
                        metrica(
                            "Costo del ciclo",
                            datos["peso_circuito"] if completo else "—",
                        ),
                        metrica("Aristas dibujadas", f"{cantidad}/{total}"),
                        metrica("Ahorro total", ahorro),
                    ],
                    className="gl-da-metricas",
                ),
                html.H4("Recorrido hamiltoniano", className="gl-da-seccion-titulo"),
                secuencia_vertices(datos["circuito"][: cantidad + 1]),
            ]
        )
        if completo:
            partes.append(
                html.Div(
                    [
                        html.Strong("Ciclo hamiltoniano construido"),
                        html.P(
                            f"Se visitaron los {len(VERTICES)} vértices exactamente una "
                            f"vez y se regresó al origen. Costo {datos['peso_circuito']} "
                            f"≤ 2 × {PESO_ARBOL} = {PESO_DOBLE}."
                        ),
                        html.P(
                            "Es una aproximación del TSP métrico; no necesariamente "
                            "el circuito óptimo."
                        ),
                    ],
                    className="gl-da-conclusion",
                )
            )
        else:
            partes.append(
                html.P(
                    "El ciclo se dibuja automáticamente, arista por arista.",
                    className="gl-da-nota-estado",
                )
            )

    return partes


LEYENDAS = {
    "arbol": [("Verde", "Árbol mínimo", "verde")],
    "duplicado": [("Ámbar", "Dos copias de cada arista", "ambar")],
    "euler": [
        ("Verde", "Copia recorrida", "verde"),
        ("Rojo", "Copia actual", "rojo"),
        ("Ámbar", "Copia pendiente", "ambar"),
    ],
    "seleccion": [("Verde", "Circuito euleriano completo", "verde")],
    "atajo": [
        ("Verde", "Tramo aún no sustituido", "verde"),
        ("Violeta", "Atajo aplicado", "violeta"),
        ("Gris", "Árbol de referencia", "gris"),
    ],
    "final": [("Azul", "Ciclo hamiltoniano", "azul")],
}


def crear_leyenda(etapa):
    return [
        html.Span(
            [
                html.I(className=f"gl-da-punto gl-da-punto-{color}"),
                texto,
            ]
        )
        for _nombre, texto, color in LEYENDAS[etapa]
    ]


def crear_pagina(paso_inicial=0, inicio_inicial="a"):
    inicio_inicial = inicio_inicial if inicio_inicial in VERTICES else VERTICES[0]
    datos = obtener_datos(inicio_inicial)
    paso_inicial = max(0, min(len(datos["pasos"]) - 1, int(paso_inicial)))
    ultimo = len(datos["pasos"]) - 1
    return html.Div(
        [
            dcc.Store(id="doble-paso", data=paso_inicial),
            dcc.Store(id="doble-origen-previo", data=inicio_inicial),
            dcc.Store(id="doble-animacion", data=0),
            dcc.Interval(
                id="doble-intervalo", interval=550, n_intervals=0, disabled=True
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "ALGORITMO DE APROXIMACIÓN", className="gl-da-eyebrow"
                            ),
                            html.H2("Doble árbol · 2-TSP"),
                            html.P(
                                "Del árbol mínimo a un ciclo hamiltoniano mediante "
                                "duplicación, recorrido euleriano y atajos."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("7 vértices"),
                            html.Span(f"AGM: {PESO_ARBOL}"),
                            html.Span("TSP métrico"),
                            html.Button(
                                "Ver código Python",
                                id={
                                    "type": "graphlab-abrir-codigo",
                                    "index": "doble_arbol",
                                },
                                n_clicks=0,
                                type="button",
                                className="gl-ver-codigo",
                            ),
                        ],
                        className="gl-da-etiquetas",
                    ),
                ],
                className="gl-da-intro",
            ),
            html.Div(
                crear_etapas(datos["pasos"][paso_inicial]["etapa"]),
                id="doble-etapas",
                className="gl-da-etapas",
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
                                            html.Label(
                                                "Vértice inicial",
                                                htmlFor="doble-inicio",
                                            ),
                                            dcc.Dropdown(
                                                id="doble-inicio",
                                                options=[
                                                    {"label": v, "value": v}
                                                    for v in VERTICES
                                                ],
                                                value=inicio_inicial,
                                                searchable=False,
                                                clearable=False,
                                            ),
                                        ],
                                        className="gl-da-selector",
                                    ),
                                ],
                                className="gl-da-grafo-cabecera",
                            ),
                            html.Div(
                                [
                                    cyto.Cytoscape(
                                        id="doble-grafo",
                                        layout={
                                            "name": "preset",
                                            "fit": True,
                                            "padding": 40,
                                        },
                                        elements=construir_elementos(
                                            paso_inicial, datos
                                        ),
                                        stylesheet=ESTILO_GRAFO,
                                        style={"width": "100%", "height": "410px"},
                                        className="gl-da-grafo",
                                        autoungrabify=True,
                                        clearOnUnhover=True,
                                    ),
                                    html.Div(
                                        id="doble-tooltip-arista",
                                        className="gl-da-tooltip-arista",
                                    ),
                                ],
                                className="gl-da-grafo-marco",
                            ),
                            html.Div(
                                crear_leyenda(datos["pasos"][paso_inicial]["etapa"]),
                                id="doble-leyenda",
                                className="gl-da-leyenda",
                            ),
                            html.P(
                                "Pasa el cursor sobre una arista para consultar su peso "
                                "y, cuando corresponda, el número de copia.",
                                className="gl-da-ayuda",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Strong(
                                                f"Paso {paso_inicial} de {ultimo}",
                                                id="doble-contador",
                                            ),
                                            html.Div(
                                                html.Div(
                                                    id="doble-progreso",
                                                    className="gl-da-progreso-valor",
                                                    style={
                                                        "width": f"{100 * paso_inicial / ultimo:.1f}%"
                                                    },
                                                ),
                                                className="gl-da-progreso-pista",
                                            ),
                                        ],
                                        className="gl-da-avance",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Button(
                                                "Anterior",
                                                id="doble-anterior",
                                                n_clicks=0,
                                                color="outline-secondary",
                                                disabled=(paso_inicial == 0),
                                            ),
                                            dbc.Button(
                                                "Siguiente",
                                                id="doble-siguiente",
                                                n_clicks=0,
                                                color="primary",
                                                disabled=(paso_inicial == ultimo),
                                            ),
                                            dbc.Button(
                                                "Reiniciar",
                                                id="doble-reiniciar",
                                                n_clicks=0,
                                                color="outline-secondary",
                                            ),
                                            dbc.Button(
                                                "Reproducir ciclo",
                                                id="doble-reproducir",
                                                n_clicks=0,
                                                color="outline-primary",
                                                disabled=True,
                                                style={"display": "none"},
                                            ),
                                        ],
                                        className="gl-da-botones",
                                    ),
                                ],
                                className="gl-da-controles",
                            ),
                        ],
                        className="gl-da-tarjeta gl-da-panel-grafo",
                    ),
                    html.Aside(
                        crear_panel_estado(paso_inicial, datos),
                        id="doble-panel-estado",
                        className="gl-da-tarjeta gl-da-panel-estado",
                    ),
                ],
                className="gl-da-distribucion",
            ),
            html.P(
                "Se utiliza el mismo grafo métrico y el mismo AGM de Kruskal; "
                "los pesos no dependen de la posición de los vértices.",
                className="gl-da-nota",
            ),
        ],
        className="pagina-algoritmo pagina-doble-arbol",
    )


def registrar_callbacks(app):
    @app.callback(
        Output("doble-paso", "data"),
        Output("doble-origen-previo", "data"),
        Output("doble-animacion", "data"),
        Output("doble-grafo", "elements"),
        Output("doble-etapas", "children"),
        Output("doble-panel-estado", "children"),
        Output("doble-leyenda", "children"),
        Output("doble-contador", "children"),
        Output("doble-progreso", "style"),
        Output("doble-anterior", "disabled"),
        Output("doble-siguiente", "disabled"),
        Output("doble-reproducir", "disabled"),
        Output("doble-reproducir", "style"),
        Output("doble-intervalo", "disabled"),
        Input("doble-anterior", "n_clicks"),
        Input("doble-siguiente", "n_clicks"),
        Input("doble-reiniciar", "n_clicks"),
        Input("doble-reproducir", "n_clicks"),
        Input("doble-inicio", "value"),
        Input("doble-intervalo", "n_intervals"),
        State("doble-paso", "data"),
        State("doble-animacion", "data"),
        State("doble-origen-previo", "data"),
    )
    def actualizar_doble_arbol(
        anterior,
        siguiente,
        reiniciar,
        reproducir,
        inicio,
        n_intervalos,
        paso,
        animacion,
        origen_previo,
    ):
        if inicio not in VERTICES:
            inicio = VERTICES[0]
        datos = obtener_datos(inicio)
        ultimo = len(datos["pasos"]) - 1
        total_aristas = len(datos["circuito"]) - 1
        paso = max(0, min(ultimo, paso if isinstance(paso, int) else 0))
        animacion = max(
            0, min(total_aristas, animacion if isinstance(animacion, int) else 0)
        )
        activador = ctx.triggered_id

        if (activador == "doble-reiniciar" and reiniciar) or (
            activador == "doble-inicio" and inicio != origen_previo
        ):
            paso = 0
            animacion = 0
        elif activador == "doble-anterior" and anterior:
            paso = max(0, paso - 1)
            animacion = 0
        elif activador == "doble-siguiente" and siguiente:
            paso = min(ultimo, paso + 1)
            animacion = 0
        elif activador == "doble-reproducir" and reproducir and paso == ultimo:
            animacion = 0
        elif activador == "doble-intervalo" and n_intervalos and paso == ultimo:
            animacion = min(total_aristas, animacion + 1)

        etapa = datos["pasos"][paso]["etapa"]
        en_final = paso == ultimo
        animar = en_final and animacion < total_aristas
        return (
            paso,
            inicio,
            animacion,
            construir_elementos(paso, datos, animacion),
            crear_etapas(etapa),
            crear_panel_estado(paso, datos, animacion),
            crear_leyenda(etapa),
            f"Paso {paso} de {ultimo}",
            {"width": f"{100 * paso / ultimo:.1f}%"},
            paso == 0,
            en_final,
            not (en_final and not animar),
            {"display": "inline-flex" if en_final else "none"},
            not animar,
        )

    @app.callback(
        Output("doble-tooltip-arista", "children"),
        Output("doble-tooltip-arista", "className"),
        Input("doble-grafo", "mouseoverEdgeData"),
        Input("doble-grafo", "tapEdgeData"),
        Input("doble-paso", "data"),
        Input("doble-animacion", "data"),
    )
    def mostrar_peso_al_pasar(datos_hover, datos_tap, paso, animacion):
        activadores = ctx.triggered_prop_ids
        if "doble-grafo.tapEdgeData" in activadores:
            datos = datos_tap
        elif "doble-grafo.mouseoverEdgeData" in activadores:
            datos = datos_hover
        else:
            return [], "gl-da-tooltip-arista"

        if not datos or datos.get("peso") is None:
            return [], "gl-da-tooltip-arista"

        copia = datos.get("copia", 0)
        subtitulo = (
            f"COPIA {copia} DE 2"
            if copia in (1, 2)
            else str(datos.get("tipo", "ARISTA")).upper()
        )
        contenido = [
            html.Span(subtitulo, className="gl-da-tooltip-titulo"),
            html.Div(
                [
                    html.Strong(
                        datos.get("arista", "—"), className="gl-da-tooltip-extremos"
                    ),
                    html.Div(
                        [
                            html.Span("Peso", className="gl-da-tooltip-peso-label"),
                            html.Strong(
                                str(datos["peso"]), className="gl-da-tooltip-peso-valor"
                            ),
                        ],
                        className="gl-da-tooltip-peso",
                    ),
                ],
                className="gl-da-tooltip-fila",
            ),
        ]
        return contenido, "gl-da-tooltip-arista gl-da-tooltip-visible"

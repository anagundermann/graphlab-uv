"""Introduccion al problema del viajante y los metodos de GraphLab UV.

Esta pagina es informativa. Los algoritmos y sus estados se mantienen
exclusivamente en sus modulos de laboratorio.
"""

from math import factorial

from dash import dcc, html

from models.grafo_data import ARISTAS, VERTICES
from models.tsp_optimo import COSTO_OPTIMO


def _total_ciclos(numero_vertices):
    """Ciclos hamiltonianos distintos en un TSP simetrico completo."""
    return factorial(numero_vertices - 1) // 2


def _tarjeta_cantidad(numero_vertices):
    """Cantidad de ciclos sin duplicar rotaciones ni inversiones."""
    total = _total_ciclos(numero_vertices)
    if total >= 1_000_000_000:
        valor = f"{total / 1_000_000_000:.1f}".replace(".", ",") + " mil millones"
    else:
        valor = f"{total:,}".replace(",", ".")
    return html.Div(
        [
            html.Span(
                f"{numero_vertices} vértices", className="gl-portada-cifra-etiqueta"
            ),
            html.Strong(valor, className="gl-portada-cifra-valor"),
            html.Span("ciclos distintos", className="gl-portada-cifra-nota"),
        ],
        className="gl-portada-cifra",
    )


def _tarjeta_algoritmo(numero, titulo, tipo, descripcion, garantia, clase=""):
    return html.Div(
        [
            html.Div(
                [
                    html.Span(numero, className="gl-portada-paso-numero"),
                    html.Span(tipo, className="gl-portada-paso-tipo"),
                ],
                className="gl-portada-paso-meta",
            ),
            html.H3(titulo, className="gl-portada-paso-titulo"),
            html.P(descripcion, className="gl-portada-paso-descripcion"),
            html.P(garantia, className="gl-portada-paso-garantia"),
        ],
        className=f"gl-portada-paso {clase}".strip(),
    )


def crear_pagina():
    numero_vertices = len(VERTICES)
    numero_aristas = len(ARISTAS)
    ciclos_instancia = _total_ciclos(numero_vertices)

    return html.Div(
        [
            html.Div(
                [
                    # IZQUIERDA: historia, planteamiento y acceso a teoria.
                    html.Section(
                        [
                            html.Span(
                                "DEL JUEGO ICOSIANO A LA OPTIMIZACIÓN",
                                className="gl-portada-kicker",
                            ),
                            html.H2(
                                "De Hamilton al problema del viajante",
                                className="gl-portada-titulo",
                            ),
                            html.P(
                                [
                                    "En 1857, el matemático irlandés ",
                                    html.A(
                                        [
                                            "William Rowan Hamilton ",
                                            html.Span(
                                                "↗",
                                                style={
                                                    "fontSize": "0.7em",
                                                    "verticalAlign": "super",
                                                },
                                            ),
                                        ],
                                        href="https://es.wikipedia.org/wiki/William_Rowan_Hamilton",
                                        target="_blank",
                                        rel="noopener noreferrer",
                                        style={
                                            "fontWeight": "bold",
                                            "color": "#38bdf8",
                                            "textDecoration": "none",
                                        },
                                    ),
                                    " propuso el juego icosiano: recorrer los ",
                                    html.Strong("20 vértices de un dodecaedro"),
                                    " sin repetir ninguno y regresar al punto de partida.",
                                ],
                                className="gl-portada-texto",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "EL DESAFÍO DE HAMILTON",
                                                className="gl-portada-definicion-etiqueta",
                                            ),
                                            html.P(
                                                [
                                                    "Encontrar un ",
                                                    html.A(
                                                        [
                                                            "ciclo hamiltoniano ",
                                                            html.Span(
                                                                "↗",
                                                                style={
                                                                    "fontSize": "0.7em",
                                                                    "verticalAlign": "super",
                                                                },
                                                            ),
                                                        ],
                                                        href="https://es.wikipedia.org/wiki/Camino_hamiltoniano",
                                                        target="_blank",
                                                        rel="noopener noreferrer",
                                                        style={
                                                            "color": "#38bdf8",
                                                            "textDecoration": "none",
                                                        },
                                                    ),
                                                    " que visite cada vértice una sola vez "
                                                    "y regrese al punto de partida.",
                                                ],
                                                className="gl-portada-definicion-texto",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                html.A(
                                                    [
                                                        "EL PROBLEMA DEL VIAJANTE (TSP) ",
                                                        html.Span(
                                                            "↗",
                                                            style={
                                                                "fontSize": "0.7em",
                                                                "verticalAlign": "super",
                                                            },
                                                        ),
                                                    ],
                                                    href="https://es.wikipedia.org/wiki/Problema_del_viajante",
                                                    target="_blank",
                                                    rel="noopener noreferrer",
                                                    style={
                                                        "color": "#0f766e",
                                                        "textDecoration": "none",
                                                    },
                                                ),
                                                className="gl-portada-definicion-etiqueta",
                                            ),
                                            html.P(
                                                "Entre todos los ciclos hamiltonianos posibles, "
                                                "encontrar aquel que minimiza el costo total "
                                                "del recorrido.",
                                                className="gl-portada-definicion-texto",
                                            ),
                                        ]
                                    ),
                                ],
                                className="gl-portada-diferencia",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "OBJETIVO MATEMÁTICO",
                                                className="gl-portada-kicker",
                                            ),
                                            html.Span(
                                                "Minimizar el peso del ciclo hamiltoniano.",
                                                className="gl-portada-formula-nota",
                                            ),
                                        ],
                                        className="gl-portada-formula-encabezado",
                                    ),
                                    dcc.Markdown(
                                        "$$\n\\min_{C\\in\\mathcal{H}(G)}\\;\\sum_{e\\in E(C)}w(e)\n$$",
                                        mathjax=True,
                                        className="gl-portada-formula",
                                    ),
                                ],
                                className="gl-portada-matematica",
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "Explorar la biblioteca matemática  ↗",
                                        id={
                                            "type": "graphlab-intro-biblioteca",
                                            "index": "introduccion",
                                        },
                                        n_clicks=0,
                                        type="button",
                                        className="gl-intro-biblioteca gl-portada-biblioteca",
                                    ),
                                    html.Span(
                                        "Definiciones, propiedades y demostraciones formales.",
                                        className="gl-portada-biblioteca-nota",
                                    ),
                                ],
                                className="gl-portada-acceso",
                            ),
                        ],
                        className="gl-portada-tarjeta",
                    ),
                    # DERECHA: por que no basta con enumerar ciclos.
                    html.Section(
                        [
                            html.Span(
                                "EL DESAFÍO COMPUTACIONAL",
                                className="gl-portada-kicker",
                            ),
                            html.H2(
                                "¿Por qué necesitamos aproximaciones?",
                                className="gl-portada-titulo",
                            ),
                            html.P(
                                "En un TSP simétrico, cada recorrido y su inverso representan el "
                                "mismo ciclo. Al aumentar los vértices, la cantidad de rutas "
                                "posibles crece factorialmente.",
                                className="gl-portada-texto",
                            ),
                            html.Div(
                                [
                                    _tarjeta_cantidad(numero_vertices),
                                    _tarjeta_cantidad(10),
                                    _tarjeta_cantidad(15),
                                ],
                                className="gl-portada-cifras",
                            ),
                            html.Div(
                                [
                                    dcc.Markdown(
                                        "$$\nN(n)=\\frac{(n-1)!}{2}\n$$",
                                        mathjax=True,
                                        className="gl-portada-conteo-formula",
                                    ),
                                    html.Span(
                                        "Ciclos distintos: se identifican los cambios de origen "
                                        "y de sentido del recorrido.",
                                        className="gl-portada-conteo-nota",
                                    ),
                                ],
                                className="gl-portada-conteo",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "NUESTRO GRAFO",
                                                className="gl-portada-ejemplo-kicker",
                                            ),
                                            html.Strong(
                                                f"{numero_vertices} vértices · {numero_aristas} aristas",
                                                className="gl-portada-ejemplo-titulo",
                                            ),
                                            html.Span(
                                                f"{ciclos_instancia:,}".replace(
                                                    ",", "."
                                                )
                                                + " ciclos examinables por fuerza bruta",
                                                className="gl-portada-ejemplo-texto",
                                            ),
                                        ],
                                        className="gl-portada-ejemplo-datos",
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                "ÓPTIMO EXACTO",
                                                className="gl-portada-ejemplo-kicker",
                                            ),
                                            html.Strong(
                                                str(COSTO_OPTIMO),
                                                className="gl-portada-ejemplo-optimo",
                                            ),
                                        ],
                                        className="gl-portada-ejemplo-resultado",
                                    ),
                                ],
                                className="gl-portada-ejemplo",
                            ),
                            html.P(
                                "Para instancias grandes podemos usar métodos exactos más avanzados "
                                "o construir soluciones aproximadas con garantías matemáticas.",
                                className="gl-portada-conclusion",
                            ),
                        ],
                        className="gl-portada-tarjeta",
                    ),
                ],
                className="gl-portada-columnas",
            ),
            # ABAJO: relacion entre los tres algoritmos, sin confundir AGM y TSP.
            html.Section(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "EL RECORRIDO DE GRAPHLAB",
                                        className="gl-portada-kicker",
                                    ),
                                    html.H2(
                                        "Un árbol generador, dos aproximaciones",
                                        className="gl-portada-metodos-titulo",
                                    ),
                                ]
                            ),
                            html.P(
                                [
                                    "Doble árbol y Christofides buscan resolver ",
                                    html.Strong("el problema del viajante (TPS)"),
                                    " construyendo recorridos aproximados. Ambos utilizan un árbol ",
                                    "generador mínimo obtenido mediante Kruskal",
                                ],
                                className="gl-portada-metodos-intro",
                            ),
                        ],
                        className="gl-portada-metodos-cabecera",
                    ),
                    html.Div(
                        [
                            _tarjeta_algoritmo(
                                "01",
                                "Kruskal",
                                "EXACTO · AGM",
                                "Encuentra el árbol generador mínimo, que sirve como punto de partida.",
                                "No aproxima el TSP.",
                                "gl-portada-paso-base",
                            ),
                            _tarjeta_algoritmo(
                                "02",
                                "Doble árbol",
                                "APROXIMACIÓN · TSP",
                                "Duplica el AGM, obtiene un circuito euleriano y aplica atajos.",
                                "Garantia: costo ≤ 2 · OPT.",
                            ),
                            _tarjeta_algoritmo(
                                "03",
                                "Christofides",
                                "APROXIMACIÓN · TSP",
                                "Agrega un matching perfecto mínimo antes del recorrido euleriano y los atajos.",
                                "Garantia: costo ≤ 1,5 · OPT.",
                            ),
                        ],
                        className="gl-portada-pasos",
                    ),
                    html.Div(
                        [
                            html.Span(
                                "Existen otros métodos exactos y heurísticas, como Held-Karp y 2-opt. "
                                "GraphLab se centra en estos tres algoritmos.",
                                className="gl-portada-metodos-nota",
                            ),
                            html.A(
                                "Origen histórico: juego icosiano",
                                href="https://es.wikipedia.org/wiki/Juego_Icosian",
                                target="_blank",
                                rel="noopener noreferrer",
                                className="gl-portada-fuente",
                            ),
                        ],
                        className="gl-portada-pie-notas",
                    ),
                ],
                className="gl-portada-metodos",
            ),
        ],
        className="gl-intro-pagina gl-portada-pagina",
    )

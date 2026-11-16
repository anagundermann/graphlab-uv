"""Interfaz didactica de Kruskal: un unico estado sincroniza toda la pagina.

Los pasos del algoritmo se calculan exclusivamente en models/kruskal.py.
La pagina no modifica su orden, decisiones, componentes ni resultados.
"""

from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from models.grafo_data import VERTICES, POSICIONES, ARISTAS
from models.kruskal import PASOS, ULTIMO_PASO, ARISTAS_ORDENADAS


PESOS_ARISTAS = {f"{u}-{v}": peso for u, v, peso in ARISTAS}
PESO_AGM = PASOS[-1]["peso_total"]
TOTAL_ARISTAS = len(ARISTAS)
ARISTAS_NECESARIAS = len(VERTICES) - 1


def construir_elementos(paso, mostrar_pendientes=True):
    """Dibujar las mismas posiciones en todos los pasos."""
    datos = PASOS[paso]
    estados = datos["estados"]
    actual = datos["actual"]
    finalizado = paso == ULTIMO_PASO

    elementos = [
        {"data": {"id": v, "label": v}, "position": POSICIONES[v].copy()}
        for v in VERTICES
    ]

    for u, v, peso in ARISTAS:
        arista_id = f"{u}-{v}"
        decision = estados.get(arista_id, "pendiente")

        if decision == "aceptada":
            visual = (
                "aceptada_actual"
                if arista_id == actual and not finalizado
                else "aceptada"
            )
        elif decision == "rechazada":
            visual = "rechazada_actual" if arista_id == actual else "oculta"
        else:
            visual = "pendiente" if mostrar_pendientes else "oculta"

        if finalizado and decision != "aceptada":
            visual = "oculta"

        elementos.append(
            {
                "data": {
                    "id": arista_id,
                    "source": u,
                    "target": v,
                    "peso": peso,
                    "estado": visual,
                }
            }
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
            "color": "white",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": 17,
            "font-weight": "bold",
            "width": 45,
            "height": 45,
        },
    },
    {
        "selector": "edge",
        "style": {
            "line-color": "#aebdcc",
            "opacity": 0.16,
            "width": 2,
        },
    },
    {
        "selector": 'edge[estado = "aceptada"]',
        "style": {"line-color": "#238a80", "width": 5, "opacity": 1},
    },
    {
        "selector": 'edge[estado = "aceptada_actual"]',
        "style": {"line-color": "#127568", "width": 7, "opacity": 1},
    },
    {
        "selector": 'edge[estado = "rechazada_actual"]',
        "style": {
            "line-color": "#ca5962",
            "line-style": "dashed",
            "width": 6,
            "opacity": 1,
        },
    },
    {"selector": 'edge[estado = "oculta"]', "style": {"display": "none"}},
]


def construir_tabla(paso):
    """Lista completa opcional: refleja exactamente el mismo paso que el grafo."""
    datos = PASOS[paso]
    filas = []
    for u, v, peso in ARISTAS_ORDENADAS:
        arista_id = f"{u}-{v}"
        estado = datos["estados"].get(arista_id, "pendiente")
        decision = {
            "aceptada": "Aceptada",
            "rechazada": "Rechazada · ciclo",
            "pendiente": "Sin examinar",
        }[estado]
        clase = (
            "gl-kr-fila-actual"
            if arista_id == datos["actual"]
            else f"gl-kr-fila-{estado}"
        )
        filas.append(
            html.Tr(
                [html.Td(f"{u}–{v}"), html.Td(str(peso)), html.Td(decision)],
                className=clase,
            )
        )

    return dbc.Table(
        [
            html.Thead(
                html.Tr([html.Th("Arista"), html.Th("Peso"), html.Th("Decisión")])
            ),
            html.Tbody(filas),
        ],
        hover=True,
        size="sm",
        className="gl-kr-tabla",
    )


def construir_arbol(paso):
    """Solo las aristas aceptadas, con su peso; nunca las rechazadas."""
    aceptadas = PASOS[paso]["estados"]
    elementos = []
    for u, v, peso in ARISTAS_ORDENADAS:
        if aceptadas.get(f"{u}-{v}") == "aceptada":
            elementos.append(
                html.Span(f"{u}–{v} · {peso}", className="gl-kr-arista-chip")
            )
    return elementos or [
        html.Span("Aún no se ha incorporado ninguna arista.", className="gl-kr-vacio")
    ]


def construir_componentes(paso):
    """Cada componente se representa como un conjunto de vertices."""
    return [
        html.Span("{" + ", ".join(grupo) + "}", className="gl-kr-componente-chip")
        for grupo in PASOS[paso]["componentes"]
    ]


def datos_decision(paso):
    if paso == 0:
        return "—", "—", "Sin examinar", "gl-kr-estado gl-kr-estado-neutro"

    arista_id = PASOS[paso]["actual"]
    estado = PASOS[paso]["estados"][arista_id]
    u, v = arista_id.split("-")
    if estado == "aceptada":
        return (
            f"{u}–{v}",
            str(PESOS_ARISTAS[arista_id]),
            "Aceptada",
            "gl-kr-estado gl-kr-estado-aceptada",
        )
    return (
        f"{u}–{v}",
        str(PESOS_ARISTAS[arista_id]),
        "Rechazada",
        "gl-kr-estado gl-kr-estado-rechazada",
    )


def construir_conclusion(paso):
    if paso != ULTIMO_PASO:
        return []

    restantes = TOTAL_ARISTAS - ULTIMO_PASO
    return html.Div(
        [
            html.H4("Árbol generador mínimo construido"),
            html.P(
                f"Se aceptaron {ARISTAS_NECESARIAS} aristas que conectan los "
                f"{len(VERTICES)} vértices sin formar ciclos. "
                f"Como ya tenemos |V| − 1 aristas, el algoritmo termina. "
                f"Se examinaron {ULTIMO_PASO} de {TOTAL_ARISTAS}; "
                f"las {restantes} restantes no necesitan examinarse."
            ),
            html.Div(
                [
                    html.Span(f"AGM = {PESO_AGM}", className="gl-kr-conclusion-peso"),
                    html.Span(f"{ARISTAS_NECESARIAS}/{ARISTAS_NECESARIAS} aceptadas"),
                    html.Span(f"{ULTIMO_PASO}/{TOTAL_ARISTAS} examinadas"),
                ],
                className="gl-kr-conclusion-metricas",
            ),
        ],
        className="gl-kr-conclusion",
    )


def crear_pagina(paso_inicial=0, inicio_inicial="a"):
    paso_inicial = max(0, min(ULTIMO_PASO, int(paso_inicial)))
    arista, peso, decision, clase_decision = datos_decision(paso_inicial)

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "ALGORITMO PASO A PASO", className="gl-kr-eyebrow"
                            ),
                            html.H2("Kruskal · Árbol generador mínimo"),
                            html.P(
                                "Examina aristas de menor a mayor peso y acepta solo las que no forman un ciclo."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Span("7 vértices"),
                            html.Span("21 aristas"),
                            html.Span("Grafo métrico"),
                            html.Button(
                                "Ver código Python",
                                id={
                                    "type": "graphlab-abrir-codigo",
                                    "index": "kruskal",
                                },
                                n_clicks=0,
                                type="button",
                                className="gl-ver-codigo",
                            ),
                        ],
                        className="gl-kr-etiquetas",
                    ),
                ],
                className="gl-kr-intro",
            ),
            dcc.Store(id="kruskal-paso", data=paso_inicial),
            html.Div(
                [
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H3("Grafo ponderado"),
                                            html.P(
                                                "Las posiciones de los vértices permanecen fijas durante la ejecución."
                                            ),
                                        ]
                                    ),
                                    dbc.Checklist(
                                        id="kruskal-mostrar-pendientes",
                                        options=[
                                            {
                                                "label": "Mostrar aristas pendientes",
                                                "value": "mostrar",
                                            }
                                        ],
                                        value=["mostrar"],
                                        switch=True,
                                        className="gl-kr-switch",
                                    ),
                                ],
                                className="gl-kr-grafo-cabecera",
                            ),
                            html.Div(
                                [
                                    cyto.Cytoscape(
                                        id="kruskal-grafo",
                                        layout={
                                            "name": "preset",
                                            "fit": True,
                                            "padding": 35,
                                        },
                                        elements=construir_elementos(paso_inicial),
                                        stylesheet=ESTILO_GRAFO,
                                        style={"width": "100%", "height": "100%"},
                                        className="gl-kr-grafo",
                                        autoungrabify=True,
                                        clearOnUnhover=True,
                                    ),
                                    html.Div(
                                        id="kruskal-tooltip-arista",
                                        className="gl-kr-tooltip-arista",
                                    ),
                                ],
                                className="gl-kr-grafo-marco",
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        [
                                            html.I(
                                                className="gl-kr-punto gl-kr-punto-verde"
                                            ),
                                            "Aceptada",
                                        ]
                                    ),
                                    html.Span(
                                        [
                                            html.I(
                                                className="gl-kr-punto gl-kr-punto-rojo"
                                            ),
                                            "Rechazada (paso actual)",
                                        ]
                                    ),
                                    html.Span(
                                        [
                                            html.I(
                                                className="gl-kr-punto gl-kr-punto-gris"
                                            ),
                                            "Pendiente",
                                        ]
                                    ),
                                ],
                                className="gl-kr-leyenda",
                            ),
                            html.P(
                                "Pasa el cursor sobre una arista para ver su peso; también puedes tocarla.",
                                className="gl-kr-ayuda gl-kr-ayuda-hover",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Strong(
                                                f"Paso {paso_inicial} de {ULTIMO_PASO}",
                                                id="kruskal-contador",
                                            ),
                                            html.Div(
                                                html.Div(
                                                    id="kruskal-progreso",
                                                    className="gl-kr-progreso-valor",
                                                    style={
                                                        "width": f"{100 * paso_inicial / ULTIMO_PASO:.1f}%"
                                                    },
                                                ),
                                                className="gl-kr-progreso-pista",
                                            ),
                                        ],
                                        className="gl-kr-avance",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Button(
                                                "Anterior",
                                                id="kruskal-anterior",
                                                n_clicks=0,
                                                color="outline-secondary",
                                                disabled=(paso_inicial == 0),
                                            ),
                                            dbc.Button(
                                                "Siguiente",
                                                id="kruskal-siguiente",
                                                n_clicks=0,
                                                color="primary",
                                                disabled=(paso_inicial == ULTIMO_PASO),
                                            ),
                                            dbc.Button(
                                                "Reiniciar",
                                                id="kruskal-reiniciar",
                                                n_clicks=0,
                                                color="outline-secondary",
                                            ),
                                        ],
                                        className="gl-kr-botones",
                                    ),
                                ],
                                className="gl-kr-controles",
                            ),
                        ],
                        className="gl-kr-tarjeta gl-kr-panel-grafo",
                    ),
                    html.Aside(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "DECISIÓN ACTUAL", className="gl-kr-eyebrow"
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "Arista",
                                                        className="gl-kr-mini-etiqueta",
                                                    ),
                                                    html.Strong(
                                                        arista,
                                                        id="kruskal-arista-actual",
                                                        className="gl-kr-arista-actual",
                                                    ),
                                                ]
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "Peso",
                                                        className="gl-kr-mini-etiqueta",
                                                    ),
                                                    html.Strong(
                                                        peso,
                                                        id="kruskal-arista-peso",
                                                        className="gl-kr-peso-arista",
                                                    ),
                                                ]
                                            ),
                                            html.Span(
                                                decision,
                                                id="kruskal-decision",
                                                className=clase_decision,
                                            ),
                                        ],
                                        className="gl-kr-decision-resumen",
                                    ),
                                    html.P(
                                        PASOS[paso_inicial]["mensaje"],
                                        id="kruskal-mensaje",
                                        className="gl-kr-mensaje",
                                        **{"aria-live": "polite"},
                                    ),
                                ],
                                className="gl-kr-bloque-decision",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "Peso acumulado",
                                                className="gl-kr-mini-etiqueta",
                                            ),
                                            html.Strong(
                                                str(PASOS[paso_inicial]["peso_total"]),
                                                id="kruskal-peso",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                "Aristas del árbol",
                                                className="gl-kr-mini-etiqueta",
                                            ),
                                            html.Strong(
                                                f"{PASOS[paso_inicial]['aceptadas']}/{ARISTAS_NECESARIAS}",
                                                id="kruskal-cantidad",
                                            ),
                                        ]
                                    ),
                                ],
                                className="gl-kr-metricas",
                            ),
                            html.Div(
                                [
                                    html.H4("Árbol en construcción"),
                                    html.Div(
                                        construir_arbol(paso_inicial),
                                        id="kruskal-arbol-lista",
                                        className="gl-kr-chips",
                                    ),
                                ],
                                className="gl-kr-seccion",
                            ),
                            html.Div(
                                [
                                    html.H4("Componentes conexas"),
                                    html.Div(
                                        construir_componentes(paso_inicial),
                                        id="kruskal-componentes",
                                        className="gl-kr-chips",
                                    ),
                                ],
                                className="gl-kr-seccion",
                            ),
                            html.Div(
                                construir_conclusion(paso_inicial), id="kruskal-final"
                            ),
                            html.Details(
                                [
                                    html.Summary("Consultar las 21 aristas ordenadas"),
                                    html.P(
                                        "Kruskal las examina por peso creciente; no siempre necesita llegar a la última.",
                                        className="gl-kr-tabla-ayuda",
                                    ),
                                    html.Div(
                                        id="kruskal-tabla",
                                        children=construir_tabla(paso_inicial),
                                        className="gl-kr-tabla-contenedor",
                                    ),
                                ],
                                className="gl-kr-desplegable",
                            ),
                        ],
                        className="gl-kr-tarjeta gl-kr-panel-estado",
                    ),
                ],
                className="gl-kr-distribucion",
            ),
            html.P(
                "Datos del ejemplo: grafo completo ponderado con distancias métricas, "
                "adaptado para GraphLab UV. Sus pesos no son los del taller original.",
                className="gl-kr-nota",
            ),
        ],
        className="pagina-algoritmo pagina-kruskal",
    )


def registrar_callbacks(app):
    """Un callback central actualiza todas las vistas a partir del mismo paso."""

    @app.callback(
        Output("kruskal-paso", "data"),
        Output("kruskal-grafo", "elements"),
        Output("kruskal-tabla", "children"),
        Output("kruskal-contador", "children"),
        Output("kruskal-mensaje", "children"),
        Output("kruskal-arista-actual", "children"),
        Output("kruskal-arista-peso", "children"),
        Output("kruskal-decision", "children"),
        Output("kruskal-decision", "className"),
        Output("kruskal-peso", "children"),
        Output("kruskal-cantidad", "children"),
        Output("kruskal-arbol-lista", "children"),
        Output("kruskal-componentes", "children"),
        Output("kruskal-final", "children"),
        Output("kruskal-progreso", "style"),
        Output("kruskal-anterior", "disabled"),
        Output("kruskal-siguiente", "disabled"),
        Input("kruskal-anterior", "n_clicks"),
        Input("kruskal-siguiente", "n_clicks"),
        Input("kruskal-reiniciar", "n_clicks"),
        Input("kruskal-mostrar-pendientes", "value"),
        State("kruskal-paso", "data"),
    )
    def actualizar_kruskal(anterior, siguiente, reiniciar, mostrar, paso):
        if not isinstance(paso, int):
            paso = 0
        paso = max(0, min(ULTIMO_PASO, paso))

        boton = ctx.triggered_id
        if boton == "kruskal-anterior":
            paso = max(0, paso - 1)
        elif boton == "kruskal-siguiente":
            paso = min(ULTIMO_PASO, paso + 1)
        elif boton == "kruskal-reiniciar":
            paso = 0

        datos = PASOS[paso]
        arista, peso, decision, clase_decision = datos_decision(paso)
        mostrar_pendientes = "mostrar" in (mostrar or [])

        return (
            paso,
            construir_elementos(paso, mostrar_pendientes),
            construir_tabla(paso),
            f"Paso {paso} de {ULTIMO_PASO}",
            datos["mensaje"],
            arista,
            peso,
            decision,
            clase_decision,
            str(datos["peso_total"]),
            f"{datos['aceptadas']}/{ARISTAS_NECESARIAS}",
            construir_arbol(paso),
            construir_componentes(paso),
            construir_conclusion(paso),
            {"width": f"{100 * paso / ULTIMO_PASO:.1f}%"},
            paso == 0,
            paso == ULTIMO_PASO,
        )

    @app.callback(
        Output("kruskal-tooltip-arista", "children"),
        Output("kruskal-tooltip-arista", "className"),
        Input("kruskal-grafo", "mouseoverEdgeData"),
        Input("kruskal-grafo", "tapEdgeData"),
    )
    def mostrar_peso_al_pasar(datos_hover, datos_tap):
        """Mostrar una ficha breve al pasar el cursor o tocar una arista.

        clearOnUnhover limpia el dato de hover al retirar el cursor.
        El evento de clic permite consultar el peso en pantallas tactiles.
        """
        if "kruskal-grafo.tapEdgeData" in ctx.triggered_prop_ids:
            datos = datos_tap
        else:
            datos = datos_hover

        if not datos or datos.get("peso") is None:
            return [], "gl-kr-tooltip-arista"

        u = datos.get("source", "?")
        v = datos.get("target", "?")
        contenido = [
            html.Span("ARISTA", className="gl-kr-tooltip-titulo"),
            html.Div(
                [
                    html.Strong(f"{u}–{v}", className="gl-kr-tooltip-extremos"),
                    html.Div(
                        [
                            html.Span("Peso", className="gl-kr-tooltip-peso-label"),
                            html.Strong(
                                str(datos["peso"]), className="gl-kr-tooltip-peso-valor"
                            ),
                        ],
                        className="gl-kr-tooltip-peso",
                    ),
                ],
                className="gl-kr-tooltip-fila",
            ),
        ]
        return contenido, "gl-kr-tooltip-arista gl-kr-tooltip-visible"

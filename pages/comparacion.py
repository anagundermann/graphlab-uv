"""Comparacion educativa de dos aproximaciones al TSP metrico.

Todos los circuitos, costos y garantias numericas proceden de models/.
Esta pagina se encarga solamente de visualizar y comparar resultados.
"""

from dash import dcc, html, Input, Output, ctx, no_update
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import plotly.graph_objects as go

from models.grafo_data import VERTICES, POSICIONES, ARISTAS
from models.comparacion import (
    PESOS,
    PESO_ARBOL,
    PESO_DOBLE,
    PESO_MATCHING,
    PESO_MULTIGRAFO,
    RESULTADOS,
    conjunto_aristas,
)
from models.tsp_optimo import COSTO_OPTIMO
from models import christofides


# Las dos vistas comparten las mismas coordenadas, escala y disposicion.
_xs = [POSICIONES[v]["x"] for v in VERTICES]
_ys = [POSICIONES[v]["y"] for v in VERTICES]
_ancho = max(max(_xs) - min(_xs), 1)
_alto = max(max(_ys) - min(_ys), 1)
POSICIONES_COMPARACION = {
    v: {
        "x": 55 + 540 * (POSICIONES[v]["x"] - min(_xs)) / _ancho,
        "y": 65 + 265 * (POSICIONES[v]["y"] - min(_ys)) / _alto,
    }
    for v in VERTICES
}

COLOR_DOBLE = "#267CA5"
COLOR_CHRISTOFIDES = "#8062B1"
COLOR_COMPARTIDA = "#A8B8C5"


def elementos_circuito(circuito, aristas_compartidas=None, destacar=False):
    """Grafo de un circuito con metadatos para distinguir aristas y mostrar hover."""
    compartidas = aristas_compartidas or set()
    elementos = [
        {
            "data": {"id": v, "label": v},
            "position": POSICIONES_COMPARACION[v].copy(),
        }
        for v in VERTICES
    ]
    for orden, (u, v) in enumerate(zip(circuito[:-1], circuito[1:]), start=1):
        estado = (
            "compartida"
            if destacar and frozenset((u, v)) in compartidas
            else "exclusiva"
            if destacar
            else "normal"
        )
        elementos.append(
            {
                "data": {
                    "id": f"ruta-{orden}-{u}-{v}",
                    "source": u,
                    "target": v,
                    "arista": f"{u}–{v}",
                    "peso": PESOS[frozenset((u, v))],
                    "orden": orden,
                    "estado": estado,
                },
            }
        )
    return elementos


def estilo_grafo(color):
    """Sin etiquetas de peso; se consultan mediante hover o clic."""
    return [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "background-color": "#247FA0",
                "color": "#FFFFFF",
                "text-valign": "center",
                "text-halign": "center",
                "font-size": 16,
                "font-weight": "bold",
                "width": 41,
                "height": 41,
                "border-width": 2,
                "border-color": "#FFFFFF",
            },
        },
        {
            "selector": "edge",
            "style": {
                "curve-style": "straight",
                "line-color": color,
                "width": 4,
                "opacity": 0.96,
                "target-arrow-shape": "triangle",
                "target-arrow-color": color,
                "arrow-scale": 0.8,
            },
        },
        {
            "selector": 'edge[estado = "compartida"]',
            "style": {
                "line-color": COLOR_COMPARTIDA,
                "target-arrow-color": COLOR_COMPARTIDA,
                "opacity": 0.85,
                "width": 3.5,
            },
        },
        {
            "selector": 'edge[estado = "exclusiva"]',
            "style": {"line-color": color, "target-arrow-color": color, "width": 4.6},
        },
    ]


def texto_circuito(circuito):
    return " → ".join(circuito)


def datos_para_vista(inicio, destacar=False):
    """Derivar ambas vistas del mismo origen; no modificar los circuitos."""
    if inicio not in RESULTADOS:
        inicio = VERTICES[0]
    datos = RESULTADOS[inicio]
    comunes = conjunto_aristas(datos["doble"]) & conjunto_aristas(datos["christofides"])
    return (
        elementos_circuito(datos["doble"], comunes, destacar),
        elementos_circuito(datos["christofides"], comunes, destacar),
    )


def resumen_diferencia(datos):
    """La diferencia se presenta con signo explicito, sin insinuar una regla universal."""
    diferencia = datos["costo_doble"] - datos["costo_christofides"]
    if diferencia > 0:
        return str(diferencia), "Menor costo: Christofides", "favor-christofides"
    if diferencia < 0:
        return str(-diferencia), "Menor costo: Doble árbol", "favor-doble"
    return "0", "Empate en costo", "empate"


def mensaje_comparacion(datos):
    diferencia = datos["costo_doble"] - datos["costo_christofides"]
    if datos["mismo_ciclo"]:
        texto_ciclo = "Ambos algoritmos construyeron el mismo ciclo hamiltoniano."
    elif diferencia == 0:
        texto_ciclo = "Construyeron ciclos diferentes, pero de igual costo."
    else:
        texto_ciclo = "Los algoritmos construyeron ciclos hamiltonianos diferentes."

    if diferencia > 0:
        texto_costo = (
            f"Christofides obtuvo un recorrido {diferencia} unidades más barato "
            f"({datos['costo_doble']} − {datos['costo_christofides']} = {diferencia})."
        )
    elif diferencia < 0:
        texto_costo = (
            f"Doble árbol obtuvo un recorrido {-diferencia} unidades más barato "
            f"en esta ejecución."
        )
    else:
        texto_costo = f"Ambos recorridos cuestan {datos['costo_doble']}."

    return [
        html.P(texto_ciclo, className="gl-cm-observacion-fuerte"),
        html.P(texto_costo),
        html.P(
            "La garantía teórica de Christofides (3/2 del óptimo) no implica "
            "que siempre mejore a doble árbol en cada ejecución.",
            className="gl-cm-aclaracion",
        ),
    ]


def tabla_costos(datos):
    filas = [
        ("Árbol mínimo de Kruskal", str(PESO_ARBOL), str(PESO_ARBOL)),
        (
            "Aristas añadidas",
            f"{len(VERTICES) - 1} copias",
            f"{len(christofides.PAREJAS_MATCHING)} del matching",
        ),
        (
            "Costo antes de los atajos",
            str(PESO_DOBLE),
            f"{PESO_ARBOL} + {PESO_MATCHING} = {PESO_MULTIGRAFO}",
        ),
        (
            "Cantidad de atajos",
            str(datos["atajos_doble"]),
            str(datos["atajos_christofides"]),
        ),
        (
            "Ahorro acumulado por atajos",
            str(datos["ahorro_doble"]),
            str(datos["ahorro_christofides"]),
        ),
        (
            "Costo final del circuito",
            str(datos["costo_doble"]),
            str(datos["costo_christofides"]),
        ),
        ("Garantía teórica (TSP métrico)", "≤ 2 × OPT", "≤ 1,5 × OPT"),
    ]
    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Concepto"),
                        html.Th("Doble árbol · 2-TSP"),
                        html.Th("Christofides"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [html.Td(concepto), html.Td(doble), html.Td(chris)],
                        className="gl-cm-fila-final"
                        if concepto == "Costo final del circuito"
                        else "",
                    )
                    for concepto, doble, chris in filas
                ]
            ),
        ],
        responsive=True,
        hover=True,
        size="sm",
        className="gl-cm-tabla",
    )


def tabla_origenes(inicio):
    filas = []
    for origen in VERTICES:
        datos = RESULTADOS[origen]
        diferencia = datos["costo_doble"] - datos["costo_christofides"]
        if diferencia > 0:
            etiqueta = f"Christofides por {diferencia}"
        elif diferencia < 0:
            etiqueta = f"Doble árbol por {-diferencia}"
        else:
            etiqueta = "Empate"
        filas.append(
            html.Tr(
                [
                    html.Td(origen),
                    html.Td(datos["costo_doble"]),
                    html.Td(datos["costo_christofides"]),
                    html.Td("Sí" if datos["mismo_ciclo"] else "No"),
                    html.Td(etiqueta),
                ],
                className="gl-cm-fila-activa" if origen == inicio else "",
            )
        )
    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Origen"),
                        html.Th("Doble árbol"),
                        html.Th("Christofides"),
                        html.Th("¿Mismo ciclo?"),
                        html.Th("Menor costo"),
                    ]
                )
            ),
            html.Tbody(filas),
        ],
        responsive=True,
        hover=True,
        size="sm",
        className="gl-cm-tabla",
    )


def figura_costos(inicio):
    """Barras con referencia al optimo exacto; clic sobre barra selecciona origen."""
    fig = go.Figure()
    for clave, nombre, color in (
        ("costo_doble", "Doble árbol", COLOR_DOBLE),
        ("costo_christofides", "Christofides", COLOR_CHRISTOFIDES),
    ):
        fig.add_trace(
            go.Bar(
                x=VERTICES,
                y=[RESULTADOS[v][clave] for v in VERTICES],
                name=nombre,
                marker={
                    "color": color,
                    "line": {
                        "color": [
                            "#1B3448" if v == inicio else color for v in VERTICES
                        ],
                        "width": [2.5 if v == inicio else 0 for v in VERTICES],
                    },
                    "opacity": [1 if v == inicio else 0.72 for v in VERTICES],
                },
                customdata=[v for v in VERTICES],
                hovertemplate="Origen %{x}<br>Costo: <b>%{y}</b><extra>"
                + nombre
                + "</extra>",
            )
        )
    if COSTO_OPTIMO is not None:
        fig.add_hline(
            y=COSTO_OPTIMO,
            line_color="#788998",
            line_dash="dot",
            line_width=1.5,
            annotation_text=f"Óptimo exacto: {COSTO_OPTIMO}",
            annotation_position="top left",
            annotation_font_color="#586E80",
            annotation_font_size=11,
        )
    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.08,
        height=275,
        margin=dict(l=32, r=15, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial, sans-serif", color="#425971", size=12),
        legend=dict(orientation="h", x=0, y=1.17, xanchor="left", yanchor="top"),
        hovermode="closest",
        clickmode="event+select",
        transition=dict(duration=180),
    )
    fig.update_xaxes(
        title_text="Vértice inicial",
        showgrid=False,
        linecolor="#DCE5EC",
        tickfont=dict(size=12),
    )
    limite = max(
        [
            RESULTADOS[v][k]
            for v in VERTICES
            for k in ("costo_doble", "costo_christofides")
        ]
        + [COSTO_OPTIMO or 0]
    )
    fig.update_yaxes(
        title_text="Costo (escala desde 80)",
        range=[80, limite + 5],
        tickmode="linear",
        tick0=80,
        dtick=5,
        gridcolor="#E9EEF2",
        zeroline=False,
        tickfont=dict(size=11),
    )
    return fig


def tarjeta_grafo(titulo, id_grafo, id_ruta, id_tooltip, color, circuito):
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "CICLO HAMILTONIANO", className="gl-cm-sobretitulo"
                            ),
                            html.H3(titulo),
                        ]
                    ),
                    html.Span(
                        "Pasa el cursor sobre una arista para ver su peso",
                        className="gl-cm-instruccion",
                    ),
                ],
                className="gl-cm-grafo-titulo",
            ),
            html.Div(
                [
                    cyto.Cytoscape(
                        id=id_grafo,
                        layout={"name": "preset", "fit": True, "padding": 35},
                        elements=elementos_circuito(circuito),
                        stylesheet=estilo_grafo(color),
                        className="gl-cm-grafo",
                        style={"width": "100%", "height": "350px"},
                        autoungrabify=True,
                        clearOnUnhover=True,
                    ),
                    html.Div(id=id_tooltip, className="gl-cm-tooltip"),
                ],
                className="gl-cm-grafo-contenedor",
            ),
            html.Div(texto_circuito(circuito), id=id_ruta, className="gl-cm-recorrido"),
        ],
        className="gl-cm-tarjeta gl-cm-tarjeta-grafo",
    )


def tarjeta_kpi(etiqueta, valor, clase, id_valor, id_detalle=None, detalle=""):
    return html.Div(
        [
            html.Span(etiqueta, className="gl-cm-kpi-etiqueta"),
            html.Strong(str(valor), id=id_valor, className="gl-cm-kpi-valor"),
            html.Span(detalle, id=id_detalle, className="gl-cm-kpi-detalle")
            if id_detalle
            else html.Span(detalle, className="gl-cm-kpi-detalle"),
        ],
        className=f"gl-cm-kpi gl-cm-kpi-{clase}",
    )


def crear_pagina():
    inicio = "g" if "g" in RESULTADOS else VERTICES[0]
    datos = RESULTADOS[inicio]
    diferencia, etiqueta, _ = resumen_diferencia(datos)
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "ANÁLISIS COMPARATIVO", className="gl-cm-sobretitulo"
                            ),
                            html.H2("Comparación de algoritmos"),
                            html.P(
                                "Dos aproximaciones al TSP métrico, sobre el mismo grafo y con el mismo origen."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label(
                                        "Vértice inicial", htmlFor="comparacion-inicio"
                                    ),
                                    dcc.Dropdown(
                                        id="comparacion-inicio",
                                        options=[
                                            {"label": v, "value": v} for v in VERTICES
                                        ],
                                        value=inicio,
                                        clearable=False,
                                        searchable=False,
                                    ),
                                ],
                                className="gl-cm-origen",
                            ),
                            html.Div(
                                [
                                    dbc.Switch(
                                        id="comparacion-diferencias",
                                        label="Destacar diferencias",
                                        value=False,
                                        className="gl-cm-switch",
                                    ),
                                ],
                                className="gl-cm-filtro",
                            ),
                        ],
                        className="gl-cm-filtros",
                    ),
                ],
                className="gl-cm-intro",
            ),
            html.Div(
                [
                    tarjeta_kpi(
                        "Doble árbol · 2-TSP",
                        datos["costo_doble"],
                        "doble",
                        "comparacion-doble-costo",
                        detalle="Costo final",
                    ),
                    tarjeta_kpi(
                        "Christofides",
                        datos["costo_christofides"],
                        "christofides",
                        "comparacion-christofides-costo",
                        detalle="Costo final",
                    ),
                    tarjeta_kpi(
                        "Diferencia",
                        diferencia,
                        "diferencia",
                        "comparacion-diferencia",
                        "comparacion-diferencia-etiqueta",
                        etiqueta,
                    ),
                ],
                className="gl-cm-kpis",
            ),
            html.Div(
                [
                    tarjeta_grafo(
                        "Doble árbol · 2-TSP",
                        "comparacion-doble-grafo",
                        "comparacion-doble-ruta",
                        "comparacion-tooltip-doble",
                        COLOR_DOBLE,
                        datos["doble"],
                    ),
                    tarjeta_grafo(
                        "Christofides",
                        "comparacion-christofides-grafo",
                        "comparacion-christofides-ruta",
                        "comparacion-tooltip-christofides",
                        COLOR_CHRISTOFIDES,
                        datos["christofides"],
                    ),
                ],
                className="gl-cm-grafos",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                [
                                    html.Span(
                                        "●", className="gl-cm-leyenda-compartida"
                                    ),
                                    " Arista compartida",
                                ],
                                className="gl-cm-leyenda-item",
                            ),
                            html.Span(
                                [
                                    html.Span("●", className="gl-cm-leyenda-doble"),
                                    " Exclusiva de doble árbol",
                                ],
                                className="gl-cm-leyenda-item",
                            ),
                            html.Span(
                                [
                                    html.Span(
                                        "●", className="gl-cm-leyenda-christofides"
                                    ),
                                    " Exclusiva de Christofides",
                                ],
                                className="gl-cm-leyenda-item",
                            ),
                        ],
                        id="comparacion-leyenda-diferencias",
                        className="gl-cm-leyenda-oculta",
                    ),
                    html.Section(
                        [
                            html.H3("¿Qué observamos?"),
                            html.Div(
                                mensaje_comparacion(datos),
                                id="comparacion-conclusion",
                                **{"aria-live": "polite"},
                            ),
                        ],
                        className="gl-cm-tarjeta gl-cm-conclusion",
                    ),
                ],
                className="gl-cm-bloque-conclusion",
            ),
            html.Details(
                [
                    html.Summary("Desglose de costos y construcción"),
                    html.Div(
                        tabla_costos(datos),
                        id="comparacion-costos",
                        className="gl-cm-tabla-contenedor",
                    ),
                ],
                className="gl-cm-detalles",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "EXPLORACIÓN DE RESULTADOS",
                                        className="gl-cm-sobretitulo",
                                    ),
                                    html.H3(
                                        "¿Qué ocurre al cambiar el vértice inicial?"
                                    ),
                                ]
                            ),
                            html.Span(
                                f"Óptimo exacto: {COSTO_OPTIMO}",
                                className="gl-cm-optimo",
                            ),
                        ],
                        className="gl-cm-seccion-cabecera",
                    ),
                    html.P(
                        "Haz clic en una barra para comparar los recorridos desde ese origen.",
                        className="gl-cm-texto-secundario",
                    ),
                    dcc.Graph(
                        id="comparacion-grafico-origenes",
                        figure=figura_costos(inicio),
                        config={"displayModeBar": False, "responsive": True},
                        className="gl-cm-grafico-barras",
                        style={"height": "275px", "width": "100%"},
                    ),
                    html.P(
                        "La heurística puede construir ciclos distintos según el origen. "
                        "Cambiar el origen no modifica el TSP óptimo del grafo.",
                        className="gl-cm-texto-secundario gl-cm-nota-grafico",
                    ),
                    html.Details(
                        [
                            html.Summary("Ver tabla completa de los siete orígenes"),
                            html.Div(
                                tabla_origenes(inicio),
                                id="comparacion-tabla-origenes",
                                className="gl-cm-tabla-contenedor",
                            ),
                        ],
                        className="gl-cm-detalles gl-cm-detalles-interno",
                    ),
                ],
                className="gl-cm-tarjeta gl-cm-analisis",
            ),
        ],
        className="pagina-algoritmo pagina-comparacion",
    )


def contenido_hover_arista(datos):
    if not datos or datos.get("peso") is None:
        return [], "gl-cm-tooltip"
    estado = datos.get("estado", "normal")
    etiquetas = {
        "compartida": "COMPARTIDA POR AMBOS CICLOS",
        "exclusiva": "EXCLUSIVA DE ESTE CICLO",
        "normal": "ARISTA DEL CIRCUITO",
    }
    return [
        html.Span(
            etiquetas.get(estado, "ARISTA"), className="gl-cm-tooltip-sobretitulo"
        ),
        html.Div(
            [
                html.Strong(datos.get("arista", "—"), className="gl-cm-tooltip-arista"),
                html.Div(
                    [
                        html.Span("Peso", className="gl-cm-tooltip-etiqueta"),
                        html.Strong(
                            str(datos["peso"]), className="gl-cm-tooltip-valor"
                        ),
                    ],
                    className="gl-cm-tooltip-peso",
                ),
            ],
            className="gl-cm-tooltip-fila",
        ),
    ], "gl-cm-tooltip gl-cm-tooltip-visible"


def registrar_callbacks(app):
    @app.callback(
        Output("comparacion-doble-grafo", "elements"),
        Output("comparacion-christofides-grafo", "elements"),
        Output("comparacion-doble-costo", "children"),
        Output("comparacion-christofides-costo", "children"),
        Output("comparacion-diferencia", "children"),
        Output("comparacion-diferencia-etiqueta", "children"),
        Output("comparacion-doble-ruta", "children"),
        Output("comparacion-christofides-ruta", "children"),
        Output("comparacion-conclusion", "children"),
        Output("comparacion-costos", "children"),
        Output("comparacion-tabla-origenes", "children"),
        Output("comparacion-grafico-origenes", "figure"),
        Output("comparacion-leyenda-diferencias", "className"),
        Input("comparacion-inicio", "value"),
        Input("comparacion-diferencias", "value"),
    )
    def actualizar_comparacion(inicio, destacar):
        if inicio not in RESULTADOS:
            inicio = VERTICES[0]
        datos = RESULTADOS[inicio]
        grafo_doble, grafo_chris = datos_para_vista(inicio, bool(destacar))
        diferencia, etiqueta, _ = resumen_diferencia(datos)
        return (
            grafo_doble,
            grafo_chris,
            str(datos["costo_doble"]),
            str(datos["costo_christofides"]),
            diferencia,
            etiqueta,
            texto_circuito(datos["doble"]),
            texto_circuito(datos["christofides"]),
            mensaje_comparacion(datos),
            tabla_costos(datos),
            tabla_origenes(inicio),
            figura_costos(inicio),
            "gl-cm-leyenda" if destacar else "gl-cm-leyenda-oculta",
        )

    @app.callback(
        Output("comparacion-inicio", "value"),
        Input("comparacion-grafico-origenes", "clickData"),
        prevent_initial_call=True,
    )
    def elegir_origen_desde_grafico(click_data):
        if not click_data or not click_data.get("points"):
            return no_update
        origen = click_data["points"][0].get("x")
        return origen if origen in RESULTADOS else no_update

    @app.callback(
        Output("comparacion-tooltip-doble", "children"),
        Output("comparacion-tooltip-doble", "className"),
        Input("comparacion-doble-grafo", "mouseoverEdgeData"),
        Input("comparacion-doble-grafo", "tapEdgeData"),
        Input("comparacion-inicio", "value"),
        Input("comparacion-diferencias", "value"),
    )
    def hover_doble(hover, tap, _inicio, _destacar):
        activadores = ctx.triggered_prop_ids
        if "comparacion-doble-grafo.tapEdgeData" in activadores:
            return contenido_hover_arista(tap)
        if "comparacion-doble-grafo.mouseoverEdgeData" in activadores:
            return contenido_hover_arista(hover)
        return [], "gl-cm-tooltip"

    @app.callback(
        Output("comparacion-tooltip-christofides", "children"),
        Output("comparacion-tooltip-christofides", "className"),
        Input("comparacion-christofides-grafo", "mouseoverEdgeData"),
        Input("comparacion-christofides-grafo", "tapEdgeData"),
        Input("comparacion-inicio", "value"),
        Input("comparacion-diferencias", "value"),
    )
    def hover_christofides(hover, tap, _inicio, _destacar):
        activadores = ctx.triggered_prop_ids
        if "comparacion-christofides-grafo.tapEdgeData" in activadores:
            return contenido_hover_arista(tap)
        if "comparacion-christofides-grafo.mouseoverEdgeData" in activadores:
            return contenido_hover_arista(hover)
        return [], "gl-cm-tooltip"

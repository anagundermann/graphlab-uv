"""Biblioteca matemática navegable: definiciones, dibujos y demostraciones."""

from dash import ALL, Input, Output, ctx, dcc, html, no_update
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from models.biblioteca_data import CATEGORIAS, CONCEPTOS


# Dibujos esquemáticos. No representan pesos del problema de GraphLab.
POS = {
    "a": {"x": 65, "y": 125},
    "b": {"x": 190, "y": 45},
    "c": {"x": 185, "y": 215},
    "d": {"x": 335, "y": 105},
    "e": {"x": 405, "y": 220},
    "f": {"x": 485, "y": 55},
}

BASE = [
    ("a", "b"),
    ("a", "c"),
    ("b", "c"),
    ("b", "d"),
    ("c", "d"),
    ("d", "e"),
    ("d", "f"),
    ("e", "f"),
]
ARBOL = [("a", "b"), ("b", "c"), ("b", "d"), ("d", "e"), ("d", "f")]
CICLO = [("a", "b"), ("b", "f"), ("f", "e"), ("e", "d"), ("d", "c"), ("c", "a")]


def elementos_figura(tipo):
    if not tipo:
        return []
    if tipo == "matching":
        pares = [("a", "b"), ("a", "c"), ("a", "d"), ("b", "c"), ("b", "d"), ("c", "d")]
        principales = {frozenset(x) for x in [("a", "c"), ("b", "d")]}
        vertices = ["a", "b", "c", "d"]
    elif tipo == "completo":
        vertices = ["a", "b", "c", "d"]
        pares = [(u, v) for i, u in enumerate(vertices) for v in vertices[i + 1 :]]
        principales = {frozenset(x) for x in pares}
    elif tipo in ("hamiltoniano", "ciclo"):
        vertices = list(POS)
        pares = list(dict.fromkeys(CICLO + [("b", "c"), ("b", "d"), ("d", "f")]))
        principales = {frozenset(x) for x in CICLO}
    elif tipo == "componentes":
        vertices = list(POS)
        pares = [("a", "b"), ("a", "c"), ("b", "c"), ("d", "e"), ("d", "f")]
        principales = {frozenset(x) for x in pares}
    elif tipo == "bosque":
        vertices = list(POS)
        pares = [("a", "b"), ("b", "c"), ("d", "e"), ("d", "f")]
        principales = {frozenset(x) for x in pares}
    elif tipo in ("arbol", "euleriano", "multigrafo"):
        vertices = list(POS)
        pares = ARBOL if tipo != "euleriano" else CICLO
        principales = {frozenset(x) for x in pares}
    elif tipo == "camino":
        vertices = list(POS)
        pares = BASE
        principales = {frozenset(x) for x in [("a", "b"), ("b", "d"), ("d", "e")]}
    elif tipo == "subgrafo":
        vertices = list(POS)
        pares = BASE
        principales = {frozenset(x) for x in [("a", "b"), ("a", "c"), ("b", "c")]}
    elif tipo == "corte":
        vertices = list(POS)
        pares = BASE
        principales = {frozenset(x) for x in [("b", "d"), ("c", "d")]}
    elif tipo == "atajo":
        vertices = list(POS)
        pares = BASE + [("a", "d")]
        principales = {frozenset(("a", "d"))}
    else:
        vertices = list(POS)
        pares = BASE
        principales = {frozenset(x) for x in pares}

    elementos = [
        {
            "data": {"id": v, "label": v},
            "position": POS[v].copy(),
            "classes": "grupo-derecha"
            if tipo == "componentes" and v in ("d", "e", "f")
            else "",
        }
        for v in vertices
    ]
    for i, (u, v) in enumerate(pares):
        clase = "destacada" if frozenset((u, v)) in principales else "base"
        if tipo == "corte" and clase == "destacada":
            clase = "corte"
        if tipo == "atajo" and {u, v} == {"a", "d"}:
            clase = "atajo"
        elementos.append(
            {"data": {"id": f"e-{i}", "source": u, "target": v}, "classes": clase}
        )
    if tipo == "multigrafo":
        elementos.append(
            {
                "data": {"id": "copia-adicional", "source": "a", "target": "b"},
                "classes": "copia",
            }
        )
    return elementos


ESTILO_FIGURA = [
    {
        "selector": "node",
        "style": {
            "label": "data(label)",
            "background-color": "#377b99",
            "color": "#ffffff",
            "font-size": 16,
            "font-weight": "bold",
            "text-valign": "center",
            "text-halign": "center",
            "width": 38,
            "height": 38,
        },
    },
    {"selector": "node.grupo-derecha", "style": {"background-color": "#816da8"}},
    {
        "selector": "edge",
        "style": {"line-color": "#bfccd6", "width": 2.5, "curve-style": "bezier"},
    },
    {"selector": "edge.destacada", "style": {"line-color": "#238a80", "width": 4.5}},
    {"selector": "edge.corte", "style": {"line-color": "#c58a35", "width": 5}},
    {
        "selector": "edge.atajo",
        "style": {"line-color": "#c58a35", "width": 5, "line-style": "dashed"},
    },
    {
        "selector": "edge.copia",
        "style": {
            "line-color": "#8c73b5",
            "width": 4,
            "curve-style": "bezier",
            "control-point-step-size": 48,
        },
    },
]


def tarjeta_concepto(clave):
    datos = CONCEPTOS[clave]
    elementos = [
        html.Div(
            [
                html.Span(datos["tipo"].upper(), className="gl-bib-kicker"),
                html.H2(datos["nombre"], className="gl-bib-titulo-concepto"),
            ],
            className="gl-bib-titulo-fila",
        ),
        html.Section(
            [
                html.H3("Definición formal", className="gl-bib-subtitulo"),
                dcc.Markdown(datos["formal"], mathjax=True, className="gl-bib-formula"),
            ],
            className="gl-bib-formal",
        ),
        html.Section(
            [
                html.H3("En palabras simples", className="gl-bib-subtitulo"),
                html.P(datos["sencillo"], className="gl-bib-explicacion"),
            ],
            className="gl-bib-sencillo",
        ),
    ]
    if datos["figura"]:
        elementos.append(
            html.Div(
                [
                    cyto.Cytoscape(
                        id="biblioteca-grafo",
                        elements=elementos_figura(datos["figura"]),
                        layout={"name": "preset", "fit": True, "padding": 30},
                        stylesheet=ESTILO_FIGURA,
                        style={"width": "100%", "height": "230px"},
                        userZoomingEnabled=False,
                        userPanningEnabled=False,
                        autoungrabify=True,
                    ),
                ],
                className="gl-bib-figura",
            )
        )
    if datos["propiedad"]:
        elementos.append(
            html.Section(
                [
                    html.H3("Propiedad matemática", className="gl-bib-subtitulo"),
                    dcc.Markdown(datos["propiedad"], mathjax=True),
                ],
                className="gl-bib-propiedad",
            )
        )
    if datos["demostracion"]:
        elementos.append(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        dcc.Markdown(
                            datos["demostracion"],
                            mathjax=True,
                            className="gl-bib-demostracion",
                        ),
                        title="Ver demostración formal",
                    )
                ],
                start_collapsed=True,
                className="gl-bib-prueba",
            )
        )
    if datos["relacionados"]:
        elementos.append(
            html.Section(
                [
                    html.H3("Conceptos relacionados", className="gl-bib-subtitulo"),
                    html.Div(
                        [
                            html.Button(
                                CONCEPTOS[otro]["nombre"],
                                type="button",
                                n_clicks=0,
                                id={"type": "biblioteca-relacionado", "index": otro},
                                className="gl-bib-relacionado",
                            )
                            for otro in datos["relacionados"]
                        ],
                        className="gl-bib-relacionados",
                    ),
                ],
                className="gl-bib-relaciones",
            )
        )
    return html.Article(elementos, className="gl-bib-articulo")


def crear_pagina():
    lista = [
        dbc.AccordionItem(
            [
                html.Button(
                    CONCEPTOS[clave]["nombre"],
                    type="button",
                    n_clicks=0,
                    id={"type": "biblioteca-item", "index": clave},
                    className="gl-bib-item",
                )
                for clave in claves
            ],
            title=categoria,
            item_id=f"categoria-{i}",
        )
        for i, (categoria, claves) in enumerate(CATEGORIAS.items())
    ]
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "RECURSOS DE APRENDIZAJE", className="gl-bib-kicker"
                            ),
                            html.H2(
                                "Biblioteca matemática",
                                className="gl-bib-encabezado-titulo",
                            ),
                            html.P(
                                "Definiciones formales, interpretaciones y demostraciones para el TSP métrico.",
                                className="gl-bib-encabezado-texto",
                            ),
                        ]
                    ),
                    html.Button(
                        "← Volver a la sección anterior",
                        id={
                            "type": "graphlab-biblioteca-volver",
                            "index": "biblioteca",
                        },
                        n_clicks=0,
                        type="button",
                        className="gl-bib-volver",
                    ),
                ],
                className="gl-bib-cabecera",
            ),
            html.Div(
                [
                    html.Aside(
                        [
                            html.Label(
                                "Buscar concepto",
                                htmlFor="biblioteca-selector",
                                className="gl-bib-buscador-label",
                            ),
                            dcc.Dropdown(
                                id="biblioteca-selector",
                                options=[
                                    {"label": d["nombre"], "value": clave}
                                    for clave, d in CONCEPTOS.items()
                                ],
                                value="tsp",
                                searchable=True,
                                clearable=False,
                                placeholder="Escribe un concepto...",
                                className="gl-bib-selector",
                            ),
                            html.Div(
                                "Explorar por tema", className="gl-bib-indice-titulo"
                            ),
                            dbc.Accordion(
                                lista,
                                active_item="categoria-3",
                                always_open=False,
                                className="gl-bib-indice",
                            ),
                            html.P(
                                f"{len(CONCEPTOS)} conceptos organizados en cuatro áreas.",
                                className="gl-bib-contador",
                            ),
                        ],
                        className="gl-bib-lateral",
                    ),
                    html.Div(
                        tarjeta_concepto("tsp"),
                        id="biblioteca-contenido",
                        className="gl-bib-lectura",
                    ),
                ],
                className="gl-bib-columnas",
            ),
            html.P(
                "Definiciones redactadas para GraphLab UV a partir de terminología matemática "
                "estándar. No son transcripciones literales de Korte y Vygen. "
                "Referencia temática: Korte y Vygen, Combinatorial Optimization: Theory and Algorithms, 6.ª ed.",
                className="gl-bib-nota-fuente",
            ),
        ],
        className="gl-bib-pagina",
    )


def registrar_callbacks(app):
    @app.callback(
        Output("biblioteca-selector", "value"),
        Input({"type": "biblioteca-item", "index": ALL}, "n_clicks"),
        Input({"type": "biblioteca-relacionado", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def elegir_concepto(_indice, _relacionado):
        activador = ctx.triggered_id
        if not isinstance(activador, dict) or not ctx.triggered[0].get("value"):
            return no_update
        clave = activador.get("index")
        return clave if clave in CONCEPTOS else no_update

    @app.callback(
        Output("biblioteca-contenido", "children"),
        Input("biblioteca-selector", "value"),
    )
    def mostrar_concepto(clave):
        return tarjeta_concepto(clave if clave in CONCEPTOS else "tsp")

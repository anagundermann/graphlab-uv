"""Explorador de código fuente: archivos reales de models y guía sincronizada."""

from dash import html, dcc, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc

from models.grafo_data import VERTICES
from models.analizador_codigo import NOMBRES, estado, fragmentos_coloreados


def crear_pagina(algoritmo="kruskal"):
    if algoritmo not in NOMBRES:
        algoritmo = "kruskal"
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                "EXPLORADOR DE CÓDIGO FUENTE",
                                className="gl-codigo-eyebrow",
                            ),
                            html.H2("Código Python de los algoritmos"),
                            html.P(
                                "El archivo original completo, coloreado como en un editor. "
                                "Las líneas iluminadas corresponden al paso de ejecución seleccionado."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Seleccionar algoritmo", htmlFor="codigo-algoritmo"
                            ),
                            dcc.Dropdown(
                                id="codigo-algoritmo",
                                value=algoritmo,
                                clearable=False,
                                searchable=False,
                                options=[
                                    {"label": nombre, "value": clave}
                                    for clave, nombre in NOMBRES.items()
                                ],
                            ),
                        ],
                        className="gl-codigo-selector",
                    ),
                ],
                className="gl-codigo-cabecera",
            ),
            html.Div(
                [
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("●", className="gl-codigo-punto"),
                                            html.Span("●", className="gl-codigo-punto"),
                                            html.Span("●", className="gl-codigo-punto"),
                                            html.Strong(
                                                id="codigo-archivo",
                                                className="gl-codigo-archivo",
                                            ),
                                        ],
                                        className="gl-codigo-barra-archivo",
                                    ),
                                    dcc.Clipboard(
                                        id="codigo-copiar",
                                        className="gl-codigo-clipboard",
                                        title="Copiar archivo completo",
                                    ),
                                ],
                                className="gl-codigo-barra",
                            ),
                            html.Div(
                                id="codigo-lineas",
                                className="gl-codigo-editor",
                                role="region",
                                **{"aria-label": "Código fuente Python completo"},
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "Archivo original de models/ · solo lectura"
                                    ),
                                    html.Span(id="codigo-total-lineas"),
                                ],
                                className="gl-codigo-pie-editor",
                            ),
                        ],
                        className="gl-codigo-tarjeta gl-codigo-visor",
                    ),
                    html.Aside(
                        [
                            html.Div(
                                [
                                    html.Span(
                                        "EJECUCIÓN GUIADA",
                                        className="gl-codigo-eyebrow",
                                    ),
                                    html.Div(
                                        id="codigo-contador",
                                        className="gl-codigo-contador",
                                    ),
                                    html.Div(
                                        html.Div(
                                            id="codigo-progreso",
                                            className="gl-codigo-progreso-valor",
                                        ),
                                        className="gl-codigo-progreso-pista",
                                    ),
                                    html.H3(
                                        id="codigo-titulo",
                                        className="gl-codigo-titulo-paso",
                                    ),
                                    html.P(
                                        id="codigo-explicacion",
                                        className="gl-codigo-explicacion",
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Span(
                                        "APLICACIÓN AL GRAFO",
                                        className="gl-codigo-eyebrow",
                                    ),
                                    html.P(
                                        id="codigo-aplicacion",
                                        className="gl-codigo-aplicacion",
                                    ),
                                    html.Button(
                                        "Ver condición de término en el código",
                                        id="codigo-ir-termino",
                                        n_clicks=0,
                                        type="button",
                                        className="gl-codigo-enlace-termino",
                                        style={"display": "none"},
                                    ),
                                ],
                                className="gl-codigo-aplicacion-panel",
                            ),
                            html.Div(
                                [
                                    dbc.Button(
                                        "← Anterior",
                                        id="codigo-anterior",
                                        color="outline-secondary",
                                    ),
                                    dbc.Button(
                                        "→ Siguiente",
                                        id="codigo-siguiente",
                                        color="primary",
                                    ),
                                    dbc.Button(
                                        "↻ Reiniciar",
                                        id="codigo-reiniciar",
                                        color="outline-secondary",
                                    ),
                                ],
                                className="gl-codigo-controles",
                            ),
                            html.Button(
                                "Volver al laboratorio",
                                id="codigo-ir-laboratorio",
                                className="gl-codigo-volver",
                                type="button",
                            ),
                            html.P(
                                "Estos controles recorren los mismos pasos del laboratorio. "
                                "Al volver al grafo, se conserva el avance seleccionado.",
                                className="gl-codigo-nota",
                            ),
                            html.Div(
                                id="codigo-scroll-hecho", style={"display": "none"}
                            ),
                            dcc.Store(id="codigo-marcador"),
                        ],
                        className="gl-codigo-tarjeta gl-codigo-guia",
                    ),
                ],
                className="gl-codigo-distribucion",
            ),
        ],
        className="pagina-codigo-fuente",
    )


def crear_lineas(codigo, marcas):
    """Renderizar cada línea de origen, sin truncar ninguna instrucción."""
    rangos = set()
    for primero, ultimo in marcas:
        rangos.update(range(primero, ultimo + 1))
    coloreadas = fragmentos_coloreados(codigo)
    return [
        html.Div(
            [
                html.Span(f"{i:03d}", className="gl-codigo-numero"),
                html.Span(
                    [html.Span(texto, className=clase) for texto, clase in fragmentos],
                    className="gl-codigo-texto",
                ),
            ],
            className="gl-codigo-linea"
            + (" gl-codigo-linea-activa" if i in rangos else ""),
            id=f"gl-codigo-linea-{i}",
        )
        for i, fragmentos in enumerate(coloreadas, 1)
    ]


def actualizar_progreso(memoria, algoritmo, paso, inicio="a"):
    """Actualizar inmutablemente solo el algoritmo seleccionado."""
    memoria = dict(memoria or {})
    ultimo = estado(algoritmo, paso, inicio)["total"]
    memoria[algoritmo] = {"paso": max(0, min(ultimo, int(paso))), "inicio": inicio}
    return memoria


def registrar_callbacks(app):
    @app.callback(
        Output("codigo-lineas", "children"),
        Output("codigo-archivo", "children"),
        Output("codigo-total-lineas", "children"),
        Output("codigo-copiar", "content"),
        Output("codigo-contador", "children"),
        Output("codigo-progreso", "style"),
        Output("codigo-titulo", "children"),
        Output("codigo-explicacion", "children"),
        Output("codigo-aplicacion", "children"),
        Output("codigo-anterior", "disabled"),
        Output("codigo-siguiente", "disabled"),
        Output("codigo-marcador", "data"),
        Output("codigo-ir-termino", "style"),
        Input("codigo-algoritmo", "value"),
        Input("graphlab-ejecucion", "data"),
    )
    def mostrar_codigo(algoritmo, memoria):
        if algoritmo not in NOMBRES:
            algoritmo = "kruskal"
        anterior = (memoria or {}).get(algoritmo, {})
        datos = estado(
            algoritmo, anterior.get("paso", 0), anterior.get("inicio", VERTICES[0])
        )
        linea_principal = datos["marcas"][0][0]
        return (
            crear_lineas(datos["codigo"], datos["marcas"]),
            f"models/{algoritmo}.py",
            f"{len(datos['codigo'].splitlines())} líneas",
            datos["codigo"],
            f"Paso {datos['paso']} de {datos['total']} · {datos['etapa']}",
            {"width": f"{100 * datos['paso'] / max(1, datos['total']):.1f}%"},
            datos["titulo"],
            datos["explicacion"],
            datos["aplicacion"],
            datos["paso"] == 0,
            datos["paso"] == datos["total"],
            f"{algoritmo}:{datos['paso']}:{linea_principal}",
            {"display": "inline-flex"}
            if algoritmo == "kruskal" and datos["paso"] == datos["total"]
            else {"display": "none"},
        )

    @app.callback(
        Output("graphlab-ejecucion", "data", allow_duplicate=True),
        Input("codigo-anterior", "n_clicks"),
        Input("codigo-siguiente", "n_clicks"),
        Input("codigo-reiniciar", "n_clicks"),
        State("codigo-algoritmo", "value"),
        State("graphlab-ejecucion", "data"),
        prevent_initial_call=True,
    )
    def recorrer_codigo(anterior, siguiente, reiniciar, algoritmo, memoria):
        activador = ctx.triggered_id
        if activador not in ("codigo-anterior", "codigo-siguiente", "codigo-reiniciar"):
            return no_update
        if not ctx.triggered[0].get("value"):
            return no_update
        if algoritmo not in NOMBRES:
            return no_update
        guardado = (memoria or {}).get(algoritmo, {})
        p = int(guardado.get("paso", 0))
        origen = guardado.get("inicio", VERTICES[0])
        p = (
            0
            if activador == "codigo-reiniciar"
            else p + (1 if activador == "codigo-siguiente" else -1)
        )
        return actualizar_progreso(memoria, algoritmo, p, origen)

    # Navega dentro del panel con desplazamiento suave, sin mover la página completa.
    app.clientside_callback(
        """function(marcador) {
            if (!marcador) return '';
            window.requestAnimationFrame(function() {
                window.requestAnimationFrame(function() {
                    const editor = document.getElementById('codigo-lineas');
                    const linea = editor && editor.querySelector('.gl-codigo-linea-activa');
                    if (editor && linea) {
                        const objetivo = linea.offsetTop
                            - editor.clientHeight / 2 + linea.clientHeight / 2;
                        editor.scrollTo({top: Math.max(0, objetivo), behavior: 'smooth'});
                    }
                });
            });
            return marcador;
        }""",
        Output("codigo-scroll-hecho", "children"),
        Input("codigo-marcador", "data"),
    )

    # Ir a la condicion de termino de Kruskal.
    app.clientside_callback(
        """
        function(clics) {
            if (!clics) {
                return "Ver condición de término";
            }

            const editor = document.getElementById("codigo-lineas");

            if (!editor) {
                return "Ver condición de término";
            }

            const lineas = editor.querySelectorAll(
                ".gl-codigo-linea-activa"
            );

            if (lineas.length === 0) {
                return "Ver condición de término";
            }

            const ultima = lineas[lineas.length - 1];

            const objetivo = ultima.offsetTop
                - editor.clientHeight / 2
                + ultima.clientHeight / 2;

            editor.scrollTo({
                top: Math.max(0, objetivo),
                behavior: "smooth"
            });

            return "Ver condición de término";
        }
        """,
        Output("codigo-ir-termino", "title"),
        Input("codigo-ir-termino", "n_clicks"),
        prevent_initial_call=True,
    )

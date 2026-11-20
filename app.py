"""GraphLab UV: laboratorio de ciclos hamiltonianos y TSP metrico."""

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, no_update
from components.conceptos import (
    crear_ventana_concepto,
    registrar_callbacks_conceptos,
)
from pages import (
    fundamentos,
    kruskal,
    doble_arbol,
    christofides,
    comparacion,
    visor_codigo,
    biblioteca_matematica,
)
from models.grafo_data import VERTICES
from models.analizador_codigo import NOMBRES

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "GraphLab UV · Optimización combinatorial"
server = app.server

SECCIONES = [
    ("explorador", "Introducción"),
    ("kruskal", "Kruskal · AGM"),
    ("doble_arbol", "Doble árbol · 2-TSP"),
    ("christofides", "Christofides"),
    ("comparacion", "Comparación"),
    ("codigo", "Código Python"),
    ("biblioteca", "Biblioteca matemática ↗"),
]
PAGINAS = {
    "explorador": fundamentos,
    "kruskal": kruskal,
    "doble_arbol": doble_arbol,
    "christofides": christofides,
    "comparacion": comparacion,
    "codigo": visor_codigo,
    "biblioteca": biblioteca_matematica,
}


def boton_seccion(clave, etiqueta):
    return html.Button(
        etiqueta,
        id={"type": "graphlab-nav", "index": clave},
        className="graphlab-nav-boton",
        n_clicks=0,
        type="button",
        **{"aria-label": f"Abrir sección {etiqueta}"},
    )


app.layout = html.Div(
    className="graphlab-app",
    children=[
        dcc.Store(id="graphlab-pagina", data="explorador"),
        dcc.Store(id="graphlab-biblioteca-origen", data="explorador"),
        dcc.Store(
            id="graphlab-codigo-algoritmo", data="kruskal", storage_type="session"
        ),
        dcc.Store(
            id="graphlab-ejecucion",
            storage_type="memory",
            data={nombre: {"paso": 0, "inicio": VERTICES[0]} for nombre in NOMBRES},
        ),
        html.Header(
            className="graphlab-encabezado",
            children=[
                html.Div(
                    [
                        html.H1("GraphLab UV", className="graphlab-titulo"),
                        html.Span(
                            "·",
                            className="graphlab-header-punto graphlab-header-punto-uv",
                            **{"aria-hidden": "true"},
                        ),
                        html.Span(
                            "Universidad de Valparaíso",
                            className="graphlab-header-universidad",
                        ),
                        html.Span(
                            "·",
                            className="graphlab-header-punto graphlab-header-punto-descripcion",
                            **{"aria-hidden": "true"},
                        ),
                        html.Span(
                            "Optimización combinatorial",
                            className="graphlab-header-descripcion",
                        ),
                    ],
                    className="graphlab-marca-lineal",
                ),
            ],
        ),
        html.Nav(
            className="graphlab-navegacion",
            children=[boton_seccion(clave, etiqueta) for clave, etiqueta in SECCIONES],
            **{"aria-label": "Navegación de algoritmos"},
        ),
        html.Main(id="contenido_pagina", className="graphlab-contenido"),
        html.Footer(
            [
                html.Span("GraphLab UV · Optimización combinatorial"),
                html.Span("Ana Gundermann · 2026"),
            ],
            className="graphlab-pie",
        ),
        crear_ventana_concepto(),
    ],
)


@app.callback(
    Output("graphlab-pagina", "data"),
    Output("graphlab-codigo-algoritmo", "data"),
    Output("graphlab-biblioteca-origen", "data"),
    Input({"type": "graphlab-nav", "index": dash.ALL}, "n_clicks"),
    Input({"type": "graphlab-abrir-codigo", "index": dash.ALL}, "n_clicks"),
    Input({"type": "graphlab-intro-biblioteca", "index": dash.ALL}, "n_clicks"),
    Input({"type": "graphlab-biblioteca-volver", "index": dash.ALL}, "n_clicks"),
    State("graphlab-pagina", "data"),
    State("graphlab-biblioteca-origen", "data"),
    prevent_initial_call=True,
)
def navegar(
    clicks,
    abrir_codigo,
    abrir_biblioteca,
    volver_biblioteca,
    pagina_actual,
    pagina_anterior,
):
    activador = dash.ctx.triggered_id
    if not dash.ctx.triggered[0].get("value"):
        return no_update, no_update, no_update

    if (
        isinstance(activador, dict)
        and activador.get("type") == "graphlab-biblioteca-volver"
    ):
        destino = (
            pagina_anterior
            if pagina_anterior in PAGINAS and pagina_anterior != "biblioteca"
            else "explorador"
        )
        return destino, no_update, no_update

    if (
        isinstance(activador, dict)
        and activador.get("type") == "graphlab-intro-biblioteca"
    ):
        origen = (
            pagina_actual
            if pagina_actual in PAGINAS and pagina_actual != "biblioteca"
            else "explorador"
        )
        return "biblioteca", no_update, origen

    if isinstance(activador, dict) and activador.get("type") == "graphlab-nav":
        pagina = activador.get("index")
        if pagina not in PAGINAS:
            return no_update, no_update, no_update
        if pagina == "biblioteca":
            origen = (
                pagina_actual
                if pagina_actual in PAGINAS and pagina_actual != "biblioteca"
                else pagina_anterior
            )
            return "biblioteca", no_update, origen
        return pagina, no_update, no_update

    if isinstance(activador, dict) and activador.get("type") == "graphlab-abrir-codigo":
        seleccion = activador.get("index")
        return (
            ("codigo", seleccion, no_update)
            if seleccion in NOMBRES
            else (no_update,) * 3
        )
    return no_update, no_update, no_update


@app.callback(
    Output("graphlab-codigo-algoritmo", "data", allow_duplicate=True),
    Input("codigo-algoritmo", "value"),
    prevent_initial_call=True,
)
def guardar_seleccion_codigo(algoritmo):
    return algoritmo if algoritmo in NOMBRES else no_update


@app.callback(
    Output("graphlab-pagina", "data", allow_duplicate=True),
    Input("codigo-ir-laboratorio", "n_clicks"),
    State("codigo-algoritmo", "value"),
    prevent_initial_call=True,
)
def volver_al_laboratorio(clicks, algoritmo):
    return algoritmo if clicks and algoritmo in NOMBRES else no_update


@app.callback(
    Output("contenido_pagina", "children"),
    [
        Output({"type": "graphlab-nav", "index": clave}, "className")
        for clave, _ in SECCIONES
    ],
    Input("graphlab-pagina", "data"),
    State("graphlab-codigo-algoritmo", "data"),
    State("graphlab-ejecucion", "data"),
)
def mostrar_pagina(pagina, algoritmo_seleccionado, memoria):
    modulo = PAGINAS.get(pagina, fundamentos)
    clases = [
        "graphlab-nav-boton" + (" activo" if pagina == clave else "")
        for clave, _ in SECCIONES
    ]
    if pagina == "codigo":
        pagina_actual = visor_codigo.crear_pagina(algoritmo_seleccionado)
    elif pagina in NOMBRES:
        datos = (memoria or {}).get(pagina, {})
        pagina_actual = modulo.crear_pagina(
            paso_inicial=datos.get("paso", 0),
            inicio_inicial=datos.get("inicio", VERTICES[0]),
        )
    else:
        pagina_actual = modulo.crear_pagina()
    return pagina_actual, *clases


def registrar_progreso(app, algoritmo, identificador_paso, identificador_origen=None):
    """Observar el avance real del laboratorio sin duplicar sus cálculos."""
    entradas = [Input(identificador_paso, "data")]
    if identificador_origen is not None:
        entradas.append(Input(identificador_origen, "value"))

    @app.callback(
        Output("graphlab-ejecucion", "data", allow_duplicate=True),
        *entradas,
        State("graphlab-ejecucion", "data"),
        prevent_initial_call=True,
    )
    def conservar_paso(*argumentos):
        if identificador_origen is None:
            paso, memoria = argumentos
            inicio = VERTICES[0]
        else:
            paso, inicio, memoria = argumentos
        if not isinstance(paso, int):
            return no_update
        if inicio not in VERTICES:
            inicio = VERTICES[0]
        memoria = dict(memoria or {})
        nuevo = {"paso": paso, "inicio": inicio}
        if memoria.get(algoritmo) == nuevo:
            return no_update
        memoria[algoritmo] = nuevo
        return memoria


registrar_callbacks_conceptos(app)
kruskal.registrar_callbacks(app)
doble_arbol.registrar_callbacks(app)
christofides.registrar_callbacks(app)
comparacion.registrar_callbacks(app)
visor_codigo.registrar_callbacks(app)
biblioteca_matematica.registrar_callbacks(app)
registrar_progreso(app, "kruskal", "kruskal-paso")
registrar_progreso(app, "doble_arbol", "doble-paso", "doble-inicio")
registrar_progreso(app, "christofides", "christofides-paso", "christofides-inicio")

if __name__ == "__main__":
    app.run(debug=False, port=8081)

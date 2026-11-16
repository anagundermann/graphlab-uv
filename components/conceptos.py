# ==========================================
# 1. IMPORTACIONES
# ==========================================

from dash import html, dcc, Input, Output, ctx, ALL, no_update
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from models.conceptos_data import vertices, conceptos


# ==========================================
# 2. LISTADO DE CONCEPTOS
# ==========================================


def crear_lista_conceptos():

    return html.Div(
        [
            html.H2("Fundamentos de grafos"),
            html.P(
                "Selecciona un concepto para consultar "
                "su definición y observar un ejemplo."
            ),
            html.Div(
                [
                    dbc.Button(
                        datos["nombre"],
                        id={"type": "abrir-concepto", "index": clave},
                        color="light",
                        className="boton-concepto",
                    )
                    for clave, datos in conceptos.items()
                ],
                className="lista-conceptos",
            ),
        ],
        className="panel-conceptos",
    )


# ==========================================
# 3. MENÚ DESPLEGABLE DE CONCEPTOS
# ==========================================


def crear_caja_conceptos(claves, ubicacion):

    opciones = []

    for clave in claves:
        if clave in conceptos:
            opciones.append(
                dbc.DropdownMenuItem(
                    conceptos[clave]["nombre"],
                    id={"type": "abrir-concepto", "index": f"{ubicacion}:{clave}"},
                    n_clicks=0,
                )
            )

    return dbc.DropdownMenu(
        label="Consultar conceptos",
        children=opciones,
        color="primary",
        direction="down",
        className="menu-conceptos",
    )


# ==========================================
# 4. VENTANA EMERGENTE DEL CONCEPTO
# ==========================================


def crear_ventana_concepto():

    return dbc.Modal(
        [
            # Encabezado
            dbc.ModalHeader(dbc.ModalTitle(id="modal-titulo"), close_button=False),
            # Contenido
            dbc.ModalBody(
                [
                    html.Div(
                        [
                            # Grafo
                            html.Div(
                                [
                                    cyto.Cytoscape(
                                        id="modal-grafo",
                                        layout={"name": "preset"},
                                        elements=[],
                                        style={"width": "100%", "height": "260px"},
                                        stylesheet=[
                                            {
                                                "selector": "node",
                                                "style": {
                                                    "background-color": "#147FA6",
                                                    "label": "data(label)",
                                                    "color": "white",
                                                    "text-valign": "center",
                                                    "text-halign": "center",
                                                    "width": 42,
                                                    "height": 42,
                                                },
                                            },
                                            {
                                                "selector": "edge",
                                                "style": {
                                                    "line-color": "#10A37F",
                                                    "width": 4,
                                                },
                                            },
                                        ],
                                    )
                                ],
                                className="grafo-concepto",
                            ),
                            # Definición y explicación
                            html.Div(
                                [
                                    html.H5("Definición"),
                                    dcc.Markdown(id="modal-definicion", mathjax=True),
                                    html.H5("En palabras simples"),
                                    html.P(id="modal-explicacion"),
                                ],
                                className="explicacion-concepto",
                            ),
                        ],
                        className="contenido-concepto",
                    )
                ]
            ),
            # Botón de cierre
            dbc.ModalFooter(
                dbc.Button("Cerrar", id="cerrar-modal-concepto", color="secondary")
            ),
        ],
        id="modal-conceptos",
        is_open=False,
        size="lg",
        centered=True,
        scrollable=True,
    )


# ==========================================
# 5. INTERACTIVIDAD (CALLBACKS)
# ==========================================


def registrar_callbacks_conceptos(app):

    @app.callback(
        Output("modal-conceptos", "is_open"),
        Output("modal-titulo", "children"),
        Output("modal-grafo", "elements"),
        Output("modal-definicion", "children"),
        Output("modal-explicacion", "children"),
        Input({"type": "abrir-concepto", "index": ALL}, "n_clicks"),
        Input("cerrar-modal-concepto", "n_clicks"),
        prevent_initial_call=True,
    )
    def actualizar_ventana(clicks, cerrar):

        # Identificar qué componente activó el callback
        identificador = ctx.triggered_id

        # --------------------------------------
        # CASO 1: CERRAR LA VENTANA
        # --------------------------------------

        if identificador == "cerrar-modal-concepto":
            if ctx.triggered[0]["value"]:
                return (False, no_update, no_update, no_update, no_update)

            return (no_update,) * 5

        # --------------------------------------
        # CASO 2: IGNORAR ACTIVACIONES AUTOMÁTICAS
        # --------------------------------------

        if not isinstance(identificador, dict):
            return (no_update,) * 5

        if not ctx.triggered[0]["value"]:
            return (no_update,) * 5

        # --------------------------------------
        # CASO 3: SELECCIONAR UN CONCEPTO
        # --------------------------------------

        clave = identificador["index"].split(":")[-1]

        if clave not in conceptos:
            return (no_update,) * 5

        datos = conceptos[clave]

        # Crear los vértices
        elementos = [vertice.copy() for vertice in vertices]

        # Agregar las aristas del concepto
        for origen, destino in datos["aristas"]:
            elementos.append({"data": {"source": origen, "target": destino}})

        # Abrir la ventana con el concepto elegido
        return (
            True,
            datos["nombre"],
            elementos,
            datos["definicion"],
            datos["explicacion"],
        )

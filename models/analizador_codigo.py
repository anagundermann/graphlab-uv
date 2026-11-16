"""Mapeo educativo entre pasos de GraphLab y el código fuente Python REAL.

No ejecuta código de usuario y no altera modelos existentes.
Los bloques se localizan por texto en el archivo real para evitar números de línea
codificados que se desactualicen cuando alguien edite una función.
"""
from pathlib import Path
import io
import keyword
import tokenize
import builtins

from models.grafo_data import VERTICES
from models import kruskal, doble_arbol, christofides

DIRECTORIO_MODELOS = Path(__file__).resolve().parent
NOMBRES = {
    "kruskal": "Kruskal",
    "doble_arbol": "Doble árbol · 2-TSP",
    "christofides": "Christofides",
}


def leer_codigo(algoritmo):
    """Leer sin alterar el archivo verdadero; solo aceptar nombres conocidos."""
    if algoritmo not in NOMBRES:
        raise ValueError("Algoritmo no permitido")
    return (DIRECTORIO_MODELOS / f"{algoritmo}.py").read_text(encoding="utf-8")


def linea_del_codigo(codigo, fragmento, ocurrencia=0):
    halladas = [i for i, linea in enumerate(codigo.splitlines(), 1) if fragmento in linea]
    if len(halladas) <= ocurrencia:
        raise ValueError(f"No se encontró el bloque del código: {fragmento}")
    return halladas[ocurrencia]


def bloque(codigo, inicio, fin=None, anterior=0, siguiente=0):
    """Rango de código auténtico inclusivo (1-indexado)."""
    i = linea_del_codigo(codigo, inicio)
    j = linea_del_codigo(codigo, fin) if fin else i
    return (max(1, i - anterior), min(len(codigo.splitlines()), j + siguiente))


def estado(algoritmo, paso=0, inicio="a"):
    """El mismo estado ya calculado por los modelos, con explicación didáctica."""
    if algoritmo not in NOMBRES:
        raise ValueError("Algoritmo no permitido")
    inicio = inicio if inicio in VERTICES else VERTICES[0]
    fuente = leer_codigo(algoritmo)
    if algoritmo == "kruskal":
        pasos = kruskal.PASOS
        paso = max(0, min(int(paso), len(pasos)-1))
        actual = pasos[paso]
        if paso == 0:
            titulo = "Ordenar las aristas por peso"
            explicacion = "sorted() ordena las 21 aristas por peso creciente; los vértices permiten desempatar."
            aplicacion = "Primero se examinará c–d, de peso 6. Inicialmente hay siete componentes."
            marcas = [bloque(fuente, "aristas_ordenadas = sorted(ARISTAS")]
        else:
            identificador = actual["actual"]
            aceptada = actual["estados"].get(identificador) == "aceptada"
            a, b = identificador.split("-")
            peso = next(w for u,v,w in kruskal.ARISTAS_ORDENADAS if {u,v} == {a,b})
            if aceptada:
                titulo = "Aceptar arista y unir componentes"
                explicacion = "unir(u, v) comprueba sus representantes; si son distintos, une los conjuntos y se suma el peso."
                marcas = [bloque(fuente, "if unir(u, v):", "aceptadas += 1")]
            else:
                titulo = "Rechazar arista que formaría un ciclo"
                explicacion = "Si ambos extremos ya tienen representante común, unir() devuelve False y la arista es rechazada."
                marcas = [bloque(fuente, 'estados[arista_id] = "rechazada"', anterior=1)]
            aplicacion = f"Arista {a}–{b}, peso {peso}: {'aceptada' if aceptada else 'rechazada'}. " + (f"El árbol pesa {actual['peso_total']} y tiene {actual['aceptadas']} aristas." if aceptada else f"El peso sigue en {actual['peso_total']}; no cambian las componentes.")
            if paso == len(pasos)-1:
                titulo += " · condición de término"
                marcas.append(bloque(fuente, "if aceptadas == len(VERTICES) - 1:", siguiente=1))
                aplicacion += " Con 6 = |V|−1 aristas, el árbol es generador y Kruskal termina."
        total = len(pasos)-1
        nombre_etapa = "AGM"
    else:
        modelo = doble_arbol if algoritmo == "doble_arbol" else christofides
        datos = modelo.obtener_datos(inicio)
        pasos = datos["pasos"]
        paso = max(0, min(int(paso), len(pasos)-1))
        actual = pasos[paso]
        etapa = actual["etapa"]
        avance = actual.get("avance", 0)
        nombre_etapa = etapa.capitalize()
        if algoritmo == "doble_arbol":
            if etapa == "arbol":
                titulo = "Obtener el árbol generador mínimo"
                explicacion = "Se reutilizan las aristas que Kruskal aceptó y se suman sus pesos."
                aplicacion = f"El AGM tiene {len(modelo.ARISTAS_ARBOL)} aristas y pesa {modelo.PESO_ARBOL}."
                marcas = [bloque(fuente, "ARISTAS_ARBOL = sorted(", "if ESTADOS_KRUSKAL.get")]
            elif etapa == "duplicado":
                titulo = "Duplicar conceptualmente las aristas"
                explicacion = "La búsqueda en profundidad recorrerá cada arista del árbol en ambos sentidos; equivale a recorrer sus dos copias."
                aplicacion = f"Las 6 aristas generan 12 travesías y un recorrido de costo {modelo.PESO_DOBLE}."
                marcas = [bloque(fuente, "recorrido.append(vecino)", "recorrido.append(actual)")]
            elif etapa == "euler":
                titulo = "Recorrer la siguiente copia de arista"
                explicacion = "zip() visita cada travesía consecutiva del recorrido y Counter contabiliza las copias utilizadas."
                arista = datos["travesias"][avance-1]
                aplicacion = f"Travesía {avance}/{len(datos['travesias'])}: {arista['origen']} → {arista['destino']}, peso {arista['peso']}, copia {arista['copia']}."
                marcas = [bloque(fuente, "for origen, destino in zip(recorrido[:-1], recorrido[1:]):", "veces[clave] += 1")]
            elif etapa == "seleccion":
                titulo = "Conservar las primeras visitas"
                explicacion = "dict.fromkeys(euler) conserva el orden de aparición y elimina repeticiones de vértices."
                aplicacion = "Las visitas repetidas se omitirán para construir un ciclo hamiltoniano."
                marcas = [bloque(fuente, "primeras = list(dict.fromkeys(euler))")]
            elif etapa == "atajo":
                a = datos["atajos"][avance-1]
                titulo = "Aplicar el siguiente atajo"
                explicacion = "Se reemplaza un tramo con vértices repetidos por la arista directa, respetando la desigualdad triangular."
                aplicacion = f"{a['origen']} → {a['destino']}: costo {a['costo_tramo']} → {a['costo_directo']}, ahorro {a['ahorro']}."
                marcas = [bloque(fuente, "costo_directo = PESOS[frozenset((origen, destino))]", "atajos.append(")]
            else:
                titulo = "Construir el ciclo hamiltoniano"
                explicacion = "Se cierra el recorrido de primeras visitas y se calcula su costo efectivo."
                aplicacion = f"Origen {inicio}: costo final {datos['peso_circuito']}."
                marcas = [bloque(fuente, "circuito = primeras + [inicio]"), bloque(fuente, "costo = peso_recorrido(circuito)")]
        else:
            if etapa == "arbol":
                titulo = "Obtener el árbol mínimo"
                explicacion = "El algoritmo reutiliza el mismo AGM de Kruskal."
                aplicacion = f"Peso del árbol: {modelo.PESO_ARBOL}."
                marcas = [bloque(fuente, "ARISTAS_ARBOL = sorted(", "if ESTADOS_KRUSKAL.get")]
            elif etapa == "impares":
                titulo = "Encontrar vértices de grado impar"
                explicacion = "Se cuenta el grado de cada vértice del AGM y se seleccionan los grados impares."
                aplicacion = f"Vértices impares: {', '.join(modelo.IMPARES)}."
                marcas = [bloque(fuente, "GRADOS_ARBOL ="), bloque(fuente, "IMPARES =")]
            elif etapa == "auxiliar":
                titulo = "Construir el grafo auxiliar"
                explicacion = "Se toman los vértices impares y sus distancias originales del grafo métrico."
                aplicacion = f"El grafo auxiliar tiene {len(modelo.IMPARES)} vértices."
                marcas = [bloque(fuente, "ARISTAS_AUXILIAR = [", "for v in IMPARES[i + 1 :]")]
            elif etapa == "candidato":
                opcion = modelo.OPCIONES[avance]
                titulo = "Evaluar un emparejamiento candidato"
                explicacion = "Se enumeran las parejas posibles y se suman sus pesos."
                aplicacion = " + ".join(f"{u}–{v}" for u,v in opcion["parejas"]) + f"; costo {opcion['costo']}."
                marcas = [bloque(fuente, "for parejas in enumerar_emparejamientos(IMPARES):", 'OPCIONES.append({"parejas": parejas, "costo": costo})')]
            elif etapa == "matching":
                titulo = "Elegir el matching de menor peso"
                explicacion = "min() compara el costo de todas las alternativas y selecciona la menor."
                aplicacion = f"Matching mínimo: peso {modelo.PESO_MATCHING}."
                marcas = [bloque(fuente, 'MEJOR = min(OPCIONES, key=lambda o: o["costo"])', "PESO_MATCHING = MEJOR[")]
            elif etapa == "multigrafo":
                titulo = "Añadir el matching al árbol"
                explicacion = "Cada arista conserva un ID único para distinguir copias paralelas."
                aplicacion = f"Costo: {modelo.PESO_ARBOL} + {modelo.PESO_MATCHING} = {modelo.PESO_MULTIGRAFO}."
                marcas = [bloque(fuente, "for u, v in PAREJAS_MATCHING:", siguiente=9)]
            elif etapa == "euler":
                t = datos["travesias"][avance-1]
                titulo = "Recorrido euleriano de Hierholzer"
                explicacion = "Se avanza por aristas todavía no usadas, guardando sus identificadores en una pila."
                aplicacion = f"Travesía {avance}/{len(datos['travesias'])}: {t['origen']} → {t['destino']}, peso {t['peso']}."
                marcas = [bloque(fuente, "while pila_vertices:", "usados.add(ident)")]
            elif etapa == "seleccion":
                titulo = "Conservar las primeras visitas"
                explicacion = "dict.fromkeys(euler) mantiene cada vértice solo una vez, en el orden de primera aparición."
                aplicacion = "Se prepara el circuito hamiltoniano antes de calcular los atajos."
                marcas = [bloque(fuente, "primeras = list(dict.fromkeys(euler))")]
            elif etapa == "atajo":
                a = datos["atajos"][avance-1]
                titulo = "Sustituir un tramo repetido"
                explicacion = "El peso directo se compara con el tramo eliminado; la desigualdad triangular garantiza que no aumenta."
                aplicacion = f"{a['origen']} → {a['destino']}: {a['original']} → {a['directo']}; ahorro {a['ahorro']}."
                marcas = [bloque(fuente, "nuevo = PESOS[frozenset((origen, destino))]", "atajos.append(")]
            else:
                titulo = "Calcular el circuito final"
                explicacion = "Se reúnen las primeras visitas, se vuelve al origen y se suman los pesos."
                aplicacion = f"Origen {inicio}: costo final {datos['costo']}."
                marcas = [bloque(fuente, "circuito = primeras + [inicio]"), bloque(fuente, "costo = costo_camino(circuito)")]
        total = len(pasos)-1
    return {
        "algoritmo": algoritmo, "paso": paso, "total": total, "inicio": inicio,
        "titulo": titulo, "explicacion": explicacion, "aplicacion": aplicacion,
        "marcas": marcas, "codigo": fuente, "etapa": nombre_etapa,
    }


def fragmentos_coloreados(codigo):
    """Tokenizador de Python estándar; ningún archivo se ejecuta para colorearlo.

    Devuelve [(texto, clase), ...] por línea, incluyendo espacios originales.
    """
    lineas = codigo.splitlines()
    estilos = [[] for _ in lineas]
    try:
        generador = tokenize.generate_tokens(io.StringIO(codigo).readline)
        anterior = None
        for token in generador:
            tipo, cadena, comienzo, fin, _ = token
            if tipo in (tokenize.ENDMARKER, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
                continue
            clase = "gl-tk-neutro"
            if tipo == tokenize.COMMENT:
                clase = "gl-tk-comentario"
            elif tipo == tokenize.STRING:
                clase = "gl-tk-cadena"
            elif tipo == tokenize.NUMBER:
                clase = "gl-tk-numero"
            elif tipo == tokenize.NAME:
                if keyword.iskeyword(cadena): clase = "gl-tk-palabra"
                elif anterior in ("def", "class"): clase = "gl-tk-funcion"
                elif cadena in dir(builtins): clase = "gl-tk-builtin"
            elif tipo == tokenize.OP:
                clase = "gl-tk-operador"
            for numero in range(comienzo[0], fin[0]+1):
                if numero < 1 or numero > len(lineas): continue
                a = comienzo[1] if numero == comienzo[0] else 0
                b = fin[1] if numero == fin[0] else len(lineas[numero-1])
                if b > a:
                    estilos[numero-1].append((a, b, clase))
            if tipo not in (tokenize.ENCODING,):
                anterior = cadena
    except (tokenize.TokenError, IndentationError):
        pass  # El código sigue mostrándose incluso si alguien lo edita temporalmente.
    resultado = []
    for linea, rangos in zip(lineas, estilos):
        rangos.sort(key=lambda x: (x[0], x[1]))
        trozos, cursor = [], 0
        for a, b, estilo in rangos:
            if a < cursor: continue
            if a > cursor: trozos.append((linea[cursor:a], "gl-tk-neutro"))
            trozos.append((linea[a:b], estilo))
            cursor = b
        if cursor < len(linea): trozos.append((linea[cursor:], "gl-tk-neutro"))
        resultado.append(trozos or [(" ", "gl-tk-neutro")])
    return resultado


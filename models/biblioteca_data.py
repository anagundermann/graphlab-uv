"""Contenido original de consulta de GraphLab UV.

Definiciones de teoría de grafos redactadas para el laboratorio; NO citas
literales de Korte y Vygen. Se mantienen separadas de la interfaz Dash.
"""

CATEGORIAS = {
    "Fundamentos de grafos": [
        "grafo",
        "adyacencia",
        "subgrafo",
        "subgrafo_inducido",
        "subgrafo_generador",
        "camino",
        "longitud_camino",
        "ciclo",
        "conexo",
        "componente",
        "maximal",
        "particion",
    ],
    "Árboles y Kruskal": [
        "grado",
        "arbol",
        "bosque",
        "arbol_generador",
        "peso_arbol",
        "agm",
        "corte",
        "propiedad_corte",
        "puente",
    ],
    "Doble árbol y Christofides": [
        "completo",
        "metrico",
        "multigrafo",
        "impar",
        "matching",
        "matching_perfecto",
        "matching_minimo",
        "euleriano",
        "atajo",
    ],
    "Ciclos hamiltonianos y TSP": [
        "hamiltoniano",
        "tsp",
        "peso_recorrido",
        "optimo",
        "aproximacion",
        "doble_arbol",
        "christofides",
    ],
}


def concepto(
    nombre,
    formal,
    sencillo,
    figura=None,
    propiedad=None,
    demostracion=None,
    relacionados=(),
    tipo="Definición",
):
    return {
        "nombre": nombre,
        "formal": formal.strip(),
        "sencillo": sencillo,
        "figura": figura,
        "propiedad": propiedad,
        "demostracion": demostracion,
        "relacionados": list(relacionados),
        "tipo": tipo,
    }


CONCEPTOS = {
    "grafo": concepto(
        "Grafo simple no dirigido",
        r"""
Un grafo simple no dirigido es un par $G=(V,E)$, con $V$ finito y

$$
E\subseteq\{\{u,v\}:u,v\in V,\;u\neq v\}
$$""",
        "Conjunto de vértices unidos por aristas sin dirección, lazos ni aristas paralelas.",
        "grafo",
        relacionados=("adyacencia", "subgrafo", "camino"),
    ),
    "adyacencia": concepto(
        "Vértices adyacentes",
        r"""
Dos vértices $u,v\in V$ son adyacentes si $\{u,v\}\in E$.""",
        "Dos vértices son vecinos cuando existe una arista directa entre ellos.",
        "grafo",
        relacionados=("grafo",),
    ),
    "subgrafo": concepto(
        "Subgrafo",
        r"""
$H=(V_H,E_H)$ es subgrafo de $G=(V,E)$ si $V_H\subseteq V$, $E_H\subseteq E$ y
cada arista de $E_H$ tiene ambos extremos en $V_H$.""",
        "Un grafo formado tomando algunos vértices y aristas del grafo original.",
        "subgrafo",
        relacionados=("subgrafo_inducido", "arbol_generador"),
    ),
    "subgrafo_inducido": concepto(
        "Subgrafo inducido",
        r"""
Para $S\subseteq V$, el subgrafo inducido es
$$G[S]=(S,\{\{u,v\}\in E:u,v\in S\}).$$""",
        "Conserva todas las aristas originales entre los vértices seleccionados.",
        "subgrafo",
        relacionados=("subgrafo", "componente"),
    ),
    "subgrafo_generador": concepto(
        "Subgrafo generador",
        r"""
$H$ es subgrafo generador de $G$ si $H\subseteq G$ y $V(H)=V(G)$.""",
        "Puede quitar aristas, pero conserva todos los vértices del grafo.",
        "arbol",
        relacionados=("subgrafo", "arbol_generador"),
    ),
    "camino": concepto(
        "Camino simple",
        r"""
Un camino es una sucesión $P=(v_0,\ldots,v_k)$ de vértices distintos tal que
$\{v_{i-1},v_i\}\in E$ para $i=1,\ldots,k$.""",
        "Una sucesión de vértices conectados en la que no se repiten vértices.",
        "camino",
        relacionados=("longitud_camino", "ciclo", "conexo"),
    ),
    "longitud_camino": concepto(
        "Longitud de un camino",
        r"""
Para un camino $P=(v_0,\ldots,v_k)$, su longitud es $\ell(P)=k=|E(P)|$.""",
        "La cantidad de aristas del camino, que no tiene por qué coincidir con su peso.",
        "camino",
        relacionados=("camino", "peso_recorrido"),
    ),
    "ciclo": concepto(
        "Ciclo simple",
        r"""
Un ciclo es una sucesión cerrada $C=(v_0,v_1,\ldots,v_{k-1},v_0)$,
$k\geq3$, en la que $v_0,\ldots,v_{k-1}$ son distintos y cada par
consecutivo es adyacente.""",
        "Un camino al que se agrega una arista que une sus extremos, sin repetir vértices intermedios.",
        "ciclo",
        relacionados=("camino", "hamiltoniano", "euleriano"),
    ),
    "conexo": concepto(
        "Grafo conexo",
        r"""
$G$ es conexo si para todo $u,v\in V$ existe un camino de $u$ a $v$.""",
        "Entre cualquier par de vértices existe un camino.",
        "conexo",
        relacionados=("camino", "componente", "arbol"),
    ),
    "componente": concepto(
        "Componente conexa",
        r"""
Una componente conexa es un subgrafo inducido $G[S]$ que es conexo y maximal
respecto de la inclusión de conjuntos de vértices.""",
        "Grupo conexo de vértices al que no se puede añadir otro vértice manteniendo la conectividad.",
        "componentes",
        relacionados=("conexo", "maximal", "bosque"),
    ),
    "maximal": concepto(
        "Maximal respecto de una propiedad",
        r"""
Sea $\mathcal F$ una familia de conjuntos ordenada por inclusión. $A\in\mathcal F$
es maximal si no existe $B\in\mathcal F$ con $A\subsetneq B$.""",
        "No se puede agrandar dentro de la familia admitida sin perder la propiedad. Maximal no significa necesariamente máximo en tamaño.",
        "componentes",
        relacionados=("componente", "matching"),
    ),
    "particion": concepto(
        "Partición",
        r"""
Una familia $\{V_1,\ldots,V_k\}$ es una partición de $V$ si
$V_i\neq\varnothing$, $V_i\cap V_j=\varnothing$ para $i\neq j$ y
$\bigcup_{i=1}^k V_i=V$.""",
        "Separa todos los vértices en grupos no vacíos que no se superponen.",
        "componentes",
        relacionados=("componente", "corte"),
    ),
    "grado": concepto(
        "Grado de un vértice",
        r"""
$$\deg_G(v)=|\{e\in E:v\in e\}|.$$""",
        "Cantidad de aristas que inciden en el vértice.",
        "arbol",
        relacionados=("impar", "euleriano"),
    ),
    "arbol": concepto(
        "Árbol",
        r"""
Un árbol es un grafo no dirigido, conexo y acíclico.""",
        "Grafo conexo que no contiene ciclos.",
        "arbol",
        propiedad=r"**Propiedad.** Todo árbol finito $T$ satisface $$|E(T)|=|V(T)|-1.$$",
        demostracion=r"""**Demostración por inducción sobre $n=|V(T)|$.**

**Base:** para $n=1$, el único árbol tiene cero aristas.

**Paso inductivo:** todo árbol con $n\geq2$ tiene una hoja (vértice de grado 1).
Al retirar esa hoja y su arista, queda un árbol con $n-1$ vértices. Por hipótesis
inductiva tiene $n-2$ aristas. Al reincorporar la hoja y su arista obtenemos
$(n-2)+1=n-1$ aristas. $\square$""",
        relacionados=("conexo", "bosque", "arbol_generador"),
    ),
    "bosque": concepto(
        "Bosque",
        r"""
Un bosque es un grafo no dirigido acíclico.""",
        "Cada una de sus componentes conexas es un árbol.",
        "componentes",
        relacionados=("arbol", "componente", "agm"),
    ),
    "arbol_generador": concepto(
        "Árbol generador",
        r"""
Sea $G=(V,E)$ conexo. $T=(V,E_T)$ es árbol generador de $G$ si
$E_T\subseteq E$ y $T$ es un árbol.""",
        "Conecta todos los vértices originales sin formar ciclos.",
        "arbol",
        relacionados=("arbol", "peso_arbol", "agm"),
    ),
    "peso_arbol": concepto(
        "Peso de un árbol",
        r"""
Dada $w:E\to\mathbb R$, el peso total es
$$w(T)=\sum_{e\in E(T)}w(e).$$""",
        "La suma de los pesos de todas las aristas del árbol.",
        "arbol",
        relacionados=("arbol_generador", "agm", "peso_recorrido"),
    ),
    "agm": concepto(
        "Árbol generador mínimo (AGM)",
        r"""
Un árbol generador $T^*$ es mínimo si

$$
w(T^*)=\min\{w(T):T\text{ es árbol generador de }G\}
$$""",
        "El árbol que conecta todos los vértices con el menor peso total posible.",
        "arbol",
        propiedad=r"**En GraphLab:** el AGM obtenido con Kruskal tiene peso $w(T^*)=64$.",
        relacionados=("peso_arbol", "corte", "propiedad_corte"),
    ),
    "corte": concepto(
        "Corte",
        r"""
Para $\varnothing\neq S\subsetneq V$, el corte es

$$
\delta(S)=\{\{u,v\}\in E:u\in S,\,v\notin S\}
$$""",
        "Conjunto de aristas que unen un grupo de vértices con el resto del grafo.",
        "corte",
        relacionados=("propiedad_corte", "conexo"),
    ),
    "propiedad_corte": concepto(
        "Propiedad del corte",
        r"""
Sea $F$ un conjunto de aristas contenido en algún AGM. Si un corte respeta a $F$
(no contiene aristas de $F$) y $e$ es una arista de peso mínimo que cruza el corte,
entonces $F\cup\{e\}$ está contenido en algún AGM.""",
        "Elegir la arista de menor peso que une dos componentes distintas es una elección segura.",
        "corte",
        propiedad="Resultado utilizado para justificar la corrección de Kruskal.",
        demostracion=r"""**Argumento de intercambio.** Sea $T$ un AGM que contiene $F$.
Si $e\in T$, no hay nada que demostrar. Si $e\notin T$, añadir $e$ a $T$ crea
un ciclo. Ese ciclo cruza el corte al menos dos veces, por lo que existe otra
arista $f$ del ciclo que cruza el corte y no pertenece a $F$. Como $e$ es
mínima entre las aristas del corte, $w(e)\leq w(f)$.

Al sustituir $f$ por $e$ obtenemos otro árbol generador que contiene $F\cup\{e\}$
y cuyo peso no supera el de $T$. Como $T$ era mínimo, el nuevo árbol también es
mínimo. $\square$""",
        relacionados=("corte", "agm"),
        tipo="Teorema",
    ),
    "puente": concepto(
        "Puente",
        r"""
Una arista $e$ de un grafo no dirigido es un puente si eliminar $e$ aumenta el
número de componentes conexas.""",
        "Al quitar esa arista, se desconecta alguna parte que antes estaba conectada.",
        "arbol",
        relacionados=("conexo", "componente"),
    ),
    "completo": concepto(
        "Grafo completo",
        r"""
En un grafo simple completo,

$$
E=\{\{u,v\}:u,v\in V,\;u\neq v\}
$$""",
        "Cada par de vértices distintos está unido por una arista.",
        "completo",
        propiedad=r"Con $n$ vértices tiene $\binom{n}{2}$ aristas. Para $n=7$: $21$.",
        relacionados=("grafo", "metrico", "tsp"),
    ),
    "metrico": concepto(
        "Grafo ponderado métrico",
        r"""
En un grafo completo con pesos simétricos, positivos entre vértices distintos,
se cumple la desigualdad triangular:
$$w(u,z)\leq w(u,v)+w(v,z)\quad\forall u,v,z\in V.$$""",
        "Ir directamente no cuesta más que pasar por otro vértice.",
        "completo",
        relacionados=("completo", "atajo", "tsp"),
    ),
    "multigrafo": concepto(
        "Multigrafo",
        r"""
Estructura $G=(V,E)$ en la que pueden existir varias aristas distintas con
los mismos dos extremos.""",
        "Dos vértices pueden quedar conectados mediante varias copias de una arista.",
        "multigrafo",
        relacionados=("euleriano", "doble_arbol", "christofides"),
    ),
    "impar": concepto(
        "Vértice de grado impar",
        r"""
$v\in V$ tiene grado impar si $\deg_G(v)\equiv1\pmod 2$.""",
        "Tiene una cantidad impar de aristas incidentes.",
        "arbol",
        propiedad=r"**Lema del apretón de manos:** $\sum_{v\in V}\deg(v)=2|E|$. Por tanto, el número de vértices de grado impar es par.",
        relacionados=("grado", "matching_perfecto", "christofides"),
    ),
    "matching": concepto(
        "Matching (emparejamiento)",
        r"""
Un matching $M\subseteq E$ satisface $e\cap f=\varnothing$ para cualesquiera
$e,f\in M$ distintos.""",
        "Aristas seleccionadas que no comparten extremos.",
        "matching",
        relacionados=("matching_perfecto", "matching_minimo"),
    ),
    "matching_perfecto": concepto(
        "Matching perfecto",
        r"""
Un matching $M$ es perfecto si todo vértice del grafo considerado pertenece
a exactamente una arista de $M$.""",
        "Todos los vértices quedan emparejados, sin repetir ninguno.",
        "matching",
        relacionados=("matching", "matching_minimo"),
    ),
    "matching_minimo": concepto(
        "Matching perfecto de peso mínimo",
        r"""
Sobre un conjunto de vértices par $S$, un matching perfecto $M^*$ satisface

$$
w(M^*)=\min\{w(M):M\text{ es matching perfecto de }S\}
$$""",
        "De todos los emparejamientos completos, escogemos el de menor suma de pesos.",
        "matching",
        propiedad=r"En el ejemplo: $S=\{a,b,c,f\}$ y $M^*=\{ac,bf\}$ de peso $29$.",
        relacionados=("matching", "impar", "christofides"),
    ),
    "euleriano": concepto(
        "Circuito euleriano",
        r"""
Es un recorrido cerrado que usa cada arista del grafo exactamente una vez.""",
        "Se recorren todas las aristas una sola vez y se regresa al origen; se pueden repetir vértices.",
        "euleriano",
        propiedad=r"Un multigrafo no dirigido y conexo admite circuito euleriano si y solo si todos sus vértices tienen grado par.",
        relacionados=("multigrafo", "hamiltoniano", "doble_arbol"),
    ),
    "atajo": concepto(
        "Atajo en un recorrido",
        r"""
En un grafo métrico, reemplazar $v_0,v_1,\ldots,v_k$ por la arista directa
$\{v_0,v_k\}$ cumple
$$w(v_0,v_k)\leq\sum_{i=0}^{k-1}w(v_i,v_{i+1}).$$""",
        "Se evitan repeticiones conectando directamente dos vértices, sin aumentar el costo.",
        "atajo",
        relacionados=("metrico", "doble_arbol", "christofides"),
    ),
    "hamiltoniano": concepto(
        "Ciclo hamiltoniano",
        r"""
Un ciclo $C=(v_1,\ldots,v_n,v_1)$ es hamiltoniano si
$\{v_1,\ldots,v_n\}=V$ y esos $n$ vértices son distintos.""",
        "Visita todos los vértices exactamente una vez y regresa al origen.",
        "hamiltoniano",
        relacionados=("ciclo", "euleriano", "tsp"),
    ),
    "tsp": concepto(
        "Problema del viajante (TSP)",
        r"""
Sea $\mathcal H(G)$ el conjunto de ciclos hamiltonianos del grafo ponderado.
Se busca $C^*$ tal que
$$w(C^*)=\min_{C\in\mathcal H(G)}w(C).$$""",
        "Se quiere visitar cada vértice una vez, regresar al inicio y pagar el menor costo total.",
        "hamiltoniano",
        relacionados=("hamiltoniano", "optimo", "aproximacion"),
    ),
    "peso_recorrido": concepto(
        "Peso de un recorrido",
        r"""
Para $R=(v_0,\ldots,v_k)$,
$$w(R)=\sum_{i=0}^{k-1}w(v_i,v_{i+1}).$$""",
        "Sumar el peso de cada desplazamiento, contando las repeticiones.",
        "camino",
        relacionados=("peso_arbol", "tsp"),
    ),
    "optimo": concepto(
        "Solución óptima",
        r"""
Una solución factible $C^*$ es óptima si $w(C^*)\leq w(C)$ para todo ciclo
hamiltoniano factible $C$.""",
        "No existe otro ciclo válido de costo menor.",
        "hamiltoniano",
        relacionados=("tsp", "aproximacion"),
    ),
    "aproximacion": concepto(
        "Algoritmo de aproximación",
        r"""
Para un problema de minimización, tiene factor de aproximación $\alpha\geq1$
si entrega una solución $C_A$ tal que
$$w(C_A)\leq\alpha\,w(C^*)$$
para toda instancia de la clase considerada.""",
        "Entrega soluciones válidas con una garantía matemática respecto del costo óptimo.",
        relacionados=("doble_arbol", "christofides", "optimo"),
    ),
    "doble_arbol": concepto(
        "Garantía del doble árbol",
        r"""
Para el TSP métrico, el algoritmo de doble árbol devuelve un ciclo $C_D$ con
$$w(C_D)\leq2\,w(C^*).$$""",
        "Su costo nunca supera el doble del óptimo para un TSP métrico.",
        "arbol",
        propiedad="La cota de aproximación es 2.",
        demostracion=r"""Sea $T$ un AGM y $C^*$ un ciclo hamiltoniano óptimo.
Al quitar una arista a $C^*$ queda un árbol generador, así que
$w(T)\leq w(C^*)$. Al duplicar $T$ todas las aristas tienen grado par y
se obtiene un circuito euleriano de costo $2w(T)$.

Los atajos métricos no aumentan ese costo. Por tanto,
$$w(C_D)\leq2w(T)\leq2w(C^*).\quad\square$$""",
        relacionados=("agm", "euleriano", "atajo"),
        tipo="Teorema",
    ),
    "christofides": concepto(
        "Garantía de Christofides",
        r"""
Para el TSP métrico, Christofides devuelve un ciclo $C_H$ con
$$w(C_H)\leq\tfrac32\,w(C^*).$$""",
        "Garantiza un costo a lo sumo una vez y media el óptimo, no necesariamente el óptimo.",
        "matching",
        propiedad="La cota de aproximación es 3/2.",
        demostracion=r"""Sea $T$ un AGM y $S$ el conjunto (par) de vértices de grado impar
de $T$. Sea $M$ el matching perfecto mínimo de $S$.

Tenemos $w(T)\leq w(C^*)$. El orden de los vértices de $S$ sobre un ciclo
óptimo divide ese ciclo en dos matchings perfectos alternantes cuando
sustituimos sus tramos por aristas directas. Por desigualdad triangular, la
suma de ambos matchings no supera $w(C^*)$, luego el menor pesa a lo sumo
$\tfrac12 w(C^*)$. Dado que $M$ es mínimo, $w(M)\leq\tfrac12w(C^*)$.

$T\cup M$ es conexo y todos sus grados son pares; admite un circuito
euleriano de costo $w(T)+w(M)$. Los atajos no aumentan el costo:
$$w(C_H)\leq w(T)+w(M)\leq\tfrac32w(C^*).\quad\square$$""",
        relacionados=("agm", "matching_minimo", "euleriano", "atajo"),
        tipo="Teorema",
    ),
}

# Guardas para detectar cambios de claves sin perder entradas en la navegación.
claves = [clave for grupo in CATEGORIAS.values() for clave in grupo]
if len(claves) != len(set(claves)) or set(claves) != set(CONCEPTOS):
    raise ValueError("Las categorias y los conceptos de la biblioteca no coinciden.")

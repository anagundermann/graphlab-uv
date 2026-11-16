# GraphLab UV

**Laboratorio interactivo de algoritmos de optimización combinatoria**

Proyecto desarrollado por **Ana Gundermann**, estudiante de Ingeniería Civil Matemática de la Universidad de Valparaíso (2026).

GraphLab UV es una aplicación educativa desarrollada en **Python y Dash** para explorar algoritmos relacionados con el problema del viajante (*Traveling Salesperson Problem*, TSP) métrico.

Permite visualizar paso a paso cómo se construye un árbol generador mínimo mediante Kruskal y cómo los algoritmos de doble árbol y Christofides utilizan esta estructura para obtener soluciones aproximadas al TSP.

## Funcionalidades

- **Introducción:** contexto histórico, formulación matemática y complejidad del problema del viajante.
- **Kruskal:** construcción paso a paso de un árbol generador mínimo.
- **Doble árbol (2-TSP):** visualización de la construcción de un ciclo hamiltoniano aproximado.
- **Christofides:** exploración del algoritmo mediante árbol mínimo, matching y construcción del recorrido.
- **Comparación:** visualización de los recorridos y sus costos, con selección del vértice inicial.
- **Código Python:** consulta del código de los algoritmos y sincronización con los pasos de ejecución.
- **Biblioteca matemática:** definiciones y conceptos utilizados en los laboratorios.

Los algoritmos se presentan sobre una misma instancia de grafo completo ponderado de 7 vértices y 21 aristas, lo que permite comparar sus resultados.

## Arquitectura

- `models/`: datos, cálculos matemáticos y algoritmos independientes de Dash.
- `pages/`: vistas, controles interactivos, gráficos y callbacks.
- `components/`: componentes reutilizables y conceptos matemáticos.
- `assets/`: estilos CSS y recursos visuales.
- `app.py`: aplicación principal, navegación y gestión del estado.
- `tests/test_modelos.py`: comprobación de invariantes matemáticos.

## Tecnologías

Python · Dash · Dash Cytoscape · Plotly · NetworkX · HTML/CSS

## Ejecución local

Desde la carpeta principal del proyecto:

```bash
pip install -r requirements.txt
python app.py
```

Abrir en el navegador:

http://127.0.0.1:8081/

## Consideraciones matemáticas

Kruskal encuentra un **árbol generador mínimo (AGM)**, no un ciclo hamiltoniano.

Doble árbol y Christofides construyen soluciones aproximadas al TSP métrico, con garantías teóricas de costo de \(2\cdot OPT\) y \(1{,}5\cdot OPT\), respectivamente.

Las posiciones visuales de los vértices no determinan los pesos de las aristas.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Desarrollo y evolución

Esta es la versión original de GraphLab UV, desarrollada con Python y Dash.

Se contempla una adaptación posterior a JavaScript para permitir su ejecución directamente en el navegador, sin depender de un servidor Python.

## Autoría

**Ana Gundermann**  
Ingeniería Civil Matemática  
Universidad de Valparaíso · Chile  
2026
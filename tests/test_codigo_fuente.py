"""Pruebas de integridad del visor: no requieren Dash."""

import ast
from pathlib import Path
import unittest

from models.grafo_data import VERTICES
from models import kruskal, doble_arbol, christofides
from models.analizador_codigo import (
    NOMBRES,
    leer_codigo,
    estado,
    fragmentos_coloreados,
)


class TestCodigoFuente(unittest.TestCase):
    def test_fuente_completa_es_el_archivo_original(self):
        for algoritmo in NOMBRES:
            ruta = Path(__file__).resolve().parents[1] / "models" / f"{algoritmo}.py"
            with self.subTest(algoritmo=algoritmo):
                self.assertEqual(
                    leer_codigo(algoritmo), ruta.read_text(encoding="utf-8")
                )
                self.assertGreater(len(leer_codigo(algoritmo).splitlines()), 100)

    def test_resaltado_referencia_codigo_real_para_todos_los_pasos(self):
        modelos = {
            "kruskal": kruskal,
            "doble_arbol": doble_arbol,
            "christofides": christofides,
        }
        for algoritmo, modelo in modelos.items():
            for inicio in VERTICES:
                cantidad = (
                    len(kruskal.PASOS)
                    if algoritmo == "kruskal"
                    else len(modelo.obtener_datos(inicio)["pasos"])
                )
                for paso in range(cantidad):
                    with self.subTest(algoritmo=algoritmo, inicio=inicio, paso=paso):
                        dato = estado(algoritmo, paso, inicio)
                        self.assertEqual(dato["paso"], paso)
                        self.assertEqual(dato["inicio"], inicio)
                        self.assertTrue(
                            dato["titulo"]
                            and dato["explicacion"]
                            and dato["aplicacion"]
                        )
                        self.assertTrue(dato["marcas"])
                        self.assertTrue(
                            all(
                                1 <= a <= b <= len(dato["codigo"].splitlines())
                                for a, b in dato["marcas"]
                            )
                        )

    def test_tokens_recomponen_cada_linea_sin_modificar(self):
        for algoritmo in NOMBRES:
            fuente = leer_codigo(algoritmo)
            lista = fragmentos_coloreados(fuente)
            self.assertEqual(len(lista), len(fuente.splitlines()))
            for original, fragmentos in zip(fuente.splitlines(), lista):
                self.assertEqual(
                    "".join(texto for texto, _ in fragmentos), original or " "
                )

    def test_navegacion_y_controles_existentes_sin_borrado(self):
        base = Path(__file__).resolve().parents[1]
        app = (base / "app.py").read_text(encoding="utf-8")
        self.assertIn('("codigo", "Código Python")', app)
        self.assertIn("graphlab-ejecucion", app)
        for algoritmo in NOMBRES:
            page = (base / "pages" / f"{algoritmo}.py").read_text(encoding="utf-8")
            self.assertIn(f'"index": "{algoritmo}"', page)
            self.assertIn("paso_inicial", page)
            ast.parse(page)
        ast.parse(app)


if __name__ == "__main__":
    unittest.main()

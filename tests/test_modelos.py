"""Verificaciones matemáticas sin dependencias gráficas."""
import unittest
from models.grafo_data import VERTICES, ARISTAS, PESOS
from models import kruskal, doble_arbol, christofides, comparacion, tsp_optimo

class TestModelos(unittest.TestCase):
    def test_grafo_metrico(self):
        self.assertEqual(len(VERTICES), 7)
        self.assertEqual(len(ARISTAS), 21)
        self.assertTrue(tsp_optimo.METRICO)

    def test_agm(self):
        self.assertEqual(kruskal.PASOS[-1]["peso_total"], 64)
        self.assertEqual(doble_arbol.PESO_ARBOL, 64)
        self.assertEqual(christofides.PESO_ARBOL, 64)

    def test_matching(self):
        self.assertEqual(christofides.PESO_MATCHING, 29)
        self.assertEqual(christofides.PESO_MULTIGRAFO, 93)

    def test_ciclos(self):
        for inicio in VERTICES:
            datos = comparacion.RESULTADOS[inicio]
            for clave in ("doble", "christofides"):
                circuito = datos[clave]
                self.assertEqual(circuito[0], inicio)
                self.assertEqual(circuito[-1], inicio)
                self.assertEqual(len(circuito), len(VERTICES) + 1)
                self.assertEqual(set(circuito[:-1]), set(VERTICES))

    def test_cotas(self):
        optimo = tsp_optimo.COSTO_OPTIMO
        for d in comparacion.RESULTADOS.values():
            self.assertLessEqual(d["costo_doble"], 2 * optimo)
            self.assertLessEqual(d["costo_christofides"], 1.5 * optimo)

if __name__ == "__main__":
    unittest.main()

import unittest

from secciones.resultados_imagen import generar
from secciones.proximo_partido_imagen import generar_proximo
from secciones.clasificacion_imagen import generar_clasificacion


class TestSectionImageModules(unittest.TestCase):
    def test_generators_are_importable(self):
        self.assertTrue(callable(generar))
        self.assertTrue(callable(generar_proximo))
        self.assertTrue(callable(generar_clasificacion))


if __name__ == "__main__":
    unittest.main()

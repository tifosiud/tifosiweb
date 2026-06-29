import unittest

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.secciones.resultados_imagen import generar
from src.secciones.proximo_partido_imagen import generar_proximo
from src.secciones.clasificacion_imagen import generar_clasificacion


class TestSectionImageModules(unittest.TestCase):
    def test_generators_are_importable(self):
        self.assertTrue(callable(generar))
        self.assertTrue(callable(generar_proximo))
        self.assertTrue(callable(generar_clasificacion))


if __name__ == "__main__":
    unittest.main()

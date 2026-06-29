import json
import tempfile
import unittest
from pathlib import Path

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.secciones.resultados import parse_resultado
from src.secciones.clasificacion import parse_clasificacion_text
from src.secciones.resultados_jornada import guardar_resultados_jornada, cargar_resultados_jornada
from src.secciones.ultimo_resultado import find_latest_result_asset


class TestSectionModules(unittest.TestCase):
    def test_parse_resultado(self):
        texto = "J12 Tifosi 2-1 Betis Goleadores: Juan(1)"
        data = parse_resultado(texto)
        self.assertEqual(data["jornada"], 12)
        self.assertEqual(data["goles_local"], 2)
        self.assertEqual(data["goles_visitante"], 1)
        self.assertEqual(data["goleadores"], [("Juan", 1)])

    def test_parse_clasificacion_text(self):
        texto = "1 Tifosi 10 8 1 1 20 5 25\n2 Betis 10 7 2 1 18 9 23"
        data = parse_clasificacion_text(texto)
        self.assertEqual(data[0]["equipo"], "Tifosi")
        self.assertEqual(data[0]["pts"], 25)

    def test_resultados_jornada_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "resultados.json"
            payload = [{"jornada": 1, "local": "Tifosi"}]
            guardar_resultados_jornada(payload, path)
            loaded = cargar_resultados_jornada(path)
            self.assertEqual(loaded, payload)

    def test_find_latest_result_asset(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            img_dir = base / "imagenes" / "j3" / "resultado"
            img_dir.mkdir(parents=True)
            asset = img_dir / "j3_resultado.png"
            asset.write_bytes(b"fake")

            latest = find_latest_result_asset(base)
            self.assertEqual(latest, "imagenes/j3/resultado/j3_resultado.png")


if __name__ == "__main__":
    unittest.main()

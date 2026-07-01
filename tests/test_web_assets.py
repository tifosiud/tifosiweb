import json
import tempfile
import unittest
from pathlib import Path

from src.processing.web_assets import build_latest_assets, write_latest_assets


class WebAssetsTests(unittest.TestCase):
    def test_build_latest_assets_uses_latest_existing_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "imagenes" / "j22" / "clasificacion").mkdir(parents=True, exist_ok=True)
            (base / "imagenes" / "j20" / "resultado").mkdir(parents=True, exist_ok=True)
            (base / "imagenes" / "j22" / "clasificacion" / "j22_clasificacion.png").write_bytes(b"img")
            (base / "imagenes" / "j20" / "resultado" / "j20_resultado.png").write_bytes(b"img")

            assets = build_latest_assets(base)

            self.assertEqual(assets["clasificacion"], "imagenes/j22/clasificacion/j22_clasificacion.png")
            self.assertEqual(assets["resultado"], "imagenes/j20/resultado/j20_resultado.png")

    def test_write_latest_assets_writes_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "imagenes" / "j1" / "clasificacion").mkdir(parents=True, exist_ok=True)
            (base / "imagenes" / "j1" / "clasificacion" / "j1_clasificacion.png").write_bytes(b"img")

            output = base / "last_assets.json"
            write_latest_assets(output_path=output, base_dir=base)

            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("clasificacion", data)
            self.assertEqual(data["clasificacion"], "imagenes/j1/clasificacion/j1_clasificacion.png")


if __name__ == "__main__":
    unittest.main()

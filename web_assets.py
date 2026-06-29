import json
from pathlib import Path
from typing import Dict, Optional


def build_latest_assets(base_dir: Optional[Path | str] = None) -> Dict[str, str]:
    base = Path(base_dir or Path(__file__).resolve().parent)
    images_dir = base / "imagenes"

    assets: Dict[str, str] = {}
    for section in ("clasificacion", "resultado"):
        assets[section] = find_latest_asset(images_dir, section)

    return assets


def find_latest_asset(images_dir: Path, section: str) -> str:
    for jornada in range(100, 0, -1):
        section_dir = images_dir / f"j{jornada}" / section
        if not section_dir.exists():
            continue

        for file_path in sorted(section_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                return str(file_path.relative_to(images_dir.parent)).replace("\\", "/")

    return ""


def write_latest_assets(output_path: Optional[Path | str] = None, base_dir: Optional[Path | str] = None) -> Dict[str, str]:
    base = Path(base_dir or Path(__file__).resolve().parent)
    output = Path(output_path or base / "last_assets.json")
    assets = build_latest_assets(base)
    output.write_text(json.dumps(assets, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return assets

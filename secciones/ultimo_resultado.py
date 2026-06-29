from pathlib import Path
from typing import Optional, Union


def find_latest_result_asset(base_dir: Optional[Union[str, Path]] = None) -> str:
    base = Path(base_dir or Path(__file__).resolve().parent.parent)
    images_dir = base / "imagenes"

    for jornada in range(100, 0, -1):
        section_dir = images_dir / f"j{jornada}" / "resultado"
        if not section_dir.exists():
            continue

        for file_path in sorted(section_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                return str(file_path.relative_to(base)).replace("\\", "/")

    return ""

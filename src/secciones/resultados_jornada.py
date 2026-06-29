import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def cargar_resultados_jornada(path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    file_path = Path(path or "data/resultados_liga.json")
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def guardar_resultados_jornada(data: List[Dict[str, Any]], path: Optional[Union[str, Path]] = None) -> None:
    file_path = Path(path or "data/resultados_liga.json")
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

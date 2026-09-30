# core/models/panel.py
import dataclasses
from typing import Any

@dataclasses.dataclass
class Panel:
    id: str
    face: Any # FreeCAD.Face
    is_base: bool = False

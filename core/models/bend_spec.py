# core/models/bend_spec.py
import dataclasses
from typing import Optional, Any
import FreeCAD

@dataclasses.dataclass
class BendSpec:
    id: str
    angle: float
    radius: float
    k_factor: float
    line_p1: FreeCAD.Vector
    line_p2: FreeCAD.Vector
    sheetmetal_feature: Optional[Any] = None
    parent_panel_id: Optional[str] = None
    child_panel_id: Optional[str] = None

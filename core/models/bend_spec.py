# core/models/bend_spec.py
import dataclasses
from typing import Optional, Any, Dict
import FreeCAD

@dataclasses.dataclass
class BendSpec:
    id: str
    angle: float
    radius: float
    k_factor: float
    line_p1: FreeCAD.Vector
    line_p2: FreeCAD.Vector
    center: FreeCAD.Vector
    axis: FreeCAD.Vector
    length: float
    direction: str
    bend_sign: int
    invert: bool
    sheetmetal_feature: Optional[Any] = None
    parent_panel_id: Optional[str] = None
    child_panel_id: Optional[str] = None
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)
    
    @property
    def rotation_deg(self) -> float:
        """Returns the kinematic rotation needed to unbend/bend this spec."""
        return (180.0 - self.angle) * self.bend_sign

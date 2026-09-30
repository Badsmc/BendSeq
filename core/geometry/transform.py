import FreeCAD
import copy
from typing import Any
from ..models.bend_spec import BendSpec

def clone_spec(spec: BendSpec) -> BendSpec:
    """Clones a BendSpec."""
    return copy.deepcopy(spec)

def compute_force_ids(shape: Any) -> None:
    """
    Computes or extracts force IDs from a shape.
    Used for physical matching and tracking topologies.
    """
    pass

def apply_transform(shape: Any, transform: FreeCAD.Placement) -> Any:
    """
    Applies a placement to a shape, returning a new shape.
    Single source of truth for transforming BREP geometry.
    """
    new_shape = shape.copy()
    new_shape.Placement = transform.multiply(new_shape.Placement)
    return new_shape

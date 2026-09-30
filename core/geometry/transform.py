import FreeCAD
import copy
from typing import Any, List, Set
from ..models.bend_spec import BendSpec

def clone_spec(spec: BendSpec) -> BendSpec:
    """Clones a BendSpec without using deepcopy on FreeCAD objects."""
    import FreeCAD
    return BendSpec(
        id=spec.id,
        angle=spec.angle,
        radius=spec.radius,
        k_factor=spec.k_factor,
        line_p1=FreeCAD.Vector(spec.line_p1),
        line_p2=FreeCAD.Vector(spec.line_p2),
        center=FreeCAD.Vector(spec.center),
        axis=FreeCAD.Vector(spec.axis),
        length=spec.length,
        direction=spec.direction,
        bend_sign=spec.bend_sign,
        invert=spec.invert,
        sheetmetal_feature=spec.sheetmetal_feature, # Keep reference
        parent_panel_id=spec.parent_panel_id,
        child_panel_id=spec.child_panel_id,
        metadata=dict(spec.metadata) if spec.metadata else {}
    )

def compute_force_ids(cur_bend: BendSpec, future_specs: List[BendSpec]) -> Set[str]:
    """
    Computes which child feature bend IDs need to be physically matched (forced)
    after unfolding/folding this bend, because they share the same moving face.
    """
    cur_meta = cur_bend.metadata or {}
    cur_feature = str(cur_meta.get("feature") or "")
    cur_side = str(cur_meta.get("body_direction") or "")
    force = set()
    if not cur_feature:
        return force
    for spec in future_specs:
        m = spec.metadata or {}
        if str(m.get("parent_feature") or "") != cur_feature:
            continue
        f_side = str(m.get("body_direction") or "")
        if cur_side and f_side == cur_side:
            force.add(spec.id)
    return force

def apply_transform(shape: Any, transform: FreeCAD.Placement) -> Any:
    """
    Applies a placement to a shape, returning a new shape.
    Single source of truth for transforming BREP geometry.
    """
    new_shape = shape.copy()
    new_shape.Placement = transform.multiply(new_shape.Placement)
    return new_shape

def transform_bend_spec_inplace(spec: BendSpec, placement: FreeCAD.Placement) -> None:
    """
    Applies a FreeCAD Placement to the geometric vectors of a BendSpec.
    """
    spec.center = placement.multVec(spec.center)
    spec.line_p1 = placement.multVec(spec.line_p1)
    spec.line_p2 = placement.multVec(spec.line_p2)
    rot = placement.Rotation
    spec.axis = rot.multVec(spec.axis)

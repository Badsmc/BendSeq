# adapters/freecad_adapter.py
from typing import List, Tuple, Any, Optional
import FreeCAD
from ..core.models.bend_spec import BendSpec

def extract_body_and_base_face(doc_selection) -> Tuple[Optional[Any], Optional[str]]:
    """
    Extracts the parent body/object and the selected face name.
    """
    if not doc_selection:
        return None, None
        
    sel = doc_selection[0]
    obj = sel.Object
    
    if not sel.SubElementNames:
        return obj, None
        
    face_name = sel.SubElementNames[0]
    if not face_name.startswith("Face"):
        return obj, None
        
    return obj, face_name

def _extract_edge_points(feature) -> Tuple[Optional[FreeCAD.Vector], Optional[FreeCAD.Vector]]:
    try:
        bo = getattr(feature, "baseObject", None)
        if not bo: return None, None
        parent, subs = bo[0], list(bo[1])
        if not parent or not subs: return None, None
        edge = parent.Shape.getElement(subs[0])
        if not edge or getattr(edge, "ShapeType", "") != "Edge": return None, None
        import Part
        v = edge.Vertexes
        if len(v) >= 2:
            return v[0].Point, v[-1].Point
    except Exception:
        pass
    return None, None

def extract_bends(body: Any) -> List[BendSpec]:
    """
    Finds SheetMetal bend features related to the body and fully populates BendSpec.
    """
    bends = []
    import FreeCAD
    doc = FreeCAD.ActiveDocument
    if not doc:
        return bends
        
    for feature in doc.Objects:
        is_sm = False
        if hasattr(feature, "Proxy") and feature.Proxy is not None:
            cname = feature.Proxy.__class__.__name__
            if "Bend" in cname or "Fold" in cname or "Wall" in cname:
                is_sm = True
                
        if not is_sm and hasattr(feature, "angle") and hasattr(feature, "radius"):
            if "SheetMetal" in str(getattr(feature, "Proxy", "")):
                is_sm = True
                
        if is_sm:
            try:
                angle = getattr(feature, 'angle', 90.0)
                if hasattr(angle, "Value"): angle = angle.Value
                else: angle = float(angle)
                
                radius = getattr(feature, 'radius', 1.0)
                if hasattr(radius, "Value"): radius = radius.Value
                else: radius = float(radius)
                
                k_factor = getattr(feature, 'kfactor', 0.5)
                if hasattr(k_factor, "Value"): k_factor = k_factor.Value
                else: k_factor = float(k_factor)
                
                invert = bool(getattr(feature, "invert", False))
                bend_sign = -1 if invert else 1
                direction = "down" if invert else "up"
                
                p1, p2 = _extract_edge_points(feature)
                if not p1 or not p2:
                    p1, p2 = FreeCAD.Vector(), FreeCAD.Vector()
                    
                center = (p1 + p2) * 0.5
                axis = p2 - p1
                length = axis.Length
                if length > 1e-9:
                    axis.normalize()
                
                spec = BendSpec(
                    id=feature.Name,
                    angle=angle,
                    radius=radius,
                    k_factor=k_factor,
                    line_p1=p1,
                    line_p2=p2,
                    center=center,
                    axis=axis,
                    length=length,
                    direction=direction,
                    bend_sign=bend_sign,
                    invert=invert,
                    sheetmetal_feature=feature,
                    metadata={"source": "feature", "invert": invert}
                )
                bends.append(spec)
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"BendSeq: Failed to extract bend {feature.Name}: {e}\n")
                
    return bends

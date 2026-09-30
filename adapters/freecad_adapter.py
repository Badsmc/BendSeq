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

def extract_bends(body: Any) -> List[BendSpec]:
    """
    Finds SheetMetal bend features related to the body.
    """
    bends = []
    import FreeCAD
    doc = FreeCAD.ActiveDocument
    if not doc:
        return bends
        
    # We will search all objects in the document that have SheetMetal bend-like properties
    # and are geometrically part of this part (or just grab all SM features for now).
    for feature in doc.Objects:
        # Check if it's a SheetMetal feature
        is_sm = False
        if hasattr(feature, "Proxy") and feature.Proxy is not None:
            cname = feature.Proxy.__class__.__name__
            if "Bend" in cname or "Fold" in cname or "Wall" in cname:
                is_sm = True
                
        # Also check standard properties
        if not is_sm and hasattr(feature, "angle") and hasattr(feature, "radius"):
            # Could be a standard FreeCAD feature acting as a bend
            if "SheetMetal" in str(getattr(feature, "Proxy", "")):
                is_sm = True
                
        if is_sm:
            try:
                angle = getattr(feature, 'angle', 90.0)
                # Some features use an object or expression for angle, so we float it if possible
                if hasattr(angle, "Value"): angle = angle.Value
                else: angle = float(angle)
                
                radius = getattr(feature, 'radius', 1.0)
                if hasattr(radius, "Value"): radius = radius.Value
                else: radius = float(radius)
                
                k_factor = getattr(feature, 'kfactor', 0.5)
                if hasattr(k_factor, "Value"): k_factor = k_factor.Value
                else: k_factor = float(k_factor)
                
                p1, p2 = FreeCAD.Vector(), FreeCAD.Vector()
                
                spec = BendSpec(
                    id=feature.Name,
                    angle=angle,
                    radius=radius,
                    k_factor=k_factor,
                    line_p1=p1,
                    line_p2=p2,
                    sheetmetal_feature=feature
                )
                bends.append(spec)
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"BendSeq: Failed to extract bend {feature.Name}: {e}\n")
                
    return bends

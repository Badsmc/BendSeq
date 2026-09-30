# adapters/overlay.py
import FreeCAD
from typing import List, Any

def create_number_overlay_on_unfold(unfold_shape: Any, bend_order: List[str]):
    """
    Draws sequence numbers on the unfolded shape's bend lines.
    """
    doc = FreeCAD.ActiveDocument
    if not doc:
        return
        
    group_name = "BendSeq_Unfold_Numbers"
    group = doc.getObject(group_name)
    if group:
        for child in group.Group:
            doc.removeObject(child.Name)
    else:
        group = doc.addObject("App::DocumentObjectGroup", group_name)
        group.Label = "Bend Sequence (Numbers)"

    try:
        import Draft
    except ImportError:
        FreeCAD.Console.PrintWarning("BendSeq: Draft module not available for text overlay.\n")
        return
        
    # We will lay out numbers roughly at Z=1 above the bounding box center, 
    # spaced apart since we don't have exact bend edge linking yet.
    
    if hasattr(unfold_shape, "BoundBox"):
        center_x = unfold_shape.BoundBox.Center.x
        center_y = unfold_shape.BoundBox.Center.y
    else:
        center_x = 0
        center_y = 0

    for i, bend_id in enumerate(bend_order):
        step_num = i + 1
        name = f"Sequence_{step_num}"
        
        try:
            # Using Draft shape string
            font_path = "" # Draft will try to find a default font
            
            text_obj = Draft.makeShapeString(String=str(step_num), FontFile=font_path, Size=10.0)
            if text_obj:
                text_obj.Placement.Base = FreeCAD.Vector(center_x + (i * 15), center_y, 1.0)
                if hasattr(text_obj, "ViewObject") and text_obj.ViewObject:
                    text_obj.ViewObject.ShapeColor = (0.0, 0.8, 0.0)
                group.addObject(text_obj)
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"BendSeq: Failed to draw number {step_num}: {e}\n")

def update_number_overlay_in_3d(current_step: int, bend_order: List[str]):
    """
    Updates 3D simulation numbers per step.
    """
    pass

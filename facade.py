# BendSeq/facade.py
# ONLY entry point for UI

from typing import Dict, Any, List
import FreeCAD
from .config import SEQUENCE_CONFIG
from .adapters import freecad_adapter, sheetmetal_api, overlay
from .algorithms import staged_solver

def find_sequence(doc_selection_or_body, *, strategy="staged", time_budget=None, tooling=None) -> Dict[str, Any]:
    """
    Finds a valid bend sequence.
    Returns: dict with keys: success (bool), order (list of bend ids), partial (bool), stats (dict), diagnostics (list).
    """
    body, face_name = freecad_adapter.extract_body_and_base_face(doc_selection_or_body)
    if not body:
        return {"success": False, "error": "No valid SheetMetal body or face selected."}
        
    bends = freecad_adapter.extract_bends(body)
    if not bends:
        return {"success": False, "error": "No bends found in the selected body."}
        
    config = dict(SEQUENCE_CONFIG)
    if time_budget:
        config["time_budget_stage3"] = time_budget
    if tooling:
        config["tooling"] = tooling
        
    result = staged_solver.solve(body, bends, config)
    
    # Generate unfold with numbers if successful
    if result.get("success"):
        get_unfold_with_numbers(body, face_name, result["order"])
        
    return result

def validate_sequence(body, order, **kwargs) -> Dict[str, Any]:
    """
    Validates a given sequence physically by attempting to unbend in reverse.
    Returns: dict with success (bool), error (str), stats (dict).
    """
    from .algorithms.physical_dfs import PhysicalOracle
    from .core.engines.fold_engine import FoldEngine
    from .core.engines.collision_engine import CollisionEngine
    from .core.models.sequence_state import SequenceState
    
    config = dict(SEQUENCE_CONFIG)
    oracle = PhysicalOracle(FoldEngine(config), CollisionEngine(config.get("collision_margin", 0.1)))
    
    bends = freecad_adapter.extract_bends(body)
    bends_by_id = {b.id: b for b in bends}
    
    try:
        current_shape = body.Shape.copy()
    except Exception:
        return {"success": False, "error": "Invalid body shape"}
        
    for bend_id in reversed(order):
        if bend_id not in bends_by_id:
            return {"success": False, "error": f"Unknown bend ID: {bend_id}"}
        bend = bends_by_id[bend_id]
        state = SequenceState(current_shape=current_shape, bends_done=frozenset(), bends_remaining=set(), order=[])
        res = oracle.try_unbend(state, bend)
        if not res:
            return {"success": False, "error": f"Validation failed at bend {bend_id}"}
        current_shape = res.shape
        
    return {"success": True, "error": "", "stats": {}}

def prepare_simulation(body, order):
    """
    Prepares a simulation state for the viewer.
    Returns: A simulation state object that the viewer can step through.
    """
    from .simulation import viewer
    return viewer.SimulationState(body, order)

def get_unfold_with_numbers(body, face_name, order):
    """
    Generates an unfolded shape/sketch and overlay label data.
    """
    res = sheetmetal_api.unfold(body, face_name)
    if res.ok:
        import FreeCAD
        doc = FreeCAD.ActiveDocument
        
        if hasattr(body, "ViewObject") and body.ViewObject:
            body.ViewObject.Visibility = False
            
        unfold_obj = doc.getObject("BendSeq_Unfold")
        if not unfold_obj:
            unfold_obj = doc.addObject("Part::Feature", "BendSeq_Unfold")
            
        unfold_obj.Shape = res.unfolded_shape
        if hasattr(unfold_obj, "ViewObject") and unfold_obj.ViewObject:
            unfold_obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
            unfold_obj.ViewObject.Visibility = True
            
        overlay.create_number_overlay_on_unfold(res.unfolded_shape, order)
        
        if hasattr(FreeCAD, "GuiUp"):
            import FreeCADGui
            FreeCADGui.SendMsgToActiveView("ViewFit")
            
        doc.recompute()
    return res

def set_manual_sequence(*args, **kwargs):
    """
    STUB: Manual sequence editing (NotImplemented).
    """
    raise NotImplementedError("Manual sequence editing is not supported in v1.")

# adapters/sheetmetal_api.py
from typing import Any, Optional, List
import traceback
from ..core.models.results import UnfoldResult, FoldResult

try:
    import FreeCAD as App
    import Part
    _FC_OK = True
except ImportError:
    App = None
    Part = None
    _FC_OK = False

_SM_AVAILABLE = False
_unfolder_v2 = None
_unfolder_v1 = None
_smFold = None

if _FC_OK:
    try:
        from SheetMetalNewUnfolder import getUnfold as _getUnfold_v2
        from SheetMetalNewUnfolder import BendAllowanceCalculator
        _unfolder_v2 = {"getUnfold": _getUnfold_v2, "BAC": BendAllowanceCalculator}
        _SM_AVAILABLE = True
    except ImportError:
        pass

    try:
        from SheetMetalUnfolder import getUnfold as _getUnfold_v1
        _unfolder_v1 = {"getUnfold": _getUnfold_v1}
        _SM_AVAILABLE = True
    except ImportError:
        pass

    try:
        from SheetMetalFoldCmd import smFold as _smFoldCmd
        _smFold = _smFoldCmd
        _SM_AVAILABLE = True
    except ImportError:
        pass

def is_sheetmetal_available() -> bool:
    return _SM_AVAILABLE and _FC_OK

def unfold(base_object: Any, face_name: str, *, k_factor: float = 0.5) -> UnfoldResult:
    if not is_sheetmetal_available():
        return UnfoldResult(ok=False, error="SheetMetal workbench is not available.")
    
    try:
        if _unfolder_v2:
            bac = _unfolder_v2["BAC"].from_single_value(k_factor, "ansi")
            sel_face, unfolded, bend_lines, root_normal, bend_info = _unfolder_v2["getUnfold"](bac, base_object, face_name)
            return UnfoldResult(
                ok=True,
                unfolded_shape=unfolded,
                bend_lines=bend_lines,
                root_normal=root_normal,
                bend_info=bend_info,
                engine="v2"
            )
        elif _unfolder_v1:
            res = _unfolder_v1["getUnfold"](k_factor, base_object, face_name, "ansi")
            # Unfold v1 returns shape as res[0]
            return UnfoldResult(
                ok=True,
                unfolded_shape=res[0] if res else None,
                engine="v1"
            )
        else:
            return UnfoldResult(ok=False, error="No unfolder module found in SheetMetal.")
    except Exception as e:
        return UnfoldResult(ok=False, error=f"SheetMetal Unfold failed: {e}\n{traceback.format_exc()}")

def fold(main_object: Any, *, bend_radius: float, bend_angle: float, k_factor: float = 0.5, bend_line_sketch: Any = None, sel_face_names: List[str] = None, **kwargs) -> FoldResult:
    if not is_sheetmetal_available() or _smFold is None:
        return FoldResult(ok=False, error="SheetMetal Fold is not available.")
        
    try:
        invertbend = kwargs.get("invertbend", False)
        flipped = kwargs.get("flipped", False)
        position = kwargs.get("position", "middle")
        
        unfold_flag = kwargs.get("unfold", False)
        
        result_shape = _smFold(
            bendR=bend_radius,
            bendA=bend_angle,
            kfactor=k_factor,
            invertbend=invertbend,
            flipped=flipped,
            unfold=unfold_flag,
            position=position,
            bendlinesketch=bend_line_sketch,
            selFaceNames=sel_face_names or [],
            MainObject=main_object
        )
        
        if result_shape is None or result_shape.isNull():
            return FoldResult(ok=False, error="smFold returned a null shape.")
            
        return FoldResult(
            ok=True,
            shape=result_shape,
            engine="smFold"
        )
    except Exception as e:
        return FoldResult(ok=False, error=f"SheetMetal Fold failed: {e}\n{traceback.format_exc()}")

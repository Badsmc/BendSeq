# core/engines/fold_engine.py
from typing import Any
from ...adapters import sheetmetal_api
from ..models.bend_spec import BendSpec
from ..models.results import FoldResult

class FoldEngine:
    """
    Wraps the sheetmetal_api fold operation into a domain-specific physical oracle layer.
    """
    def __init__(self, config: dict):
        self.config = config

    def can_apply(self, shape: Any, bend: BendSpec) -> bool:
        """
        Quick check if folding is structurally possible before attempting full compute.
        (E.g., topological prerequisites).
        """
        # In a full implementation, you'd check topological panel graph.
        return True

    def apply(self, shape: Any, bend: BendSpec, is_unfold: bool = False) -> FoldResult:
        """
        Executes the fold using the SheetMetal API smFold, with OCC fallback.
        """
        import FreeCAD
        
        # We need the sketch or bend lines for smFold, but smFold expects actual FreeCAD sketches.
        # Since we are operating on intermediate shapes during sequence search, we use simulate_bend_occ.
        # This is because SheetMetal smFold strongly relies on the document tree, while we are operating headlessly.
        
        # smFold Attempt (if config allows and if we have Document objects)
        use_smfold = self.config.get("use_smfold", False)
        if use_smfold:
            sm_result = sheetmetal_api.fold(
                main_object=shape,
                bend_radius=bend.radius,
                bend_angle=bend.angle,
                k_factor=bend.k_factor,
                unfold=is_unfold,
                # We lack the sketch/face names dynamically without tree tracking
            )
            if sm_result.ok:
                return sm_result
        
        # Fallback to OCC Geometric Fold
        from ..geometry.bend_simulator import simulate_bend_occ
        from ..geometry.transform import transform_bend_spec_inplace
        
        try:
            # simulate_bend_occ requires angle_factor. For unbending, it is usually -1.0
            angle_factor = -1.0 if is_unfold else 1.0
            
            # simulate_bend_occ returns (new_shape, transform_info)
            new_shape, transform_info = simulate_bend_occ(
                part_shape=shape,
                bend_spec=bend,
                kinematics=None,
                angle_factor=angle_factor,
                logger=None
            )
            
            if new_shape and not new_shape.isNull():
                return FoldResult(ok=True, shape=new_shape, engine="occ", transform_info=transform_info)
            else:
                return FoldResult(ok=False, error="simulate_bend_occ returned null shape.")
                
        except Exception as e:
            return FoldResult(ok=False, error=f"simulate_bend_occ failed: {e}")

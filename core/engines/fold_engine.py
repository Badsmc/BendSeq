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
        Executes the fold using the SheetMetal API.
        """
        return sheetmetal_api.fold(
            main_object=shape,
            bend_radius=bend.radius,
            bend_angle=bend.angle,
            k_factor=bend.k_factor,
            unfold=is_unfold,
            # Additional required parameters like bend line would be passed here
        )

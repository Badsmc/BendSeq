# core/engines/collision_engine.py
from typing import Any

class CollisionEngine:
    """
    Handles all collision checks for a sequence state.
    """
    def __init__(self, margin: float = 0.1):
        self.margin = margin

    def check_sheet_vs_sheet(self, shape: Any) -> bool:
        """Self-intersection check."""
        try:
            if hasattr(shape, "isValid") and not shape.isValid():
                return True
            # Advanced BRepCheck could go here
        except Exception:
            pass
        return False

    def _check_dist(self, shape1: Any, shape2: Any) -> bool:
        if not shape1 or not shape2: return False
        if isinstance(shape2, str): return False # if passed a name instead of BREP
        try:
            dist, pts, info = shape1.distToShape(shape2)
            if dist < self.margin:
                return True
        except Exception:
            pass
        return False

    def check_sheet_vs_punch(self, shape: Any, punch_shape: Any) -> bool:
        return self._check_dist(shape, punch_shape)

    def check_sheet_vs_die(self, shape: Any, die_shape: Any) -> bool:
        return self._check_dist(shape, die_shape)

    def check_sheet_vs_press(self, shape: Any, press_shape: Any) -> bool:
        return self._check_dist(shape, press_shape)

    def check_sheet_vs_backgauge(self, shape: Any, backgauge_shape: Any) -> bool:
        return self._check_dist(shape, backgauge_shape)

    def check_all(self, shape: Any, tooling: dict) -> list:
        """
        Runs all collision checks. Returns a list of collision error strings.
        Empty list means no collisions.
        """
        errors = []
        if self.check_sheet_vs_sheet(shape):
            errors.append("sheet_vs_sheet")
        if tooling:
            if self.check_sheet_vs_punch(shape, tooling.get('punch')):
                errors.append("sheet_vs_punch")
            if self.check_sheet_vs_die(shape, tooling.get('die')):
                errors.append("sheet_vs_die")
            if self.check_sheet_vs_press(shape, tooling.get('press')):
                errors.append("sheet_vs_press")
            if self.check_sheet_vs_backgauge(shape, tooling.get('backgauge')):
                errors.append("sheet_vs_backgauge")
        return errors

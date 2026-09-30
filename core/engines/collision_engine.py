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
        # Using standard FreeCAD logic: if shape.isValid() and not shape.check() etc.
        # Placeholder
        return False

    def check_sheet_vs_punch(self, shape: Any, punch_shape: Any) -> bool:
        return False

    def check_sheet_vs_die(self, shape: Any, die_shape: Any) -> bool:
        return False

    def check_sheet_vs_press(self, shape: Any, press_shape: Any) -> bool:
        return False

    def check_sheet_vs_backgauge(self, shape: Any, backgauge_shape: Any) -> bool:
        return False

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

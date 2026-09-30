# algorithms/scoring.py
from typing import Dict, Any
from ..core.models.sequence_state import SequenceState
from ..core.models.bend_spec import BendSpec

def calculate_step_cost(state: SequenceState, next_bend: BendSpec, config: Dict[str, Any]) -> float:
    """
    Calculates workshop penalty score for making this bend next.
    Considers tool changes, part rotation, flipping, etc.
    """
    # Base cost
    cost = config.get("penalty_base", 1.0)
    
    # Placeholder for actual kinematics diff scoring
    return cost

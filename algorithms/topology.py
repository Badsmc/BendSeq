# algorithms/topology.py
from typing import List, Set
from ..core.models.bend_spec import BendSpec
from ..core.models.sequence_state import SequenceState

def filter_candidates_backward(state: SequenceState, all_bends: List[BendSpec]) -> List[BendSpec]:
    """
    Returns candidate bends that can be unbent (undone) from the current state.
    Prefer outside-in (leaf-first).
    """
    # Placeholder: currently returns all remaining bends.
    # A full topological implementation builds a panel graph and limits choices to leaves.
    return [b for b in all_bends if b.id in state.bends_remaining]

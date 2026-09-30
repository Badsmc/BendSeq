# algorithms/greedy_backward.py
from typing import List, Optional
from ..core.models.sequence_state import SequenceState
from ..core.models.bend_spec import BendSpec
from .topology import filter_candidates_backward
from .scoring import calculate_step_cost

def search(initial_state: SequenceState, all_bends: List[BendSpec], config: dict) -> Optional[List[str]]:
    """
    Fast greedy search starting from fully bent model, undoing bends until flat.
    Uses only topology and scoring, no physical engine check.
    """
    state = initial_state
    bends_by_id = {b.id: b for b in all_bends}
    
    while state.bends_remaining:
        candidates = filter_candidates_backward(state, [bends_by_id[bid] for bid in state.bends_remaining])
        if not candidates:
            return None # Dead end
            
        # Sort candidates by lowest penalty cost
        candidates.sort(key=lambda b: calculate_step_cost(state, b, config))
        
        # Pick best
        best_bend = candidates[0]
        
        next_bends_remaining = set(state.bends_remaining)
        next_bends_remaining.remove(best_bend.id)
        next_bends_done = set(state.bends_done)
        next_bends_done.add(best_bend.id)
        
        next_order = [best_bend.id] + state.order
        
        state = SequenceState(
            current_shape=state.current_shape, # Ignore geometry updates in fast stage
            bends_done=frozenset(next_bends_done),
            bends_remaining=next_bends_remaining,
            order=next_order,
            cost=state.cost + calculate_step_cost(state, best_bend, config)
        )
        
    return state.order

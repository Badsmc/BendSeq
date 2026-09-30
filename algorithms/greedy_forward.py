# algorithms/greedy_forward.py
from typing import List, Optional
from ..core.models.sequence_state import SequenceState
from ..core.models.bend_spec import BendSpec
from .topology import filter_candidates_forward
from .scoring import calculate_step_cost

def search(initial_state: SequenceState, all_bends: List[BendSpec], config: dict) -> Optional[List[str]]:
    """
    Fast greedy search forward from flat to fully bent.
    Uses only topology and scoring.
    """
    state = initial_state
    bends_by_id = {b.id: b for b in all_bends}
    
    while state.bends_remaining:
        candidates = filter_candidates_forward(state, all_bends)
        if not candidates:
            return None
            
        prev_bend_obj = bends_by_id[state.order[-1]] if state.order else None
        
        candidates.sort(key=lambda b: calculate_step_cost(state, b, prev_bend_obj, config))
        best_bend = candidates[0]
        step_cost = calculate_step_cost(state, best_bend, prev_bend_obj, config)
        
        next_bends_remaining = set(state.bends_remaining)
        next_bends_remaining.remove(best_bend.id)
        next_bends_done = set(state.bends_done)
        next_bends_done.add(best_bend.id)
        
        next_order = state.order + [best_bend.id]
        
        state = SequenceState(
            current_shape=state.current_shape,
            bends_done=frozenset(next_bends_done),
            bends_remaining=next_bends_remaining,
            order=next_order,
            cost=state.cost + step_cost
        )
        
    return state.order

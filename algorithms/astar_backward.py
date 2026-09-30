# algorithms/astar_backward.py
import heapq
from typing import List, Optional
from ..core.models.sequence_state import SequenceState
from ..core.models.bend_spec import BendSpec
from .topology import filter_candidates_backward
from .scoring import calculate_step_cost

class StateNode:
    def __init__(self, state: SequenceState, g: float, h: float):
        self.state = state
        self.g = g
        self.h = h
        self.f = g + h
        
    def __lt__(self, other):
        return self.f < other.f

def search(initial_state: SequenceState, all_bends: List[BendSpec], config: dict) -> Optional[List[str]]:
    """
    A* search backward from bent to flat.
    """
    bends_by_id = {b.id: b for b in all_bends}
    open_set = []
    closed_set = set()
    
    start_node = StateNode(initial_state, 0.0, float(len(initial_state.bends_remaining)))
    heapq.heappush(open_set, start_node)
    
    while open_set:
        current_node = heapq.heappop(open_set)
        state = current_node.state
        
        if not state.bends_remaining:
            return state.order
            
        if state.key in closed_set:
            continue
        closed_set.add(state.key)
        
        candidates = filter_candidates_backward(state, [bends_by_id[bid] for bid in state.bends_remaining])
        prev_bend_obj = bends_by_id[state.order[0]] if state.order else None
        
        for cand in candidates:
            cost = calculate_step_cost(state, cand, prev_bend_obj, config)
            next_bends_remaining = set(state.bends_remaining)
            next_bends_remaining.remove(cand.id)
            next_bends_done = set(state.bends_done)
            next_bends_done.add(cand.id)
            
            next_state = SequenceState(
                current_shape=state.current_shape,
                bends_done=frozenset(next_bends_done),
                bends_remaining=next_bends_remaining,
                order=[cand.id] + state.order,
                cost=state.cost + cost
            )
            
            if next_state.key not in closed_set:
                g = current_node.g + cost
                h = float(len(next_bends_remaining))
                heapq.heappush(open_set, StateNode(next_state, g, h))
                
    return None

# algorithms/physical_dfs.py
import time
from typing import List, Optional, Any
from ..core.models.sequence_state import SequenceState
from ..core.models.bend_spec import BendSpec
from .topology import filter_candidates_backward

class PhysicalOracle:
    """Wrapper that combines fold_engine + collision_engine + transform."""
    def __init__(self, fold_engine, collision_engine):
        self.fold_engine = fold_engine
        self.collision_engine = collision_engine

    def try_unbend(self, state: SequenceState, bend: BendSpec) -> Optional[Any]:
        if not self.fold_engine.can_apply(state.current_shape, bend):
            return None
            
        result = self.fold_engine.apply(state.current_shape, bend, is_unfold=True)
        if not result.ok:
            return None
            
        new_shape = result.shape
        errors = self.collision_engine.check_all(new_shape, self.tooling)
        if errors:
            return None
            
        return new_shape

def search(initial_state: SequenceState, all_bends: List[BendSpec], oracle: PhysicalOracle, config: dict) -> Optional[List[str]]:
    """
    Full physical DFS with backtracking using the PhysicalOracle.
    Respects the time budget.
    """
    start_time = time.time()
    budget = config.get("time_budget_stage3", 15.0)
    
    dead_states = set()
    bends_by_id = {b.id: b for b in all_bends}
    
    def dfs(state: SequenceState) -> Optional[List[str]]:
        if time.time() - start_time > budget:
            return None
            
        if not state.bends_remaining:
            return state.order
            
        if state.key in dead_states:
            return None
            
        candidates = filter_candidates_backward(state, [bends_by_id[bid] for bid in state.bends_remaining])
        
        for bend in candidates:
            new_shape = oracle.try_unbend(state, bend)
            if new_shape:
                next_bends_remaining = set(state.bends_remaining)
                next_bends_remaining.remove(bend.id)
                next_bends_done = set(state.bends_done)
                next_bends_done.add(bend.id)
                
                next_order = [bend.id] + state.order
                
                next_state = SequenceState(
                    current_shape=new_shape,
                    bends_done=frozenset(next_bends_done),
                    bends_remaining=next_bends_remaining,
                    order=next_order,
                    cost=state.cost
                )
                
                result = dfs(next_state)
                if result:
                    return result
                    
        dead_states.add(state.key)
        return None
        
    return dfs(initial_state)

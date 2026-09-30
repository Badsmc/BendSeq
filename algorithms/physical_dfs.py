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
        errors = self.collision_engine.check_all(new_shape, getattr(self, "tooling", {}))
        if errors:
            return None
            
        return result

def search(initial_state: SequenceState, all_bends: List[BendSpec], oracle: PhysicalOracle, config: dict) -> Optional[List[str]]:
    """
    Full physical DFS with backtracking using the PhysicalOracle.
    Respects the time budget.
    """
    start_time = time.time()
    budget = config.get("time_budget_stage3", 15.0)
    
    dead_states = set()
    bends_by_id = {b.id: b for b in all_bends}
    
    def dfs(state: SequenceState, current_specs: dict) -> Optional[List[str]]:
        if time.time() - start_time > budget:
            return None
            
        if not state.bends_remaining:
            return state.order
            
        if state.key in dead_states:
            return None
            
        candidates = filter_candidates_backward(state, [current_specs[bid] for bid in state.bends_remaining])
        
        for bend in candidates:
            result = oracle.try_unbend(state, bend)
            if result:
                new_shape = result.shape
                t_info = getattr(result, "transform_info", None)
                
                next_specs = {}
                from ..core.geometry.transform import compute_force_ids, transform_bend_spec_inplace, clone_spec
                force_ids = compute_force_ids(bend, [s for s in current_specs.values() if s.id != bend.id])
                
                for bid, spec in current_specs.items():
                    if bid == bend.id: continue
                    cloned = clone_spec(spec)
                    if t_info and bid in force_ids:
                        placement = t_info.get("placement")
                        if placement:
                            transform_bend_spec_inplace(cloned, placement)
                    next_specs[bid] = cloned
                
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
                
                res = dfs(next_state, next_specs)
                if res:
                    return res
                    
        dead_states.add(state.key)
        return None
        
    return dfs(initial_state, bends_by_id)

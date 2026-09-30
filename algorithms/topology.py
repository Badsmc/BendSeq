# algorithms/topology.py
from typing import List, Set
from ..core.models.bend_spec import BendSpec
from ..core.models.sequence_state import SequenceState

def filter_candidates_backward(state: SequenceState, all_bends: List[BendSpec]) -> List[BendSpec]:
    """
    Returns candidate bends that can be unbent (undone) from the current state.
    Prefers outside-in (leaf-first) based on SheetMetal feature dependencies.
    """
    remaining_bends = [b for b in all_bends if b.id in state.bends_remaining]
    if not remaining_bends:
        return []
        
    remaining_features = {b.metadata.get("feature", b.id): b for b in remaining_bends}
    
    parent_features_in_use = set()
    for b in remaining_bends:
        p = b.metadata.get("parent_feature")
        if p and p in remaining_features:
            parent_features_in_use.add(p)
            
    candidates = []
    for b in remaining_bends:
        feat = b.metadata.get("feature", b.id)
        if feat not in parent_features_in_use:
            candidates.append(b)
            
    # Fallback if no leaves found (should not happen in valid SM tree)
    if not candidates:
        return remaining_bends
        
    return candidates
def filter_candidates_forward(state: SequenceState, all_bends: List[BendSpec]) -> List[BendSpec]:
    """
    Returns candidate bends that can be bent (done) from the current flat-ish state.
    Requires parent features to be already bent.
    """
    remaining_bends = [b for b in all_bends if b.id in state.bends_remaining]
    if not remaining_bends:
        return []
        
    done_features = set()
    for bid in state.bends_done:
        for b in all_bends:
            if b.id == bid:
                done_features.add(b.metadata.get("feature", b.id))
                break
                
    candidates = []
    for b in remaining_bends:
        p = b.metadata.get("parent_feature")
        if not p or p in done_features:
            candidates.append(b)
            
    if not candidates:
        return remaining_bends
    return candidates

# algorithms/scoring.py
from typing import Dict, Any, Optional
from ..core.models.sequence_state import SequenceState
from ..core.models.bend_spec import BendSpec

def calculate_step_cost(state: SequenceState, next_bend: BendSpec, prev_bend: Optional[BendSpec], config: Dict[str, Any]) -> float:
    """
    Calculates workshop penalty score for making this bend next.
    Considers tool changes, part rotation, flipping, etc.
    """
    cost = config.get("penalty_base", 1.0)
    if not prev_bend:
        return cost
        
    w_flip = config.get("penalty_flip", 2.0)
    w_rot = config.get("penalty_rotation", 1.0)
    w_tool = config.get("penalty_tool_change", 2.0)
    w_len = config.get("penalty_tool_length", 1.0)
    w_feature = config.get("penalty_feature", 0.3)
    
    if next_bend.direction != prev_bend.direction:
        cost += w_flip
        
    dot = next_bend.axis.dot(prev_bend.axis)
    cost += (1.0 - abs(dot)) * w_rot
    
    if abs(next_bend.radius - prev_bend.radius) > 1e-3:
        cost += w_tool
        
    if abs(next_bend.length - prev_bend.length) > 1.0:
        cost += w_len
        
    n_feat = next_bend.metadata.get("parent_feature")
    p_feat = prev_bend.metadata.get("parent_feature")
    if n_feat and p_feat and n_feat != p_feat:
        cost += w_feature
        
    return cost

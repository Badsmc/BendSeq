# algorithms/staged_solver.py
from typing import List, Dict, Any
from ..core.models.bend_spec import BendSpec
from ..core.models.sequence_state import SequenceState
from . import greedy_backward
from . import physical_dfs

def solve(initial_shape: Any, bends: List[BendSpec], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrates the sequence search through stages.
    Stage 1: Topology/Fast search (greedy_backward/astar_backward)
    Stage 2: Full physical validation
    """
    # 1. Initialize states
    bends_remaining = set(b.id for b in bends)
    state = SequenceState(
        current_shape=initial_shape,
        bends_done=frozenset(),
        bends_remaining=bends_remaining,
        order=[]
    )
    
    stats = {"time_taken": 0.0, "nodes_visited": 0}
    diagnostics = []
    
    # 2. Try fast backward first
    order = greedy_backward.search(state, bends, config)
    if order:
        return {"success": True, "order": order, "partial": False, "stats": stats, "diagnostics": diagnostics}
        
    from ..core.engines.fold_engine import FoldEngine
    from ..core.engines.collision_engine import CollisionEngine
    
    # 3. Fallback to physical search
    fold_engine = FoldEngine(config)
    collision_engine = CollisionEngine(config.get("collision_margin", 0.1))
    oracle = physical_dfs.PhysicalOracle(fold_engine, collision_engine)
    
    tooling = config.get("tooling", {})
    if tooling:
        import os
        from ..tooling.library import ToolLibrary
        lib_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ToolLibrary")
        if not os.path.exists(lib_dir):
            lib_dir = "/Users/badmc/Desktop/BendSeq/ToolLibrary"
        lib = ToolLibrary(lib_dir)
        
        punch_shape = None
        die_shape = None
        
        punch_name = tooling.get("punch")
        if punch_name:
            for p in lib.data.get("punches", []):
                if p.get("name") == punch_name or p.get("id") == punch_name:
                    punch_shape = lib.get_tool_shape("punches", p.get("id"))
                    break
                    
        die_name = tooling.get("die")
        if die_name:
            for d in lib.data.get("dies", []):
                if d.get("name") == die_name or d.get("id") == die_name:
                    die_shape = lib.get_tool_shape("dies", d.get("id"))
                    break
                    
        oracle.tooling = {"punch": punch_shape, "die": die_shape}
    
    order = physical_dfs.search(state, bends, oracle, config)
    if order:
        return {"success": True, "order": order, "partial": False, "stats": stats, "diagnostics": diagnostics}
    
    return {"success": False, "order": [], "partial": True, "stats": stats, "diagnostics": ["Search exhausted."]}

"""
dfs_backward.py - Reference Backward DFS Solver with Physical Oracle (SMBS Phase 6)

SPEC v1.0 Requirement (Section 20 & 43):
First production/reference solver: Backward DFS + Backtracking operating directly on Physical Oracle.
Uses `dead_states` set to prune known dead-ends and explicit path tracking to avoid FoldState memory leaks.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from Core.fold_state import FoldState
from Core.bend_graph import BendGraph, BendRecord
from Core.panel_graph import PanelGraph
from Physics.validator import PhysicalValidator, ValidationResult
from .base_planner import BasePlanner


class DFSBackwardPlanner:
    """
    Reference Backward Depth-First Search (DFS) Planner with Backtracking.
    """

    def __init__(
        self,
        bend_graph: BendGraph,
        validator: PhysicalValidator,
        panel_graph: Optional[PanelGraph] = None
    ):
        self.bend_graph = bend_graph
        self.validator = validator
        self.panel_graph = panel_graph
        self.rejection_records: List[Dict[str, Any]] = []

    def solve(
        self,
        initial_state: FoldState,
        max_depth: int = 500,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute backward DFS search with backtracking and dead-state pruning.

        :param initial_state: Root FoldState (fully bent 3D part).
        :param max_depth: Maximum recursion search depth limit.
        :param timeout: Maximum allowed execution time in seconds.
        :return: Result dictionary containing 'success', 'sequence', 'explored_count'.
        """
        import time
        start_time = time.time()
        explored_count = 0
        self.rejection_records.clear()
        dead_states: Set[str] = set()

        def _dfs(current: FoldState, depth: int, current_path: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
            nonlocal explored_count
            explored_count += 1
            
            if timeout is not None and (time.time() - start_time) > timeout:
                return None
            
            fingerprint = current.fingerprint()
            if fingerprint in dead_states:
                return None

            if current.is_goal():
                return list(current_path)

            if depth >= max_depth:
                return None

            def score_candidate(b_id: str) -> int:
                """Cheap topological score: prioritize outer bends (fewer moving panels)."""
                if self.panel_graph:
                    return len(self.panel_graph.moving_subtree(b_id))
                return 0

            def get_symmetry_signature(b_id: str) -> str:
                """Create a signature for a bend to detect symmetric sibling branches."""
                bend_rec = self.bend_graph.get_bend(b_id)
                if not bend_rec:
                    return b_id
                score = score_candidate(b_id)
                # Bends from the same parent with same angle, length, and moving subtree size are topologically symmetric.
                return f"{bend_rec.parent_panel_id}_{bend_rec.signed_angle:.1f}_{bend_rec.length:.1f}_{score}"

            all_candidates = sorted(list(current.remaining_bends), key=score_candidate)
            
            # Point 4: Symmetry Pruning
            candidates = []
            seen_signatures = set()
            for b_id in all_candidates:
                sig = get_symmetry_signature(b_id)
                if sig not in seen_signatures:
                    seen_signatures.add(sig)
                    candidates.append(b_id)
                else:
                    # Skip this branch, it's identical to a sibling we are already checking!
                    pass

            from concurrent.futures import ThreadPoolExecutor
            
            # Prepare valid candidates
            valid_successors = []
            
            # Use ThreadPoolExecutor to validate all candidates for the current state in parallel.
            # This massively speeds up the search because OCC BRepExtrema operations are CPU-bound 
            # and FreeCAD releases the GIL during heavy C++ geometry operations.
            with ThreadPoolExecutor() as executor:
                futures = []
                for bend_id in candidates:
                    bend_rec = self.bend_graph.get_bend(bend_id)
                    if bend_rec is None:
                        continue

                    # Predictive cache check
                    next_fp = current.predict_successor_fingerprint(bend_id)
                    if next_fp in dead_states:
                        continue

                    # Submit validation task
                    f = executor.submit(
                        self.validator.validate_step,
                        current,
                        bend_rec,
                        self.panel_graph
                    )
                    futures.append((bend_id, f))

                # Collect results in topological order
                for bend_id, f in futures:
                    val_result: ValidationResult = f.result()
                    
                    if not val_result.valid:
                        self.rejection_records.append({
                            "bend_id": bend_id,
                            "stage": val_result.stage,
                            "reason": val_result.reason,
                            "depth": depth
                        })
                        continue

                    if val_result.next_state is not None:
                        valid_successors.append((bend_id, val_result.next_state))

            # DFS Recurse on valid successors
            for bend_id, successor in valid_successors:
                moving_panels = list(self.panel_graph.moving_subtree(bend_id)) if self.panel_graph else []
                action = {
                    "bend_id": bend_id,
                    "unfolded_angle": 0.0,
                    "moving_panels": moving_panels,
                    "step_number": len(current.remaining_bends)
                }
                
                current_path.append(action)
                result_path = _dfs(successor, depth + 1, current_path)
                
                # Cleanup if branch failed
                if result_path is None:
                    if hasattr(successor, "shape") and successor.shape is not None:
                        if hasattr(successor.shape, "nullify"):
                            try:
                                successor.shape.nullify()
                            except Exception:
                                pass
                        successor.shape = None
                    current_path.pop()
                else:
                    # Clear remaining unused valid successors to save memory
                    for b_id, s in valid_successors:
                        if s != successor and hasattr(s, "shape") and s.shape is not None:
                            try: s.shape.nullify()
                            except: pass
                    return result_path

            # Dead end
            dead_states.add(fingerprint)
            return None

        # Execute DFS
        final_path = _dfs(initial_state, 0, [])

        if final_path is not None:
            # The path built during backward DFS needs to be inverted for forward bending!
            # If path is [Bend3, Bend1, Bend2], the forward sequence is Bend2, Bend1, Bend3
            # Wait, step_number is already assigned descending (len(remaining)).
            # Let's just reverse the path:
            forward_sequence = list(reversed(final_path))
            # Fix step_numbers to be sequential
            for i, step in enumerate(forward_sequence):
                step["step_number"] = i + 1

            return {
                "success": True,
                "sequence": forward_sequence,
                "explored_count": explored_count,
                "rejections_count": len(self.rejection_records),
                "dead_states_count": len(dead_states)
            }

        return {
            "success": False,
            "error": f"DFS search exhausted after exploring {explored_count} states without finding a valid path.",
            "explored_count": explored_count,
            "rejections": self.rejection_records,
            "dead_states_count": len(dead_states)
        }

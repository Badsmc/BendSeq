# core/models/sequence_state.py
import dataclasses
from typing import List, Set, Any

@dataclasses.dataclass
class SequenceState:
    current_shape: Any
    bends_done: Set[str]
    bends_remaining: Set[str]
    order: List[str]
    cost: float = 0.0
    diagnostics: List[str] = dataclasses.field(default_factory=list)

    @property
    def key(self):
        """Returns a hashable key for state caching."""
        return frozenset(self.bends_done)

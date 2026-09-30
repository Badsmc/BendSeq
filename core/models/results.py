# core/models/results.py
import dataclasses
from typing import List, Optional, Any, Dict

@dataclasses.dataclass
class UnfoldResult:
    ok: bool
    unfolded_shape: Optional[Any] = None
    bend_lines: List[Any] = dataclasses.field(default_factory=list)
    root_normal: Optional[Any] = None
    bend_info: List[Any] = dataclasses.field(default_factory=list)
    error: Optional[str] = None
    engine: Optional[str] = None

@dataclasses.dataclass
class FoldResult:
    ok: bool
    shape: Optional[Any] = None
    error: Optional[str] = None
    engine: Optional[str] = None

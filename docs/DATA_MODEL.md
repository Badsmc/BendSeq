# BendSeq Data Model

## `BendSpec`
Represents a bend operation in the system.
- **id**: String identifier.
- **angle**: Bend angle in degrees.
- **radius**: Bend inner radius.
- **k_factor**: Neutral axis factor.
- **line_p1, line_p2**: FreeCAD Vectors representing the bend line.

## `SequenceState`
Represents a node in the sequence search graph.
- **current_shape**: The FreeCAD TopoShape at this step.
- **bends_done**: Frozenset of completed bend IDs (used for caching).
- **bends_remaining**: Set of bend IDs yet to be processed.
- **order**: List of bend IDs representing the sequence taken to reach this state.
- **cost**: Accumulated workshop penalty.

## `Panel`
A simple topology representation.
- **id**: Panel string identifier.
- **face**: FreeCAD Face reference.
- **is_base**: Boolean flag.

## `Results`
- `UnfoldResult`: Unfolded shape, bend lines, normals.
- `FoldResult`: Result of folding operation.

# BendSeq Architecture

## Core Philosophy
BendSeq strictly separates the logic into Data Models, Physical Engines, Search Algorithms, and UI via a Facade.
It never vendors the SheetMetal unfolder source code. Instead, it relies entirely on the FreeCAD Python API for geometry operations and upstream SheetMetal workbench for fold/unfold.

## Directory Structure
- **adapters/**: Bridges the FreeCAD and SheetMetal API to BendSeq's data model.
  - `sheetmetal_api.py`: The ONLY gateway to unfold/fold.
  - `freecad_adapter.py`: FreeCAD selection extraction.
  - `overlay.py`: 3D and 2D number drawing.
- **core/**: Core pure domain logic.
  - `models/`: Pure Python dataclasses.
  - `geometry/transform.py`: Single source of truth for shape manipulations.
  - `engines/`: Physical/Collision engines wrapping FreeCAD logic.
- **algorithms/**: Pure python search algorithms (Greedy, A*, DFS).
- **simulation/**: State machine for viewing steps and smooth animations.
- **tooling/**: `library.py` caching BREP objects for collisions.
- **ui/**: Task panels and FreeCAD UI commands.
- `facade.py`: The central orchestrator interface for `ui/`.

## Staged Solver
1. **Stage 1 (Topology)**: Reduce candidates using panel connectivity.
2. **Stage 2 (Fast Search)**: Greedy or A* backward.
3. **Stage 3 (Physical DFS)**: Full collision checking using `PhysicalOracle`.

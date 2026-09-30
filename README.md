# BendSeq

A FreeCAD Addon for automatic SheetMetal bend sequencing and simulation.

## Requirements
- FreeCAD 1.0 or newer.
- `SheetMetal` workbench MUST be installed via Addon Manager.

## Features
- Automatic bend sequence search (backward and forward algorithms).
- 3D step simulation of bending with smooth motion.
- Sequence numbers displayed on the SheetMetal unfold and on the 3D model during simulation.
- Parametric ToolLibrary support.

## Usage
1. Open a FreeCAD document with a SheetMetal part.
2. Select the base face of the unfolded part.
3. Run **BendSeq Auto Sequence** from the BendSeq workbench.
4. Open the **BendSeq Simulation Viewer** to see the simulated sequence.

## License
LGPL-2.1

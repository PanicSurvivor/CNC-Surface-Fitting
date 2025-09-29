# CNC Surface Fitting (G-code Z Correction)
A small PyQt5 desktop app that loads a probed surface map (x, y, z) and an existing G-code file, then adjusts Z along the toolpath to follow the measured surface (nearest-neighbor). Includes a 3D preview of the surface and the corrected path.

## Features
- Load surface map (.txt) with three columns: 'x,y,z' (no header).
- (Optional) Use the “Normalize X/Y Coordinates” toggle and min/max fields to remap XY ranges before fitting.
- Visualize a nearest-neighbor surface (KD-Tree) against probed points.
- Load a G-code file and offset Z along 'G01' linear moves to match the surface.
- Preview the corrected toolpath in 3D and export corrected G-code.


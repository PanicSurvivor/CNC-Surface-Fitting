# CNC Surface Fitting (G-code Z Correction)
A small PyQt5 desktop app that loads a probed surface map (x, y, z) and an existing G-code file, then adjusts Z along the toolpath to follow the measured surface (nearest-neighbor). Includes a 3D preview of the surface and the corrected path.

## Features
- Load surface map (.txt) with three columns: ```x,y,z``` (no header).
- (Optional) Use the “Normalize X/Y Coordinates” toggle and min/max fields to remap XY ranges before fitting.
- Visualize a nearest-neighbor surface (KD-Tree) against probed points.
- Load a G-code file and offset Z along ```G01``` linear moves to match the surface.
- Preview the corrected toolpath in 3D and export corrected G-code.

## Requirements
Python 3.9+
Windows / Linux / macOS with a working Qt GUI
Packages:
- numpy
- scipy
- matplotlib
- PyQt5
Intallation:
```
pip install -r requirements.txt
```

## Run
### Option 1 - Run from the source (no install)
```
python src/cnc_surface_fit/app.py
```
### Option 2 - Use the launcher
```
python -m cnc_surface_fit
```
### Option 3 - Consule command
```
pip install -e "."
cnc-surface-fit
```
## Workflow 
### 1. Load Surface Map
Click “Load surface_map.txt” and choose a map file with 3 columns ```x,y,z``` (no header).
Example: examples/surface_map.txt (values in mmm)
### 2. (Optional) X/Y Normalization 
Use the “Normalize X/Y Coordinates” toggle and min/max fields to remap XY ranges before fitting.
### 3. Fit Surface
Builds a KD-Tree and shows a coarse 3D surface via nearest-neighbor lookup, overlaying your probe points.
### 4. Load Original G-Code
Click “Load original G-code” and pick a file in absolute units (mm), with linear moves (```G1/G01```) and words ```X```, ```Y```, ```Z```.
Example: examples/star.gcode 
### 5. Correct G-Code
The app computes the cutting depth as ```abs(min(Z))``` from your file and subtracts it from the probed surface so the relative cut depth is preserved. It then replaces/appends ```Z``` on ```G01``` moves using nearest-neighbor surface values and prompts you to save the corrected file. A 3D preview of the corrected path is shown.

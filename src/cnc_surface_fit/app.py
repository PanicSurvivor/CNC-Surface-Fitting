import numpy as np
import re

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QSpinBox, QTextEdit, QHBoxLayout,
    QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt
import sys

# USE the split helpers, but keep behavior identical
from cnc_surface_fit.surface import build_kdtree, make_grid, nearest_Z_grid
from cnc_surface_fit.gcode import detect_depth, correct_lines

class SurfaceFittingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Surface Fitting & G-code Correction")
        self.setGeometry(100, 100, 1200, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        file_layout = QHBoxLayout()
        self.load_surface_button = QPushButton("Load surface_map.txt")
        self.load_surface_button.clicked.connect(self.load_surface_map)
        self.load_gcode_button = QPushButton("Load original G-code")
        self.load_gcode_button.clicked.connect(self.load_gcode_file)
        file_layout.addWidget(self.load_surface_button)
        file_layout.addWidget(self.load_gcode_button)
        main_layout.addLayout(file_layout)

        self.splitter = QSplitter(Qt.Vertical)
        self.figure = plt.figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.addWidget(self.canvas)

        self.equation_output = QTextEdit()
        self.equation_output.setReadOnly(True)
        self.splitter.addWidget(self.equation_output)
        main_layout.addWidget(self.splitter)

        # --- Normalization UI ---
        norm_layout = QHBoxLayout()

        self.normalize_checkbox = QPushButton("Normalize X/Y Coordinates")
        self.normalize_checkbox.setCheckable(True)
        norm_layout.addWidget(self.normalize_checkbox)

        norm_layout.addWidget(QLabel("X Min:"))
        self.x_min_input = QTextEdit()
        self.x_min_input.setFixedHeight(25)
        self.x_min_input.setFixedWidth(100)
        norm_layout.addWidget(self.x_min_input)

        norm_layout.addWidget(QLabel("X Max:"))
        self.x_max_input = QTextEdit()
        self.x_max_input.setFixedHeight(25)
        self.x_max_input.setFixedWidth(100)
        norm_layout.addWidget(self.x_max_input)

        norm_layout.addWidget(QLabel("Y Min:"))
        self.y_min_input = QTextEdit()
        self.y_min_input.setFixedHeight(25)
        self.y_min_input.setFixedWidth(100)
        norm_layout.addWidget(self.y_min_input)

        norm_layout.addWidget(QLabel("Y Max:"))
        self.y_max_input = QTextEdit()
        self.y_max_input.setFixedHeight(25)
        self.y_max_input.setFixedWidth(100)
        norm_layout.addWidget(self.y_max_input)

        main_layout.addLayout(norm_layout)

        self.fit_surface_button = QPushButton("Fit Surface Only")
        self.fit_surface_button.clicked.connect(self.fit_surface)
        self.correct_gcode_button = QPushButton("Correct G-code")
        self.correct_gcode_button.clicked.connect(self.fit_and_correct)
        main_layout.addWidget(self.fit_surface_button)
        main_layout.addWidget(self.correct_gcode_button)

        self.X = self.Y = self.Z = None
        self.gcode_lines = []
        self.corrected_gcode = []

    def load_surface_map(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Surface Map File", "", "Text Files (*.txt)")
        if file_path:
            data = np.loadtxt(file_path, delimiter=',')
            self.X, self.Y, raw_Z = data[:, 0], data[:, 1], data[:, 2]

            # Apply optional normalization (kept exactly as in your original code)
            if self.normalize_checkbox.isChecked():
                try:
                    z_min = float(self.z_min_input.toPlainText())
                    z_max = float(self.z_max_input.toPlainText())
                    z_norm = (raw_Z - raw_Z.min()) / (raw_Z.max() - raw_Z.min())
                    self.Z = z_norm * (z_max - z_min) + z_min
                    self.equation_output.setText(f"Surface Z normalized to range ({z_min}, {z_max})")
                except Exception as e:
                    self.Z = raw_Z
                    self.equation_output.setText("⚠ Failed to normalize Z: " + str(e))
            else:
                self.Z = raw_Z

            self.equation_output.append(f"Loaded {len(self.X)} surface points.")

    def load_gcode_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open G-code File", "", "G-code Files (*.gcode *.nc *.txt)")
        if file_path:
            with open(file_path, 'r') as f:
                self.gcode_lines = f.readlines()
            self.equation_output.append(f"Loaded {len(self.gcode_lines)} G-code lines.")

    def fit_surface(self):
        if self.X is None or self.Y is None or self.Z is None:
            self.equation_output.setText("Please load a surface map file.")
            return

        # Normalize X and Y if enabled (kept exactly as in your original code)
        if self.normalize_checkbox.isChecked():
            try:
                x_min = float(self.x_min_input.toPlainText())
                x_max = float(self.x_max_input.toPlainText())
                y_min = float(self.y_min_input.toPlainText())
                y_max = float(self.y_max_input.toPlainText())

                orig_x_min, orig_x_max = self.X.min(), self.X.max()
                orig_y_min, orig_y_max = self.Y.min(), self.Y.max()

                x_norm = (self.X - orig_x_min) / (orig_x_max - orig_x_min)
                y_norm = (self.Y - orig_y_min) / (orig_y_max - orig_y_min)

                self.X = x_norm * (x_max - x_min) + x_min
                self.Y = y_norm * (y_max - y_min) + y_min

                self.equation_output.setText(
                    f"✅ Normalized X and Y:\n"
                    f"Original X range: ({orig_x_min:.4f}, {orig_x_max:.4f}) → ({x_min}, {x_max})\n"
                    f"Original Y range: ({orig_y_min:.4f}, {orig_y_max:.4f}) → ({y_min}, {y_max})"
                )

            except Exception as e:
                self.equation_output.setText("⚠ Failed to normalize X/Y: " + str(e))

        # Build KD-tree and grid (moved, same behavior)
        self.kdtree = build_kdtree(self.X, self.Y)
        self.Z_values = self.Z.copy()
        self.equation_output.append("KD-tree created for nearest-neighbor lookup.")

        grid_size = 30
        self.X_grid, self.Y_grid = make_grid(self.X, self.Y, grid_size=grid_size)
        Z_grid = nearest_Z_grid(self.X_grid, self.Y_grid, self.kdtree, self.Z_values)

        self.figure.clear()
        ax = self.figure.add_subplot(121, projection='3d')
        ax.plot_surface(self.X_grid, self.Y_grid, Z_grid, cmap='viridis', alpha=0.8)
        ax.scatter(self.X, self.Y, self.Z, color='red', s=20)
        ax.set_title("Nearest Neighbor Surface (Normalized)" if self.normalize_checkbox.isChecked() else "Nearest Neighbor Surface")
        self.canvas.draw()

    def fit_and_correct(self):
        if self.X is None or self.Y is None or self.Z is None or not self.gcode_lines:
            self.equation_output.setText("Please load both surface map and G-code file.")
            return

        depth = detect_depth(self.gcode_lines)  # same computation as before
        corrected_lines = correct_lines(self.gcode_lines, self.kdtree, self.Z_values, depth)
        self.corrected_gcode = corrected_lines

        output_path, _ = QFileDialog.getSaveFileName(self, "Save Corrected G-code", "corrected_output.gcode", "G-code Files (*.gcode)")
        if not output_path:
            self.equation_output.append("\nSave cancelled.")
            return
        with open(output_path, 'w') as f:
            f.writelines(self.corrected_gcode)

        self.equation_output.append(f"\nCorrected G-code saved as '{output_path}'")

        ax2 = self.figure.add_subplot(122, projection='3d')
        gcode_x, gcode_y, gcode_z = [], [], []
        current_X = current_Y = None
        for line in self.corrected_gcode:
            match_x = re.search(r'X([-+]?\d*\.?\d+)', line)
            match_y = re.search(r'Y([-+]?\d*\.?\d+)', line)
            match_z = re.search(r'Z([-+]?\d*\.?\d+)', line)
            if match_x: current_X = float(match_x.group(1))
            if match_y: current_Y = float(match_y.group(1))
            if match_z and current_X is not None and current_Y is not None:
                gcode_x.append(current_X)
                gcode_y.append(current_Y)
                gcode_z.append(float(match_z.group(1)))

        if len(gcode_x) >= 2:
            ax2.plot(gcode_x, gcode_y, gcode_z, linestyle='dashed', marker='o', color='blue')
            ax2.set_title("Corrected G-code")
        else:
            ax2.text2D(0.1, 0.8, "Not enough G-code points to plot.", transform=ax2.transAxes)
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SurfaceFittingApp()
    window.show()
    sys.exit(app.exec_())
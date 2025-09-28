import numpy as np
from scipy.spatial import cKDTree

def build_kdtree(X: np.ndarray, Y: np.ndarray) -> cKDTree:
    """Build the KD-tree exactly like in the original code."""
    return cKDTree(np.column_stack((X, Y)))

def make_grid(X: np.ndarray, Y: np.ndarray, grid_size: int = 30):
    """Create the X/Y meshgrid exactly like the original code."""
    x_grid = np.linspace(X.min(), X.max(), grid_size)
    y_grid = np.linspace(Y.min(), Y.max(), grid_size)
    X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
    return X_grid, Y_grid

def nearest_Z_grid(X_grid: np.ndarray, Y_grid: np.ndarray, kdtree: cKDTree, Z_values: np.ndarray):
    """Fill Z_grid by nearest-neighbor lookup exactly like the original code."""
    Z_grid = np.zeros_like(X_grid)
    for i in range(X_grid.shape[0]):
        for j in range(X_grid.shape[1]):
            _, idx = kdtree.query([X_grid[i, j], Y_grid[i, j]])
            Z_grid[i, j] = Z_values[idx]
    return Z_grid
import re
from typing import List, Tuple

_Z_NUM = r'[-+]?\d*\.?\d+'
_WORD_RE = re.compile(rf'X({_Z_NUM})?|Y({_Z_NUM})?|Z({_Z_NUM})')

def detect_depth(gcode_lines: List[str]) -> float:
    """Compute depth = abs(min(Z)) exactly like your original code."""
    z_values = [float(m.group(1)) for line in gcode_lines
                if (m := re.search(rf'Z({_Z_NUM})', line))]
    return abs(min(z_values)) if z_values else 0.0

def correct_lines(gcode_lines: List[str], kdtree, Z_values, depth: float) -> List[str]:
    """Apply the same correction logic line-by-line as in your original code."""
    corrected_lines: List[str] = []
    current_X = None
    current_Y = None
    pattern = _WORD_RE

    for line in gcode_lines:
        original_line = line.strip()
        matches: List[Tuple[str, str, str]] = pattern.findall(original_line)
        for match in matches:
            if match[0]:
                current_X = float(match[0])
            if match[1]:
                current_Y = float(match[1])

        if original_line.startswith('G01') and current_X is not None and current_Y is not None:
            _, idx = kdtree.query([current_X, current_Y])
            corrected_Z = Z_values[idx] - depth
            if 'Z' in original_line:
                corrected_line = re.sub(rf'Z({_Z_NUM})', f'Z{corrected_Z:.4f}', original_line)
            else:
                corrected_line = original_line + f' Z{corrected_Z:.4f}'
        else:
            corrected_line = original_line

        corrected_lines.append(corrected_line + '\n')

    return corrected_lines
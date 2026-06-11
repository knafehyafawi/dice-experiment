"""
view_web.py — view the d30 in a smooth, GPU-accelerated WebGL window,
generated entirely from your own code (same three.js tech viewstl uses).

    python view_web.py        # writes d30_view.html and opens it in your browser

Drag to rotate, scroll to zoom. No matplotlib, no plugins.
"""

import webbrowser
import numpy as np
import trimesh
from trimesh.viewer import scene_to_html

from geometry import rhombic_triacontahedron, die_data


def build_colored_mesh():
    mesh = rhombic_triacontahedron()
    data = die_data(mesh)

    # one colour per logical face, then map each triangle to its face's colour
    face_palette = trimesh.visual.color.interpolate(
        np.linspace(0, 1, 30), color_map="viridis"
    )
    mesh.visual.face_colors = face_palette[data["tri_to_face"]]
    return mesh


def main():
    mesh = build_colored_mesh()
    scene = mesh.scene()
    html = scene_to_html(scene)
    out = "d30_view.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {out}")
    webbrowser.open(out)


if __name__ == "__main__":
    main()
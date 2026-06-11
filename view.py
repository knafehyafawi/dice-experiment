"""
view.py — render the d30 so you can actually see it.

Run it two ways:
    python view.py            # opens an interactive window you can rotate
    python view.py --save     # writes d30_render.png instead

Uses matplotlib only (no extra 3D/GUI plugins needed).
"""

import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from geometry import rhombic_triacontahedron, die_data


def render(save=False, show_numbers=True):
    mesh = rhombic_triacontahedron()
    data = die_data(mesh)
    V = data["vertices"]
    tris = data["triangles"]              # (60,3) triangle vertex indices
    tri_to_face = data["tri_to_face"]     # which logical face each triangle is

    # one colour per logical face (so each rhombus reads as a single unit)
    cmap = plt.get_cmap("twilight")
    face_colors = cmap(np.linspace(0, 1, 30))

    polys = [V[t] for t in tris]
    colors = [face_colors[tri_to_face[i]] for i in range(len(tris))]

    if save:
        matplotlib.use("Agg")
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    coll = Poly3DCollection(polys, facecolors=colors, edgecolors="k", linewidths=0.4, alpha=1.0)
    ax.add_collection3d(coll)

    if show_numbers:
        # put each face's value at the face centroid, pushed slightly outward
        for face_id in range(30):
            tri_ids = np.where(tri_to_face == face_id)[0]
            centroid = V[tris[tri_ids].reshape(-1)].mean(axis=0)
            label_pos = centroid * 1.08
            ax.text(*label_pos, str(int(data["face_value"][face_id])),
                    ha="center", va="center", fontsize=8, fontweight="bold")

    lim = np.abs(V).max() * 1.1
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.set_title("d30 — rhombic triacontahedron")
    fig.tight_layout()

    if save:
        fig.savefig("d30_render.png", dpi=130)
        print("wrote d30_render.png")
    else:
        plt.show()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true", help="save a PNG instead of opening a window")
    ap.add_argument("--no-numbers", action="store_true", help="hide face numbers")
    args = ap.parse_args()
    render(save=args.save, show_numbers=not args.no_numbers)
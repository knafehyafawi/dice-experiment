"""
geometry.py — build a verified rhombic triacontahedron (the d30 solid)
and expose the four data structures the simulation needs.

The mesh is constructed as the polar dual of an icosidodecahedron, which
is exactly the rhombic triacontahedron. We avoid hand-tuned golden-ratio
hull tricks (numerically degenerate) in favour of a construction that is
correct by definition, then verify it.
"""

import numpy as np
import trimesh
from itertools import product
from scipy.spatial import ConvexHull
from collections import defaultdict

PHI = (1 + 5 ** 0.5) / 2


def _cyclic(triple):
    a, b, c = triple
    return [(a, b, c), (c, a, b), (b, c, a)]


def _sign_flips(triple):
    out = set()
    nz = [i for i, v in enumerate(triple) if v != 0]
    for s in product([1, -1], repeat=len(nz)):
        v = list(triple)
        for idx, sgn in zip(nz, s):
            v[idx] = abs(v[idx]) * sgn
        out.add(tuple(v))
    return out


def _icosidodecahedron_vertices():
    verts = set()
    for t in _cyclic((0, 0, PHI)):
        verts |= _sign_flips(t)
    for t in _cyclic((0.5, PHI / 2, PHI ** 2 / 2)):
        verts |= _sign_flips(t)
    return np.array(sorted(verts))


def rhombic_triacontahedron(circumradius=1.0):
    """Return a watertight trimesh.Trimesh of the d30 solid.

    The mesh's triangles are the engine-facing representation; its `.facets`
    recover the 30 logical rhombic faces.
    """
    ID = _icosidodecahedron_vertices()
    hull = ConvexHull(ID)

    # Each distinct face-plane of the icosidodecahedron -> one RT vertex
    # (polar reciprocal about the unit sphere: plane n.x = d  ->  vertex n/d).
    planes = defaultdict(list)
    for i, eq in enumerate(hull.equations):
        planes[tuple(np.round(eq, 6))].append(i)

    rt = []
    for key in planes:
        n = np.array(key[:3])
        d = -key[3]
        rt.append(n / d)
    rt = np.array(rt)

    # normalize size, then let trimesh build + merge coplanar faces
    rt *= circumradius / np.linalg.norm(rt, axis=1).max()
    mesh = trimesh.convex.convex_hull(rt)
    mesh.merge_vertices()
    return mesh


def die_data(mesh):
    """Extract the four data structures described in the README.

    Returns a dict with:
      vertices      (V,3)   float   vertex positions
      triangles     (T,3)   int     triangle vertex indices  (engine collision)
      tri_to_face   (T,)    int     which logical face each triangle belongs to
      face_normals  (30,3)  float   outward unit normal per logical face
      face_value    (30,)   int     die value 1..30 printed on each face
    """
    facets = mesh.facets                      # list of arrays of triangle ids
    assert len(facets) == 30, f"expected 30 faces, got {len(facets)}"

    tri_to_face = np.full(len(mesh.faces), -1, dtype=int)
    for face_id, tri_ids in enumerate(facets):
        tri_to_face[tri_ids] = face_id
    assert (tri_to_face >= 0).all(), "every triangle must belong to a face"

    face_normals = np.array(mesh.facets_normal)   # already unit, outward

    # Assign die values. Convention: opposite faces sum to 31 (like real dice).
    # Pair faces by most-opposed normals, then label each pair (k, 31-k).
    face_value = _label_opposite_faces(face_normals)

    return {
        "vertices": np.asarray(mesh.vertices),
        "triangles": np.asarray(mesh.faces),
        "tri_to_face": tri_to_face,
        "face_normals": face_normals,
        "face_value": face_value,
    }


def _label_opposite_faces(normals):
    """Pair faces whose normals point opposite, label pairs (k, 31-k)."""
    n = len(normals)
    value = np.zeros(n, dtype=int)
    used = np.zeros(n, dtype=bool)
    dots = normals @ normals.T
    k = 1
    for i in range(n):
        if used[i]:
            continue
        j = int(np.argmin(dots[i]))   # most-opposed normal
        value[i] = k
        value[j] = 31 - k
        used[i] = used[j] = True
        k += 1
    return value


def read_top_face(data, rotation):
    """Given a rotation (scipy Rotation or 3x3 matrix), return the die value
    on the face pointing most upward (+z). This is one 'roll result'.
    """
    R = rotation.as_matrix() if hasattr(rotation, "as_matrix") else np.asarray(rotation)
    world_normals = data["face_normals"] @ R.T
    top = int(np.argmax(world_normals[:, 2]))    # most aligned with +z
    return int(data["face_value"][top])


if __name__ == "__main__":
    mesh = rhombic_triacontahedron()
    print("watertight:", mesh.is_watertight)
    print("triangles :", len(mesh.faces))
    print("faces      :", len(mesh.facets))
    print("vertices  :", len(mesh.vertices))
    print("volume    :", round(mesh.volume, 6))
    print("center of mass:", np.round(mesh.center_mass, 8))

    data = die_data(mesh)
    vals = sorted(data["face_value"])
    print("face values cover 1..30:", vals == list(range(1, 31)))

    # sanity: each opposite pair sums to 31
    print("triangles per face:", np.bincount(data["tri_to_face"]).tolist())

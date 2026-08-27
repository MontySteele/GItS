"""Skeleton math and polygon/weight generation.

Used by the cutout and mesh approaches. Kept out of `spec.py` because it is
approach-specific derivation, not part of the rig's definition -- the layered
and particle approaches never call any of it, and that asymmetry is itself one
of the source-burden findings.

Coordinate convention: everything below is in RIG SPACE (the space of the
`Rig` node), y-down, origin at the figure's waist-ish centre, matching
`spec.PARTS[*].rest`.
"""
from __future__ import annotations

from .art import PAD
from .spec import BONE_BY_NAME, BONES, PART_BY_NAME, Part


def bone_global(name: str) -> tuple[float, float]:
    """Rig-space position of a bone, by walking its parent chain."""
    x = y = 0.0
    cur: str | None = name
    while cur is not None:
        bone = BONE_BY_NAME[cur]
        x += bone.rest[0]
        y += bone.rest[1]
        cur = bone.parent
    return x, y


def bone_node_name(name: str) -> str:
    """`leg_front` -> `LegFront`. Bone2D node names are the animation path."""
    return "".join(word.capitalize() for word in name.split("_"))


def bone_path(name: str) -> str:
    """Skeleton-relative Godot node path for a bone, e.g. `Root/Hip/Spine`."""
    chain: list[str] = []
    cur: str | None = name
    while cur is not None:
        chain.append(bone_node_name(cur))
        cur = BONE_BY_NAME[cur].parent
    chain.reverse()
    return "/".join(chain)


def sprite_offset(part: Part) -> tuple[float, float]:
    """Where a part's sprite sits inside its driving bone (cutout approach)."""
    bx, by = bone_global(part.bone)
    return part.rest[0] - bx, part.rest[1] - by


# --------------------------------------------------------------------------
# polygons
# --------------------------------------------------------------------------

#: Vertical subdivisions for the torso. One ring per row, walked down the left
#: side and back up the right, so that hip/spine/neck weights actually bend it
#: instead of translating it rigidly.
TORSO_ROWS = 5


def part_rect(part: Part) -> tuple[float, float, float, float]:
    """Rig-space (left, top, right, bottom) of a part's padded layer."""
    w = part.size[0] + 2 * PAD
    h = part.size[1] + 2 * PAD
    return (
        part.rest[0] - w / 2,
        part.rest[1] - h / 2,
        part.rest[0] + w / 2,
        part.rest[1] + h / 2,
    )


def polygon_for(part: Part) -> list[tuple[float, float]]:
    """Rig-space outline. The torso is subdivided; everything else is a quad."""
    left, top, right, bottom = part_rect(part)
    if part.name != "torso":
        return [(left, top), (right, top), (right, bottom), (left, bottom)]
    rows = TORSO_ROWS
    verts: list[tuple[float, float]] = []
    for i in range(rows):  # down the left edge
        t = i / (rows - 1)
        verts.append((left, top + (bottom - top) * t))
    for i in range(rows):  # back up the right edge
        t = (rows - 1 - i) / (rows - 1)
        verts.append((right, top + (bottom - top) * t))
    return verts


def uv_for(part: Part, polygon: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Texture-space UVs. Godot's Polygon2D UVs are in PIXELS, not 0..1."""
    left, top, _right, _bottom = part_rect(part)
    return [(x - left, y - top) for x, y in polygon]


def weights_for(part: Part, polygon: list[tuple[float, float]]) -> list[tuple[str, list[float]]]:
    """(bone name, per-vertex weight) rows for a part's Polygon2D.

    Only the torso is multi-bone. Every other part rides one bone at weight 1,
    which is the honest shape: a cutout figure converted to meshes is mostly
    rigid quads with a few deforming pieces, and pretending otherwise would
    inflate the mesh approach's authoring cost in the wrong direction.
    """
    if part.name != "torso":
        return [(part.bone, [1.0] * len(polygon))]

    _left, top, _right, bottom = part_rect(part)
    span = bottom - top
    hip: list[float] = []
    spine: list[float] = []
    neck: list[float] = []
    for _x, y in polygon:
        t = (y - top) / span  # 0 at the top (head end), 1 at the bottom (hip end)
        neck_w = max(0.0, 1.0 - t * 2.0)
        hip_w = max(0.0, (t - 0.5) * 2.0)
        spine_w = max(0.0, 1.0 - abs(t - 0.5) * 2.0)
        total = neck_w + hip_w + spine_w
        neck.append(round(neck_w / total, 4))
        spine.append(round(spine_w / total, 4))
        hip.append(round(hip_w / total, 4))
    return [("hip", hip), ("spine", spine), ("neck", neck)]


def mesh_vertex_count() -> int:
    return sum(len(polygon_for(PART_BY_NAME[p.name])) for p in PART_BY_NAME.values())


def skeleton_bone_count() -> int:
    return len(BONES)

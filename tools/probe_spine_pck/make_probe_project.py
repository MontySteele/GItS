"""Build the Track M spine probe's scratch Godot project -- OUTSIDE the repo.

WHAT THIS IS FOR
    Track M asks whether a .tscn that references SpineSkeletonFileResource /
    SpineAtlasResource survives OUR pack build (MegaDot --headless --import
    then --export-pack) and loads in-game, given that the MegaDot editor has no
    spine importer at all (F1 §1d).

    The probe answers it with a base-game rig, copied read-only out of
    SlayTheSpire2.pck. THE COPY NEVER ENTERS THE REPO. --out must point
    somewhere outside it; cleanup_probe.ps1 deletes the tree afterwards.

WHAT IT WRITES  (all under --out)
    project.godot, export_presets.cfg      two presets: "strict" mirrors
                                           tools/build_pck.ps1 exactly
                                           (export_filter=all_resources,
                                           empty include_filter); "wide" adds
                                           an include_filter for the four
                                           spine extensions. The pair is the
                                           experiment: it separates "the
                                           exporter dropped the file" from
                                           "the engine could not resolve the
                                           type".
    spineprobe/rig.spskel  .spatlas        the imported shape Downfall 0.1.7
                                           ships (pck-verified)
    spineprobe/rig.skel    .atlas          the raw shape Downfall HEAD ships
    spineprobe/rig.png                     atlas page, decoded out of the
                                           base game's .ctex
    spineprobe/probe_imported.tscn         SpineSprite -> .spskel/.spatlas
    spineprobe/probe_raw.tscn              SpineSprite -> .skel/.atlas
    spineprobe/probe_control.tscn          Sprite2D only -- the control arm:
                                           if this is missing from the pack
                                           too, the failure was never spine's

The .spskel/.spatlas shapes are not guesses. Measured against the shipped
packs: an imported .spskel is the raw Spine binary byte-for-byte (the base
game's punch_construct.spskel opens with the Spine hash and the length-prefixed
version string "4.2.43"), and a .spatlas is a four-key JSON envelope around the
verbatim .atlas text -- atlas_data, source_path, normal_texture_prefix,
specular_texture_prefix.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pck_read import find, parse, read  # noqa: E402

DEFAULT_GAME_PCK = (
    r"C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.pck"
)
# punch_construct: 54 bones / 44 atlas regions, one 1307x207 page, 165 KB
# skeleton (F1 memo section 1b). Mid-sized, single-page, no skins -- the
# least exotic rig in the pack, which is what a probe wants.
DEFAULT_RIG = "punch_construct"

PROJECT_GODOT = """; Throwaway project for the Track M spine probe. Its only job is to import a
; PNG and export a pack, exactly as tools/build_pck.ps1's scratch project does.
config_version=5

[application]

config/name="SpineProbe"
"""

# preset.0 is byte-equivalent to the preset tools/build_pck.ps1 writes, so a
# difference between the two exports is a difference in the filter and nothing
# else.
EXPORT_PRESETS = """[preset.0]

name="strict"
platform="Windows Desktop"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="probe_strict.pck"
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.0.options]

binary_format/embed_pck=false

[preset.1]

name="wide"
platform="Windows Desktop"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter="*.skel,*.atlas,*.spskel,*.spatlas"
exclude_filter=""
export_path="probe_wide.pck"
patches=PackedStringArray()
encryption_include_filters=""
encryption_exclude_filters=""
seed=0
encrypt_pck=false
encrypt_directory=false
script_export_mode=2

[preset.1.options]

binary_format/embed_pck=false
"""

TSCN_SPINE = """[gd_scene load_steps=4 format=3]

[ext_resource type="SpineAtlasResource" path="res://spineprobe/{atlas}" id="1_atlas"]
[ext_resource type="SpineSkeletonFileResource" path="res://spineprobe/{skel}" id="2_skel"]

[sub_resource type="SpineSkeletonDataResource" id="SpineSkeletonDataResource_probe"]
atlas_res = ExtResource("1_atlas")
skeleton_file_res = ExtResource("2_skel")

[node name="Visuals" type="SpineSprite"]
skeleton_data_res = SubResource("SpineSkeletonDataResource_probe")
"""

TSCN_CONTROL = """[gd_scene load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://spineprobe/rig.png" id="1_tex"]

[node name="Visuals" type="Sprite2D"]
texture = ExtResource("1_tex")
"""


def decode_ctex(data: bytes) -> bytes:
    """Pull the atlas page out of a lossless CompressedTexture2D, as PNG bytes.

    The GST2 container stores the image as an embedded PNG or -- which is what
    the base game's monster pages actually are -- a lossless WebP RIFF. Both
    are handled; a VRAM-compressed page would not be, and reports as such.
    """
    if not data.startswith(b"GST2"):
        raise ValueError("not a .ctex (missing GST2 magic)")

    idx = data.find(b"\x89PNG\r\n\x1a\n")
    if idx >= 0:
        return data[idx:]

    idx = data.find(b"RIFF")
    if idx < 0:
        raise ValueError("no embedded PNG or WebP -- page is VRAM-compressed")
    riff_len = int.from_bytes(data[idx + 4: idx + 8], "little") + 8
    blob = data[idx: idx + riff_len]

    import io

    from PIL import Image  # repo venv dependency; the art pipeline's own

    buf = io.BytesIO()
    Image.open(io.BytesIO(blob)).save(buf, "PNG")
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="scratch project dir, OUTSIDE the repo")
    ap.add_argument("--game-pck", default=DEFAULT_GAME_PCK)
    ap.add_argument("--rig", default=DEFAULT_RIG)
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.commonpath([out, repo]) == repo:
        print(f"REFUSED: --out {out} is inside the repo {repo}.", file=sys.stderr)
        print("Base-game assets must never be written into a tracked tree.", file=sys.stderr)
        return 2

    f, hdr, entries = parse(args.game_pck)
    print(f"{args.game_pck}: format={hdr[0]} entries={len(entries)}")

    def one(suffix: str):
        hits = [e for e in find(entries, args.rig) if e.path.endswith(suffix)]
        if len(hits) != 1:
            raise SystemExit(f"expected exactly one {suffix} for {args.rig}, got {len(hits)}")
        return hits[0]

    skel = read(f, one(".spskel"))
    atlas_json = json.loads(read(f, one(".spatlas")).decode("utf-8"))
    ctex = read(f, one(".ctex"))

    rig_dir = os.path.join(out, "spineprobe")
    os.makedirs(rig_dir, exist_ok=True)

    # The raw pair, as Downfall HEAD ships it.
    with open(os.path.join(rig_dir, "rig.skel"), "wb") as fh:
        fh.write(skel)
    atlas_text = atlas_json["atlas_data"]
    # The page name inside the atlas text must match the file we write next to
    # it; the runtime's texture loader resolves it relative to the atlas.
    first_line = atlas_text.lstrip("\r\n").split("\n", 1)[0].strip()
    atlas_text = atlas_text.replace(first_line, "rig.png", 1)
    with open(os.path.join(rig_dir, "rig.atlas"), "w", encoding="utf-8", newline="") as fh:
        fh.write(atlas_text)

    # The imported pair, as Downfall 0.1.7 ships it: identical bytes, different
    # extension, plus the JSON envelope.
    with open(os.path.join(rig_dir, "rig.spskel"), "wb") as fh:
        fh.write(skel)
    with open(os.path.join(rig_dir, "rig.spatlas"), "w", encoding="utf-8", newline="") as fh:
        json.dump(
            {
                "atlas_data": atlas_text,
                "normal_texture_prefix": atlas_json.get("normal_texture_prefix", "n"),
                "source_path": "res://spineprobe/rig.atlas",
                "specular_texture_prefix": atlas_json.get("specular_texture_prefix", "s"),
            },
            fh,
        )

    with open(os.path.join(rig_dir, "rig.png"), "wb") as fh:
        fh.write(decode_ctex(ctex))

    with open(os.path.join(rig_dir, "probe_raw.tscn"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(TSCN_SPINE.format(atlas="rig.atlas", skel="rig.skel"))
    with open(os.path.join(rig_dir, "probe_imported.tscn"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(TSCN_SPINE.format(atlas="rig.spatlas", skel="rig.spskel"))
    with open(os.path.join(rig_dir, "probe_control.tscn"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(TSCN_CONTROL)

    with open(os.path.join(out, "project.godot"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(PROJECT_GODOT)
    with open(os.path.join(out, "export_presets.cfg"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(EXPORT_PRESETS)

    print(f"Probe project written to {out}")
    for name in sorted(os.listdir(rig_dir)):
        print(f"  spineprobe/{name}  {os.path.getsize(os.path.join(rig_dir, name))} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

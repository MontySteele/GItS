"""The co-op treasure-room hands: names, packing, and the ctex reader.

`tools/gen_multiplayer_hands.py` writes twelve Tier F recolours that the game
finds only by name: `CharacterModel.Arm<Pose>TexturePath` derives
`res://images/ui/hands/multiplayer_hand_<id.entry>_<pose>.png` and nothing
overrides it. So the things that can silently break are all spellings, each
invisible on its own:

  * the output names against the ids BaseLib gives our three characters;
  * the generator's outputs against art_lint's GENERATOR_OWNED claims;
  * build_pck.ps1's copy block landing the files at the ENGINE path;
  * KleeAssetPathFallback no longer sending Klee's arms to the Ironclad's.

The pixels themselves need the installed game pck and are checked by
`gen_multiplayer_hands.py --check` on the art-bearing checkout.
"""

from __future__ import annotations

import io
import re
import struct
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import art_lint  # noqa: E402
import gen_multiplayer_hands as hands  # noqa: E402

CHARACTERS = ("klee", "furina", "kokomi")
BUILD_PCK = ROOT / "tools" / "build_pck.ps1"
FALLBACK_CS = ROOT / "klee-mod" / "KleeCode" / "KleeAssetPathFallback.cs"


def test_outputs_are_the_engine_derived_names_for_all_three():
    want = {f"multiplayer_hand_kleemod-{c}_{p}.png"
            for c in CHARACTERS for p in hands.POSES}
    assert set(hands.OUTPUTS) == want


def test_each_character_class_exists_so_its_id_entry_is_kleemod_name():
    # BaseLib's id is "<MODPREFIX>-" + the class name upper-cased; the lower-
    # cased entry is what the output names above embed.
    for c in CHARACTERS:
        cs = ROOT / "klee-mod" / "KleeCode" / f"{c.capitalize()}.cs"
        text = cs.read_text(encoding="utf-8")
        assert re.search(rf"class {c.capitalize()}\s*:\s*CustomCharacterModel",
                         text), cs


def test_generator_owned_claims_exactly_the_generators_outputs():
    claimed = {out for out, gen in art_lint.GENERATOR_OWNED.items()
               if gen == "gen_multiplayer_hands.py"}
    assert claimed == {f"{hands.OUT_DIR}/{n}" for n in hands.OUTPUTS}


def test_build_pck_copies_the_hands_to_the_engine_path():
    text = BUILD_PCK.read_text(encoding="ascii")
    src_dir = hands.OUT_DIR.split("ImageGen/images/", 1)[1]
    assert f"$handsSrc = Join-Path $src '{src_dir}'" in text
    assert "Join-Path $work 'images\\ui\\hands'" in text


def test_klee_arms_are_no_longer_redirected_to_the_ironclad():
    text = FALLBACK_CS.read_text(encoding="utf-8")
    listed = re.search(r"PathProperties\s*=\s*\{(.*?)\};", text, re.S).group(1)
    assert "Arm" not in re.sub(r"//.*", "", listed)


def _png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _webp_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "WEBP", lossless=True)
    return buf.getvalue()


@pytest.mark.parametrize("encode", [_png_bytes, _webp_bytes])
def test_ctex_payload_is_found_by_signature(encode):
    img = Image.new("RGBA", (6, 4), (200, 40, 10, 128))
    header = b"GST2" + struct.pack("<7I", 1, 6, 4, 0, 0, 2, 5) + b"\0" * 16
    got = hands._decode_ctex(header + encode(img) + b"trailing")
    assert got.convert("RGBA").tobytes() == img.tobytes()


def test_ctex_rejects_a_non_gst2_blob():
    with pytest.raises(ValueError):
        hands._decode_ctex(b"NOPE" + b"\0" * 32)


def test_check_skips_cleanly_without_a_game_pack(tmp_path, capsys):
    rc = hands.main(["--check", "--art-root", str(tmp_path),
                     "--game-dir", str(tmp_path / "no-game")])
    assert rc == 0
    assert "SKIPPED" in capsys.readouterr().out

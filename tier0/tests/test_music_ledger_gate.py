r"""The music half of the media pipeline: the ledger is the gate, not the tree.

`docs/current/operations/media.md` sec.1 makes `media/out/` gitignored and
`media/MUSIC.tsv` the one tracked thing about a track, so the ledger carries
every track's title, origin and licence and the pre-public copyright pass is
`grep PLACEHOLDER-COPYRIGHTED media/*.tsv`. sec.4 step 2 turns that into a
packaging rule: **a file under `media/out/` with no ledger row is never
copied.**

That rule cannot be tested by running the packager here. `tools/build_pck.ps1`
needs the MegaDot editor and the gitignored art tree, and PS 5.1 semantics
cannot be executed from pytest at all -- the same wall
`test_repo_python_convention.py` and `test_act_placeholder_plan.py` already
stand behind. So the block is pinned as SOURCE TEXT, and what is pinned is
chosen to be the things whose absence is silent:

  * that the gate reads the LEDGER (a tree-first block would ship an unledgered
    drop with no provenance into a pack that may one day be public);
  * that a row with no file on disk is a `Note-Skip` and not a throw (art never
    blocks a build);
  * that a broken ledger IS a throw (an absent asset and a broken tracked file
    are different things, and skipping the second ships silence);
  * that the loop point comes out of the ledger column and into the `.import`,
    which is the only place Godot will read it.

The ledger FILE is checked for real, because it is tracked: its header, its
encoding, and -- for whatever rows exist on a given machine -- the invariants
sec.1 and sec.2 state.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_PCK = ROOT / "tools" / "build_pck.ps1"
LEDGER = ROOT / "media" / "MUSIC.tsv"

# media.md sec.2's columns, in order.
COLUMNS = ["out", "raw", "scene", "title", "origin", "licence", "loop_start_s", "notes"]

# media.md sec.1's SLOT vocabulary (EB-814), and it is closed: six faces
# (R273's layout 1, two per act) crossed with four face slots, plus three
# global ones -- twenty-seven scenes. The face names are exactly what
# `TeyvatFrame.MediaScene` derives and the slot names are exactly
# `TeyvatMusic`'s own constants; see the three-way cross-file pin below, which
# is what stops any of them drifting.
FACES = [
    "act1_mondstadt",
    "act1_liyue",
    "act2_natlan",
    "act2_inazuma",
    "act3_fontaine",
    "act3_sumeru",
]
FACE_SLOTS = ["combat", "elite", "boss", "map"]
GLOBAL_SLOTS = ["menu", "shop", "rest"]
ACT_SCENES = [f"{face}/{slot}" for face in FACES for slot in FACE_SLOTS]
SCENES = ACT_SCENES + GLOBAL_SLOTS

TEYVAT_FRAME = ROOT / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatFrame.cs"
TEYVAT_MUSIC = ROOT / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatMusic.cs"
MEDIA_MD = ROOT / "docs" / "current" / "operations" / "media.md"

# media.md sec.3: OGG Vorbis is the default, MP3 is accepted, WAV never.
EXTENSIONS = (".ogg", ".mp3")


def music_block() -> str:
    r"""The music section of `tools/build_pck.ps1`, sliced out rather than
    grepped for.

    Every assertion below is about what the MUSIC block does; the same words
    sitting in a PNG block next door would mean something else entirely, and a
    grep over the whole 1,100-line script would pass on them.
    """
    script = BUILD_PCK.read_text(encoding="utf-8")
    start = script.index("# THE MEDIA LEDGER'S MUSIC")
    end = script.index("# Animation sprint 1 (Track B)", start)
    return script[start:end]


def music_code() -> str:
    """The same block with its comment lines dropped.

    The block explains itself at length and names the PNG machinery it is
    deliberately NOT reusing, so a negative assertion ("this block never
    enumerates a directory") has to be made against the code and not against
    the prose about the code.
    """
    return "\n".join(
        line for line in music_block().splitlines() if not line.lstrip().startswith("#")
    )


def test_the_ledger_is_read_and_the_tree_is_not_enumerated():
    """sec.4 step 2, and the one assertion the whole provenance story rests on.

    A block that walked `media/out/` would pack a hand-dropped track that has no
    row, no title, no origin and no licence -- invisible to the copyright pass
    by construction. So: the ledger path is read, and no directory listing of
    `media\\out` appears anywhere in the block.
    """
    code = music_code()
    assert r"Join-Path $repo 'media\MUSIC.tsv'" in code
    assert "ReadAllLines($musicLedger" in code
    assert "Get-ChildItem" not in code
    assert "Select-PackablePngs" not in code


def test_a_row_with_no_file_is_a_skip_and_not_a_failure():
    """sec.4 step 2's second half: art never blocks a build.

    Paired with the negative, because `Note-Skip` sitting in the block proves
    nothing on its own if the missing-file path also throws.
    """
    block = music_code()
    assert 'Note-Skip "media\\out\\$outRel" $from; continue' in block


def test_a_broken_ledger_throws_on_each_of_its_four_shapes():
    """The other side of the same switch.

    A duplicate `out` (sec.1: one producer per out-path), an unknown scene, a
    WAV (sec.3), and an unparseable `loop_start_s` are errors in a TRACKED file
    -- always fixable, never an absent asset. Skipping one would deploy a run
    with no music and every gate green, which is the failure this file exists to
    make impossible.
    """
    block = music_code()
    throws = [line for line in block.splitlines() if "throw " in line]
    assert len(throws) >= 5
    joined = "\n".join(throws)
    assert "one producer per out-path" in joined
    assert "sec.1 lists" in joined
    assert "never WAV" in joined
    assert "is not a number" in joined


def test_the_scene_vocabulary_and_the_two_formats_are_the_documented_ones():
    """sec.1's twenty-seven scenes and sec.3's two formats, named in the script.

    A twenty-eighth scene costs a word here, exactly as a seventh act dressing
    costs one in `test_act_placeholder_plan.py`.
    """
    block = music_code()
    assert len(SCENES) == 27
    for scene in SCENES:
        assert f"'{scene}'" in block, scene
    assert "$ext -ne '.ogg' -and $ext -ne '.mp3'" in block


def test_the_destination_is_the_frames_own_namespace():
    """`res://teyvat/music/<scene>/`, which is `TeyvatMusic.Root` plus the
    ledger's own `scene` column. Not `res://klee/`: the frame's media is not one
    character's.

    A face scene is nested one level (`act1_liyue/boss`), so the destination
    takes the column with its separator normalised for Windows and its NAME
    untouched -- see the verbatim pin below.
    """
    block = music_code()
    assert 'Join-Path $work "teyvat\\music\\$sceneDir"' in block
    assert "$sceneDir = $scene.Replace('/', '\\')" in block

    reader = TEYVAT_MUSIC.read_text(encoding="utf-8")
    assert 'public const string Root = "res://teyvat/music/";' in reader


def test_the_slot_vocabulary_agrees_across_all_three_files():
    r"""EB-814's three-way pin, and the reason it is one test rather than three.

    A slot name lives in three places that cannot see each other: the packager's
    ``$musicScenes`` whitelist (which THROWS on anything outside it), `media.md`
    §1 (which is what a human files a track against), and `TeyvatMusic`'s own
    `Slot*` constants (which are what the resolver actually asks `DirAccess`
    for). Any two of them agreeing is not enough: a slot missing from the
    whitelist is a build that throws on a by-the-book ledger row; a slot missing
    from the constants is a directory that is packed and never asked for --
    exactly the failure `EB-814` existed to close; a slot missing from the page
    is a grammar nobody can file against.
    """
    code = music_code()
    music = TEYVAT_MUSIC.read_text(encoding="utf-8")
    page = MEDIA_MD.read_text(encoding="utf-8")

    # The constants ARE the slot names, spelled once each.
    for slot in FACE_SLOTS + GLOBAL_SLOTS:
        assert f'Slot{slot.capitalize()} = "{slot}";' in music, slot

    # And the two arrays that group them are the two shapes of the grammar.
    assert ("FaceSlots = { SlotCombat, SlotElite, SlotBoss, SlotMap };") in music
    assert ("GlobalSlots = { SlotMenu, SlotShop, SlotRest };") in music

    # The page names every one of them, and the whitelist is checked above.
    for slot in FACE_SLOTS:
        assert f"`{slot}`" in page, slot
    for scene in SCENES:
        assert f"'{scene}'" in code, scene


def test_the_reader_resolves_to_the_ledgers_names_and_the_packager_does_not():
    r"""The decision this file exists to keep: **the ledger's names are the
    spec and the READER moves.**

    A track filed exactly per media.md §1 under `act1_mondstadt` has to be the
    one the reader asks for. Two ways that can break silently, and both are
    pinned here:

      * the packager grows a rename, so the ledger stops describing the pack;
      * the reader goes back to `actEntry.ToLowerInvariant()`, so a
        by-the-book track lands where nothing looks.

    The six face names themselves are checked as a CROSS-FILE agreement:
    `TeyvatFrame.MediaScene` builds them as `act{act}_{entry.ToLowerInvariant()}`
    from the arm's one dressing registry, so the names never appear as literals
    on the C# side and cannot be grepped for. What can be checked is that every
    scene this packager accepts is one the six faces and seven slots account
    for, and that every one of them now HAS a resolver -- the note EB-814
    closed.
    """
    code = music_code()
    frame = TEYVAT_FRAME.read_text(encoding="utf-8")
    music = TEYVAT_MUSIC.read_text(encoding="utf-8")

    # The packager copies `scene` through: it is the destination leaf, and the
    # only thing done to it anywhere in the block is the separator swap.
    assert "$sceneDir = $scene.Replace('/', '\\')" in code
    assert "$scene =" not in code.replace("$scene  = $cols[2].Trim()", "")

    # The reader resolves, and the old spelling is gone.
    assert "TeyvatFrame.MediaScene(actEntry, slot)" in music
    assert "actEntry.ToLowerInvariant()" not in music
    assert 'var face = $"act{act}_{entry.ToLowerInvariant()}";' in frame
    # The nested scene is the face, a slash, and the slot -- built here and
    # nowhere else, so the packager never has to know the shape.
    assert 'face + "/" + slot' in frame

    # The act number is derived from the base zone, so there is no parallel
    # dressing-to-act table to drift: the arm's one registry stays AssetAlias.
    assert "AssetAlias.TryGetValue(entry, out var zone)" in frame
    assert "BaseZoneAct.TryGetValue(zone, out var act)" in frame

    # Every face the packager accepts is a dressing constant on the C# side.
    for face in FACES:
        act, nation = face.split("_", 1)
        assert act in {"act1", "act2", "act3"}, face
        assert f'public const string {nation.capitalize()} = "{nation.upper()}";' in frame

    # EB-814: every scene has a caller now. The room slots reach `DirAccess`
    # through `SlotFor`, which is the room table media.md §1 documents, and the
    # global three short-circuit the dressing in `MediaScene`.
    assert "public static string SlotFor(RoomType? room)" in music
    assert "if (TeyvatMusic.IsGlobalSlot(slot))" in frame
    for room, slot in (("Boss", "SlotBoss"), ("Elite", "SlotElite"),
                       ("Monster", "SlotCombat"), ("Shop", "SlotShop"),
                       ("RestSite", "SlotRest")):
        assert f"RoomType.{room} => {slot}," in music, room
    assert "_ => SlotMap," in music


def test_the_loop_point_travels_from_the_column_into_the_import_file():
    """sec.3: the loop convention is one ledger column and never a filename
    suffix, so the packager writes Godot's own importer keys.

    Both importers are named, because an `.mp3` row given the Vorbis importer
    would reimport as the wrong type and the loop would be the least of it. The
    invariant-culture formatting is pinned too: on a comma-decimal locale
    `loop_offset=12,4` parses as 12 and the track loops a minute early with
    nothing in any log to say why.
    """
    block = music_code()
    assert "loop=true" in block
    assert "loop_offset=$offset" in block
    assert "importer = 'oggvorbisstr'; $type = 'AudioStreamOggVorbis'" in block
    assert "importer = 'mp3'; $type = 'AudioStreamMP3'" in block
    assert block.count("[Globalization.CultureInfo]::InvariantCulture") == 2
    # An EMPTY loop_start_s writes no .import at all (sec.2: blank means no
    # loop edit), so the importer's own defaults stand.
    assert "if ($loopAt) { Write-AudioImport" in block


def test_the_ledger_is_tracked_utf8_with_the_documented_header():
    r"""sec.1's encoding rule, and its line endings are NOT sec.1's to choose.

    `.gitattributes` is `* text=auto eol=lf` repo-wide, so a ledger hand-written
    with CRLF is normalised into the index and checked back out as LF -- exactly
    what `art/plan.tsv` and `art/SOURCES.tsv` measure as today
    (`git ls-files --eol`). An assertion that this file holds CRLF would pass on
    the machine that wrote it and fail on the next checkout, which is the
    opposite of a pin. So: UTF-8, no BOM, no stray `\r` riding into the last
    column, and the documented header.

    TSV and not CSV is not taste either: `.gitignore` ignores `*.csv` repo-wide,
    so a `.csv` ledger would be untracked and the provenance record would not
    exist.
    """
    assert LEDGER.exists(), "media/MUSIC.tsv is the tracked half of the pipeline"
    raw = LEDGER.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "no BOM"
    text = raw.decode("utf-8")  # raises if it is not UTF-8
    assert "\r" not in text, ".gitattributes normalises this file to LF"
    assert text.split("\n", 1)[0].split("\t") == COLUMNS


def test_every_ledger_row_obeys_the_ledgers_own_rules():
    """Empty on today's tree -- no track has been placed -- and that is the
    point: the first row [USER] writes is checked by this, not by a build."""
    with LEDGER.open(encoding="utf-8", newline="") as fh:
        lines = [line.rstrip("\r\n") for line in fh]
    rows = [line.split("\t") for line in lines[1:] if line.strip()]

    seen: set[str] = set()
    for row in rows:
        assert len(row) == len(COLUMNS), row
        out, _raw, scene, _title, _origin, licence, loop_start_s, _notes = row
        assert out not in seen, f"one producer per out-path: {out}"
        seen.add(out)
        assert out.startswith("music/"), out
        assert out.lower().endswith(EXTENSIONS), out
        assert scene in SCENES, scene
        assert licence, "sec.2: licence defaults to PLACEHOLDER-COPYRIGHTED, never blank"
        if loop_start_s:
            assert float(loop_start_s) >= 0.0, loop_start_s

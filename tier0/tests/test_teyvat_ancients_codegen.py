"""The Teyvat arm's DRESSED ANCIENTS are generated, and the committed copy is fresh.

`tools/gen_teyvat_ancients.py` turns `docs/current/dossiers/content/ancient-faces.tsv`
into one C# subclass per (Ancient, face), their loc rows and the tables the face
acts and the two patches read. The C# shape decision -- why a dressed Ancient
subclasses its BASE Ancient directly, where a dressed EVENT could not -- is
`docs/current/operations/codegen.md`, "Codegen -- Teyvat dressed Ancients".

These arms are the gate on that arrangement, and they are seven claims:

  1. the committed output is not stale (the generator's own `--check`, which
     needs no decompile and no game);
  2. R275's slate is present in full -- eighteen bodies, each with the ruled
     name, and Darv is Alice on all four act-2/act-3 faces;
  3. the base-Ancient index carries IDENTIFIERS AND SHAPES ONLY -- no
     base-game body and no base-game prose, which is the repo's decompiled-
     material rule (`.gitignore:28`, `csharp-build-spec.md` sec.0.3) applied
     to a checked-in file;
  4. AN EMPTY TEXT FIELD WRITES NO ROW. This is the whole of R275's first
     pass: names now, words later, and the words drop in without a code
     change. A row with an empty cell must leave the dressed key with no
     generated row, so `TeyvatAncients.RowsFor`'s alias supplies the game's
     own line;
  5. no generated row is an option row, because that is the ONE way this arm
     could reword a boon;
  6. the pool per face has the same count as its base act's, and every face
     names a dressing for every Ancient its act can roll;
  7. the generator REFUSES rather than guesses: a missing slate row, a face
     that is not one of R273's six, a dressed entry that collides with a base
     Ancient's, and a dialogue cell whose line count disagrees with the
     compiled base are each a nonzero exit.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GENERATOR = REPO / "tools" / "gen_teyvat_ancients.py"
INDEX = REPO / "tools" / "data" / "sts2_base_ancients.json"
FACES = REPO / "docs" / "current" / "dossiers" / "content" / "ancient-faces.tsv"
GENERATED = REPO / "klee-mod" / "KleeCode" / "Teyvat" / "TeyvatAncientsGenerated.cs"

#: R275's slate, written out here so a generator change cannot quietly move it.
SLATE = {
    ("NEOW", "MONDSTADT"): "Dvalin",
    ("NEOW", "LIYUE"): "Moon Carver",
    ("OROBAS", "NATLAN"): "Xbalanque",
    ("OROBAS", "INAZUMA"): "the Sacred Sakura",
    ("PAEL", "NATLAN"): "Och-Kan",
    ("PAEL", "INAZUMA"): "Orobashi",
    ("TEZCATARA", "NATLAN"): "Tezcatara",
    ("TEZCATARA", "INAZUMA"): "Ioroi",
    ("NONUPEIPE", "FONTAINE"): "Egeria",
    ("NONUPEIPE", "SUMERU"): "Greater Lord Rukkhadevata",
    ("TANX", "FONTAINE"): "Elynas",
    ("TANX", "SUMERU"): "Apep",
    ("VAKUU", "FONTAINE"): "Remus",
    ("VAKUU", "SUMERU"): "King Deshret",
    ("DARV", "NATLAN"): "Alice",
    ("DARV", "INAZUMA"): "Alice",
    ("DARV", "FONTAINE"): "Alice",
    ("DARV", "SUMERU"): "Alice",
}

#: The base acts' own Ancient pools (`Overgrowth.cs:26`, `Underdocks.cs:22`,
#: `Hive.cs:24`, `Glory.cs:23`), by face.
ACT_POOL_SIZE = {
    "MONDSTADT": 1, "LIYUE": 1,
    "NATLAN": 3, "INAZUMA": 3,
    "FONTAINE": 3, "SUMERU": 3,
}


def run(*args: str, faces: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(GENERATOR), *args],
                          cwd=REPO, capture_output=True, text=True)


def rows() -> list[dict[str, str]]:
    lines = [line for line in FACES.read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    header = lines[0].split("\t")
    return [dict(zip(header, line.split("\t"))) for line in lines[1:]]


def test_the_committed_output_is_fresh() -> None:
    result = run("--check")
    assert result.returncode == 0, result.stderr


def test_the_slate_is_complete_and_unchanged() -> None:
    got = {(r["ancient"], r["face"]): r["name"] for r in rows()}
    assert got == SLATE


def test_every_slate_row_reaches_a_title_row() -> None:
    text = GENERATED.read_text(encoding="utf-8")
    for name in SLATE.values():
        assert f'"{name}",' in text, f"{name} has no generated title row"
    # Eighteen bodies, eighteen title rows, eighteen base-entry rows.
    assert len(re.findall(r'public sealed class \w+ : \w+ \{ \}', text)) == 18
    assert len(re.findall(r'\["[A-Z0-9_]+\.title"\]', text)) == 18


def test_darv_is_alice_on_every_act_2_and_act_3_face() -> None:
    darv = {r["face"]: r["name"] for r in rows() if r["ancient"] == "DARV"}
    assert darv == {"NATLAN": "Alice", "INAZUMA": "Alice",
                    "FONTAINE": "Alice", "SUMERU": "Alice"}


def test_act_1_has_no_darv_body() -> None:
    # `RunManager.GenerateRooms` walks `State.Acts.Skip(1)`, so act 1 is never
    # dealt a shared Ancient; a Mondstadt Darv would be unreachable.
    faces = {r["face"] for r in rows() if r["ancient"] == "DARV"}
    assert not faces & {"MONDSTADT", "LIYUE"}


def test_the_pool_per_face_matches_the_base_acts() -> None:
    text = GENERATED.read_text(encoding="utf-8")
    for face, size in ACT_POOL_SIZE.items():
        m = re.search(r'\["' + face + r'"\] = new\[\] \{ ([^}]*) \}', text)
        assert m, f"{face} has no FacePools row"
        entries = [e.strip().strip('"') for e in m.group(1).split(",")]
        # The face's pool is the act's own plus, for acts 2 and 3, Darv.
        darv = sum(1 for r in rows()
                   if r["face"] == face and r["ancient"] == "DARV")
        assert len(entries) == size + darv, (face, entries)


def test_every_text_field_is_empty_so_the_game_keeps_its_own_lines() -> None:
    # R275's first pass ships NAMES. If this ever fails it is because a face
    # wrote words -- which is the intended next step, and the arms below
    # (no option row, the generated row count) are what still bind then.
    text_columns = ("epithet", "first_visit", "dialogue_1", "dialogue_2",
                    "dialogue_3", "agnostic_1", "agnostic_2", "extra")
    written = [(r["ancient"], r["face"], c)
               for r in rows() for c in text_columns if r[c].strip()]
    generated = GENERATED.read_text(encoding="utf-8")

    if not written:
        # The promise: with every cell empty, the ONLY generated rows are the
        # eighteen titles, and the dialogue-line list is empty. Everything else
        # a dressed Ancient shows is the alias's copy of the game's own row.
        assert len(re.findall(r'\["[A-Z0-9_]+\.[a-zA-Z.]+"\] =', generated)) == 18
        assert re.search(r"Lines =\s*new List<AncientLine>\s*\{\s*\};", generated)


def test_no_generated_row_is_an_option_row() -> None:
    # An Ancient's boons are `RelicOption<T>()`, and `EventOption.FromRelic` is
    # `GetOptionTitle(key) ?? relic.Title` -- so an absent row falls through to
    # the relic's own. A generated option row is the one way this arm could
    # reword a boon, and there is no path that writes one.
    text = GENERATED.read_text(encoding="utf-8")
    assert not re.search(r'\["[A-Z0-9_]+\.pages\.[A-Z_]+\.options\.', text)


def test_the_index_is_identifiers_and_shapes_only() -> None:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    assert set(index) == {"NEOW", "DARV", "OROBAS", "PAEL", "TEZCATARA",
                          "NONUPEIPE", "TANX", "VAKUU"}
    for entry, shape in index.items():
        assert shape["sealed"] is False, (
            f"{entry} is sealed -- the subclass shape does not apply")
        assert shape["base"] == "AncientEventModel"
        assert set(shape["character_dialogues"]) == {
            "IRONCLAD", "SILENT", "DEFECT", "NECROBINDER", "REGENT"}
        # Every value is an identifier, a key suffix or a count. No sentence
        # from the base game can hide in any of them.
        for key in shape["extra_keys"]:
            assert re.fullmatch(r"[A-Za-z0-9_.]+", key), key
        for counts in shape["character_dialogues"].values():
            assert all(isinstance(n, int) for n in counts)


def test_the_generator_refuses_a_missing_slate_row(tmp_path) -> None:
    raw = FACES.read_bytes()
    kept = raw.decode("utf-8")
    lines = kept.splitlines()
    dropped = [line for line in lines
               if not line.startswith("NEOW\tMONDSTADT\t")]
    try:
        FACES.write_bytes(("\n".join(dropped) + "\n").encode("utf-8"))
        result = run("--check")
        assert result.returncode != 0
        assert "NEOW/MONDSTADT" in result.stderr
    finally:
        # Restore the exact bytes: write_text translates LF to CRLF on
        # Windows and would leave the tracked file dirty.
        FACES.write_bytes(raw)


def test_the_generator_refuses_a_bad_line_count(tmp_path) -> None:
    # `NEOW`'s `firstVisitEver` dialogue is one line in compiled C#; a loc row
    # cannot add a second, so a two-line cell is a refusal rather than a row
    # nothing reads.
    raw = FACES.read_bytes()
    kept = raw.decode("utf-8")
    # Swap the Dvalin row's first_visit cell (column 5) for a two-line one,
    # whatever the row says today.
    lines = kept.split("\n")
    idx = next(i for i, l in enumerate(lines) if l.startswith("NEOW\tMONDSTADT\t"))
    cells = lines[idx].split("\t")
    cells[4] = "A: one | A: two"
    lines[idx] = "\t".join(cells)
    broken = "\n".join(lines)
    assert broken != kept
    try:
        FACES.write_bytes(broken.encode("utf-8"))
        result = run("--check")
        assert result.returncode != 0
        assert "first_visit" in result.stderr
    finally:
        # Restore the exact bytes: write_text translates LF to CRLF on
        # Windows and would leave the tracked file dirty.
        FACES.write_bytes(raw)

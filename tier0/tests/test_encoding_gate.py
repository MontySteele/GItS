"""The text-encoding gate as a red test ([USER] ratified 2026-07-27).

Every text read/write must declare `encoding=`. The rule and its reasoning
live in tools/lint_text_encoding.py; the short version is that an omitted
encoding resolves to the LOCALE codepage, so the defect appears on Windows
(cp1252) and is invisible on Linux CI (UTF-8). The gate has to be structural
for exactly that reason -- a behavioural check passes on the machine running
it and says nothing about the machine that breaks.

Found the hard way: `loader.py` carried five bare `read_text()` calls, which
decoded `Salon Debut`'s accented `e` to mojibake in memory. The card gallery
rendered it, and re-running the C# codegen on Windows would have shipped it
into the mod's Localization strings. Nothing reached a commit, and no test
could have caught it -- there was no gate, and CI runs the platform that
works.

The content path (tier0/content/, tier05/ pool loaders, both CSV writers) was
fixed at ratification. What remains is curated below as DEBT, not as a pass:
tools and tests that read .cs/.tsv/.ps1 fixtures, where the same class is
live but the blast radius is one script rather than every consumer of the
card index.
"""
from tools import lint_text_encoding as lint

# Undeclared text read/write calls per file at ratification. Counts, not line
# numbers, so ordinary edits above an offence do not churn this list -- but a
# NEW offence in an already-listed file still trips the gate, because it
# pushes the count above the recorded one.
#
# An entry here is DEBT. Work it off by adding `encoding="utf-8"` and lowering
# the number; the staleness test below forces that edit, so this list can only
# shrink.
DEBT: dict[str, int] = {
    "tier0/tests/test_extract_base_game_pool.py": 11,
    "tier0/tests/test_ironclad_upgrades.py": 1,
    "tier0/tests/test_measurement_world_digest.py": 8,
    "tier0/tests/test_real_ironclad.py": 1,
    "tier0/tests/test_real_silent.py": 1,
    "tier0/tests/test_roster_runtime_contracts.py": 10,
    "tier0/tests/test_upgrades.py": 1,
    "tools/archive/autocrop_card_art.py": 1,
    "tools/art_lint.py": 2,
    "tools/art_process.py": 8,
    "tools/build_official_sheet.py": 10,
    "tools/cut_combat_layers.py": 3,
    "tools/cut_salon_members.py": 2,
    "tools/extract_base_game_pool.py": 7,
    "tools/gen_furina_stills.py": 2,
    "tools/gen_kokomi_stills.py": 2,
    "tools/lint_furina_registers.py": 1,
    "tools/lint_kokomi_decksize.py": 1,
    "tools/lint_unique_names.py": 1,
}


def test_no_new_undeclared_encodings():
    live = {rel: len(hits) for rel, hits in lint.scan().items()}
    new = []
    for rel, count in sorted(live.items()):
        allowed = DEBT.get(rel, 0)
        if count > allowed:
            detail = ", ".join(f"line {ln} {what}"
                               for ln, what in lint.scan()[rel])
            new.append(f"{rel}: {count} undeclared (allowed {allowed}) "
                       f"-- {detail}")
    assert not new, (
        "text read/write without encoding= (gate RATIFIED 2026-07-27; "
        "an omitted encoding is cp1252 on Windows and UTF-8 on CI, so this "
        "cannot be caught by running the code): " + "; ".join(new))


def test_debt_list_is_not_stale():
    """A file that has been fixed must leave the list, or its entry rots into
    cover for the next real offence in that same file."""
    live = {rel: len(hits) for rel, hits in lint.scan().items()}
    stale = {rel: (recorded, live.get(rel, 0))
             for rel, recorded in DEBT.items()
             if live.get(rel, 0) < recorded}
    assert not stale, (
        "these improved -- lower the DEBT count (recorded, actual): "
        f"{stale}")


def test_the_content_path_carries_no_debt():
    """The loaders are the reason the gate exists: a mojibake card name there
    reaches the sheet, the sim, the gallery and the generated C# at once. They
    are never allowed onto the debt list, however small the entry looks."""
    protected = ("tier0/content/", "tier0/engine/", "tier05/")
    listed = [rel for rel in DEBT if rel.startswith(protected)]
    assert not listed, f"the content path may not carry encoding debt: {listed}"

    live = [rel for rel in lint.scan() if rel.startswith(protected)]
    assert not live, f"undeclared encoding on the content path: {live}"

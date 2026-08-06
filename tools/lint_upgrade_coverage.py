"""G-C1: every draftable card can be upgraded, in the sim AND in the game.

A card with no upgrade is a dead campfire choice. The player pays a rest, picks
the card, and gets nothing -- and nothing in the build complains, because
"absent" is not an error anywhere. It shipped, and it was found by a playtester
rather than by us.

THREE LAYERS, each one added because the layer before it reported all-clear on
a defect that had already shipped.

  LAYER 1 -- SHEET. Every draftable card has a delta in some *-upgrades.yaml,
  and that delta is applicable (non-empty, not `_unexpressible`, not in
  upgrades.UNAPPLIABLE). This is the check the sprint doc asked for.

  LAYER 2 -- CODEGEN. Every generated C# card actually emits an upgrade. A
  card can have a perfectly good sheet delta that the generator cannot
  express, in which case OnUpgrade() is an empty method with a comment in it
  and the LIVE card is unupgradable while the SIM's is fine. That is exactly
  `nicole_celestial_gift`, the card the 2026-07-25 playtest named: it has
  `{block_per_turn: +2}` in klee-upgrades.yaml, so layer 1 passes it, and its
  generated OnUpgrade does nothing at all.

  LAYER 3 -- THE EMITTED C#. Layer 2 asks the manifest and believes it. The
  manifest is written by the generator, so layer 2 believes the generator's
  own account of what the generator did -- and one shipped bug is what that
  costs: a generator that drops a delta, emits an empty OnUpgrade whose
  comment says "Flagged in manifest", and never flags the manifest. Layer 3
  reads the shipped .cs instead and needs nothing to be true about the
  manifest for its finding to fire.

Layer 2 is why this is a lint and not a spot-fix, and why the two layers get
separate exemption lists: "we have not authored a delta yet" and "the delta
exists but the generator cannot say it" are different debts with different
fixes, and collapsing them hides the second behind the first.

CURATION, not suppression. Every exemption carries a reason and, where it is a
debt rather than a rule, the gate that clears it. The house pattern: when a
defect is structurally invisible, give it a ledger and a lint.

Usage: python tools/lint_upgrade_coverage.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tier0.content import loader, upgrades          # noqa: E402
from tools.gen_klee_cards import pascal             # noqa: E402

# --- Layer 1 exemptions: cards that legitimately have no sheet delta. --------
#
# Entries are normally a RULE, not a debt: the card is not a campfire choice at
# all, so "no upgrade" is correct rather than missing.
#
# ONE entry is a curated DEBT rather than a rule, and it says so in its own
# reason string with the gate that removes it. It is carried here rather than in
# a fourth list because the L1 check is the check it suppresses; splitting the
# register would put one card's gate two lists away from the assertion it
# silences.
SHEET_EXEMPT: dict[str, str] = {
    # CURATED EXEMPTION -- [USER] reply of 2026-08-06 to the Second Wind open
    # one-liner (2) (`docs/archive/surplus-week-manifest-2026-08-05.md`, "Open
    # one-liners this batch generated for [USER]"): *"curated exemption now;
    # the replacement delta is deferred behind FLAG-2."*
    #
    # DEBT, not a rule. R110's S-1 erratum (X3) made Encore Performance a
    # 0-cost card, which empties its upgrade: `copy_cost_override: 0` was the
    # delta's only content and a 0-cost card cannot be discounted to 0. The
    # card IS a draftable campfire pick and SHOULD gain an upgrade; it does not
    # have one that means anything, and this entry is the register saying so
    # out loud rather than the lint quietly passing a hollow delta.
    #
    # LOAD-BEARING as of 2026-08-06. It was pre-positioned when it was written;
    # [USER]'s Y-4 reply ("YES") then deleted `copy_cost_override: 0` from
    # `docs/furina-upgrades.yaml`, and this entry is now the only thing holding
    # Layer 1 green for this card. Verified in both directions at landing:
    # disable the entry and L1 reports `encore_performance` at once.
    #
    # REMOVAL CONDITION: when FLAG-2 (X3's two adjacent closures) is ruled, a
    # replacement upgrade delta is authored for `encore_performance` and THIS
    # ENTRY IS DELETED with it. FLAG-2 is HELD; nothing may be built against it,
    # which is exactly why the delta is deferred and the exemption is carried.
    "encore_performance":
        "DEBT -- upgrade emptied by R110/S-1 (X3): `copy_cost_override: 0` is "
        "meaningless on a card that now costs 0. Curated exemption per [USER] "
        "2026-08-06; replacement delta deferred behind FLAG-2. Gate: FLAG-2 "
        "ruled -> author the delta -> delete this entry.",
}

# Whole classes are exempted by predicate rather than by listing every id --
# a list would have to be edited every time a card is added, which is the
# failure mode that produces a stale lint nobody trusts.
#
#   kit cards      -- Bursts arrive by charging the meter, never by drafting,
#                     and never sit in a deck to be upgraded.
#   guest stars    -- generated by their generator card, which is what
#                     upgrades; the token itself is not a draft pick.
#   non-generatable -- tokens, statuses and curses. Not offered, not upgraded.


def _draftable(card) -> tuple[bool, str]:
    """Is this a card a player can draft and then upgrade at a campfire?"""
    if card.kit_card:
        return False, "kit card (arrives charged, never drafted)"
    if card.guest_star or card.generated_by_guest_star:
        return False, "guest star (upgrades via its generator)"
    if not card.generatable:
        return False, "not generatable (token/status/curse)"
    if card.id.endswith(upgrades.SUFFIX):
        return False, "already an upgraded copy"
    return True, ""


# --- Layer 2 exemptions: sheet delta exists, codegen cannot express it. ------
#
# These ARE debts. Each names the gate that clears it, per the curated-set
# discipline: an entry with no gate is an entry nobody will ever remove.
# `nicole_celestial_gift` was the one entry -- the card the 2026-07-25 playtest
# named -- and G-C2 paid the debt by moving its delta onto a field the grammar
# can express. The lint's own stale-curation sweep is what noticed the entry had
# become a lie, which is the behaviour a curated list is supposed to have.
#
# ONE ENTRY AGAIN as of 2026-08-06, and it is SHEET_EXEMPT's twin rather than a
# new judgment. [USER]'s Y-4 reply deleted `copy_cost_override: 0` from
# `docs/furina-upgrades.yaml`, which emptied `encore_performance`'s upgrade. The
# pre-positioned exemption above was written against LAYER 1 (the sheet) only;
# regenerating the C# then moved the same single fact into the Furina manifest's
# `no_upgrade_path`, where LAYER 2 reads it. Two layers see one absent delta, so
# the curated set needs the card named in both. Same debt, same gate, same
# removal condition -- and both entries are deleted together or not at all.
CODEGEN_DEBT: dict[str, str] = {
    "encore_performance":
        "DEBT -- twin of SHEET_EXEMPT's entry, not a second decision. The "
        "sheet delta was deleted by [USER] 2026-08-06 (Y-4) because R110/S-1 "
        "made the card 0-cost, so the generator correctly emits no upgrade "
        "path. Gate: FLAG-2 ruled -> author the replacement delta -> delete "
        "THIS ENTRY AND THE SHEET_EXEMPT ENTRY TOGETHER.",
}


# --- Layer 3 plumbing: reading the emitted C# -------------------------------
#
# Text extraction, not a C# parser -- the house pattern for a lint that has to
# read the mod (tools/lint_handwritten_parity.py regex-extracts every idiom it
# checks). Generated OnUpgrade bodies are a handful of lines emitted by one
# template, so a brace match is enough and a parser dependency would not be.
#
# The one place naive brace matching would misread is a brace inside a comment
# or a string -- `florid_cadenza`'s body carries `{IfUpgraded:show:...}` in its
# comment today. So the match runs over a MASKED copy with comment and literal
# CONTENT blanked to spaces, offsets preserved: the mask says where the body
# ends and how much of it is statements, the original says what it says.

MARKERS = ("Flagged in manifest", "NO upgrade path")
_ONUPGRADE_RE = re.compile(r"OnUpgrade\s*\([^)]*\)\s*\{")


def _mask(text: str) -> str:
    """`text` with comment and string-literal content blanked, offsets kept."""
    out = list(text)
    i, n = 0, len(text)

    def blank(j: int) -> None:
        if out[j] != "\n":
            out[j] = " "

    while i < n:
        pair = text[i:i + 2]
        if pair == "//":
            while i < n and text[i] != "\n":
                blank(i)
                i += 1
        elif pair == "/*":
            blank(i)
            i += 1
            while i < n and text[i:i + 2] != "*/":
                blank(i)
                i += 1
            for _ in range(2):
                if i < n:
                    blank(i)
                    i += 1
        elif pair == '@"':                      # verbatim string: "" escapes "
            blank(i)
            blank(i + 1)
            i += 2
            while i < n:
                if text[i] == '"' and text[i:i + 2] != '""':
                    blank(i)
                    i += 1
                    break
                blank(i)
                i += 1
        elif text[i] in "\"'":                  # ordinary or $-interpolated
            quote = text[i]
            blank(i)
            i += 1
            while i < n:
                if text[i] == "\\" and i + 1 < n:
                    blank(i)
                    blank(i + 1)
                    i += 2
                    continue
                closing = text[i] == quote
                blank(i)
                i += 1
                if closing:
                    break
        else:
            i += 1
    return "".join(out)


def _onupgrade_body(text: str) -> tuple[str, str] | None:
    """(body as written, body with comments/literals blanked), or None.

    None means the file has no OnUpgrade() whose braces balance -- either it is
    not a card file at all (the generated roster/registry classes) or the emit
    is malformed. The caller decides which, from whether the class name maps to
    a sheet id.
    """
    masked = _mask(text)
    match = _ONUPGRADE_RE.search(masked)
    if match is None:
        return None
    depth, i = 1, match.end()
    while i < len(masked) and depth:
        if masked[i] == "{":
            depth += 1
        elif masked[i] == "}":
            depth -= 1
        i += 1
    if depth:
        return None
    return text[match.end():i - 1], masked[match.end():i - 1]


def main() -> int:
    findings: list[str] = []

    # Scope is the DOCS sheets: the cards this project authors. The reference
    # characters' sheets are deliberately out -- ref_ironclad's upgrades are
    # a hand-approximation of the real game's, and holding a reference
    # approximation to our own authoring law would be checking someone else's
    # homework.
    cards = []
    for sheet in loader.DOCS_CARD_SHEETS:
        rows = yaml.safe_load(
            (loader.DOCS_DIR / sheet).read_text(encoding="utf-8")) or []
        for row in rows:
            if isinstance(row, dict) and "id" in row:
                cards.append(loader.peek_card(row["id"]))

    # ---------------- Layer 1: the sheet ----------------
    for card in sorted(cards, key=lambda c: c.id):
        draftable, _why = _draftable(card)
        if not draftable:
            continue
        if card.id in SHEET_EXEMPT or card.id in CODEGEN_DEBT:
            continue        # already named, with its gate, in a curated set
        if not upgrades.has_upgrade(card.id):
            reason = ("no entry in any *-upgrades.yaml"
                      if card.id not in upgrades._upgrade_index()
                      else "entry exists but is not applicable "
                           "(empty, _unexpressible, or in UNAPPLIABLE)")
            findings.append(
                f"[L1] {card.id} ({card.rarity} {card.type}): {reason}")

    # ---------------- Layer 2: the codegen ----------------
    #
    # Read from each profile's manifest rather than re-deriving: the manifest
    # is what the generator actually wrote, so this cannot drift from the
    # emitted C# the way a re-derivation could.
    manifests = sorted(
        (REPO / "klee-mod" / "KleeCode" / "Cards").rglob("manifest.json"))
    if not manifests:
        findings.append("[L2] no codegen manifests found -- has the "
                        "generator ever run?")
    for path in manifests:
        blocked = json.loads(path.read_text(encoding="utf-8"))
        gaps = blocked.get("upgrades", {}).get("no_upgrade_path", {})
        for card_id, why in sorted(gaps.items()):
            if card_id in CODEGEN_DEBT:
                continue
            findings.append(
                f"[L2] {card_id}: generated card ships with NO upgrade path "
                f"-- {why} ({path.relative_to(REPO)})")

    # ---------------- Layer 3: the emitted C# ----------------
    #
    # WHY THE MANIFEST IS NOT A WITNESS TO ITSELF. Layer 2 reads
    # `upgrades.no_upgrade_path` because "the manifest is what the generator
    # actually wrote", which is true and is exactly the problem: the component
    # that writes the manifest is the component that decides whether to emit an
    # upgrade, so one bug in it produces a matching pair of lies and layer 2
    # prints green (that exact shape has shipped: an empty OnUpgrade carrying
    # the no-path marker, unregistered in the manifest). A second witness has
    # to be the artifact the player actually runs: the .cs.
    #
    # EMPTY means NO STATEMENTS -- whitespace and comments only, decided on the
    # masked body so a `{...}` inside a comment cannot be mistaken for code.
    #
    # BUT AN EMPTY BODY IS NOT ITSELF A DEFECT, and this is the discrimination
    # the layer turns on. Most Furina and Kokomi upgrades are structural
    # (`encore: +1`, `add: {op: draw}`, `copy_cost_override: 0`); the generator
    # expresses them by having OnPlay READ IsUpgraded, so OnUpgrade correctly
    # has nothing to do and carries a comment saying where the upgrade went
    # ("expressed at play time as an IsUpgraded read"). Those cards are
    # upgradable and appear in neither the manifest nor CODEGEN_DEBT. So
    # comment-presence cannot be the discriminator -- both the healthy and the
    # broken bodies are one comment long.
    #
    # THE DISCRIMINATOR IS THE CLAIM THE COMMENT MAKES. A body carrying
    # MARKERS ("NO upgrade path" / "Flagged in manifest") asserts that this
    # card has no upgrade and that the manifest says so; that assertion is
    # checkable and is checked. A body with no marker asserts the opposite --
    # the upgrade exists and lives in OnPlay -- and is held to the sheet
    # instead: it must have an applicable delta, which is the fact the play-time
    # emission is derived from. An empty body with NO comment at all claims
    # nothing and is the silent-drop shape itself, so it fails outright.
    #
    # Scope matches layer 1's: guest stars, kit cards and tokens are skipped by
    # the same `_draftable` predicate, for the same reason (their generated
    # files carry the marker legitimately -- a guest-star token is not a
    # campfire pick and its generator card is what upgrades).
    by_class = {pascal(card.id): card for card in cards}
    gaps_cache: dict[Path, dict] = {}
    bodies_read = 0
    for path in sorted(
            (REPO / "klee-mod" / "KleeCode" / "Cards").rglob("Generated/*.cs")):
        text = path.read_text(encoding="utf-8")
        body = _onupgrade_body(text)
        card = by_class.get(path.stem)
        where = path.relative_to(REPO)
        if card is None:
            # The generated roster/registry classes (CompanionRoster.cs,
            # FurinaCardRoster.cs, ...) are not cards and have no OnUpgrade.
            # They are recognised by THAT rather than by a name list, so a real
            # card whose class name stops matching its sheet id is a finding
            # instead of a silent skip.
            if body is not None:
                findings.append(
                    f"[L3] {where}: has an OnUpgrade() but its class name maps "
                    "to no id on any docs sheet -- nothing checks this card")
            continue
        if not _draftable(card)[0]:
            continue

        manifest = path.parent / "manifest.json"
        if manifest not in gaps_cache:
            written_manifest = json.loads(
                manifest.read_text(encoding="utf-8")
            ) if manifest.is_file() else {}
            gaps_cache[manifest] = written_manifest.get(
                "upgrades", {}).get("no_upgrade_path", {})
        gaps = gaps_cache[manifest]
        registered = card.id in gaps or card.id in CODEGEN_DEBT

        delta = upgrades._upgrade_index().get(card.id)
        # Severity, spelled out in the finding: an unupgradable live card whose
        # delta is RATIFIED is a promise the sheet makes and the build breaks,
        # and the sim has been measuring the upgraded card all along.
        sheet_note = (
            f"; docs/*-upgrades.yaml carries a ratified delta {delta} that the "
            "live card does not have" if delta else
            "; no sheet delta either, so nothing anywhere upgrades this card")

        if body is None:
            findings.append(
                f"[L3] {card.id}: no OnUpgrade() with balanced braces in "
                f"{where} -- the card cannot express an upgrade at all")
            continue
        written, statements = body
        bodies_read += 1

        if statements.strip():
            if registered:
                findings.append(
                    f"[L3] {card.id}: {where} emits upgrade statements, but "
                    "the card is registered as having no upgrade path "
                    "(manifest no_upgrade_path / CODEGEN_DEBT) -- it is stale "
                    "and layer 2 is suppressing a card that works")
            continue

        # --- empty body from here down ---
        if any(marker in written for marker in MARKERS):
            if not registered:
                findings.append(
                    f"[L3] {card.id}: {where} has an EMPTY OnUpgrade() whose "
                    f"comment claims the manifest flags it, but "
                    f"{manifest.relative_to(REPO)} does not list it and it is "
                    f"not in CODEGEN_DEBT{sheet_note}")
        elif not registered:
            if not written.strip():
                findings.append(
                    f"[L3] {card.id}: {where} has an EMPTY OnUpgrade() with no "
                    "comment at all -- a dropped delta leaves exactly this "
                    f"shape{sheet_note}")
            elif not upgrades.has_upgrade(card.id):
                findings.append(
                    f"[L3] {card.id}: {where} has an EMPTY OnUpgrade() whose "
                    "comment claims the upgrade is expressed at play time, but "
                    "the sheet has no applicable delta for it to be derived "
                    "from")

    # ---------------- Stale curation ----------------
    #
    # An exemption that no longer applies is worse than no exemption: it reads
    # as a considered decision while silently covering nothing. Both lists are
    # swept.
    known = {c.id for c in cards}
    for card_id in sorted(SHEET_EXEMPT):
        if card_id not in known:
            findings.append(
                f"[STALE] SHEET_EXEMPT lists '{card_id}', which is not on any "
                "sheet -- remove it")
    # NOT swept: "SHEET_EXEMPT names a card that has an applicable delta".
    # That is the natural mirror of CODEGEN_DEBT's sweep below and it was
    # written, run, and REMOVED on 2026-08-06 because it fired on
    # `encore_performance` for a reason that was not staleness: R110's S-1 had
    # deleted the card's energy refund but STOPPED short of deleting
    # `copy_cost_override: 0` from `docs/furina-upgrades.yaml`, so the sheet
    # still carried a delta R110 had already made meaningless.
    #
    # THAT STATE ENDED 2026-08-06. [USER]'s Y-4 reply authorised the stopped
    # deletion; the sheet entry is gone and the exemption above stopped being
    # pre-positioned and became LOAD-BEARING -- remove it and L1 reports
    # `encore_performance` immediately (checked in both directions when the
    # deletion landed). The sweep this comment describes is therefore now
    # addable without turning a stopped deletion into a red lint. It is still
    # NOT added, because adding it is a lint-hardening decision of its own and
    # Y-4 authorised a deletion, not a new check. Recorded so the next reader
    # inherits the reason rather than re-deriving it.
    live_gaps = {
        cid
        for path in manifests
        for cid in json.loads(
            path.read_text(encoding="utf-8")
        ).get("upgrades", {}).get("no_upgrade_path", {})
    }
    for card_id in sorted(CODEGEN_DEBT):
        if card_id not in live_gaps:
            findings.append(
                f"[STALE] CODEGEN_DEBT lists '{card_id}', but the generator "
                "now emits its upgrade -- delete the entry, the debt is paid")

    if findings:
        print(f"upgrade coverage: {len(findings)} finding(s)")
        for finding in findings:
            print(f"  {finding}")
        return 1

    drafted = sum(1 for c in cards if _draftable(c)[0])
    # The L3 count is printed for the same reason lint_unique_names prints its
    # relic line: a layer that read ZERO files reports the same clean word as
    # one that read them all, and this one globs for its inputs.
    print(f"upgrade coverage OK: {drafted} draftable cards across "
          f"{len(loader.DOCS_CARD_SHEETS)} sheets, "
          f"{len(CODEGEN_DEBT)} curated codegen debt(s), "
          f"{bodies_read} generated OnUpgrade bodies read")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

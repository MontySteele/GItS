#!/usr/bin/env python3
"""One source for the custom-keyword loc rows: the C#. The pck copy is derived.

    python tools/gen_keyword_loc.py            # write the derived json
    python tools/gen_keyword_loc.py --check    # verify it, write nothing

THE DEFECT. Every `KLEEMOD-*` keyword tooltip the game shows existed TWICE:

  * `klee-mod/KleeCode/KleeMod.cs`, in the `keywordFallback` dictionary, with
    its numerals INTERPOLATED from the constants they quote (`EB-89`, so a
    repricing cannot leave a tip telling a player a retired number);
  * `tools/build_pck.ps1`, hand-typed inside a heredoc, with the numerals as
    literals.

and the pck copy WINS -- the game merges the packaged table over ours, so the
half a player actually reads was the half no constant fed. The two agreed only
because nobody had repriced anything yet. `EB-89`'s whole argument, applied to
the copy that loses, is a lint that measures the wrong file.

THE FIX, in the shape the rest of this repo uses for the same problem
(`gen_roster_cards.py`, `gen_prototype_cards.py`): the C# is the source, the
pck's json is GENERATED from it and committed, `--check` is the staleness gate,
and `tools/build_pck.ps1` no longer types the rows at all -- the file lands in
the pack through the `klee-mod/pck-src` overlay, like every other tracked pck
resource.

WHICH ROWS ARE DERIVED, and why not all of them.

  * Only rows whose KEY is a plain string literal (`["KLEEMOD-BOMB.title"]`).
    The dictionary also holds rows keyed by a C# constant
    (`[Cards.FurinaRiderTips.FanfareKey + ".title"]`) -- those are hover-tip
    TITLES whose bodies are built live in C# from per-card numbers, the pck
    has never carried one, and resolving their keys would mean evaluating C#
    rather than reading it. They stay DLL-only, which is where their only
    source has always been.
  * Nothing inside `#if PROTOTYPE_CARDS`. Those are the quarantined arms'
    keywords (`EB-272`). The pck is built once and ships in release packages;
    a release pack carrying arm text would be the quarantine leaking through
    a resource file instead of through the dll.

INTERPOLATION IS RESOLVED, NOT COPIED. `{Elements.ReactionConstants.AuraDurationTurns}`
is looked up in the C# `public const` that defines it, so the generated json
carries the same number the dll computes. An expression this cannot resolve is
an ERROR, never a passthrough: a `{...}` left in a loc string renders as a
SmartFormat placeholder against a table that has no such variable.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENTRY = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"
CSHARP_ROOT = REPO / "klee-mod" / "KleeCode"
OUT = (REPO / "klee-mod" / "pck-src" / "klee" / "localization" / "eng"
       / "card_keywords.json")

BLOCK_START = "var keywordFallback = new Dictionary<string, string>"
BLOCK_END = "keywordTable.MergeWith(keywordFallback"

# ["KEY"] = "value" / $"value", the value possibly on the following line.
ROW = re.compile(
    r'\[\s*"(?P<key>[^"]+)"\s*\]\s*=\s*(?P<dollar>\$?)"(?P<value>[^"]*)"\s*,',
    re.S)

INTERP = re.compile(r"\{([^{}]+)\}")


def constants() -> dict[str, str]:
    """Every `public const <T> Name = <value>;` in the C# tree, by short name
    and by `Class.Name`.

    Both spellings, because the call sites are written both ways
    (`{Powers.BurstConstants.PerSkillTag}` and, elsewhere, a bare name), and
    resolution here is by SUFFIX match -- the last one or two dotted segments
    -- which is exactly how a C# reader disambiguates them too.
    """
    table: dict[str, str] = {}
    pattern = re.compile(
        r"public\s+static\s+class\s+(?P<cls>\w+)"
        r"|public\s+const\s+\w+\s+(?P<name>\w+)\s*=\s*(?P<value>[^;]+);")
    for path in sorted(CSHARP_ROOT.rglob("*.cs")):
        current = ""
        for match in pattern.finditer(path.read_text(encoding="utf-8")):
            if match.group("cls"):
                current = match.group("cls")
                continue
            value = match.group("value").strip()
            if not re.fullmatch(r"-?\d+", value):
                continue                     # only numerals reach a loc row
            table[match.group("name")] = value
            table[f"{current}.{match.group('name')}"] = value
    return table


def resolve(expression: str, table: dict[str, str], key: str) -> str:
    """`Powers.BurstConstants.PerSkillTag` -> `5`, or die saying which row."""
    parts = expression.strip().split(".")
    for depth in (2, 1):
        if len(parts) >= depth:
            candidate = ".".join(parts[-depth:])
            if candidate in table:
                return table[candidate]
    raise SystemExit(
        f"gen_keyword_loc: cannot resolve '{{{expression}}}' in row '{key}'. "
        f"A loc row may only interpolate a `public const` numeral -- an "
        f"unresolved brace ships to the player as a SmartFormat placeholder "
        f"against a table that has no such variable.")


def strip_prototype(text: str) -> str:
    """Drop every `#if PROTOTYPE_CARDS` region.

    Nesting is not handled and does not need to be: `KleeMod.cs` has no nested
    conditionals, and a new one would show up as an unbalanced `#endif` here
    rather than as arm text quietly reaching a release pack -- the failure
    direction that matters.
    """
    out, skipping = [], False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#if PROTOTYPE_CARDS"):
            skipping = True
            continue
        if skipping and stripped.startswith("#endif"):
            skipping = False
            continue
        if not skipping:
            out.append(line)
    return "\n".join(out)


def rows() -> dict[str, str]:
    """The derived table, in the order the C# declares it."""
    text = ENTRY.read_text(encoding="utf-8")
    try:
        start = text.index(BLOCK_START)
        end = text.index(BLOCK_END, start)
    except ValueError:
        raise SystemExit(
            f"gen_keyword_loc: could not find the keywordFallback dictionary "
            f"in {ENTRY}. It is the SOURCE of these rows; if it was renamed, "
            f"this generator has to be pointed at the new name rather than "
            f"quietly emitting nothing.")
    block = strip_prototype(text[start:end])

    table = constants()
    out: dict[str, str] = {}
    for match in ROW.finditer(block):
        key = match.group("key")
        value = match.group("value")
        if match.group("dollar"):
            value = INTERP.sub(
                lambda m: resolve(m.group(1), table, key), value)
        elif "{" in value:
            raise SystemExit(
                f"gen_keyword_loc: row '{key}' has a brace but is not an "
                f"interpolated string. SmartFormat would read it as a "
                f"placeholder.")
        out[key] = value
    if not out:
        raise SystemExit(
            "gen_keyword_loc: the dictionary parsed to ZERO rows. An empty "
            "sweep is the failure mode, not a pass.")
    return out


def rendered(table: dict[str, str]) -> str:
    return json.dumps(table, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify the committed json, write nothing")
    args = parser.parse_args(argv)

    text = rendered(rows())
    if args.check:
        if not OUT.exists():
            print(f"gen_keyword_loc: {OUT.relative_to(REPO)} is missing. "
                  f"Run: python tools/gen_keyword_loc.py")
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print(f"gen_keyword_loc: {OUT.relative_to(REPO)} is STALE -- the "
                  f"pck's keyword rows no longer match KleeMod.cs, and the "
                  f"pck copy is the one the player reads. Run: python "
                  f"tools/gen_keyword_loc.py")
            return 1
        print(f"gen_keyword_loc: OK ({len(rows())} rows)")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"gen_keyword_loc: wrote {OUT.relative_to(REPO)} "
          f"({len(rows())} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

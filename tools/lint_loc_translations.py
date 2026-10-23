#!/usr/bin/env python3
"""Translation lint: placeholders and staleness (localization route b, 2026-10-19).

THE FORMAT. A translation ships in the mod pck as the game's own flat table
file, key -> string, one per language and table:

    klee-mod/pck-src/klee/localization/<lang>/<table>.json

The game merges it over that language's base table and it wins per key; a key
it lacks falls back to our English (the English table; see
`klee-mod/KleeCode/Localization/EnglishLoc.cs`). The game file stays flat, so
the English each row was translated from is recorded beside it, outside the
pck, as a sidecar of the same shape:

    klee-mod/localization/hashes/<lang>/<table>.json    key -> hash

where hash is the first 16 hex digits of sha256 of the English row (UTF-8).
`--stamp <lang>` writes the sidecar for every row a translation holds, against
today's English; run it once a translator has finished a pass.

The English is `klee-mod/localization/reference/eng.json` ({table: {key:
English}}), written by the C# test `LocReferenceTests`, which also fails when
it is stale.

THE CHECKS, per translated row:
  * the table and key exist in the English reference (an orphan row is a key
    that drifted, and the game would never read it);
  * every `{placeholder}` matches its English row: the same multiset of
    `{Name:formatter}` heads (the plural / cond branches inside may differ,
    since each language writes its own forms);
  * a hash is recorded, and it is the hash of today's English: a row whose
    English moved since it was translated is STALE.

THE TEYVAT FRAME'S ROWS are not to translate while the frame is off. The
reference lists them because its build turns the frame arm on; a release
build merges none of them. `klee-mod/localization/reference/teyvat_frame_rows.json`
({table: [key, ...]}, written beside the reference by the same test) names
them, and a translated row among them is a finding (the work would ship
nowhere, and its English has had no full pass: review/active/story-text-audit-2026-10-23.md).
The clean report counts the rows left to translate without them.

There are no translations today, so it passes vacuously.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "klee-mod" / "localization" / "reference" / "eng.json"
TRANSLATIONS = ROOT / "klee-mod" / "pck-src" / "klee" / "localization"
HASHES = ROOT / "klee-mod" / "localization" / "hashes"
FRAME_ROWS = ROOT / "klee-mod" / "localization" / "reference" / "teyvat_frame_rows.json"

#: The game's languages (`LocManager._supportedLanguages`, v0.111.0).
LANGUAGES = frozenset({
    "eng", "zhs", "zht", "deu", "esp", "fra", "ind", "ita", "jpn", "kor",
    "pol", "ptb", "rus", "spa", "tha", "tur",
})


def english_hash(text: str) -> str:
    """The recorded hash of one English row."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def placeholders(text: str) -> Counter:
    """The `{...}` groups at brace depth 0, by head: the selector and its
    formatter name (`{Cards:plural:card|cards}` -> `Cards:plural`,
    `{Damage:diff()}` -> `Damage:diff`, `{Amount}` -> `Amount`)."""
    heads: Counter = Counter()
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0:
                inner = text[start:i]
                parts = inner.split(":", 2)
                head = parts[0].strip()
                if len(parts) > 1:
                    head += ":" + parts[1].split("(", 1)[0].strip()
                heads[head] += 1
    return heads


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def translation_files(root: Path = TRANSLATIONS):
    """(lang, table, path) for every translated table file."""
    if not root.is_dir():
        return
    for lang_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if lang_dir.name == "eng":
            continue
        for path in sorted(lang_dir.glob("*.json")):
            yield lang_dir.name, path.stem, path


def frame_rows(path: Path = FRAME_ROWS) -> dict[str, set[str]]:
    """The Teyvat frame's rows, {table: {key}}; empty when the list is
    missing."""
    if not path.exists():
        return {}
    return {table: set(keys) for table, keys in load_json(path).items()}


def to_translate(reference: dict, frame: dict[str, set[str]]) -> int:
    """The rows a translation covers: the reference less the frame's."""
    return sum(1 for table, rows in reference.items()
               for key in rows if key not in frame.get(table, ()))


def check(reference: dict, translations_root: Path = TRANSLATIONS,
          hashes_root: Path = HASHES,
          frame: dict[str, set[str]] | None = None) -> list[str]:
    """Every finding, as one line each. `frame` is the Teyvat frame's rows
    (`frame_rows()`), not to translate."""
    frame = frame or {}
    findings: list[str] = []
    for lang, table, path in translation_files(translations_root):
        where = f"{path.relative_to(translations_root).as_posix()}"
        if lang not in LANGUAGES:
            findings.append(f"{where}: '{lang}' is not one of the game's languages")
            continue
        rows = load_json(path)
        if not isinstance(rows, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in rows.items()):
            findings.append(f"{where}: not a flat key -> string table")
            continue
        english = reference.get(table)
        if english is None:
            findings.append(f"{where}: no table '{table}' in the English reference")
            continue
        hash_path = hashes_root / lang / f"{table}.json"
        hashes = load_json(hash_path) if hash_path.exists() else {}
        for key, text in sorted(rows.items()):
            source = english.get(key)
            if source is None:
                findings.append(f"{where}: {key}: no such English row (orphan)")
                continue
            if key in frame.get(table, ()):
                findings.append(f"{where}: {key}: a Teyvat frame row, not to "
                                "translate while the frame is off")
                continue
            want, got = placeholders(source), placeholders(text)
            if want != got:
                missing = sorted((want - got).elements())
                extra = sorted((got - want).elements())
                findings.append(
                    f"{where}: {key}: placeholders differ from English"
                    + (f"; missing {missing}" if missing else "")
                    + (f"; extra {extra}" if extra else ""))
            recorded = hashes.get(key)
            if recorded is None:
                findings.append(f"{where}: {key}: no English hash recorded "
                                f"(run --stamp {lang} after translating)")
            elif recorded != english_hash(source):
                findings.append(f"{where}: {key}: STALE, the English changed since "
                                "it was translated")
    return findings


def stamp(reference: dict, lang: str, translations_root: Path = TRANSLATIONS,
          hashes_root: Path = HASHES) -> int:
    """Write the hash sidecars for every row `lang` translates. Returns the
    number of rows stamped."""
    count = 0
    for file_lang, table, path in translation_files(translations_root):
        if file_lang != lang:
            continue
        english = reference.get(table, {})
        rows = load_json(path)
        hashes = {key: english_hash(english[key])
                  for key in sorted(rows) if key in english}
        out = hashes_root / lang / f"{table}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(hashes, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8", newline="\n")
        count += len(hashes)
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--stamp", metavar="LANG",
                        help="record today's English hash for every row LANG translates")
    args = parser.parse_args(argv)

    if not REFERENCE.exists():
        print(f"lint_loc_translations: {REFERENCE.relative_to(ROOT)} is missing")
        return 1
    reference = load_json(REFERENCE)

    if args.stamp:
        n = stamp(reference, args.stamp)
        print(f"lint_loc_translations: stamped {n} row(s) for {args.stamp}")
        return 0

    frame = frame_rows()
    findings = check(reference, frame=frame)
    files = sum(1 for _ in translation_files())
    if findings:
        for line in findings:
            print(line)
        print(f"lint_loc_translations: {len(findings)} finding(s) in {files} file(s)")
        return 1
    skipped = sum(len(keys) for keys in frame.values())
    print(f"lint_loc_translations: OK ({files} translated table file(s); "
          f"{to_translate(reference, frame)} rows to translate, "
          f"{skipped} Teyvat frame rows skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Gate 4 -- package contents against the pck build contract.

`tools/build_pck.ps1` derives `klee.pck.contract.txt` from the files that
actually landed in the export work directory (the C4 repair: the v2 contract
was a hand-written list that asserted a set of resources whether or not the
copy blocks had run). The contract is therefore the closest thing this project
has to a manifest of what shipped, and `validate.ps1` S2 already proves it
BELONGS to the pack next to it by sha256.

What no rule asks today, and what this gate asks:

  * is the contract itself well formed -- one sha256, sorted, no duplicates,
    no build scaffolding, no `.import` sidecars, every row namespaced;
  * does the staged package have exactly the shape ModManager expects (one
    manifest.json, one .pck, that pck's contract beside it, and no other
    JSON -- the portable half of S1, which is PowerShell-only today);
  * does every git-tracked scene source under `klee-mod/pck-src` have a row
    in the contract? That is the question the C4 repair makes answerable and
    nobody asks: `pck-src` is committed, so a scene that exists in the repo
    and NOT in the pack is visible on any machine, with no art and no game.

Everything here takes explicit paths. The gate never looks for a deployed mod
and never reads the game directory.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from .findings import Report

GATE = "contract"

DEFAULT_VERSION = "roster-pck-v3"

_RESOURCE_PREFIX = "resource=res://"
_SHA_LINE = re.compile(r"^sha256=([0-9A-Fa-f]*)$")
_VERSION_LINE = re.compile(r"^contract=(.*)$")

#: Never legitimate rows. The exporter's own scaffolding and its import cache;
#: build_pck.ps1 excludes them when it derives the file, so their presence
#: means the contract was written by something else -- most likely by hand,
#: which is the whole class C4 retired.
_SCAFFOLDING = ("project.godot", "export_presets.cfg", ".godot/", ".import")


@dataclass
class Contract:
    version: str | None = None
    sha256: str | None = None
    sha_lines: int = 0
    resources: list[str] = field(default_factory=list)
    other_lines: list[tuple[int, str]] = field(default_factory=list)

    @property
    def resource_set(self) -> set[str]:
        return set(self.resources)


def parse(text: str) -> Contract:
    contract = Contract()
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        match = _VERSION_LINE.match(line)
        if match:
            if contract.version is None:
                contract.version = match.group(1).strip()
            else:
                contract.other_lines.append((number, line))
            continue
        match = _SHA_LINE.match(line)
        if match:
            contract.sha_lines += 1
            if contract.sha256 is None:
                contract.sha256 = match.group(1)
            continue
        if line.startswith(_RESOURCE_PREFIX):
            contract.resources.append(line[len(_RESOURCE_PREFIX):])
            continue
        contract.other_lines.append((number, line))
    return contract


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    # Builtin-`open` form rather than `path.open("rb")` deliberately:
    # tools/lint_text_encoding.py reads the mode from positional arg 1, so the
    # bound-method form is invisible to it and gets counted as an undeclared
    # TEXT read. See the lane handoff -- the lint blind spot is reported, not
    # worked around by editing a file this lane does not own.
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def check_contract(
    contract: Contract,
    report: Report,
    where: str,
    expected_version: str = DEFAULT_VERSION,
    pck_path: Path | None = None,
) -> None:
    if contract.version is None:
        report.error("CT-NO-VERSION", where,
                     "contract has no 'contract=' line; it cannot be told "
                     "apart from a stale hand-written list.")
    elif contract.version != expected_version:
        report.error(
            "CT-VERSION", where,
            f"contract version is {contract.version!r}, expected "
            f"{expected_version!r}. A v2 contract is a hand-written assertion, "
            "not a measurement -- rebuild with tools/build_pck.ps1.",
        )

    if contract.sha_lines != 1:
        report.error("CT-SHA-COUNT", where,
                     f"expected exactly one sha256 line, found "
                     f"{contract.sha_lines}.")
    elif not re.fullmatch(r"[0-9A-Fa-f]{64}", contract.sha256 or ""):
        report.error("CT-SHA-FORMAT", where,
                     f"sha256 value {contract.sha256!r} is not 64 hex digits.")
    elif pck_path is not None:
        if not pck_path.is_file():
            report.error("CT-NO-PCK", str(pck_path),
                         "pck named for the sha256 comparison does not exist.")
        else:
            actual = sha256_of(pck_path)
            if actual.upper() != (contract.sha256 or "").upper():
                report.error(
                    "CT-SHA-MISMATCH", where,
                    f"contract sha256 {contract.sha256} does not match "
                    f"{pck_path.name} ({actual}). The contract describes a "
                    "different pack than the one beside it.",
                )

    for number, line in contract.other_lines:
        report.error("CT-UNKNOWN-LINE", f"{where}:{number}",
                     f"unrecognised line {line!r}; a contract carries only "
                     "contract=, sha256= and resource=res:// lines.")

    if not contract.resources:
        report.error(
            "CT-EMPTY", where,
            "contract declares no resources. build_pck.ps1 refuses to write "
            "an empty one, so an empty contract here means the file was "
            "produced some other way.",
        )
        return

    seen: set[str] = set()
    for resource in contract.resources:
        if resource in seen:
            report.error("CT-DUPLICATE", where,
                         f"resource res://{resource} is listed more than once.")
        seen.add(resource)
        if "/" not in resource:
            report.error(
                "CT-NO-NAMESPACE", where,
                f"resource res://{resource} sits at the pack root. Every "
                "shipped resource lives under a character or shared "
                "namespace; a root-level file collides with the base game.",
            )
        for bad in _SCAFFOLDING:
            if bad in resource:
                report.error(
                    "CT-SCAFFOLDING", where,
                    f"resource res://{resource} is exporter scaffolding "
                    f"({bad}). build_pck.ps1 excludes these when it derives "
                    "the contract.",
                )
                break
        if resource.endswith(".pck"):
            report.error("CT-SELF", where,
                         f"contract lists the pack itself (res://{resource}).")

    if contract.resources != sorted(contract.resources):
        report.warning(
            "CT-UNSORTED", where,
            "resource rows are not sorted. build_pck.ps1 sorts them, so an "
            "unsorted contract was edited after the build -- and an unsorted "
            "contract makes every diff between two builds unreadable.",
        )


def check_package(package_dir: Path, report: Report, root: Path) -> Path | None:
    """The staged-package shape rules. Returns the contract file if found."""
    try:
        where = package_dir.relative_to(root).as_posix()
    except ValueError:
        where = package_dir.as_posix()

    if not package_dir.is_dir():
        report.error("PK-NO-DIR", where, "staged package directory does not exist.")
        return None

    files = sorted(
        (p for p in package_dir.rglob("*") if p.is_file()),
        key=lambda p: p.as_posix(),
    )
    report.checked["package_files"] = len(files)
    if not files:
        report.error("PK-EMPTY", where,
                     "staged package contains no files. An empty sweep is the "
                     "failure mode, not a pass.")
        return None

    jsons = [p for p in files if p.suffix.lower() == ".json"]
    if not any(p.name == "manifest.json" for p in jsons):
        report.error("PK-NO-MANIFEST", where,
                     "package has no manifest.json; ModManager will not load it.")
    for path in jsons:
        if path.name != "manifest.json":
            report.error(
                "PK-STRAY-JSON", path.relative_to(package_dir).as_posix(),
                "ModManager walks mods/ recursively and parses EVERY *.json "
                "as a manifest; a stray one throws on every boot, for every "
                "mod. (Portable restatement of validate.ps1 S1.)",
            )

    pcks = [p for p in files if p.suffix.lower() == ".pck"]
    if len(pcks) != 1:
        report.error("PK-PCK-COUNT", where,
                     f"expected exactly one .pck in the package, found "
                     f"{len(pcks)}: {[p.name for p in pcks]}.")
        return None
    pck = pcks[0]
    contract_path = pck.with_name(pck.name + ".contract.txt")
    if not contract_path.is_file():
        report.error(
            "PK-NO-CONTRACT", where,
            f"{pck.name} has no build contract beside it at "
            f"{contract_path.name}. Rebuild with tools/build_pck.ps1.",
        )
        return None
    return contract_path


def check_sources(
    pck_src: Path, contract: Contract, report: Report, root: Path
) -> None:
    """Every committed scene source must appear in the contract.

    `klee-mod/pck-src` is git-tracked and copied verbatim into the export work
    directory (build_pck.ps1:733-737), so its layout IS its pack layout. A file
    there with no contract row did not reach the pack.
    """
    if not pck_src.is_dir():
        report.note("PK-NO-SRC", str(pck_src),
                    "no pck-src directory supplied; source coverage not checked.")
        return
    sources = sorted(
        (p for p in pck_src.rglob("*")
         if p.is_file() and p.suffix in (".tscn", ".tres")),
        key=lambda p: p.as_posix(),
    )
    report.checked["scene_sources"] = len(sources)
    if not sources:
        report.error("PK-SRC-EMPTY", str(pck_src),
                     "pck-src holds no .tscn/.tres files; an empty sweep is "
                     "the failure mode, not a pass.")
        return
    packed = contract.resource_set
    for path in sources:
        relative = path.relative_to(pck_src).as_posix()
        if relative not in packed:
            report.error(
                "PK-SRC-UNPACKED",
                path.relative_to(root).as_posix()
                if root in path.parents else path.as_posix(),
                f"scene source is committed at pck-src/{relative} but the "
                f"contract has no res://{relative} row. It did not reach the "
                "pack, and every C# path that names it resolves to nothing.",
            )


def run(
    contract_path: Path | None,
    root: Path,
    package_dir: Path | None = None,
    pck_src: Path | None = None,
    pck_path: Path | None = None,
    expected_version: str = DEFAULT_VERSION,
) -> Report:
    report = Report(GATE)
    if package_dir is not None:
        found = check_package(package_dir, report, root)
        if contract_path is None:
            contract_path = found
        if pck_path is None and found is not None:
            pck_path = found.with_name(found.name[: -len(".contract.txt")])
    if contract_path is None:
        if not report.findings:
            report.error("CT-NO-CONTRACT", str(root),
                         "no contract file given and none found.")
        return report
    if not contract_path.is_file():
        report.error("CT-NO-CONTRACT", str(contract_path),
                     "contract file does not exist.")
        return report
    try:
        where = contract_path.relative_to(root).as_posix()
    except ValueError:
        where = contract_path.as_posix()
    contract = parse(contract_path.read_text(encoding="utf-8", errors="replace"))
    report.checked["contract_resources"] = len(contract.resources)
    check_contract(contract, report, where, expected_version, pck_path)
    if pck_src is not None:
        check_sources(pck_src, contract, report, root)
    return report

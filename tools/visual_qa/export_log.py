"""Gate 1 -- read a MegaDot headless import/export log for errors.

What `tools/build_pck.ps1` does today (read, not edited by this lane):

    $importLog = Invoke-NativeCaptured $MegaDot --headless --path $work --import
    if ($LASTEXITCODE -ne 0) { ... throw "MegaDot import failed" }
    $importErrors = $importLog | Select-String 'ERROR'
    if ($importErrors) { ... throw "MegaDot import reported errors." }

    $exportLog = Invoke-NativeCaptured $MegaDot --headless --path $work --export-pack ...
    if ($LASTEXITCODE -ne 0) { ... throw "MegaDot export failed" }

    -- tools/build_pck.ps1:770-781

Two properties of that, both of which this gate exists to cover:

  * the ERROR sweep is applied to the IMPORT log ONLY. The export stage's log
    is checked by exit code alone, so an export that logs a missing dependency
    and still exits 0 goes through clean.
  * `Select-String 'ERROR'` is case-INSENSITIVE (PowerShell's default) and
    unanchored, so a path containing the letters "error" trips it, while a
    Godot `USER ERROR:` and its `at:` continuation line are reported as one
    naked line with no context.

This gate takes the log as TEXT -- captured to a file, or piped in -- so it
runs anywhere, including on a machine with no editor. It attributes every
finding to a stage by watching for build_pck.ps1's own banner lines, and it
requires the banners to be present: a truncated log that contains no errors
because it contains nothing is the failure mode, not a pass.

The gate does not run MegaDot and never will: the game is single-install on
this machine and a build is [USER]'s to start.
"""

from __future__ import annotations

import re
from pathlib import Path

from .findings import Report

GATE = "export-log"

#: Godot's own diagnostic prefixes, matched CASE-SENSITIVELY and anchored to
#: the start of a (possibly indented) line, which is how the engine writes
#: them. Anything looser matches file names.
_ERROR_LINE = re.compile(r"^\s*(?:USER\s+|SCRIPT\s+)?ERROR:\s*(?P<msg>.*)$")
_WARN_LINE = re.compile(r"^\s*(?:USER\s+)?WARNING:\s*(?P<msg>.*)$")
_AT_LINE = re.compile(r"^\s*at:\s*(?P<at>.*)$")

#: Failures Godot reports at NOTICE volume -- no ERROR: prefix, and every one
#: of them means a resource did not load. Substring matches, because the
#: engine writes them mid-line with a path appended.
_SOFT_FAILURES = (
    "Unrecognized dependency",
    "Failed loading resource",
    "Failed to load resource",
    "Cannot open file",
    "No loader found for resource",
    "Resource file not found",
    "Can't open dynamic library",
    "Condition \"err != OK\" is true",
)

#: build_pck.ps1's stage banners. Their absence means the log is not a build
#: log, or is truncated -- either way the gate must not report "clean".
STAGE_MARKERS = {
    "import": "Importing assets (MegaDot headless)",
    "export": "Exporting pack",
}
#: The line build_pck.ps1 prints only after the pck AND its derived contract
#: landed (tools/build_pck.ps1:824).
COMPLETION_MARKER = "contract roster-pck-v3"


def _stage_at(index: int, stage_starts: dict[str, int]) -> str:
    stage = "preamble"
    best = -1
    for name, start in stage_starts.items():
        if start <= index and start > best:
            stage, best = name, start
    return stage


def scan(text: str, source: str = "<log>", require_completion: bool = True) -> Report:
    """Read one captured build log."""
    report = Report(GATE)
    lines = text.splitlines()
    report.checked["log_lines"] = len(lines)

    if not lines:
        report.error("XL-EMPTY", source,
                     "log is empty. A build that produced no output did not "
                     "run; there is nothing here to have been clean about.")
        return report

    stage_starts: dict[str, int] = {}
    for index, line in enumerate(lines):
        for stage, marker in STAGE_MARKERS.items():
            if stage not in stage_starts and marker in line:
                stage_starts[stage] = index

    errors = 0
    warnings = 0
    for index, line in enumerate(lines):
        number = index + 1
        stage = _stage_at(index, stage_starts)
        match = _ERROR_LINE.match(line)
        if match:
            errors += 1
            context = ""
            if index + 1 < len(lines):
                at = _AT_LINE.match(lines[index + 1])
                if at:
                    context = f"  (at: {at.group('at').strip()})"
            report.error(
                "XL-ERROR", f"{source}:{number}",
                f"[{stage} stage] {match.group('msg').strip()}{context}",
            )
            continue
        match = _WARN_LINE.match(line)
        if match:
            warnings += 1
            report.warning(
                "XL-WARNING", f"{source}:{number}",
                f"[{stage} stage] {match.group('msg').strip()}",
            )
            continue
        for needle in _SOFT_FAILURES:
            if needle in line:
                errors += 1
                report.error(
                    "XL-DEPENDENCY", f"{source}:{number}",
                    f"[{stage} stage] {line.strip()} -- Godot reports this "
                    "without an ERROR: prefix, so an exit-code check and a "
                    "grep for 'ERROR' both miss it.",
                )
                break

    report.checked["godot_errors"] = errors
    report.checked["godot_warnings"] = warnings

    for stage, marker in sorted(STAGE_MARKERS.items()):
        if stage not in stage_starts:
            report.error(
                "XL-STAGE-MISSING", source,
                f"log contains no {stage!r} stage banner ({marker!r}). Either "
                "this is not a build_pck.ps1 log or it is truncated; a clean "
                "read of a log that never reached the stage proves nothing.",
            )
    if require_completion and COMPLETION_MARKER not in text:
        report.error(
            "XL-INCOMPLETE", source,
            f"log never reaches the completion line ({COMPLETION_MARKER!r}); "
            "the build did not finish writing the pck and its contract.",
        )
    return report


def run(log_path: Path, root: Path, require_completion: bool = True) -> Report:
    if not log_path.is_file():
        report = Report(GATE)
        report.error("XL-NO-LOG", str(log_path), "log file does not exist.")
        return report
    try:
        where = log_path.relative_to(root).as_posix()
    except ValueError:
        where = log_path.as_posix()
    return scan(
        log_path.read_text(encoding="utf-8", errors="replace"),
        source=where,
        require_completion=require_completion,
    )

"""Gate 3 -- unintended cross-character fallback, and silently skipped art.

`tools/build_pck.ps1` fills a character's missing pck asset from Klee's copy
and prints one line per substitution:

    Write-Host "Furina fallback: $relative <- Klee" -ForegroundColor DarkYellow
    -- tools/build_pck.ps1:230 (and :264 for Kokomi)

and it collects every copy block whose source directory was absent:

    Write-Host "SKIPPED: $what -- no source at $path" -ForegroundColor Yellow
    -- tools/build_pck.ps1:128

Both lines are the build being honest. Neither is a GATE: they are console
output on a machine where nobody is watching the console, and the comment at
build_pck.ps1:196-201 records exactly that failure -- a `-Exclude` bug dropped
BOTH characters back onto Klee's fallbacks, the build went green, and it was
"caught only because the fallback lines are printed".

This gate turns the printed lines into a checked ledger. It fails in BOTH
directions, which is the repo's standing shape for an allowlist (validate.ps1
S12's `$pckDeferred`, tier0/tests/test_pck_reference_gate.py):

  * an observed fallback or skip that the policy does not declare is a
    FINDING -- that is the unintended cross-character fallback;
  * a policy entry that the build did not produce is a FINDING too -- a stale
    exemption is how the next one gets waved through.

The policy is a plain data file (YAML if PyYAML is importable, else the JSON
subset). This lane ships a SAMPLE, never a live policy: writing down which of
today's fallbacks are intended is a call about the art plan, and belongs to
[USER] / the art owner, not to a QA gate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .findings import Report

GATE = "fallback"

_FALLBACK_PREFIX = " fallback: "
_SKIP_PREFIX = "SKIPPED: "
_SKIP_SEPARATOR = " -- no source at "


def _normalise(resource: str) -> str:
    """`ui\\transition_wipe.png` and `ui/transition_wipe.png` are one key.

    build_pck.ps1 prints Windows separators because it joins Windows paths;
    the contract and every C# reference use forward slashes. Comparing them
    raw is a bug waiting for the first policy author.
    """
    return resource.strip().replace("\\", "/").lstrip("/")


@dataclass(frozen=True)
class Fallback:
    into: str          # character whose namespace received the file
    resource: str      # normalised, namespace-relative: "ui/char_icon.png"
    source: str        # character the file came from
    line: int

    def key(self) -> tuple[str, str, str]:
        return (self.into.lower(), self.resource, self.source.lower())


@dataclass(frozen=True)
class Skip:
    what: str          # normalised copy-block label, e.g. "kokomi/summon"
    path: str          # the absent source directory, as printed
    line: int


def parse_log(text: str) -> tuple[list[Fallback], list[Skip]]:
    """Pull the fallback and skip lines out of a captured build log.

    Deliberately substring-driven rather than regex-driven: the message text
    is a build-script literal that could gain a colour code or a prefix, and a
    strict anchored regex would then silently match nothing -- which reads as
    "no fallbacks happened".
    """
    fallbacks: list[Fallback] = []
    skips: list[Skip] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if _FALLBACK_PREFIX in line and " <- " in line:
            head, _, tail = line.partition(_FALLBACK_PREFIX)
            resource, _, source = tail.partition(" <- ")
            into = head.split()[-1] if head.split() else ""
            if into and resource and source:
                fallbacks.append(
                    Fallback(into, _normalise(resource), source.strip(), number)
                )
            continue
        if line.startswith(_SKIP_PREFIX):
            body = line[len(_SKIP_PREFIX):]
            what, _, path = body.partition(_SKIP_SEPARATOR)
            skips.append(Skip(_normalise(what), path.strip(), number))
    return fallbacks, skips


def load_policy(path: Path) -> dict:
    """Read a policy file. YAML when PyYAML is available, JSON otherwise."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError as exc:                       # pragma: no cover
            raise SystemExit(
                f"{path} is YAML but PyYAML is not importable ({exc}). "
                "Write the policy as .json instead."
            ) from None
        return yaml.safe_load(text) or {}
    return json.loads(text or "{}")


def _policy_fallbacks(policy: dict) -> dict[tuple[str, str, str], str]:
    out: dict[tuple[str, str, str], str] = {}
    for row in policy.get("allowed_fallbacks") or []:
        key = (
            str(row.get("into", "")).lower(),
            _normalise(str(row.get("resource", ""))),
            str(row.get("from", row.get("source", ""))).lower(),
        )
        out[key] = str(row.get("reason", "")).strip()
    return out


def _policy_skips(policy: dict) -> dict[str, str]:
    return {
        _normalise(str(row.get("what", ""))): str(row.get("reason", "")).strip()
        for row in (policy.get("allowed_skips") or [])
    }


def check(
    text: str,
    policy: dict,
    source: str = "<log>",
    require_build_markers: bool = True,
) -> Report:
    report = Report(GATE)
    lines = text.splitlines()
    report.checked["log_lines"] = len(lines)

    if require_build_markers and "Stamped build id" not in text:
        report.error(
            "FB-NOT-A-BUILD-LOG", source,
            "log carries no 'Stamped build id' line, so it is not a complete "
            "tools/build_pck.ps1 run. Reading 'no fallbacks' out of a log "
            "that never reached the fallback blocks is exactly the false "
            "clean this gate exists to prevent.",
        )

    fallbacks, skips = parse_log(text)
    report.checked["fallbacks"] = len(fallbacks)
    report.checked["skips"] = len(skips)

    allowed = _policy_fallbacks(policy)
    seen_fallbacks: set[tuple[str, str, str]] = set()
    for fallback in fallbacks:
        key = fallback.key()
        seen_fallbacks.add(key)
        if key not in allowed:
            report.error(
                "FB-UNDECLARED", f"{source}:{fallback.line}",
                f"{fallback.into} ships {fallback.resource} taken from "
                f"{fallback.source}, and no policy row allows it. A player "
                f"sees {fallback.source}'s art on {fallback.into}'s surface, "
                "and nothing else in the build says so.",
            )
        elif not allowed[key]:
            report.warning(
                "FB-NO-REASON", f"{source}:{fallback.line}",
                f"{fallback.into} <- {fallback.source} for "
                f"{fallback.resource} is allowed by a policy row that gives "
                "no reason. An allowlist without reasons is a list of things "
                "nobody can retire.",
            )
    for key, reason in sorted(allowed.items()):
        if key not in seen_fallbacks:
            into, resource, source_char = key
            report.error(
                "FB-STALE", source,
                f"policy allows {into} <- {source_char} for {resource} "
                f"({reason or 'no reason given'}) but the build produced no "
                "such fallback. Either the art landed and the row should go, "
                "or the copy block that used to fire no longer runs.",
            )

    allowed_skips = _policy_skips(policy)
    seen_skips = {skip.what for skip in skips}
    for skip in skips:
        if skip.what not in allowed_skips:
            report.error(
                "SK-UNDECLARED", f"{source}:{skip.line}",
                f"copy block {skip.what!r} was skipped (no source at "
                f"{skip.path}); those resources are NOT in the pck and no "
                "policy row declares the absence.",
            )
    for what, reason in sorted(allowed_skips.items()):
        if what not in seen_skips:
            report.error(
                "SK-STALE", source,
                f"policy allows skipping {what!r} ({reason or 'no reason given'}) "
                "but the build did not skip it. The art is there now; drop the row.",
            )
    return report


def run(
    log_path: Path,
    policy_path: Path | None,
    root: Path,
    require_build_markers: bool = True,
) -> Report:
    if not log_path.is_file():
        report = Report(GATE)
        report.error("FB-NO-LOG", str(log_path), "build log does not exist.")
        return report
    policy: dict = {}
    if policy_path is not None:
        if not policy_path.is_file():
            report = Report(GATE)
            report.error("FB-NO-POLICY", str(policy_path),
                         "policy file does not exist.")
            return report
        policy = load_policy(policy_path)
    try:
        where = log_path.relative_to(root).as_posix()
    except ValueError:
        where = log_path.as_posix()
    report = check(
        log_path.read_text(encoding="utf-8", errors="replace"),
        policy,
        source=where,
        require_build_markers=require_build_markers,
    )
    if policy_path is None:
        report.note(
            "FB-NO-POLICY-FILE", where,
            "no --policy given, so the empty policy was used: EVERY observed "
            "fallback and skip is reported. That is the strictest reading and "
            "the right default; it is not the same as a curated policy.",
        )
    return report

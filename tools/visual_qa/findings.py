"""One finding shape and one report shape for every gate in this package.

Two properties the gates in this repo have earned the hard way and that this
module makes structural rather than optional:

  * **An empty sweep is a failure, not a pass.** validate.ps1 S8 scanned a
    directory containing zero .ps1 files for its entire life and passed every
    run; S12 says the same thing about a reference sweep that finds nothing.
    Every gate here therefore reports how many things it actually looked at
    (`Report.checked`), and every gate that can be pointed at an empty input
    raises its own `*-EMPTY-SWEEP` finding rather than returning clean.
  * **Severity is declared, never inferred from the message.** `ERROR` fails
    the gate; `WARNING` is printed and fails only under `--strict`; `NOTE` is
    never a failure and exists so a gate can say what it deliberately did not
    check (a stated known-limit, the S12 pattern).
"""

from __future__ import annotations

from dataclasses import dataclass, field

ERROR = "error"
WARNING = "warning"
NOTE = "note"

_ORDER = {ERROR: 0, WARNING: 1, NOTE: 2}


@dataclass(frozen=True)
class Finding:
    """One thing a gate noticed.

    `rule` is a short stable id (``SD-ANIM-MISSING``). It is the handle a
    suppression, a debt list, or a bug report names, so it must not change
    when the message text does.

    `where` is the most specific location the gate can name -- a repo-relative
    path, a path plus line, a log line number, or a resource path. It is free
    text on purpose: a log line and a scene node do not share a coordinate
    system.
    """

    gate: str
    rule: str
    severity: str
    where: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.rule} {self.where}: {self.detail}"


@dataclass
class Report:
    """The result of running one gate."""

    gate: str
    findings: list[Finding] = field(default_factory=list)
    #: what the gate looked at, e.g. {"scenes": 8, "resources": 126}. Printed
    #: on every run, pass or fail -- a gate that reports "0 scenes, OK" is
    #: telling you it did nothing, and that has to be visible without reading
    #: the source.
    checked: dict[str, int] = field(default_factory=dict)

    def add(self, rule: str, severity: str, where: str, detail: str) -> Finding:
        finding = Finding(self.gate, rule, severity, where, detail)
        self.findings.append(finding)
        return finding

    def error(self, rule: str, where: str, detail: str) -> Finding:
        return self.add(rule, ERROR, where, detail)

    def warning(self, rule: str, where: str, detail: str) -> Finding:
        return self.add(rule, WARNING, where, detail)

    def note(self, rule: str, where: str, detail: str) -> Finding:
        return self.add(rule, NOTE, where, detail)

    def extend(self, other: "Report") -> None:
        self.findings.extend(other.findings)
        for key, value in other.checked.items():
            self.checked[key] = self.checked.get(key, 0) + value

    def count(self, severity: str) -> int:
        return sum(1 for f in self.findings if f.severity == severity)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == ERROR]

    def failed(self, strict: bool = False) -> bool:
        if self.count(ERROR):
            return True
        return bool(strict and self.count(WARNING))

    def render(self, verbose: bool = False) -> str:
        """Human-readable block. Sorted by severity, then rule, then location.

        NOTEs are hidden unless `verbose`: they are the gate saying what it
        chose not to check, which is worth having on demand and is noise on
        every run.
        """
        shown = [f for f in self.findings if verbose or f.severity != NOTE]
        lines = [
            "{}: {} finding(s) [{} error, {} warning, {} note]  checked: {}".format(
                self.gate,
                len(self.findings),
                self.count(ERROR),
                self.count(WARNING),
                self.count(NOTE),
                ", ".join(f"{k}={v}" for k, v in sorted(self.checked.items()))
                or "nothing",
            )
        ]
        for finding in sorted(
            shown, key=lambda f: (_ORDER[f.severity], f.rule, f.where)
        ):
            lines.append("  " + str(finding))
        return "\n".join(lines)

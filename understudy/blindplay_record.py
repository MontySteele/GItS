"""What a finished session leaves behind: the audit and the sealed record.

Cut out of `blindplay.py` by `EB-180`: the provenance reads (which mod
build, which game build, which arms), the leak audit over what the
tester was actually shown, and the two halves `seal` writes.
Re-exported from `blindplay.py`, so `blindplay.seal(...)` and
`blindplay.build_version()` still resolve.

`LOCAL_PROPS` stays on `blindplay.py` and is read back off it at call
time (`_bp`): it is the path a caller reaches in and swaps, so it has
ONE home and a copy bound here at import would never see the swap.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from understudy import qa_packet

from understudy.blindplay_read import _int, _text
from understudy.blindplay_shape import RECORD_ROOT


def _bp():
    """`understudy.blindplay` itself, imported at CALL time.

    `LOCAL_PROPS` is declared on the facade because that is where a caller
    reaches in and swaps it. Binding it here at import would take a private
    copy and the swap would never be seen.
    """
    from understudy import blindplay
    return blindplay


def _game_dir() -> Path | None:
    try:
        text = _bp().LOCAL_PROPS.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"<GameDir>([^<]+)</GameDir>", text)
    return Path(m.group(1).strip()) if m and m.group(1).strip() else None


def _json_field(path: Path, key: str) -> str:
    try:
        # `deploy.ps1` writes the manifest through PowerShell, which stamps a
        # UTF-8 BOM; `utf-8-sig` reads it either way.
        blob = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return ""
    return _text(blob.get(key)) if isinstance(blob, dict) else ""


def build_version(wire: Any = None) -> tuple[str, str]:
    """`(mod build, where it was read)` for the DEPLOYED package. Never guessed.

    `EB-174`. This used to read the bridge's health payload, which carries the
    VENDORED bridge's own version (`v0.4.0`) and has never carried ours -- so
    every sealed record's identity block read `(not read)`, on a document
    whose whole purpose is provenance. The honest source is the package that
    is actually installed: `<GameDir>\\mods\\klee\\manifest.json`, whose
    producer is `klee-mod\\build\\deploy.ps1` and whose `version` is the
    string the deploy stamped (`MAJOR.AUTO`, R214, with `+proto` beside it
    where `deploy_proto.ps1` built it).

    Read off DISK rather than off the wire on purpose: the file is what a
    person would open to answer "which build was this", and a record that
    names a build nobody can find on the machine is not provenance. `wire` is
    accepted and ignored so the call site does not have to know that.
    """
    game = _game_dir()
    if game is None:
        return "", (f"no GameDir in {_bp().LOCAL_PROPS.name}, so the deployed "
                    f"package cannot be found")
    manifest = game / "mods" / "klee" / "manifest.json"
    version = _json_field(manifest, "version")
    if version:
        return version, "the deployed `mods\\klee\\manifest.json` `version`"
    return "", (f"no `version` in {manifest}" if manifest.is_file()
                else f"no deployed package at {manifest}")


def granted_arms(seed: str, log_dir: Path | None = None) -> tuple[str, str]:
    """`(arms granted into this run's deck, where it was read)`. EB-188.

    A blind whole-fight run cannot DRAW a prototype row -- the surface is
    quarantined out of every pool -- so `understudy/embark.py --arm` grants it
    into the starting deck before the tester sees a screen. A record that did
    not name the grant would describe a deck the generators never produced as
    though they had, which is the claim `bridge.GRANT_GUARDRAIL` exists to
    refuse.

    MATCHED BY SEED, and that is the whole of the honesty here. The sidecar is
    written by whichever process opened the run, and this may be a different
    process on a different day; the seed is the run's identity (R95), so a
    sidecar whose seed is not this run's is a record of a DIFFERENT run and
    its arms are not reported. Read off disk like the two version reads above,
    and for the same reason -- this module may never import the operator side.

    Answers `("(none)", ...)` when nothing matches, which is a positive
    statement rather than a gap: the run met only what the pools offered.
    """
    d = log_dir or (Path(__file__).resolve().parent / "logs")
    none = ("(none)", "no `--arm` grant recorded against this run's seed")
    if not seed or not d.is_dir():
        return none
    for path in sorted(d.glob("embark-*.json"), reverse=True):
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):                         # noqa: PERF203
            continue
        if not isinstance(blob, dict) or _text(blob.get("run_seed")) != seed:
            continue
        granted = blob.get("arms_granted") or []
        if not granted:
            return none
        named = ", ".join(_text(g.get("card_id")) for g in granted)
        return named, f"the embark sidecar `{path.name}`, matched by run seed"
    return none


def game_version(wire: Any = None) -> tuple[str, str]:
    """`(game build, where it was read)`. Never guessed.

    The other half of `EB-174`: a record has to name the GAME too, because a
    live number was never comparable across a game build (R95) and the pin
    moved under this tool once already (R218, v0.107.1 -> v0.111.0 mid-sitting).

    `release_info.json` in the install root is the game's own statement of its
    version, and it is the first of the four facts
    `operations/understudy-seats.md` names for
    confirming a pin. Cheaper and steadier than the two alternatives: reading
    `release=v...` out of `godot.log` means scanning a file that reaches
    gigabytes on a bad run, and Steam's `appmanifest` buildid names a build
    without naming a version.
    """
    game = _game_dir()
    if game is None:
        return "", (f"no GameDir in {_bp().LOCAL_PROPS.name}, so the "
                    f"install root "
                    f"cannot be found")
    info = game / "release_info.json"
    version = _json_field(info, "version")
    if version:
        return version, "the game's own `release_info.json` `version`"
    return "", (f"no `version` in {info}" if info.is_file()
                else f"no `release_info.json` at {info}")


# --------------------------------------------------------- the leak audit --

# The seed is added per-session; these are the standing extra rules, ON TOP of
# `qa_packet.FORBIDDEN`, which the render already enforces at write time.
#
# WHY AN AUDIT AT ALL WHEN THE RENDER ALREADY SCRUBS. Because "the scrubber
# ran" and "no observation carried a leak" are different claims, and only the
# second one is `EB-167`'s acceptance. The scrubber is a belt on the render
# path; this is a brace read back off what was ACTUALLY SHOWN to the tester --
# every `turn-*/prompt.md`, the exact bytes `codex exec` was handed. A scrubber
# that silently stopped running would still leave this audit able to say so.
#
# The four extra patterns are the SIM's vocabulary rather than the sheet's.
# `qa_packet` guards ids, rulings and sheet fields; a prompt that said "policy"
# or "EV" or "counterfactual" would be leaking the pilot's reasoning instead,
# which is the specific thing R217 E forbids by naming `harness state` as the
# endpoint this tool may never build on.
AUDIT_EXTRA: tuple[tuple[str, str], ...] = (
    ("pilot-vocabulary-policy", r"\bpolicy\b"),
    ("pilot-vocabulary-score", r"\bscores?\b|\bscoring\b"),
    ("pilot-vocabulary-ev", r"\bEV\b|\bexpected value\b"),
    ("pilot-vocabulary-counterfactual", r"\bcounterfactual\b"),
    ("pilot-vocabulary-pilot", r"\bpilot\b"),
)


def leak_audit(log_dir: Path, seed: str = "") -> dict[str, Any]:
    """Scan every observation actually shown to the tester. Never writes.

    Returns `{observations, rules: {rule: count}, offenders: [(file, rule,
    hit, context)], total}`. An empty `rules` map with a non-zero
    `observations` count is the finding this is for.

    `seed` is audited as its own rule: the run seed is not design vocabulary,
    but a tester who can see it can look the run up, and R95's whole point is
    that a number is only comparable inside a labelled world.
    """
    rules: list[tuple[str, re.Pattern[str]]] = [
        (rule, pattern) for rule, pattern in qa_packet.FORBIDDEN]
    rules += [(rule, re.compile(pat, re.I)) for rule, pat in AUDIT_EXTRA]
    if seed:
        rules.append(("run-seed", re.compile(re.escape(seed), re.I)))

    counts: dict[str, int] = {}
    offenders: list[tuple[str, str, str, str]] = []
    pages = sorted(log_dir.glob("turn-*/prompt.md"))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for line in text.splitlines():
            for rule, pattern in rules:
                for m in pattern.finditer(line):
                    counts[rule] = counts.get(rule, 0) + 1
                    if len(offenders) < 40:
                        offenders.append((page.parent.name, rule, m.group(0),
                                          line.strip()[:160]))
    return {"observations": len(pages), "rules": counts,
            "offenders": offenders, "total": sum(counts.values())}


def turn_notes(log_dir: Path) -> list[tuple[str, str, str]]:
    """The tester's own per-turn sentence, off the gitignored turn pages.

    `(turn, command, thinking)` per answered turn. The blind prompt REQUIRES a
    `thinking` field on every answer and the schema enforces it, but until now
    nothing carried it into the committed record — so a record could not
    evidence a claim about what the tester said IN ADVANCE of a play, which is
    exactly what a legibility slate grades. Reads only; the material is the
    tester's own words, the same class the fight records already carry
    verbatim, and no observation text is copied out.
    """
    rows: list[tuple[str, str, str]] = []
    for reply in sorted(log_dir.glob("turn-*/reply.json")):
        try:
            data = json.loads(reply.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        rows.append((reply.parent.name, _text(data.get("command")),
                     _text(data.get("thinking"))))
    return rows


def notes_markdown(rows: list[tuple[str, str, str]]) -> str:
    """The per-turn channel as the committed record carries it."""
    out = ["## Turn by turn, in the tester's own words", "",
           "One line per answered turn: the command the tester gave and the "
           "sentence it gave for it, verbatim, off `turn-*/reply.json`. The "
           "same R217 G label rides on it as on the fight records — it is one "
           "model's account, not a measurement.", ""]
    if not rows:
        out += ["No answered turn carried a note."]
        return "\n".join(out) + "\n"
    out += ["| turn | command | the tester's sentence |", "|---|---|---|"]
    for turn, command, thinking in rows:
        note = thinking.replace("|", "\\|").replace("\n", " ").strip()
        cmd = command.replace("|", "\\|").strip()
        out.append(f"| `{turn}` | `{cmd}` | {note} |")
    return "\n".join(out) + "\n"


def read_snapshots(path: Path) -> list[dict[str, Any]]:
    """The wire snapshots of a finished session, from either half.

    `EB-216`. A grader is handed one of two directories and should not have to
    care which: the GITIGNORED log dir (`wire.jsonl`, which is what every
    committed `review/qa/blindplay/*/grade.py` is pointed at, beside the
    `turn-*/` pages they already read) or the COMMITTED record dir
    (`wire.json`, which is what survives the log being swept). A directory
    with neither answers with nothing rather than raising: a session sealed
    before this channel existed has no snapshots, and that is a fact about the
    session, not an error in the reader.
    """
    jsonl = path / "wire.jsonl"
    if jsonl.is_file():
        rows = []
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows
    blob = path / "wire.json"
    if blob.is_file():
        data = json.loads(blob.read_text(encoding="utf-8"))
        return [r for r in (data.get("snapshots") or [])
                if isinstance(r, dict)]
    return []


def meter_plays(snapshots: list[dict[str, Any]],
                meter: str = "spark") -> list[dict[str, Any]]:
    """Every ledger row for one meter, flattened out of the snapshots.

    `EB-216` / R225's clause: the per-play `{card, before, price_paid, gains
    {source: n}, after}` a grader counts against. The snapshot a row rides on
    is carried through as `snapshot` and `turn`, because a play is only
    interesting beside the board it was made on.

    NOTHING PUBLISHED IS RE-GRADED THROUGH THIS (R101b, R224 A). It is the
    read the NEXT run's slate has; a record sealed before the channel existed
    has no rows and stays exactly as it was graded.

    `meter` is a parameter for the reason it is a field on the mod side:
    Charge and Encore are the same shape and will want the same counts.
    """
    out = []
    for snap in snapshots:
        for row in (snap.get("ledger") or []):
            if not isinstance(row, dict):
                continue
            if meter and _text(row.get("meter")) != meter:
                continue
            out.append({**row, "snapshot": _int(snap.get("index")),
                        "turn": _int(row.get("turn", snap.get("turn")))})
    return out


def audit_markdown(audit: dict[str, Any]) -> str:
    """The audit as the committed record carries it."""
    out = ["## Leak audit", "",
           f"Every observation the tester was actually shown — "
           f"`turn-*/prompt.md`, the exact bytes handed to `codex exec` — "
           f"scanned against `qa_packet.FORBIDDEN` plus the pilot-vocabulary "
           f"rules and this run's seed.", "",
           f"- **observations scanned**: {audit['observations']}",
           f"- **total hits**: {audit['total']}"]
    if audit["rules"]:
        out += ["", "| rule | hits |", "|---|---|"]
        out += [f"| `{r}` | {n} |" for r, n in sorted(audit["rules"].items())]
        out += ["", "Offenders (first 40):", ""]
        out += [f"- `{d}` — `{r}` matched `{hit}` in: {ctx}"
                for d, r, hit, ctx in audit["offenders"]]
    else:
        out += ["", "No rule matched in any observation."]
    return "\n".join(out) + "\n"


def record_markdown(summary: dict[str, Any], identity: dict[str, Any]) -> str:
    """The COMMITTED half: identity, then the model's words verbatim."""
    out = [f"# Blind play session `{summary['session_id']}`", "",
           "**R217 G — subjective feedback from an independent model playing "
           "the real game. Useful for iteration; not human validation, not "
           "balance evidence, not approval. It never enters an Understudy "
           "report, a win-rate table or a measurement register.**", "",
           "## Identity", ""]
    for key in ("model_requested", "model_observed",
                # The LOCAL backend's four, and they are absent from a codex
                # run's identity entirely, so a codex record is byte-identical
                # to what this function has always written. `seat_family` is
                # the VENDOR family R217 C is read off, which the authorship
                # family (`local`) names a chair rather than answering;
                # `blindness` says out loud that this backend's claim is
                # structural where the codex seat's is transcript-proved.
                "backend", "seat_family", "endpoint",
                "server_version", "server_version_source",
                "schema_enforced", "blindness", "seat_status",
                "codex_version",
                "build_version", "build_version_source",
                "game_version", "game_version_source", "run_seed",
                "arms_granted", "arms_granted_source",
                "prompt_sha256", "actions", "termination",
                # `EB-229`. Present only where a registration switched the
                # forecast channel on, so nothing moves on a run that did not.
                "forecast_asked"):
        if key in identity:
            out.append(f"- **{key}**: {identity[key] or '(not read)'}")
    out += ["", f"- **guardrail**: {summary['guardrail']}", ""]
    # `EB-216`. The record NAMES the machine channel and does not inline it:
    # `wire.json` is a board, not prose, and a reader who wants a count wants
    # the file rather than a table of it. The count is here so a missing file
    # is visible from the record alone.
    if summary.get("wire") is not None:
        out += [f"- **wire snapshots**: {len(summary['wire'])} in "
                f"`wire.json` beside this file — one row per play and per "
                f"end turn, machine-written off the API and never shown to "
                f"the tester (`EB-216`, R101b)", ""]
    # `EB-229`. The forecasts are on the COMMITTED half, because they are the
    # thing a registration that asked for them has to count, and the
    # gitignored log is swept. Absent entirely on a run that asked for none.
    if summary.get("forecast_questions"):
        rows = summary.get("forecasts") or []
        short = len([r for r in rows if r.get("short")])
        out += ["## Forecasts, stated in advance", "",
                "One row per combat turn the tester was asked on, written "
                "BEFORE its command and never graded here (`EB-229`).", "",
                f"- **asked on**: {len(rows)} turns, "
                f"{short} of them answered short", ""]
        out += [f"{i}. {q}"
                for i, q in enumerate(summary["forecast_questions"], 1)]
        out += ["", "| action | " + " | ".join(
            f"answer {i}" for i in range(
                1, len(summary["forecast_questions"]) + 1)) + " |",
            "|---" * (len(summary["forecast_questions"]) + 1) + "|"]
        for r in rows:
            cells = list(r.get("answers") or [])
            cells += [""] * (len(summary["forecast_questions"]) - len(cells))
            out.append(f"| {r.get('action')} | " + " | ".join(
                str(c).replace("|", "\\|").replace("\n", " ")
                for c in cells) + " |")
        out.append("")
    for i, text in enumerate(summary["fight_records"], 1):
        out += [f"## Fight {i}, in the tester's own words", "", text.rstrip(),
                ""]
    if summary["run_record"]:
        out += ["## The run, in the tester's own words", "",
                summary["run_record"].rstrip(), ""]
    return "\n".join(out).rstrip() + "\n"


def seal(summary: dict[str, Any], identity: dict[str, Any], *,
         log_dir: Path, record_root: Path | None = None) -> Path:
    """Write both halves. The gitignored one first, the committed one after."""
    (log_dir / "session.json").write_text(
        json.dumps({**summary, **identity}, indent=1, default=str) + "\n",
        encoding="utf-8")
    for i, text in enumerate(summary["fight_records"], 1):
        (log_dir / f"fight-{i:02d}.md").write_text(text, encoding="utf-8")
    if summary["run_record"]:
        (log_dir / "run.md").write_text(summary["run_record"],
                                        encoding="utf-8")
    out = (record_root or RECORD_ROOT) / summary["session_id"]
    out.mkdir(parents=True, exist_ok=True)
    # `EB-216`. BOTH SIDES GET IT, and for the reason the graders are written
    # the way they are: every `review/qa/blindplay/*/grade.py` takes the
    # GITIGNORED log dir as its argument and reads the run's own artefacts out
    # of it, while the committed half is what survives the log being swept. It
    # is the same rows either way.
    rows = summary.get("wire") or []
    (log_dir / "wire.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n"
                for r in rows), encoding="utf-8")
    (out / "wire.json").write_text(
        json.dumps({"session_id": summary["session_id"],
                    "snapshots": rows}, indent=1, default=str) + "\n",
        encoding="utf-8")
    path = out / "record.md"
    path.write_text(record_markdown(summary, identity), encoding="utf-8")
    return path

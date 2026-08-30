#!/usr/bin/env python3
"""EB-225 (R225 item 6, M66 pick 2): every prototype Harmony patch is
character-scoped and seat-guarded.

THE SHAPE THIS GENERALISES IS `d217b4f`. `KurageMemoryCard`'s
`NCombatUi.Deactivate` postfix asked the combat it still held for the local
seat. `LocalContext.GetMe(ICombatState)` is not the null-answering lookup it
reads as -- no `NetId` answers null, but a MISS THROWS
`InvalidOperationException("Local player not found in combat.")` -- and
`NCombatRoom._Ready` runs that postfix while the NEXT room is still being
built and holds no seats yet. The throw escaped `_Ready`, the room never
finished readying, the gauge spawn then NRE'd on a null vfx container, and the
fight never started at all. Two whole-fight blind sessions (`KLEESPARK-W1`,
`KLEESPARK-W2`) ended at the first frame of their second Monster room, and
`understudy.soak`'s policy bot reproduced it with no arm and no Codex in it.
The fix was a `TryGetMe` guard plus a bridge degrade.

WHY A LINT AND NOT A REVIEW HABIT. R225 kept the SINGLE `PROTOTYPE_CARDS`
switch (M66 pick 2) over splitting it per arm. That is the cheap answer to a
quarantine, and its whole cost is cross-arm breakage: one flag compiles
Kokomi's Kurage memory AND Klee's Sparks, so a Kokomi patch that runs on a
Klee seat -- or on no seat at all -- takes down a run that has nothing to do
with the arm being tried. It has been witnessed twice (`EB-194`, `EB-221`).
The guard the single switch does not buy is bought here instead, and it is
bought MECHANICALLY, because the two defects both looked like working code:
a postfix with no character test reads exactly like a postfix, and an
unguarded `GetMe` reads exactly like a null-safe lookup.

THE TWO RULES, on every Harmony patch under the three `Compile Remove`
prototype directories (`KleeCode.csproj`):

  (a) CHARACTER SCOPE. The patch returns early unless the creature it is about
      belongs to the arm's character. The accepted spellings are an ALLOWLIST
      of expressions (`SCOPE_IDIOMS`) rather than a regex over everything --
      the identity predicates the mod already owns, plus the interface tests
      they are made of. A new spelling is a row there, added deliberately;
      it must not be something a patch can drift into by accident.

  (b) SEAT GUARD. Every resolution of the local seat goes through the guarded
      form. `LocalContext.GetMe(` is red on this surface unless it sits inside
      a `try` -- which is exactly `KurageMemoryCard.TryGetMe`'s body and
      `SelectionTelemetry`'s shape, the two places that already had it right.
      `TryGetMe(` and `LocalContext.IsMe(` are guarded by construction.

BOTH RULES READ THROUGH THE PATCH'S OWN CALLS, not just its body. Every patch
in this tree is a two-line postfix that delegates -- `Postfix() =>
KurageMemoryCard.DiscardAll(...)` -- so a lint that read only the method body
would find nothing on every patch and nothing on the one that took the runs
down. The effective body is the transitive closure over same-file methods the
patch names (`FOLLOW_DEPTH`), which is where `DiscardAll -> TryGetMe` lives.
The closure is same-FILE on purpose: it is the unit an author edits in one
sitting, and following further would turn a lint into a call-graph analysis
that is wrong in a way nobody can see.

EXEMPTION, AND IT IS VISIBLE. A patch that touches neither a run nor a seat --
a pure static teardown, say -- is exempt only through an explicit
`// lint: no-seat: <reason>` marker in the patch class. Every marker in the
tree is PRINTED on every run, pass or fail, so an exemption cannot become
invisible by being correct. A marker with no reason is itself a finding.

WHAT THIS DOES NOT DO. It does not look at shipped (non-prototype) patches.
The rule is bought for the quarantine, where a defect crosses arms under one
flag; a shipped patch has its own reviewers and its own release gate, and
widening the walk here without widening the ALLOWLIST first would produce a
wall of findings that says one structural thing.

Run: python tools/lint_prototype_patch_scope.py
     python tools/lint_prototype_patch_scope.py --self-test   # prove it bites
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The three `Compile Remove` directories of KleeCode.csproj, in its order.
PROTOTYPE_DIRS: tuple[str, ...] = (
    "klee-mod/KleeCode/Cards/Prototype",
    "klee-mod/KleeCode/Powers/Prototype",
    "klee-mod/KleeCode/Vfx/Prototype",
)

# (a) The accepted CHARACTER SCOPE spellings. An allowlist, not a pattern:
# each row is a predicate the mod already owns and whose whole job is "is this
# creature the arm's character".
#
#   * `KokomiResources.IsKokomi` / `FurinaResources.IsFurina` are the identity
#     predicates themselves (`Player.Character is I<X>Character`);
#   * `KurageMemory.IsLive` / `BaseKitLive` are Kokomi's arm gate, whose whole
#     body is `IsKokomi` plus the arm's own switch;
#   * the raw `is [not] I<X>Character` tests are what those are made of, and
#     are accepted so a patch in a file that cannot reach the resources class
#     is not pushed into a worse spelling;
#   * `Powers.OfType<SparkAttackCostPower>` is the Sparks arm's scope: the
#     power is granted to one character, so its PRESENCE on the owner is the
#     character test. Named explicitly rather than accepting `OfType<` at
#     large, which would let any power stand in for an identity check.
SCOPE_IDIOMS: tuple[str, ...] = (
    "KokomiResources.IsKokomi(",
    "FurinaResources.IsFurina(",
    "KurageMemory.IsLive(",
    "KurageMemory.BaseKitLive(",
    "is IKokomiCharacter",
    "is not IKokomiCharacter",
    "is IFurinaCharacter",
    "is not IFurinaCharacter",
    "is IKleeCharacter",
    "is not IKleeCharacter",
    "Powers.OfType<SparkAttackCostPower>",
)

# (b) The seat accessors. RAW throws on a combat with no local seat (see the
# module docstring); GUARDED are the two forms that cannot.
RAW_SEAT: tuple[str, ...] = ("LocalContext.GetMe(", "LocalContext.Me")
GUARDED_SEAT: tuple[str, ...] = ("TryGetMe(", "LocalContext.IsMe(")

# Harmony's method names when the class carries the `[HarmonyPatch]`.
PATCH_METHOD_NAMES = frozenset(
    {"Prefix", "Postfix", "Transpiler", "Finalizer", "ILManipulator"})

PATCH_METHOD_ATTRS = ("[HarmonyPrefix", "[HarmonyPostfix", "[HarmonyTranspiler",
                      "[HarmonyFinalizer", "[HarmonyReversePatch")

# How far the effective body follows same-file calls. Four is the deepest
# chain this tree has (`Postfix -> DiscardAll -> TryGetMe -> LocalContext`)
# with room for one more hop; unbounded following buys nothing here and makes
# a finding hard to argue with.
FOLLOW_DEPTH = 4

# `[ \t]` and not `\s` throughout: `\s` crosses the newline, and a marker with
# no reason then swallows the `[HarmonyPatch]` line below it as its reason --
# which is precisely the "silent exemption" this marker exists to prevent.
MARKER_RE = re.compile(
    r"//[ \t]*lint:[ \t]*no-seat[ \t]*[:\-]?[ \t]*(?P<reason>[^\n]*)", re.I)

# A declaration is a modifier run, a return type, a name, a parenthesised
# parameter list, then either a block or an expression body. The modifier run
# is REQUIRED, which is what keeps `if (...) {` and every call site out; the
# cost is that a modifier-less local function is not seen, and there are none
# on this surface.
_MODS = (r"(?:public|private|protected|internal|static|async|override|sealed"
         r"|virtual|new|partial|extern|unsafe|readonly)")
# The return type is one lazy negated class rather than a token grammar
# (`[\w<>,\.]+(?:\s*[\w<>,\.]+)*?`): the token form has a nested unbounded
# quantifier and backtracks catastrophically on a 1200-line file -- the first
# run of this lint did not terminate. A single character class cannot.
MEMBER_RE = re.compile(
    r"(?m)^[ \t]*(?:" + _MODS + r"\s+)+"
    r"[^;{}()\n=]+?\s+"
    r"(?P<name>\w+)[ \t]*"
    r"\((?s:[^;{}]*?)\)[ \t\r\n]*"
    r"(?P<sep>=>|\{)")

TYPE_RE = re.compile(
    r"(?m)^[ \t]*(?:(?:public|private|protected|internal|static|sealed"
    r"|abstract|partial|readonly|ref)\s+)*"
    r"(?:class|struct|record)\s+(?P<name>\w+)")

WORD_RE = re.compile(r"\b\w+\b")

MANUAL_PATCH_RE = re.compile(r"\.Patch\s*\(")


# ------------------------------------------------------------- lexing --


def code_only(text: str) -> str:
    """`text` with comments and literals blanked, offsets and lines preserved.

    Every expression match below runs on this. The reason is one line of
    `KurageMemoryCard`'s own docstring, which names `LocalContext.GetMe(
    ICombatState)` while EXPLAINING why it must not be called -- a lint that
    read prose would report the comment that fixed the defect.
    """
    out = list(text)
    i, n = 0, len(text)

    def blank(a: int, b: int) -> None:
        for k in range(a, min(b, n)):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        ch = text[i]
        two = text[i:i + 2]
        if two == "//":
            j = text.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif two == "/*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            blank(i, j)
            i = j
        elif two in ('@"', '$"') or ch == '"':
            verbatim = two == '@"'
            j = i + (2 if two in ('@"', '$"') else 1)
            while j < n:
                if verbatim:
                    if text[j] == '"':
                        if text[j:j + 2] == '""':
                            j += 2
                            continue
                        j += 1
                        break
                else:
                    if text[j] == "\\":
                        j += 2
                        continue
                    if text[j] == '"':
                        j += 1
                        break
                    if text[j] == "\n":
                        break
                j += 1
            blank(i, j)
            i = j
        elif ch == "'":
            j = i + 1
            while j < n and text[j] != "'":
                j += 2 if text[j] == "\\" else 1
            blank(i, min(j + 1, n))
            i = min(j + 1, n)
        else:
            i += 1
    return "".join(out)


def match_block(code: str, brace: int) -> int:
    """Index just past the `}` closing the `{` at `brace`."""
    depth, i, n = 0, brace, len(code)
    while i < n:
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def match_expression(code: str, arrow: int) -> int:
    """Index just past the `;` ending an expression body starting at `=>`."""
    depth, i, n = 0, arrow, len(code)
    while i < n:
        c = code[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == ";" and depth <= 0:
            return i + 1
        i += 1
    return n


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def leading_trivia(text: str, index: int) -> str:
    """The attributes and comments immediately above the declaration."""
    start = text.rfind("\n", 0, index) + 1
    lines: list[str] = []
    while start > 0:
        prev_start = text.rfind("\n", 0, start - 1) + 1
        line = text[prev_start:start - 1]
        stripped = line.strip()
        if stripped and not (stripped.startswith("[")
                             or stripped.startswith("//")
                             or stripped.startswith("]")):
            break
        lines.append(line)
        start = prev_start
    return "\n".join(reversed(lines))


# ------------------------------------------------------------ parsing --


@dataclass
class Member:
    name: str
    start: int          # index of the declaration
    body_start: int
    body_end: int
    trivia: str

    def body(self, code: str) -> str:
        return code[self.body_start:self.body_end]


@dataclass
class PatchUnit:
    path: str
    line: int
    name: str
    member: Member
    kind: str                            # "attribute" | "manual"
    class_span: tuple[int, int]
    marker: str | None = None            # the exemption reason, if any
    marker_line: int = 0
    reached: list[Member] = field(default_factory=list)


def members(code: str, text: str) -> list[Member]:
    out: list[Member] = []
    for m in MEMBER_RE.finditer(code):
        if m.group("sep") == "{":
            b0 = code.index("{", m.end() - 1)
            out.append(Member(m.group("name"), m.start(), b0,
                              match_block(code, b0), leading_trivia(text, m.start())))
        else:
            a0 = m.end() - 2
            out.append(Member(m.group("name"), m.start(), a0,
                              match_expression(code, a0),
                              leading_trivia(text, m.start())))
    return out


def types(code: str, text: str) -> list[tuple[str, int, int, str]]:
    out: list[tuple[str, int, int, str]] = []
    for m in TYPE_RE.finditer(code):
        brace = code.find("{", m.end())
        if brace < 0:
            continue
        out.append((m.group("name"), m.start(), match_block(code, brace),
                    leading_trivia(text, m.start())))
    return out


def scan_source(text: str, label: str) -> list[PatchUnit]:
    """Every Harmony patch in one C# file, with its effective body resolved."""
    code = code_only(text)
    all_members = members(code, text)
    by_name: dict[str, list[Member]] = {}
    for mem in all_members:
        by_name.setdefault(mem.name, []).append(mem)

    units: list[PatchUnit] = []
    seen: set[int] = set()

    def enclosing(index: int) -> Member | None:
        best: Member | None = None
        for mem in all_members:
            if mem.body_start <= index < mem.body_end:
                if best is None or mem.body_start > best.body_start:
                    best = mem
        return best

    def add(mem: Member, cls: str, span: tuple[int, int], kind: str,
            cls_trivia: str, cls_index: int) -> None:
        if mem.start in seen:
            return
        seen.add(mem.start)
        unit = PatchUnit(label, line_of(text, mem.start),
                         f"{cls}.{mem.name}" if cls else mem.name,
                         mem, kind, span)
        hay = cls_trivia + "\n" + mem.trivia + "\n" + text[span[0]:span[1]]
        found = MARKER_RE.search(hay)
        if found:
            unit.marker = found.group("reason").strip()
            at = text.find(found.group(0))
            unit.marker_line = line_of(text, at) if at >= 0 else unit.line
        unit.reached = close_over(mem)
        units.append(unit)

    def close_over(mem: Member) -> list[Member]:
        out: list[Member] = [mem]
        frontier = [mem]
        seen_names = {mem.name}
        for _ in range(FOLLOW_DEPTH):
            nxt: list[Member] = []
            for cur in frontier:
                for word in WORD_RE.findall(cur.body(code)):
                    if word in seen_names or word not in by_name:
                        continue
                    seen_names.add(word)
                    for target in by_name[word]:
                        out.append(target)
                        nxt.append(target)
            frontier = nxt
            if not frontier:
                break
        return out

    for cls, c0, c1, trivia in types(code, text):
        if "[HarmonyPatch" not in trivia:
            continue
        for mem in all_members:
            if not (c0 <= mem.start < c1):
                continue
            if (mem.name in PATCH_METHOD_NAMES
                    or any(a in mem.trivia for a in PATCH_METHOD_ATTRS)):
                add(mem, cls, (c0, c1), "attribute", trivia, c0)

    # A method carrying its own `[HarmonyPatch]`, and manual `Harmony.Patch(`
    # call sites. Neither shape exists on this surface today; both are here
    # because the lint must not be silent on the first one that does.
    for mem in all_members:
        if "[HarmonyPatch" in mem.trivia or any(
                a in mem.trivia for a in PATCH_METHOD_ATTRS):
            add(mem, "", (mem.start, mem.body_end), "attribute", "", mem.start)
    for m in MANUAL_PATCH_RE.finditer(code):
        host = enclosing(m.start())
        if host is not None:
            add(host, "", (host.start, host.body_end), "manual", "", host.start)
    return units


# ------------------------------------------------------------ checking --


def try_spans(body: str) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for m in re.finditer(r"\btry\b[ \t\r\n]*\{", body):
        brace = m.end() - 1
        out.append((brace, match_block(body, brace)))
    return out


def unit_findings(unit: PatchUnit, text: str) -> list[str]:
    """The two rules, on one patch. `[]` when it is clean or exempt."""
    code = code_only(text)
    here = f"{unit.path}:{unit.line}: {unit.name}"

    if unit.marker is not None:
        if len(unit.marker) < 8:
            return [f"{here}: the `// lint: no-seat` marker carries no reason. "
                    f"An exemption without one is a silent exemption -- say "
                    f"what the patch touches instead of a run or a seat."]
        return []

    out: list[str] = []
    bodies = [mem.body(code) for mem in unit.reached]
    blob = "\n".join(bodies)

    if not any(idiom in blob for idiom in SCOPE_IDIOMS):
        out.append(
            f"{here}: missing (a) CHARACTER SCOPE. Nothing this patch reaches "
            f"asks whether the creature is the arm's character, so it runs on "
            f"every seat at the table under the one PROTOTYPE_CARDS switch "
            f"(EB-194, EB-221). Accepted spellings: "
            f"{', '.join(SCOPE_IDIOMS[:4])}, ... (SCOPE_IDIOMS).")

    for mem in unit.reached:
        body = mem.body(code)
        spans = try_spans(body)
        for raw in RAW_SEAT:
            for m in re.finditer(re.escape(raw), body):
                if any(a <= m.start() < b for a, b in spans):
                    continue
                out.append(
                    f"{unit.path}:{line_of(text, mem.body_start + m.start())}: "
                    f"{unit.name} (via {mem.name}): missing (b) SEAT GUARD. "
                    f"`{raw}` THROWS on a combat with no local seat, and "
                    f"`NCombatRoom._Ready` runs teardown patches on exactly "
                    f"that combat (d217b4f). Use the guarded form "
                    f"({' or '.join(GUARDED_SEAT)}) or wrap it in a try.")
    return out


def sources(roots: list[Path] | None = None) -> list[Path]:
    dirs = roots if roots is not None else [REPO / d for d in PROTOTYPE_DIRS]
    out: list[Path] = []
    for d in dirs:
        if d.is_dir():
            out += sorted(d.rglob("*.cs"))
    return out


def scan(roots: list[Path] | None = None
         ) -> tuple[list[str], list[str], int]:
    """`(findings, marker lines, patches examined)`."""
    hits: list[str] = []
    markers: list[str] = []
    count = 0
    for path in sources(roots):
        text = path.read_text(encoding="utf-8-sig")
        try:
            label = path.relative_to(REPO).as_posix()
        except ValueError:
            label = path.as_posix()
        for unit in scan_source(text, label):
            count += 1
            if unit.marker:
                markers.append(
                    f"{label}:{unit.marker_line}: {unit.name} exempt -- "
                    f"{unit.marker}")
            hits += unit_findings(unit, text)
    return hits, markers, count


# ---------------------------------------------------------- self-test --

_GREEN = """
using HarmonyLib;
namespace X;
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class A_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => Thing.DiscardAll(Mem.Combat);
}
internal static class Thing
{
    public static void DiscardAll(CombatState? state)
    {
        var me = TryGetMe(state);
        if (me == null || !KokomiResources.IsKokomi(me.Creature)) return;
    }
    private static Player? TryGetMe(CombatState? state)
    {
        if (state == null) return null;
        // The brace on its OWN line, which is the shipped shape: the first
        // draft of `try_spans` only accepted `try {` and reported
        // `KurageMemoryCard.TryGetMe` -- the guard the lint exists to require.
        try
        {
            return LocalContext.GetMe(state);
        }
        catch (Exception)
        {
            return null;
        }
    }
}
"""

_NO_SCOPE = _GREEN.replace(
    "if (me == null || !KokomiResources.IsKokomi(me.Creature)) return;",
    "if (me == null) return;")

_RAW_SEAT = _GREEN.replace(
    "var me = TryGetMe(state);", "var me = LocalContext.GetMe(state);")

_MARKED = """
using HarmonyLib;
namespace X;
/// <summary>Static teardown only.</summary>
// lint: no-seat: pure static teardown -- it reads no run and no seat.
[HarmonyPatch(typeof(NCardPileScreen), nameof(NCardPileScreen._ExitTree))]
internal static class B_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => Ring.Disarm();
}
"""

_MARKED_NO_REASON = _MARKED.replace(
    "// lint: no-seat: pure static teardown -- it reads no run and no seat.",
    "// lint: no-seat")

_COMMENT_ONLY = """
using HarmonyLib;
namespace X;
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class C_Patch
{
    /// <summary>`LocalContext.GetMe(state)` must never be called here.</summary>
    [HarmonyPostfix]
    public static void Postfix()
    {
        if (!KurageMemory.IsLive(Mem.Creature)) return;
        var s = "LocalContext.GetMe(x)";
    }
}
"""

FIXTURES: dict[str, tuple[str, tuple[str, ...]]] = {
    "green": (_GREEN, ()),
    "no-scope": (_NO_SCOPE, ("(a) CHARACTER SCOPE",)),
    "raw-seat": (_RAW_SEAT, ("(b) SEAT GUARD",)),
    "marked": (_MARKED, ()),
    "marked-no-reason": (_MARKED_NO_REASON, ("carries no reason",)),
    "comment-only": (_COMMENT_ONLY, ()),
}


def fixture_findings(source: str) -> list[str]:
    out: list[str] = []
    for unit in scan_source(source, "<fixture>.cs"):
        out += unit_findings(unit, source)
    return out


def _self_test() -> int:
    for name, (src, wanted) in FIXTURES.items():
        hits = fixture_findings(src)
        if not wanted:
            assert not hits, f"{name} must be clean, got {hits}"
        for want in wanted:
            assert any(want in h for h in hits), f"{name}: {want!r} not in {hits}"
        if wanted:
            assert len(hits) == len(wanted), f"{name}: {hits}"
    assert scan_source(_GREEN, "x.cs"), "the patch must be FOUND at all"
    print("lint_prototype_patch_scope: self-test OK "
          f"({len(FIXTURES)} fixture(s))")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true",
                    help="run the fixtures that prove this lint bites")
    ap.add_argument("--dir", action="append", type=Path,
                    help="scan these directories instead of the prototype "
                         "three (investigation only -- the gate is the "
                         "bare invocation)")
    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()

    hits, markers, count = scan(args.dir)
    for line in markers:
        print(f"exempt: {line}")
    for line in hits:
        print(line)
    if hits:
        print(f"\n{len(hits)} finding(s) over {count} prototype patch(es).")
        return 1
    print(f"lint_prototype_patch_scope: OK ({count} prototype patch(es), "
          f"{len(markers)} marked exempt)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

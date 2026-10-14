#!/usr/bin/env python3
"""The player hover's house rule, held on every generated card.

    python tools/lint_hover_tips.py              # the gate
    python tools/lint_hover_tips.py --census     # per-card boxes and lengths

THE TOOLTIP TRIM (2026-10-14, review/active/tooltip-trim-2026-10-14.md,
pick 1 (a)). [USER], during the 2026-10-14 Furina run: "her cards still make a
million words of tooltips come up ... so the tooltips aren't half the screen."
The house rule for a PLAYER's static hover:

  * at most `CAP_BOXES` boxes (the mod's own keyword boxes such as
    `Applies Pyro`, every tip the card's `ExtraHoverTips` raises, and a card
    preview counted as one box);
  * each box at most `CAP_CHARS` visible characters ("about 90", base-game
    style: what the word does, in one sentence).

WHAT IT READS. A generated card's `ExtraHoverTips` is either one chain or
`TipAudience.Seat ? <seat chain> : <player chain>`; the player chain is the
one measured (the seat chain is the blind seats' and keeps every rider, word
for word). Bodies are read off the C#: `PlayerTips.Bodies` where a key has
player words, the seat sentence in `ArmKeywordTips` where it does not, the
guest half `PlayerTips.Guest` picks off the face, and the Applies-X rows in
`KleeMod.cs`. A base-game tip (`BaseKeywordTips`, a card preview) is a box
of the base game's own length and is counted, not measured.

NOT COUNTED: a tip that shows only on a board in the state it names
(`ForEmptyField`, `ForElementSwitch`) or only to one owner (a Companion's
Plan line, to a Kokomi: `ForCompanionPlan`), and the reaction previews inside
`KleeCardTooltips.ForCard`, which a player sees only while aiming.

A structurally invisible defect ("structurally invisible defects" in memory):
nothing renders wrong when a hover grows a fifth box, so the cap is a lint.
"""

from __future__ import annotations

import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lint_text_conventions as tc  # noqa: E402

REPO = tc.REPO
MOD = tc.MOD
GEN = MOD / "Cards" / "Prototype" / "Generated"
ARM = MOD / "Cards" / "Prototype" / "ArmKeywordTips.cs"
PLAYER = MOD / "Cards" / "Prototype" / "PlayerTips.cs"

CAP_BOXES = 3
CAP_CHARS = 100

#: Shown only on a board in the state the tip names, or only to one owner
#: (a Companion's Plan line, to a Kokomi): not a static box.
BOARD_ONLY = frozenset({
    "ArmKeywordTips.ForEmptyField",
    "ArmKeywordTips.ForElementSwitch",
    "ArmKeywordTips.ForCompanionPlan",
})

#: Cards whose own mod keywords alone pass the cap, curated: the generator
#: can cut a tip but not a keyword the card declares. An entry that has since
#: come under the cap FAILS, so the set only shrinks.
BOX_DEBT = {
    "ProtoVkTempestOfTheFourWinds": "applies all four elements, and each "
                                    "Applies keyword is its element gem",
}

#: Long tips a ruled pick keeps, curated. An entry no card raises FAILS.
LONG_OK = {
    "YaeSakuraTip": "her shrine's rule, the strike, timer, cap and plant "
                    "Level in one tip ([USER]'s wording, 2026-10-14)",
}

_GOLD = re.compile(r"\[/?(gold|blue)\]")


def visible(text: str) -> str:
    return _GOLD.sub("", text)


def split_layers(expr: str) -> list[tuple[str, str]]:
    """`Outer(Inner(base.ExtraHoverTips, a), b)` as `[(Inner, ', a'),
    (Outer, ', b')]`. Kept independent of the generator on purpose."""
    layers: list[tuple[str, str]] = []
    expr = " ".join(expr.split())
    while expr != "base.ExtraHoverTips":
        m = re.match(r"([\w.<>]+)\(", expr)
        if not m or not expr.endswith(")"):
            raise ValueError(f"not a tip chain: {expr!r}")
        start, depth, i = m.end(), 0, m.end()
        while i < len(expr):
            c = expr[i]
            if c == "(":
                depth += 1
            elif c == ")":
                if depth == 0:
                    break
                depth -= 1
            elif c == "," and depth == 0:
                break
            i += 1
        layers.append((m.group(1), expr[i:-1]))
        expr = expr[start:i]
    return layers[::-1]


def player_chain(src: str) -> str | None:
    m = re.search(r"ExtraHoverTips =>\s*(.*?);\n", src, re.S)
    if not m:
        return None
    expr = m.group(1)
    if expr.startswith("TipAudience.Seat"):
        expr = expr.split("\n            : ", 1)[1]
    return " ".join(expr.split())


def mod_keywords(src: str) -> list[str]:
    m = re.search(r"CanonicalKeywords =>\s*(.*?);\n", src, re.S)
    if not m:
        return []
    return list(dict.fromkeys(re.findall(r"KleeKeywords\.(\w+)", m.group(1))))


def face(src: str) -> str:
    m = re.search(r'\("description", "((?:[^"\\]|\\.)*)"\)', src)
    return m.group(1) if m else ""


# --- the bodies, read off the C# --------------------------------------------

def _expr_until_comma(src: str, i: int) -> str:
    """The expression from `i` to the `,` (or `}`) that ends a dictionary
    entry, literal- and paren-aware."""
    start, depth = i, 0
    while i < len(src):
        c = src[i]
        if c == '"':
            i = tc.skip_literal(src, i)
            continue
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif c in ",}" and depth == 0:
            break
        i += 1
    return src[start:i]


def player_bodies() -> dict[str, str]:
    src = re.sub(r"^\s*//.*$", "", tc.read(PLAYER), flags=re.M)
    statics = {name: tc.csharp_text(expr) for name, expr in re.findall(
        r"static readonly string (\w+) =\s*(.*?);", src, re.S)}
    out: dict[str, str] = {}
    for m in re.finditer(r"\[ArmKeywordTips\.(\w+Key)\]\s*=\s*", src):
        expr = _expr_until_comma(src, m.end()).strip()
        out[m.group(1)] = statics.get(expr, tc.csharp_text(expr))
    spark = re.search(r"SparkBody\(bool openingBank\) =>\s*openingBank\s*"
                      r"\?\s*(.*?)\n\s*:\s*(.*?);", src, re.S)
    out["SparkKey"] = tc.csharp_text(spark.group(1))
    return out


def seat_bodies() -> dict[str, str]:
    return {row.ident: row.raw for row in tc.tip_rows()}


def method_keys() -> dict[str, str]:
    """`ForBomb` -> `BombKey`, read off each attach method's body."""
    src = tc.read(ARM)
    out: dict[str, str] = {}
    heads = list(re.finditer(
        r"public static IEnumerable<IHoverTip> (For\w+)\(", src))
    for n, m in enumerate(heads):
        end = heads[n + 1].start() if n + 1 < len(heads) else len(src)
        key = re.search(r"With\(inherited, (\w+Key)", src[m.end():end])
        if key:
            out[m.group(1)] = key.group(1)
    return out


def arm_statics() -> dict[str, str]:
    """`static readonly string` tip bodies in `ArmKeywordTips`, rendered."""
    src = re.sub(r"^\s*//.*$", "", tc.read(ARM), flags=re.M)
    return {name: tc.csharp_text(expr) for name, expr in re.findall(
        r"static readonly string (\w+) =\s*(.*?);", src, re.S)}


def annotation_rules() -> dict[tuple[str, str], str]:
    """`YaeAnnotationText.Rule` and `.SakuraRule`'s arms, rendered, keyed
    (method, member)."""
    src = tc.read(MOD / "Powers" / "Prototype" / "YaeAnnotations.cs")
    out: dict[tuple[str, str], str] = {}
    for method in ("Rule", "SakuraRule"):
        body = src[src.index(f"public static string {method}("):]
        body = body[:body.index("_ =>")]
        arms = re.split(r"YaeAnnotation\.(\w+) =>", body)[1:]
        for member, expr in zip(arms[::2], arms[1::2]):
            out[(method, member)] = tc.csharp_text(expr)
    return out


def annotation_body(args: str) -> str:
    """`ForAnnotation(..., this, YaeAnnotation.X, onSakura)`'s body, as
    `YaeAnnotationText.TipBody` picks it."""
    m = re.search(r"YaeAnnotation\.(\w+),\s*(true|false)", args)
    if not m:
        return ""
    rules = annotation_rules()
    if m.group(2) == "true" and rules.get(("SakuraRule", m.group(1))):
        return rules[("SakuraRule", m.group(1))]
    return rules.get(("Rule", m.group(1)), "")


def keyword_bodies() -> dict[str, str]:
    rows = {row.ident: row.raw for row in tc.keyword_fallback_rows()}
    consts = tc._consts(re.sub(r"^\s*//.*$", "", tc.read(ARM), flags=re.M))
    out = {}
    for name, key in (("AppliesPyro", "APPLIES_PYRO"),
                      ("AppliesHydro", "APPLIES_HYDRO"),
                      ("AppliesElectro", "APPLIES_ELECTRO"),
                      ("AppliesCryo", "APPLIES_CRYO"),
                      ("AppliesAnemo", "APPLIES_ANEMO"),
                      ("AppliesGeo", "APPLIES_GEO"),
                      ("Confiscated", "CONFISCATED")):
        out[name] = rows.get(f"KLEEMOD-{key}", "")
    out["Knight"] = consts.get("KnightTipText", "")
    return out


def line_opening(line: str) -> str:
    """Up to the line's first number. The C# reads a digit; here a number
    read off a method call (`NaviaDiscount(upgraded)`) renders empty, which
    leaves a double space where the digit was."""
    m = re.search(r"\d|  ", line)
    return line[:m.start()] if m else line


def act_texts() -> dict[str, str]:
    """`StagePerformerBadge.ActText` per guest, base card: the upgraded
    clause `(upgraded ? ... : "")` is dropped before the literals join."""
    src = tc.read(MOD / "Powers" / "Prototype" / "FurinaStageBadges.cs")
    body = src[src.index("public static string ActText"):]
    body = body[body.index("return who switch"):]
    body = body[:body.index("_ =>") + 4]
    body = re.sub(r'\(upgraded\s*\?.*?:\s*""\)', "", body, flags=re.S)
    return {who: tc.csharp_text(expr)
            for who, expr in tc._ACT_ARM.findall(body)}


def guest_body(full: str, card_face: str) -> str:
    """`PlayerTips.Guest`, mirrored."""
    if " Act: " not in full:
        return full
    line, act = full.split(" Act: ", 1)
    if "Act:" in card_face:
        return line
    if line_opening(line) in card_face:
        return "Act: " + act
    return full


class Bodies:
    def __init__(self) -> None:
        self.player = player_bodies()
        self.seat = seat_bodies()
        self.keys = method_keys()
        self.keywords = keyword_bodies()
        self.acts = act_texts()

    def layer(self, call: str, args: str, cls: str,
              card_face: str) -> tuple[int, str | None, str]:
        """(boxes, visible body or None when unmeasured, label)."""
        owner, _, method = call.partition(".")
        if call in BOARD_ONLY:
            return 0, None, method
        if call == "KleeCardTooltips.ForCard":
            boxes = 0
            body = None
            if "includesConfiscatedRules: true" in args:
                boxes += 1
                body = visible(self.keywords["Confiscated"])
            if "includesDazedCard: true" in args:
                boxes += 1
            return boxes, body, "ForCard"
        if owner != "ArmKeywordTips":
            # Base-game tips and card previews: one box, base length.
            return 1, None, method
        if method == "ForAnnotation":
            return 1, visible(annotation_body(args)), method
        if method == "ForTenko":
            return 1, visible(arm_statics()["YaeTenkoTip"]), method
        if method == "ForEdit":
            return 1, visible(arm_statics()["YaeEditTip"]), method
        if method == "ForSakura" and cls.startswith("ProtoYm"):
            return 1, "@YaeSakuraTip", method
        if method == "ForSpark":
            return 1, visible(self.player["SparkKey"]), method
        key = self.keys.get(method)
        if key is None:
            return 1, "", method
        if key in self.player:
            return 1, visible(self.player[key]), method
        who = method[3:]
        if who in self.acts:
            return 1, visible(guest_body(self.acts[who], card_face)), method
        return 1, visible(self.seat.get(key, "")), method


def measure(path: Path, bodies: Bodies) -> dict:
    src = tc.read(path)
    chain = player_chain(src)
    kws = mod_keywords(src)
    card_face = face(src)
    boxes: list[tuple[str, str | None]] = []
    for kw in kws:
        boxes.append((kw, visible(bodies.keywords.get(kw, ""))))
    for call, args in split_layers(chain) if chain else []:
        n, body, label = bodies.layer(call, args, path.stem, card_face)
        for _ in range(n):
            boxes.append((label, body))
    title = re.search(r'\("title", "((?:[^"\\]|\\.)*)"\)', src)
    return {"cls": path.stem, "title": title.group(1) if title else path.stem,
            "boxes": boxes}


def chars(card: dict) -> int:
    return sum(len(b) for _, b in card["boxes"]
               if b is not None and not b.startswith("@"))


def findings(cards: list[dict]) -> list[str]:
    bad: list[str] = []
    used_long: set[str] = set()
    for card in cards:
        n = len(card["boxes"])
        if card["cls"] in BOX_DEBT:
            if n <= CAP_BOXES:
                bad.append(f"BOX_DEBT names {card['cls']}, now {n} boxes: "
                           "drop it")
        elif n > CAP_BOXES:
            bad.append(f"{card['cls']}: {n} boxes on a player's hover "
                       f"(cap {CAP_BOXES}): "
                       + ", ".join(label for label, _ in card["boxes"]))
        for label, body in card["boxes"]:
            if body is None:
                continue
            if body.startswith("@"):
                used_long.add(body[1:])
                continue
            if len(body) > CAP_CHARS:
                bad.append(f"{card['cls']}: {label} is {len(body)} "
                           f"characters (cap {CAP_CHARS}): {body!r}")
    for name in sorted(set(LONG_OK) - used_long):
        bad.append(f"LONG_OK names {name}, which no card raises: drop it")
    return bad


def load() -> list[dict]:
    bodies = Bodies()
    return [measure(p, bodies) for p in sorted(GEN.glob("Proto*.cs"))]


def census(cards: list[dict]) -> None:
    for card in sorted(cards, key=lambda c: (-len(c["boxes"]), -chars(c))):
        print(f"{card['cls']}\t{len(card['boxes'])}\t{chars(card)}\t"
              + " ; ".join(label for label, _ in card["boxes"]))
    n = [len(c["boxes"]) for c in cards]
    ch = [chars(c) for c in cards]
    print(f"\n{len(cards)} cards: boxes median {statistics.median(n)} max "
          f"{max(n)}; chars median {statistics.median(ch)} max {max(ch)}")


def main(argv: list[str]) -> int:
    tc_console = getattr(sys.stdout, "reconfigure", None)
    if tc_console:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cards = load()
    if "--census" in argv:
        census(cards)
        return 0
    bad = findings(cards)
    for line in bad:
        print(line)
    if bad:
        print(f"\n{len(bad)} hover(s) break the house rule (at most "
              f"{CAP_BOXES} boxes, {CAP_CHARS} characters a box). The "
              "player chain is `gen_klee_cards.player_tip_layers`'; a long "
              "body takes player words in `PlayerTips.Bodies`.")
        return 1
    print(f"lint_hover_tips: {len(cards)} generated cards, every player hover "
          f"at most {CAP_BOXES} boxes of at most {CAP_CHARS} characters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

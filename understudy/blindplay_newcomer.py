"""THE NEWCOMER SEAT (2026-10-19): a page that shows only what a human sees.

[USER], 2026-10-19: "see if the seats can actually independently figure out
how to pilot the characters". The ordinary seat page reads far more than a
player does: the seat's longer hover tips, the resolution ledger ("Since last
page", what each card hit, kill causes, relic receipts), forecasts and
previews, reaction and amplifier explanations, the board summaries the kits
grew (Spark sources, the stage forecast, the Oath and shrine blocks), the
glossary, and `--define`. A round that asks whether a kit explains ITSELF has
to take all of that away.

ON when `GITS_NEWCOMER=1` (`bridge.NEWCOMER_ENV`), which
`tools/seat.py --opus-brief --newcomer` bakes into the seat's lane scripts.
OFF, nothing here runs and every page is the page it always was.

WHAT THE PAGE KEEPS, AND WHERE EACH COMES FROM
---------------------------------------------
* The hover tips are the PLAYER's: the bridge is asked `?audience=player` and
  builds the state outside the seat scope (`gits/GitsSeatTips.cs`). An older
  bridge ignores the ask and its state carries no `tip_audience`;
  `bridge_ignored_audience` says so, and `observe` warns once per lane.
* A fight is printed by `combat_page` from the wire's own text: HP, Block,
  Energy, the piles' counts, every power on you and on each enemy with the
  game's own description (the badge's tooltip, nothing added), relics,
  potions, the hand as the card faces print it with their hover tips, each
  enemy's HP, Block and intents (the icon's number and its hover), and the
  board pieces a player sees drawn on screen (the Plans queued on the
  Bake-Kurage, the stage's seats, an ally's HP). Names are the page's handles
  (`Nibbit (1)`, `Coral Guard (2)`), because a command needs them.
* Every other screen is the ordinary page with the seat-only parts cut
  (`trim_page`): the ledger sections, the glossary, the "why it is not on
  this list" notes, and the page's own italic notes, except a note that
  names a command (that is how-to-act, which the newcomer keeps).
* `--define` answers with the game's own keyword tip for the word on this
  screen, or `NO_TIP` (`define`).
"""
from __future__ import annotations

import re
from typing import Any

from understudy import bridge, qa_packet
from understudy.blindplay_coop import banner as coop_banner
from understudy.blindplay_faces import _powers
from understudy.blindplay_read import _enemies, _hand, _int, _player, _text

#: What `observe --define` says when the game has no tip for the word here.
NO_TIP = 'No tip for "{word}" on this screen.'

#: Printed on stderr once per lane where the bridge did not answer the ask
#: for the player's tips (a bridge older than the newcomer seat).
OLD_BRIDGE_WARNING = ("newcomer seat: this lane's bridge predates "
                      "`?audience=player`, so hover tips on this page are the "
                      "SEAT's longer ones; redeploy the bridge "
                      "(deploy_bridge.ps1) before a newcomer round.")
#: The words-store key that warning is filed under.
OLD_BRIDGE_KEY = "__newcomer_old_bridge__"


def on() -> bool:
    """Whether this process renders the newcomer page."""
    return bridge.newcomer()


def bridge_ignored_audience(state: dict[str, Any]) -> bool:
    """True when a live state lacks the bridge's `tip_audience` mark."""
    return isinstance(state, dict) and state.get("tip_audience") != "player"


# ------------------------------------------------------------- the fight --

def _tip_lines(keywords: Any, indent: str = "    ") -> list[str]:
    out = []
    for k in keywords or []:
        if not isinstance(k, dict):
            continue
        name = _text(k.get("name") or k.get("title"))
        text = _text(k.get("description") or k.get("text"))
        if name and text:
            out.append(f"{indent}*{name}* — {text}")
    return out


def _power_line(power: dict[str, Any], indent: str) -> str:
    line = f"{indent}{power['name']}"
    if power.get("numbered") is not False:
        line += f" {power['stacks']}"
    if power.get("text"):
        line += f" — {_text(power['text'])}"
    return line


def _card_lines(entry: dict[str, Any], label: str, face: dict[str, Any]
                ) -> list[str]:
    kind = _text(entry.get("type")).lower()
    head = f"- **{label}** — cost {qa_packet.cost_label(face)}"
    if kind:
        head += f", {kind}"
    ench = face.get("enchantment")
    if isinstance(ench, dict) and ench.get("name"):
        head += f" [{ench['name']}" + (f" {ench['amount']}"
                                       if ench.get("amount") else "") + "]"
    if entry.get("can_play") is False:
        head += " (cannot be played now)"
    out = [head]
    text = _text(entry.get("description"))
    if text:
        out.append(f"    {text}")
    return out + _tip_lines(entry.get("keywords"))


def _intent_line(intent: dict[str, Any]) -> str:
    label = _text(intent.get("label"))
    title = _text(intent.get("title"))
    kind = _text(intent.get("type"))
    head = title or kind or "Intent"
    if label:
        head += f" ({label})"
    text = _text(intent.get("description"))
    return f"    Intent: {head}" + (f" — {text}" if text else "")


def _plans_lines(plans: dict[str, Any] | None) -> list[str]:
    """The Plans waiting on the Bake-Kurage, numbered for `flip <n>`, each
    with the lines its card prints. Nothing the mod measured or forecast."""
    if not plans:
        return []
    out = ["", f"## {plans.get('pet_name') or 'Bake-Kurage'}"]
    queue = plans.get("queue") or []
    if not queue:
        out.append("- No Plans waiting.")
    for n, row in enumerate(queue, 1):
        line = f"{n}. **{row.get('name')}**"
        if row.get("two_line"):
            which = "now-line" if row.get("line") == "now" else "Plan line"
            line += f" (set to its {which})"
            out.append(line)
            if row.get("plan_line"):
                out.append(f"    Plan line: {row['plan_line']}")
            if row.get("now_line"):
                out.append(f"    Now-line: {row['now_line']}")
        else:
            out.append(line)
    return out


def _stage_lines(stage: dict[str, Any] | None) -> list[str]:
    """The stage's seats, front to back, by the name drawn on each."""
    if not stage:
        return []
    seats = stage.get("seats") or []
    out = ["", "## Your stage", f"- Fanfare {stage.get('fanfare', 0)}"]
    if not seats:
        out.append("- The stage is empty.")
    else:
        out.append("- Seats, front to back: "
                   + ", ".join(f"**{s.get('name')}**" for s in seats) + ".")
    return out


def combat_page(state: dict[str, Any], obs: dict[str, Any]) -> str:
    """The fight as a player sees it (`obs` is `observation(state)`)."""
    c = obs["combat"]
    you = c["you"]
    p = _player(state)
    out: list[str] = []
    out += coop_banner(obs.get("coop"))
    out += [f"# Battle — round {c['round']}", "",
            f"- HP {you['hp']}/{you['max_hp']}",
            f"- Block {you['block']}",
            f"- Energy {you['energy']}/{you['max_energy']}"]
    if you.get("stars") is not None:
        out.append(f"- Stars {you['stars']}")
    for name, amount in (you.get("meters") or {}).items():
        out.append(f"- {name} {amount}")
    piles = c["piles"]
    out.append(f"- Draw pile {piles['draw']}, discard pile "
               f"{piles['discard']}, exhaust pile {piles['exhaust']}")
    powers = _powers(p)
    if powers:
        out += ["", "## Your powers"] + [_power_line(pw, "- ")
                                         for pw in powers]
    out += _plans_lines(c.get("plans"))
    out += _stage_lines(c.get("stage"))
    for pet in c.get("pets") or []:
        out.append(f"- Your ally **{pet['name']}**: HP {pet['hp']}/"
                   f"{pet['max_hp']}"
                   + (f", Block {pet['block']}" if pet["block"] else ""))
    relics = you.get("relics") or []
    if relics:
        out += ["", "## Your relics"]
        for r in relics:
            line = f"- **{r['name']}**"
            if r.get("counter") not in (None, ""):
                line += f" ({r['counter']})"
            if r.get("text"):
                line += f" — {r['text']}"
            out.append(line)
    potions = you.get("potions") or []
    out += ["", f"## Potions ({len(potions)} of {you.get('potion_slots')})"]
    out += ([f"- **{x['title']}** — {x['text']}" for x in potions]
            or ["- none"])
    out += ["", "## Your hand"]
    hand = _hand(state)
    if not hand:
        out.append("- (empty)")
    for entry, face in zip(hand, c["hand"]):
        out += _card_lines(entry, face["title"], face)
    out += ["", "## Enemies"]
    for raw, e in zip(_enemies(state), c["enemies"]):
        if _int(raw.get("hp")) <= 0 and not raw.get("intents"):
            continue
        line = f"- **{e['name']}** — HP {e['hp']}/{e['max_hp']}"
        if e.get("block"):
            line += f", Block {e['block']}"
        out.append(line)
        for pw in _powers(raw):
            out.append(_power_line(pw, "    - "))
        intents = raw.get("intents") or raw.get("intent") or []
        if isinstance(intents, dict):
            intents = [intents]
        for intent in intents:
            if isinstance(intent, dict):
                out.append(_intent_line(intent))
    out += ["", "## What you can say", ""]
    out += [f"- `{cmd}`" for cmd in obs.get("commands") or []]
    out += ["", obs["guardrail"]]
    text = "\n".join(out) + "\n"
    qa_packet.assert_blind(text)
    return text


# ------------------------------------------------------- every other page --

#: Sections of the ordinary page a player's screen has no counterpart for.
CUT_SECTIONS = (
    "## Since the screen before this one",
    "## Between the last screen and this one",
    "## Words on this screen",
    "## Not on this list, and why",
    "## What these enemies do",
    "## The fight behind this chooser",
)
_CUT_HEADING = re.compile(r"^## .*'s last carry-out")
#: A page note: an italic line at the margin (a hover tip is indented).
_NOTE = re.compile(r"^\*.*\*\s*$")
#: The rest site's own arithmetic beside the HP.
_REST_ROOM = re.compile(r" \(healing stops at max HP: at most \d+ more\)")


def trim_page(text: str) -> str:
    """The ordinary page minus what only a seat is shown."""
    out: list[str] = []
    cutting = False
    for line in text.split("\n"):
        if line.startswith("## "):
            cutting = (line.startswith(CUT_SECTIONS)
                       or bool(_CUT_HEADING.match(line)))
        if cutting:
            continue
        if line.startswith("- Since last page"):
            continue
        if _NOTE.match(line) and "`" not in line:
            continue
        out.append(_REST_ROOM.sub("", line))
    kept: list[str] = []
    for line in out:
        if line == "" and kept and kept[-1] == "":
            continue
        kept.append(line)
    return "\n".join(kept)


# ---------------------------------------------------------------- define --

def _tips_on_screen(blob: Any, out: list[tuple[str, str]]) -> None:
    """Every `{name, description}` hover tip anywhere in the wire state,
    plus every power's own name and description."""
    if isinstance(blob, dict):
        for key in ("keywords", "hover_tips"):
            for k in blob.get(key) or []:
                if isinstance(k, dict):
                    name = _text(k.get("name") or k.get("title"))
                    text = _text(k.get("description") or k.get("text"))
                    if name and text and (name, text) not in out:
                        out.append((name, text))
        for s in blob.get("status") or []:
            if isinstance(s, dict):
                name = _text(s.get("title") or s.get("name"))
                text = _text(s.get("description"))
                if name and text and (name, text) not in out:
                    out.append((name, text))
        for value in blob.values():
            if isinstance(value, (dict, list)):
                _tips_on_screen(value, out)
    elif isinstance(blob, list):
        for value in blob:
            _tips_on_screen(value, out)


def define(state: dict[str, Any], word: str) -> str:
    """The game's own tip for `word` on this screen, or `NO_TIP`."""
    want = " ".join(word.split()).casefold()
    tips: list[tuple[str, str]] = []
    _tips_on_screen(state, tips)
    hits = [f"**{name}** — {text}" for name, text in tips
            if name.casefold() == want]
    text = "\n".join(hits) if hits else NO_TIP.format(word=word.strip())
    qa_packet.assert_blind(text)
    return text + "\n"

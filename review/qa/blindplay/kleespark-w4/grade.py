"""Grade `KLEESPARK-W4`'s slate off a finished blind-play session.

COMMITTED BEFORE THE RUN. Mechanical only. Every slot is computed from
artefacts the run wrote by itself -- the rendered observation pages
(`turn-*/prompt.md`), the tester's own per-turn reply (`turn-*/reply.json`),
and `transcript.jsonl` -- and nothing here reads a design judgement or the
tester's prose. Guardrail-7 and R217 G ride on the output: these are counts
about one capped batch of fights, not a comparison and not evidence about
balance.

    python review/qa/blindplay/kleespark-w4/grade.py <log_dir> [--json out]

The slate is `review/active/klee-sparks-2026-08-29.md` sec 19.4. It carries
the shapes `kleespark-w3/grade.py` used -- the same page parser, the same
AFFORDABLE rule, the same fight boundary -- plus sec 19.1's pre/post-Power
partition and the converted-Attack read `K2'''` needs.

  W1''' >= 3 PRE-POWER combat pages where the bank affords TWO distinct priced
        titles at once and at least one of them is a NON-DAMAGE sink
        (1-2 SPLIT, 0 MISS; UNREACHED only on zero pre-Power combat pages).
        The same count over POST-POWER pages is RECORDED, NOT GRADED.
  K1''' >= 2 successful plays of a CONVERTED ATTACK on POST-POWER pages whose
        printed bank was >= 3 (1 SPLIT, 0 MISS). UNREACHED if the Power never
        resolves, or if no post-Power page printed a bank >= 3. The
        DENOMINATOR -- post-Power combat pages printing a bank >= 3 -- is
        printed with the grade.
  K2''' both halves. (i) on EVERY post-Power combat page every converted
        Attack in hand prints Spark 3 / Energy 0; (ii) on >= 1 post-Power page
        a Skill or Power is played AND a converted Attack is paid in Sparks on
        the same page. Both = PREDICTED, exactly one = SPLIT, neither = MISS.
        UNREACHED if the Power never resolves; half (i) alone is UNREACHED if
        no post-Power page ever printed an Attack in hand, and the slot then
        grades on (ii) alone.
  K3''' >= 1 post-Power page posing a CONVERTED ATTACK (3) against a price-2
        NON-DAMAGE sink, both affordable, where the non-damage sink was the
        play. 0 with a crowding denominator >= 3 = MISS; 0 with 1-2 = SPLIT;
        denominator 0 = UNREACHED.
  K4''' RECORDED, NOT GRADED: whether the Power was drawn and where it
        resolved, the pre/post-Power attack share, and the per-fight peak bank.

THE PARTITION, sec 19.4, implemented as written. The POWER PAGE is the combat
page on which a successful `play` of the Power is recorded; PRE-POWER pages are
every combat page up to and INCLUDING it and POST-POWER pages every combat page
after it. Success is read off the NEXT page's `What happened last time` line,
which the driver writes as `ok ...` for a command the game accepted. If the
Power is never played there are no post-Power pages and every `K` slot is
UNREACHED.

  A DIAGNOSTIC RIDES THE PARTITION, RECORDED AND GRADING NOTHING. A power lasts
  one combat, so a Power played in fight N is gone in fight N+1 while sec 19.4's
  partition keeps calling those later pages POST-POWER. The count of pages that
  actually PRINT the Power in the player's own power block is reported beside
  the partition as `power_active_pages`. It is a fact about the run, it is not a
  grade, and no slot above is computed from it: the registered predicate is the
  registered predicate.

A CONVERTED ATTACK, sec 19.4: a hand card the page prints as an Attack that
carries no printed Spark price. The Power exempts X-cost Attacks
(`SparkAttackCostPower.Converts`), so a card printing `cost X` is excluded and
recorded. Ka-pow! prints its own price and is never converted (sub-pick (a)).

WHAT "PRINTS SPARK 3" MEANS ON THE PAGE, stated before the run because the
observation page has no per-card Spark corner. The blind page prints a card as
`- **Title** - cost N, kind` plus its body, and a Spark price appears only
where the CARD's own body prints one (`Spend 2 Sparks.`). The Power does not
rewrite a converted Attack's body; it zeroes the printed Energy line
(`TryModifyEnergyCostInCombat`) and states its price once, in its own power
text at the top of the page. So half (i) is read as the two things the page
does print: every converted Attack shows an Energy cost of 0, AND the page's
own power block carries the Power's rule with the price 3 in it. A converted
Attack still printing a non-zero Energy cost, or a page carrying the Power
without the price 3 in its text, FAILS half (i) and the page and card are
named. This is the reading taken, fixed here before the run, and it is an
instrument limit rather than a claim about the card.

AFFORDABLE, once, for the whole slate (sec 19.4, taken from sec 18.4
unchanged): printed Spark price <= the printed Spark bank AND printed Energy
cost <= the printed current Energy. A CONVERTED ATTACK's Spark price is 3 and
its Energy cost is 0.

A FIGHT is a maximal run of CONSECUTIVE combat pages in turn order, exactly as
`W3`'s grader defined it.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# The granted deck, sec 19.3. Printed name -> Spark price. The MAKERS carry no
# price and are in neither map: a maker is never an affordable "use" of the
# bank, and counting one as a sink would inflate `W1'''` by construction.
DAMAGE_SINKS = {
    "Ka-pow!": 1,
}
NONDAMAGE_SINKS = {
    "Set It Off": 2,
    "Dig In": 2,
    "Powder Smoke": 2,
    "Rummage": 3,
}
PRICED = {**DAMAGE_SINKS, **NONDAMAGE_SINKS}
MAKERS = ("Powder Pop", "Skip and Hop", "Warm Glow", "Snap!", "Hot Hands",
          "All of My Treasures!", "Da-da-da!")

# The subject of this read. The CARD is the sheet's name; the POWER it applies
# carries its own title from `SparkAttackCostPower.Localization`. Both are
# matched, because the card is what a `play` row names and the power is what a
# page's power block prints.
POWER_CARD = "Spark Knight's Oath"
POWER_TITLES = (POWER_CARD, "True Spark Knight")
CONVERTED_PRICE = 3          # C.SPARK_ATTACK_POWER_PRICE, sec 19.3
NONDAMAGE_RUNG = 2           # the price-2 rung `K3'''` asks about

BANK = re.compile(r"^\s*-\s*Spark[:\s]\s*(\d+)", re.I | re.M)
ENERGY = re.compile(r"^\s*-\s*Energy[:\s]\s*(\d+)\s*/", re.I | re.M)
CARD_HEAD = re.compile(r"^\s*-\s+\*\*(.+?)\*\*(?:\s+\(upgraded\))?"
                       r"(?:\s+—\s+(.*))?$", re.M)
COST = re.compile(r"\bcost\s+(\d+)", re.I)
COST_X = re.compile(r"\bcost\s+X\b", re.I)
SPEND_SPARK = re.compile(r"\bspends?\s+(\d+)\s+spark", re.I)
COMBAT = re.compile(r"^#\s+Battle", re.I | re.M)
LAST_OK = re.compile(r"^ok\b", re.I | re.M)
PLAY_CMD = re.compile(r'^\s*play\s+"(.+?)"', re.I)


def _bare(title: str) -> str:
    """A printed title with `EB-177`'s repeat number taken back off."""
    return re.sub(r"\s*\(\d+\)\s*$", "", title).strip()


def _section(page: str, heading: str) -> str:
    """The text under one `## Heading`, up to the next heading of any depth."""
    head = re.search(rf"^#+\s*{heading}.*$", page, re.I | re.M)
    if not head:
        return ""
    rest = page[head.end():]
    nxt = re.search(r"^#+\s", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def _hand(page: str) -> list[dict]:
    """Every card face the page prints under `Your hand`, with its body.

    Only the hand section is read: a reward screen prints faces too, and a card
    the tester cannot play is not a skipped sink.
    """
    block = _section(page, "Your hand")
    if not block:
        return []
    heads = list(CARD_HEAD.finditer(block))
    out = []
    for i, m in enumerate(heads):
        body = block[m.end(): heads[i + 1].start() if i + 1 < len(heads)
                     else len(block)]
        title = _bare(m.group(1))
        tail = (m.group(2) or "").lower()
        kind = ""
        for k in ("attack", "skill", "power", "status", "curse"):
            if k in tail:
                kind = k
                break
        cost = COST.search(tail)
        spend = SPEND_SPARK.search(body)
        out.append({
            "title": title,
            "kind": kind,
            "energy": int(cost.group(1)) if cost else None,
            "cost_is_x": bool(COST_X.search(tail)),
            "printed_spark_price": int(spend.group(1)) if spend else None,
        })
    return out


def _power_block(page: str) -> str:
    """The player's own status lines -- everything above `## Your hand`."""
    cut = re.search(r"^#+\s*Your hand", page, re.I | re.M)
    return page[:cut.start()] if cut else page


def _page_carries_power(page: str) -> bool:
    """Does this page print the Power in the player's own power block?"""
    head = _power_block(page)
    return any(t.lower() in head.lower() for t in POWER_TITLES)


def _page_prints_price_3(page: str) -> bool:
    """Does the Power's own printed text on this page carry the price 3?"""
    head = _power_block(page)
    for line in head.splitlines():
        if any(t.lower() in line.lower() for t in POWER_TITLES):
            if re.search(rf"\b{CONVERTED_PRICE}\b\s*(\[gold\])?\s*spark",
                         line, re.I):
                return True
    return False


def _pages(log_dir: Path) -> list[dict]:
    """One row per answered turn, in order, with everything a slot needs."""
    rows = []
    prompts = sorted(log_dir.glob("turn-*/prompt.md"))
    texts = [p.read_text(encoding="utf-8", errors="replace") for p in prompts]
    for i, (prompt, page) in enumerate(zip(prompts, texts)):
        reply_path = prompt.parent / "reply.json"
        reply = {}
        if reply_path.is_file():
            try:
                reply = json.loads(reply_path.read_text(encoding="utf-8"))
            except ValueError:
                reply = {}
        bank = BANK.search(page)
        energy = ENERGY.search(page)
        combat = bool(COMBAT.search(page))
        # AN ABSENT SPARK LINE ON A COMBAT PAGE IS A BANK OF ZERO, NOT AN
        # UNREAD ONE (`W1`'s, `W2`'s and `W3`'s graders, same reason): the game
        # prints a power only while it is held, so a spent-out bank prints
        # nothing.
        value = int(bank.group(1)) if bank else (0 if combat else None)
        # Did the command this page answered succeed? The NEXT page reports it.
        nxt = _section(texts[i + 1], "What happened last time") \
            if i + 1 < len(texts) else ""
        rows.append({
            "turn": prompt.parent.name,
            "combat": combat,
            "bank": value,
            "energy": int(energy.group(1)) if energy else None,
            "hand": _hand(page),
            "command": str(reply.get("command") or "").strip(),
            "thinking": str(reply.get("thinking") or "").strip(),
            "accepted": bool(LAST_OK.search(nxt.strip())),
            "carries_power": combat and _page_carries_power(page),
            "prints_price_3": combat and _page_prints_price_3(page),
        })
    return rows


def _converted(card: dict) -> bool:
    """A CONVERTED ATTACK, sec 19.4 -- an Attack with no printed Spark price.

    X-cost Attacks are exempt by the Power's own rule
    (`SparkAttackCostPower.Converts`) and are excluded here.
    """
    return (card["kind"] == "attack"
            and card["printed_spark_price"] is None
            and not card["cost_is_x"])


def _affordable(row: dict, *, post_power: bool) -> list[dict]:
    """The distinct priced titles this page's bank and Energy pay for.

    On a POST-POWER page the converted Attacks join the list at a price of 3
    and an Energy cost of 0, which is the whole point of the Power; on a
    PRE-POWER page only the printed prices count, exactly as `W3` counted them.
    """
    seen: dict[str, dict] = {}
    if row["bank"] is None:
        return []
    for card in row["hand"]:
        title = card["title"]
        if title in seen:
            continue
        if title in PRICED:
            price, nondamage, converted = PRICED[title], \
                title in NONDAMAGE_SINKS, False
        elif post_power and _converted(card):
            price, nondamage, converted = CONVERTED_PRICE, False, True
        else:
            continue
        if price > row["bank"]:
            continue
        # Energy binds only where the page printed both numbers. A converted
        # Attack's Energy cost is 0 by the rule, so it never binds.
        energy = 0 if converted else card["energy"]
        if (energy is not None and row["energy"] is not None
                and energy > row["energy"]):
            continue
        seen[title] = {"title": title, "price": price,
                       "nondamage": nondamage, "converted": converted}
    return list(seen.values())


def _partition(rows: list[dict]) -> dict:
    """sec 19.4's partition, off the transcript's own `play` row."""
    combat = [r for r in rows if r["combat"]]
    power_page = None
    for r in combat:
        m = PLAY_CMD.match(r["command"])
        if m and _bare(m.group(1)).lower() == POWER_CARD.lower() \
                and r["accepted"]:
            power_page = r["turn"]
            break
    if power_page is None:
        pre, post = combat, []
    else:
        idx = [r["turn"] for r in combat].index(power_page)
        pre, post = combat[:idx + 1], combat[idx + 1:]
    return {"power_page": power_page,
            "pre": pre, "post": post,
            "pre_pages": len(pre), "post_pages": len(post),
            # RECORDED, NOT GRADED -- see the module docstring.
            "power_active_pages": sum(1 for r in combat if r["carries_power"]),
            "power_drawn": any(
                any(c["title"] == POWER_CARD for c in r["hand"])
                for r in combat)}


def w1(part: dict) -> dict:
    """`W1''`'s question at the longer batch, on PRE-POWER pages only."""
    def scan(pages, post_power):
        hits = []
        for r in pages:
            aff = _affordable(r, post_power=post_power)
            if len(aff) >= 2 and any(a["nondamage"] for a in aff):
                hits.append({"turn": r["turn"], "bank": r["bank"],
                             "energy": r["energy"],
                             "affordable": [a["title"] for a in aff]})
        return hits

    hits = scan(part["pre"], False)
    n = len(hits)
    den = part["pre_pages"]
    if not den:
        grade = "UNREACHED"
    elif n >= 3:
        grade = "PREDICTED"
    elif n >= 1:
        grade = "SPLIT"
    else:
        grade = "MISS"
    post_hits = scan(part["post"], True)
    return {"slot": "W1'''", "value": n, "pre_power_pages": den,
            "grade": grade, "hits": hits,
            # sec 19.1: printed so the number exists, grading nothing.
            "post_power_count_recorded_not_graded": len(post_hits),
            "post_power_pages": part["post_pages"],
            "post_power_hits": post_hits,
            # sec 19.4's MISS branch reads on a denominator of >= 30.
            "denominator_ge_30": den >= 30}


def k1(part: dict) -> dict:
    """Is the converted price of 3 ever actually PAID?"""
    den_pages = [r for r in part["post"] if (r["bank"] or 0) >= CONVERTED_PRICE]
    hits = []
    for r in den_pages:
        m = PLAY_CMD.match(r["command"])
        if not m or not r["accepted"]:
            continue
        played = _bare(m.group(1))
        card = next((c for c in r["hand"] if c["title"] == played), None)
        if card and _converted(card):
            hits.append({"turn": r["turn"], "played": played,
                         "bank": r["bank"], "energy": r["energy"]})
    n = len(hits)
    if part["power_page"] is None:
        grade, why = "UNREACHED", "the Power never resolved"
    elif not den_pages:
        grade, why = "UNREACHED", ("no post-Power page printed a bank of >= "
                                   f"{CONVERTED_PRICE}; the fault is income at "
                                   "the price-3 rung on this batch")
    else:
        why = ""
        grade = "PREDICTED" if n >= 2 else ("SPLIT" if n == 1 else "MISS")
    return {"slot": "K1'''", "value": n, "grade": grade, "why": why,
            "denominator_post_power_pages_bank_ge_3": len(den_pages),
            "denominator_turns": [r["turn"] for r in den_pages],
            "hits": hits}


def k2(part: dict) -> dict:
    """Once played, is the effect FELT -- the two halves sec 5 names."""
    failures = []
    pages_with_attacks = 0
    for r in part["post"]:
        conv = [c for c in r["hand"] if _converted(c)]
        if conv:
            pages_with_attacks += 1
        for c in conv:
            if c["energy"] not in (0, None):
                failures.append({"turn": r["turn"], "card": c["title"],
                                 "printed_energy": c["energy"],
                                 "fault": "converted Attack printed a "
                                          "non-zero Energy cost"})
            elif not r["prints_price_3"]:
                failures.append({"turn": r["turn"], "card": c["title"],
                                 "fault": "the page did not print the Power's "
                                          f"price of {CONVERTED_PRICE}"})
    if pages_with_attacks == 0:
        half_i = "UNREACHED"
    else:
        half_i = "PASS" if not failures else "FAIL"

    half_ii_hits = []
    for r in part["post"]:
        m = PLAY_CMD.match(r["command"])
        if not m or not r["accepted"]:
            continue
        played = _bare(m.group(1))
        card = next((c for c in r["hand"] if c["title"] == played), None)
        if not card:
            continue
        # Every successful post-Power play, with what the page printed about
        # it. `_energy_turns` below does the pairing half (ii) asks for.
        half_ii_hits.append({"turn": r["turn"], "title": played,
                             "kind": card["kind"],
                             "converted": _converted(card),
                             "energy_cost": card["energy"]})
    turns = _energy_turns(part["post"], half_ii_hits)
    half_ii = "PASS" if turns else "FAIL"

    if part["power_page"] is None:
        grade = "UNREACHED"
    else:
        passes = sum(1 for h in (half_i, half_ii) if h == "PASS")
        if half_i == "UNREACHED":
            grade = "PREDICTED" if half_ii == "PASS" else "MISS"
        elif passes == 2:
            grade = "PREDICTED"
        elif passes == 1:
            grade = "SPLIT"
        else:
            grade = "MISS"
    return {"slot": "K2'''", "grade": grade,
            "half_i_cost_corner": half_i,
            "half_i_post_power_pages_printing_an_attack": pages_with_attacks,
            "half_i_failures": failures,
            "half_ii_energy_is_skill_currency": half_ii,
            "half_ii_turns": turns,
            "plays_post_power": half_ii_hits}


def _energy_turns(post: list[dict], plays: list[dict]) -> list[dict]:
    """Turns on which the bank bought an Attack and Energy bought a Skill.

    A blind session answers ONE command per page, so a `turn` here is the run
    of pages between two `end turn` commands. sec 19.4 half (ii) asks for the
    Energy and the bank buying different things on the same turn.
    """
    by_turn = {p["turn"]: p for p in plays}
    out = []
    group: list[dict] = []
    for r in post:
        if r["turn"] in by_turn:
            group.append(by_turn[r["turn"]])
        if r["command"].strip().lower() == "end turn":
            out.append(group)
            group = []
    if group:
        out.append(group)
    hits = []
    for g in out:
        conv = [p for p in g if p["converted"]]
        other = [p for p in g if p["kind"] in ("skill", "power")
                 and (p["energy_cost"] or 0) > 0]
        if conv and other:
            hits.append({"attack": [p["title"] for p in conv],
                         "energy_spent_on": [p["title"] for p in other],
                         "turns": [p["turn"] for p in g]})
    return hits


def k3(part: dict) -> dict:
    """Does the price-3 rung CROWD OUT the price-2 rungs?"""
    posed = []
    for r in part["post"]:
        aff = _affordable(r, post_power=True)
        conv = [a for a in aff if a["converted"]]
        rung = [a for a in aff
                if a["nondamage"] and a["price"] == NONDAMAGE_RUNG]
        if conv and rung:
            m = PLAY_CMD.match(r["command"])
            played = _bare(m.group(1)) if m and r["accepted"] else ""
            posed.append({"turn": r["turn"], "bank": r["bank"],
                          "converted": [a["title"] for a in conv],
                          "rung": [a["title"] for a in rung],
                          "played": played,
                          "took_rung": played in [a["title"] for a in rung],
                          "took_converted": played in [a["title"]
                                                       for a in conv]})
    den = len(posed)
    n = sum(1 for p in posed if p["took_rung"])
    if den == 0:
        grade = "UNREACHED"
    elif n >= 1:
        grade = "PREDICTED"
    elif den >= 3:
        grade = "MISS"
    else:
        grade = "SPLIT"
    return {"slot": "K3'''", "value": n, "grade": grade,
            "crowding_denominator": den, "posed": posed,
            "share_taken_by_converted_attack_recorded_not_graded":
                (sum(1 for p in posed if p["took_converted"]) / den * 100)
                if den else None}


def _fights(rows: list[dict]) -> list[list[dict]]:
    """Maximal runs of CONSECUTIVE combat pages, in turn order."""
    out: list[list[dict]] = []
    current: list[dict] = []
    for r in rows:
        if r["combat"]:
            current.append(r)
        elif current:
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def _plays(log_dir: Path, rows: list[dict]) -> list[dict]:
    idx: dict[str, str] = {}
    for r in rows:
        for card in r["hand"]:
            if card["kind"] and card["title"] not in idx:
                idx[card["title"]] = card["kind"]
    out = []
    transcript = log_dir / "transcript.jsonl"
    if not transcript.is_file():
        return out
    for line in transcript.read_text(encoding="utf-8",
                                     errors="replace").splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("kind") != "command" or not rec.get("ok"):
            continue
        if rec.get("verb") != "play":
            continue
        blob = rec.get("printed")
        raw = (blob.get("card") if isinstance(blob, dict) else blob) or ""
        title = _bare(str(raw))
        out.append({"title": title, "kind": idx.get(title, "")})
    return out


def _share(pages: list[dict]) -> dict:
    """The attack share of the successful plays on one set of pages."""
    total = attacks = 0
    for r in pages:
        m = PLAY_CMD.match(r["command"])
        if not m or not r["accepted"]:
            continue
        card = next((c for c in r["hand"] if c["title"] == _bare(m.group(1))),
                    None)
        total += 1
        if card and card["kind"] == "attack":
            attacks += 1
    return {"plays": total, "attacks": attacks,
            "pct": (attacks / total * 100) if total else None}


def k4(rows: list[dict], part: dict, plays: list[dict]) -> dict:
    """RECORDED, NOT GRADED -- three numbers the next reader will want."""
    fights = _fights(rows)
    peaks = [max(r["bank"] or 0 for r in f) for f in fights]
    return {"slot": "K4'''", "grade": "NOT GRADED",
            "a_power_drawn": part["power_drawn"],
            "a_power_page": part["power_page"],
            "a_power_active_pages": part["power_active_pages"],
            "b_attack_share_pre_power": _share(part["pre"]),
            "b_attack_share_post_power": _share(part["post"]),
            "b_attack_share_whole_session": {
                "plays": len(plays),
                "attacks": sum(1 for p in plays if p["kind"] == "attack"),
                "pct": (sum(1 for p in plays if p["kind"] == "attack")
                        / len(plays) * 100) if plays else None},
            "c_fights": len(peaks), "c_peaks": peaks,
            "c_median_peak_bank": statistics.median(peaks) if peaks else None,
            "c_pages_per_fight": [len(f) for f in fights]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("log_dir")
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)
    log_dir = Path(args.log_dir)
    rows = _pages(log_dir)
    part = _partition(rows)
    plays = _plays(log_dir, rows)
    out = {
        "log_dir": str(log_dir),
        "turns": len(rows),
        "combat_turns": sum(1 for r in rows if r["combat"]),
        "partition": {k: v for k, v in part.items()
                      if k not in ("pre", "post")},
        "W1'''": w1(part),
        "K1'''": k1(part),
        "K2'''": k2(part),
        "K3'''": k3(part),
        "K4'''": k4(rows, part, plays),
    }
    print("partition: " + json.dumps(out["partition"]))
    for slot in ("W1'''", "K1'''", "K2'''", "K3'''", "K4'''"):
        s = out[slot]
        print(f"{slot}: {s['grade']}  " + json.dumps(
            {k: v for k, v in s.items()
             if k in ("value", "pre_power_pages", "post_power_pages",
                      "post_power_count_recorded_not_graded",
                      "denominator_post_power_pages_bank_ge_3",
                      "half_i_cost_corner", "half_ii_energy_is_skill_currency",
                      "crowding_denominator", "a_power_drawn", "a_power_page",
                      "c_peaks", "c_median_peak_bank")}, default=str))
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=1, default=str)
                                   + "\n", encoding="utf-8")
        print(f"json: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""THE MISREAD CLASSES: a reader who got the board wrong and reasoned well.

Klee slice 1 round 1's failure was not a bad line -- it was a reader who
thought the wrong Attack was free and reasoned correctly from there. That is
the shape a weaker reader reproduces most often, and it is the shape a verdict
column cannot see, because the form comes back well-formed and confident.

Two classes live here, and each is NARROW ON PURPOSE. A false MISREAD is worse
than a missed one: the whole value of this list is that a row carrying an
entry is worth a person's attention, and a check that fired on hypotheticals
would spend that credibility in a round.

  * **COSTS** (`free_card_misreads`) -- "X is free", checked against the cost
    the packet PRINTS. Round 1's failure, made mechanical.
  * **ARITHMETIC** (`block_prevention_misreads`) -- the Codex seat's own catch
    on the 2026-08-29 sanity read: *"the 3 HP that block would have
    prevented"*, where five Block against an eight-damage intent prevents
    five and three is what gets through. The residual quoted as the
    prevention: one subtraction the wrong way round.

WHY IT IS A MODULE AND NOT A HALF OF THE SANITY HARNESS. It was the harness's,
and `understudy/local_tester.py` needs the same checks on a LIVE tester read.
A tool importing `understudy` is the direction this tree runs; `understudy`
importing a tool is not, so the checks moved down and
`tools/local_model_sanity.py` re-exports them. Both callers therefore ask the
same question, which is the only way the sanity comparison stays comparable to
the thing it sanctioned.

WHAT NEITHER CLASS READS. A design sheet. Both work off the PACKET -- what the
reader was shown -- because the question is whether the reading matches the
page, not whether it matches the truth. `understudy/resource_order.py` is the
check that does need the sheets, and it is deliberately a different file.
"""

from __future__ import annotations

import re
from typing import Any

# A claim of the form "X is free". Deliberately literal: this is looking for
# one known misread, not doing sentiment analysis on a reader's prose.
FREE_CLAIMS: tuple[str, ...] = (
    "free", "costs 0", "cost 0", "costs zero", "0 energy", "zero energy",
    "0-cost", "zero-cost", "no energy",
)
# How far either side of the claim a card title still counts as its subject.
CLAIM_WINDOW = 90

_CARD_HEAD = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
_COST = re.compile(r"^-\s*Cost:\s*(\d+)", re.MULTILINE)

# The arithmetic class. It can only fire when all three numbers are on the
# page: a stated prevention P, a stated Block B in the SAME sentence, and an
# incoming intent D the PACKET prints. It cannot compute the Block the line
# actually ends with -- that would be replaying the turn -- it cannot read a
# prevention claim that names no Block, and against several intents it tries
# each printed one. It fires only on the exact residual identity, P == D - B
# with B < D, so a correct sentence ("the 5 HP that block would have
# prevented") is silent and a vague one is silent too.
_PREVENT = re.compile(
    r"(\d+)\s+(?:hp|damage|health)\b[^.]{0,48}?\bprevent", re.IGNORECASE)
_BLOCK_AMOUNT = re.compile(r"(\d+)\s+block\b", re.IGNORECASE)
_INTENT = re.compile(r"attack for\s+(\d+)\s+damage", re.IGNORECASE)
_SENTENCE = re.compile(r"(?<=[.!?])\s+")


def printed_costs(packet_md: str) -> dict[str, int]:
    """`{printed title: printed cost}` for every card the packet's hand shows.

    Read off the PACKET rather than a sheet, deliberately: the question is
    what the reader was SHOWN, and a sheet would answer what is true.
    """
    costs: dict[str, int] = {}
    heads = list(_CARD_HEAD.finditer(packet_md or ""))
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(packet_md)
        cost = _COST.search(packet_md[head.end():end])
        if cost:
            costs[head.group(1).strip()] = int(cost.group(1))
    return costs


def free_card_misreads(packet_md: str, text: str) -> list[str]:
    """Every "<card> is free" claim in the prose that the packet contradicts.

    It fires only where a claim word sits within `CLAIM_WINDOW` characters of
    a card title the packet prints a NON-ZERO cost for. A cleverer matcher
    would start reporting a reader's hypotheticals ("if it were free") as
    misreads, and a misread report nobody trusts is worse than none.
    """
    costs = printed_costs(packet_md)
    if not costs:
        return []
    low = str(text or "").casefold()
    found: list[str] = []
    for claim in FREE_CLAIMS:
        start = 0
        while (i := low.find(claim, start)) != -1:
            window = low[max(0, i - CLAIM_WINDOW):i + len(claim)
                         + CLAIM_WINDOW]
            for title, cost in costs.items():
                if cost != 0 and title.casefold() in window:
                    line = (f"called {title!r} {claim!r}, but the packet "
                            f"prints Cost: {cost}")
                    if line not in found:
                        found.append(line)
            start = i + len(claim)
    return found


def intent_damages(packet_md: str) -> list[int]:
    """Every incoming attack number the packet TELEGRAPHS, in printed order."""
    return [int(m.group(1)) for m in _INTENT.finditer(packet_md or "")]


def block_prevention_misreads(packet_md: str, text: str) -> list[str]:
    """Every "N HP that Block would have prevented" the arithmetic denies.

    Conservative by construction -- see the note above `_PREVENT`. One line
    per distinct claim, naming all three numbers so the reader can check it
    without opening the packet.
    """
    incoming = intent_damages(packet_md)
    if not incoming:
        return []
    found: list[str] = []
    for sentence in _SENTENCE.split(str(text or "")):
        claim = _PREVENT.search(sentence)
        if not claim or "block" not in sentence.casefold():
            continue
        prevented = int(claim.group(1))
        blocks = {int(m.group(1)) for m in _BLOCK_AMOUNT.finditer(sentence)}
        for block in sorted(blocks):
            for damage in incoming:
                residual = prevented == damage - block
                if block < damage and residual and prevented != block:
                    line = (f"said {prevented} was prevented, but {block} "
                            f"Block against a printed {damage}-damage intent "
                            f"prevents {min(block, damage)}; {prevented} is "
                            f"the damage that gets THROUGH")
                    if line not in found:
                        found.append(line)
    return found


def misreads(packet_md: str, text: str) -> list[str]:
    """Both classes, costs first. The ONE caller-facing door.

    Every reader of a misread list goes through this, so a third class is
    added in exactly one place and no caller silently keeps the old set.
    """
    return (free_card_misreads(packet_md, text)
            + block_prevention_misreads(packet_md, text))


def prose_of(form: dict[str, Any], questions: "tuple[str, ...]") -> str:
    """The reader's own words, joined -- the only text either class scans."""
    return "\n".join(str(form.get(q) or "") for q in questions)

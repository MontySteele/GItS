# Docket — the Klee rework

**Status:** DOCKET. Routed, not decided, not scheduled. Zero design authority:
nothing here proposes a card, a number or a fix. Opened 2026-08-06 (Track R)
against the sitting of 2026-08-06
(`docs/sitting-record-predraft-2026-08-06.md`); rulings R109 and R111.

Source for every item: `review/redteam/exploit-ledger.md` (S13 — 71 lines,
71/71 replay-verified, 14 mechanism families). Pins:
`tier0/tests/test_s13_exploit_pins.py`.

---

## 1. X1 — the companion cost-delta accumulator (NOTE, R111)

**Verdict, verbatim:** *"Let's make a note of this for the Klee rework."*

The note, so the session does not have to re-derive it:
`state.companion_cost_delta_this_turn` is additive and uncapped
(`tier0/engine/effects.py:961-962`) and `card_cost` floors every companion at 0
(`tier0/engine/combat.py:159-160`). One play of Klee's **`friendly_visit`** — a
common that draws its own replacement — makes every companion in hand free for
the turn; any self-replacing companion then loops until the engine's 25-play
detector fires. Ten S13 lines across four independent slices ride this one
accumulator.

### FLAG-1 — HELD, and this docket does not answer it

The accumulator has **two** run-plausible enablers riding the same shared
uncapped state: Klee's `friendly_visit` (common) **and Kokomi's `honor_guard`
(printed 0-cost)**. A Klee-rework-only note leaves the Kokomi leg live.

Two questions were put and neither has an answer:

1. Should the note also ride the Kokomi pool-rework docket
   (`docs/dockets/kokomi-workshop.md`)?
2. Should the accumulator **itself** — shared machinery, uncapped, floored at
   0 — take a structural disposition at a systems session, rather than being
   handled once per character kit?

**Held means held.** Until one-line verdicts land, this docket carries the Klee
leg only, and the Kokomi leg is live and unrouted by design rather than by
oversight.

---

## 2. X7 — the Klee spark economy (NEW LAW + AUDIT, R109)

**Verdict, verbatim:** *"Gate repeatable spark generation behind Uncommon or
make sure no card below Rare is both 'sparks + draw enabler'"*

### 2a. The law

**EITHER** repeatable spark generation sits at **Uncommon or higher**, **OR**
no card below **Rare** is simultaneously a spark source and a draw enabler.

The disjunction is load-bearing and is recorded as stated. Two ways to satisfy
it; the law is not collapsed to one here, and a session that collapses it is
making a design decision that this docket has not been given.

Mechanism the law is aimed at, from the ledger: the spark printer's only bound
is Exhaust, and the shipped upgrade is exactly `{remove: exhaust}`.

### 2b. Audit findings — **EMPTY, owned by Track T**

> **SLOT. Do not fill speculatively.** A sweep of the Klee pool for cards that
> violate **both** limbs of §2a — i.e. repeatable spark generation below
> Uncommon *and* below-Rare cards that are both spark source and draw enabler.
> The auditor **reports**; the auditor does not bump, reprice or rework. Every
> finding lands here with a card id, its rarity, and which limb it fails.
>
> _(no findings recorded — the audit has not run)_

---

## 3. X8 — bomb damage, two uncapped terms (AUDIT, R111)

**Verdict, verbatim:** *"Not a problem at higher rarity — need to check these
cards."*

The verdict prices the mechanism as acceptable **at higher rarity** and asks
for the rarity fact, which nobody has. Mechanism, from the ledger:
`_op_modify_bombs` adds a bonus to every bomb on every enemy with no per-card,
per-bomb or per-turn limit, and bomb damage is the product of two uncapped
terms.

### Findings — **EMPTY**

> **SLOT. Do not fill speculatively.** A rarity check on the carrier cards of
> **both** uncapped terms. Report card id, term carried, current rarity. No
> bumps, no proposals: "not a problem at higher rarity" becomes a finding only
> once the rarities are on the page.
>
> _(no findings recorded — the check has not run)_

---

## 4. What this docket is not

It is not the Klee rework plan, and it is not a list of things to fix. Three
items arrived from one red-team sweep; the rework session owns everything else
about Klee, including whether these three are even the interesting ones.

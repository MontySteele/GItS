# Kokomi exploratory playtest — raw notes, 2026-08-26 (evening)

> **What this is.** [USER]'s live observations during the EXPLORATORY Kokomi run
> (R175 sequence: exploratory → `S4-G6` band declaration → `S4-G14` confirmatory).
> Graded against nothing; a source of understanding, per the protocol's own
> re-anchor note. Build: mod **0.2-1159**, build id `20260826-204650+98fb3a0`
> (main `0e329b9` + EB-67 icons landed). Claude's code reads are marked as such
> and are NOT fixes; nothing here changes a sheet, a stamp, or a ruling.

## A. Bug reports

| # | Report ([USER], verbatim) | Claude's code read (same evening) | Triage |
|---|---|---|---|
| A1 | "what does Pearl Barrage even do? Seems to just do 5 damage all the time." | Sheet (`docs/kokomi-cards.yaml:428-430`): exhaust 1 chosen card, deal 5 + 3 × that card's cost (ladder 5/8/11). Generated C# (`Cards/Kokomi/Generated/PearlBarrage.cs`) reads the cost through `CalculatedDamageVar(...).WithMultiplier(ExhaustSelection.Cost(card))`. `ExhaustSelection.Close()` does NOT clear the record and `Current()` stays in scope, so the record is there at attack time. Leading hypothesis: the base game computes the calculated var when the card is rendered/played (multiplier 0, no selection yet) and does not recalculate mid-`OnPlay`, so the attack lands at the base 5. Same shape on the sibling at `docs/kokomi-cards.yaml:639` (5 + 2×cost to all enemies). | **Probable defect.** Prove with the understudy scenario harness (give card, set energy, play with a cost-1 victim, expect HP delta 8), then fix at the generator (recalculate after the selection block). Not during the playtest. |
| A2 | "'All Hands' just adds 2 companion cards to my hand, rather than transforming 2 cards into companion cards." | Sheet row (`docs/kokomi-cards.yaml:808-811`): `{op: conscript, amount: 2, mode: create}`; generator emits `createMode: true`; printed text "Muster 2, adding the units to your hand." The default Muster (no `mode:`) is the other behaviour. | **As ruled, not a defect.** If [USER] wants All Hands to transform instead, that is a design pick → QUEUE (numbered, with the two Muster modes named). |
| A3 | "Vigil of the Deep adds 3 block after you take damage, rather than preventing 3 damage" — then: "On second look, Vigil of the Deep worked as expected another time. I might have misread the numbers the first time." | Not investigated (retracted). | **Withdrawn by [USER].** Keep an eye out; if it recurs, capture the exact numbers. |
| A4 | "Klee's cards that give Burst energy are labelled, but Kokomi's are not." | Not yet read. Klee's Burst-gain cards carry a printed keyword/rider; Kokomi's Charge/Burst gain appears to print none. | **Legibility defect** (printed-keyword class, cf. the Fanfare keyword work). Read `CanonicalKeywords` on Kokomi's gain_charge / burst rows; fix at the generator. |

## B. Design observations ([USER], verbatim — NOT interpreted here)

- "Did a few playtests, never winning the game."
- "Kokomi's Charge mechanic is ridiculously powerful (often hitting for 100+) but otherwise suffers from low numbers... her best turn is usually 'spam companion cards to block until you can hit with the Charge'"
- "Inazuma companion cards are mostly 'block or do a little damage', nothing terribly interesting, so the Muster usually is just 'hope you get some block'"
- "Cards in the mod generally have a LOT of words compared to cards in the base game. I feel like this could all use some sort of grammar standardization / cleanup pass"

**Routing (Claude, no verdicts):** these are [USER]'s post-playtest design calls and belong in QUEUE §1 (Kokomi band / playtest / levers) and §5 (post-playtest design calls, `M45`), assembled as ONE slate for the next sitting (R206). Two engineering checks ride alongside, both harness-provable and NOT design: (1) whether a 100+ Charge hit is the sheet's arithmetic or an uncapped/unconsumed accrual (a `CHARGE_PER_EXHAUST`-class read; note `S4-G13`'s staged lever would RAISE accrual 1→2, so the observation bears on that pick); (2) the card-text word count per card vs the base game, as a measured table before any grammar pass is scoped.

## C. Not in this file

No Answers-block entries (that block belongs to the confirmatory run). No band. No lever pulled. No ids minted: the next `EB` block is reserved by the dispatch-3 charter; [USER] assigns.

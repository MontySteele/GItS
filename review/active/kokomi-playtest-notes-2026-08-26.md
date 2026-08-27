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
| A1 | "what does Pearl Barrage even do? Seems to just do 5 damage all the time." | Sheet (`docs/kokomi-cards.yaml:428-430`): exhaust 1 chosen card, deal 5 + 3 × that card's cost (ladder 5/8/11). Generated C# (`Cards/Kokomi/Generated/PearlBarrage.cs`) reads the cost through `CalculatedDamageVar(...).WithMultiplier(ExhaustSelection.Cost(card))`. `ExhaustSelection.Close()` does NOT clear the record and `Current()` stays in scope, so the record is there at attack time. Leading hypothesis: the base game computes the calculated var when the card is rendered/played (multiplier 0, no selection yet) and does not recalculate mid-`OnPlay`, so the attack lands at the base 5. Same shape on the sibling at `docs/kokomi-cards.yaml:639` (5 + 2×cost to all enemies). | **NOT A DEFECT** (2026-08-27, `EB-151` closed). The harness proved it twice on `0.2.1209`: `pearl-barrage-cost-ladder` PASS 5/5 (8 at cost-1, 11 at cost-2) and `tide-of-names-cost-ladder` PASS 2/2 (7 at cost-1) — and both also passed on the OLD build `0.2-1159`, before any change, so the hypothesis above was wrong and nothing was ever miscomputed. What misled the seat is that the face hid the +3 (fixed, commit 1 of R215): the printed number previews base + per × 0, so the card read "Deal 5 damage" until it resolved. [USER]'s design observation on the card is in §B and routes to the Kokomi slice. |
| A2 | "'All Hands' just adds 2 companion cards to my hand, rather than transforming 2 cards into companion cards." | Sheet row (`docs/kokomi-cards.yaml:808-811`): `{op: conscript, amount: 2, mode: create}`; generator emits `createMode: true`; printed text "Muster 2, adding the units to your hand." The default Muster (no `mode:`) is the other behaviour. | **As ruled, not a defect.** If [USER] wants All Hands to transform instead, that is a design pick → QUEUE (numbered, with the two Muster modes named). |
| A3 | "Vigil of the Deep adds 3 block after you take damage, rather than preventing 3 damage" — then: "On second look, Vigil of the Deep worked as expected another time. I might have misread the numbers the first time." | Not investigated (retracted). | **Withdrawn by [USER].** Keep an eye out; if it recurs, capture the exact numbers. |
| A4 | "Klee's cards that give Burst energy are labelled, but Kokomi's are not." | Not yet read. Klee's Burst-gain cards carry a printed keyword/rider; Kokomi's Charge/Burst gain appears to print none. | **Legibility defect** (printed-keyword class, cf. the Fanfare keyword work). Read `CanonicalKeywords` on Kokomi's gain_charge / burst rows; fix at the generator. |
| A5 | "Deep Breath's 'choose one' mechanic doesn't work - softlocks the game" (with a screenshot). | `godot.log` (same evening, `[ERROR] System.NullReferenceException`): the throw is in the BASE GAME's `NChooseACardSelectionScreen.AfterOverlayShown()`, reached via `NOverlayStack.Push` <- `NChooseACardSelectionScreen.ShowScreen(cards, canSkip)` <- `CardSelectCmd.FromChooseACardScreen` <- `KleeMod.Cards.ModalChoice.SelectMode` <- `Cards/Furina/Generated/DeepBreath.cs:70` (`OnPlay`). So our mode-choice helper hands the choose-a-card screen option cards that the screen's after-shown step cannot dereference; the awaited selection never returns and the turn hangs. | **CONFIRMED, FIXED, VERIFIED LIVE** (2026-08-27, `EB-150` closed). Fixed in `ModalChoice` and proven on the deployed `0.2.1209`: the `deep-breath-modal-choice` scenario is PASS 5/5, both modes resolve, and the scenario is committed as the regression proof. |

## B. Design observations ([USER], verbatim — NOT interpreted here)

- "Did a few playtests, never winning the game."
- "Kokomi's Charge mechanic is ridiculously powerful (often hitting for 100+) but otherwise suffers from low numbers... her best turn is usually 'spam companion cards to block until you can hit with the Charge'"
- "Inazuma companion cards are mostly 'block or do a little damage', nothing terribly interesting, so the Muster usually is just 'hope you get some block'"
- "Cards in the mod generally have a LOT of words compared to cards in the base game. I feel like this could all use some sort of grammar standardization / cleanup pass"
- (Klee run) "Klee's cards mostly strike me as boring flavors of 'attack and/or bomb' - compared to Ironclad, who has a similar intended attack-focused playstyle, she seems much less interesting. This run hasn't shown me many companion cards."
- (2026-08-27, on Pearl Barrage, after the harness read) "We need to show the real number somehow. Why can't we preview the real number?" — then, on being told the card reads the CHOSEN card's cost (R211): "Oh, I see. In that case I think the card is just bad. I thought it was tracking how many cards had been exhausted that whole turn."

**Routing (Claude, no verdicts):** these are [USER]'s post-playtest design calls and belong in QUEUE §1 (Kokomi band / playtest / levers) and §5 (post-playtest design calls, `M45`), assembled as ONE slate for the next sitting (R206). Two engineering checks ride alongside, both harness-provable and NOT design: (1) whether a 100+ Charge hit is the sheet's arithmetic or an uncapped/unconsumed accrual (a `CHARGE_PER_EXHAUST`-class read; note `S4-G13`'s staged lever would RAISE accrual 1→2, so the observation bears on that pick); (2) the card-text word count per card vs the base game, as a measured table before any grammar pass is scoped.

## C. Not in this file

No Answers-block entries (that block belongs to the confirmatory run). No band. No lever pulled. Ids were minted the next morning (R214 released the block): A1 -> `EB-151`, A4 -> `EB-152`, A5 -> `EB-150`; A2 as ruled, A3 withdrawn. All three ids are CLOSED at R215 (2026-08-27): `EB-150` fixed and live-green, `EB-151` not a defect, `EB-152`'s Burst half shipped with its lint and its Charge half deferred into R213 E1's Charge reopening.

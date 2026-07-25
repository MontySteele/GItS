# Playtest — co-op A0, 2026-07-25 (Klee + Furina)

Two players, both A8 regulars in the base game. Ascension 0. **Full clear, "by
the skin of our teeth."** This is the input that produced the "Ship What We
Know" sprint (docs/ship-what-we-know-sprint-plan.md).

## Provenance of these notes

The observations below are recorded **as quoted in the sprint doc**, which is
the form they reached the repo in. Where a phrase is in quotation marks it is
verbatim from the sprint doc's citation of the session; the surrounding
description is reconstruction, not transcript.

**If fuller raw notes exist, they belong here and should replace this section.**
Flagging that explicitly rather than letting a reconstruction pass as a
transcript: the house rule is that the repo holds the artifact, and a partial
artifact that looks complete is worse than one that says what it is missing.

## THE BUILD DECODER — read this before treating any note as a bug

The build played **predates the read-only Fanfare rework.**

The fanfare sprint ratified, tested and shipped read-only Fanfare to the
**sim** and the **sheet**, then hard-gated the C# port (F-D) behind an F-C that
its own close-out says will never run. So the live C# layer still implemented
the **retired** design: a capped, spendable meter with no decay and no floor.

**Consequence: some notes below describe a kit that does not exist in the
design of record.** They are accurate reports about the build in front of the
players and say nothing about the design. Triage marks each one.

The port landed as track G-A on 2026-07-25 (commit `5e631f0`). **Every future
playtest is against the real kit; this one was not.**

## Notes and triage

| # | Note | Reads on | Track | Disposition |
|---|---|---|---|---|
| 1 | *"Furina fanfare still capped"* | **superseded kit** | G-A | **Not a bug.** An accurate description of a pre-F-D build. Fixed by shipping the design that already existed: Fanfare now decays, floors, and cannot be spent. |
| 2 | Best Friends Forever *"pulled the co-op partner's cards"* | live defect | G-B1 | **Real bug, fixed.** Root cause was deeper than an unfiltered query — the tracker stored no owner at all, so ownership was unrecoverable. |
| 3 | `nicole_celestial_gift` has no upgrade | live defect | G-C1/C2 | **Real bug, fixed.** It had a sheet delta all along; the delta was unexpressible, so the *generated* card's `OnUpgrade()` did nothing. Sim upgraded it, game did not. |
| 4 | Touch of Orobas swapped the starter for an effect-less placeholder | live defect | G-C3 | **Real bug, partly fixed.** Vanilla falls back to the Circlet for any starter it does not know. Klee and Kokomi now register upgraded forms. **Furina still does not** — see G-C3 in the sprint log for why, and note she is the character this was played on. |
| 5 | `rain_of_roses` *"weak"* | balance | G-D1 | Repriced one energy cheaper. PROPOSED. |
| 6 | `star_of_the_show` *"weak"* | balance | G-D2 | Printed bonus raised. PROPOSED. Bounded to the magnitude — spotlight's real problem is structural. |
| 7 | `controlled_demolition` *"seems weak"* | balance | G-D3 | Base bomb count raised. PROPOSED. |
| 8 | `ebb_and_flow` — *"???"* | **superseded kit** | G-D4 | **The confusion was correct about the build played.** See the ruling below. |
| 9 | Player *"went for engine pieces… rarely bothered"* with Salon | structural | G-E3 | **Deliberately not acted on.** Measured instead; the number is in the sprint log and it is large. Evidence for the pool-sweep pass. |
| 10 | A0 felt *"by the skin of our teeth"* to A8 players | difficulty | — | **Deliberately not acted on.** One more playtest first. |

## The `ebb_and_flow` ruling (G-D4)

Gated behind G-A by the sprint's ordering law, because the card is a different
card in the two builds. G-A has landed, so the ruling can be made.

*Ebb and Flow*: `encore_cost 1`, gain 3 Encore, draw 1.

**In the build played**, Fanfare was capped and pinned, so Encore churn fed a
meter that was already full. The churn genuinely did nothing. The *"???"* was
the correct reaction to the card in front of them.

**In the design of record**, the same churn mints **4 Fanfare** — 1 for the
Encore spent, 3 for the Encore gained — into a meter that fades 20% every turn
and therefore always has room. It nets +2 Encore and a card on top. That is
precisely the flux a decaying meter wants, and it is the card working as
designed.

**RULING: this is the legibility branch, not the redesign branch.** The card
justifies itself; what it does not do is *say* so. It gets a text fix, not a
pool-sweep redesign slot.

Scope note, so the ruling is not mistaken for the fix: the text change is a
**generator** change (a Fanfare-generation tip on Encore-churn cards), which
would touch every card carrying `encore_cost` or `gain_encore` — not one card.
That is more than the "cheap" the sprint budgeted for a single card, so it is
**named and not done here**. Partial mitigation already shipped in G-A: the
Fanfare meter's own tooltip now reads *"Generated by HP loss, Encore activity,
and Center Stage plays… fades by 20% at the start of each of your turns"*, so
the rule is at least discoverable in the run.

## What this sprint deliberately did NOT act on

**Salon going unused in co-op free-draft (note 9).** The sprint measured it
rather than responding to it, and the measurement is the strongest single
number the sprint produced — see G-E3. The design response belongs to the
pool-sweep pass.

**A0 feeling skin-of-teeth to A8 players (note 10).** One data point, and two
explanations are still entangled: a genuinely over-tuned A0, or a learning
curve on an unfamiliar roster with three custom resource systems. Those are not
separable from a single session, and they call for opposite fixes. **One more
playtest before this is a finding.** Recorded so it is not lost, and named in
the sprint's non-goals so it is not quietly acted on.

## The standing gap this session exposed

**Co-op has no sim backstop.** tier 0.5 models exactly one seat, so no run in
this repository could have found note 2 — and none could find the next one
either. Every co-op defect is play-derived until that changes. Building a
second seat is a design-stage question, named in the sprint's non-goals, and
not started.

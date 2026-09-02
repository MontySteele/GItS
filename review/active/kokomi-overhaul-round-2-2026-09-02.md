Status: OPEN (the Plan build's first round; the Opus seat played and the game hung, guarded since; the Codex seat's record and your run follow)

# Kokomi overhaul, round two: the Plan build's first seat

2026-09-02. Draft 6 (brief approved R241, slice on it) is built as PR
#266 and deployed as 0.2.2001+proto.dirty: the Bake-Kurage as a pet, a
card played on it carried out at the start of the next turn, Tamakushi
Casket striking for 2 Hydro on a debuff, the ten-card starter and the
26-card pool. The soak ran three fights clean, but the soak bot never
plays a card on the jellyfish, so it never touched the new path.

| Seat | Seed | Actions | Fights | Stopped by |
|---|---|---|---|---|
| Opus | DLTN172Y4QDB | 40 | fight 1 won at 56/80; fight 2 one blow from won | the game hung (section 2) |
| GPT (Codex) | after the fix | | | |

Record: `review/qa/blindplay/kokomi-overhaul-r2-opus/record.md`. Seat
numbers are floors, not fun claims (Guardrail 7).

## 1. What the Opus seat found in forty actions

1. **The tension is there from fight one.** "Now versus next turn, and
   it is a genuinely sharp tension because the cost is paid immediately
   either way. Every energy I put on the jellyfish is energy I do not have
   for block this turn, and I have to price it against an intent I can
   see." Twice it chose block over Battle Plan and once the reverse, "and
   all three felt like real reads rather than defaults."
2. **The morning read as a payoff.** "Round 2 opened at 5 energy with the
   front slime already Vulnerable and Weak and 6 HP lighter from the
   relic." And: "The 5/3 energy display is the first time the deck felt
   like an engine rather than a hand of singles."
3. **Battle Plan is automatic.** "Net +1 energy and a card for a one-turn
   delay is never wrong once the fight is longer than two rounds." The
   seat took a second copy as its only card reward. That is the number to
   watch in your run: a Plan that pays back more energy than it cost is
   the one card in the pool that is never a choice.
4. **Vanguard is free damage, and the relic pays 6 where its text reads
   4.** Vanguard costs 0 and applies two debuffs; the relic strikes twice,
   and the Vulnerable it applied first makes the second strike 3. By the
   rules that is right (the jellyfish's hit is a real hit), but the text
   should say so.
5. **A Plan-only card is a keystroke, not a choice.** Kurage's Oath,
   Vanguard and Battle Plan have one legal target, so "play it on the
   jellyfish" decides nothing; the choice lives on the two-line cards.
   Read the Field, 3 now or 8 at dawn, is the shape the seat wanted more
   of.
6. **Smaller reads.** Deep Current is dead in a single-target fight;
   Shrink, an attack-damage debuff, slides off planned damage because most
   Plans are Skills, which the seat liked; Coral Guard is "the flattest
   thing in the deck."

## 2. The hang, and the other defects

- **EB-292, the game hang.** The first non-finite value appears the
  moment the first card is ever played on the Bake-Kurage, in fight one;
  the game then errors every frame and runs out of memory in the base
  game's card trail a fight later, whose gap-fill loop never ends on an
  infinite distance. The build now refuses a non-finite value at the
  three doors it came through and logs the node chain, and a live
  scenario that plays two Plans on the pet and crosses the turn passes on
  0.2.2007+proto.dirty (PR #268). The source of the bad number was not
  reproduced in four targeted attempts on the seat's own seed, so the row
  stays open; the guard means it cannot take the game down again.
- **EB-293, text.** Vanguard prints "Exhaust." twice on one line; the Plan-only
  cards say nothing about having one target and the grammar offers them
  the normal play; the relic's text reads as 4 where it pays 6.
- **EB-294, the blind render.** An enemy's Hydro aura prints as `(buff)` beside
  `(debuff)`s, so the aura you applied reads as helping them; the bundle
  chooser prints no mark after a pick; an emptied reward screen still
  advertises `choose`.
- **EB-295, an HP question.** The first combat screen printed 64/80 with no HP
  cost taken; the seat's fight-one arithmetic (finished at 56 after one 8)
  confirms it started at 64. Something took 16 HP before the first fight.
- Not ours: Shrink rewriting the printed damage without a marker is the
  game's own preview; a second Weak not moving the intent is Weak's
  duration stacking; the map render is the known limitation.

## 3. Your run, and the four questions

The rules changed, so this is the "first build of a kit's rules" gate.
One act-one run, three or four fights including an elite, on the build
that carries the fix. A sentence each:

1. Did "now or at dawn" come up as a choice, and when did you plan?
2. Did a morning ever feel like a payoff?
3. Did the jellyfish's strikes off a debuff register, and did the 2
   matter?
4. Which card did you never want to play?

Two things to watch while you play: whether Battle Plan is ever not the
play, and whether Vanguard at 0 energy reads as a status card or as free
damage.

## 4. Picks

None owed. Two numbers are watch items for the next round, applied only
if the seats and your run agree: Battle Plan's rate (a Plan paying 2
energy for 1 is a loan at plus one; "Plan: gain 1 Energy and draw 2" is
the one-line change) and Vanguard's cost.

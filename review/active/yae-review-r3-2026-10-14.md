# Yae review r3: Sakura kinds, the Masterpiece, signature cards, 2026-10-14

Five blind Sonnet seats played build 0.2.5533 at A0. It was the first build
with typed Tenko that strikes **and** adds its bonus, with full-shrine plants
that strike, and with Sakura Channeling. Two seats were resumed mid-run after
seat-tool stops. Records: `seats/archive/yae-r3-*` in the session scratchpad.

## Result: her first win

| Seat | End |
|---|---|
| lane 2 | **Won** against Test Subject (act-3 boss), about 20 of 72 HP |
| lanes 4, 5 | Died to the Queen with Torch Head (act-3 boss), floor 48 |
| lanes 1, 3 | Died in act 2, floor 25 (Infested Prism; Ovicopter) |

Round 2 had no wins and two act-3 runs; round 1 had no wins in nine. The win
ran on Proofread+ Reprint, three Tenko Kenshin and Shrine Maiden's Guard
(a Reprinted Guard gave 54 Block), with Sakura at about Level 20. One seat
said Foxfire Sweep's Wildfire Tenko "ended fights in 1-2 turns", too strong
for act 1 and 2. The two act-2 deaths were the opposite problem: slow first
fights and no Block card in hand.

[USER]: "Wow, yeah - making the Tenko busted much have done the trick and unlocked her
runaway scaling." So the late game is found; the job now is to make it
cleaner and less all-or-nothing.

## 1. Sakura kinds (direction agreed)

[USER] agreed on 2026-10-14 to Defect-style kinds, with the defensive one as a
decoy: "Agreed on the decoy framing!" Yae does not shield. A fox illusion
draws the blow.

- **Each Sakura has a kind, set when it is planted.**
  - **Sakura** (Thunder, the default): strikes an enemy for 2 + its Level.
  - **Foxfire Sakura:** hits ALL enemies for 1 + its Level.
  - **Kitsune Sakura** (the decoy): a fox illusion draws the blow. You gain
    2 + its Level Block.
- **A Sakura acts** at the end of your turn, once more when it withers (Last
  Bloom), and when Tenko fires.
- **Planting into a full shrine** (amended after GPT's review: with kinds, the
  old rule could never change a full shrine's mix):
  - **Same kind as your oldest:** the oldest acts, refreshes to at least 3
    turns and gains a Level, as now. A one-kind shrine keeps its scaling.
  - **A different kind:** the oldest acts, withers, and the new Sakura takes
    its place at its printed Level. Changing the board's mix costs you an
    established Sakura.
  - **Amended 2026-10-17:** both branches act on the Sakura closest to
    withering (fewest turns left, the oldest on a tie; a Deadline Extension
    Sakura last), not the first planted. A run of Sakura Seals had refreshed
    slot 1 again and again while the other two ran out. [USER]: "I think
    that's closest to the expectation."
  - **Amended 2026-10-17 (Levels carry over):** the new Sakura takes the
    higher of its own Level and the replaced one's, and a Sakura (Thunder)
    now strikes for 1 + 2 per Level (`review/active/yae-sakura-levels-2026-10-17.md`,
    picks 1 (a) and 2 (a)).
- **Tenko** becomes one plain rule again: "Every Sakura acts now. Refresh them
  to at least 3 turns." The typed Tenko and its double effect go. This is the
  power cut: one action per Sakura, not two. The mix of kinds you planted
  decides whether Tenko is damage, AoE or Block.
- **Annotations on a Sakura** work on any kind: Red Ink adds 3 to what it does
  (damage, each enemy's damage, or Block); Fox Fire, Deadline Extension and
  Edict of Cleansing as now (Edict on damage kinds only).

**Cards that change:**

| Card | Now | Becomes |
|---|---|---|
| Shrine Maiden's Guard (C) | Gain 6 [9] Block. Tenko (Warding). | Gain 6 [9] Block. Plant a Kitsune Sakura. |
| Foxfire Sweep (C) | 4 [6] to ALL. Tenko (Wildfire). | Deal 4 [6] to ALL enemies. Plant a Foxfire Sakura. |
| Kitsune Guile (U) | 2 [3] Weak to ALL. Tenko (Wildfire). | Apply 2 [3] Weak to ALL enemies. Tenko. |
| Manuscript Pile (U) | Draw 2 [3]. Tenko (Offering). | Draw 2 [3] cards. Each Sakura lasts 1 more turn. |

Every other planting card plants a plain Sakura. Early defence improves
because the Common Guard now leaves a Block source behind.

## 2. The Masterpiece: Publishing stacks

[USER] asked whether Publish should be "many smaller buffs" or "some kind of
'super card' style effect that does something insane". Claude recommends the
super card:
- **Two layers on each card** (amended after GPT's review):
  - **The permanent stack:** every Published Annotation, kept for the run.
    Red Ink twice is +6; Reprint twice replays twice; Sakura Seal twice plants
    two.
  - **One temporary slot:** a combat Edit fills it, and another Edit replaces
    it. It never touches the stack. So repeated Proofreads cannot pile up
    Reprints within one fight.
  - **Publishing moves the temporary layer onto the stack,** once.
- **The real bound** is not "four to six". It is one Publish per elite and
  boss, plus every Seven Glamours you play (a Rare, Exhaust, usable in any
  fight). A seat round judges the Masterpiece with those rules, not with an
  assumed count.
- **Reprint, exactly:** a card's Reprints add up. On the card's first play
  each combat it replays once per Reprint layer, then those go inert for the
  combat. A new temporary Reprint arms one fresh replay. A copy is a new card:
  its Reprints are armed.
- Technically, one custom enchantment holds both layers and its tip lists
  them.

## 3. Signature cards (new)

| Card | Text |
|---|---|
| Second Printing (U Skill, 0) | Put an Annotated card from your Discard Pile into your hand. [It costs 0 this turn.] Exhaust. |
| Author's Copy (U Skill, 1 [0]) | Add a copy of an Annotated card in your hand (not an Author's Copy) to your hand. It keeps its Annotations. Exhaust. |
| Serial Novel (Rare Power, 2 [1]) | At the start of your turn, put a random Annotated card from your Discard Pile into your hand. |

**Author's Copy cannot copy an Author's Copy.** GPT found a loop: an
Author's Copy+ Annotated with Royalties, copied by another Author's Copy, makes
a 0-cost copy that copies the original again, for +1 Energy each time. LAW
forbids energy-positive copy loops ("copy effects never make an
energy-positive loop"). Banning copies of generated cards would not close it,
because the target is the original in hand.

Bestseller and Print Run stay as support. **Watch:** a Masterpiece makes one
card matter a lot. The round should say whether runs feel more dependable or
more dependent on drawing one card.

## 4. Seat cleanup

- **Fallen Petals** was the "never again" card in four records: seats refresh
  Sakura, so they never wither. It becomes an active evoke, **Fallen Petals**
  (U Skill, 0): "Your oldest Sakura withers (it acts once, its Last Bloom). If
  one did, gain 1 Energy [and draw 1 card]." One action in total, and nothing
  with no Sakura.
- **Seat page:** mark Published cards; warn that a two-card Edit opens a
  second chooser; say where a Sakura's Levels came from.
- **Watch next round:** Inked Branches, Print Run, Royalties and Sakura
  Channeling (all passed or unused).

## Picks

**Ruled 2026-10-14: both picks (a), as amended.** [USER]: "Let's send it." And on
the bound: "I do think that the masterpiece strategy will scale more than you
think... an aggressive run can do 3 elites per act + 2 bosses = 11 mods before
the final fight before a Power gives anything more. But as a payoff strategy,
that might also just be 'fine.'" So the round should look at runs that take
many elites, not only typical ones.

[USER] on the plan: "I like the new direction!" GPT's sanity check
recommended the amended defaults below, and this page now carries them.

1. **This plan as a whole** (kinds, Masterpiece, three signature cards,
   Fallen Petals).
   - **(a, default)** Build all of it as amended (full-shrine replacement by
     kind, the real Publish bound, Author's Copy closed), then a five-seat
     round.
   - (b) Kinds first, Masterpiece and signature cards in a later round.
2. **An Edit on a Published card.**
   - **(a, default)** It fills the one temporary slot, which a later Edit
     replaces and a Publish moves onto the stack.
   - (b) Published cards stay closed to Edits; only Publish adds.

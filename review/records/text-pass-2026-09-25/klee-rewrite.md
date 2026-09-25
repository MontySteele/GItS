# Klee arm: text rewrite (from `textpass/klee.md`, 2026-09-25)

TEXT ONLY. No number or behaviour moves. Keep every `{Var:diff()}` token where
the old text had one; numbers shown here are base values. Numbers in tips and
badges stay interpolated from their Law constants (e.g. the growth of 4).

## The tips that matter most (they print on nearly every card)

| Tip | New text |
|---|---|
| Bomb | Deals its size in [gold]Pyro[/gold] damage when [gold]Set off[/gold]. Grows 4 at the start of your turn. If its enemy dies, it jumps to another. |
| Mine | A [gold]Bomb[/gold] that also goes off just before its enemy attacks. |
| Set off | Every [gold]Bomb[/gold] on the enemy goes off, oldest first. A random Set off picks an enemy with Bombs. |

- **Dropped from the tips**, deliberately: "Block stops it" (it is ordinary damage),
  "only Vulnerable and the HP cap move it", "a second Bomb stacks beside the
  first", "no when-hit power fires", "the first takes the aura", and "the hit
  still lands unless the Mine kills". These are edge cases a player learns by
  playing.
- **The seat glossary** may keep ONE short edge-case line per keyword if a seat
  test needs it. Report what you kept.
- **The lint EXCEPTIONS** for BombKey, SetOffKey and MineKey are removed; all
  three must now fit the ceiling.

## The Bomb pile badge on the enemy (ProtoBombPower)

**Static description** (reward shelf, compendium): `Klee's Bombs. They deal their size in [gold]Pyro[/gold] damage when [gold]Set off[/gold] and grow at the start of her turn.`

**The live smart-badge grid** is rebuilt from at most three short sentences:

1. `Set off here deals {N} [gold]Pyro[/gold] damage` + (only if a reaction) ` with {Reaction}` + (only if Sparks > 0) ` and gives {S} Spark{s}` + `.`
   - The number already includes Vulnerable and the HP cap. DROP the words
     "after Vulnerable", "capped by Hard To Kill" and "in N hits".
2. `Bombs here, oldest first: {sizes}` + (only if Mines) `, including {M} Mine{s}` + `.`
3. (Only when a rider is present) `One drops Mine {P} on ALL enemies when it goes off.`

- **DROPPED from the grid:** "growing each turn / at your turn's start", "None
  goes off by itself", "If the enemy dies with them on, they move to a survivor",
  and the long Mine clause. The Bomb and Mine tips carry these.
- **Ceilings.** The common case (no reaction, one Bomb) must fit 125. The rider
  variants may exceed 125. If they do, keep ONE named lint exception for the
  rider rows only, and report their length.

## Shared Burst tip (KleeCardTooltips.ForBurst / BurstBody)

`Fills {5} from each Elemental Skill card and each [gold]Elemental Reaction[/gold]. When full, your Burst card joins your hand, and casting it empties the meter. {12}/{40}.`

- Keep the live numbers where the old tip had them. Drop "energy past full is
  lost at the cast".
- If a character's actual fill rule differs from this text, STOP and report.

## Cards

| Card | New face |
|---|---|
| Hair Trigger | Your [gold]Bombs[/gold] on the enemy become [gold]Mines[/gold]. Draw 1 card. |
| Rapid Fire | [gold]Set off[/gold] a random enemy and deal 3 damage to it, 4 times. |
| Vermillion Pact (card + badge) | Whenever one of your [gold]Bombs[/gold] triggers an [gold]Elemental Reaction[/gold], the Attack that [gold]Set[/gold] it [gold]off[/gold] triggers one too. (If splitting the gold markup breaks the tip attach, use `the Attack that Set it off` with Set off in gold as one token. Your call; report it.) |
| Coven Errand | Place a [gold]Bomb[/gold] 5 on the enemy, or on ALL enemies if you played a [gold]Companion[/gold] card this turn. |
| Team Effort | [gold]Set off[/gold] the enemy, or ALL enemies if you played a [gold]Companion[/gold] card this turn. Deal 6 damage. |
| Return to Sender | Gain 8 [gold]Block[/gold]. This turn, damage that Block absorbs becomes a [gold]Bomb[/gold] on the attacker. |
| ReturnToSenderPower (badges) | This turn, damage your Block absorbs becomes a [gold]Bomb[/gold] on the attacker. |
| Big Bounce | [gold]Set off[/gold]. Deal 5 damage. Explosion damage past the enemy's HP hits a random other enemy. |
| Windblume Fireworks | [gold]Set off[/gold] ALL enemies, deal 10 damage to them, and place a [gold]Bomb[/gold] 6 on each. |
| Fish Fry | Deal 7 damage to ALL enemies. Enemies with a [gold]Bomb[/gold] take 5 additional damage. |
| SecondSurprisePower (badge) | Whenever one of your [gold]Mines[/gold] goes off, place a [gold]Bomb[/gold] half its size, rounded down, on that enemy. |
| Careful Arrangement | Move all your [gold]Bombs[/gold] onto the enemy as one Bomb. It grows by 5, and is a [gold]Mine[/gold] if any of them were. |
| Big Badda Boom | [gold]Set off[/gold]. Deal 12 damage plus the damage your Bombs dealt. |
| Careful Now | Gain [gold]Block[/gold] equal to your largest [gold]Bomb[/gold], up to 10. |
| All of My Treasures! | Place a [gold]Bomb[/gold] the size of your largest Bomb on the enemy. |
| Sit Tight (card + badge) | Gain 5 [gold]Block[/gold]. At the end of your turn, gain 4 Block if none of your [gold]Bombs[/gold] went off. |
| Patience, Klee! (card + badge) | At the end of your turn, if you played no [gold]Set off[/gold] card, your largest [gold]Bomb[/gold] grows by 4. |
| Wait For It... (card + badge) | The next time a [gold]Bomb[/gold] triggers an [gold]Elemental Reaction[/gold] this turn, draw 2 cards and gain 1 [gold]Energy[/gold]. |
| GroundedPower (unpaid badge) | You played a [gold]Set off[/gold] card last turn, so no Block or Spark this turn. |
| The Big One | [gold]Set off[/gold]. Your [gold]Bombs[/gold] deal quadruple damage. |

## Truthfulness checks before wiring

- **Sit Tight and Patience, Klee!** "At the end of your turn … went off / played no
  Set off card" must mean THIS turn. Confirm it.
- **The Big One.** Confirm that quadruple applies to the Bombs only, not to any
  other damage. The face has no other damage, so the new face is exact.
- **Big Badda Boom.** Confirm "12 damage plus the damage your Bombs dealt" lands as
  one hit or as two. If it is two hits (Block and Vulnerable apply twice), write
  `Deal 12 damage, then damage equal to what your Bombs dealt.`

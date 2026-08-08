# Test Subject

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

> **ACCEPTED OUTLIER (R131, 2026-08-07; closes `EB-29s`).** The full-HP
> instrument reads ~0% winrate here against 90–98% for every other act-3 boss.
> That is WORKING AS INTENDED: the sim pilot is worse than a real player, the
> sim stays accurate to the game rather than to the pilot, and the brutal
> numbers below stand as authored. Any quoted `test_subject` winrate cites this.

- **Class:** `TestSubject`
- **Kind:** boss
- **Act:** 3 (Glory, act index 2)
- **Encounter:** `TestSubjectBoss` — single slot, boss room, custom background, custom BGM `act3_boss_test_subject`
- **Fight class:** **mixed**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

The Test Subject is the second of Act 3's three bosses in the act's boss discovery order (behind the
Queen, ahead of Aeonglass). The encounter spawns exactly **one** creature and nothing else — no
minions, no summons, no adds at any point in the fight.

Its displayed name carries a **running specimen number**: the localized title interpolates a count
equal to 8 plus the player's lifetime Test Subject kills recorded in the profile save. This is
persistent across runs and purely cosmetic — "Test Subject #8" on a fresh profile, incrementing every
time you kill it. The in-run kill counter is also bumped the first time it is knocked down, not when
the fight ends.

The fight drives a music-progress parameter through four steps: entry, first knockdown, each
respawn, and the true death. There is no gameplay hook on any of it.

It takes damage with the "armor" sound family, and while it still has its revive power its death
sound is a **knock-out** cue rather than a death cue — an audio tell that the corpse is not final.

## Intent pattern

The move machine is **fully deterministic — no random branches anywhere**. The only branch in the
graph is a conditional one that reads the respawn counter. The whole fight is three phases separated
by two forced deaths, and the player controls when each transition happens by dealing damage.

### Phase 1 — first form (before any respawn)

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Bite** | single AoE attack, 20 | attack |
| 2 | **Skull Bash** | AoE attack 14, then Vulnerable 1 to every player | attack + debuff |

These two point at each other, so Phase 1 is a strict A-B-A-B alternation starting on Bite,
continuing until the form is knocked down. Nothing else can happen in Phase 1.

### The knockdown interrupt

The Test Subject carries an **Adaptable** power from setup. When its HP reaches zero, that power
prevents removal from combat, prevents the combat from ending, and immediately **forces the next
intent to Respawn**, overriding whatever was already telegraphed and refreshing the intent display on
the spot. Whatever move you were about to eat is cancelled.

The Respawn state is flagged must-perform-once, so the machine cannot skip past it: the boss spends
its entire next turn reviving and deals **zero damage on that turn**. During the revive window the
Adaptable power also **blocks the creature from being hit or receiving powers**, so pre-loading
debuffs onto the corpse does not work.

Respawn shows a **heal + buff** intent pair.

### Phase 2 — second form (respawns == 1)

Revives at full second-form HP, gains **Painful Stabs 1**, and grows visually 10% larger.

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| loop | **Multi Claw** | multi-hit AoE attack, 10 per hit, **hit count starts at 3 and permanently increases by 1 after every use** | multi-attack (×N) |

Multi Claw follows onto itself, so Phase 2 is a single move repeated forever with a hit count that
never resets: 3 hits, then 4, then 5, then 6… The counter lives on the monster, not the state, and is
never cleared.

### Phase 3 — third form (respawns >= 2)

Revives at full third-form HP, grows 20% larger, gains **Nemesis**, and **loses both Adaptable and
Painful Stabs**. From this point the boss can die for real, and the Wound generator is gone.

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Lacerate** | multi-hit AoE attack, 10 × **3** (fixed — does not inherit the Multi Claw counter) | multi-attack (×3) |
| 2 | **Big Pounce** | single AoE attack, **45** | attack |
| 3 | **Burning Growl** | 3 Burns into every player's discard, +2 Strength to itself | status + buff |

Three-beat loop, forever, starting on Lacerate immediately after the second revive.

### Bestiary display note

**Bite, Skull Bash and Lacerate are hidden from the bestiary.** A player who scouts this boss sees
only Multi Claw, Big Pounce, Burning Growl and the Respawn — i.e. the escalating claw and the 45 are
advertised, while the entire Phase 1 pattern and the Phase 3 opener are not.

## Damage / block numbers

The Test Subject gains **no block at any point in the fight** — there is no defend move and no block
source on any of its powers. Every point of its HP has to be chewed through raw.

| Stat | Base | Ascension variant |
|---|---|---|
| First-form HP (min = max, no roll) | **100** | **111** at A8 `ToughEnemies` |
| Second-form HP | **200** | **212** at A8 |
| Third-form HP | **300** | **313** at A8 |
| Total HP across all three forms | **600** | **636** at A8 |
| Bite | 20 | 22 at A9 `DeadlyEnemies` |
| Skull Bash | 14 | 16 at A9 |
| Skull Bash — Vulnerable applied | 1 | 1 |
| Multi Claw — damage per hit | 10 | 11 at A9 |
| Multi Claw — starting hit count | 3 | 3 |
| Multi Claw — hit count growth per use | +1 | +1 |
| Lacerate — damage per hit | 10 | 11 at A9 |
| Lacerate — hit count | 3 (fixed) | 3 |
| Big Pounce | **45** | **45 — not ascension-scaled** |
| Burning Growl — Burns added | 3 | 5 at A9 |
| Burning Growl — Strength gained | 2 | 3 at A9 |
| Enrage — Strength per player Skill played | 2 | 3 at A9 |
| Painful Stabs — Wounds per unblocked hit | 1 | 1 (Phase 2 only) |

### Base-difficulty incoming per turn

Assuming a solo player who knocks the form down on their turn immediately before each listed enemy
turn, no Enrage triggers, and Vulnerable ignored (it lands turn 2 and ticks off turn 3, so it inflates
one Bite by 50% per cycle if you are still in Phase 1):

| Enemy turn | Move | Raw damage | Side effect |
|---|---|---|---|
| 1 | Bite | 20 | — |
| 2 | Skull Bash | 14 | Vulnerable 1 |
| 3 | Bite | 20 (30 if Vulnerable is live) | — |
| … | alternating | 20 / 14 | — |
| *knockdown* | **Respawn** | **0** | second form, Painful Stabs |
| n+1 | Multi Claw ×3 | 30 | 3 Wounds |
| n+2 | Multi Claw ×4 | 40 | 4 Wounds |
| n+3 | Multi Claw ×5 | 50 | 5 Wounds |
| n+4 | Multi Claw ×6 | 60 | 6 Wounds |
| *knockdown* | **Respawn** | **0** | third form, Nemesis |
| m+1 | Lacerate 10×3 | 30 | — |
| m+2 | Big Pounce | 45 | — |
| m+3 | Burning Growl | 0 | 3 Burns, Str→2 |
| m+4 | Lacerate 12×3 | 36 | — |
| m+5 | Big Pounce | 47 | — |
| m+6 | Burning Growl | 0 | 3 Burns, Str→4 |
| m+7 | Lacerate 14×3 | 42 | — |
| m+8 | Big Pounce | 49 | — |

Three separate shapes fall out of this:

- **Phase 1 is flat and cheap** — 20/14 alternating on a 100 HP bar. This is the softest opening of
  any Act 3 boss; it exists to let you set up.
- **Phase 2 is the only runaway in the fight** — +10 damage *and* +1 Wound every single turn, with no
  cap and no reset. It crosses Big Pounce's 45 on its fifth use and keeps going. Any deck that cannot
  kill 200 HP inside roughly five turns loses here, and it loses to the deck-clog as much as to the
  damage.
- **Phase 3 is a rhythm, not a ramp** — 75 damage per three turns before Strength, +8 per completed
  loop (Strength is worth ×3 on Lacerate and ×1 on Pounce). Every third turn is a free turn.

### The Strength multiplier

Strength enters from two sources — Burning Growl (Phase 3 only) and **Enrage, which is live from
setup for the entire fight**. Its per-move leverage is wildly uneven:

| Move | Value of +1 Strength |
|---|---|
| Bite / Skull Bash / Big Pounce | +1 |
| Lacerate | +3 |
| Multi Claw | **+N**, where N is the current and still-growing hit count |

Multi Claw at 6 hits converts every point of Strength into 6 damage per turn, then 7, then 8. This is
the single most dangerous interaction on the sheet, and it is entirely under player control — see
Enrage below.

## Gimmicks

### Adaptable (the two false deaths)

Not a phase threshold and not a scripted HP gate: the boss genuinely dies, and the power catches it.
Consequences worth modeling:

- It **stops combat from ending** and **stops the creature being removed** on death, and survives the
  owner's death itself, so the usual "reduce to 0, fight over" logic never fires in forms 1 and 2.
- Overkill is **wasted**. Excess damage past 0 does not carry into the next form; every point spent
  past lethal on form 1 buys nothing.
- Each knockdown **costs the boss a full turn**. Killing form 1 or form 2 on your turn buys you a
  guaranteed zero-damage enemy turn, which makes the knockdown itself a defensive tempo play.
- Because the revive window blocks hits and power application, you cannot stack debuffs on the corpse
  in advance of the next form.
- The revive **sets max HP and then heals to it**, so max-HP reduction or leech effects applied to a
  previous form are erased at the transition.
- Removal-style effects that make a monster disappear outright are **suppressed until the third
  form** — the boss explicitly refuses to vanish while it still has respawns left, so it cannot be
  skipped past. It becomes a legal target for that class of effect only once it is in its final form.

### Painful Stabs (form 2 only)

While in form 2 it has Painful Stabs 1: **every unblocked hit of an attack adds 1 Wound to that
player's discard pile**, counted per hit and per player. Combined with the growing Multi Claw count,
partial blocks are actively punished — a turn where you block 3 of 5 claw hits still hands you 2
Wounds. A turn where you block all of them hands you none.

Cumulative Wounds across a five-turn form 2, unblocked: 3+4+5+6+7 = **25 Wounds** in the discard
pile. This is the fight's real clock: it does not kill you, it dilutes the deck you need to kill form
3 with. Painful Stabs is stripped on the second revive, so the total is capped by how fast you clear
form 2.

### Nemesis (form 3 only)

At the end of every enemy turn, Nemesis **toggles**: on odd toggles it applies Intangible 1 to the
boss, on even toggles it removes it. Intangible caps all damage received at **1 per hit**, and the
boss is drawn half-transparent while it is up.

Because the toggle has period 2 and the move loop has period 3, the fight settles into a **6-turn
combined cycle**. Working from the second revive:

| Player turn | Boss state | Enemy turn that follows |
|---|---|---|
| 1 | **Intangible — damage capped at 1/hit** | Lacerate |
| 2 | vulnerable, full damage | Big Pounce 45 |
| 3 | **Intangible** | Burning Growl |
| 4 | vulnerable, full damage | Lacerate |
| 5 | **Intangible** | Big Pounce |
| 6 | vulnerable, full damage | Burning Growl |

**Half of Phase 3 is unkillable.** Effective HP for pacing purposes is not 300, it is 300 spread over
twice as many turns — call it a 600-HP-equivalent phase — and every one of those extra turns is a
turn of Burn accumulation and Strength growth. The cap is per hit, so multi-hit damage plans are
punished the hardest on Intangible turns while a single big hit loses the least in relative terms.
Correct play is to dump nothing on Intangible turns and bank resources for the open ones.

### Enrage (whole fight, player-driven)

Applied at setup at 2 stacks (3 at A9): **every Skill any player plays gives the boss that much
Strength**, permanently, for the entire fight. Nothing about this is telegraphed by an intent.

This is the fight's central tension and it is completely self-inflicted. A defensive deck playing
three Skills a turn hands the boss +6 Strength per turn, which by the middle of Phase 2 is worth
+36 or more damage per Multi Claw. The Test Subject's low base numbers are priced on the assumption
that the player is feeding it. Notable corollaries:

- Block-heavy survival plans are anti-synergistic with the exact phase (2) where you most want block.
- Attack-only turns are strictly safe.
- The Strength gained is never removed and carries **across knockdowns and revives** — only the
  Adaptable and Painful Stabs powers are cleaned up at the second revive, not Strength.

### Burns (form 3)

Burning Growl adds 3 Burns (5 at A9) to **every** player's discard pile per use, once per three-turn
loop, with no cap. It is the mirror of Phase 2's Wounds: Wounds clog you while the damage ramps,
Burns clog you while the damage is on a rhythm — and Burns also bite back when drawn. A Phase 3 that
runs four loops long has put 12 Burns (20 at A9) into the deck on top of whatever Wounds survived
Phase 2.

## Scaling

**By act:** none. The Test Subject exists only in Act 3; the act index is read only through the
shared multiplayer HP formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | HP 100/200/300 → 111/212/313 (total 600 → 636, only +6%) |
| A9 `DeadlyEnemies` | Bite 20→22, Skull Bash 14→16, Multi Claw 10→11 per hit, Lacerate 10→11 per hit, Burning Growl Burns 3→5 and Strength +2→+3, Enrage 2→3 per Skill |

Two things stand out. First, **Big Pounce is the only attack in the fight that does not scale with
ascension** — the 45 is a constant, which means it shrinks in relative importance at A9. Second, the
A9 change to **Enrage is worth more than every damage number combined** for a Skill-heavy deck: going
from +2 to +3 per Skill is a 50% increase on the fight's dominant multiplier, and it lands on the
Multi Claw hit count. The A8 HP bump is nearly irrelevant by comparison.

**By seat count (multiplayer):**

- **All three form HPs scale** by the standard formula: base × players × 1.3 (Act 3 **boss-room**
  multiplier). The first form is scaled at spawn; the second and third are scaled explicitly at each
  revive, using the same formula, so the phase structure is preserved at every seat count.

| Players | Form 1 | Form 2 | Form 3 | Total |
|---|---|---|---|---|
| 1 | 100 | 200 | 300 | 600 |
| 2 | 260 | 520 | 780 | 1560 |
| 3 | 390 | 780 | 1170 | 2340 |
| 4 | 520 | 1040 | 1560 | 3120 |

- **Every attack is AoE.** All five attacks are built as monster attacks against all opponents, so
  each seat takes the full listed number — Multi Claw at 6 hits is 6 hits *on each player*, not split.
  Party-wide incoming scales linearly with seats on top of the HP scale.
- **Skull Bash's Vulnerable and Burning Growl's Burns hit every player**, undiluted; each seat gets
  its own 3 (or 5) Burns per Growl.
- **Painful Stabs is resolved per player per unblocked hit**, so a four-seat party eats up to 4× the
  Wounds of a solo run at the same claw count.
- **Enrage listens to every seat's Skills.** This is the largest co-op swing in the fight: a
  four-player party naturally plays roughly four times as many Skills per round, so the Strength ramp
  can run ~4× faster while the boss's hit count is simultaneously growing. Co-op parties should expect
  Phase 2 to be dramatically more lethal than the solo table suggests.
- Nemesis, Adaptable and the respawn structure are unchanged by seat count — Intangible is a property
  of the boss, so the "half of Phase 3 is unkillable" tax applies to the whole party at once.

## Proposed fight class: **mixed**

Three forms make three genuinely different demands and no single curve covers them. Phase 1 asks for
almost nothing — flat 20/14 into a 100 HP bar — and exists as a setup window. Phase 2 is a pure
**race with a hard, uncapped ramp**: +10 damage and +1 Wound every turn with no reset, so the demand
is concentrated burst inside roughly five turns, and failing it loses to deck dilution as much as to
damage. Phase 3 flips to a **timing puzzle** — Intangible on alternating turns means half your damage
output is legally worthless and the real requirement is banking resources for the open turns while
surviving a 45-point spike on a fixed three-beat rhythm. Underneath all three sits Enrage, a
player-driven multiplier that punishes the exact defensive play the middle phase invites, which makes
the fight's difficulty partly a function of deck composition rather than turn count. For Track B,
model this as three sequential demand vectors joined at two player-timed breakpoints (low, then
burst-under-a-clock, then alternating burst-window), with a global Strength term proportional to the
party's Skills-played rate and a per-hit rider (Wounds in phase 2, damage cap in phase 3) that makes
hit *count* the load-bearing variable rather than raw damage.

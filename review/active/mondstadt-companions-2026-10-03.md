# Mondstadt companions: a pool review

Paper, 2026-10-03. Main session design. [USER], after his Klee finish-line
run: "'Mona - Stellaris Phantasm' seems undertuned - actually maybe we should
review the entire Mondstadt companion pool."

## 1. What the pool is

`proto_mc_` rows in `docs/prototype-surface.yaml`: 48 cards (18 Common / 19
Uncommon / 11 Rare; 45 Mondstadt, 2 Liyue, 1 Inazuma). The fourth card of a
reward (`CompanionSlot.Roll`) offers them to every character. 13 carry
`personal_pool: klee` because they read Bombs, Mines, Grounded or statuses;
the other **35 reach Klee, Kokomi, Furina and Varka alike**. A row with no
`upgrade` takes the generator's default delta (`prototype_default_delta`),
so no card is un-upgradable.

Yardsticks, base game: Strike 6, Defend 5; a Common 1-cost Attack about 9
damage with a rider, a Common Block Skill about 8 (Shrug It Off 8 and draw,
Survivor 8 and discard); Shockwave (U, 2, Exhaust) 3 Weak and 3 Vulnerable to
ALL now.

## 2. Findings

Most of the pool sits on the yardsticks: the 1-cost Attacks at 7 to 10 with a
rider (Fischl's two, Kaeya's two, Razor, Rosaria, Jean — Gale Blade), the
Block Skills at 6 to 7 with a rider, the timed Skills at about 15 to 18 over
their turns ([USER] kept them, AoE trim sec.6). Five do not:

| Card | Today | Problem |
|---|---|---|
| Mona — Stellaris Phantasm (R, 2, Exhaust) | Hydro to ALL; next turn, 2 Vulnerable to ALL | a Rare below Shockwave: half its effect, a turn late, the same cost |
| Noelle — Breastplate (C, 1) | 6 Block, 4 more below half HP | a Defend +1 above half HP; the low-HP half rarely matters |
| Sucrose — Wind Spirit Creation (U, 0) | Swirl the enemy, draw 1 | Sucrose — Mollis Favonius is the same card plus "reactions deal 4 more this turn", same cost and rarity; four Sucrose cards in one tier |
| Amber — Fiery Rain (U, 1) | 4 Pyro to ALL, 3 times | 12 to every enemy for 1 Energy; the AoE trim counted the kits, not this pool, and this card reaches all four |
| Amber — Explosive Puppet | C | ruled to Uncommon today (Klee finish-line batch) |

The pool's AoE: Fiery Rain, Mika — Starfrost Swirl, Venti — Wind's Grand Ode,
Durin — Binary Form (White), Amber — Explosive Puppet and Sucrose —
Astable Anemohypostasis hit or Swirl ALL, on top of each kit's own count. Only
Fiery Rain is far above its tier.

## 3. Changes

| Card | Becomes | Why |
|---|---|---|
| Mona — Stellaris Phantasm | 1 Energy, Exhaust: "Apply Hydro and 3 [4] Vulnerable to ALL enemies." | Shockwave's Vulnerable now, cheaper, with the aura; a Rare that sets up a team turn |
| Noelle — Breastplate | 8 [11] Block; 4 more below half HP | a Common Block Skill at the yardstick; the rider stays a bonus |
| Sucrose — Wind Spirit Creation | 1 Energy: "Swirl ALL enemies. Draw 1 card." (upgrade draw 2) | the repeatable spread at a price; Astable stays the free Exhaust one-shot; no longer a subset of Mollis |
| Amber — Fiery Rain | 3 Pyro to ALL, 3 times (upgrade 4) | 9 to each enemy, still the pool's best AoE; three Pyro applications keep it a reaction card |

Pool counts do not move (no row added or cut). Sim: Klee's and Varka's
smoke sims rerun on the change, as a check, not a gate.

## Picks

[USER], 2026-10-03: "Agreed on the Mondstadt pool changes you proposed."

1. **Mona, Breastplate, Fiery Rain as in sec.3.** Default: yes.
   **RULED (2026-10-03): yes**, at the default.
2. **Wind Spirit Creation becomes the repeatable Swirl ALL** (or cut it and
   let the Uncommon tier hold three Sucrose cards). Default: the rewrite.
   **RULED (2026-10-03): the rewrite**, at the default.

Built: Mona's next-turn omen power (`mc_omen` / `StellarisOmenPower`) had no
other user and is deleted in both engines. Wind Spirit Creation now costs 1
while its Klee stand-in Sucrose — Mollis Favonius keeps 0; the stand-in pin
that required equal cost exempts that one pair (rarity still matches).

## 4. The Klee-only companions (ruled)

[USER], 2026-10-03: "Yeah, agreed on all of these." Then, on Kitchen Alchemy:
keep it, "it's quite good!", and cut Once More! in its place.

The 13 `proto_mc_` rows with `personal_pool: klee`:

| Change | Rows |
|---|---|
| To the shared pool (they read nothing of Klee's) | Qiqi — Herald of Frost, Fischl — Undone Be Thy Sinful Hex, Sucrose — Mollis Favonius, Nicole — Ladder of Divine Ascent |
| Cut (each reads Bombs, Mines or Grounded and has a near-twin in the shared pool) | Barbara — Front Row Seat, Diona — Shaken, Not Purred, Noelle — I Got Your Back, Kaeya — Cold-Blooded Strike, Sayu — Yoohoo Art: Silencer's Secret, Yaoyao — Yuegui: Throwing Mode |
| Into Klee's own draftable pool (text, numbers and rarity unchanged; still Companion cards) | Albedo — Dust of Purification (R), Jean — Lion's Fang, Fair Protector (R), Prune — Ring-A-Ding-Ding! Hexhunter Chime (U) |
| Cut from Klee's pool to hold 78 and 24 / 33 / 21 | Second Surprise (R), Solitary Confinement (R), Once More! (U) |

Gorou — Crystal Collapse (Kokomi's) is untouched.

Counts: Klee's pool 78 (24 / 33 / 21); the shared Mondstadt roster 35 to 39
(38 Mondstadt and Qiqi, Liyue's); no Klee-only companion is left, so the
stand-in table and the coven Personal list are empty (the hand-off seam stays,
handing nothing off).

Built as worded, with four mechanical notes:

1. The three stand-ins that went to the shared pool also lose `replaces:`,
   not only `personal_pool:`. The sheet refuses `replaces:` without an owner.
2. The three rows in Klee's pool keep their `proto_mc_` ids. The arm-pool
   parity lint wanted the `proto_ko_` prefix; it now accepts the three by
   name (`C.KLEE_OWN_COMPANION_IDS`) rather than renaming them.
3. There is no `docs/retired-card-ids.yaml`. Each cut row is tombstoned in
   `docs/prototype-surface.yaml` the way earlier cuts were (an "IS CUT"
   comment where the row stood); art plan rows stay, as for earlier cuts.
4. Engine pieces only the cut cards used are deleted in both engines: the
   three caretaker watchers and Kaeya's Grounded blind, Yuegui, Second
   Surprise's half-size Bomb, Solitary Confinement's cost rule, and Once
   More!'s `return_last_set_off` op with the last-Set-off-card note it read.

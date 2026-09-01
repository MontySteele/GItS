# fontaine-companions.yaml - comment provenance

Long comment blocks that used to sit in `docs/fontaine-companions.yaml`. They
moved here on 2026-09-01 so an agent reading the sheet loads rows,
not prose. Blocks are verbatim and in sheet order.

A heading names the row the block was attached to. `before <id>`
means a column-0 section note that sat above that row. `header` is
the file header. Blocks of three lines or fewer stayed in the sheet.

## lynette_box_trick

```
   # Pure velocity glue. Plain by design: the pool's honest draw common; every archetype takes it, none warps around it.
   # RENAMED to canon 2026-08-10 ([USER], QUEUE N3+N4): the authored "Box Trick" named no Lynette talent; the
   # Bogglecat Box is the construct her Burst summons. The id stays `lynette_box_trick` — ids are not slugs of
   # titles here (codegen keys the C# class and the art path off the id), so the rename is display-only.
```

## charlotte_enduring_frosthelm

```
   # REDESIGNED per healing-policy tightening (heal = Rare AND Exhaust; sub-Rare sustain = Block only).
   # Pre-emptive block: 4 now + 4 at start of next turn — sustain-over-time identity without true healing.
   # RENAMED to canon 2026-08-10 ([USER], QUEUE N3+N4): the shipped "Enduring Frosthelm" named no Charlotte
   # talent at all. "First-Person Shutter" is [USER]'s pick among her three real passives (Moment of Impact /
   # Diversified Investigation / First-Person Shutter), and it reads onto the card: she braces behind the
   # camera and takes the shot. The id stays `charlotte_enduring_frosthelm` — ids are not slugs of titles here
   # (codegen keys the C# class and the art path off the id), so the rename is display-only.
   # NEW OP: block_next_turn. Spotlighted in a Furina deck the empowered
   # block is still Encore-adjacent tempo; the quiet synergy survives the conversion.
```

## before navia_cannon_fire_support

```
# ---------- FONTAINE 5-STAR RARES (v0.2, 2026-07-25 — R64/R65; ALL NUMBERS PROPOSED, awaiting red-pen) ----------
# The roster gap the shop-companion coverage lint found live: Fontaine designed ZERO Rare companions,
# graded by [USER] as a roster gap rather than a fallback quirk. Four characters, one card each (§4.2).
#
# THIS IS THE SET THAT TURNS THE BANNER ON. Four Rares against BANNER_FEATURED_SLOTS = 3 makes the
# Featured Banner selective for the first time anywhere (R64) — Mondstadt sits at exactly 3 and Inazuma
# at 2, so the roll has been a no-op everywhere until now. One of these four is excluded per run.
#
# Element spread honours §4.1's off-element lean for the home-nation slot: Geo/Electro/Pyro are all off
# Furina's Hydro; Neuvillette on-element is deliberate and accepted (he is the Hydro Sovereign, and D2
# rules his shared Rare is a DIFFERENT card from the Guest Star cameos below).
#
# §4.3 compliance, stated per card: all four are SUPPORT payoffs — buffs, reaction payoff, aura
# manipulation. None is an independent damage engine and none self-scales. Only one carries a damage
# body at all (Clorinde), and it is a fixed number on a card that also carries a power — not an engine.
#
# Healing law (Rare AND Exhaust, conjunctive) is satisfied VACUOUSLY: no card here heals. Arlecchino
# interacts with healing in the opposite direction — see her note.
#
# NAMES: checked against docs/reserved-card-names.txt and the in-repo sheets BEFORE proposing, per the
# kickoff. The check earned its keep — "O Tides, I Have Returned" was the natural Neuvillette pick and
# is RESERVED four lines below for his future playable kit-Burst. Following that precedent, each entry
# below records the Burst name it is deliberately NOT taking, so the next pass inherits the reservation
# instead of rediscovering it.
```

## navia_cannon_fire_support

```
   # ROLE: glue. The President of the Spina di Rosula pays the POOL rather than the character — the only
   # card in the game whose trigger is "a companion was played", which is exactly a companion-pool payoff.
   # NEW POWER: cannon_fire_support.
   # CRYSTALLIZE, deliberately avoided (kickoff Track A note — Zhongli's slot-4 archetype owns that space):
   # she applies no Geo, collects no shards, and pays no Crystallize rider. Her trigger is card-type, not
   # elemental, so nothing here pre-commits how Crystallize scales.
   # OVERLAP FLAGGED, NOT RESOLVED: Albedo's solar_isotoma is already "Geo defensive engine" (block off
   # attacks vs aura'd enemies). Navia stacks with it but does not duplicate it — different trigger
   # (companion play vs aura'd hit), different pool pressure. If red-pen reads two Geo block engines as
   # one too many, Navia is the one to move, because Albedo predates her and anchors Mondstadt.
   # Burst name "As the Sunlit Sky's Singing Salute" RESERVED for a future playable kit-Burst (v1.9).
```

## clorinde_impale_the_night

```
   # RATIFIED 2026-07-25 [USER]: "double that stat line to 20 damage and +6 vs auras", from 10/+3.
   # THE DOMINATION FLAG THIS ENTRY OPENED IS CLOSED — RAIDEN MOVED (2026-07-25 [USER]). Recorded in
   # full because the resolution is the interesting part: the doubling briefly made her out-hit Raiden's
   # Musou no Hitotachi (then 18, the sheet's stated "biggest one-card hit") at the SAME 2 cost while (lint-ok: cross-sheet superseded value)
   # also carrying a permanent power, where Raiden was deliberately shapeless to pay for her number.
   # No lint could have raised it — lint_strict_domination compares within a sheet, and the two live in
   # different nations' files. It was flagged here by hand for exactly that reason, and the red-pen
   # session took the third option: Raiden went to 3 cost / 40 damage / Vulnerable 2 / Exhaust. The two (lint-ok: cross-sheet ratified value)
   # cards no longer share a cost or a shape, and neither is strictly better than the other.
   # KEEP THE HAND-FLAG HABIT: cross-sheet comparisons are structurally invisible to the tooling.
   # ROLE: payoff. The Champion Duelist reads the board before she moves: her payoff is conditional on the
   # pool having done its job, so she pays every applier in the set rather than standing alone.
   # NEW POWER: night_vigil.
   # DELIBERATE SYMMETRY with Albedo: solar_isotoma turns "attack an aura'd enemy" into BLOCK, night_vigil
   # turns the same trigger into DAMAGE. Same hook in deal_damage_to_enemy, opposite currency. Recorded so
   # the pairing reads as design rather than as one of them being a copy of the other.
   # §4.3: a conditional flat buff, not an engine — it never grows, and with no aura on the board it is
   # worth zero. Her 20-damage body sits ABOVE Itto's (14+6 at the same 2 cost) and far below Raiden's
   # (40 at 3 cost, once): the Inazuma pair are shapeless jackpots that carry nothing else, and she (lint-ok: cross-sheet ratified value)
   # carries a permanent power instead of a bigger number.
   # Burst name "Last Lightfall" RESERVED for a future playable kit-Burst (v1.9).
```

## neuvillette_ancient_sea_authority

```
   # ROLE: enabler. Aura manipulation, named in §4.3 as permitted payoff-grade support space, and the one
   # facet of the Hydro Sovereign no card touches yet: not applying water, but holding authority over it.
   # NEW POWER: ancient_sea_authority (read in reactions.apply_aura).
   # D2: this is his SHARED-POOL Rare and is a DIFFERENT card from the three Guest Star cameos below,
   # per the standing Guest Star ruling. Mechanically the separation is already enforced —
   # five_star_roster filters both guest_star and personal_pool, so this enters the banner roster and the
   # cameos never do. The WATCHLIST convergence cell on guest_neuvillette_judgment is untouched.
   # WHY NOT MASS HYDRO, which was the obvious design: the sheet ALREADY prices that. The watchlist note
   # on guest_neuvillette_judgment records mass-Hydro + the Cryo pair as mass-Frozen potential, with the
   # 3 self-damage named as "the intended brake: spamming judgment to fish freezes costs HP". A free
   # mass-Hydro applier at Rare would delete that brake while leaving the note in place, which is worse
   # than the freeze risk itself. Extending aura DURATION adds no new application and so cannot initiate
   # a freeze that was not already going to happen; it lengthens the window the pool already earns.
   # Burst name "O Tides, I Have Returned" is RESERVED (line 96) and was NOT taken. (lint-ok: sheet line number, not a game number)
```

## arlecchino_masque_red_death

```
   # ROLE: payoff. R65 places her in FONTAINE (House of the Hearth) — Snezhnaya is not a designed sheet.
   # NEW POWER: masque_red_death. Amount is STRENGTH PER TURN (a ratchet, like Nicole's celestial_gift);
   # the Bond is the flat MASQUE_BOND_BLOCK constant, mirrored C#-side and parity-lint watched.
   #
   # REDESIGNED 2026-07-25 [USER], replacing "+4 damage on Attacks; you can no longer be healed".
   # The new shape is Bond of Life proper — a DEBT rather than a denial — and it fixes both problems
   # the first draft was flagged with:
   #   1. The old drawback priced to ZERO for Kokomi (LAW 2 forbids her heals at all), making the card
   #      pure upside for exactly one character. The Bond bites everyone, because everyone gains Block.
   #   2. The old drawback was not fully buildable: the engine exposes no heal hook on PowerModel, so
   #      the C# side could only block heals from MOD cards. Nothing here needs a hook that does not
   #      exist — Strength and Block both have real funnels in both layers.
   #
   # THE KOKOMI INTERACTION IS NOW INTERESTING RATHER THAN BROKEN. Her LAW 3 (Flawless Strategy) says
   # she cannot gain Strength: it converts to Charge at the one apply chokepoint. So Arlecchino pays
   # her in Charge instead of Strength — a different currency, not a dead line — and she still pays
   # the Bond in full. Deliberately NOT special-cased: routing through the standard chokepoint is what
   # makes that fall out on its own.
   # Burst name "Balemoon Rising" RESERVED for a future playable kit-Burst (v1.9).
```

## before guest_neuvillette_tears

```
# ---------- OPEN ITEMS ----------
# 1. Furina personal-pool: RESOLVED (user design, session ruling) — the "Guest Star" generation suite.
#    Personal-pool cards that generate companion cards, Discovery-class machinery (solved; Klee's
#    copy_companion ops are the in-project precedent). Scoping guardrails, all four binding:
#      a. Generated cards are THIS-COMBAT-ONLY (never join the permanent deck — no rewards bypass).
#      b. Generators Exhaust.
#      c. Equal-rarity clause: a generator creates cards of its own rarity (sub-Rare generators
#         cannot create 5-star Rares — banner governor untouched).
#      d. Generation pulls from the shared companion pool PLUS a purpose-built GUEST STAR set —
#         never from playable characters' actual pools (cadence rules live on the character dial;
#         generated playable-cards would have undefined element behavior).
#    Guest Star set v0.1: 2–3 Neuvillette cards at common/uncommon, support-shaped, explicit
#    applies_element flags, personal-pool scoped (banner-exempt: temporary cameos, not drafted 5-stars).
#    Seeds his future playable identity; his shared-pool 5-star Rare remains banner-governed.
#    Upgrade grammar per user: base "create a card of equal rarity from a companion's kit, Exhaust";
#    better versions "choose 1 of 3 from different companions" / "it costs 0 this turn" (Discovery parity).
#    Generated cards ARE legal Spotlight targets — generation is Spotlight's bricking mitigation
#    (the soft form of Appendix A.3; Columbina gets the hard guarantee).
#    Registered bet: generation lifts Spotlight's FLOOR, not its ceiling — one-shot cameos can't match
#    drafted-kit Fanfare throughput. If the sim shows generation beating real drafting, the knob is
#    generator cost, not the concept.
# 2. Fontaine 5-star Rares: FOUR SHIPPED 2026-07-25 (Navia, Clorinde, Neuvillette, Arlecchino) — see the
#    5-STAR RARES block above. Arlecchino is here by R65 (unreleased-nation placement: residence until
#    Snezhnaya ships as a sheet). Still later scope: Sigewinne, Lyney, Wriothesley. Lore audit per v1.7
#    is [USER] and NOT yet done for the four that shipped.
# 3. WATCHLIST: Kaeya+Freminet cross-nation Cryo-attack redundancy — a Furina drafting both has doubled freeze
#    initiation. Monitor in the hydro+cryo convergence checks; roster geometry, not a card bug.
# 4. DSL asks for this set: Chevreuse's reaction_triggered_this_turn predicate, Freminet's shatter_bonus power,
#    Charlotte's block_next_turn op — all trivially loggable as UNIMPLEMENTED stubs for pass 1 per house convention.
```

## before guest_neuvillette_tears

```
# ---------- GUEST STAR SET v0.1 — NEUVILLETTE (Furina personal-pool ONLY; never in shared rewards) ----------
# Access: exclusively via Furina's Guest Star generators (this-combat-only, generators Exhaust, equal-rarity).
# `guest_star: true` exempts these from the §4.2 5-star rule (rare, one card) — they are temporary cameos,
# not drafted 5-stars; his shared-pool 5-star Rare remains banner-governed and is a DIFFERENT card.
# Burst name "O Tides, I Have Returned" RESERVED for his future playable kit-Burst (v1.9: bursts are kit).
# Generated mid-combat -> all three deliberately dead-simple: legible in a choose-1-of-3 at a glance.
```

## guest_neuvillette_judgment

```
   # The charged-attack identity: the Iudex draws on his own life to render judgment.
   # In Furina's deck the 3 self-damage is Fanfare flux BY DESIGN — the interlock is the point, not a leak.
   # Kept below the uplifted Ring of Bursting Grenades (10 all + element): the HP rider pays for
   # mass-Hydro application upside. WATCHLIST: mass Hydro + the Cryo pair = mass-Frozen potential —
   # add to the hydro+cryo convergence checks (the self-damage cost is the intended brake: spamming
   # judgment to fish freezes costs HP that a freeze deck cannot easily recoup under R8).
```

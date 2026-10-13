# Kokomi: late growth from her Genshin kit (2026-10-12)

**Why.** After the three rounds and the forced growth test (`review/records/kokomi-growth-test-2026-10-12.md`), [USER]:

> before we lock that in, can you kick off a research census of Kokomi's genshin kit and lore and see if that triggers inspiration on any ideas to get us out of the current issue on growth?
>
> It does feel like we've taken some cues from Silent's Shiv direction on this Sting build, which is fine - we can see if there's a reasonably lore-ful way to lean into that.

**Sources:**
- A census of her Genshin kit and lore, in the session scratchpad (`kokomi-census/genshin-kokomi-census.md`). It is drawn from KeqingMains, genshin.gg, Fextralife and GamerGuides; the Fandom wiki refused the fetch.
- The round records `kokomi-round-1/2/3-2026-10-12.md` and the growth test.
- `docs/prototype-surface.yaml` for today's card texts.

- `game_ref/silent.json` for the Silent's StS2 Shiv cards.
- A Fable review of this paper's first draft (`kokomi-census/fable-review-jellyfish.md`). It corrected the diagnosis, five numbers and two rarities, and added the big hit.

## 1. Why Stings never pile up

- Her own cards deal 62% of the base five's damage in act-3 normal fights, and 45% against act-2 bosses (round 3).
- With Watchful Shoal forced into four decks, only 28 Stings were played in 53 fights, and Stings made 5% of her damage.

**Supply is the limit, and supply is low because the generators are poor cards.**
- 28 Stings in 53 fights is about one generator play a fight, each making one Sting.
- Lane 3's deck had no Sting maker at all. Lane 1 had two. Lane 4 had three and played every Sting it made.
- No deck ever had more Stings than Energy.

**Why the generators are poor: a Sting costs 1 Energy.**
- Jellyfish Drift is a Strike plus a card that needs another Energy.
- Shoal Call (0, Exhausts, 2 Stings) is really 2 Energy for 14. It went from 16 plays in round 2 to none in round 3.
- The Silent's Shiv costs 0, so Cloak and Dagger and Blade Dance are good cards in one play, and Accuracy has a pile of hits to multiply.

So a lean into the Shiv shape starts with the token's cost, because that is what makes a generator worth drafting.

**What the Shiv shape costs.** Both act-1 deaths in jellyfish decks were to bosses that cut damage: Vantom's Slippery and the Matriarch's -2 Strength. A stream of 4s loses more to those than a stream of 7s does. So the change has to come with a big hit (section 3).

## 2. What her Genshin kit offers

| In Genshin | What it does | What it suggests here |
|---|---|---|
| **Bake-Kurage** (Kurage's Oath) | A jellyfish that pulses small Hydro "ripple" damage every 2 seconds | Stings are those ripples: many, small, free |
| **The Shape of Water**, her normal attack | A three-hit combo, biggest hit last | The Silent's Finisher: one hit that pays for the Stings before it |
| **Tamakushi Casket** (A1) | Her burst refreshes the jellyfish already on the field | When the Bake-Kurage carries out a Plan, it leaves a Sting behind. This joins her two halves. |
| **C5 All Streams Flow to the Sea** | (a talent-level constellation; only the name is used) | The name for a card that gathers every Sting played this combat |
| **C1 At Water's Edge** | Her last hit releases a fish worth 30% of Max HP | A flat big hit. The name is taken by her debuff Rare; not proposed now. |
| **Everlasting Moonglow** and **C4** | Normal-attack hits refund Energy after her burst | The same idea as a free Sting. As its own card it is pick 1 (b), with that option's risk. |
| **Ocean-Hued Clam** | Banks healing into a foam that bursts for 90% of it as damage | Block banked into damage. Not proposed: Tidal Rebuke and Coral Crash already do this, and so does Varka's Retaliating Tide. |
| **Nereid's Ascension** (the Garment) | Her damage scales with Max HP | Not proposed: Max HP barely grows over a run, so it is not growth. |

## 3. The proposal: Stings become her Shivs

**The token.** It costs 0 and keeps a Plan line. (This draft first dropped the Plan line, reading the card paper's rule 2 as "no 0-cost Plans". [USER]: "I'm actually totally fine with 0-cost plans; it's Dusk Plans that were 'kinda silly' since they take place within your turn (at the end) like a normal card with extra steps".)

| Card | Today | Proposed |
|---|---|---|
| **Sting** (token) | 1: "Deal 7 [10] Hydro damage. Plan: Deal 5 [7] Hydro damage to ALL enemies." Ethereal | **0:** "Deal 4 [6] Hydro damage. Plan: Deal 3 [4] Hydro damage to ALL enemies." Ethereal, Exhausts (the Shiv, with a Plan) |
| **Ward** (token) | 1: "Gain 7 [10] Block. Plan: Apply 1 [2] Weak to ALL enemies." Ethereal | **0:** "Gain 4 [6] Block. Plan: Apply 1 [2] Weak to ALL enemies." Ethereal, Exhausts |

- Watchful Shoal (+3 [5] to each Sting and Ward) becomes the Accuracy it was modelled on. It is a point lower than Accuracy because it buffs two tokens.
- Kurage Bloom (a Sting each turn) becomes Infinite Blades.

**The generators,** priced at the Silent's StS2 rates (Cloak and Dagger: 6 Block and a Shiv for 1; Blade Dance: Common, 1, 3 [4] Shivs, Exhausts):

| Card | Today | Proposed |
|---|---|---|
| Jellyfish Drift (C, 1) | "Deal 8 Hydro damage. Add a Sting to your hand." | "Deal 6 [8] Hydro damage. Add a Sting to your hand." |
| Watatsumi Drill (C, 1) | "Deal 8 [11] Hydro damage. Add a Ward to your hand." | "Deal 6 [9] Hydro damage. Add a Ward to your hand." |
| Bubble Ward (C, 1) | "Gain 7 Block. Add a Ward to your hand." | "Gain 5 [8] Block. Add a Ward to your hand." |
| Shoal Call (U) | 0, Exhausts: "Add 2 Stings to your hand." [upgraded Stings] | 1, Exhausts: "Add 3 [4] Stings to your hand." (Blade Dance) |

**Growth: three cards.** Her pool stays at 78, with one Rare slot becoming an Uncommon.

> **Endless Shoal** (Uncommon Power, 1): Whenever the Bake-Kurage carries out a Plan, add a Sting to your hand.

- **Today** it is a Rare, 2 [1]: "Whenever the Bake-Kurage carries out a Sting or Ward, add a copy of it to your hand." Free Stings that can be written would make that copy loop for nothing, so its text changes.
- **Lore:** the Tamakushi Casket, where carrying out a Plan refreshes the jellyfish.
- **Rate:** Infinite Blades' rate, tied to her spine, so any Plan deck can dip into Stings.
- **Doubled carry-outs:** a carry-out done twice (Nereid's Ascension, Second Wave) gives two Stings.
- **Slot:** it takes Measured Breath's Uncommon slot.

> **All Streams Flow to the Sea** (Rare Attack, 1): Deal 4 [8] Hydro damage, plus 2 for each Sting you played this combat.

- **Role:** the jellyfish twin of Sango Isshin, which counts Plans carried out this combat. Each half of her kit gets one card that grows over a fight.
- **Rarity:** a per-combat snowball is a Rare, and her Rare Attacks get drafted (Masterstroke 5 of 7).
- **Slot:** it takes Endless Shoal's old Rare slot.
- **Damage:** at 4 to 6 Stings a fight it is a Strike in a short fight, and 30 to 40 by turn 8 of a boss fight, where her wall is.

> **The Shape of Water** (Uncommon Attack, 1): Deal 6 [8] Hydro damage for each Sting you played this turn.

- **Role:** her normal attack's last and biggest hit, and the Silent's Finisher.
- **The big hit:** it is one hit, so it answers the damage-cutting bosses a stream of 4s loses to. It also pays from turn 2, where All Streams is still a Strike.
- **Slot:** it takes Spring Tide's Rare slot. Spring Tide is a NEVER AGAIN and on the post-run pool-pass list.

**Unchanged:** Kurage Bloom, Kurage Barrage, Watchful Shoal, Watatsumi Resistance, and every Plan card. Kurage's Wake, whose Plan adds 2 Stings, becomes the Common card that joins the two halves.

## 4. What it costs and what to check

- **Stings stay in the Plan queue, and now cost nothing to write.** The choice each turn is 4 to one enemy now, or 3 to ALL next turn.
  - A written Sting counts for "Plans waiting" (Feint, Breakwater, Tideturn, Shoal of Spears) and fires Coordinated Tide, so round 3's best jellyfish turn stays.
  - The risk is free Plans inflating those counters. Tideturn (8 per Plan waiting) with four written Stings is 32 more for 1 Energy. The round watches the biggest Tideturn and Shoal of Spears hits.
  - Endless Shoal plus a written Sting makes one Sting a turn that keeps itself going, and Nereid's Ascension grows it by one a turn. That goes in the probe's known set.
- **Treatise** draws once a turn when you play a card you could have written, so a Sting played now can feed it.
- **The ceiling.**
  - Kurage Bloom, Endless Shoal, Shoal Call, Watchful Shoal and The Shape of Water together make a turn of 50 to 70. The Silent's assembled Shiv deck makes about 70.
  - Nereid's Ascension plus Kurage's Wake plus Endless Shoal gives 6 Stings a turn on a Rare, an Uncommon and a Common.
- **Loops.**
  - Nothing makes a card when a Sting is played, so free Stings cannot chain.
  - Grand Design plus Endless Shoal (3 free Plans, 3 Stings) goes in the probe's known set.
  - No card that replays Stings from the Exhaust Pile (the Silent's Knife Trap) should enter her pool.
- **The Companion half is not addressed.**
  - Its growth is still Grand Strategist and Sango Isshin, and shared Companions were 8% of her round-3 damage.
  - If you want a card for it, the next one is a Commander twin of All Streams ("plus 2 for each Companion written this combat"), checked against Sango Isshin first.
- **Check lines for the next round:**
  - Stings made, played and lost per fight (a telemetry field to add first), against 28 played in 53 fights.
  - Sting share of her damage, against 5%.
  - Her own-card damage, against 62% of the base five's in act-3 normal fights and 45% against act-2 bosses.
  - Each new card taken at least once.

## For [USER]

1. **The jellyfish token.**
   - **(a) Default:** Stings and Wards become 0-cost Shivs that keep a Plan line, with the generators at the Silent's rates (section 3).
   - (b) Keep Stings at 1 Energy with their Plan line, and add a Rare Power, "Everlasting Moonglow: Your Stings cost 0." The risk is that free Stings make free Plans, which feed the Plans-waiting counters: the Dusk problem again.
   - (c) No change before your run.
2. **Growth cards** (with 1 (a) or (b)).
   - **(a) Default:** all three.
     - Endless Shoal becomes the Uncommon "a Sting per Plan carried out".
     - All Streams Flow to the Sea is the Rare.
     - The Shape of Water is the Uncommon finisher.
   - (b) Endless Shoal and The Shape of Water only.
   - (c) None.
3. **When to play it.**
   - **(a) Default:** I build your picks, run a Kokomi seat round on them, and you play that build, rather than today's 0.2.5020.
   - (b) You play 0.2.5020 as it is first, and the jellyfish change waits for your verdict.

## Ruled (2026-10-12)

[USER]: "On Kokomi - I'm actually totally fine with 0-cost plans; it's Dusk Plans that were 'kinda silly' since they take place within your turn (at the end) like a normal card with extra steps. So we can allow for Stings to Plan if there is an actual reason to do it. Likewise for other 0-cost cards. At a glance - Kokomi looks good otherwise! Good with all defaults."

All three picks at (a), with the token keeping its Plan line:
- Sting "0: Deal 4 [6] Hydro damage. Plan: Deal 3 [4] Hydro damage to ALL enemies."
- Ward "0: Gain 4 [6] Block. Plan: Apply 1 [2] Weak to ALL enemies."
- The generators at the Silent's rates. Shoal Call becomes Blade Dance.
- Endless Shoal becomes the Uncommon "a Sting per Plan carried out". All Streams Flow to the Sea is the Rare, and The Shape of Water the Uncommon.
- I build it and run a Kokomi seat round, and [USER] plays that build.

The card paper's rule 2 ("No card with a Plan line costs 0") is lifted. The rule that stands is that no Plan happens within your own turn (Dusk).

The growth-test record's picks go with this: late growth is answered here, and the generators keep rolling Inazuma Commons (pick 2 (a)).

Status: RECORD

# EB-148 — Companion audit: is Block bought, or is it free?

**For [USER]. Written 2026-08-27 on branch `eb148-companion-audit`.**
Commissioned by R213 item C. This is facts and sorting only. Nothing here changes
a number, an effect, a sheet or a register, and nothing here recommends a design.
The questions at the end are pick lists.

Machine-readable twin: `review/records/eb148-companion-audit-2026-08-27.tsv`.

---

## 1. Summary

There are **51 Companion cards** across the three nation sheets: 17 Mondstadt
(Klee's pool), 19 Fontaine (Furina's pool, including the 3 Guest Star cameos),
15 Inazuma (Kokomi's pool).

**30 of the 51 grant no defence at all.** The other 21 do, and they split like
this: **14 are PURCHASED defence** — you spend the card and the energy mainly to
block, and whatever else is on the card is small, random or conditional.
**7 are SUBSIDIZED defence** — the Block rides along on a card you were buying
for something else.

Of those 7 subsidized cards, **5 carry no price whatsoever**: the engine effect
and the Block both land, every time, for the one cost. One (Nicole) is paid for
once, at play time, and is free every turn after. Exactly **one card in the whole
set — Prune — makes the Block and the engine payoff mutually exclusive**, which
is the only place a player is ever asked to choose between defending and
advancing.

Per nation:

| Nation | Cards | Purchased | Subsidized | No defence | Grants Block |
|---|---|---|---|---|---|
| Mondstadt (Klee) | 17 | 5 | 2 | 10 | 7 (41%) |
| Fontaine (Furina) | 19 | 3 | 2 | 14 | 5 (26%) |
| Inazuma (Kokomi) | 15 | 6 | 3 | 6 | **9 (60%)** |
| **All** | **51** | **14** | **7** | **30** | **21 (41%)** |

Two cards are marked separately as **subsidy engines**: Albedo's Solar Isotoma
and Navia's Cannon Fire Support. Each is bought purely for defence, so each is
classified PURCHASED — but what they buy is a standing rule that hands you Block
for an action you were taking anyway (attacking an aura'd enemy; playing any
Companion). After the one purchase, every later block is free. Navia's trigger
is literally "you played a Companion card", which is the exact loop [USER]
described in the playtest notes.

---

## 2. How each card was classified

The classification was made per card, before the hidden-name test, using one
question:

> **Strip the Block off the card. Is what remains, on its own, a normal reason to
> play this card at this cost?**

- If **yes** — the rest is the purchase and the Block is a rider → **SUBSIDIZED**.
  A real attack, a Swirl, a scaling power, a Muster: these are things a player
  buys for their own sake.
- If **no** — what remains is small, conditional, or fires at a random target, so
  a player who did not want Block would not play the card → **PURCHASED**.
- No Block and no other damage prevention → **no defence**.

Then, for every SUBSIDIZED card only, R213 item E3's four prices were checked:
does the defence cost **tempo**, **identity position**, **resource**, or **the
loss of another outcome**? "Unpriced" is recorded where none of the four applies.

No card in any of the three sheets grants damage prevention by any route other
than Block — there is no ward, no negate, no damage reduction anywhere in the
Companion pools.

---

## 3. The full table

| Nation | id | Printed name | Cost | Type | Effect text | Block | Other effects on the same card | Classification | E3 price | Sheet line |
|---|---|---|---|---|---|---|---|---|---|---|
| Mondstadt | `dahlia_sacramental_shower` | Dahlia - Sacramental Shower | 1 | attack | Deal 6 damage to one enemy. Applies Hydro. | - | 6 damage (Hydro applied) | no defence | -- | `docs/mondstadt-companions.yaml:20` |
| Mondstadt | `dahlia_favonian_favor` | Dahlia - Favonian Favor | 1 | skill | Gain 5 Block. Apply a Hydro aura to a random enemy. | 5 | Hydro aura on a RANDOM enemy | **PURCHASED** | -- | `docs/mondstadt-companions.yaml:22` |
| Mondstadt | `fischl_nightrider` | Fischl - Nightrider | 1 | attack | Deal 5 damage to one enemy. Applies Electro. | - | 5 damage (Electro applied) | no defence | -- | `docs/mondstadt-companions.yaml:24` |
| Mondstadt | `fischl_oz` | Fischl - Oz, at Your Side | 1 | power | For 3 turns: at end of turn deal 3 damage and apply Electro to a random enemy. | - | 3-turn damage summon | no defence | -- | `docs/mondstadt-companions.yaml:26` |
| Mondstadt | `barbara_melody` | Barbara - Let the Show Begin♪ | 1 | skill | Gain 6 Block. Gain 4 Burst Energy. | 6 | 4 Burst Energy (meter) | **PURCHASED** | -- | `docs/mondstadt-companions.yaml:30` |
| Mondstadt | `barbara_shining_idol` | Barbara - Shining Miracle♪ | 1 | skill | Gain 5 Block. Apply a Hydro aura to a random enemy. Draw 1 card. | 5 | Hydro aura on a RANDOM enemy; draw 1 | **PURCHASED** | -- | `docs/mondstadt-companions.yaml:36` |
| Mondstadt | `sucrose_gust` | Sucrose - Wind Spirit Creation | 0 | skill | Swirl an enemy's aura. Draw 1 card. | - | Swirl; draw 1 | no defence | -- | `docs/mondstadt-companions.yaml:41` |
| Mondstadt | `sucrose_astable` | Sucrose - Astable Anemohypostasis | 0 | skill | Swirl an enemy's aura. Gain 8 Burst Energy. Exhaust. | - | Swirl; 8 Burst Energy | no defence | -- | `docs/mondstadt-companions.yaml:48` |
| Mondstadt | `sucrose_catalyst_conversion` | Sucrose - Catalyst Conversion | 0 | skill | Gain 1 Energy. Draw 1 card. Exhaust. | - | 1 Energy; draw 1 | no defence | -- | `docs/mondstadt-companions.yaml:58` |
| Mondstadt | `bennett_passion` | Bennett - Passion Overload | 0 | skill | Your next Attack deals 4 more damage. Gain 5 Burst Energy. | - | +4 next Attack; 5 Burst Energy | no defence | -- | `docs/mondstadt-companions.yaml:69` |
| Mondstadt | `bennett_fantastic_voyage` | Bennett - Fantastic Voyage | 1 | skill | Gain 3 Strength. Exhaust. | - | +3 Strength (permanent) | no defence | -- | `docs/mondstadt-companions.yaml:71` |
| Mondstadt | `kaeya_frostgnaw` | Kaeya - Frostgnaw | 1 | attack | Deal 6 damage to one enemy. Applies Cryo. | - | 6 damage (Cryo applied) | no defence | -- | `docs/mondstadt-companions.yaml:77` |
| Mondstadt | `diona_icy_paws` | Diona - Icy Paws | 1 | skill | Gain 5 Block. Apply a Cryo aura to a random enemy. | 5 | Cryo aura on a RANDOM enemy | **PURCHASED** | -- | `docs/mondstadt-companions.yaml:79` |
| Mondstadt | `albedo_solar_isotoma` | Albedo - Solar Isotoma | 1 | power | For 3 turns: your Attacks against enemies that have an aura grant 3 Block. | 3 per hit | -- | **PURCHASED** (subsidy engine) | -- | `docs/mondstadt-companions.yaml:83` |
| Mondstadt | `durin_witchs_flame` | Durin - Witch's Flame | 1 | power | At end of turn consume Pyro from each enemy; per aura consumed, deal 6 damage and gain 3 Burst Energy. | - | damage + Burst Energy per Pyro aura | no defence | -- | `docs/mondstadt-companions.yaml:85` |
| Mondstadt | `nicole_celestial_gift` | Nicole - Celestial Gift | 2 | power | At the start of each turn gain 1 Strength and 4 Block. | 4 per turn | +1 Strength per turn (ratchet) | **SUBSIDIZED** | resource, ONCE (2 Energy at play); every later turn's Block is free | `docs/mondstadt-companions.yaml:87` |
| Mondstadt | `prune_witch_hunt` | Prune - Little Witch's Hunt | 1 | skill | Swirl an enemy's aura. If that triggered a reaction, gain 1 Spark; otherwise gain 5 Block. Gain 1 Spark. | 5 (only on whiff) | Swirl; 1-2 Spark | **SUBSIDIZED** | loss of another outcome - the Block and the reaction Spark are mutually exclusive | `docs/mondstadt-companions.yaml:102` |
| Fontaine | `chevreuse_interdiction_fire` | Chevreuse - Interdiction Fire | 1 | attack | Deal 7 damage to one enemy. Applies Pyro. | - | 7 damage (Pyro applied) | no defence | -- | `docs/fontaine-companions.yaml:11` |
| Fontaine | `chevreuse_vanguards_valor` | Chevreuse - Vanguard's Valor | 0 | skill | Your next Attack deals 3 more damage. If a reaction triggered this turn, +3 more. | - | +3 (+3) next Attack | no defence | -- | `docs/fontaine-companions.yaml:14` |
| Fontaine | `chevreuse_bursting_grenades` | Chevreuse - Ring of Bursting Grenades | 2 | attack | Deal 10 damage to ALL enemies. Applies Pyro. | - | 10 AoE damage (Pyro applied) | no defence | -- | `docs/fontaine-companions.yaml:18` |
| Fontaine | `lynette_enigmatic_feint` | Lynette - Enigmatic Feint | 1 | skill | Swirl an enemy's aura. Gain 5 Block. | 5 | Swirl | **SUBSIDIZED** | UNPRICED - the Swirl and the Block both land, always | `docs/fontaine-companions.yaml:23` |
| Fontaine | `lynette_box_trick` | Lynette - Bogglecat Box | 1 | skill | Draw 2 cards. | - | draw 2 | no defence | -- | `docs/fontaine-companions.yaml:26` |
| Fontaine | `lynette_astonishing_shift` | Lynette - Magic Trick: Astonishing Shift | 1 | skill | Swirl an enemy's aura. Deal 4 damage to ALL enemies (no element applied). | - | Swirl; 4 AoE damage | no defence | -- | `docs/fontaine-companions.yaml:32` |
| Fontaine | `charlotte_freezing_point` | Charlotte - Framing: Freezing Point Composition | 1 | attack | Deal 4 damage to one enemy. Applies Cryo. Draw 1 card. | - | 4 damage (Cryo applied); draw 1 | no defence | -- | `docs/fontaine-companions.yaml:38` |
| Fontaine | `charlotte_enduring_frosthelm` | Charlotte - First-Person Shutter | 1 | skill | Gain 4 Block. Gain 4 Block at the start of next turn. | 4 + 4 next turn | -- | **PURCHASED** | -- | `docs/fontaine-companions.yaml:41` |
| Fontaine | `charlotte_snappy_silhouette` | Charlotte - Snappy Silhouette | 1 | skill | Apply Vulnerable 2 to an enemy. Draw 1 card. | - | Vulnerable 2; draw 1 | no defence | -- | `docs/fontaine-companions.yaml:52` |
| Fontaine | `freminet_pers_deploy` | Freminet - Pers, Deploy! | 1 | attack | Deal 6 damage to one enemy. Applies Cryo. | - | 6 damage (Cryo applied) | no defence | -- | `docs/fontaine-companions.yaml:57` |
| Fontaine | `freminet_pressurized_floe` | Freminet - Pressurized Floe: Backstroke | 2 | attack | Deal 10 damage to one enemy (no element applied). Gain 6 Block. | 6 | 10 damage; Shatters a Frozen enemy | **SUBSIDIZED** | UNPRICED - 2 Energy buys the full attack AND the full Block | `docs/fontaine-companions.yaml:62` |
| Fontaine | `freminet_shattering_pressure` | Freminet - Shattering Pressure | 1 | power | Your Shatters deal 4 more damage. | - | +4 Shatter damage | no defence | -- | `docs/fontaine-companions.yaml:67` |
| Fontaine | `navia_cannon_fire_support` | Navia - Cannon Fire Support | 1 | power | Whenever you play a Companion card, gain 3 Block. | 3 per Companion played | -- | **PURCHASED** (subsidy engine) | -- | `docs/fontaine-companions.yaml:98` |
| Fontaine | `clorinde_impale_the_night` | Clorinde - Impale the Night | 2 | attack | Deal 20 damage to one enemy. Applies Electro. Your Attacks against enemies that have an aura deal 6 more. | - | 20 damage; permanent +6 vs aura'd enemies | no defence | -- | `docs/fontaine-companions.yaml:112` |
| Fontaine | `neuvillette_ancient_sea_authority` | Neuvillette - Heir to the Ancient Sea's Authority | 1 | power | Auras you apply last 1 extra turn. | - | aura duration +1 | no defence | -- | `docs/fontaine-companions.yaml:137` |
| Fontaine | `arlecchino_masque_red_death` | Arlecchino - Masque of the Red Death | 1 | power | At the start of each turn gain 1 Strength. Your Bond of Life eats the first 5 Block you gain each turn. | NEGATIVE 5 per turn | +1 Strength per turn (ratchet) | no defence | -- | `docs/fontaine-companions.yaml:154` |
| Fontaine | `guest_neuvillette_tears` | Neuvillette - O Tears, I Shall Repay | 1 | attack | Deal 5 damage to one enemy. Applies Hydro. | - | 5 damage (Hydro applied) | no defence | -- | `docs/fontaine-companions.yaml:212` |
| Fontaine | `guest_neuvillette_droplets` | Neuvillette - Sourcewater Droplets | 1 | skill | Gain 4 Block. Apply a Hydro aura to a random enemy. | 4 | Hydro aura on a RANDOM enemy | **PURCHASED** | -- | `docs/fontaine-companions.yaml:215` |
| Fontaine | `guest_neuvillette_judgment` | Neuvillette - Equitable Judgment | 2 | attack | Lose 3 HP. Deal 7 damage to ALL enemies. Applies Hydro. | - | 7 AoE damage (Hydro applied); 3 self-damage | no defence | -- | `docs/fontaine-companions.yaml:219` |
| Inazuma | `gorou_inuzaka_charge` | Gorou - Inuzaka All-Round Defense | 0 | attack | Deal 6 damage to one enemy (no element applied). Exhaust. | - | 6 damage | no defence | -- | `docs/inazuma-companions.yaml:29` |
| Inazuma | `gorou_war_banner` | Gorou - General's War Banner | 1 | skill | Gain 4 Block. Your next Attack deals 3 more damage. | 4 | +3 next Attack | **PURCHASED** | -- | `docs/inazuma-companions.yaml:36` |
| Inazuma | `gorou_heart_of_the_clan` | Gorou - Forward Unto Victory | 1 | skill | Gain 3 Block. Gain Metallicize 2 (2 Block at the end of every turn). | 3 + 2 per turn | -- | **PURCHASED** | -- | `docs/inazuma-companions.yaml:39` |
| Inazuma | `sayu_yoohoo_windwheel` | Sayu - Yoohoo Art: Fuuin Dash | 1 | attack | Deal 4 damage to one enemy (no element applied). Swirl its aura. | - | 4 damage; Swirl | no defence | -- | `docs/inazuma-companions.yaml:47` |
| Inazuma | `sayu_daruma_gift` | Sayu - Muji-Muji Daruma | 1 | skill | Gain 4 Block. Gain 4 Block at the start of next turn. | 4 + 4 next turn | -- | **PURCHASED** | -- | `docs/inazuma-companions.yaml:50` |
| Inazuma | `sayu_naptime` | Sayu - Naptime | 0 | skill | Gain 3 Block. Draw 1 card. | 3 | draw 1 (replaces itself) | **PURCHASED** | -- | `docs/inazuma-companions.yaml:54` |
| Inazuma | `shinobu_sanctifying_ring` | Shinobu - Sanctifying Ring | 2 | skill | Deal 3 damage to ALL enemies. Applies Electro. Gain 4 Block. | 4 | 3 AoE damage (Electro applied) | **SUBSIDIZED** | UNPRICED - the mass Electro application and the Block both land | `docs/inazuma-companions.yaml:59` |
| Inazuma | `shinobu_grass_ring_bond` | Shinobu - Grass Ring of Sanctification | 0 | skill | Gain 4 Block. | 4 | -- | **PURCHASED** | -- | `docs/inazuma-companions.yaml:63` |
| Inazuma | `shinobu_thundergrust` | Shinobu - Thundergrust | 1 | attack | Deal 7 damage to one enemy. Applies Electro. | - | 7 damage (Electro applied) | no defence | -- | `docs/inazuma-companions.yaml:66` |
| Inazuma | `thoma_blazing_barrier` | Thoma - Blazing Barrier | 1 | skill | Gain 5 Block. Gain 2 Block at the start of next turn. | 5 + 2 next turn | -- | **PURCHASED** | -- | `docs/inazuma-companions.yaml:71` |
| Inazuma | `thoma_crimson_ooyoroi` | Thoma - Crimson Ooyoroi | 2 | attack | Deal 8 damage to one enemy. Applies Pyro. Gain 3 Block. | 3 | 8 damage (Pyro applied) | **SUBSIDIZED** | UNPRICED - 2 Energy buys the tagged attack AND the Block | `docs/inazuma-companions.yaml:74` |
| Inazuma | `sara_crowfeather_cover` | Kujou Sara - Crowfeather Cover | 0 | skill | Your next Attack deals 4 more damage. | - | +4 next Attack | no defence | -- | `docs/inazuma-companions.yaml:79` |
| Inazuma | `sara_tengu_stormcall` | Kujou Sara - Tengu Stormcall | 1 | skill | Deal 4 damage to one enemy. Applies Electro. Gain 2 Strength (2 Charge in Kokomi's hands). | - | 4 damage; +2 Strength / +2 Charge | no defence | -- | `docs/inazuma-companions.yaml:82` |
| Inazuma | `itto_superlative_superstrength` | Itto - Superlative Superstrength | 2 | attack | Deal 14 damage to one enemy (no element applied). Gain 6 Block. | 6 | 14 damage | **SUBSIDIZED** | UNPRICED - 2 Energy buys the biggest repeatable hit AND 6 Block | `docs/inazuma-companions.yaml:89` |
| Inazuma | `raiden_musou_no_hitotachi` | Raiden Shogun - Musou no Hitotachi | 3 | attack | Deal 40 damage to one enemy. Applies Electro. Apply Vulnerable 2. Exhaust. | - | 40 damage; Vulnerable 2 | no defence | -- | `docs/inazuma-companions.yaml:99` |

---

## 4. The hidden-name test

Run after the classification above. Names, ids, characters, nations and flavour
were stripped; only the effect texts were compared. The 51 cards fall into
**15 strategic identities**. The card ids are put back below only so the groups
can be read.

**Cluster A - Deal N damage to one enemy, nothing else (8 cards)**

- 1 Energy, attack: Deal 6 damage to one enemy. Applies Hydro. -- (`dahlia_sacramental_shower`, Mondstadt)
- 1 Energy, attack: Deal 5 damage to one enemy. Applies Electro. -- (`fischl_nightrider`, Mondstadt)
- 1 Energy, attack: Deal 6 damage to one enemy. Applies Cryo. -- (`kaeya_frostgnaw`, Mondstadt)
- 1 Energy, attack: Deal 7 damage to one enemy. Applies Pyro. -- (`chevreuse_interdiction_fire`, Fontaine)
- 1 Energy, attack: Deal 6 damage to one enemy. Applies Cryo. -- (`freminet_pers_deploy`, Fontaine)
- 1 Energy, attack: Deal 5 damage to one enemy. Applies Hydro. -- (`guest_neuvillette_tears`, Fontaine)
- 0 Energy, attack: Deal 6 damage to one enemy (no element applied). Exhaust. -- (`gorou_inuzaka_charge`, Inazuma)
- 1 Energy, attack: Deal 7 damage to one enemy. Applies Electro. -- (`shinobu_thundergrust`, Inazuma)

**Cluster B - Gain ~5 Block and apply an aura to a RANDOM enemy (4 cards)**

- 1 Energy, skill: Gain 5 Block. Apply a Hydro aura to a random enemy. -- (`dahlia_favonian_favor`, Mondstadt)
- 1 Energy, skill: Gain 5 Block. Apply a Hydro aura to a random enemy. Draw 1 card. -- (`barbara_shining_idol`, Mondstadt)
- 1 Energy, skill: Gain 5 Block. Apply a Cryo aura to a random enemy. -- (`diona_icy_paws`, Mondstadt)
- 1 Energy, skill: Gain 4 Block. Apply a Hydro aura to a random enemy. -- (`guest_neuvillette_droplets`, Fontaine)

**Cluster C - Gain Block now and more Block at the start of next turn (3 cards)**

- 1 Energy, skill: Gain 4 Block. Gain 4 Block at the start of next turn. -- (`charlotte_enduring_frosthelm`, Fontaine)
- 1 Energy, skill: Gain 4 Block. Gain 4 Block at the start of next turn. -- (`sayu_daruma_gift`, Inazuma)
- 1 Energy, skill: Gain 5 Block. Gain 2 Block at the start of next turn. -- (`thoma_blazing_barrier`, Inazuma)

**Cluster D - Swirl an aura, plus one rider (6 cards)**

- 0 Energy, skill: Swirl an enemy's aura. Draw 1 card. -- (`sucrose_gust`, Mondstadt)
- 0 Energy, skill: Swirl an enemy's aura. Gain 8 Burst Energy. Exhaust. -- (`sucrose_astable`, Mondstadt)
- 1 Energy, skill: Swirl an enemy's aura. If that triggered a reaction, gain 1 Spark; otherwise gain 5 Block. Gain 1 Spark. -- (`prune_witch_hunt`, Mondstadt)
- 1 Energy, skill: Swirl an enemy's aura. Gain 5 Block. -- (`lynette_enigmatic_feint`, Fontaine)
- 1 Energy, skill: Swirl an enemy's aura. Deal 4 damage to ALL enemies (no element applied). -- (`lynette_astonishing_shift`, Fontaine)
- 1 Energy, attack: Deal 4 damage to one enemy (no element applied). Swirl its aura. -- (`sayu_yoohoo_windwheel`, Inazuma)

**Cluster E - A 2-Energy attack with a Block rider on the same card (4 cards)**

- 2 Energy, attack: Deal 10 damage to one enemy (no element applied). Gain 6 Block. -- (`freminet_pressurized_floe`, Fontaine)
- 2 Energy, skill: Deal 3 damage to ALL enemies. Applies Electro. Gain 4 Block. -- (`shinobu_sanctifying_ring`, Inazuma)
- 2 Energy, attack: Deal 8 damage to one enemy. Applies Pyro. Gain 3 Block. -- (`thoma_crimson_ooyoroi`, Inazuma)
- 2 Energy, attack: Deal 14 damage to one enemy (no element applied). Gain 6 Block. -- (`itto_superlative_superstrength`, Inazuma)

**Cluster F - Make your next Attack hit harder (4 cards)**

- 0 Energy, skill: Your next Attack deals 4 more damage. Gain 5 Burst Energy. -- (`bennett_passion`, Mondstadt)
- 0 Energy, skill: Your next Attack deals 3 more damage. If a reaction triggered this turn, +3 more. -- (`chevreuse_vanguards_valor`, Fontaine)
- 1 Energy, skill: Gain 4 Block. Your next Attack deals 3 more damage. -- (`gorou_war_banner`, Inazuma)
- 0 Energy, skill: Your next Attack deals 4 more damage. -- (`sara_crowfeather_cover`, Inazuma)

**Cluster G - Gain Strength, or Strength every turn (4 cards)**

- 1 Energy, skill: Gain 3 Strength. Exhaust. -- (`bennett_fantastic_voyage`, Mondstadt)
- 2 Energy, power: At the start of each turn gain 1 Strength and 4 Block. -- (`nicole_celestial_gift`, Mondstadt)
- 1 Energy, power: At the start of each turn gain 1 Strength. Your Bond of Life eats the first 5 Block you gain each turn. -- (`arlecchino_masque_red_death`, Fontaine)
- 1 Energy, skill: Deal 4 damage to one enemy. Applies Electro. Gain 2 Strength (2 Charge in Kokomi's hands). -- (`sara_tengu_stormcall`, Inazuma)

**Cluster H - A standing engine that pays Block for something you were doing anyway (3 cards)**

- 1 Energy, power: For 3 turns: your Attacks against enemies that have an aura grant 3 Block. -- (`albedo_solar_isotoma`, Mondstadt)
- 1 Energy, power: Whenever you play a Companion card, gain 3 Block. -- (`navia_cannon_fire_support`, Fontaine)
- 1 Energy, skill: Gain 3 Block. Gain Metallicize 2 (2 Block at the end of every turn). -- (`gorou_heart_of_the_clan`, Inazuma)

**Cluster I - A small effect that draws its own replacement (4 cards)**

- 0 Energy, skill: Gain 1 Energy. Draw 1 card. Exhaust. -- (`sucrose_catalyst_conversion`, Mondstadt)
- 1 Energy, skill: Draw 2 cards. -- (`lynette_box_trick`, Fontaine)
- 1 Energy, attack: Deal 4 damage to one enemy. Applies Cryo. Draw 1 card. -- (`charlotte_freezing_point`, Fontaine)
- 1 Energy, skill: Apply Vulnerable 2 to an enemy. Draw 1 card. -- (`charlotte_snappy_silhouette`, Fontaine)

**Cluster J - A 0-Energy card whose whole body is a little Block (2 cards)**

- 0 Energy, skill: Gain 3 Block. Draw 1 card. -- (`sayu_naptime`, Inazuma)
- 0 Energy, skill: Gain 4 Block. -- (`shinobu_grass_ring_bond`, Inazuma)

**Cluster K - Gain Block and fill a meter (1 card)**

- 1 Energy, skill: Gain 6 Block. Gain 4 Burst Energy. -- (`barbara_melody`, Mondstadt)

**Cluster L - A power that deals damage at the end of each turn (2 cards)**

- 1 Energy, power: For 3 turns: at end of turn deal 3 damage and apply Electro to a random enemy. -- (`fischl_oz`, Mondstadt)
- 1 Energy, power: At end of turn consume Pyro from each enemy; per aura consumed, deal 6 damage and gain 3 Burst Energy. -- (`durin_witchs_flame`, Mondstadt)

**Cluster M - One very large single hit (2 cards)**

- 2 Energy, attack: Deal 20 damage to one enemy. Applies Electro. Your Attacks against enemies that have an aura deal 6 more. -- (`clorinde_impale_the_night`, Fontaine)
- 3 Energy, attack: Deal 40 damage to one enemy. Applies Electro. Apply Vulnerable 2. Exhaust. -- (`raiden_musou_no_hitotachi`, Inazuma)

**Cluster N - Deal damage to ALL enemies (2 cards)**

- 2 Energy, attack: Deal 10 damage to ALL enemies. Applies Pyro. -- (`chevreuse_bursting_grenades`, Fontaine)
- 2 Energy, attack: Lose 3 HP. Deal 7 damage to ALL enemies. Applies Hydro. -- (`guest_neuvillette_judgment`, Fontaine)

**Cluster O - A power that changes the rules of a reaction (2 cards)**

- 1 Energy, power: Your Shatters deal 4 more damage. -- (`freminet_shattering_pressure`, Fontaine)
- 1 Energy, power: Auras you apply last 1 extra turn. -- (`neuvillette_ancient_sea_authority`, Fontaine)

### Near-duplicates — pairs a player would not tell apart in play

These are stated as facts about the printed effects. Element and flavour differ;
the play does not.

1. **`barbara_shining_idol` contains `dahlia_favonian_favor` whole.** Both are
   Mondstadt, both uncommon, both 1 Energy skills, both give 5 Block and apply a
   Hydro aura to a random enemy. Barbara also draws a card. Same sheet, same
   rarity, same cost, same element.
   (`docs/mondstadt-companions.yaml:22`, `:36`)
2. **`dahlia_favonian_favor` and `diona_icy_paws`** are the same card with the
   element swapped (5 Block + a random aura, 1 Energy). (`:22`, `:79`)
3. **`sayu_daruma_gift` and `charlotte_enduring_frosthelm`** are the same card in
   two different nations: 1 Energy, 4 Block now, 4 Block next turn.
   (`docs/inazuma-companions.yaml:50`, `docs/fontaine-companions.yaml:41`)
4. **Three 1-Energy 6-damage elemental attacks:** `dahlia_sacramental_shower`
   (Hydro), `kaeya_frostgnaw` (Cryo), `freminet_pers_deploy` (Cryo). Kaeya and
   Freminet are also the same element. The Fontaine sheet already records the
   Kaeya/Freminet parity in a comment (`docs/fontaine-companions.yaml:61`).
5. **Two 1-Energy 5-damage attacks:** `fischl_nightrider` (Electro) and
   `guest_neuvillette_tears` (Hydro) — the Fontaine sheet notes the parity itself
   (`:214`).
6. **Two 1-Energy 7-damage attacks:** `chevreuse_interdiction_fire` (Pyro) and
   `shinobu_thundergrust` (Electro).
7. **`sara_crowfeather_cover` and `bennett_passion`** are both 0-Energy "your next
   Attack deals 4 more"; Bennett adds 4 Burst Energy on top.
   (`docs/inazuma-companions.yaml:79`, `docs/mondstadt-companions.yaml:69`)
8. **`itto_superlative_superstrength` and `freminet_pressurized_floe`** are the
   same shape: 2 Energy, a big untagged single-target hit, plus 6 Block. 14 vs 10
   damage. (`docs/inazuma-companions.yaml:89`, `docs/fontaine-companions.yaml:62`)
9. **`albedo_solar_isotoma` and `navia_cannon_fire_support`** are both 1-Energy
   Rare powers that turn a routine action into Block. The Fontaine sheet flags the
   overlap in its own comment (`docs/fontaine-companions.yaml:106-109`).

---

## 5. Findings (facts only)

1. **21 of 51 Companions grant Block. 30 grant nothing defensive.** No Companion
   in any nation grants any other kind of damage prevention — no ward, no negate,
   no reduction. Block is the only defensive currency the pools have.
2. **7 cards give Block as a rider on something else. 5 of those 7 are unpriced**
   by any of R213 E3's four prices: `lynette_enigmatic_feint`,
   `freminet_pressurized_floe`, `shinobu_sanctifying_ring`,
   `thoma_crimson_ooyoroi`, `itto_superlative_superstrength`. On each, the engine
   effect and the Block both resolve, every time, for the printed cost.
3. **Exactly one card in the whole set prices its Block by the loss of another
   outcome:** `prune_witch_hunt`, where the 5 Block only arrives if the Swirl
   failed to trigger a reaction. It is Klee's personal-pool card, so no drafted
   shared-pool Companion carries that shape.
4. **Exactly one card makes Block cost anything at all:** `arlecchino_masque_red_death`,
   whose Bond of Life eats the first 5 Block you gain each turn. It is the only
   negative-Block effect in the three sheets, and it is a Rare in the pool Kokomi
   does not draw from.
5. **Inazuma — Kokomi's Muster pool — is the most defensive of the three: 9 of 15
   rows carry Block (60%),** against 41% in Mondstadt and 26% in Fontaine.
6. **7 of Inazuma's 9 Skill cards grant Block.** The only two that do not are both
   Kujou Sara's (`sara_crowfeather_cover`, `sara_tengu_stormcall`). If a Muster
   hands Kokomi a Skill, it gives Block 78% of the time.
7. **Three of Inazuma's four 2-Energy cards are attack-plus-Block hybrids**
   (`shinobu_sanctifying_ring`, `thoma_crimson_ooyoroi`,
   `itto_superlative_superstrength`); all three are unpriced.
8. **Muster makes every recruit cheaper and pays Charge.** `_op_conscript`
   (`tier0/engine/effects.py:3369-3416`) gives the recruit `CONSCRIPT_COST_DELTA`
   = -1 cost (floor 0) and sets Exhaust; exhausting a card pays
   `CHARGE_PER_EXHAUST` = 1 Charge (`tier0/constants.py:343`,
   `tier0/engine/refpowers.py:322`). So a Mustered Block Companion in Kokomi's
   hands is *Block, plus one step toward the Charge finisher, at one Energy less
   than printed.* Under Muster, defending never costs her progress toward the
   payoff — this is the mechanical form of "spam companion cards to block until
   you can hit with the Charge".
9. **Two cards are standing Block engines** (`albedo_solar_isotoma`,
   `navia_cannon_fire_support`). Both are bought for defence and nothing else, so
   both classify as PURCHASED — but after the single purchase, each pays Block for
   an action the player takes anyway. Navia's trigger is "you played a Companion
   card". `gorou_heart_of_the_clan`'s Metallicize 2 is a third, weaker version
   (Block every turn for no trigger at all).
10. **Navia is reachable by Kokomi even though she is a Fontaine card.** Muster
    draws home-nation only, but shop slot 2 is wildcard-nation at an Uncommon
    floor (R59), and the Featured Banner is cross-nation. So the
    "play a Companion, gain Block" engine is available to a Muster deck.
11. **`sayu_naptime` is a 0-Energy, hand-neutral 3 Block** (it draws its own
    replacement). It classifies as PURCHASED, but it costs the player nothing at
    all — neither a card nor Energy. Unpriced defence is not confined to the
    subsidized bucket.
12. **Two Block cards also fill a meter for free:** `barbara_melody` (6 Block + 4
    Burst Energy at 1 Energy) and, per turn, `nicole_celestial_gift` (4 Block + 1
    Strength every turn, forever, after one 2-Energy play).
13. **The largest hidden-name cluster is "deal N damage to one enemy and nothing
    else" at 8 cards**, spread across all three nations, differing only in element
    and in a 5/6/7 damage number. The second largest is "Swirl plus one rider" at
    6. Together those two identities are 14 of 51 cards.
14. **Within the "Swirl plus one rider" cluster the riders converge on exactly two
    currencies:** a Block number (`lynette_enigmatic_feint`, `prune_witch_hunt`)
    or a damage number (`lynette_astonishing_shift`, `sayu_yoohoo_windwheel`), with
    two resource variants in Mondstadt (`sucrose_gust`, `sucrose_astable`).
15. **`barbara_shining_idol` prints `dahlia_favonian_favor`'s entire effect plus
    "Draw 1 card", at the same cost, same rarity, same element, on the same
    sheet.** Under the strict-domination rule (R26/R77, scoped to adjacent
    rarities) these two are the same rarity, so this would triage as a defect
    rather than a design call. Recorded here as a fact; not filed, per the audit's
    no-register-edits scope.
16. **Every Companion is upgradeable** (sheet header,
    `docs/mondstadt-companions.yaml:6-17`), so every Block number above is a floor,
    not a ceiling.

---

## 6. Questions for [USER]

Numbered picks. Each option is concrete. No recommendation is made, and R213's
freeze on numeric tuning is assumed to hold — several options below are only
legal on the quarantined prototype surface (shipped; `EB-147` closed at R215).
**Q1, Q2 and Q4 are ANSWERED** — R216 records the picks and each carries the
pick in place of its list. Q3 and Q5 are still open.

### Q1 — The five unpriced subsidized cards — ANSWERED

`lynette_enigmatic_feint`, `freminet_pressurized_floe`, `shinobu_sanctifying_ring`,
`thoma_crimson_ooyoroi`, `itto_superlative_superstrength` all give their engine
effect and their Block together, for one cost, always.

**Pick: (6) — test more than one**, with the two arms being (1) mutually
exclusive (Prune's shape) and (4) the Block priced in the cost line. They run
as competing prototype arms on the quarantined surface; the shipped sheet is
untouched. (R216 C.)

### Q2 — Muster's Charge subsidy (finding 8) — ANSWERED

A Mustered Companion costs 1 less, Exhausts, and pays 1 Charge when played, so
blocking with a Mustered Companion also advances Kokomi's finisher.

**Pick: (5) — defer**, folded into R213 E1's reopened "Charge is uncapped and
never spent" question rather than settled here. (R216 D.)

### Q3 — The two standing Block engines (finding 9)

`albedo_solar_isotoma` (attack an aura'd enemy → 3 Block) and
`navia_cannon_fire_support` (play a Companion → 3 Block).

1. **Keep both as they are.**
2. **Keep one.** The Fontaine sheet's own note says if one has to move, Navia is
   the one, since Albedo predates her and anchors Mondstadt.
3. **Re-trigger them on something the player would not otherwise do** — e.g. pay
   the Block only when you did not attack, or only on the first Companion each
   turn.
4. **Send both to the prototype surface** and let the Kokomi slice decide with a
   real staged turn.

### Q4 — Which pool the Kokomi slice runs against (findings 5, 6) — ANSWERED

Inazuma is 60% Block, and 7 of its 9 Skills give Block.

**Pick: (2) — Inazuma as it ships, plus a priced-defence prototype subset**, so
the two sit side by side in one Muster pool. (R216 B.)

### Q5 — The near-duplicate templates (§4, findings 13, 14)

Two identities hold 14 of the 51 cards, and nine pairs/sets are the same card in
different colours.

1. **Accept it.** Colour variety across nations is the intended texture of a
   shared pool; a vanilla attacker per element is a feature.
2. **Differentiate the riders** so no two Companions in one cluster carry the same
   currency (each Swirl card gets a different second effect; each vanilla attacker
   gains a distinct hook).
3. **Cut the redundant rows** and let each nation's pool be smaller and more
   distinct.
4. **Not now** — leave the pools alone until the Kokomi slice returns, and revisit
   duplication after the defence question is settled.

---

*Sources: `docs/mondstadt-companions.yaml`, `docs/fontaine-companions.yaml`,
`docs/inazuma-companions.yaml`; `tier0/engine/effects.py:3369-3416` (the Muster
verb and its two modes); `tier0/constants.py:343`, `:511`;
`tier0/engine/refpowers.py:322`; `docs/current/LAW.md` (rotation law, healing law,
Charge law); `docs/current/atlas/tier05-economy.md` and
`docs/current/atlas/klee-mod-runtime.md` (the shop's two companion slots, R59/R60/R61);
`docs/current/STATE.md:83-85` (pools ship per nation); R213 (`1050f67`);
`review/records/kokomi-playtest-notes-2026-08-26.md` §B.*

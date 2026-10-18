# The Inazuma companion pool, reworked (2026-10-18)

The user, 2026-10-18: "I think that the entire Inazuma companion pool needs an examination again now that we have two
characters who actually make use of it. ... the upper rarities especially should be more interesting." On the audit's
picks: "agreed on (a) for 1 and 3. For 2, typically off-character cards can give you access to that mechanic, which
might be fine, but we'd need to make sure that the off-character Plan mechanic actually works as expected, or else
remove the Plan aspect." Then: "Ok, agreed on all defaults for both the PR and inazuma companions".

So the direction is ruled: a rework, a few Plan lines if off-character Plans work, and a few cards that suit Yae.
The card designs below are mine and carry no pick. The numbers are first-pass and go to a seat round.

## What the audit found

All of these numbers are checkable: offer and take counts are from `tools/telemetry_report.py --offers --since
2026-10-10`, and the card texts are from `docs/prototype-surface.yaml`.
- **The pool is 21 cards (7 / 10 / 4), half of Mondstadt's 42.** It has no Powers, and Mondstadt has about nine.
- **Eight cards share one shape,** "for N turns, deal X to a random enemy". Sesshou Sakura makes nine.
- **The pool has none of these:** draw (beyond Naptime's conditional draw), Energy, Weak, Vulnerable, Strength,
  Retain, or any way to take enemy Strength.
- **Kokomi's seats take the Rares at about par** (28–31% against an average card's 27%), the Uncommons at 3–20% and
  the Commons at 2–15%. Yae's reward slot only went in on 2026-10-17, so her numbers are too thin to read.
- **Neither kit's mechanic reaches the pool.** No card has a Plan line, and nothing reads or helps Sakura, Edits or
  Weak.

## The order of work

1. **Off-character Plans first.** Plans and the Bake-Kurage are made to work for any character holding a Plan card,
   with tests, as Klee, Furina and Varka were swept (`*OffCharacterSweepTests`). This is the BACKLOG line due at
   Kokomi's Balance anyway, and it is being built now.
2. **Then the cards.** The four Plan-line cards below ship with their Plan lines only if step 1 passes. If it can't
   pass, each drops its Plan line and keeps the text marked "without Plans".
3. **Then a seat round** (a new card batch): two seats, Kokomi and Yae, each with one record.

## The pool after: 29 cards (8 / 13 / 8), 6 Powers

**Kept as they are (10):** Sayu, Yoohoo Art: Fuuin Dash; Shinobu, Grass Ring of Sanctification; Shinobu,
Thundergrust; Thoma, Blazing Barrier; Kujou Sara, Crowfeather Cover; Shinobu, Sanctifying Ring; Kazuha Slash;
Yae Miko, Sesshou Sakura (still hidden from Yae); Kamisato Ayaka, Soumetsu; Yumemizuki Mizuki, Anraku.

**Cut (3):**
- **Yoimiya, Aurous Blaze:** it's a weak timed-damage card. Yoimiya returns as a Rare.
- **Raiden Shogun, Musou no Hitotachi:** a 3-Energy card that counts companions, and seats play about one. Raiden
  returns as a Rare and an Uncommon.
- **Itto, Superlative Superstrength:** a stat card at Rare. Itto returns as a Rare and an Uncommon.

### Commons (8: 5 kept, 2 rebuilt, 1 new)

| Card | Cost | Text |
|---|---|---|
| Shikanoin Heizou, Heartstopper Strike (rebuilt) | 1 Attack | Deal 4 Anemo damage, plus 4 for each other Attack you played this turn. |
| Sayu, Naptime (rebuilt, Plan) | 1 Skill | Gain 7 Block. Plan: Gain 7 Block and draw 1 card. *Without Plans:* Gain 9 Block. |
| Kamisato Ayaka, Kamisato Art: Hyouka (new) | 1 Attack | Deal 4 Cryo damage to ALL enemies and apply 1 Weak to each. |

- **Heartstopper** no longer needs Swirls from other cards. It is a Finisher at a Common rate.
- **Naptime** was 4 Block in an Attack deck. It now follows the "no cycling at Common" rule, since its draw is a turn
  late and costs 1.
- **Hyouka** is the Ironclad's Thunderclap with Weak instead of Vulnerable. Weak is what Yae's Fox's Verdict,
  Saiguu's Lesson and Foxfire Lure read.

### Uncommons (13: 4 kept, 5 rebuilt, 4 new)

| Card | Cost | Text |
|---|---|---|
| Kirara, Surprise Dispatch (kept, Plan added) | 1 Skill | Gain 8 Block. Next turn, deal 10 damage to a random enemy. Plan: Gain 14 Block. |
| Sayu, Muji-Muji Daruma (rebuilt, Plan) | 1 Skill | Gain 6 Block. Plan: Gain 1 Energy and 6 Block. *Without Plans:* Gain 6 Block. Next turn, gain 1 Energy. |
| Thoma, Crimson Ooyoroi (rebuilt, Power) | 1 Power | At the start of your turn, keep up to 6 of your Block. |
| Kujou Sara, Tengu Stormcall (rebuilt) | 0 Skill | Apply 2 Vulnerable. Your next Attack this turn applies Electro. |
| Chiori, Fluttering Hasode (rebuilt) | 1 Attack | Deal 5 Geo damage twice. This ignores Block. |
| Kamisato Ayato, Kyouka (rebuilt) | 1 Skill | Apply Hydro to ALL enemies. This turn, your Attacks deal 3 more damage. |
| Itto, Ushi to the Rescue (new) | 1 Skill | Gain 8 Block. If an enemy intends to attack, gain 1 Strength. |
| Raiden Shogun, Transcendence: Baleful Omen (new) | 1 Skill | ALL enemies lose 2 Strength this turn. Your next Attack this turn applies Electro. |
| Yumemizuki Mizuki, Aisa Utamakura (new) | 1 Skill | Draw 2 cards. Mend 4. |
| Shikanoin Heizou, Windmuster Kick (new) | 2 Attack | Deal 12 Anemo damage and Swirl the enemy. Draw 1 card. |

The four kept Uncommons (Sanctifying Ring, Kazuha Slash, Sesshou Sakura, Kirara) are taken at 11–20%, and between
them they keep the pool's one Swirl-to-all and its one Sakura.
- **Ooyoroi** is Thoma's stacking shield. It keeps part of your Block, as the Calipers do, and it is the one
  Uncommon Power. Kokomi's Read the Tide wants exactly this.
- **Tengu Stormcall** is the base game's Trip with an Electro rider.
- **Baleful Omen** is the pool's only way to take enemy Strength, as a 1-turn Disarm to every enemy.
- **Aisa Utamakura** is draw with a Mend. Kokomi already uses Mend.

### Rares (8: 2 kept, 6 new; 5 Powers)

| Card | Cost | Text |
|---|---|---|
| Raiden Shogun, Plane of Euthymia (new) | 2 Power | At the end of your turn, Retain your Hand. |
| Itto, Royal Descent: Behold, Itto the Evil! (new) | 2 Power | Whenever an enemy's attack deals you no damage, deal 6 Geo damage to it. |
| Yoimiya, Niwabi Fire-Dance (new) | 2 Power | The first Attack you play each turn is played twice. |
| Kaedehara Kazuha, Chihayaburu (new) | 1 Power | Whenever you Swirl, draw 1 card. |
| Wanderer, Hanega: Song of the Wind (new) | 1 Power | At the start of your turn, gain 1 Energy. You can't gain Block. |
| Kamisato Ayato, Kyouka Fuushi (new, Plan) | 2 Attack | Deal 7 Hydro damage 3 times. Plan: Deal 7 Hydro damage 3 times, and once more for each Plan carried out before it this turn. *Without Plans:* Deal 7 Hydro damage 3 times. Costs 1 less if you played a Skill this turn. |

Each Rare now changes how you play, not how much you deal:
- **Euthymia** is Raiden's eternity: your hand stops leaving. It's the base's Runic Pyramid as a card. It also helps
  Yae, whose Annotated cards wait for the right turn.
- **Royal Descent** turns full Blocks into counterattacks, Kokomi's "survive, then turn it into damage" in another
  character's voice.
- **Niwabi** is a two-for-one on your first Attack every turn, and it decides your openings.
- **Chihayaburu** makes Swirl a draw engine for the pool's four Swirl cards.
- **Hanega** is the hard bend: an Energy a turn for giving up Block. It's built for fragile, fast decks (Klee), and
  a trap for Kokomi, on purpose.
- **Kyouka Fuushi** is the Plan Rare. On the Bake-Kurage at the end of a long morning, it is Kokomi's best finisher.

Yae fit (pick 3 (a)): Hyouka's Weak (which three of her cards read) and Euthymia's Retain suit her without naming her mechanic. My
audit's other example ("turn-end damage that counts as a Sakura strike") would only mean something on Yae, so it
belongs in her own pool and is not built here. **One open check:** does Red Ink's "3 more damage" add per hit? If it
does, Chiori and Kyouka Fuushi are Yae's best Edit targets in the pool.

## Rates against the companion standard

The companion standard says a Common may be weak and an Uncommon or Rare is Colorless-tier, a little above the
character's own.
- **Commons:** Hyouka and Heartstopper sit at the base Common rate, and Naptime a little under it.
- **Uncommons:** each matches a base Uncommon or Colorless card (Trip, Disarm, Calipers, Finisher).
- **Rares:** each is a bend with a cost:
  - Euthymia costs 2 Energy.
  - Hanega gives up Block.
  - Niwabi only touches one card a turn.
  - Royal Descent needs full Blocks.

## Not changed

- No starter, and no kit's own pool.
- No Mondstadt or Fontaine companion.
- No offer rule. Banner gating now applies to Inazuma, which has 8 Rares, more than the banner's 3.
- Gorou's four cards stay in Kokomi's pool.
- Art: the new characters and cards (Wanderer, Hyouka, Ushi, Baleful Omen, Aisa Utamakura, Windmuster Kick, Euthymia,
  Royal Descent, Niwabi, Chihayaburu, Hanega, Kyouka Fuushi) need card art: official art of that character, picked in
  the art pass that builds them.

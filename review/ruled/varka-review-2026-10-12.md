# Varka review: Pyro, Anemo, switch against mono, and his Ancients, 2026-10-12

This is the Varka half of the review. Your agenda:
- "his Pyro core is still 'up for grabs' if we can't make the Strength / Exhaust ideas work out, and we need to make sure that Anemo actually makes sense as a thing you do";
- "too much power hiding in some of the 'switch vs mono-element' cards and relics ... more a vibe than a firm design theory";
- "more tinkering with specific card effects than redesigning how Oath and Knights work."

**Evidence.** The packet is `scratchpad/varka-review/packet.md` (gitignored). It covers:
- 44 Varka run-lines since 2026-10-07 and 941 solo fights in telemetry;
- the offer logs;
- the tracked records.

The builds changed between rounds and seeds repeat, so every comparison below is a distribution, not a controlled test.

## Where he stands

- **He wins at A0 more than the base five do.** He won 9 of 44 run-lines, and most deaths reached act 3. The base five's A0 baseline was 0 of 5.
- **He hits slightly harder than base and takes more damage late.** Normal-fight damage per turn is 1.05, 1.12 and 1.12 times base across acts 1 to 3. HP lost is 0.40, 0.56 and 1.11 times base.
- **His deaths are Block deaths.** "Every death came on a boss turn short of Block" (wave 1). The A5 and A8 deaths "followed a turn spent on damage when it should have gone on Block". That is the Block paper's ground (`varka-block-paper-2026-10-12.md`, built), so it isn't reopened here.

## 1. Pyro: the Strength core now works

The Strength version (Ashen Oath gives Strength, Ember Cleave gives Strength this turn, Stoke adds +5 to the next Pyro Attack) landed on 2026-10-12.
- **Pyro cards are drafted now:** 30% take rate, up from 12 to 16% under the Exhaust texts.
- **The wave-2 Pyro win was a real Pyro deck.** Its plays: Ashen Oath 12, Stoke 11, Blazing Charge 16. It reached 5 Strength or more in a tenth of its fights.
- **The two wave-2 Pyro losses were close:** one left the final boss at 1 HP, the other died on 3 HP.
- **Ember Cleave lags:** 1 of 6 in wave 2, 8 of 80 overall. "Deal 7 Pyro, gain 2 Strength this turn" is a Strike-plus that pays only if a second Attack follows. I'll raise it to 9 [11]; that's a card number, my call.

**Your earlier worry was "too niche and self-contained".** The new Pyro cards each do something alone: Strength, damage and Oath. So I'd stop calling the Pyro core up for grabs. That's pick 1.

## 2. Anemo is the plan, not the glue

Your test was "could you run a deck that's half Anemo and half whatever other element pieces you saw". It's what every seat does:
- **Anemo cards are his most-taken tag:** 30%, against 15 to 18% for each element.
- **Anemo is the largest damage source.** Counting Windbound, his other Anemo cards, Four Winds' Ascension and Swirl together, it's over half of his credited damage.
- **Half-Anemo decks went deep:** in wave 1, 5 of 6 runs reached the act-3 boss.
- **Pure Anemo doesn't work, as intended.** Only one run drafted 40% or more Anemo, and it died on floor 44. Anemo needs an element to Swirl and to pay out.

**No change.**

## 3. Switch against mono: the vibe isn't in the numbers

**The worry:** relics and cards that let him switch elements and still bank Oath at once.

**What the data shows:**
- **No runaway.** The two highest Oath peaks (25 and 27) came from mono runs, one Hydro and one Pyro. The highest-switching run (2.4 switches a fight) peaked no higher than the rest.
- **Mono, mixed and switch decks finish alike.** Mono decks won 3 of 7 and switch decks 2 of 11. Ascension damage per play is close: 24.4 mono, 23.3 mixed, 22.1 switch.
- **The relic most likely to break it hasn't been seen.** Banner of the West Wind carries Oath across a switch, but no seat has held it. Windblume Garland hasn't been held either.
- **The one strong switch engine** was four copies of Cycle of Seasons (17 to 27 damage a switch). That's a thin-deck loop the seat had to assemble, which your loop rule allows.

**No change.** I'll read Banner of the West Wind the first time a seat holds it. That's pick 2.

## 4. Four Winds' Ascension: the signature, and it works

- It is 19% of his damage, 22% in boss fights.
- He plays it once in 70% of fights, and twice or more in 68% of boss fights.
- That makes it his Osty: the card every fight is built around. Playing it every fight is the design, not repetition.
- Andrius's Howl (it returns to hand each turn) reached 2.5 plays a fight in its one run, an A5 run that died on floor 40. That's one sample; I'll watch it.

**Text fixes (my calls, no pick):**
- Boreas's Fang will say the Ascension "returns after a reshuffle". A seat was surprised by it, and the text doesn't say so.
- Wolfpack's shuffled copy will show on the page.
- `STATE.md` will say the upgrade is "costs 1", which is what the code does. It currently reads "10 [13] ... 3 [4] per Oath".

## 5. Reading the switch

**The records' complaint:** a non-Knight card can move his current element off his best Oath, and he only finds out afterward. Knights already carry "Knight, Pyro" in the hand row.

**Fixes (my calls, no pick):**
- Stoke the Flames' text will say "Pyro becomes your current element." The code does this, and the card doesn't say so.
- Any card of his that would change the current element will show "(Makes Pyro current)" in combat, the same in-combat preview Kokomi's Plans use. This covers Kindled Edge, Charged Lunge and others.
- The "Pyro Oath (left)" lines after a switch go, since a seat called them "noise".

## 6. His missing Ancient cards

Klee, Kokomi and Furina each have two Ancient cards: big rewards from an Ancient, one of which bends the kit's own rule (Alice's Masterpiece leaves a set-off Bomb at half size). Varka has none, so Darv's Tome hands him a Four Winds' Ascension. Proposed:
- **All Four Winds** (Power, 3 [2]): "Your cards read your Oath of every element together."
  - It is the Rare Elixir of the Four Winds' one-turn effect, for the whole combat.
  - It is the "both at once" power you worried about, sold openly as the once-a-run bend.
- **Dandelion Gale** (Attack, 2): "Deal 9 [12] Anemo damage to ALL enemies. Swirl every aura. These Swirls pay twice."
  - It is the big Swirl turn the Anemo half builds toward.

## Ruled 2026-10-12

[USER]: "On Varka - wow, ok, sounds like we've outright solved the open issues. Pending my playtest, I guess, but we might be about to hit Balance." On the Ancients: "Both sound workable to me - Dandelion Gale could be the Replace version."

- **Picks 1 and 2, (a).** Pyro is settled, with Ember Cleave at 9 [11]. Switch against mono is unchanged.
- **Pick 3, (a), with Dandelion Gale as the replace card.** The base game has two Ancient rewards:
  - Darv's Dusty Tome adds a random Ancient card.
  - Orobas's Archaic Tooth turns the character's own starter card into its stronger version (Bash to Break, Dualcast to Quadcast).
  - So **All Four Winds** is his Dusty Tome card, and **Dandelion Gale** is Windbound Execution's replacement.
  - Dandelion Gale costs 1, like a starter-slot card should: "Deal 7 [10] Anemo damage to ALL enemies. Swirl every aura. These Swirls pay twice."
  - Darv's Tome stops handing him Four Winds' Ascension.
- **Next:** your playtest, then Balance.

## For [USER] (ruled above)

1. **Pyro core.**
   - **(a) Default:** settled as built (Strength core), with Ember Cleave at 9 [11].
   - (b) Still open: one more Pyro pass.
2. **Switch against mono.**
   - **(a) Default:** no change; read Banner of the West Wind when a seat holds it.
   - (b) Trim the switch payoffs now: Cycle of Seasons 7 → 5.
3. **Ancient cards.**
   - **(a) Default:** both, All Four Winds and Dandelion Gale.
   - (b) All Four Winds only.
   - (c) Different ideas. Tell me the feel you want.

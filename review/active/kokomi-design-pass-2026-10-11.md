# Kokomi: Plans and Ethereal, the Casket gone (2026-10-12)

**Why.** From [USER]'s run (`review/records/kokomi-user-run-2026-10-11.md`): "I won the Kokomi run, but honestly... it felt clunky. Not difficult, but clunky. The early game was slow and the late game was Plan Spam." Then, over three rounds of this paper's first draft:

> "lots of small plans" vs "one really big plan" is not actually compelling as an archetype split, so the runs devolve into one note builds. ... The Plan mechanic is fine; I just don't think it can carry a character by itself with no other archetype options.

> Kokomi is a support type character, so I'm thinking the answer comes from one archetype flavored through Companion cards and another archetype that flavors with her jellyfish. ... it should tie into the established machinery or the Plan track so we aren't inventing a second piece of bespoke kit just for her.

> it's dangerous having multiple archetypes with isolated payoff structures. Players should feel like they can slightly dip off of their main drafting strategy without having one side brick the other. ... I actually wonder if the Casket itself is the problem and we should leave the Plan track as the only piece of core machinery on the kit, then balance around a normal amount of Strength, not 10 to 20. One random idea - we haven't used Ethereal much so far in character design.

On the relic: "Let's tentatively go with option 1."

Ruled out on the way: Block and debuff archetypes (Varka already has both), and a Casket that forks between two archetypes (whichever way you open it, one side is bricked).

This paper sets the direction. The card-by-card list follows the ruling, as its own paper.

**Source.** A census of her 78-card pool on `main` (session scratchpad, `kokomi-archetype-census.md`): each card tagged from its text, offers and takes from `tools/offer_report.py` over five lanes (2026-10-08 to 2026-10-11; the pool changed during the window), plays from fight telemetry.

## 1. Why every run is the same deck

- **The Casket feeds every deck.** Every Plan adds a point, and every point is Strength. The Plan payoffs are taken 75% to 82% of the time (Flood Tide, Grand Design, Masterstroke, Surging Shoal). Her other payoffs are almost never taken: Block payoffs 4 of 59 offers, and Watatsumi's Grace, Tidal Rebuke, Tidal Riposte, Ceremonial Garment, Sea's Reproach and At Water's Edge never.
- **Eight things to count.** Her cards read the Casket, Plans carried out this turn, Plans waiting, Plans written this turn, Energy paid for waiting Plans, "only" or "exactly one" Plan, the first Plan or the Plan after this one, and 0-cost Plans written.
- **A free engine.** 15 of 78 cards cost 0, and Kurage Swarm, Kurage School and Shoal Call multiply the 0-cost Plans. A late turn is clicking Plans.
- **A slow start.** A Plan pays next turn, and act-1 fights last about 3 turns. The seats lost a median 12.5% of max HP in each act-1 normal fight.

## 2. The proposal

### 2.1 What stays

The Plan rules (brief sec.2, rules 1 to 6): the Bake-Kurage, Plan lines, carry-out order, Dusk, the queue. Her starter cards. Nereid's Ascension and the order riders (Opening Gambit, Second Wave), which make queue order a decision.

### 2.2 The Casket goes

The Tamakushi Casket's count, Open the Casket, and the 10 cards that read or feed the count (Shell Guard, Driftglass, Depths' Judgment, Coral Tithe, Flood Tide, What the Tokoyo Returns, Abyssal Salvage, Grand Design, Kurage Swarm, What the Tokoyo Took). Her Strength comes from ordinary cards at a base-game level: one Uncommon in the Inflame class, no per-Plan Strength.

### 2.3 The starter relic

"At the end of your turn, if a Plan is waiting, gain 3 Block." (Tentatively ruled.) It pays for writing at least one Plan a turn and covers her slow start, as Burning Blood covers the Ironclad. The relic can keep the Tamakushi Casket's name and art.

### 2.4 Ethereal is how the pool talks to Plans

Ethereal is the base game's keyword: a card still in hand at the end of the turn Exhausts. Writing a card as a Plan takes it out of the hand, so **writing an Ethereal card as a Plan already saves it.** No new rule is needed. Her turn becomes "now, later, or lose it", and her Ethereal cards can be printed above rate, because the price is timing.

### 2.5 Two flavours on one track

Both flavours make Ethereal cards and spend them through Plans, so both read the same payoffs. A deck can lean one way and dip the other without either side going dead.

- **The Commander (her allies).** Some of her cards call Companions: "Add 2 random Inazuma Companions to your hand. They are Ethereal." A Companion card can be written as a Plan and is carried out as printed (pick 4). Her Plans apply Hydro, and the Companions bring Pyro, Electro and Cryo, so the order of the queue sets up the reactions at dawn. Gorou's four cards become her signature.
- **The Kurage (the jellyfish).** Some of her cards make small Ethereal jellyfish cards, shaped like Nip (a sting, a ward, a mend for a partner in co-op), which cost Energy and are hers to use, write or lose. Kurage cards make them bigger or more frequent. The jellyfish still never acts on its own (rule 4); it acts through the cards it hands you.
- **Shared payoffs** read the track both flavours use: "Whenever you write an Ethereal card as a Plan ...", "Whenever a Plan causes a reaction ...", Plans waiting. No payoff reads a resource only one flavour makes.
- **Klee's Companion cards** pay for playing a Companion. Kokomi's pay for writing one as a Plan and for the reactions at dawn, so the two kits draft Companions differently.

### 2.6 The spam is designed out

Generated cards cost Energy, never 0. The 0-cost Plan Commons are cut down, Kurage School goes, and Shoal Call becomes a Kurage card that makes Ethereal jellyfish cards. Draw moves toward a base character's density. Cards read only Plans waiting or a trigger.

### 2.7 The start

The relic's Block, and Commons whose now-line pays this turn.

## 3. Risks

- **Losing cards feels bad.** Above-rate numbers must be visible on the card, and Ethereal cards come from her own generators, not as random handouts.
- **Volume.** Two generator flavours could rebuild the spam. Generated cards cost Energy, and the card paper caps generators per rarity.
- **Companion supply.** The Commander needs Companions beyond the fourth reward slot; the generators supply them, so the slot stays a bonus, as ruled for the Companion pass.
- **The relic** could make "write one Plan, pass" the safe default. 3 Block is sized under a Defend so that it is not.

## 4. Next

Fable's review (below), your picks, then the card paper: what each of the 78 cards keeps, changes or loses, with take rates. Then the build, a seat round and your run.

## For [USER]

1. **Direction.**
   - **(a) Default:** Plans and Ethereal are the spine, with the Commander and the Kurage as two flavours on shared payoffs.
   - (b) Something else (say what).
2. **The Casket.**
   - **(a) Default:** removed, with its 10 cards; Strength at a base-game level.
   - (b) Kept as one Rare card's effect, not the relic.
3. **The starter relic** (this changes her starter).
   - **(a) Default:** "At the end of your turn, if a Plan is waiting, gain 3 Block."
   - (b) Another (say what).
4. **Companions as Plans.**
   - **(a) Default:** any Companion card can be written as a Plan and is carried out as printed.
   - (b) Only the Companions her own cards generate.
5. **Dusk.**
   - **(a) Default:** it stays; the card paper cuts the Dusk cards that are only slow Block.
   - (b) Retire it.

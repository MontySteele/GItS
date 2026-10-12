# Kokomi: Plans and Ethereal, the Casket gone (2026-10-12)

**Why.** From [USER]'s run (`review/records/kokomi-user-run-2026-10-11.md`): "I won the Kokomi run, but honestly... it felt clunky. Not difficult, but clunky. The early game was slow and the late game was Plan Spam." Then, over three rounds of this paper's first draft:

> "lots of small plans" vs "one really big plan" is not actually compelling as an archetype split, so the runs devolve into one note builds. ... The Plan mechanic is fine; I just don't think it can carry a character by itself with no other archetype options.

> Kokomi is a support type character, so I'm thinking the answer comes from one archetype flavored through Companion cards and another archetype that flavors with her jellyfish. ... it should tie into the established machinery or the Plan track so we aren't inventing a second piece of bespoke kit just for her.

> it's dangerous having multiple archetypes with isolated payoff structures. Players should feel like they can slightly dip off of their main drafting strategy without having one side brick the other. ... I actually wonder if the Casket itself is the problem and we should leave the Plan track as the only piece of core machinery on the kit, then balance around a normal amount of Strength, not 10 to 20. One random idea - we haven't used Ethereal much so far in character design.

On the relic: "Let's tentatively go with option 1."

Ruled out on the way: Block and debuff archetypes (Varka already has both), and a Casket that forks between two archetypes (whichever way you open it, one side is bricked).

This paper sets the direction. The card-by-card list follows the ruling, as its own paper. A Fable reviewer read the second draft (session scratchpad, `kokomi-design-review-fable.md`); this draft takes its changes, listed in sec.5.

**Source.** A census of her 78-card pool on `main` (session scratchpad, `kokomi-archetype-census.md`): each card tagged from its text, offers and takes from `tools/offer_report.py` over five lanes (2026-10-08 to 2026-10-11; the pool changed during the window), plays from fight telemetry.

## 1. Why every run is the same deck

- **The Casket feeds every deck.** Every Plan adds a point, and every point is Strength. The Plan payoffs are taken 75% to 82% of the time (Flood Tide, Grand Design, Masterstroke, Surging Shoal). Her other payoffs are almost never taken: Block payoffs 4 of 59 offers, and Watatsumi's Grace, Tidal Rebuke, Tidal Riposte, Ceremonial Garment, Sea's Reproach and At Water's Edge never.
- **Eight things to count.** Her cards read the Casket, Plans carried out this turn, Plans waiting, Plans written this turn, Energy paid for waiting Plans, "only" or "exactly one" Plan, the first Plan or the Plan after this one, and 0-cost Plans written.
- **A free engine.** 15 of 78 cards cost 0, Kurage Swarm, Kurage School and Shoal Call multiply the 0-cost Plans, and seven cards pay Energy (War Council, Riptide, Vanguard, Lull, The Long Game, Patient Tide, Stolen Chapter). A late turn is clicking Plans.
- **A slow start.** A Plan pays next turn, and an act-1 fight lasts about 3 turns. Act-1 normal fights cost her 8.4 to 8.8 HP against base's 5.6 (`review/records/kokomi-fullrun-round-3-2026-10-11.md`, rounds 3 and 4), a median 12.5% of max HP in round 4 by GPT's count (`review/active/four-character-independent-review-2026-10-11.md`).

## 2. The proposal

### 2.1 What stays

The Plan rules (brief sec.2, rules 1 to 4 and 6): the Bake-Kurage, Plan lines, carry-out order, the queue. The halves rule (brief sec.3): a Plan line never does the same thing as the now-line, later. Her starter cards. Nereid's Ascension and the order riders (Opening Gambit, Second Wave), which make queue order a decision.

### 2.2 What goes

- **The Casket:** its count, Open the Casket, and the 10 cards that read or feed it (Shell Guard, Driftglass, Depths' Judgment, Coral Tithe, Flood Tide, What the Tokoyo Returns, Abyssal Salvage, Grand Design, Kurage Swarm, What the Tokoyo Took). Her Strength comes from ordinary cards at a base-game level: one Uncommon in the Inflame class (Inflame is an Uncommon, 1 Energy, 2 Strength in `game_ref/ironclad-cards.yaml`). Masterstroke and Surging Shoal ("Strength affects this Plan 3 times / twice", taken 75% and 82%) and the multi-hits were written for Casket Strength; the card paper retargets or cuts them.
- **Dusk** (pick 5). [USER] said Dusk Plans "feel kinda silly", and the reason they existed (a Casket point and an effect the same turn) leaves with the Casket. Breakwater's "3 more for each Plan waiting" becomes a now-line.
- **0-cost Plans.** No card with a Plan line costs 0. Nip-shaped Plans live on as the Kurage's jellyfish cards (2.5), at cost 1.

### 2.3 The starter relic

"At the end of your turn, if a Plan is waiting, gain 3 Block." (Tentatively ruled.) About 9 Block in a 3-turn act-1 fight, against Burning Blood's 6 HP. It pays for writing at least one Plan a turn; with no 0-cost Plans left (2.2), that Plan costs Energy, so the condition is a real price. The relic can keep the Tamakushi Casket's name and art.

### 2.4 Ethereal: what it changes

Ethereal is the base game's keyword: a card still in hand at the end of the turn Exhausts. The Necrobinder has 16 Ethereal cards of 91, four of them Common (`game_ref/necrobinder.json`), so above-rate Ethereal at Common is base-game practice.

A card she does not play is discarded today and comes back after the next reshuffle. An Ethereal one is gone for the fight. Writing it as a Plan takes it out of the hand, so the Plan is how she keeps it, at its full cost now. Her turn is then an Energy question: which cards to play for this turn, which to write for tomorrow, which to let go. The second question, as now, is the order of the queue.

### 2.5 Two flavours, mostly shared payoffs

- **The Commander (her allies).** A few of her cards hand her Companions: "Add 2 random Common Inazuma Companions to your hand. They are Ethereal." A Companion card can be written as a Plan, and **the Bake-Kurage applies Hydro to its target first**, so a written Companion reacts and a played one does not. That is the two halves doing different things. Her Inazuma roster is Electro 7, Geo 5, Anemo 5, Pyro 3, Cryo 1, so the usual reactions are Electro-Charged, Crystallize (Block) and Swirl, with Vaporize from the three Pyro cards. Gorou's four cards are her signature.
- **The Kurage (the jellyfish).** A few of her cards make small Ethereal jellyfish cards, Nip-shaped (a sting, a ward), at cost 1, to use, write or lose. Kurage cards make them bigger or more frequent. The jellyfish still never acts on its own (rule 4); it acts through the cards it hands her. Its Hydro is what the Commander's written Companions react with, so a Commander deck that dips into the Kurage gains, and the reverse.
- **Payoffs.** Commons and Uncommons read the track both use: "Whenever you write an Ethereal card as a Plan ...", and Plans waiting. One Rare per flavour reads its own thing: the Commander's reads reactions caused by Plans; the Kurage's reads jellyfish cards. A Rare bends, and the shared Commons keep a dip from bricking.
- **Generated cards Exhaust** when played or carried out, as the base game's generated cards do, so they never cycle back through the discard pile. A generator makes at most 2 cards.
- **Klee's Companion cards** pay for playing a Companion; Kokomi's pay for writing one. Watatsumi Resistance and Gorou's Crystal Collapse read Companion plays today: the card paper either counts a carried-out Companion as played or replaces them.

### 2.6 The spam is designed out

No 0-cost Plans; generated cards cost Energy and Exhaust; Kurage School goes; Shoal Call becomes a Kurage card. The Energy Plans (War Council, Riptide, Vanguard, Lull, The Long Game, Patient Tide, Stolen Chapter) are trimmed in the card paper, and draw moves toward a base character's density. Cards read only Plans waiting or a trigger.

### 2.7 The start

Her Commons get now-lines that pay this turn; the relic adds a little Block. The card paper keeps a Block-card count as a line, since Shell Guard and the Dusk Block go and earlier rounds found her decks thin on Block.

## 3. Risks

- **Losing cards feels bad,** most of all on turn 1. Ethereal cards come from her own generators, at most 2 at a time, with above-rate numbers on the face.
- **The Commander's ceiling.** Random Companions could hand her a Rare (Raiden, Itto, Ayaka) at 1 Energy; the generator draws Commons only.
- **Healing.** A jellyfish card that Mends a partner would break `LAW.md` (true healing is Rare and Exhausts). There is none.
- **Co-op.** Her dawn reactions consume the aura a partner set up. A co-op round reads it.

## 4. Next

Your picks, then the card paper: what each of the 78 cards keeps, changes or loses, with take rates, a Block count, an Energy and draw count, and the generator list. Then the build, a seat round and your run.

## 5. What the Fable review changed

Fable's review (scratchpad, `kokomi-design-review-fable.md`) checked the claims against the census, `game_ref/` and the element code. Taken: Companion Plans must differ from playing them (the halves rule), so the jellyfish applies Hydro first; generated cards Exhaust so they do not cycle back; the Energy Plans join the trim; the reaction payoff is the Commander's Rare, not shared (in solo the jellyfish's Hydro only refreshes Hydro); one Rare per flavour; Common-only Companions from the generator; Dusk retired; Masterstroke and Surging Shoal named; a Block count in the card paper; no partner Mend; the act-1 HP numbers corrected; the Necrobinder cited. Checked in code, and holding: Plans carried out in order apply and react before the aura tick, and the reacting hit is the one amplified; each reaction eats the aura, so a queue alternates Hydro and another element. Not taken: the review's reading that Ethereal removes "keeping a card in hand"; unplayed cards are discarded at the end of a turn anyway, so what Ethereal removes is the card coming back later (sec.2.4).

## For [USER]

1. **Direction.**
   - **(a) Default:** Plans and Ethereal are the spine; the Commander and the Kurage are two flavours with shared Common and Uncommon payoffs and one Rare each.
   - (b) Something else (say what).
2. **The Casket.**
   - **(a) Default:** removed, with its 10 cards; Strength at a base-game level; Masterstroke and Surging Shoal retargeted or cut.
   - (b) Kept as one Rare card's effect, not the relic.
3. **The starter relic** (this changes her starter).
   - **(a) Default:** "At the end of your turn, if a Plan is waiting, gain 3 Block."
   - (b) Another (say what).
4. **Companions as Plans.**
   - **(a) Default:** any Companion card can be written as a Plan; the Bake-Kurage applies Hydro to its target first.
   - (b) Only the Companions her own cards generate, with the same rule.
   - (c) Companions are not Plans; the Commander's payoffs read Companion plays.
5. **Dusk.**
   - **(a) Default:** retired; its cards become now-line cards or go.
   - (b) Kept.

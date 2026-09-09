Status: RULED R269 2026-09-08

The working theory gave way to the Stage brief,
`review/active/furina-stage-brief-2026-09-08.md`; PR #433 closed with it.

# Furina, back to the identity: three concepts, none of them the stage

Written 2026-09-07, night. After three passes on the Salon panel and the
stage-direction packet (`review/active/furina-stage-direction-2026-09-07.md`,
PR #433), [USER] stopped the polishing: it does not feel right, the
question goes back to the design layer, and the answer must not be a Defect
with Fanfare for Focus. GPT's read of the same day agrees: slots, a front,
replacement payoffs and a scaling stat were held fixed while we argued what
activates them, and that frame is Defect's whatever fires it. So: what the
character is, then three concepts that differ from each other, none
required to keep the Salon queue, Encore or Fanfare, each tested the same
way. The current build stays deployed as the reference.

## 1. What the repo already says she is

`docs/current/characters/furina-identity-record.md` (the LAW text as it stood
until 2026-09-01): Hydro, skill-grade **support-protagonist**, modest
numbers, scaling that routes through others; elite sustain and elite
utility, a dreadful frontload and a real setup tax
(`furina-kickoff-v0.1.md` §2). The kickoff's one line: "her numbers are
modest, her cast is not."

What the source character does, because it matters here: her Salon
members hit harder by **spending the party's HP** while HP is high; her
Singer **heals**; and her Fanfare grows on **every HP change in the party,
up or down**, and amplifies both the hitting and the healing. Her duality
is a conversion: damage taken becomes healing power, healing done becomes
hitting power. The old LAW carried half of this ("every point of damage
past Block prints exactly 1 Fanfare", identity record) and the reframe of
2026-08-29 dropped it when Fanfare became the Salon's Focus. That is the
step where she became an Orb character.

The identity, in one sentence to hold the concepts against: **Furina's
party is the show; she turns what happens to it into damage and back into
protection, and her numbers are small on their own.**

## 2. The test each concept has to pass

GPT's four, plus [USER]'s one. Each concept shows: an ordinary turn with a
real choice; a payoff that follows from earlier decisions; what defence
looks like when the setup is missing; what a Companion card contributes
that her own cards do not; and why someone would pick her over Defect.
Numbers below are illustrative and are not sheet numbers.

## 3. Concept A: the Tide (duality by conversion)

**Rule.** Her Attacks carry a **Spend** line: "Spend 4 HP: this deals 12
instead of 7." Spend is allowed only above half HP. Her Skills heal and
Block. One number on her, **Fanfare**, grows by 1 for every point of HP any
ally loses, spends or regains this combat. Her Burst (the kit-Burst the
game already grants on meter fill) is "Let the People Rejoice": heal the
party for half of Fanfare, deal Fanfare to all enemies, Fanfare to 0.

**Ordinary turn.** 52 of 78 HP, hand Salon Solitaire (Spend 4: 12 to one),
Surging Waters (heal 5, Block 5), Strike, Defend. The enemy intends 11.
Spend and hit for 12 (Fanfare +4, HP 48) then heal 5 (Fanfare +5), or hold
HP and Block. Both routes move Fanfare; the question every turn is how low
she is willing to run for how much.

**Payoff.** A fight of spending and healing banks 40 Fanfare; the Burst
heals the party 20 and hits everything for 40. The payoff is the story of
the fight so far, cashed once, and the decision is when.

**Defence without setup.** Below half HP, Spend is closed by rule, her
Skills heal and Block as ordinary cards, and the Burst is the recovery.
Nothing to summon, nothing to fill.

**Companions.** Their Pyro, Cryo and Anemo react off her Hydro, which is
where her damage ceiling lives; and in co-op the whole party's HP prints
Fanfare, so she is the healer whose engine runs on the team's fights.

**Not Defect because** there is no slot object and nothing scales on its
own; the engine is the HP bar you already watch, and nobody else in StS2
touches healing.

**Cost.** Reopens "true healing is Rare and Exhausts" (kickoff §4, R8 of
the m7 rulings): the loop needs Common heals. HP-spend in a permadeath
game needs the half-HP gate and the sim's dead-run rate before a flag.

## 4. Concept B: the Arkhe (duality by switching)

**Rule.** The Salon is **one summon with two faces**. In **Ousia** it is
the trio and hits at the end of your turn (Hydro on the target); in
**Pneuma** it is the Singer and heals and Blocks the party at the end of
your turn. Her cards have two texts, one per face: "Ousia: deal 9. Pneuma:
heal 3 and Block 4." A card with **Arkhe** flips the face when played. The
first performance after a flip is an **Encore** and is doubled; the Burst
meter fills on flips, and the Burst shows both faces for two turns. No
counter is added; the face is the only state.

**Ordinary turn.** Salon in Ousia, hand Salon Solitaire (Arkhe), Curtain
(Ousia 9 / Pneuma heal 3 Block 4), Strike, Defend; enemy intends 14. Stay
in Ousia and take the hit for the trio's end-of-turn blow, or flip to
Pneuma so Curtain reads as Block and the Singer's Encore heals double, and
give up the damage turn. The hand is two hands; the flip picks which.

**Payoff.** Alternating fills the Burst; two turns of both faces is the
fight's climax, earned by having flipped rather than camped.

**Defence without setup.** Pneuma is one card away, and every card's
Pneuma half is protection, so a hand with no summon still Blocks and
heals at ordinary rates.

**Companions.** Their cards are face-neutral and are the reaction partners;
a few read her face ("if Furina is in Pneuma, this also heals 3"), which
is the support-buff loop [USER] wants to keep: managing the Salon's face
is what the party's cards respond to.

**Not Defect because** there is one object, not three, and it does not
grow; and not the Watcher because the stance is the summon's and the
cards' halves, not a damage multiplier on her, and the Watcher is not in
StS2's roster.

**Cost.** Reopens "Pneuma/Ousia is pure flavor, zero mechanics" (kickoff
§3, ratified 2026-07-20) with this packet as the new fact. The Salon needs
a two-face portrait, one image that flips, which is smaller than the
three-portrait panel.

## 5. Concept C: the Flood (duality by coordination)

**Rule.** Her cards put **Hydro** on enemies and it **stacks**; the stack
is the one number, shown on the enemy. A Companion's reaction off it
consumes the stack and is amplified by it (Vaporize on 3 Hydro hits for
+3). Her own cash-out is **Surge**: deal damage equal to the stack to that
enemy. Her support is the rule "when an ally's card reacts off your Hydro,
that ally heals 2 and Furina Blocks 2": the water heals those who play with
it.

**Ordinary turn.** Two enemies, one at Hydro 3 and one dry; hand Tidal
Strike (4 and Hydro +1), Surge, Chevreuse's Interdiction Fire (Pyro 7),
Defend. Vaporize the wet one now for 10 and the heal, or spread Hydro to
the dry one and Surge next turn. Where the water goes is the decision.

**Payoff.** A boss soaked over two turns takes a companion's amplified
reaction and the party heals on it; the payoff is targeting done earlier.

**Defence without setup.** Her Skills Block as ordinary cards; with no
Companion in hand, Surge cashes the stack slowly. Sustain is the weakest of
the three without a Companion.

**Companions.** Everything: they are the converters, and the concept is
built on the reaction system `review/active/reaction-brief-2026-09-06.md`
is already specifying. It is the concept the three-slot stage was
structurally, with the number moved from her to the enemy.

**Not Defect because** the number lives on the enemy and is spent by
targeting, not grown by waiting.

**Cost.** Companion-poor runs are dim (kickoff Pillar 4 says dim, never
bricked; Surge is the floor). Sustain depends on reactions happening.

## 6. Side by side, and the pick

| | A Tide | B Arkhe | C Flood |
|---|---|---|---|
| New counters | 1 (Fanfare) | 0 (a face) | 1, on the enemy |
| Sustain without setup | heals and Burst | Pneuma half of every card | Block only |
| Keeps a Salon to manage | as cards, not a summon | yes, one object | no |
| Duality is felt as | how low to run | which face for this enemy turn | where the water goes |
| Prior ruling reopened | Rare-only healing | flavor-only Arkhe | none |
| Panel reads with | HP bar + one number | one portrait that flips | a number on each enemy |

My recommendation is **B**. It keeps the Salon as the thing [USER] manages
to support the party, it adds no counter at all, its sustain is one card
away on any hand, the Encore word survives as a moment instead of a meter,
and nothing in StS2's roster plays that way. A is the truest to the source
character and the strongest conversion loop, and it is the one to take if
"how low do I run" is the feeling you want more than "which face". C is
what we built, made honest; it is third because its sustain is
conditional on Companions.

Whichever is picked gets a one-page brief revision, then a `+proto` build
and a seat round with the two questions "did the choice show up on an
ordinary turn" and "did the payoff feel earned". PR #433's stage-direction
pick is not asked; this packet replaces it, and its branch closes when
this one is ruled.

1. **Which concept goes to the brief.** Taken by [USER] the same night:
   **A, the Tide, as the working theory** (GPT's read concurred: B's faces
   split offense from defence, and its healing summon reopens the same law
   as A; C is the least hers). The deeper sketch is
   `review/active/furina-tide-sketch-2026-09-07.md`, and its picks are
   where this line continues. B is held as the challenger.
2. **PR #433.** Default: closed unmerged, its packet superseded by this
   one. 2: merged as a record of the stage analysis with its pick marked
   withdrawn.
3. **The current build.** Default (E, applied): stays deployed as the
   reference until the chosen concept's first `+proto` build replaces it;
   no further Salon panel passes.

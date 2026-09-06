Status: OPEN (no pick; the layer's brief, read against the kit checklist; GPT audit owed)

# The elemental reactions — the layer's brief

Written 2026-09-06 under R263 pick 2, item 1 of the sweep
(`review/ruled/elements-reaction-sweep-2026-09-05.md` §4). The reaction
layer is the one system every character borrows and the only one that never
had the document each character has. This is that document, in the shape
the kit checklist (`docs/current/kit-checklist.md`) reads a brief against.
Two pages, no pick. It describes the layer as shipped; the reading
(`review/records/reaction-sequences-2026-09-06.md`) says where the shipped
layer fails its own brief, and a change waits on that.

## 1. The promise

Your character paints in one colour. The companions you draft answer in
theirs, and the answer is bigger when you chose the order. A reaction is
never something the game gives you: it is the second half of a sentence
you started with your own hit, and the deck you build decides which
sentences you can finish.

In play: every hit of yours leaves your element on the enemy. A companion
card, a relic or a potion supplies a second element, and the pair does one
of eight things. The two amplifiers reward ordering; Frozen and Swirl reward
targeting; the rest pay out a number. Off-element access is scarce by law,
so the draft is where the layer's decisions are made, and the fight is where
they are collected.

## 2. The rules, in seven sentences

1. Pyro, Hydro, Electro and Cryo leave an **aura** on the enemy they hit;
   Anemo and Geo leave none and only trigger (`LAW.md` §Combat).
2. One aura per enemy, for two of your turns, refreshed by a same-element
   hit (`AURA_DURATION_TURNS`, `tier0/constants.py`).
3. A different element consumes the aura and fires the pair's reaction on
   that hit (`tier0/engine/reactions.py`, `resolve_hit`).
4. **Vaporize** (Pyro, Hydro) makes that hit ×1.5 and **Melt** (Pyro, Cryo)
   makes it ×1.75; the multiplier lives and dies with the one hit, and no
   reaction ever makes a persistent or compounding multiplier: the iron
   rule (`LAW.md` §Combat).
5. **Overload** (Pyro, Electro) deals 6 to every enemy through Block and
   Weakens the target; **Superconduct** (Electro, Cryo) applies Vulnerable
   2; **Electro-Charged** (Hydro, Electro) puts a Poison-shaped stack of 4
   on the target that ticks through Block and decays by one a turn (4, 3,
   2, 1) and stacks on a repeat (`tier0/engine/powers.py`, the `dot` power;
   the mod applies the base game's PoisonPower); **Crystallize** (Geo on
   any aura) gives you 4 Block.
6. **Frozen** (Hydro, Cryo) halves the enemy's next action and lets the
   first Attack hit Shatter it for 6; in a boss room a non-Minion takes
   Vulnerable 2 instead. **Swirl** (Anemo on any aura) copies that aura to
   every enemy.
7. No character card applies an off-element aura; companions, relics,
   potions and a co-op partner are the only second colour (`LAW.md`
   §Combat, "reactions are earned, not given").

## 3. What each reaction asks

| reaction | the question | whose deck it belongs to |
|---|---|---|
| Vaporize, Melt | which of two hits carries the multiplier, since the first consumes the aura | any deck with one large hit and one applier: Klee's Cook, a Bomb into Cryo |
| Frozen | which enemy to freeze, and whether to Shatter it now or let it whiff | a deck that takes hits: the Hydro characters with a Cryo companion |
| Swirl | which aura to copy and on what turn, since it copies what is standing | a Hydro or Pyro character against three enemies |
| Overload | none at the table; in the draft, whether a Pyro-into-Electro pair is worth a slot for the 6 to all | Klee against packs |
| Superconduct | none at the table; in the draft, the same | any deck, but see §4 |
| Electro-Charged | when to stack it, since a second application adds to the count | the Hydro characters with an Electro companion |
| Crystallize | none; 4 Block arrives | a Geo companion's only sentence |

Four of eight ask nothing once the cards are drafted. That is not a defect
by itself: the checklist's check 6 says a plain card is legal, and a plain
reaction is too. It is a defect where the plain reaction is the only one a
companion can make, because then the companion asks nothing either.

## 4. Reach: what one same-nation companion buys

The nation sheets, by row (`docs/mondstadt-companions.yaml` 17,
`docs/inazuma-companions.yaml` 15, `docs/fontaine-companions.yaml` 19):

| character | own element | same-nation elements | one-companion reactions | two-companion only |
|---|---|---|---|---|
| Klee (Pyro) | Pyro | Hydro 4, Pyro 4, Anemo 4, Electro 2, Cryo 2, Geo 1 | Vaporize, Melt, Overload, Swirl, Crystallize | Superconduct, Electro-Charged, Frozen |
| Kokomi (Hydro) | Hydro | Electro 6, Geo 4, Anemo 3, Pyro 2; the prototype pool the seats play (`docs/prototype-surface.yaml`, `proto_mi_*`) adds Ayaka (Cryo) and Ayato (Hydro), both 5-star behind the Featured Banner | Electro-Charged, Crystallize, Swirl, Vaporize; Frozen through Ayaka when the banner shows her | Melt, Overload, Superconduct |
| Furina (Hydro) | Hydro | Cryo 6, Hydro 4, Pyro 4, Anemo 3, Geo 1, Electro 1 | Frozen, Vaporize, Swirl, Crystallize, Electro-Charged (one row) | Melt, Overload, Superconduct |

Three facts fall out of the table and are the brief's own findings:

- **Superconduct is a two-companion reaction for every character.** Electro
  and Cryo are nobody's element, so it is never the second half of a
  sentence a character started. That is why the old packet found it "found
  by HP arithmetic": nobody planned it, because nobody could with one draft.
- **Kokomi's home Cryo is one 5-star row behind the banner** (Ayaka, in
  the prototype pool; the shipped sheet has none), so Frozen, the reaction
  whose targeting question suits a Plan-writing character best, is
  off-nation for her on most runs (Inazuma 4-stars: Electro 6, Geo 4,
  Anemo 3, Pyro 2).
- **Klee reaches both amplifiers at home** (Hydro 4, Cryo 2), which is the
  layer working as designed: the ordering question the seats called the
  puzzle four rounds running is the one her nation sells.

## 5. What fight one teaches

- **Klee.** Every hit is Pyro, so the first fight teaches the aura: a
  Bomb goes off into her own Pyro and nothing happens, which is the
  lesson that the second colour has to come from somewhere else. The first
  Kaeya or Barbara in a reward is the layer's real fight one.
- **Kokomi.** Her hits are Hydro and her carry-outs land a turn later, so
  fight one teaches that an aura she painted today is there for a
  companion tomorrow; an Electro Universal from Inazuma turns that into
  Electro-Charged, a number, and the layer's first real question for her
  waits on Cryo.
- **Furina.** The Salon performs every turn and all three members are
  Hydro (`SALON_MEMBERS`, `tier0/constants.py`; a member's element counts
  as on screen, `EB-547`), so the stage is the Hydro half of every
  reaction and the card in hand is the other; fight one with a member
  teaches that the performance paints and the card answers, or the
  reverse.

None of the three starters carries an off-element card, by law, so the
layer's tutorial is the first companion reward, and the reward screen is
where the preview (`EB-428`'s reward half) has to do the teaching.

## 6. Failure modes

1. **A number that arrives.** A reaction the seat learns from the HP
   arithmetic, not from a choice: Superconduct's order (`EB-472`), a Mine
   into Cryo at 12 where 7 printed (`EB-450`). The cure is never a bigger
   number; it is a question the reaction asks, or a name on the page.
2. **A glossary nobody can act on.** The nine-line keyword block for a
   mono-Pyro deck (`EB-428`, BUILT: rows print only where the screen can
   supply both elements). The remaining half is `EB-410`: a fired reaction
   is never named on the page, from any source.
3. **A second colour with no sentence.** A companion whose only reaction
   is Crystallize, or whose element the character cannot pair with anything
   at home (Kokomi and Cryo, one banner-gated row). The draft cannot fix
   what the nation sheet does not sell.
4. **A setup nobody can afford.** A two-companion reaction is two drafts
   for one payoff; where the reading shows it never planned, the answer is
   access (a character or a member of that element), not a rule change.

## 7. The checklist, read against the layer

1. Brief before pool: this is it, sixteen rounds late. 2. Leverage: the
amplifiers and Frozen are steerable by ordering and targeting from the first
companion; Overload, Superconduct, Electro-Charged and Crystallize are not
steerable at the table, only in the draft. 3. Binding prices: the aura slot
is the price, one per enemy, and an amplifier spends it. 4. Visible and live:
half paid (`EB-428` built, `EB-410` open). 5. Simple surfaces: eight
reactions, seven sentences, and the depth is in ordering across cards from
two sources; the faces carry one word. 6. Every reaction has a place: the
four plain ones are draft-time cards' places, not table decisions. 7. Mesh
without preassembly: the nation sheets are the mesh, and §4 shows where it
is thin. 8. Distinct patterns: amplify, target, spread, pay out, four
patterns over eight rows. 9. Shared layer: every companion package connects
to the character's element through this table, which is the layer's whole
job.

The checklist finds two "no"s, on checks 2 and 4, both already carried:
the plain reactions (a hypothesis each in the old packet's §4, gated on the
reading) and the display half (`EB-410`). What the sweep must not touch
stands as ruled: the amplifiers, the aura duration, the one-aura rule and
both laws.

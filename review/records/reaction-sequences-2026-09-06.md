Status: RECORD

# The reaction reading: what the seats actually did with the table, and which companions they chose

A READING, not a count. Written 2026-09-06 under R263 pick 2 (ii): "review
concrete sequences and companion choices" before any rule moves. It corrects
the baseline the census set (`review/records/reaction-census-2026-09-05.md`),
whose largest bucket was "unmarked" because a regex over a sentence cannot
say whether a seat planned a reaction or found it. Here every claim is a
fight event or a reward-screen choice read in context, with the seat's own
words, over the same record set: every `*.md` directly inside
`review/qa/klee-round-*`, `review/qa/kokomi-round-*` and
`review/qa/furina-reframe-round-*` (the control Ironclad runs have no
elements and are not read).

**Method, and how far to trust it.** Three Sonnet extraction passes, one
per kit, read every record for (A) every reaction the record says fired in
a fight, with its aura source, its trigger source, and whether the seat
CHOSE the order before playing or FOUND the reaction afterwards in the HP
arithmetic, and (B) every companion card offered, taken, passed or bought,
with the seat's stated reason. Those tables are working files and are not
committed, because a spot check found one row attributed to a round whose
transcripts never mention the reaction (a Furina round-2 "Superconduct" that
is really round 7's). So **every sentence quoted below was searched for in
the transcript by hand and is cited by its path**; a claim about frequency
("most", "never") is mine, made over the tables and the census together,
and is worded as a reading rather than a number. The one number this record
leans on is the census's per-kit mention count, which is reproducible.

## 1. What the count got wrong

The old packet's §2 said the four transformative reactions "were never
named as a decision in any record." That was the census's artifact, and it
is false. Read in context:

- **Superconduct is chosen, and chosen against Melt.** "Against one
  high-block target I picked Superconduct over Melt: Kaeya first (8 damage,
  leaves Cryo), then Shinobu (Electro on Cryo → 2 Vulnerable applied before
  the hit, so 8 became 12)"; "against one big blocker I picked Superconduct
  because the Vulnerable persists; against three rats I picked Overloaded
  because the 6 spills" (`review/qa/klee-round-17-2026-09-05/opus-arm-act1.md`).
  A Furina seat front-loaded it: "deliberately front-loading Superconduct so
  the next turn's big cards would land into Vulnerable"
  (`review/qa/furina-reframe-round-7-2026-09-04/opus-act1.md`). A Klee seat
  read the two previews as one choice: "picking Melt over Superconduct is
  picking which enemy dies first, not which number is bigger"
  (`review/qa/klee-round-15-2026-09-04/opus-run2-act1.md`).
- **Overload is the most planned reaction after the amplifiers.** Klee:
  "Ka-pow!-before-Razor to spend a Pyro aura on an Overloaded", and the
  Weak is the point: "I played it anyway for the Overloaded Weak, which cut
  the incoming 14 to 10" (`review/qa/klee-round-19-2026-09-05/opus-natural-act1.md`);
  "32 damage from a 1-cost card" off a Mine into Electro
  (`klee-round-15-2026-09-04/opus-run2-act1.md`). Kokomi: "Kujou Sara
  first, deliberately: Electro onto a bare body, then Thoma's Pyro fires
  Overloaded", called "the best decision the kit gave me all act, and it came
  from card order alone" (`kokomi-round-9-2026-09-04/opus-act1.md`). Furina:
  "Swirl the Electro onto both bodies so one Pyro card Overloads twice — is
  a play I constructed from printed text before I saw it work"
  (`furina-reframe-round-7-2026-09-04/opus-act1.md`).
- **Crystallize is chosen too, as the thing to sequence AROUND.** "Gorou
  first (banking the Crystallize Block), then Slack Water to re-apply Hydro,
  so Shinobu's end-of-turn Electro still had an aura to react with"
  (`kokomi-round-5-2026-09-03/opus-run3-act1.md`); "Gorou (Geo) must come
  after the Electro hit or its Crystallize eats the aura the reaction
  needs", under the heading "element ordering is the deepest decision this
  deck has, and it is entirely undocumented"
  (`kokomi-round-5-2026-09-03/opus-run3-act2.md`).
- **Electro-Charged is chosen for the kill timing** ("Poison 5 would kill
  it at the start of its turn",
  `furina-reframe-round-2-2026-09-04/opus-run2-act2.md`) and is the one
  reaction the seats meet under the wrong name, since the page prints the
  base game's Poison (`EB-410`).

So the corrected baseline is: **the plain reactions do ask a question, and
the question is which reaction to make from the aura that is standing.**
Once a deck holds two off-elements, Superconduct versus Melt on a Cryo aura
and Overload versus Vaporize on a Pyro aura are real picks with different
answers by board. What the four plain reactions lack is a decision *inside*
the reaction (no ordering, no targeting) once it is chosen, which is the
checklist's check 2 read narrowly, and is not the defect the old packet
described.

## 2. Per reaction: what the seats did

- **Melt and Vaporize.** Chosen almost every time they fired, in every kit.
  The decision is the one the old packet named: which hit carries it. Klee's
  version is the Set off rule, "the first takes the aura, so the oldest Bomb
  Vaporizes" (`klee-round-20-2026-09-05/opus-natural-act1.md`); Furina's is
  member-first or card-first ("Charlotte-then-Chevreuse is Melt; Chevreuse-
  then-Charlotte is nothing", `furina-reframe-round-3-2026-09-04/opus-act2.md`).
  One quirk recurs and has no row: an applier with no damage fires a null
  amplifier and strips the aura. "The Hydro was consumed to Vaporize a hit
  that carried no damage, left bare for nothing"
  (`klee-round-8-2026-09-03/opus-run2-act2.md`); a later seat used it on
  purpose, "the first application Vaporizes the Pyro away and leaves the
  body bare" (`klee-round-10-2026-09-04/opus-run2-act2.md`). It is the
  one-aura rule working, and the preview goes silent exactly there. See §5.
- **Frozen.** Chosen, as targeting and as mitigation: "freezing the attacker
  halved 11 to 5, strictly better mitigation than buying Block"
  (`furina-reframe-round-9-2026-09-04/opus-act1.md`); the Shatter cash-out
  read as a trade in four Furina records. A Cryo Universal at random target
  loses it: "it took the 2-HP Twig Slime instead of the Cryo-soaked B, so I
  lost the Frozen" (`furina-reframe-round-15-2026-09-06/opus-arm-act1.md`).
- **Swirl.** Chosen when it fired, always to set up the next card: the
  Overload-twice line above, "spending a turn to move the aura onto the 26
  HP target is the best turn of the run"
  (`furina-reframe-round-3-2026-09-04/opus-act1.md`). In Klee's decks it is
  passed at the draft: "copying Pyro onto everything looked close to a
  no-op" (`klee-round-7b-2026-09-02/opus-act1.md`); "Swirl would have opened
  Elemental Reactions, but my only reaction payoff was a minor rider"
  (`klee-round-20-2026-09-05/opus-arm-act1.md`). Swirl is a Hydro
  character's reaction: it copies an aura someone else will react with, and
  Klee has nobody else.
- **Overload, Superconduct, Electro-Charged.** §1. One more fact about
  Overload: the two records where it did not fire are defects, not design
  (`EB-387` for Chevreuse; Raiden Shogun, "the screen said the reaction was
  there, the outcome says it was not",
  `klee-round-18-2026-09-05/opus-spray-act1.md`).
- **Crystallize.** The 4 Block is never the reason a Geo card is played or
  taken; the aura it eats is the reason it is sequenced first or last. When
  it fires unplanned it is invisible: "a Crystallize is the only
  explanation, and no line on any screen said so"
  (`furina-reframe-round-14-2026-09-05/opus-arm-act1.md`).

## 3. Per kit: the sequences that recur

**Klee.** A Cryo companion into her own Pyro is the kit's reaction: Diona,
Rosaria, Kaeya or Charlotte, then a Set off, in most Klee records with a
reaction at all. The seat plans it from the reward screen ("Rosaria leaves
the Cryo aura that makes the next Pyro detonation worth 1.75×",
`klee-round-15-2026-09-04/opus-run2-act1.md`; "Cryo is the only route I had
been offered to a Melt on my own Pyro bombs",
`klee-round-8-2026-09-03/opus-act1.md`). Barbara into a Set off is the second
sequence. Overload arrives with the arm's Electro rows (Razor, Shinobu, Oz)
and is planned from the tip: "One Electro card turns my permanent
self-applied Pyro aura into a guaranteed Overloaded"
(`klee-round-10-2026-09-04/opus-run3-act1.md`). A Klee deck with no
companion fires nothing, and the seats say why in the same words across
rounds: "a Pyro hit on a Pyro aura only refreshes it"
(`klee-round-9-2026-09-04/opus-act1.md`, `klee-round-10-2026-09-04/opus-act2.md`).

**Furina.** The Salon makes the sequence two-sided: a member performs Hydro
every turn, so the card in hand supplies the trigger (Chevreuse's Pyro for
Vaporize, Freminet's or Charlotte's Cryo for Frozen), or the card lays the
aura and the performance triggers it. Both orders are chosen and named
("deploying the Hydro member first is what makes Charlotte's Cryo a
reaction", `furina-reframe-round-3-2026-09-04/opus-act1.md`). Two
off-elements in one deck is ordinary for her (Fontaine sells Cryo 6 and Pyro
4), which is why Superconduct, Overload and Electro-Charged are all planned
in her records and in nobody else's at that rate. The recurring
disagreement is the face: "printed 10 and delivered 15" is `EB-511` and
`EB-589`, both built; the printed number now folds the amplifier in the
preview, not the face.

**Kokomi.** Her reaction is Electro-Charged, because Inazuma sells Electro
six ways and nothing else that reacts with Hydro except Pyro twice. The
sequence the seats learn is Electro first, Hydro second: "Slack Water first
is what set up the reaction; that ordering had been learned in fight 2"
(`kokomi-round-20-2026-09-05/opus-natural-b-act1.md`); "Lisa into a board my
own AoE had just painted Hydro is the kit's best single button"
(`kokomi-round-13-2026-09-04/opus-act1.md`). The Plan adds a shape no other
kit has, a reaction written a turn ahead: "Shinobu leaves an Electro aura,
and next turn's planned Hydro hit should consume it"
(`kokomi-round-14-2026-09-04/opus-act1.md`); "aiming her at the 27 HP body
meant next morning's Plan would react on the target"
(`kokomi-round-18-2026-09-05/opus-arm-act1.md`). Frozen's boss clause is
hunted on purpose wherever a Cryo row was drafted. Two things are found
rather than chosen and both are display: the Casket relic's Hydro ping
fires reactions of its own ("the Casket's proc is not chip damage: it is a
Hydro hit that triggers elemental reactions of its own",
`kokomi-round-4d-2026-09-03/opus-act3.md`; called a "hidden reaction" in
`kokomi-round-14-2026-09-04/opus-act1.md`), which is `EB-410`'s relic-tick
half; and a Geo hit eating her aura, "my Geo hit ate my own Hydro aura for
nothing" (`kokomi-round-17-2026-09-05/opus-natural-act1.md`), the same
Crystallize cost the round-5 seat sequenced around.

The Kokomi fact that matters most is reach. Ten of her thirty-seven records
fire no reaction in the whole run, and the seats say it the same way each
time: "I never saw an Elemental Reaction in six fights"
(`kokomi-round-11-2026-09-04/opus-run2-act1.md`); "finished the act having
observed zero" (`kokomi-round-19-2026-09-05/opus-arm-act1.md`); "never
triggered a single reaction" (`kokomi-round-22-2026-09-06/opus-natural-act1.md`);
and a natural lane's "first chance in the whole run to put a second
element" arriving at the fifth reward
(`kokomi-round-21-2026-09-06/opus-natural-act1.md`). Klee's blank runs are
the same shape with fewer of them.

## 4. Companion choices: what a seat pays for, and whether it is a reaction

- **Klee takes Cryo for Melt and Hydro for Vaporize, by name.** Almost every
  reaction-motivated pick in her records is Diona, Rosaria, Kaeya or
  Barbara, and the quote is the multiplier. Electro is passed early on a
  draft-time reading of the glossary, "Overloaded is the only reaction on
  the glossary with no damage multiplier — the worst element to pair with a
  Pyro deck" (`klee-round-8-2026-09-03/opus-run2-act2.md`), and taken later
  as an instrument ("wanted to see whether that block of text was real",
  `klee-round-10-2026-09-04/opus-run3-act1.md`; "taken deliberately as an
  instrument", `klee-round-9-2026-09-04/opus-act1.md`), after which the same
  seats call it strong. That is a glossary that undersells a reaction at the
  reward screen, a display finding and not a rule finding.
- **Geo is never taken for Crystallize.** Gorou is taken for "unconditional
  8 Block and 10 damage on one card" or passed for rate; Albedo's Solar
  Isotoma is taken for its own text. No record buys a Geo row to make Block.
- **Anemo is passed by Klee and Kokomi and taken by Furina.** Lynette's
  Swirl "looked like it would do three jobs; it did" in a Salon deck
  (`furina-reframe-round-8-2026-09-04/opus-act1.md`); Sucrose and Kazuha are
  passed by Klee for the reason in §2, and Kokomi's seats pass Heizou, Sayu
  and Lynette on one sentence, "worthless with Hydro as my only element and
  no second element" (`kokomi-round-19-2026-09-05/opus-arm-act1.md`). Swirl
  on a mono-element deck copies the deck's own aura, which is a setup for a
  companion the seat does not yet own, and no face says so.
- **Kokomi takes the first off-element row she is shown, whatever it is:**
  "the only card that can make a Reaction happen"
  (`kokomi-round-4c-2026-09-02/opus-act1.md`), "the only card on the sheet
  that reaches a second element" (`kokomi-round-22-2026-09-06/opus-arm-act1.md`),
  "specifically to own a second element" at the shop
  (`kokomi-round-17-2026-09-05/opus-natural-act1.md`). A card the nation
  cannot feed is refused for that reason alone: Freminet's Shatter reader
  "unplayable: Shatter needs a Frozen enemy and nothing in my deck or relics
  makes Cryo" (`kokomi-round-20-2026-09-05/opus-natural-b-act1.md`;
  the missing keyword is `EB-537`, built).
- **Furina buys the second element on purpose and says so:** "a second
  element is what makes the reaction layer live"
  (`furina-reframe-round-16-2026-09-06/opus-arm-act1.md`); "a fourth element
  opens Melt/Vaporize/Overloaded" (`furina-reframe-round-4-2026-09-04/opus-act1.md`).
  Her passes are about the stage, not the element (a Block member at the
  front, Encore, energy).
- **Off-nation companions are common in every kit's records** (Kaeya and
  Diona in Furina decks, Shinobu and Sara in Klee's, Thoma and Chevreuse in
  Kokomi's), so the reward channel's off-nation half is doing its job and
  the reach table in the brief (`review/active/reaction-brief-2026-09-06.md`
  §4) is the floor, not the ceiling.

## 5. Where a specific weakness is demonstrated, and where it is not

Under R263 pick 2 (iii) a change is tested only where this reading shows a
weakness. Read against the old packet's three hypotheses and the loop's
order of intervention (`operations/stage-gate.md`, smallest first):

1. **Crystallize: demonstrated, and the smallest intervention is display.**
   The weakness is that a Geo hit is a cost to a reaction deck (it eats the
   aura for 4 Block) and nothing says so until the arithmetic does. The
   seats already sequence around it; they should be able to see it. First:
   the Geo card's preview names the consumption ("Crystallize: 4 Block,
   consumes the aura") and the fired line is named (`EB-410`). A rule
   change (Crystallize leaves the aura standing, or pays the aura's own
   effect once, the old (a)) is tested only if the seats still avoid it once
   they can see it.
2. **Overload: not demonstrated.** It is planned, its Weak is chosen as
   mitigation, and its flat 6 is what makes it the pack answer against
   three bodies. The old (b) is not taken.
3. **Superconduct: not demonstrated.** It is chosen against Melt on the
   same aura because the Vulnerable persists and Melt does not; that is the
   Cryo-shaped decision the old (c) wanted to add, and it is already there.
   The old (c) is not taken.
4. **The null amplifier: demonstrated, no row, a preview fix.** A zero-damage
   applier on an off-element aura strips it silently. The preview should
   say "consumes the aura, no damage to amplify" where it now goes silent.
   This is a display row to mint at the next sitting, not a rule.
5. **Electro-Charged under the name Poison: demonstrated, already carried**
   (`EB-410`, a bridge build). Nothing to add.
6. **Two-companion reactions are planned when the nation sells both
   elements** (Furina), and reached as an instrument when it does not
   (Klee). This is the fact the boundaries paper's §4 needs
   (`review/active/dendro-boundaries-2026-09-06.md`): Quicken at two drafts
   is Superconduct's access, and Superconduct at two drafts does get
   planned; the price is not prohibitive where the sheets sell the pair.
7. **Reach: demonstrated for Kokomi, and the smallest intervention is
   access, not a rule.** A third of her records never reach the table,
   and the seats take the first off-element row shown. In the loop's order
   this is "access improved" (`operations/stage-gate.md`), which here means
   the reward channel and not the reaction table: the first hypothesis the
   sweep should test when the machine is back is that a run's early
   companion offers include one off-element row, as a flag on the reward
   roll, read on an assembled deck and a natural lane like any other. It
   is disclosed here as the candidate; it is not built, and no constant
   moves until a round reads it. The alternative that is a design direction
   and not a hypothesis, a Cryo row on the Inazuma sheet so Kokomi reaches
   Frozen at home, returns as a pick only if the flag fails.

Nothing here moves a constant, a sheet or a law. The two display items (1
and 4) are the sweep's next rows; both are page and preview text, and the
fired-line half of item 1 is `EB-410`'s bridge build. Item 7 is the first
flagged hypothesis and waits on the game.

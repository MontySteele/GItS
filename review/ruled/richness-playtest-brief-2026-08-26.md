Status: RULED (see RULINGS.md)

# Playtest brief — the three-character richness pass, 2026-08-26

> Read this before you sit down. It is short on purpose. It says what changed,
> what we already know, and the three things only a person at the table can
> tell us.

## Why there is a playtest at all

Over the last two weeks all three characters were reworked with one goal: make
their kits ask you questions instead of resolving themselves. Four internal
reviews and one outside audit have now read the result. They agree on both
halves of the verdict.

Against where the characters were, it worked. Things that used to happen
automatically now happen because you chose them, and the choice has a
consequence later in the fight. Nothing was inflated to get there — ceilings
are flat or lower, bars went up rather than down, and cap riders came off. Five
of the nine deck plans moved down in the simulator, and so did the reference
characters we measure against, which is what "no inflation" looks like.

Against the base game, they are not finished. The pass raised how much the
cards touch each other, strongly: the share of cards that read some contested
piece of the board went from 53% to 73% for Klee, 46% to 66% for Furina, and
56% to 63% for Kokomi. What it barely moved is the number of cards that ask you
to make a choice while you are playing them. Klee has five, the same as before.
Furina has two, the same as before. Kokomi went from 27 to 31. The base game
gets its depth from simple cards sitting in wide shared systems; we get ours
from explicit choices, conditionals and private subsystems. That is a
difference in kind, and it is not something another rework packet fixes by
itself.

So both reviews say the same thing: stop building, and play. Nothing new is
opening. The two deferred card families stay closed. Kokomi's staged power
lever stays staged and unpulled. Nothing gets nerfed or buffed off the
simulator alone. The next move is a session at the table.

## What to play

Play the next deploy after the current integration branch lands. It carries two
fixes you want:

- **Take It From the Top now works.** It was silently paying its Block and
  dropping its damage entirely whenever the Spotlight had moved. That is
  already in the build.
- **Hover tips come back on Furina and Kokomi's rider cards.** The Card Library
  had been dropping a card's whole tip set on any card whose tip asked who
  owned it. Fixed in source, not yet deployed — so deploy before you play.

Five new cards show the BETA placeholder art: Klee's Powder Charge, Hold the
Line and Smoke and Sparks, and Furina's Change the Bill and Take It From the
Top. That is known and expected. Do not report it.

**Order: Klee, then Furina, then Kokomi.** Kokomi goes last for a reason given
in her section below.

## The three questions

One per character. These are the questions the session exists to answer, and
everything else in this document is context for answering them well.

**Klee — did Bomb placement or Spark spending ever change a decision, or did
her large starter faces simply end the fight?**

**Furina — was the Spotlight mode choice ever genuinely ambiguous, and did the
Salon, the Encore bar and the Spotlight feel like one machine rather than three
separate dashboards?**

**Kokomi — when you chose a card to discard or to Exhaust, were there usually
two plausible choices with different consequences, or was one card obviously
the disposable one?**

## Klee — what is already known

Say what is new. These are not discoveries:

- **Smoke and Sparks is a tax and will read as one.** Surprise Visit is the
  same rarity, the same cost, and does the same thing: Vulnerable 2, free.
  Smoke and Sparks gives Vulnerable 3 and charges you 2 Sparks for the extra
  point. Expect to notice this. Judge the other two Spark sinks — Powder Charge
  and Hold the Line — on their own merits, not through it.
- **Hold the Line's conditional half is effectively always on.** The
  "if the enemy intends to attack" branch fires on roughly seven plays in ten.
  It reads like a choice and is mostly not one.
- **Holding Sparks is not really available.** At 3 Sparks your next Attack goes
  free and the bank pays for it automatically — no prompt, no confirmation. The
  sinks cost 2. So the live band is a bank of 3 or 4, and "hold or spend" is in
  practice a question about the order you play cards in *this* turn. Watch
  whether that ordering ever felt like a real decision.
- **Her reaction plan was not touched by this pass.** She writes no aura
  herself, so nothing in the rework reaches it.
- **Her starter is unchanged.** Four copies of Kaboom! at 7 damage, four Duck
  and Cover at Block 5, Jumpy Dumpty for 2 (two hits of 8, plus a Bomb worth 6),
  and Pop! for free (a Bomb worth 5). One attack slot and one support slot are
  swapped for a random companion at run start.

If she feels trivially strong in act 1 — and the simulator says she clears act 1
about 82% of the time, which is above both reference characters — the number to
look at is Jumpy Dumpty and the size of the basic cards, not the Bomb and Spark
machinery. Say so if that is what you see.

## Furina — what is already known

- **Change the Bill has nothing to read it.** The card rotates who performs and
  who bows next in the Salon. No card anywhere on her sheet cares which member
  is at the front. So "why would I play this" is the correct reaction, and it is
  a hole we already know about, not a finding. What is worth reporting is
  whether rotation felt like it *should* matter.
- **Encore now has a bar but almost nothing to spend it on.** The House Rises
  pays extra Block once your Encore is at 5 or more. The family of cards that
  actually spends Encore was deliberately held back. Note whether the Encore
  meter felt stranded — filling with no door out.
- **The Spotlight selector may just be a chore.** [USER]'s own read is that the
  Ethereal Spotlight relic's selector card is one more thing to remember to
  play at the start of every turn, and might be annoying rather than
  interesting. So: was the mode choice ever actually contested, or did it
  collapse to a rule — "Guest Cast if I'm holding a Companion, otherwise Center
  Stage"? If it collapsed to a rule, say which rule.
- **There is an upgraded version of that relic that deletes the choice
  entirely.** If the run offers you the Ancient boon that improves your starter
  relic, take it and report what happened. Both modes turn on at once, every
  "moved the Spotlight this turn" condition is permanently satisfied, and the
  selector card stops arriving. Whether that is a relief or a loss is exactly
  the sort of thing only the table knows.
- **The Salon is her default plan, but the starter barely teaches it.** Only one
  starter card is a Salon card and it picks its member at random. The relic
  teaches the Spotlight instead. Watch whether the plan you ended up drafting
  was the plan the opening deck pointed you at.

## Kokomi — what is already known, and the scripted opening

**Play her last, and start her with a script.** Her whole Exhaust-and-Charge
identity can only be reached once per fight from the opening deck: exactly one
card in the twelve she starts with Exhausts at all (Gorou). A cold start would
grade a character you never actually met.

So for this run, do two things:

1. Weight the early card picks toward the priest plan.
2. Force one copy of **Pearl Barrage** or **Tide of Names** into your hand
   directly, using the attended harness:

   ```
   python -m understudy.harness give-card KLEEMOD-PEARL_BARRAGE --pile hand --upgraded --why "richness brief: reach the Exhaust choice in act 1"
   python -m understudy.harness give-card KLEEMOD-THE_TIDE_REMEMBERS --pile hand --upgraded --why "richness brief: reach the Exhaust choice in act 1"
   ```

   (Tide of Names still carries its old internal name, which is why the second
   command does not say what the card says.) The grant must be on the attended
   harness, never the unattended one, and it must carry the reason. Granting a
   card makes the run non-comparable to any other run, which is fine — this is
   an exploratory session and grades nothing.

Then, the things not to re-report:

- **She has clone families and we know it.** Seven cards are a flat lump of
  Block with a rider (Coral Guard, Drifting Lantern, Hold the Narrows, Pearl
  Bulwark, Quiet Harbor, Salt Line, Tidal Lure). Three are discard-and-draw.
  Three are block-and-discard. Five are the conscript core. Do not report clone
  fatigue. Report whether the *new* decisions were felt.
- **The Exhaust choice usually collapses to a coin flip.** Pearl Barrage pays
  you more for Exhausting an expensive card, but almost every cost-2 card she
  has is a Rare — so in practice the choice is between a 0 and a 1, and the
  difference is one point.
- **Sango Isshin lost its scaling on purpose.** It used to grow with the
  Exhaust pile; it now deals a flat 14 and pays extra Block once the pile
  reaches 8. That was a ruled change and it is the one edit in the pass that
  reduced interaction. Report whether you ever hit that bar deliberately, or
  only by accident.
- **Charge has no door.** Salvage the Line pulls a card back out of the Exhaust
  pile, which feeds the Charge bank faster. The bank is uncapped and is never
  spent. Note whether Charge ever felt like a resource you were managing, or
  just a number going up.

## What the simulator can and cannot tell you

The standing numbers are diagnostic only, and that is a formal status, not a
hedge. The bot cannot value spending a Spark against holding one, cannot read
either of Furina's new Salon verbs, cannot see the "moved the Spotlight this
turn" bar, and cannot price Tide of Names' payout. Three repairs to fix all of
that are in progress and will land together. Until they do, those cards
contribute a floor to every number below and a null result on them is not
evidence of a null card.

For context, the current table reads: Klee's demolition plan wins 5.1% of runs
and clears act 1 82.4% of the time; Furina's salon plan 2.5% and 50.5%;
Kokomi's priest plan 0.9% and 45.0%. The real Ironclad floors at 5.2% and
65.5%; the real Silent at 1.2% and 54.1%. **Kokomi's 0.9% sits inside the
spread between our own two reference characters, so it is not evidence that she
is weak.** Whether she is generally underpowered is precisely what the table
decides, and a staged power lever is waiting on that answer.

One number did move enough to be real: Kokomi's priest plan now clears act 1
45.0% of the time, up from 39.9%. That is the only separation anywhere in the
table. Full table: `review/records/sitting-reads-2026-08-25-c19-d17-p10.md`.

## Before the session

If the scenario harness has merged by then, four bot checks run first, so the
table is not spent on things a machine can verify: Take It From the Top pays
its damage, Powder Charge applies its detonation bonus, Tide of Names splashes
across two or more enemies, and a Spark sink is correctly refused when the bank
is short. Whether the frames *look* right stays a human item — a screenshot is
material for a person, never a verdict on its own.

## After the session

Everything this session turns up goes into one decision slate — `M45` in
`docs/current/QUEUE.md` — which stays closed until [USER] rules it. Nothing
gets designed, repriced or cut before that.

## Related

Kokomi has a separate, older protocol with seven questions of its own:
`docs/current/playtest/kokomi-playtest-protocol.md`. It is not superseded by
this brief and is not duplicated here. That run is a different event: it is
confirmatory, it fills in an answers table, and it is still blocked on a band
declaration. This session is exploratory and grades nothing. If you want to
answer its questions too while you are in there, they are good questions — but
answering them here does not consume it.

# Blind seat — KLEEMOD-FURINA, lane 2, act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat, lane 2 (port 15528).
- **Run seed:** `Y89TQ208H8KY` (read back off the wire). Stamp `20260904-131025`.
- **Character:** Furina. **Ascension the run opened at:** 2. Opening HP as first
  printed in combat: **62/78** — I never saw a screen that explained the missing
  16; the first battle screen simply opened at 62/78.
- **Act / boss:** Act 1. The map named the act boss **Soul Fysh**. I did not
  reach it.
- **Actions accepted:** **120** (the cap). Two commands were refused; neither
  counted, and they never ran consecutively.
- **Termination reason:** the action budget, at a rest site on floor 10 of 16,
  immediately after confirming a Smith upgrade. About six floors short of the
  boss. Wall clock was not close to 5400 s.
- **HP trajectory:** 62 (opening) → 62 after fight 1 → 50 after fight 2 → 45
  after fight 3 → rest → 68 → 61 after fight 4 → 57 after the elite. **Ended
  57/78.**
- **Gold:** 187 at the stop (99 start + 16 + 19 + 17 + 56 chest + 15 + 43, less
  78 spent in the shop).
- **Potions held:** 1 of 3 slots — **Speed Potion** (Gain 5 Dexterity; lose 5 at
  end of turn). Never used.
- **Relics at the end:** Ethereal Spotlight (starter), Booming Conch,
  **Vambrace**, Centennial Puzzle.
  *Vambrace is in that list because a reward screen printed the bare word
  "Vambrace" with no rules text under it, and I took it. I still do not know
  what it does; no screen since has printed its text.*
- **Deck at the end** (read off the Smith screen, plus the two cards taken
  after it):
  Freminet — Pers, Deploy!; Soloist's Solicitation ×2; Charlotte —
  First-Person Shutter; Stage Presence ×2; Regal Bearing; Aria of Recompense
  (reframe); **Salon Début+** (upgraded: "Deploy Mademoiselle Crabaletta. Gain 2
  Encore."); An Invitation; Duet; Standing Ovation; Curtain Cue; High Tide;
  Deep Breath.

**Neow pick: Booming Conch** ("At the start of Elite combats, draw 2 additional
cards and gain [Energy]"). I took it over Pomander because I had not yet seen a
single card of the kit and could not tell which one deserved an upgrade, and
over Cursed Pearl because 333 gold with a curse is a bet on shops I had no map
for. It paid: the one elite I fought opened at 4 energy and 8 cards.

---

## Fight 1 — Corpse Slug (1) 25/25, Corpse Slug (2) 26/26

Slug 1 intended Attack 8; slug 2 intended a Debuff. Both carried *Ravenous 4 —
"When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and
gaining 4 Strength."*

Opening hand: Ethereal Spotlight (0, **"CANNOT BE PLAYED: you have no Encore,
and this costs 2"**), Stage Presence ×2, Freminet — Pers, Deploy! (1, 6 dmg,
Cryo), Salon Début (1, Deploy Crabaletta), Soloist's Solicitation (1, 6 dmg).

**Turn 1.** Played Salon Début → Freminet on slug 2 → Soloist on slug 2.

- The first thing I tried was `play "Salon Début" on "Corpse Slug (1)"` and it
  was **refused**: *"'Salon Début' is played on you, not on an enemy."* That is
  a finding, not a tool complaint: the card's own reminder text says the member
  "Performs for 6 Hydro damage", and a card that deals damage but takes no
  target is not something the face warns you about. The Salon picked slug 2 on
  its own. I never got to choose a member's target all round.
- The deploy log read: *"**Crabaletta** hit Corpse Slug (2) for 4 Hydro, and it
  is wearing a Hydro aura (**dry**: it could not pay its Encore, so it acted at
  three-quarters)."* 6 → 4. That is where I learned that the whole Salon runs at
  75% until some card I had not yet seen gives me Encore.
- Freminet's face then grew a line it had not had a moment earlier: *"Reaction
  preview: Frozen — Hydro meets Cryo."* That preview is the single best piece of
  text in the kit; it turned a keyword wall into a plan.
- **The alternative I rejected:** double Stage Presence for 12 Block, which
  fully eats the 8 incoming. I rejected it because it leaves both slugs at full
  and teaches me nothing, and because the Frozen preview offered a line where
  the shatter carries the kill.
- Outcome: slug 2 died. What I did **not** predict is that Freminet is itself a
  Companion card, so playing it *also* performed Crabaletta a second time — 26
  HP fell to 4 Hydro + 6 Cryo (Frozen) + 4 Hydro + (6 + 6 shatter). Ravenous
  fired: the survivor became **Stunned** and took **Strength 4**.

**Turn 2** (0 damage taken; the survivor was Stunned). Drew **Aria of
Recompense (reframe)** — *"Gain 5 Encore. If you have at least 6 Fanfare, gain 5
more."* This is the only Encore faucet I had all act, and the fact that it lives
in the draw pile rather than the opening hand governed every fight below.

Played: An Invitation (0) → Aria (1) → Ethereal Spotlight (0, −2 Encore) →
Gorou — Inuzaka All-Round Defense (0, the Companion An Invitation handed me) →
Charlotte — First-Person Shutter (1) → Soloist (1). Slug dead at the end of it.

- **The alternative I rejected:** Regal Bearing / Stage Presence to eat the 12.
  Rejected because Aria first meant Crabaletta stopped acting dry, and Ethereal
  Spotlight at 0 energy for 2 Encore is the cheapest multiplier on the board.
- **Where screen and outcome disagreed.** Ethereal Spotlight says *"Spotlight
  every Companion card. Their printed damage and Block are 50% stronger."*
  Gorou's face went 6 → 9 and Charlotte's Block went 4 → 6, so the *cards* were
  buffed. But the Salon log for the same beat read *"**Crabaletta** hit Corpse
  Slug for **6** Hydro"* — the member kept its printed 6. The player-facing
  status buff meanwhile reads *"Guest Cast 1 — Companion cards are Spotlighted:
  50% stronger printed damage and Block, **no Fanfare**"*, and Fanfare went 3 →
  5 on that very beat. I could not reconcile "no Fanfare" with the meter going
  up by 2.

**Reward:** 16 Gold, and I took **Duet** over Undercurrent / Compose Herself /
Lynette, because a card that repeats a Companion play looked like the lever on
the Salon engine.

---

## Fight 2 — Toadpole (1) 24/24, Toadpole (2) 22/22

**Turn 1.** An Invitation (0) → Standing Ovation (1, the power I had just bought)
→ Gorou — General's War Banner (1) → Soloist on Toadpole 2 (1). Took 7.

- **The alternative I rejected:** Stage Presence for 6 Block instead of Gorou's
  4+3. Gorou's banner is 4 Block *and* +3 on the next attack, which is strictly
  more for the same energy; the rejection was easy, which is itself a mark
  against the pair existing side by side.
- Standing Ovation printed two buffs I could not use: *"Ovation Trickle 1 — The
  first Spotlighted card each turn grants 1 Encore."* But nothing is Spotlighted
  until I play Ethereal Spotlight, and Ethereal Spotlight **costs 2 Encore**.
  The engine that makes Encore is gated behind having Encore. All act, Aria was
  the only key.

**Turn 2.** Toadpole 1 had gained *Thorns 2* and moved to 3×3. Played Salon
Début (deploy, 4 dry) → **Duet** → Freminet on Toadpole 2. Toadpole 2 died.

- **This is the turn I most want on the record.** Duet says *"The next Companion
  card you play this turn is played an extra time."* Freminet is a Companion.
  After it resolved, the Salon log showed **two** Crabaletta lines and Fanfare
  read 4 (= 2 performs × 2). One of those performs was Salon Début's own deploy.
  So *at most one* of the two Freminet plays performed a member. No line
  anywhere on the screen said "Duet" or named a repeat. I ended the turn unable
  to say whether Duet had fired at all.
- **The alternative I rejected:** Stage Presence + Soloist + Freminet — 6 Block
  and 12 damage, no ambiguity. I chose the Duet line specifically to find out
  what it did, and it did not tell me.

**Turn 3.** Aria → Ethereal Spotlight → Charlotte → Salon Début (second member).
Here the status bar grew a row reading **"Spotlight Spend Boost: 30 — the game's
data feed carries this meter's amount only: no maximum, and no rule for how it
is spent."** Nothing on the screen defines *Spotlight Spend Boost*. Standing
Ovation says 10%; the meter said 30. I never learned what it was measuring.

**Turn 4.** Freminet alone (now printing 9) finished the last Toadpole. **No
rejected alternative — one card was lethal and everything else was worse.** A
turn with no decision.

**Reward:** 19 Gold, took **Curtain Cue** ("If you moved the Spotlight this
turn: gain 3 Encore and draw 1 card. Otherwise: gain 1 Encore") over a second
Duet, Stage Combat, and Charlotte — Framing. Encore was the bottleneck and this
is a 0-cost faucet.

---

## Fight 3 — Seapunk 44/44

**Turn 1.** Salon Début → Soloist → Stage Presence. Took 5.
**The alternative I rejected:** Regal Bearing (3 Block + 1 Weak) instead of
Stage Presence (6 Block). Against an 11 they are arithmetically identical — 11
blocked to 5 either way. That equivalence is a small flatness in the kit: two
different-looking cards were the same card that turn.
Also of note: **Duet was in my hand with no Companion card to double.** Salon
Début is a Deploy, not a Companion, and the distinction is only findable by
reading the *Companion* glossary line ("A card titled with a character's name, a
dash, then its own"). Duet was a dead card that turn and the screen did not warn
me.

**Turn 2.** The engine turn, and the best turn of the run:
Aria (+5 Encore) → Ethereal Spotlight (−2) → **Curtain Cue** (Spotlight moved
this turn, so +3 and a draw) → An Invitation → Charlotte (Companion; Crabaletta
performed for a full 6) → Neuvillette — Sourcewater Droplets (Companion; 6 Block
and a second full perform). Encore arithmetic came out exactly as printed:
5 − 2 + 3 − 1 − 1 = 4. **This is the one place where every number on the screen
added up and I could plan three cards ahead.**
**The alternative I rejected:** Standing Ovation instead of Neuvillette for the
last energy — I wanted the Block and the perform now over 10% later.

**Turn 3.** Salon Début (second member) → Freminet → Neuvillette. Seapunk died.
**Alternative rejected:** High Tide (not yet owned at that point) — n/a; the
real rejection was Stage Presence, dropped because the enemy was dead on the
maths.

**Reward:** 17 Gold, took **High Tide** ("Deal 15 damage, already including
Fanfare. Burst +5. Elemental Skill") over Crashing Waves / Witness Stand / Kujou
Sara. I took it partly to see the **Burst** meter, which no screen had mentioned
until this card appeared.

---

## Interlude — Sunken Treasury, and a rest

Event: First Chest (56 Gold) vs Second Chest (311 Gold + Greed). I took the
**First**. My deck was 14 cards and the Salon engine wants specific cards in
specific order; a curse is a dead draw in a deck that already whiffs when Aria
is on the bottom.

Rest site: I **rested** (45 → 68) rather than Smith. With an elite two floors on
and a kit whose defence is Encore that I could not reliably generate, HP was the
resource that bought me more fights to observe.

---

## Fight 4 — Sewer Clam 56/56, Block 8, *Plating 8*

*"At the end of your turn, gain 8 Block. Plating is reduced by 1 at the start of
your turn."* An enemy that eats chip damage. This is the fight that showed me
the shape of the kit's damage.

**Turn 1.** Aria → Ethereal Spotlight → An Invitation → Stage Presence → Regal
Bearing. Took 0.
**The alternative I rejected:** Fischl — Nightrider for 7. Rejected explicitly
*because of Plating*: 7 damage into 8 Block that regenerates is 0, so the right
play was to bank Encore and Spotlight and burst later. That was a genuine,
enemy-driven decision and the kit supported it.

**Turn 2.** Salon Début → **Duet** → Freminet. Clam 56 → 28.
The arithmetic reconstructs exactly: 6 + 6 (two Crabaletta) eats the 8 Block and
4 HP; Freminet 9 (Frozen reaction); Freminet 9 again **+ 6 shatter**. So the
**Duet copy of Freminet did land its 9 damage — and did not perform a Salon
member.** Two Crabaletta lines, Fanfare 4, for three Companion-card plays' worth
of triggers. That is the clean version of the turn-2 ambiguity in fight 2:
**Duet doubles the card's own text but not the Salon perform the card is
supposed to cause, and nothing on any screen says so.**
Also here: the shatter's own text says *"The first Attack to hit it Shatters for
6 unblockable damage **and removes Frozen**"* — the shatter demonstrably
happened (the 6 is in the HP total) and the board still read **Frozen 1**
afterwards. Screen and outcome disagreed.

**Turn 3.** Curtain Cue → Aria → High Tide (16) → Soloist. Took 7 through 7
Encore.
Here I found the **Burst** problem. High Tide's own reminder reads *"every
Elemental Reaction grants 5 … You hold **0 of 70** Burst Energy"* — printed on
the turn *after* a Frozen reaction had fired. Two things at once: the meter did
not move for a reaction it says pays 5, and the threshold is **70** for a deck
holding exactly one Elemental Skill card. I never saw the Burst card. I have no
idea what Furina's Burst is.

**Turn 4.** Standing Ovation → Salon Début → Fischl. Clam died.
**Alternative rejected:** Stage Presence — the clam intended a Buff, not an
attack, so Block was worth nothing and the power was free real estate.

**Reward:** 15 Gold + Speed Potion. I **skipped the card** to conserve actions.

---

## Fight 5 (Elite) — Skulking Colony 75/75, *Hardened Shell 20*

*"Skulking Colony cannot lose more than 20 HP each turn."* Booming Conch fired:
**4 energy, 8 cards.**

**Turn 1.** High Tide (15) + Soloist (6) = 21, clipped to exactly **20**
(75 → 55) → Stage Presence → Regal Bearing. Took 1.
**Alternative rejected:** a third attack. The cap made the *fourth* damage card
worth literally zero, so the turn became "hit the cap with the two cheapest
things, then buy Block with the rest." A real decision, and a legible one —
the enemy did the work, not the kit.

**Turn 2.** Aria → Ethereal Spotlight → Curtain Cue (+3, Spotlight moved) →
Salon Début → Freminet. 55 → 35 (capped again). Took 3.
This was the turn where the kit felt best: Encore paid for the Spotlight, the
Spotlight paid Freminet up to 9, Curtain Cue refunded more than the Spotlight
cost, Frozen halved the incoming, and the leftover Encore ate the rest. Five
cards that all pointed the same way.

**Turn 3.** Aria → An Invitation → High Tide → Freminet. 35 → 15. Took 0.
**Alternative rejected:** Duet on Freminet. Rejected because fight 4 had just
shown me Duet does not double the perform, and the Hardened Shell cap meant the
extra 9 would have been thrown away anyway.

**Turn 4.** Curtain Cue (+1 Encore, so Crabaletta performed at a full 6) →
Freminet (9 + 6 = 15 = exactly lethal). Dead.
My follow-up `play "Soloist's Solicitation (1)"` was **refused** — the fight was
already over. Second and last refusal of the round.

**Reward:** 43 Gold, **Vambrace** (name only, no text printed), and I took
**Deep Breath** ("Choose one: Gain 1 Energy and 2 Encore | Spend 3 Encore: draw
3 cards. Exhaust") over Stage Combat / Macaron Break / Freminet — Pressurized
Floe.

---

## Floors 9–10 and the stop

Treasure: **Centennial Puzzle**. Rest site: **Smith**, and I spent my last two
actions upgrading **Salon Début → Salon Début+ ("Deploy Mademoiselle
Crabaletta. **Gain 2 Encore.**")** — chosen because the whole act had been
bottlenecked on Encore, and the upgrade is exactly the missing faucet.

Two things the Smith screen printed that belong in a legibility record:

- A block headed *"Not on this list, and why"* listing **four separate copies of
  Ethereal Spotlight** and a **second Freminet — Pers, Deploy!**, each annotated
  *"on the screen's list nowhere, and nothing on the feed says why."* The relic
  adds an Ethereal Spotlight to hand every turn; something is retaining those
  copies in the deck state the screen reads.
- The pick preview printed **both** the unupgraded and the upgraded face, each
  tagged `PICKED`, which read at first as though I had selected two cards.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The good ones were all about **Encore**, and they were genuinely good. Encore is
one pool doing three jobs at once: it is my armour *under* Block, it is the fee a
Salon member pays to perform at full strength instead of 75%, and it is the
price of the Ethereal Spotlight that makes every Companion card 50% bigger. So
every turn with Aria in hand is a real allocation problem — spend 2 on the
Spotlight and my members go dry, or keep the pool fat and hit softer but survive
the swing. Fight 3 turn 2 and elite turn 2 were the two best turns of the run,
and both were that trade resolved five cards deep with the numbers all visible.

Second real choice: **which element to land, and in what order.** The *Reaction
preview* line that appears on an attack when the target already wears an aura is
the clearest text in the kit. Frozen-then-shatter carried two kills. Turning
Crabaletta's Hydro into a setup for Freminet's Cryo is the kit's most satisfying
sentence.

Third: **Plating and Hardened Shell forced real sequencing** — bank vs. burst,
and "the 21st point of damage is worth nothing, buy Block instead." Those were
decisions the *enemies* created, though, not the kit.

**(b) What felt automatic, and what never seemed worth playing.**

Aria of Recompense is never a choice; it is a tax. If it is in hand it is the
first card played, every time, because nothing else in the deck makes Encore and
half the deck reads worse without it. Ethereal Spotlight is the same — 0 energy
for a permanent 50%, so it is played the instant the Encore exists. Two of my
best cards are auto-plays.

Stage Presence and Regal Bearing were interchangeable filler; against an 11-damage
attack they blocked identically, and I never once thought about which to play.
Soloist's Solicitation (6 damage, no element, no text) is the card the deck is
padded with; it exists to be the thing you play when nothing is happening.

Duet never earned its slot. Against the Sewer Clam it doubled 9 damage and did
*not* double the Salon perform, which is the only reason a Furina player would
ever want it.

**(c) What I could not understand, or that contradicted its own printed text.**

Five things, in order of how much they cost me:

1. **The Spotlight bootstrap.** Ethereal Spotlight costs 2 Encore. Standing
   Ovation's *Ovation Trickle* grants Encore "the first Spotlighted card each
   turn" — but nothing is Spotlighted until Ethereal Spotlight is played. The
   Encore engine is locked behind the resource it produces, and the only key is
   one copy of Aria sitting somewhere in the draw pile.
2. **Duet.** It doubled the card and not the perform. No line on any screen
   named Duet resolving, so on the first attempt I could not even tell whether
   it had fired.
3. **Burst Energy: 0 of 70**, printed on a turn after an Elemental Reaction that
   the same paragraph says grants 5. Either the reaction did not pay or the
   meter does not display it. Either way, 70 with one Elemental Skill card in
   the deck means I finished the act never having seen Furina's Burst card, and
   with no idea it existed until a shop card mentioned it.
4. **"Spotlight Spend Boost: 30"** appeared in my status bar with the explicit
   admission that the feed carries "no rule for how it is spent." Nothing on the
   screen defines the term.
5. **Guest Cast says "no Fanfare"** and Fanfare went up by 2 on the beat it was
   applied. And **Frozen's shatter says it "removes Frozen"**; the shatter
   landed and *Frozen 1* was still on the board.

Two smaller ones. The Salon activity log writes *"Crabaletta hit Corpse Slug"*
with no copy number, so in a two-of-a-kind fight I could not tell which body it
hit. And **Salon Début deals damage but takes no target** — the refusal told me
so, the card face did not.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Duet.** It is a conditional that needs a Companion card *and* a
Salon member already on stage to mean anything, it was dead in hand in fight 3,
and when it finally worked it did half of what I thought it did.

Happiest to draw: **Aria of Recompense (reframe)** — and that is a complaint as
much as praise. It is the card that turns the whole kit on. Drawing it is
relief, not excitement.

The card I most *enjoyed*: **Freminet — Pers, Deploy!**, because it is three
things at once (a 6–9 damage attack, an aura, and a Companion trigger that
performs a member) and the *Reaction preview* line tells you which of the three
matters this turn.

Last, the literal text: my Encore card prints its title as **"Aria of
Recompense (reframe)"**. `(reframe)` reads as a development tag that escaped
onto a card face; it is on the card in hand, in the deck list, and in the
upgrade screen.

**(e) Did the first turn of the first fight already present a decision?**

Yes, and a good one. The opening hand held two Stage Presence (12 Block, which
fully eats the only incoming attack) against Salon Début + Freminet + Soloist,
and Freminet grew a *Reaction preview: Frozen* line the moment Crabaletta put
Hydro on the target. Choosing to eat 8 damage to set up a shatter, on turn one,
knowing nothing about the character, is a real decision made from printed text
alone.

The caveat is the other half of that same screen: **Ethereal Spotlight was in my
opening hand, unplayable, on turn 1 of every single fight of the run.** Its
"CANNOT BE PLAYED: you have no Encore, and this costs 2" was the first line of
the first hand and it never once changed. A relic that hands you a dead card
every turn until an uncertain draw is the first thing a new player reads about
this character.

---

## Non-blindness declaration

My model family is **Opus (Claude)**. This kit's author is a **different Claude
model**, so this seat is not independent of the authoring model family, only of
the authoring session and of the repo.

**Repo files read: none.**

Commands run outside `blindplay observe` / `blindplay act`:

- `python -m understudy.embark --character KLEEMOD-FURINA --lane 2` — once, to
  open the lane, exactly as the coordinator instructed. Its output printed the
  seed, stamp, character, ascension and lane/port and nothing about the kit.
- `mkdir -p review/qa/furina-reframe-round-5-2026-09-04` — once, folded into the
  same shell call as an `observe`.
- Shell text filters applied to the output of `observe` only, to re-read one
  block of a long screen without re-printing it whole: `head`, `tail`, `sed -n`,
  `grep`, and one `for` loop that issued several `act` calls in sequence. No
  filter reached anything but the bridge's own printed output.

Tools used: **Bash** (for every command above) and **Write** (once, for this
file). No Read, Glob, Grep-over-repo, Agent, or web tool was used at any point. I
did not run `harness state`, `scenario`, `staged_turn`, `soak`, or any other
understudy subcommand. I did not tear the lane down.

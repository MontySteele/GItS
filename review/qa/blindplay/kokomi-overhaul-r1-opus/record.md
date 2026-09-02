# Blind play session `kokomi-overhaul-r1-opus`

**R217 G, and same model family as the author: subjective feedback from a Claude Opus subagent playing the real game through the blind render. Useful for iteration; not human validation, not balance evidence, not approval, and not an author-disjoint read.**

## Identity
- model: claude-opus (this agent)
- build_version: not printed to the tester
- run_seed: UNT2Z7S6TXQM (given by the operator)
- actions: 112
- termination: run ended (died on floor 7, fight 4)

## Pre-fight: Neow

Three options: +11 Max HP, "Lost Coffer" (1 card reward + 1 random potion), "Silver
Crucible" (first 3 card rewards Upgraded, first Treasure Chest empty). I took Lost
Coffer: two concrete things now, no downside, and as someone who had never seen this
character I wanted more cards to learn from. The reward card list was
`High Tide (proto)` (Exert 3, Tide +10), `Read the Field` (3 Block, Plan: 4 Block),
`Battle Plan` (Plan: gain 2 Energy). Three of the four nouns on that screen — Exert,
Tide, Plan — had no definition anywhere on it, while `Block` did. I took High Tide on
the guess that Tide was the character's resource and +10 was a big number. That was a
coin flip, not a decision.

## Fight 1 — Sludge Spinner (38 HP), in the tester's own words

1. Opened at 64/80 with 3 energy, 2x Water's Edge, 2x Coral Guard, Kurage's Oath.
   I played Kurage's Oath first purely to find out what "Exert 2" meant — HP went
   64 → 62, so Exert is paying HP. Then both Water's Edge (38 → 26). Round 2 I was
   Weak, so I banked instead of swinging blind: High Tide (Tide 5 → 15, −3 HP), then
   Water's Edge, then Rising Tide, which I had just drawn and which was the first card
   that told me how Tide converts ("Deal 4 damage. Surge."). 4 + 15 = 19 raw, 18 landed
   through Weak: 26 → 8. Round 3 the Spinner had Strength 3 and telegraphed 11, so
   Water's Edge (8 → 2) plus 2x Coral Guard for 10 block, taking 1. Round 4 one
   Water's Edge finished it. **Ended at 48/80.**
2. The line I did not take: two Water's Edge on round 1 instead of leading with
   Kurage's Oath, i.e. 12 damage now instead of 5 stored damage and −2 HP. It would
   have put the Spinner a full turn closer to dead and cost 2 fewer HP, and by my own
   later arithmetic it was the better play. I paid the difference to learn the keyword.
3. What would have changed my line: if Weak had not landed on round 2 I would have
   just attacked and probably skipped the Tide bank entirely. And if the Spinner had
   opened with the 3x3 multi-hit rather than a single 8, I would have blocked round 1
   instead of racing.
4. Automatic: Water's Edge. It is 6 damage for 1 energy and nothing in the deck beats
   that rate, so it was never a decision. Dead: nothing was truly dead, but Kurage's
   Oath was close — 1 energy and 2 HP for 5 stored damage is worse than 1 energy for
   6 immediate damage, and it is only worth playing on a turn where I already know a
   Surge card is in hand.
5. My plan changed exactly once, when Rising Tide appeared and Tide stopped being an
   abstraction. Before that I was hoarding a number I had no way to spend.
6. Confusing: "Exert", "Tide", "Surge" and "Mends" all appear in card and relic text
   with no definition on the screen that uses them. I learned Exert = lose HP by
   watching my HP bar. The relic says "At the end of each turn you did not Surge, it
   Mends you 2" and I could not predict when that 2 arrived (see fight 3). Also the
   Spinner's printed intent went from 8 to 6 between round 1 and round 2 with nothing
   on screen accounting for it — no debuff on it, and its Strength 3 only showed up in
   round 3.

## Fight 2 — Toadpole (24 HP) + Toadpole (22 HP), in the tester's own words

1. Round 1 I dumped 3x Water's Edge into the 22 HP Toadpole (22 → 4) rather than split,
   and ate 7. Round 2 my whole hand was skills — 2x Coral Guard, 2x Kurage's Oath,
   Stolen Chapter — with no attack at all, into a 3x3 and a Thorns 2 that the other
   Toadpole had just Empowered onto itself. Stolen Chapter dug out Rising Tide, which
   at Tide 0 was just a 4-damage attack, but 4 was exactly the wounded Toadpole's HP,
   so it died; Coral Guard covered 5 of the 9. Round 3 was a dead-ish turn (no attack
   worth the energy) so I played Coral Bulwark for 6 block + Tide 6 and chipped with
   Water's Edge. Round 4 the survivor Empowered instead of attacking — a free turn — so
   High Tide (Tide 6 → 16) into Rising Tide for 4 + 16 = 20 killed it from 18.
   **Ended at 35/80.**
2. The line I did not take on round 2: 2x Coral Guard for 10 block, eating nothing and
   letting the 4 HP Toadpole live and Empower. That would have kept my HP whole and
   given the small one Thorns; I chose to kill the body instead and take 4. I still
   think killing was right, but it was the closest call of the fight.
3. What would have changed it: an attack card in that round-2 hand. Five skills and
   one enemy at 4 HP is the draw that made me buy card draw later.
4. Automatic: Water's Edge again, and Coral Bulwark the moment I had it — 6 block plus
   Tide 6 for 2 energy is the only Tide source that does not charge me HP, and that
   made it the card I always wanted to see. Dead: Rising Tide at Tide 0 is a 1-energy
   4-damage attack, i.e. strictly worse than Water's Edge; it was dead every turn I
   drew it before I had banked.
5. The plan changed from "race" to "bank on the turns the enemy is not hitting me".
   Both Toadpoles spent turns on Empower, and those free turns are where the Tide
   engine actually pays.
6. Confusing: the Empower buff on the Toadpole was described as "Thorns 2 (buff) — When
   hit by an attack, deal 2 damage back", then it simply vanished from the display a
   round later with no printed expiry. The page itself warns it cannot say when powers
   end, which is honest but means I was guessing whether attacking would cost me 2.

## Fight 3 — Seapunk (44 HP), in the tester's own words

1. Entered at 35/80 against a 44 HP enemy telegraphing 11, so round 1 I played
   Coral Bulwark+ (6 block, Tide 6) and Coral Guard (5 block) for exactly 11 and took
   nothing. Round 2 it switched to 2x4; Kurage's Oath took Tide to 11, Rising Tide hit
   for 4 + 11 = 15 (44 → 29), Coral Guard covered 5 of the 8. Round 3 it Empowered — a
   free turn — and with Tide back at 0 I found that plain Water's Edge + Breaker
   (6 + 8 = 14) beat anything the Tide cards could do from an empty bank, so I took
   that: 29 → 15. Round 4 it had 15 HP behind 7 Block and was swinging 12. I spent the
   Energy Potion to get 5 energy and chained High Tide (Tide 10), Kurage's Oath (15),
   Coral Bulwark+ (21, +6 block), then Rising Tide for 4 + 21 = 25, which went through
   the 7 Block and killed it outright. **Ended at 25/80.**
2. The line I did not take: saving the Energy Potion and settling for ~19 damage,
   leaving the Seapunk at 3 HP and eating another 12. That was the safer-feeling play
   and it was wrong — the potion bought the whole fight.
3. What would have changed my line: if the round-3 intent had been an attack rather
   than Empower I would have had to block and the fight would have run two more rounds,
   which at 30 HP I probably do not survive.
4. Automatic: Coral Bulwark+ into Coral Guard as the "block exactly the telegraph"
   package. Dead: Undertow, which I had just bought — I drew it twice at Tide 0, where
   it deals 0 and blocks 0. It is a blank card unless the bank is already full.
5. The plan hardened into a rhythm: block on the turns they hit, bank Tide on the turns
   they do not, dump the bank the moment I can see a kill. The Energy Potion turn was
   the one moment in the run where the engine felt genuinely good.
6. Confusing, and the sharpest thing I hit all run: **the relic's Mend does not fire
   the way it reads.** "At the end of each turn you did not Surge, it Mends you 2, up
   to 8 per combat." At the end of round 1 here I did not Surge, I was at 35/80, and I
   went into round 2 at 35/80 — no 2. It only ever healed me on turns where I had
   already taken damage *in that combat*, which is a rule nothing on screen states.
   Second: **`Coral Bulwark+` (upgraded) prints exactly the same numbers as the
   unupgraded card** — "Gain 6 Block. Tide +6" — and in play it gave 6 block and Tide 6.
   Same for `Water's Edge (proto)+`, which prints "Deal 6 damage" and dealt 6. I have
   no way to tell what my Light Door upgrade bought.

## Fight 4 — three Two-Tailed Rats (19 / 18 / 21 HP), in the tester's own words

1. Entered at 25/80. Round 1 the Block Potion (12) plus Coral Guard covered the 14
   incoming and Breaker chipped the 18 HP rat to 10. Round 2 they hit me with Frail and
   swung 20 into a hand whose best block, after Frail, was 9 — I burned Fysh Oil for the
   Dexterity and still fell to 14. Round 3 they all went passive (one Summon, two
   Debuff), so I spent the whole turn killing the summoner: Rising Tide for 11, then
   both Water's Edge, 19 HP dead before it could summon. Round 4 the second rat took
   over the summoning; I could only manage Feint (4 now, 8 planned) and a Coral Guard,
   and a fresh 17 HP rat arrived anyway. From there it was a treadmill: rounds 5–8 I
   killed one rat per turn or two while the summoner replaced it, my block cards came
   in ones and twos, and my HP ratcheted 14 → 14 → 14 → 12 → 11 while the board went
   back to three bodies. Round 9 all three rats telegraphed 8 apiece — 24 into 11 HP —
   and my hand was five attacks and a Kurage's Oath with not one block card in it.
   I killed the 5 HP rat and put Breaker into the summoner, which left 16 incoming and
   nothing to stop it. **Died at 11/80 on floor 7.**
2. The line I did not take, and it is the one I would replay: on round 8, at 12 HP with
   Tide 6, I could have chained High Tide + Kurage's Oath into Undertow for 15 damage
   and killed the wounded rat outright, at a cost of 5 HP and no Mend. I played the
   cheap line instead (Coral Bulwark+ for block, Water's Edge for 6) because 7 HP felt
   unsurvivable. It bought me one more round and I died anyway. Against a summoner, the
   bodies are the clock, and I priced HP over tempo one turn too long.
3. What would have changed my line: literally one block card in the round-9 hand. My
   deck has three Coral Guards, a Coral Bulwark and an Undertow and I drew none of them
   in five cards. Also: if the summoner had been the low-HP rat rather than the 20–21
   HP one, I could have removed the engine on round 3 instead of removing a body.
4. Automatic: Coral Guard, every single turn, no thought involved. Water's Edge,
   likewise. Dead: Reading the Tide at low Tide (at Tide 0 it draws nothing and I
   played it once to confirm; at Tide 6 it drew exactly 1); Breaker at Tide 0, where
   it is 8 damage for 2 energy and therefore worse than two Water's Edge; Undertow at
   Tide 0, which is a literal blank. The Skill Potion was dead in the strongest sense —
   it would not fire at all.
5. My plan changed three times: race → kill the summoner → survive the treadmill. The
   third was not really a plan. Once the summoner outpaced my damage there was no line
   in the deck that closes the gap, and I was choosing which rat to be behind on.
6. Confusing: **when a rat died the survivors were renumbered.** Round 4 ended with
   Rat (1) at 6/18 and Rat (2) at 21/21; round 5 opened with "Two-Tailed Rat (1) —
   HP 17/17" and "Two-Tailed Rat (2) — HP 21/21", which reads as two brand-new
   full-health enemies. I had to reconstruct from the HP numbers that the wounded one
   had died to Feint's Plan and the summon had slotted into its index. With a summoner
   on the field I could never be sure which body was which. Second: **Fysh Oil says
   "Gain 1 Strength and 1 Dexterity" and I only ever got the Dexterity** — no Strength
   line appeared in my status, and Rising Tide on the very next turn dealt exactly
   4 + 7 = 11 with no +1 anywhere.

## The run, in the tester's own words

1. From the cards alone, this character is a battery. You spend HP and energy on
   turns you are not being punished (Exert 2 for Tide 5, Exert 3 for Tide 10, or
   Coral Bulwark's 6 block *and* Tide 6), and then one card — Rising Tide, Breaker,
   Undertow — cashes the whole bank at once and resets it to zero. Water is the theme
   in a mechanical way: every attack applies a Hydro aura, and the aura text keeps
   promising an "Elemental Reaction" from a different element that this deck never
   contains, so all run the aura was decoration.
2. The recurring tension was real and I felt it every turn: **Tide costs HP or tempo
   now for damage later, and later may not come.** The bank only pays if a Surge card
   is in your hand on the turn the bank is full, and I had four builders to three
   outlets in a 16-card deck. Twice I banked 15+ and had nothing to spend it with;
   twice I drew Undertow at Tide 0 and held a blank. Underneath that sat a harder,
   less interesting arithmetic: Kurage's Oath is 1 energy + 2 HP for 5 stored damage,
   and Water's Edge is 1 energy for 6 immediate damage. **The signature mechanic is
   worse than the basic attack unless you are stacking two or more builders into one
   outlet on a turn nobody is hitting you.** That is a narrow window, and every time I
   did the arithmetic honestly the boring line won.
3. Carried the run: Water's Edge (the rate nothing else matches), Coral Guard (the only
   block I could ever count on), Coral Bulwark (the one Tide source that doesn't bill
   me HP), and the Energy Potion, which single-handedly won fight 3 by letting three
   builders and an outlet land on the same turn. Never mattered: Reading the Tide (drew
   1 card, once, all run); Undertow (blank both times I saw it); Stolen Chapter, which
   was fine but never changed an outcome; the Hydro aura, which did nothing at all
   across four fights.
4. It became repetitive at fight 4 and reduced to a single loop: read the telegraph,
   play Coral Guard, play whatever attack the hand gave me, end turn. Rounds 5 through
   9 were the same turn five times with different numbers, because the summoner meant
   the board never got smaller and my hand never got a burst. Before that — fights 1 to
   3 — the free turns where the enemy Empowered were genuinely interesting, because
   those are the turns the Tide bank is actually correct.
5. Next time I would draft the other way round: **outlets before builders.** I bought
   Breaker and Undertow at the shop specifically to fix a 3-builders/1-outlet deck and
   it was the right instinct one purchase too late. I would take Deep Current over
   Coral Bulwark for the multi-enemy fights (fight 4 killed me and a 4-damage sweep
   that also builds Tide would have changed rounds 5–9), I would skip Reading the Tide
   entirely — it needs a Tide floor my deck could not hold — and I would take Gorou or
   Charlotte for a body/block rather than a fourth way to make a number go up. And I
   would not take High Tide at Neow again; paying 3 HP for a resource whose payoff card
   I had not yet seen was a blind bet the screen gave me no way to price.

## Defects and oddities

- **The Skill Potion cannot be used.** `use potion "Skill Potion"` returned, three
  separate times across two different turns, `{"ok": true, "verb": "use potion",
  "post": {"action": "use_potion", "slot": 1}, "printed": {"potion": "Skill Potion"},
  "refusal": ""}` followed by a bare `error` with no message. The potion stayed in the
  list every time. It was my only remaining out on the turn I died.
- **Fysh Oil grants only half of what it prints.** Text: `Gain 1 Strength and 1
  Dexterity.` After using it my status showed `Dexterity 1 (buff) — Increases Block
  gained from cards by 1` and no Strength entry at all. Rising Tide on the next turn
  dealt exactly 11 into a 19 HP rat with Tide 7 (4 + 7), i.e. no Strength bonus applied
  to the attack either.
- **Upgraded cards print identical text and identical numbers to their base versions.**
  `Coral Bulwark+ (upgraded) — cost 2, skill / Gain 6 Block. Tide +6.` gave exactly
  6 Block and Tide +6 in play. `Water's Edge (proto)+ (upgraded) — cost 1, attack /
  Deal 6 damage.` dealt exactly 6. The `Light Door` event ("Upgrade 2 random cards")
  therefore has no visible effect from the player's seat.
- **The relic's Mend does not behave as written.** `Tamanooya's Casket — ... At the end
  of each turn you did not Surge, it Mends you 2, up to 8 per combat.` At the end of
  fight 3 round 1 I did not Surge and was at 35/80; round 2 opened at 35/80. It only
  ever healed on turns where I had already taken damage in that same combat. That rule
  is nowhere on screen, and it makes the "block everything" turn silently worse than
  the card text implies.
- **Raw markup leaks into potion text**: `Energy Potion — Gain [Energy][Energy].`
- **Enemies are renumbered when one dies, with no indication.** Fight 4 round 4 ended
  with `Two-Tailed Rat (1) — HP 10/18` and `Two-Tailed Rat (2) — HP 21/21`; round 5
  opened with `Two-Tailed Rat (1) — HP 17/17` and `Two-Tailed Rat (2) — HP 21/21`. With
  a Summon enemy on the board there is no way to tell a renumbered survivor from a new
  arrival except by reading max-HP values.
- **Keywords used with no definition on the screen that uses them**: `Exert` (I learned
  it means lose HP by watching my HP drop), `Tide`, `Surge`, `Mends`, `Swirl`
  (`Sayu — Yoohoo Art: Fuuin Dash — Deal 4 damage. Swirl an enemy's aura.`), and
  `Elemental Reaction` (the Hydro Aura text says "A hit of a different element consumes
  the aura and triggers an Elemental Reaction" and never says what one does). `Plan`
  was undefined on the card (`Battle Plan — Plan: gain 2 Energy`) and only got a
  definition once I had a Plan buff on me: `Plan 1 (buff) — 1 planned effect will
  happen at the start of your next turn`.
- **`(proto)` is printed inside card titles shown to the player**: `Water's Edge
  (proto)`, `Kurage's Oath (proto)`, `High Tide (proto)`, `Sango Isshin (proto)`.
- **An enemy's intent number changed with nothing on screen to explain it.** Sludge
  Spinner round 1: `Intent: Aggressive, 8`. Round 2: `Intent: Aggressive, 6`, with no
  debuff shown on it and its `Strength 3` only appearing in round 3.
- **Sold-out shop slots lose their identity**: after buying, the shelf printed
  `**Card** — 48 gold (not available)` and `**Card** — 38 gold (not available)` instead
  of the names. Relatedly, **shop cards print no energy cost and no card type** — the
  reward screens print `cost 1, attack` but the shop prints only rules text, so I bought
  Breaker and Undertow without knowing what they cost to play.
- **`Reading the Tide` is a fully blank card below 5 Tide** (`cost 0, skill / Draw 1
  card per 5 Tide`). I played it at Tide 0 to confirm: it drew nothing, with no warning
  and no refusal. Same category: `Undertow (proto)` at Tide 0 deals 0 damage and gains
  0 block, and `Rising Tide` at Tide 0 is a strictly-worse Water's Edge.
- Not a defect, but the page's own caveats bit twice: enemy `Thorns 2` appeared and then
  silently vanished, and the "two cards print the same name / cannot show which is
  enchanted" note meant I never knew which of my two same-named cards was the upgraded
  one when both were in hand.

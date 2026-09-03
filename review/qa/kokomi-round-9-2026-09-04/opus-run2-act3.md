# Kokomi round 9, run 2, act 3 — blind seat record

## Identity

- **Model / seat:** Opus, blind TESTER seat, lane 1 (`GITS_LANE=1`).
- **Run:** Kokomi round 9, run 2. Third of three chained seats; acts 1 and 2 were
  cleared by earlier seats and I inherited their deck, relics and potions on the
  act-3 map.
- **Neow pick: none, inherited.** I did not make one and never saw the Neow screen.
- **Character:** Kokomi (Bake-Kurage / Plan kit).
- **Act:** 3. The map printed the act's top as **Aeonglass**. I never reached it —
  the boss was 10 floors away when the run ended.
- **Actions accepted:** 84 `act` calls, all accepted. **Zero refusals.**
- **Termination:** not a budget stop. **The run ended — I died** in the third
  fight of the act. `observe` printed:

  ```
  TOOL-BLOCKED: game_over

  the run is over; there is nothing left to play

  The run ended on floor 39.
  ```

  Well inside both budgets (84 of 250 actions).
- **HP trajectory:** 69/81 entering fight 1 → 24/81 after it → 25/82 into fight 2
  → 5/76 out of it (Paper Cuts ate 6 Max HP) → 6/77 into fight 3 → dead. I was
  under 25% HP for the last two fights and never saw a rest site: the act-3 map
  put the first RestSite 5+ floors ahead and every branch I was offered after the
  opening Ancient room was a **single node**, four times running.
- **Gold at the end:** 279 (247 inherited + 19 + 13). **I never spent any of it** —
  see the shop note in fight 2's lead-in.
- **Potions held at the end:** none. I entered act 3 with Orobic Acid, gained
  Duplicator from fight 1, and spent both.
- **Relics at the end (9):** Tamakushi Casket (start with the Bake-Kurage; applying
  a debuff deals 2 Hydro to that enemy), Silver Crucible, Vajra (1 Strength),
  Radiant Pearl (1 Luminesce into hand each combat), Whetstone, Red Mask (1 Weak
  to ALL at combat start), The Chosen Cheese, **Blessed Antler** (my pick — +1
  energy per turn, 3 Dazed shuffled in each combat), **Gorget** (4 Plating each
  combat).
- **Deck at the end:** I was never shown a deck list, so this is only what the
  bridge actually printed to me across three fights — draw piles opened at 30/31/32
  cards, so this is partial. Attacks: Strike ×3+ (one printed 7, one 10, one
  upgraded Strike+ 10), Undertow, Undertow+, Feint, Sango Isshin, Sango Isshin+,
  Predator+, Amber — Fiery Rain, Slack Water, Deep Current+ (added), Ambush+
  (added). Skills: Defend ×3+, Read the Field, Coral Bulwark+, Salt Line, Luminesce,
  Lynette — Bogglecat Box, Stolen Chapter, War Council, Kurage's Oath+, Vanguard+,
  Expose+, Exposed Flank+ ×2, Kirara — Surprise Dispatch+, Nereid's Ascension,
  Kamisato Ayato — Kyouka. Powers: The Moon Overlooks the Waters, Treatise, Song of
  Pearls. Plus 3 Dazed per combat from the Antler.

### The one pick I did make

**Ancient room, three relics: Blessed Antler over Beautiful Bracelet and Glitter.**
"Gain [Energy] at the start of each turn" is a permanent ~25–33% increase in cards
played per turn, and I judged 3 Dazed per combat an acceptable price. In hindsight
this is arguable: the Dazed are Ethereal so they self-clear, but every fight I drew
2 of them in the hand that mattered, and my deck was already ~30 cards. The energy
was not the binding constraint in any of the three fights — **cards in hand were**,
and the Antler made hand quality worse while making energy I twice could not spend.
Twice I ended a turn with 1–2 energy unspent and nothing playable.

---

## Fight 1 — Devoted Sculptor, HP 160/162

Entered at 69/81. The Sculptor already had Weak 1 and Hydro Aura 1 before I acted
(Red Mask, then Tamakushi Casket's 2 Hydro off that debuff — which is why it was at
160/162, not 162/162). Turn 2 revealed **Ritual 9 — "At the end of its turn, gains
9 Strength."** That is the whole fight: its attack went 9 → 21 → 30 → 39 and I had
to kill 162 HP before the fourth one landed.

**Turn 1** (4 energy; intent Empower, so zero damage incoming).
Played Lynette — Bogglecat Box (draw 2), then Undertow (11 damage), then wrote
**War Council** and **Read the Field** as Plans on the Kurage.
*Rejected:* playing War Council now for its 1 Weak, and playing the two Defends in
hand. Both rejected for the same printed reason — the intent line said Empower, so
Block "until next turn" would expire against nothing, and War Council's Plan line
("Deal 5 damage and apply 1 Weak to ALL") is strictly larger than its play line
("Apply 1 Weak to ALL"). This is a genuinely good decision shape: the Plan mechanic
turns a no-damage enemy turn into a resource rather than a dead one.
*Also rejected:* playing Luminesce for +2 energy — I had nothing worth buying with
it, so I banked it (it Retains, so banking is free bar the hand slot).
This turn also answered a rules question the cards do not: **two Plans queue**, and
the board printed them in order.

**Turn 2** (Sculptor now Ritual 9 / attacking 21; my 10 Block from the Read the Field
Plan covered it exactly, I took 0).
Vanguard+ (1 Vulnerable) → Orobic Acid potion (three free cards: Undertow, Salt Line,
Treatise) → Treatise → Kyouka → Undertow (22) → Strike (16).
*Rejected:* writing Vanguard+ as a Plan for 2 Vulnerable + 1 Weak next turn instead
of 1 Vulnerable now. Larger on paper, but I had just drawn a potion's worth of cards
and wanted the multiplier live *this* turn; against a Ritual enemy, damage now beats
damage later. *Also rejected:* Salt Line's free 8 Block — the Sculptor's hit was
already covered, and an exhausting card spent for wasted Block is a card deleted
from the fight, so I let it discard back into the deck.
**First disagreement between screen and outcome here.** Kyouka reads
*"For 2 turns, your Attacks apply Hydro and deal 4 additional damage. Then deal 12
Hydro damage to a random enemy."* I played it expecting 12 damage immediately. The
Sculptor's HP did not move — 139 before, 139 after. See (c).
**Second disagreement.** Strike printed 7. With Strength 1 and Kyouka's +4 both
displayed on me, and Vulnerable 1 on the target, I predicted (7+1+4)×1.5 = 18. It
dealt **16**. Undertow the same turn dealt exactly the 22 I predicted. I could not
make one arithmetic fit both.

**Turn 3** (enemy at Strength 9, hitting 21; my hand had exactly one attack).
Luminesce → The Moon Overlooks the Waters → Strike → Song of Pearls → wrote
Nereid's Ascension as a Plan.
*Rejected:* the all-offence line. I counted it and it was 16 damage — the hand had
one attack in it — against 101 HP, so racing was arithmetically dead and I built the
engine instead. *Rejected:* Defend for 5 Block, in favour of Nereid's Ascension,
because Nereid's also gives the Kurage something to carry out next morning, which
turns on Treatise's draw and Song of Pearls' Block.
**Strike printed 11 and dealt exactly 11**, with Strength 1 and Kyouka still shown
on my own status line. So on this turn neither modifier applied, and on the previous
turn one of the two did.
Writing Nereid's paid immediately and taught me the actual engine: **the Moon fires
a Plan the moment you write it, and it stays queued as well.** The board said so in
words the card does not use: *"Plans also happen NOW as you write them."* Song of
Pearls gave 3 Block and Treatise drew me a card off it. This was the best turn of
the run and the only one where the kit felt like it had a machine in it.

**Turn 4** (enemy 77, Strength 18, hitting 30; I was at 51).
The morning carried out Nereid's **twice**, and the enemy had quietly dropped 90 → 77
with no attack of mine in between — that is Kyouka's missing 12, arriving two turns
late as 13 when the buff expired.
Amber — Fiery Rain (17) → Sango Isshin+ (**31**) → Sango Isshin (21). Enemy 77 → 8.
*Rejected:* Undertow+ (10 damage for 1 energy) in favour of the second Sango at 2
energy, because **Sango Isshin** reads *"If the Bake-Kurage carried out a Plan this
turn, deal a quarter of your Max HP to ALL enemies instead"* — 20, and the Kurage had
carried out two. This card is the best-designed thing in the kit: the condition is
checkable on the board, the payoff is large, and it made the Plan I wrote a turn ago
feel like it mattered.
**Third disagreement.** I sequenced Amber (Pyro) first specifically to set up a
Vaporize for the Hydro Sangos. After Amber, the enemy's status block showed **no aura
at all** — not the Pyro the printed rule says a hit on a bare body leaves. I wrote off
the Vaporize and re-planned for 20-damage Sangos. Then Sango Isshin+ hit for **31**,
which is 20 × 1.5 + 1 — the Vaporize happened. The screen showed no aura for two
consecutive observes; the body had one.

**Turn 5.** Expose+ (0 cost, 3 Vulnerable, and 2 Casket damage off the debuff) → Strike.
Kill. *Rejected:* bare Strike. The enemy had 8 HP and Strike prints 7; with Strength 1
that is exactly 8, but I had watched Strike ignore Strength twice already, so I spent
a free card to make an 8-HP kill a 3-point-margin kill instead of a coin flip. **A card
whose printed number I could not trust turned a free action into a mandatory one.**

Rewards: 19 gold, Duplicator, and **Ambush+** ("Deal 5 damage. Plan: Deal 15 damage")
over Treatise+, Deep Current+ and Rosaria — chosen because its Plan line is triple its
play line, which is the axis the Moon and Nereid's multiply.

### Between fights 1 and 2 — the empty shop

The next node printed:

```
# The shop

You have 247 gold.

On the shelves:


## What you can say

- `buy "<item>"`
- `proceed`
```

Nothing on the shelves. I re-ran `observe` to rule out a load-timing artifact and got
the identical screen. There was no event text, no options, no card removal — only
`proceed`. The only hint that this was not a broken shop came in the tool's own status
line **after** I left: `ok Proceeding from fake merchant`. So it was an event
masquerading as a shop, and from the seat's chair it is indistinguishable from a shop
that failed to stock. **I carried 247–279 unspent gold to my death**; this was the one
screen in the act that could have converted it, and it printed as empty.

Then a chest: took **Gorget** (4 Plating at combat start).

---

## Fight 2 — 3× Scroll of Biting, HP 33/35, 30/32, 32/34

Entered at 25/82. Every Scroll carried **Paper Cuts 2 — "Whenever Scroll of Biting
deals unblocked attack damage to you, you lose 2 Max HP."** At 25 HP that is a fight
where taking a hit costs twice.

**Turn 1** (Scroll 1: 3×2, Scroll 2: Empower, Scroll 3: 10).
Luminesce → Expose+ on Scroll 3 → Undertow → Strike → Sango Isshin+ — killed Scroll 3
— then wrote Nereid's Ascension as a Plan.
*Rejected:* spreading damage across all three, and killing Scroll 1 instead. I focused
Scroll 3 because it was the largest printed intent (10) and Vulnerable is single-target,
so the multiplier and the threat pointed at the same body. That is a real decision and
the screen gave me everything I needed to make it.
*Rejected:* Sango Isshin+'s big mode — the Kurage had carried out nothing on turn 1, so
it was an 8-damage card, and I used it as one.
Ended on 4 Block from Plating against a weakened 3×2; took 2 damage and 2 Max HP.

**Turn 2** — **the turn I lost the fight on, by misreading a card.**
23 HP, 28 incoming (14 + 7×2), no Block cards drawn but Coral Bulwark+, Read the Field
and three Defends in hand. I played **The Moon Overlooks the Waters** (2) and then
**Read the Field** (1) normally, expecting *"Plans also happen when played"* to give me
its base 5 Block **and** its Plan line's 10 — 15 Block for one energy, the same total as
four Defends but with the engine deployed for free.
It gave **5**. The Moon does not do that. It fires a Plan when the card is *written onto
the Kurage*, which the board states clearly and the card does not.
That left me on 5 Block with 1 energy against 28. I spent the **Duplicator** potion on a
Defend for 10 Block — 15 total, 18 with Plating — and took 6.
*Rejected:* saving Duplicator for a Sango Isshin later (20 to ALL, duplicated to 40,
which would have cleared this board outright). I judged a ~30% chance of drawing a Sango
too thin to gamble 5 HP on at 23/80. I still think that was right; the error was one card
earlier.
**Had I read the Moon correctly I would have played three Defends and Read the Field for
20 Block and kept the potion.** Instead I finished the fight at 5 HP, which is the direct
cause of everything after it.

**Turn 3** (17 HP, 28 incoming, no Block cards at all in hand).
Wrote **Stolen Chapter** as a Plan — with the Moon out, "Draw 4" landed immediately, and
that is what made the turn. *Rejected:* playing it for its 2. Then wrote **Kurage's Oath+**
(10 to ALL, immediately), then **Predator+** to kill Scroll 2.
*Rejected:* the maximum-Block line (Kirara+ 11 + Plating 2 = 13 against 28, leaving both
Scrolls alive) — it left me at 2 HP with the same problem next turn, whereas killing one
Scroll halved the incoming permanently. There was no line that both blocked and killed;
choosing which was a real and uncomfortable decision.
This turn also showed that **Nereid's doubling does not apply to the Moon's immediate
copy** — Stolen Chapter drew 4, not 8, with Nereid's Ascension 2 active on my status line.
Took 12, down to 5 HP.

**Turn 4.** Last Scroll at 13 and only Empowering — a free turn. Exposed Flank+ then Strike
killed it. *Rejected:* nothing meaningful; with no incoming damage and 22 damage available
against 13 HP this turn presented no decision at all, and saying so is the finding.

Rewards: 13 gold, **Deep Current+** over Tide Wall, Exposed Flank+ (third copy) and Ayaka —
Soumetsu. Chosen for being cheap, immediate and unconditional in a deck that was already
30+ cards and full of conditions.

---

## Fight 3 — Fabricator, HP 148/150, plus summons (Guardbot, Stabbot, Zapbot, Noisebot)

Entered at 6/77, because the map gave me a single Monster node and no rest site. **This
fight was not survivable from 6 HP and I do not think any line I had wins it** — but I got
it to one attack from won, so the shape is worth recording.

Everything hangs on one printed line: **"Minion 1 — Minions abandon combat without their
leader."** So the Fabricator is the only real target, at 148 HP, while it summons a fresh
pair of attackers every other turn.

**Turn 1** (intent Summon — no damage incoming).
Bogglecat, then wrote **three** Plans: Coral Bulwark+, Stolen Chapter, War Council.
*Rejected:* playing Sango Isshin for 8 (its big mode needs a Plan already carried out, and
turn 1 has none), and playing any Block (nothing was coming). *Rejected:* Luminesce — three
Plans cost exactly my 3 remaining energy, and Luminesce Retains, so banking it was free.
The morning paid: 11 Block, draw 4, and 5 damage + Weak to ALL that hit the two new summons
for 7 each through Casket procs. **This is the kit at its best** — a turn spent entirely on
next turn, then a next turn that visibly pays.

**Turn 2.** Luminesce → Moon → wrote Exposed Flank+ (3 Vulnerable to ALL, immediately) →
Undertow+ killed Stabbot → Strike killed Guardbot → wrote Ambush+ (15 to the Fabricator now,
15 queued).
*Rejected:* Kirara+'s 11 Block. Killing both summons took the incoming to zero, which is
strictly better than blocking it, and the screen made that computable.
**Fourth disagreement.** Immediately after the Exposed Flank+ Plan resolved, all three
enemies took 3 Casket damage each — proof a debuff had been applied to each — but **not one
of them displayed Vulnerable**. I recomputed my kills without the 1.5× on that basis. Two
actions later the Fabricator's block showed **Vulnerable 3**, and Ambush+ hit for 22
(15 × 1.5). The debuff was there; the screen was a beat behind. I made a decision on a
screen that was wrong.

**Turn 3.** Predator+ killed Zapbot (16 incoming, removed) → Strike into the Fabricator →
wrote Slack Water as a Plan. *Rejected:* Defend, again because killing the attacker beat
blocking it. Zero damage taken.

**Turn 4.** Four enemies, 15 incoming, 6 HP. Expose+ stripped the Fabricator's 12 Block and
stacked Vulnerable → wrote Kurage's Oath+ (**15 to ALL immediately**, killing Guardbot, and
queued) → Amber — Fiery Rain cleared Zapbot and Noisebot in one card → wrote Vanguard+ →
Strike+ into the Fabricator, leaving it at roughly 15–18 HP, alone.
*Rejected:* spending 2 energy on Nereid's Ascension to double next morning's Oath (15 → 30,
i.e. 45 with Vulnerable). I took Strike+'s guaranteed 15 now instead, on the grounds that
leaving the Fabricator at ~15 needs only a single Oath to finish, which is more margin than
needing 45 against 30. I still think that was the better of the two.
*Rejected:* Amber's ordering — I chose it over Strike+ for the Zapbot kill because 3 × 5 = 15
clears a 10-HP body even if every modifier I had misread was wrong. After four turns of
unreliable arithmetic I was deliberately choosing cards whose floor killed, not whose
expectation killed. **That is a real cost of (c): I stopped being able to plan and started
buying insurance.**

**And then I died.** The last screen I read gave me: HP **6**, Plating **1** (so 1 Block at
end of turn), the Fabricator alone, its intent printed as **"the number on its icon is 8 —
This enemy intends to Attack for 8 damage"**, carrying **Weak 3 — "Attacks deal 25% less
damage"**. By those printed numbers the hit is 8 × 0.75 = 6, less 1 Block = 5, and I end the
turn on 1 HP with a queued Kurage's Oath+ that kills the Fabricator at the start of my next
morning before it can act again. That is the line I played, and I played it deliberately.

The next `observe` printed `TOOL-BLOCKED: game_over` / "The run ended on floor 39." **I never
got a screen that showed the lethal blow**, so I cannot say whether Weak was not applied,
whether the intent number understated the attack, whether Plating's Block did not arrive, or
whether something else resolved. What I can say is that **I did the arithmetic off the printed
intent and the printed Weak, concluded I survive at 1 HP, and was wrong.** Per the brief I
stopped at the `TOOL-BLOCKED` line and did not look further.

---

## The kit, after 3 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The Plan/Kurage axis is a genuinely good decision generator, and it produced the best turns
of the run. Every Plan card is two cards — a small immediate and a larger delayed — and
choosing between them is a real read of the intent line. Concretely:

- **Write vs play.** War Council play = 1 Weak; War Council Plan = 5 damage + 1 Weak to ALL.
  Ambush+ play = 5; Plan = 15. Read the Field 5 Block vs 10. The Plan is always bigger and
  always a turn late, so the question is always "does this enemy give me the turn?" — and the
  intent line answers it. Against a turn-1 Empower it is free; at 6 HP against a printed 16 it
  is unaffordable. That is a clean, legible trade.
- **Turn 1 of fight 3** was the best turn I played: I spent every point of energy on three
  Plans and did nothing at all in the present, because the intent said Summon. The morning paid
  11 Block, 4 cards and 7 damage to each of three bodies. Spending a whole turn on the future
  and watching it land is the kit's real pleasure.
- **Block or kill**, repeatedly and painfully. Fight 2 turn 3 (17 HP, 28 incoming) had no line
  that did both: 13 Block with both Scrolls alive, or kill one and eat 12. I have played that
  choice in many deckbuilders and this one was sharper than most, because Paper Cuts priced
  unblocked damage twice.
- **Sango Isshin's condition** is the best-designed card in the kit. "A quarter of your Max HP
  to ALL enemies if the Kurage carried out a Plan this turn" makes a Plan I wrote last turn into
  a visible, large, checkable payoff — and it made me sequence a whole turn around a condition
  rather than around a cost.
- **Elemental ordering**, when it worked. Deliberately leading with Amber's Pyro so a Hydro
  Sango could Vaporize is a satisfying thing to plan. It is undercut badly by (c).

**(b) What felt automatic, and what never seemed worth playing.**

- **Defend and Strike.** Every turn I held one it was filler; I never once chose a Defend over
  something else on its merits, only when nothing else was affordable. Strike was worse than
  filler because its printed number did not predict its damage (see (c)).
- **Luminesce** is close to automatic, but in the good direction — it Retains, so the correct
  play is almost always "bank it until a turn where 2 energy buys something," and I made that
  call three times without ever really having to think.
- **Fight 2's last turn** presented no decision whatsoever: 13 HP of enemy, no incoming damage,
  22 damage in hand. I list it because a turn with no rejected alternative is the instrument
  reading zero.
- **Nereid's Ascension** never earned its 2 energy. Its doubling applies only to the Kurage's
  morning carry-out, not to the Moon's immediate copy, so it wants a board where you have both
  spare energy *and* queued Plans *and* a turn to spare — which is the board where you are
  already winning. I played it three times and I am not sure it did anything the third time.
- **The Dazed from Blessed Antler** are never a decision, only a tax; they are Ethereal so they
  clear themselves, but they cost me the hand slot in the hand that mattered twice.
- **Exposed Flank+** — I ended the act holding three copies of a debuff card in a deck that
  wanted damage.

**(c) What I could not understand, or that contradicted its own printed text.**

This is the long section, and it is the finding of the round. **Six separate times the screen
told me something the game did not do**, and by the last fight I had stopped trusting card
numbers and was choosing plays by their worst case.

1. **The Moon Overlooks the Waters — "Plans also happen when played."** I read this as
   "playing a Plan card normally also fires its Plan clause." It does not. It means *a Plan you
   write onto the Kurage also happens immediately*. The board says this correctly in different
   words — *"Plans also happen NOW as you write them"* — so the two surfaces disagree, and the
   card's wording is the one you read first. **This misreading cost me ~10 Block at 23 HP and a
   potion, and it is the proximate cause of my death two fights later.** "When played" is doing
   the opposite of the work it looks like it is doing: writing a card onto the Kurage is the
   thing the card calls "played", and playing it from hand is the thing it doesn't cover.
2. **Kamisato Ayato — Kyouka — "Then deal 12 Hydro damage to a random enemy."** Nothing happened
   on play; the enemy's HP was 139 before and after. The 12 (as 13) arrived **two turns later**,
   when the buff expired, as an unexplained HP drop I had to reverse-engineer. The word "Then"
   reads as "now, after the first clause"; it means "when this ends."
3. **Strike's damage does not reconcile with my own status line.** Printed 7 → dealt 16 under
   Kyouka +4 and Vulnerable (consistent with Strength being ignored). Printed 11 → dealt exactly
   **11**, with Strength 1 *and* Kyouka +4 both still displayed on me. Undertow the same turn
   took both modifiers correctly (22, exactly as predicted). I never found an arithmetic that
   fit all three, and I could not predict my own damage from the screen.
4. **Amber — Fiery Rain leaves no visible aura.** The rules text on every combat screen says a
   hit on a bare enemy "applies its own element for 2 turns instead." After Amber's three Pyro
   hits the enemy displayed **no aura at all**, across two consecutive observes. I re-planned my
   turn on that basis. The next card, Hydro, then dealt **31 instead of 20** — a Vaporize off a
   Pyro aura that was never on screen. The screen prints a long paragraph warning that one
   specific hidden-reaction case exists; this was a different case, and it was invisible in the
   direction that made me play worse.
5. **Debuff display lags a beat.** A planned Exposed Flank+ applied 3 Vulnerable to three enemies
   — the Casket fired on all three, which only happens on a debuff — and **none of them displayed
   Vulnerable**. It appeared two actions later. I sized two kills off the wrong number.
6. **The killing blow.** Printed intent 8, printed Weak "25% less", 6 HP, 1 Plating Block. That is
   5 damage and survival at 1 HP. I died. No screen explained it.

Separately, and not a card: **the "fake merchant"** printed as `# The shop`, told me I had 247
gold, listed an empty shelf, offered `buy` as a legal verb, and gave no event text at all. Only
the tool's status line on exit ("Proceeding from fake merchant") revealed it was an event. From
the seat's side it is identical to a shop that failed to load, and it was the only chance in the
act to convert 279 gold into survival.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted: Strike.** Not because it is weak filler — I expect filler — but because it was
  the specific card whose printed number I learned I could not trust. By fight 1's last turn I was
  spending a free Expose+ purely to widen the margin on an 8-HP kill that a 7-damage Strike with a
  displayed +1 Strength should have made trivially. A vanilla card that makes you *hedge* is worse
  than a vanilla card that bores you. (Runner-up: **Nereid's Ascension**, which I paid 2 energy for
  three times and never clearly saw pay.)
- **Happiest to draw: Sango Isshin / Sango Isshin+.** "A quarter of your Max HP to ALL enemies" is
  a big, legible, board-checkable payoff on a condition you set up a turn earlier, and the turn I
  chained Amber → Sango+ → Sango for 69 damage was the one moment the kit felt like it had a combo
  worth finding. **Kurage's Oath+** is a close second for the same reason — writing it and watching
  15 land on every body *immediately* is the clearest the Moon/Plan engine ever got.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one** — though I inherited a built deck and a relic-heavy board, so this is not a
fair read on the kit's opening. The Sculptor's intent printed Empower, which made both Defends in
hand dead cards and turned the turn into a pure question about the Plan axis: play War Council now
for 1 Weak, or write it for 5 damage + 1 Weak next morning; same for Read the Field's 5 Block vs 10.
I also had to decide whether to bank Luminesce. Three real choices with a legible basis, and the
turn taught me the queueing rule by playing it. The kit's opening turn is in good shape; it is turns
3 onward, where the arithmetic stops matching the text, that fall apart.

---

## Non-blindness declaration

**Repo files read: none.**

I ran no understudy command other than the two allowed (`observe` and `act`) — no `harness state`,
no `scenario`, no `staged_turn`, no `soak`. I opened no file in
`review/qa/kokomi-round-9-2026-09-04/` or anywhere else in the repo, and I read no YAML sheet, C#
source, doc, packet or other seat's record.

Tools used outside the two allowed commands:

- **Bash**, only to shape the output of `observe` for my own reading, never to reach any other
  source. Specifically: `sed -n '<range>p'`, `awk '/x/,/y/'`, `head -N` and `tail -N` piped from
  `observe`; `echo "---"` as a separator; `&&` chaining of allowed commands; and `>/dev/null` to
  suppress `act` receipts I did not need.
- I redirected `observe` output to a scratch file **`/tmp/o.txt`** roughly a dozen times so I could
  read several sections of one screen without re-running the command. I should have used the
  session scratchpad directory named in my environment rather than `/tmp`; declaring the deviation.
  The file only ever contained `observe` output.
- **Write**, once, to produce this record at
  `review/qa/kokomi-round-9-2026-09-04/opus-run2-act3.md`.

One self-inflicted artifact worth noting: on two occasions my `sed` ranges overlapped and printed
the same screen block two or three times over. That is my formatting error, not the bridge's, and
I re-read the duplicated output rather than re-running the command.

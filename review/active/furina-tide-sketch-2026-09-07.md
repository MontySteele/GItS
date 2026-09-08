Status: OPEN (five picks, §7)

# Furina, the Tide: what she does, what her plans are, and why healing does not break her

Written 2026-09-07, night, after [USER] took concept A of
`review/active/furina-identity-concepts-2026-09-07.md` as the working theory
and asked for a deeper sketch: what the character does, her central plans,
and how the obvious degenerate loop with HP recovery is handled. GPT's three
conditions are answered by name in §4. Numbers are illustrative unless a
file is cited.

## 1. Why the Kokomi precedent does not disqualify this

`docs/current/characters/kokomi-kickoff-v1.md` records the standing axis
"Furina = HP volatility, Kokomi = HP stability", and Kokomi's first binding
law is no self-damage anywhere, because "the moment a Kokomi card costs HP,
the Furina boundary blurs." The record shows a partition, not a balance
failure: the HP engine was reserved for Furina and never built for her. The
healing law that partition sits under is `docs/current/LAW.md` line 200:
true in-combat healing is Rare and Exhausts, and below Rare sustain routes
through Block. Furina is the one character declared as "the healing
metric's protagonist" (`furina-kickoff-v0.1.md` §2, A4 4.3). The sketch
needs one exception to that law, stated in §4 and priced there; it is a C
pick.

## 2. The character in three sentences

Furina's party is the show, and the show is HP moving. Her Attacks hit
harder when she **Spends** her own HP, allowed only while she is above half.
Her Skills **Restore** HP, but never above the HP she entered the fight with;
and every point of HP that any ally loses, spends or restores fills her
Burst, **Let the People Rejoice**, the one heal that can exceed the entry
line. A fight that goes well ends where it began. A fight that goes badly
costs what it costs, and the Burst is how she gets some of it back.

The screen shows the HP bar with the half-line marked and the Burst meter
every character already has. Nothing else is counted.

## 3. The rules, each with its job

- **Spend N.** A rider on Attacks: pay N HP before the hit for a larger
  number ("Deal 7. Spend 4: deal 12 instead."). Allowed only above half HP.
  Job: the wager, and the half-line as the thing you play around.
- **Restore N.** On Skills: heal N, capped at the HP you entered this
  combat with. Job: recover the wager and the fight's chip, never the run's.
  A Restore with nothing to recover is a dead card, and holding it is the
  decision.
- **Fanfare** is her Burst meter, not a separate counter. It rises by 1 per
  point of HP any ally loses, Spends or Restores. It has a cap, and the
  Burst empties it; the Burst's own healing does not fill it. Job: the
  payoff timer; the faster HP moves, the sooner it comes.
- **Let the People Rejoice** (the kit-Burst, granted on fill, never in the
  pool): Restore 10 to each ally, this time above the entry line up to max
  HP, and deal 15 to all enemies. Job: the one true heal, earned by
  volatility, bounded by the cap and by one fill at a time.
- **Salon Solitaire** (a Power, not a panel): "At the end of your turn, if
  above half HP, Spend 3: deal 9 to a random enemy." **Singer of Many
  Waters** (a Power): "At the end of your turn, Restore 3." Job: the Salon
  as something you run, in one object each, with no queue and no slots;
  the Ousia and Pneuma flavor sits on these two cards.

Companion cards keep their present job: their Pyro, Cryo and Anemo react off
her Hydro, which is her damage ceiling, and in co-op every ally's HP fills
her meter, so a party in the fray is her engine. This is a card-level
relationship, in line with LAW's rule that co-op depth arrives as cards.

## 4. The degenerate loop, and the three rules that price it

The loop GPT named: Spend 4, Restore 5, nine Fanfare, repeat. Three rules
make that a wager instead of bookkeeping.

1. **Restore never exceeds entry HP.** Stalling a fight cannot make the run
   healthier; at best it returns the fight's HP. That is the reason to end
   fights: past the entry line there is nothing to gain, and StS2 enemies
   escalate.
2. **Restores are smaller than Spends on cards, and cost a card and Energy
   each.** Spend 4 for +5 damage costs nothing but HP; Restore 4 costs a
   card, 1 Energy, and only works below the entry line. A turn of Spend and
   Restore is a turn without a Block card, and the hit lands.
3. **Fanfare has a cap, and the Burst's healing does not count.** Stalling
   past the cap fills nothing. The Burst is the only heal above the entry
   line and it comes once per fill, so the party's real recovery per fight
   is bounded by the cap divided by the fill, an amount the sim reads.

What is left is the wager: Spend while above half, knowing the enemy's hit
may push you under and close the engine, or Block to keep the half-line and
give up the number. Block is not anti-synergy here; it guards the threshold
that Spend needs.

**Does damage taken count?** Yes, as in the source character and the old
LAW line "every point of damage past Block prints exactly 1 Fanfare". The
counterweight is the half-line: a hit that fills the meter also closes
Spend, so face-tanking is paid in the next turn's numbers.

## 5. One fight, with the starter

Starter, illustrative: four Soloist's Solicitation (6), four Stage Presence
(Block 6), Regal Bearing (Block 3, Weak), Salon Début rewritten as "Deal 7.
Spend 4: deal 12 instead", Aria of Recompense rewritten as "Restore 4".
Furina 78 of 78, entry 78, half-line 39, meter fills at 30. Enemy 42 HP,
intents 11, then 7 with Block, then 11.

| Turn | Hand and play | Rejected, and why | HP after enemy | Fanfare |
|---|---|---|---|---|
| 1 | Début with Spend (78 to 74) for 12, Solicitation 6, Presence 6; hit 11, 5 through | Two Presences and Début unspent: 0 Fanfare, 78 HP, enemy at 35 | 69 | 9 |
| 2 | Aria Restore 4 (to 73), Presence 6, Solicitation 6; hit 7, 1 through | Bearing and Presence for 9 Block and no Aria: Aria is only live while HP is under 78, and holding it past the kill wastes it | 72 | 14 |
| 3 | Début with Spend (to 68) 12, Solicitation, Solicitation: 24 on 18, dead | Unspent: 19 on 18, also dead, and 4 HP kept; the Spend was for Fanfare, not the kill | 68 | 18 |

The fight cost 10 HP and put 18 on a 30 meter. The next fight opens at 68,
Restore is capped there, the meter fills mid-fight, and the Burst puts the
party back toward 78. Over two fights she is near where she started: the
sustain fantasy, paid for by having Spent and having been hit.

**The contested turn** is the one near the line: 44 of 78, an intent of
15, hand Début, Solicitation, Presence, Aria, Bearing. Spend now (to 40) and
the hit puts her at 25, under half, so next turn Début is a 7 and Salon
Solitaire is silent; Presence and Bearing for 9 Block leaves 38, also
under, so the real play is Presence, Bearing and Solicitation, taking 6 to
land at 38, then Aria next turn to reopen the line. Which of those a seat
finds is the round's read.

## 6. Her plans, three, separated by card slots

- **The Salon (default, solo floor):** Spend Attacks and the two Powers;
  Block cards that guard the half-line. Wants HP above half and a Restore in
  hand.
- **The Fanfare deck (velocity):** cards that move HP fast both ways to
  reach the Burst twice a fight; Rare Restores that Exhaust, as the law has
  them. Wants to be hit and to answer it.
- **The Guest Cast (draft-gated ceiling):** Hydro on enemies and Companions
  who react off it; in co-op, the party's HP as her meter. Wants Companions.

The statline moves: frontload is no longer her weakness, since Spend is
early damage; the weakness is the half-line, under which she is a plain
character with modest numbers. The brief redeclares A1 and A7 on that.

## 7. What is asked

1. **The healing exception (C, LAW line 200).** Default: Furina's Restore is
   legal below Rare, capped at combat-entry HP; the Burst is her one heal
   above it; Rare heals stay Rare and Exhaust. 2: no exception, Restore
   becomes Block and the Burst alone heals. 3: the exception without the
   entry cap.
2. **Fanfare is the Burst meter.** Default: yes, no second counter, capped,
   filled by any ally's HP lost, Spent or Restored, emptied by the Burst.
   2: a separate Fanfare with a numeric bonus, Focus-like.
3. **Damage taken counts.** Default: yes. 2: only Spend and Restore count.
4. **The Salon as two Powers,** no panel. Default: yes. 2: one persistent
   summon with a portrait.
5. **Next step.** Default: the one-page brief revision from this sketch,
   then a `+proto` build and a seat round on the two questions in the
   concepts packet. 2: a second sketch pass first.

Status: OPEN (the Kokomi card audit; D defaults applied; picks at the end)

# Kokomi card audit: every prototype row's base and upgrade, read by design

2026-09-02. You asked for this after the upgrade pass: "I noticed you let
Opus do the upgrade pass. I think that, once it finishes, we should stick a
Fable agent (per character) to do a card audit, since I don't trust Opus with
this." That pass (PR #295) derived every upgrade by rule from the printed
numbers. This is the designer's read of all 28 `proto_kk_` rows in
`docs/prototype-surface.yaml`, base and upgrade, against Strike 6 / Defend 5,
the base game's Common / Uncommon / Rare shapes, the text conventions, and
what you ruled today (R243: the once-per-turn Powers, Sango Isshin's setup,
The Moon, A Ship at 3 / 6, no momentum rule, no energy-generating Power,
Battle Plan and Vanguard held as watch items). The seat records for rounds 2
and 3 and the balance record
(`review/records/balance-read-prototype-2026-09-02.md`) are the play
evidence quoted below.

Seven rows change, all as D defaults under R212 (applied, disclosed, yours to
veto by card name). Twenty-one are left as they are, each with its reason.
Three picks close the page.

## 1. Rows changed

| Card | Was | Now | Why |
|---|---|---|---|
| Treatise (U, 1, Power) | upgrade: draws 1 card when played | upgrade: Innate | An engine Power's upgrade is Innate, the base game's shape for its 1-cost setup Powers (Storm, Hello World, Machine Learning). A second draw per morning walks back the cap you ruled today; a draw-on-play is a lever nobody reaches for at a campfire. |
| The General's Banner (U, 1, Power) | upgrade: draws 1 card when played | upgrade: Innate | The same reasoning. A second Weak per turn is the volume you called "a LOT"; the Commander wants the Banner down before the first Companion, and Innate is what buys that. |
| Undertow (C, 1, Attack) | 7, or 10 against a debuffed enemy; upgrade: draws 1 card | same numbers; upgrade: 10, or 13 (+3 on both) | A Strike-shaped Common upgrades its damage. The `+` face prints the swap itself, because the two numbers sit inside a condition the rule could not reach. |
| Moon's Reflection (U, 1, Skill, Exhaust) | upgrade: loses Exhaust | upgrade: costs 0, keeps Exhaust; text "or the card if it has none" is now "or plays it if it has none" | Without Exhaust it replays Nereid's Ascension every time it comes round, which is the replay-as-chassis the brief demoted to one card (sec.6). The base game's answer for this card is Exhume+: cheaper, still Exhaust. The text is what the card does: the replayed card is put in hand and played. The round-2 Opus seat could not parse the older wording. |
| War Council (U, 1, Skill, Plan-only) | Plan: 4 damage and 1 Weak to ALL; upgrade +3 damage and +1 Weak | Plan: 5 damage and 1 Weak to ALL; upgrade +3 damage only (8 and 1 Weak) | Kurage's Oath, a basic, went to 7 to ALL today. At 4 the Uncommon trailed the basic on damage and only just passed it with the Casket's 2. At 5 the Casket makes it Oath's 7 plus a Weak on everyone, the Uncommon's step; upgraded it is Oath+'s 10 plus the Weak. One axis on the upgrade, Thunderclap's shape. |
| Chain of Command (U, 1, Skill, Plan-only) | Plan: 4 damage per Companion played last turn; upgrade +1 | Plan: 6 per Companion; upgrade +2 (8) | At 4 it needed three Companions in one turn to match Ambush's 12, which does not happen; the sim never played it (0 of 18 draws). At 6, two Companions are an Ambush and three are the Commander's morning (18). Per-instance +2 is Flechettes' delta. |
| Stolen Chapter (C, 1, Skill) | Draw 1; Plan: Draw 3; upgrade: Plan Draw 4 | Draw 2; Plan: Draw 4; upgrade: Draw 3 / Plan Draw 5 | "Draw 1 for 1" is a tax, the reading today's pass gave Feint's 4 and Read the Field's 4. Draw 2 is a card; the Plan doubles it, Read the Field's 5 / 10 shape. Both lines take +1. The round-3 Opus seat named this the one Plan whose trade read right and then found the delayed cards worthless on three energy, which is the Plan line's honest role: the spare-energy turn. |

Every number above is on the row; every upgrade is in the row's `upgrade:`
block and in the emitted `OnUpgrade`
(`klee-mod/KleeCode/Cards/Prototype/Generated/ProtoKk*.cs`).

## 2. The two named items

**Sango Isshin takes cost 2 to 1, and that is right.** The card is "8, or a
quarter of your Max HP to ALL enemies on a morning the Bake-Kurage carried
out a Plan". Nobody smiths it for the 8; the quarter has no number to move;
so the Rare's own privilege (52 of the base game's 92 cost upgrades are
Rares) is the lever, and it makes the setup turn cheaper, which is the turn
the card is for. Left as PR #295 derived it.

**Vanguard's upgrade moving from "loses Exhaust" to "2 Vulnerable and 1
Weak" is right.** Vanguard is 0 energy, Exhaust, and the balance record's
most automatic card (played on 13 of 13 draws, 9.25 damage for nothing with
the Casket). Taking Exhaust off a free card the record already calls over
would be the biggest upgrade in the pool on the card least in need of one.
The base game upgrades its 0-cost Exhaust debuff cards by the number
(Panacea, Disarm), and the rule moved the Vulnerable, the better half. Left
as derived; the base stays a watch item (R243, round 3).

## 3. Read and left alone

- **Kurage's Oath** 7 to ALL at dawn, +3: today's number; +3 is Cleave's.
- **Slack Water** 4 and 1 Weak, Plan 2 Weak to ALL: the signature basic; its
  three bumps are pick 2.
- **Feint** 6 / 10, +3 / +3: today's numbers; each mode gets a Strike's +3.
- **Ambush** 12 at dawn, +3: the commit card, 2 over Feint's dawn line for
  giving up the now-line; on the 2x line, not over it.
- **Read the Field** 5 / 10, +3 / +3: today's numbers.
- **Exposed Flank** 1 Vulnerable / 2 to ALL, +1 / +1: the Plan-only premium
  today's pass named; the thin now-line is the price of the option.
- **Song of Pearls** 3 Block once per turn, +1: your cap; +1 is Metallicize's.
- **Nereid's Ascension** 2, Exhaust, cost -1: the duration ("for 2 turns")
  is the lever a designer reaches for, but no key moves it and cost -1 is
  the Rare shape. Noted, not built.
- **The Moon Overlooks the Waters** 2, cost -1: a Rare Power's upgrade.
- **Sea-Salt Prayer** 4 Block and 1 Weak, +3 / +1: a two-number Common's
  dual bump has precedent (Iron Wave, Dodge and Roll); the Codex seat's
  "best defensive card" was the + form doing its job.
- **Deep Current** 6 to ALL, +3: today's number.
- **Coral Bulwark** 6 / 8 and 1 Weak, +3 / +3 and +1: today's numbers; not
  Read the Field twice, because the dawn line feeds the Casket.
- **Cleansing Wave** 5 and a cleanse / 10, +3 / +3: pick 3.
- **The Clouds Like Waves Rippling** 2 Block per debuff, cost 2, +1: per
  trigger is safe here because Block does not carry over; it reads a touch
  under Feel No Pain's rate at 2 energy, but a 2-cost Rare Power is the
  base's shape. Watch.
- **The Moon, A Ship O'er the Seas** 3 / 6, +2 / +2: R243 item 3, closed.
- **Rally** 1 Weak and the discount, +1 Weak: round 2's ruling.
- **Change of Plans** 1, Exhaust, loses Exhaust: today's cost, round 2's upgrade.
- **Salt Line** 8 Block, Exhaust, +3: Ghostly Armor's shape; Moon's
  Reflection can fetch it back.
- **Battle Plan** 2 Energy and 1 card at dawn, +1 card: the rule refuses an
  energy delta and the draw is the right half to move; the base is pick 1.
- **Sango Isshin** and **Vanguard**: section 2.

Text: all 28 faces pass `tools/lint_text_conventions.py` (186 prototype-arm
strings, every face under the 120-character ceiling). One legibility note,
unchanged: Chain of Command's "last turn" reads oddly from the hand on the
turn you write it, but it is exact, since the count is always the turn before
the carry-out, which is why Change of Plans and The Moon read the previous
turn's Companions.

## 4. Picks

1. **Battle Plan under the two Rares.** Nereid's Ascension carries out every
   Plan twice, so a Battle Plan written under it pays 4 Energy and 2 cards
   for 1; The Moon Overlooks the Waters makes it pay 2 Energy now and 2 at
   dawn, net +3 for a 1-cost card. That is the extra-energy engine you
   refused as a rule today, reached through two Rares and the one card
   already on watch. The new fact is the Rare interaction; the round-2 and
   round-3 reads priced Battle Plan alone. (1) **Hold; the three-act seat
   runs read it, as R243 round 3 already says. Default.** (2) "Plan: Gain 1
   Energy and draw 2 cards" now, the one-line change on the table since
   round 2.
2. **Slack Water's upgrade moves three numbers:** 7 damage, 2 Weak, and the
   Plan's 3 Weak to ALL. Bash's dual bump is the signature-basic precedent;
   the third is the Plan line, and the Codex seat called Slack Water+ the card
   that "defined most fights". (1) **Leave it; the signature basic is meant
   to be the starter's best card. Default.** (2) Bash-exact: 7 and 2 Weak
   now, the Plan line unchanged at 2 Weak
   (`upgrade: {damage: 3, power_amount: 1}`).
3. **Cleansing Wave's dawn line is Read the Field's** ("Plan: Gain 10
   Block" on both). (1) **Leave it; the Uncommon is Read the Field plus a
   cleanse, a legal Uncommon step. Default.** (2) Give it its own morning:
   "Plan: Gain 8 Block and draw 1 card".

## 5. Gates

`python tools/run_lints.py --lane ci` 35 of 35; `pytest tier0/tests -q -p
no:cacheprovider -k "prototype or kokomi or upgrade or face or keyword"` 663
passed, 0 failed; `python tools/gen_prototype_cards.py --check` up to date;
`dotnet build klee-mod/KleeCode -p:PrototypeCards=true` 0 errors; `dotnet
test klee-mod/KleeTests -p:PrototypeCards=true` 629 passed, 0 failed.
Nothing deployed, nothing played: the seven changes meet a player at the
next dev build and the three-act seat runs.
